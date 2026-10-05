#!/usr/bin/env python3
"""Extract real video frames and make labeled review sheets without replacing evidence."""

import argparse
import bisect
import hashlib
import json
import math
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def time_list(value):
    try:
        times = [float(part.strip()) for part in value.split(",")]
    except ValueError as error:
        raise argparse.ArgumentTypeError("Use comma-separated seconds.") from error
    if not times or any(not math.isfinite(t) or t < 0 for t in times):
        raise argparse.ArgumentTypeError("Times must be finite, nonnegative seconds.")
    return times


def run(argv, cwd=None):
    result = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, timeout=300)
    if result.returncode:
        raise ValueError(f"{Path(argv[0]).name} failed: {result.stderr.strip()[-2000:]}")
    return result.stdout


def fingerprint(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def nearest_frame(timestamps, time):
    right = bisect.bisect_left(timestamps, time)
    candidates = {max(0, right - 1), min(len(timestamps) - 1, right)}
    return min(candidates, key=lambda index: (abs(timestamps[index] - time), index))


def make_sheet(records, source_dir, target, columns, width, title):
    from PIL import Image, ImageDraw, ImageFont, ImageOps

    try:
        font = ImageFont.load_default(size=16)
    except TypeError:  # Support older Pillow installations too.
        font = ImageFont.load_default()
    columns = min(columns, len(records))
    with Image.open(source_dir / records[0]["path"]) as first:
        image_height = min(640, max(90, round(width * first.height / first.width)))
    gap, header, label = 12, 42, 30
    cell_height = image_height + label
    rows = math.ceil(len(records) / columns)
    size = (columns * (width + gap) + gap, header + rows * (cell_height + gap) + gap)
    if size[0] * size[1] > 40_000_000:
        raise ValueError("Sheet is too large; use fewer samples or a smaller thumbnail width.")
    sheet = Image.new("RGB", size, "#17191d")
    draw = ImageDraw.Draw(sheet)
    draw.text((gap, 12), title[:110], font=font, fill="#f5f5f5")
    for position, record in enumerate(records):
        x = gap + (position % columns) * (width + gap)
        y = header + (position // columns) * (cell_height + gap)
        with Image.open(source_dir / record["path"]) as frame:
            thumbnail = ImageOps.contain(frame.convert("RGB"), (width, image_height))
            sheet.paste(thumbnail, (x + (width - thumbnail.width) // 2,
                                    y + (image_height - thumbnail.height) // 2))
        caption = f"f{record['frame']:06d} | {record['seconds']:.4f}s"
        draw.text((x, y + image_height + 5), caption, font=font, fill="#f5f5f5")
    sheet.save(target)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", type=Path)
    parser.add_argument("--times", type=time_list, help="Sample seconds from the first video frame.")
    parser.add_argument("--strip-at", type=time_list, default=[], help="Centers for adjacent-frame strips.")
    parser.add_argument("--radius", type=int, default=3, help="Frames each side of a strip center (0-30).")
    parser.add_argument("--columns", type=int, default=4)
    parser.add_argument("--thumb-width", type=int, default=360)
    parser.add_argument("--out", required=True, type=Path, help="New evidence directory; never overwritten.")
    args = parser.parse_args()
    if not 0 <= args.radius <= 30 or not 1 <= args.columns <= 6 or not 160 <= args.thumb_width <= 640:
        parser.error("Use radius 0-30, columns 1-6, and thumbnail width 160-640.")
    source = args.video.expanduser().resolve()
    output = args.out.expanduser().absolute()
    if not source.is_file():
        parser.error(f"Video does not exist: {source}")
    if output.exists() or output.is_symlink():
        parser.error(f"Evidence directory already exists: {output}; choose a new --out.")
    ffmpeg, ffprobe = shutil.which("ffmpeg"), shutil.which("ffprobe")
    if not ffmpeg or not ffprobe:
        parser.error("FFmpeg and ffprobe must be available on PATH.")
    try:
        import PIL  # noqa: F401
    except ImportError:
        parser.error("Pillow must be available in the active Python environment.")

    source_hash = fingerprint(source)
    probe_command = [ffprobe, "-v", "error", "-select_streams", "v:0", "-show_frames",
                     "-show_streams", "-show_entries",
                     "frame=best_effort_timestamp_time:stream=index,codec_name,width,height,avg_frame_rate,r_frame_rate,time_base,duration",
                     "-of", "json", str(source)]
    info = json.loads(run(probe_command))
    if not info.get("streams") or not info.get("frames"):
        raise ValueError("Source contains no decodable video frames.")
    try:
        pts = [float(frame["best_effort_timestamp_time"]) for frame in info["frames"]]
    except (KeyError, ValueError) as error:
        raise ValueError("Cannot establish timestamps for every decoded video frame.") from error
    if any(not math.isfinite(t) for t in pts) or any(b < a for a, b in zip(pts, pts[1:])):
        raise ValueError("Video timestamps are invalid or not in presentation order.")
    timestamps = [t - pts[0] for t in pts]
    requests = args.times
    if requests is None:
        requests = [] if args.strip_at else [timestamps[-1] * i / 11 for i in range(12)]
    if any(t > timestamps[-1] + 0.000001 for t in requests + args.strip_at):
        raise ValueError(f"Requested time exceeds last video frame ({timestamps[-1]:.6f}s).")
    selected = {0, len(timestamps) - 1}
    mappings = []
    for time in requests:
        index = nearest_frame(timestamps, time)
        selected.add(index)
        mappings.append({"requested_seconds": time, "frame": index, "actual_seconds": timestamps[index]})
    strips = []
    for time in args.strip_at:
        center = nearest_frame(timestamps, time)
        indices = list(range(max(0, center - args.radius), min(len(pts), center + args.radius + 1)))
        selected.update(indices)
        strips.append({"requested_seconds": time, "center_frame": center, "frames": indices})
    indices = sorted(selected)
    if len(indices) > 120:
        raise ValueError("More than 120 frames selected; split the review into smaller sheets.")

    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".video-review-", dir=output.parent) as temporary:
        stage = Path(temporary)
        (stage / "frames").mkdir()
        expression = "+".join(f"eq(n\\,{index})" for index in indices)
        extract_command = [ffmpeg, "-v", "error", "-i", str(source), "-map", "0:v:0",
                           "-vf", f"select={expression}", "-fps_mode", "passthrough",
                           "-frames:v", str(len(indices)), "capture-%06d.png"]
        run(extract_command, cwd=stage)
        captures = sorted(stage.glob("capture-*.png"))
        if len(captures) != len(indices):
            raise ValueError(f"Expected {len(indices)} frames, extracted {len(captures)}.")
        records = []
        for index, capture in zip(indices, captures):
            relative = f"frames/frame-{index:06d}.png"
            capture.rename(stage / relative)
            records.append({"frame": index, "seconds": timestamps[index],
                            "source_pts_seconds": pts[index], "path": relative})
        make_sheet(records, stage, stage / "contact-sheet.png", args.columns, args.thumb_width, source.name)
        by_index = {record["frame"]: record for record in records}
        for number, strip in enumerate(strips):
            strip["sheet"] = f"strip-{number:02d}.png"
            make_sheet([by_index[i] for i in strip["frames"]], stage, stage / strip["sheet"],
                       args.columns, args.thumb_width, f"Transition around {strip['requested_seconds']:.4f}s")
        if fingerprint(source) != source_hash:
            raise ValueError("Source changed during capture; repeat the review on a stable candidate.")
        manifest = {"schema_version": 1, "source": str(source), "source_sha256": source_hash,
                    "stream": info["streams"][0], "decoded_frame_count": len(pts),
                    "time_origin_pts_seconds": pts[0], "last_frame_seconds": timestamps[-1],
                    "requested_samples": mappings, "strips": strips, "frames": records,
                    "probe_argv": probe_command, "extract_argv": extract_command,
                    "extract_working_directory": "temporary staging directory",
                    "limitations": "Decoded-video evidence only; visual, motion, audio, and source-seeking review remain separate."}
        (stage / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        shutil.copytree(stage, output)  # Fail if another process has created the target.
    print(f"Captured {len(indices)} frames: {output / 'contact-sheet.png'}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, subprocess.TimeoutExpired) as error:
        print(f"Review capture failed: {error}", file=sys.stderr)
        sys.exit(1)
