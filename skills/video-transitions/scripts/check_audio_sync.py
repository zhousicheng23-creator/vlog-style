#!/usr/bin/env python3
"""Estimate an original-audio offset; this does not verify picture/audio sync.

Requires Python 3.9+, numpy, scipy, and an explicitly supplied FFmpeg executable.
Positive delay means the matching audio occurs LATER than --rendered-start.
--source-start maps to --rendered-start; --window is in OUTPUT seconds and
source time advances by --speed source seconds per output second. Use a window
inside one constant-speed edit. Speed changes use FFmpeg's pitch-preserving
atempo with stereo audio at 48 kHz; other stretching algorithms or processing
formats may not correlate reliably. Set --tempo-layout mono for a mono tempo
pipeline. Inspect/listen to the picture separately.

Example (all media stay local and read-only):
  python check_audio_sync.py --ffmpeg /absolute/path/ffmpeg \
    --source source.mov --rendered export.mp4 --source-start 2.6 \
    --rendered-start 1.4 --window 0.5 --speed 1.5 \
    --lag-min-ms -200 --lag-max-ms 200 --report offset.json

Exit codes: 0 = offset estimated, 2 = inconclusive, 1 = execution/input error.
An estimated offset is evidence about audio only, not a pass/fail sync verdict.
"""

import argparse
import json
import math
from pathlib import Path
import subprocess
import sys


class CheckError(Exception):
    """A readable input or decoder error."""


def parser():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--ffmpeg", required=True, type=Path, help="Absolute FFmpeg executable path; PATH is never searched")
    p.add_argument("--source", required=True, type=Path)
    p.add_argument("--rendered", required=True, type=Path)
    p.add_argument("--source-start", required=True, type=float, help="Source trim start, in seconds")
    p.add_argument("--rendered-start", required=True, type=float, help="Expected output time for source-start, in seconds")
    p.add_argument("--window", required=True, type=float, help="Comparison duration in OUTPUT seconds")
    p.add_argument("--speed", type=float, default=1.0, help="Constant source playback rate; 1.5 means 1.5x faster")
    p.add_argument("--lag-min-ms", type=float, default=-200.0)
    p.add_argument("--lag-max-ms", type=float, default=200.0)
    p.add_argument("--sample-rate", type=int, default=16000)
    p.add_argument("--tempo-layout", choices=("mono", "stereo"), default="stereo", help="Channel layout before source atempo; match the edit pipeline (default: stereo)")
    p.add_argument("--min-correlation", type=float, default=0.6)
    p.add_argument("--silence-dbfs", type=float, default=-60.0, help="Minimum AC RMS level for usable audio")
    p.add_argument("--min-peak-margin", type=float, default=0.05, help="Required lead over alternative peaks at least 10 ms away")
    p.add_argument("--report", type=Path, help="Optional JSON destination; JSON is always also printed")
    return p


def tempo_filters(speed):
    """Keep every atempo stage in [0.5, 2], including extreme valid speeds."""
    stages = []
    while speed > 2.0:
        stages.append("atempo=2")
        speed /= 2.0
    while speed < 0.5:
        stages.append("atempo=0.5")
        speed *= 2.0
    if not math.isclose(speed, 1.0, rel_tol=0, abs_tol=1e-12):
        stages.append(f"atempo={speed:.12g}")
    return stages


def decode(ffmpeg, media, start, input_duration, sample_rate, filters, np):
    cmd = [str(ffmpeg), "-nostdin", "-hide_banner", "-loglevel", "error",
           "-ss", f"{start:.12f}", "-t", f"{input_duration:.12f}",
           "-i", str(media), "-map", "0:a:0", "-vn", "-sn", "-dn",
           "-af", ",".join(filters) if filters else "anull",
           "-ar", str(sample_rate), "-ac", "1", "-c:a", "pcm_f32le",
           "-f", "f32le", "pipe:1"]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    except OSError as exc:
        raise CheckError(f"Could not execute FFmpeg: {exc}") from exc
    if result.returncode:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise CheckError(f"FFmpeg failed for {media} (exit {result.returncode}): {detail}")
    if len(result.stdout) % 4:
        raise CheckError(f"FFmpeg returned incomplete float audio for {media}")
    samples = np.frombuffer(result.stdout, dtype="<f4").astype(np.float64)
    if not np.all(np.isfinite(samples)):
        raise CheckError(f"Non-finite decoded audio samples in {media}")
    return samples


