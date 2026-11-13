#!/usr/bin/env python3
"""Render manually authored motion masks; this is not tracking or segmentation.

Usage: python build_motion_mask.py config.json --output edit/masks
Requires numpy and Pillow. Writes 8-bit grayscale mask_000000.png onward:
white retains upper layer A, black reveals lower layer B.

JSON fields: shape (line|polygon), width, height, fps (number or "30000/1001"),
exactly one of frame_count / duration_seconds, feather_px (default 0),
white_side (positive|negative for line; inside|outside for polygon), keyframes.
Each keyframe has frame and optional interpolation (linear|hold, applies to
the following segment). Line frames also have point: [x,y], normal_angle_deg.
Polygon frames have points: [[x,y],...], without repeating the first point.
Coordinates use image-edge units: (0,0) top-left, (1,1) bottom-right; offscreen
coordinates are allowed. Line normal angles are clockwise in screen space:
0 means positive/white on the right; 90 means positive/white below the line.
Angles interpolate as written: use 350 -> 370 for a 20-degree clockwise turn.
Polygon vertex count and correspondence must stay constant across keyframes.
feather_px is the full linear black-to-white ramp width, centered on the edge.
First/last keyframes must cover frames 0 and frame_count-1. Frame n is at n/fps;
clip duration is frame_count/fps. Duration must describe an integer frame count.
CLI timing overrides do not retime keyframe indices; update endpoints accordingly.
Import the PNG sequence from frame 0 at the declared fps in the compositor.
No easing is imposed. Add measured keyframes to represent nonlinear motion.
"""

import argparse
import bisect
from fractions import Fraction
import json
import math
from pathlib import Path
import sys

import numpy as np
from PIL import Image


def fail(message):
    raise ValueError(message)


def keys(value, allowed, required, context):
    if not isinstance(value, dict):
        fail(f"{context} must be an object")
    missing, unknown = required - value.keys(), value.keys() - allowed
    if missing or unknown:
        fail(f"{context}: missing {sorted(missing)}; unknown {sorted(unknown)}")


def number(value, context):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        fail(f"{context} must be a finite number")
    try:
        result = float(value)
    except OverflowError:
        fail(f"{context} must be a finite number")
    if not math.isfinite(result):
        fail(f"{context} must be a finite number")
    return result


def integer(value, context, minimum=1):
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        fail(f"{context} must be an integer >= {minimum}")
    return value


def point(value, context):
    if not isinstance(value, list) or len(value) != 2:
        fail(f"{context} must be [x, y]")
    result = [number(v, context) for v in value]
    # Avoid numeric overflow from corrupt coordinates while allowing offscreen edges.
    if any(abs(v) > 1_000_000 for v in result):
        fail(f"{context}: normalized coordinate magnitude exceeds 1000000")
    return result