def energy(samples, np):
    if not len(samples):
        return {"samples": 0, "rms": 0.0, "rms_dbfs": None, "ac_rms": 0.0,
                "ac_rms_dbfs": None, "mean_square": 0.0, "peak": 0.0}
    mean_square = float(np.mean(samples * samples))
    rms = math.sqrt(mean_square)
    ac_rms = float(np.std(samples))
    return {"samples": len(samples), "rms": rms,
            "rms_dbfs": 20 * math.log10(rms) if rms else None,
            "ac_rms": ac_rms,
            "ac_rms_dbfs": 20 * math.log10(ac_rms) if ac_rms else None,
            "mean_square": mean_square, "peak": float(np.max(np.abs(samples)))}


def check(args, np, correlate):
    finite_fields = ("source_start", "rendered_start", "window", "speed", "lag_min_ms",
                     "lag_max_ms", "min_correlation", "silence_dbfs", "min_peak_margin")
    for name in finite_fields:
        if not math.isfinite(getattr(args, name)):
            raise CheckError(f"--{name.replace('_', '-')} must be finite")
    if not args.ffmpeg.is_absolute() or not args.ffmpeg.is_file():
        raise CheckError("--ffmpeg must be an absolute path to an existing executable")
    for name in ("source", "rendered"):
        if not getattr(args, name).is_file():
            raise CheckError(f"--{name} is not an existing local file: {getattr(args, name)}")
    if args.report and args.report.resolve() in {args.source.resolve(), args.rendered.resolve(), args.ffmpeg.resolve()}:
        raise CheckError("--report must not overwrite either input or the FFmpeg executable")
    if args.report and args.report.exists():
        raise CheckError("--report already exists; choose a new path (existing files are never overwritten)")
    if args.source_start < 0 or args.rendered_start < 0:
        raise CheckError("Start times must be nonnegative")
    if args.window < 0.1 or args.speed <= 0 or args.sample_rate < 1000:
        raise CheckError("--window must be >= 0.1 s, --speed > 0, and --sample-rate >= 1000")
    if args.lag_min_ms >= args.lag_max_ms:
        raise CheckError("--lag-min-ms must be smaller than --lag-max-ms")
    if not 0 < args.min_correlation <= 1 or not 0 <= args.min_peak_margin <= 1:
        raise CheckError("Correlation threshold must be in (0,1], and peak margin in [0,1]")

    rate = args.sample_rate
    count = round(args.window * rate)
    duration = count / rate
    lag_min = max(round(args.lag_min_ms * rate / 1000), math.ceil(-args.rendered_start * rate))
    lag_max = round(args.lag_max_ms * rate / 1000)
    if lag_min >= lag_max:
        raise CheckError("No searchable lag range remains after clipping to the start of the rendered file")
    search_start = max(0.0, args.rendered_start + lag_min / rate)
    search_duration = duration + (lag_max - lag_min) / rate
    stages = tempo_filters(args.speed)
    # Extra decode context avoids atempo's short-window tail truncation. Only the
    # first 'count' samples participate; no source/output silence is fabricated.
    context_seconds = 0.25 if stages else 0.05
    source_duration = (duration + context_seconds) * args.speed
    # Fix the processing layout before atempo. Otherwise FFmpeg can negotiate
    # the final mono layout upstream into aresample, changing atempo's waveform
    # alignment compared with the common stereo edit pipeline.
    source = decode(args.ffmpeg, args.source, args.source_start, source_duration, rate,
                    ["aresample=48000", f"aformat=channel_layouts={args.tempo_layout}", *stages,
                     f"atrim=duration={duration:.12f}"], np)[:count]
    rendered = decode(args.ffmpeg, args.rendered, search_start, search_duration + 0.05,
                      rate, [], np)[:count + lag_max - lag_min]
    report = {
        "status": "inconclusive",
        "scope": "Original-audio offset estimate only; does not prove picture/audio synchronization.",
        "delay_convention": "Positive delay: matching rendered audio is later than rendered_start.",
        "delay_ms": None, "normalized_correlation": None, "absolute_correlation": None,
        "reasons": [], "warnings": [],
        "inputs": {"source": str(args.source.resolve()), "rendered": str(args.rendered.resolve()),
                   "ffmpeg": str(args.ffmpeg.resolve()), "source_start_seconds": args.source_start,
                   "rendered_start_seconds": args.rendered_start,
                   "output_window_seconds": duration, "speed": args.speed,
                   "source_interval_seconds": [args.source_start, args.source_start + duration * args.speed],
                   "source_decode_context_seconds": context_seconds * args.speed,
                   "tempo_processing_format": f"{args.tempo_layout}, 48000 Hz, FFmpeg atempo",
                   "sample_rate": rate, "requested_lag_range_ms": [args.lag_min_ms, args.lag_max_ms]},
        "thresholds": {"min_absolute_correlation": args.min_correlation,
                       "silence_ac_rms_dbfs": args.silence_dbfs,
                       "min_peak_margin": args.min_peak_margin,
                       "alternative_peak_exclusion_ms": 10.0},
        "energy": {"source": energy(source, np), "rendered_search": energy(rendered, np)},
        "method": "Mono waveform Pearson correlation; equal full-window sample count at every candidate lag.",
    }
    if len(source) < count or len(rendered) < count + 2:
        report["reasons"].append("insufficient_audio_for_full_window_and_lag_search")
        return report
    threshold = 10 ** (args.silence_dbfs / 20)
    if report["energy"]["source"]["ac_rms"] < max(threshold, 1e-12):
        report["reasons"].append("source_is_silent_or_below_energy_threshold")
    if report["energy"]["rendered_search"]["ac_rms"] < max(threshold, 1e-12):
        report["reasons"].append("rendered_audio_is_silent_or_below_energy_threshold")
    if report["reasons"]:
        return report

    # Center the template once; center each candidate using rolling moments.
    # A global rendered norm (or unnormalized correlation) biases the best lag.
    centered = source - np.mean(source)
    source_ss = float(np.dot(centered, centered))
    sums = np.concatenate(([0.0], np.cumsum(rendered)))
    squares = np.concatenate(([0.0], np.cumsum(rendered * rendered)))
    window_sum = sums[count:] - sums[:-count]
    window_ss = np.maximum(squares[count:] - squares[:-count] - window_sum * window_sum / count, 0.0)
    denominator = np.sqrt(source_ss * window_ss)
    correlations = np.zeros_like(denominator)
    usable = (window_ss / count >= threshold * threshold) & (denominator > 1e-20)
    dots = correlate(rendered, centered, mode="valid", method="fft")
    correlations[usable] = dots[usable] / denominator[usable]
    correlations = np.clip(correlations, -1.0, 1.0)
    if not np.any(usable):
        report["reasons"].append("all_candidate_windows_are_silent_or_below_energy_threshold")
        return report
    scores = np.abs(correlations)
    best = int(np.argmax(np.where(usable, scores, -1.0)))
    lag_samples = lag_min + best
    report["delay_ms"] = lag_samples * 1000 / rate
    report["normalized_correlation"] = float(correlations[best])
    report["absolute_correlation"] = float(scores[best])
    report["effective_lag_range_ms"] = [lag_min * 1000 / rate, (lag_min + len(scores) - 1) * 1000 / rate]
    report["energy"]["rendered_matched_window"] = energy(rendered[best:best + count], np)
    report["matched_rendered_start_seconds"] = args.rendered_start + lag_samples / rate
    exclusion = max(1, round(0.010 * rate))
    alternatives = usable & (np.abs(np.arange(len(scores)) - best) >= exclusion)
    runner_up = float(np.max(scores[alternatives])) if np.any(alternatives) else None
    report["alternative_peak_absolute_correlation"] = runner_up
    report["peak_margin"] = float(scores[best] - runner_up) if runner_up is not None else None
    if scores[best] < args.min_correlation:
        report["reasons"].append("correlation_below_threshold")
    if best <= 1 or best >= len(scores) - 2:
        report["reasons"].append("peak_at_search_boundary_expand_range_or_move_window")
    if runner_up is not None and scores[best] - runner_up < args.min_peak_margin:
        report["reasons"].append("ambiguous_competing_correlation_peaks")
    if correlations[best] < 0:
        report["warnings"].append("best_match_has_inverted_audio_polarity")
    if len(rendered) < count + lag_max - lag_min:
        report["warnings"].append("rendered_file_ended_before_requested_search_range")
    if not report["reasons"]:
        report["status"] = "estimated"
    return report


def main():
    args = parser().parse_args()
    try:
        import numpy as np
        from scipy.signal import correlate
        result = check(args, np, correlate)
    except ImportError as exc:
        result = {"status": "error", "error": f"Missing dependency: {exc}. Install numpy and scipy in the Python environment used to run this script."}
    except (CheckError, OSError, ValueError) as exc:
        result = {"status": "error", "error": str(exc)}
    serialized = json.dumps(result, ensure_ascii=True, indent=2, allow_nan=False)
    # On validation errors never write a report: the supplied path may itself
    # have caused the error (for example, it names original media).
    if args.report and result["status"] != "error":
        try:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            with args.report.open("x", encoding="utf-8") as report_file:
                report_file.write(serialized + "\n")
        except OSError as exc:
            print(json.dumps({"status": "error", "error": f"Cannot write report: {exc}"}), file=sys.stderr)
            print(serialized)
            return 1
    print(serialized)
    return {"estimated": 0, "inconclusive": 2, "error": 1}[result["status"]]


if __name__ == "__main__":
    sys.exit(main())