def cross(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def validate_polygon(points, context):
    count = len(points)
    epsilon = 1e-10
    area = sum(cross((0, 0), points[i], points[(i + 1) % count])
               for i in range(count))
    if abs(area) <= epsilon:
        fail(f"{context}: polygon has zero or near-zero area")
    for i, a in enumerate(points):
        b = points[(i + 1) % count]
        if math.dist(a, b) <= epsilon:
            fail(f"{context}: repeated/indistinguishable adjacent vertices")
        for j in range(i + 1, count):
            if j == i + 1 or (i == 0 and j == count - 1):
                continue
            c, d = points[j], points[(j + 1) % count]
            overlaps = (max(min(a[0], b[0]), min(c[0], d[0])) <=
                        min(max(a[0], b[0]), max(c[0], d[0])) + epsilon and
                        max(min(a[1], b[1]), min(c[1], d[1])) <=
                        min(max(a[1], b[1]), max(c[1], d[1])) + epsilon)
            ac, ad, ca, cb = cross(a, b, c), cross(a, b, d), cross(c, d, a), cross(c, d, b)
            if overlaps and ac * ad <= epsilon**2 and ca * cb <= epsilon**2:
                fail(f"{context}: polygon edges intersect or touch")


def validate(config):
    allowed = {"shape", "width", "height", "fps", "frame_count", "duration_seconds",
               "feather_px", "white_side", "keyframes"}
    keys(config, allowed, {"shape", "width", "height", "fps", "white_side", "keyframes"}, "config")
    if config["shape"] not in ("line", "polygon"):
        fail("shape must be line or polygon")
    config["width"] = integer(config["width"], "width")
    config["height"] = integer(config["height"], "height")
    try:
        if isinstance(config["fps"], bool):
            fail("fps must be positive")
        fps = Fraction(str(config["fps"]))
    except (ValueError, ZeroDivisionError):
        fail("fps must be a positive number or rational string, e.g. 30000/1001")
    if fps <= 0 or not math.isfinite(float(fps)):
        fail("fps must be positive and finite")
    config["fps"] = fps
    if ("frame_count" in config) == ("duration_seconds" in config):
        fail("provide exactly one of frame_count and duration_seconds")
    if "duration_seconds" in config:
        duration = number(config["duration_seconds"], "duration_seconds")
        count = duration * float(fps)
        if duration <= 0 or not math.isfinite(count) or abs(count - round(count)) > 1e-7:
            fail("duration_seconds * fps must be a positive integer; use frame_count for exact alignment")
        config["frame_count"] = round(count)
    integer(config["frame_count"], "frame_count")
    config["feather_px"] = number(config.get("feather_px", 0), "feather_px")
    if config["feather_px"] < 0:
        fail("feather_px must be >= 0")
    sides = ("positive", "negative") if config["shape"] == "line" else ("inside", "outside")
    if config["white_side"] not in sides:
        fail(f"white_side for {config['shape']} must be one of {sides}")
    frames = config["keyframes"]
    if not isinstance(frames, list) or not frames:
        fail("keyframes must be a nonempty list")
    shape_keys = {"point", "normal_angle_deg"} if config["shape"] == "line" else {"points"}
    previous = -1
    vertex_count = None
    for index, frame in enumerate(frames):
        context = f"keyframes[{index}]"
        keys(frame, {"frame", "interpolation"} | shape_keys, {"frame"} | shape_keys, context)
        position = integer(frame["frame"], context + ".frame", 0)
        if position <= previous or position >= config["frame_count"]:
            fail(f"{context}: frames must be strictly increasing and inside the clip")
        previous = position
        frame["interpolation"] = frame.get("interpolation", "linear")
        if frame["interpolation"] not in ("linear", "hold"):
            fail(f"{context}: interpolation must be linear or hold")
        if config["shape"] == "line":
            frame["point"] = point(frame["point"], context + ".point")
            frame["normal_angle_deg"] = number(frame["normal_angle_deg"], context + ".normal_angle_deg")
        else:
            if not isinstance(frame["points"], list) or len(frame["points"]) < 3:
                fail(f"{context}: points must contain at least three vertices")
            frame["points"] = [point(p, context + ".points") for p in frame["points"]]
            if vertex_count is not None and len(frame["points"]) != vertex_count:
                fail(f"{context}: polygon vertex counts must match")
            vertex_count = len(frame["points"])
            validate_polygon(frame["points"], context)
    if frames[0]["frame"] != 0 or frames[-1]["frame"] != config["frame_count"] - 1:
        fail("keyframes must include frame 0 and frame_count - 1")
    # Check every delivered polygon before creating any output, including interpolated shapes.
    if config["shape"] == "polygon":
        for index in range(config["frame_count"]):
            validate_polygon(state_at(config, index)["points"], f"interpolated frame {index}")
    return config


def state_at(config, index):
    frames = config["keyframes"]
    slot = bisect.bisect_right([f["frame"] for f in frames], index) - 1
    start = frames[slot]
    if slot == len(frames) - 1 or start["interpolation"] == "hold":
        return start
    end = frames[slot + 1]
    amount = (index - start["frame"]) / (end["frame"] - start["frame"])
    def mix(a, b):
        return (1 - amount) * np.asarray(a, dtype=float) + amount * np.asarray(b, dtype=float)
    if config["shape"] == "line":
        return {"point": mix(start["point"], end["point"]),
                "normal_angle_deg": float(mix(start["normal_angle_deg"], end["normal_angle_deg"]))}
    return {"points": mix(start["points"], end["points"])}


def render(config, state, x, y):
    width, height = config["width"], config["height"]
    feather = config["feather_px"]
    if config["shape"] == "line":
        px, py = state["point"] * np.array([width, height])
        angle = math.radians(state["normal_angle_deg"] % 360)
        distance = (x - px) * math.cos(angle) + (y - py) * math.sin(angle)
        if config["white_side"] == "negative":
            distance = -distance
    else:
        points = np.asarray(state["points"]) * [width, height]
        inside = np.zeros((height, width), dtype=bool)
        distance2 = np.full((height, width), np.inf) if feather else None
        for index, a in enumerate(points):
            b = points[(index + 1) % len(points)]
            dx, dy = b - a
            if dy != 0:
                inside ^= ((a[1] > y) != (b[1] > y)) & (x < (y - a[1]) * dx / dy + a[0])
            if feather:
                amount = np.clip(((x - a[0]) * dx + (y - a[1]) * dy) / (dx * dx + dy * dy), 0, 1)
                distance2 = np.minimum(distance2, (x - a[0] - amount * dx)**2 + (y - a[1] - amount * dy)**2)
        if config["white_side"] == "outside":
            inside = ~inside
        distance = np.where(inside, 1, -1) * np.sqrt(distance2) if feather else np.where(inside, 1, -1)
    mask = np.clip(0.5 + distance / feather, 0, 1) if feather else distance >= 0
    return Image.fromarray(np.rint(mask * 255).astype(np.uint8))


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            fail(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("config", type=Path)
    parser.add_argument("--output", type=Path, required=True, help="new or empty directory; never overwritten")
    parser.add_argument("--width", type=int)
    parser.add_argument("--height", type=int)
    parser.add_argument("--fps", help="number or rational string")
    timing = parser.add_mutually_exclusive_group()
    timing.add_argument("--frames", type=int, help="override frame_count/duration_seconds")
    timing.add_argument("--duration", type=float, help="override frame_count/duration_seconds in seconds")
    parser.add_argument("--feather-px", type=float)
    args = parser.parse_args()
    try:
        config = json.loads(args.config.read_text(encoding="utf-8-sig"), object_pairs_hook=unique_object)
        if not isinstance(config, dict):
            fail("config must be a JSON object")
        for name in ("width", "height", "fps", "feather_px"):
            if getattr(args, name) is not None:
                config[name] = getattr(args, name)
        if args.frames is not None or args.duration is not None:
            config.pop("frame_count", None)
            config.pop("duration_seconds", None)
            config["frame_count" if args.frames is not None else "duration_seconds"] = (
                args.frames if args.frames is not None else args.duration)
        validate(config)
        output = args.output
        if output.exists() and (not output.is_dir() or any(output.iterdir())):
            fail("output must be a new or empty directory; no files were overwritten")
        output.mkdir(parents=True, exist_ok=True)
        x = np.arange(config["width"], dtype=float)[None, :] + 0.5
        y = np.arange(config["height"], dtype=float)[:, None] + 0.5
        for index in range(config["frame_count"]):
            # Exclusive creation also protects files created by another process during rendering.
            with (output / f"mask_{index:06d}.png").open("xb") as handle:
                render(config, state_at(config, index), x, y).save(handle, format="PNG")
        print(f"Wrote {config['frame_count']} grayscale masks at {config['width']}x{config['height']}, "
              f"{config['fps']} fps ({config['frame_count'] / float(config['fps']):.9g} seconds) to {output}")
        return 0
    except (ValueError, OSError, OverflowError, MemoryError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
