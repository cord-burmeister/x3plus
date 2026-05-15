#!/usr/bin/env python3
"""Export a series of Nav2 maps into an equal-sized image sequence or a video.

This script reads ROS/Nav2 map YAML files, loads their referenced PGM images,
and projects each map onto a common world-aligned canvas based on map
resolution and origin. The result is a frame sequence where all frames share
the same dimensions, suitable for time-lapse visualization and video encoding.

Examples:
  # Export frames from a folder of timestamped map YAML files
  ./export_nav2_map_sequence.py ./maps --output-dir ./frames

  # Export PNG frames and an MP4 video
  ./export_nav2_map_sequence.py ./maps --image-format png --video ./map_timelapse.mp4

  # Use a fixed output resolution (meters/pixel)
  ./export_nav2_map_sequence.py ./maps --target-resolution 0.05 --video ./map.mp4
"""

from __future__ import annotations

import argparse
import math
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Tuple


@dataclass
class MapMeta:
    """Map metadata required for alignment and export."""

    yaml_path: Path
    image_path: Path
    resolution: float
    origin_x: float
    origin_y: float
    width: int
    height: int
    pixels: bytes


def _read_non_comment_tokens(header_bytes: bytes, needed: int) -> Tuple[list[str], int]:
    """Read PGM header tokens while skipping comments.

    Returns the collected tokens and the byte offset at which pixel data starts.
    """
    tokens: list[str] = []
    i = 0
    n = len(header_bytes)

    while i < n and len(tokens) < needed:
        while i < n and chr(header_bytes[i]).isspace():
            i += 1
        if i >= n:
            break

        if header_bytes[i] == ord("#"):
            while i < n and header_bytes[i] not in (ord("\n"), ord("\r")):
                i += 1
            continue

        start = i
        while i < n and not chr(header_bytes[i]).isspace() and header_bytes[i] != ord("#"):
            i += 1
        token = header_bytes[start:i].decode("ascii", errors="strict")
        tokens.append(token)

    while i < n and chr(header_bytes[i]).isspace():
        i += 1

    return tokens, i


def read_pgm(file_path: Path) -> Tuple[int, int, int, bytes]:
    """Read a PGM file and return width, height, maxval, pixel bytes."""
    raw = file_path.read_bytes()
    tokens, data_offset = _read_non_comment_tokens(raw, needed=4)

    if len(tokens) < 4:
        raise ValueError(f"Invalid PGM header in {file_path}: expected magic, width, height, maxval")

    magic, width_s, height_s, maxval_s = tokens
    if magic not in {"P2", "P5"}:
        raise ValueError(f"Unsupported PGM format in {file_path}: {magic} (expected P2 or P5)")

    width = int(width_s)
    height = int(height_s)
    maxval = int(maxval_s)

    if width <= 0 or height <= 0:
        raise ValueError(f"Invalid image size in PGM header: {file_path}")
    if maxval <= 0 or maxval > 65535:
        raise ValueError(f"Invalid maxval in PGM header: {file_path}")

    pixel_count = width * height

    if magic == "P5":
        if maxval < 256:
            expected_size = pixel_count
            pixel_data = raw[data_offset : data_offset + expected_size]
            if len(pixel_data) != expected_size:
                raise ValueError(f"PGM pixel data is shorter than expected: {file_path}")
            return width, height, maxval, pixel_data

        expected_size = pixel_count * 2
        pixel_data = raw[data_offset : data_offset + expected_size]
        if len(pixel_data) != expected_size:
            raise ValueError(f"PGM pixel data is shorter than expected: {file_path}")

        # For 16-bit PGM values, keep low byte for 8-bit export.
        low_bytes = pixel_data[1::2]
        return width, height, maxval, low_bytes

    text_payload = raw[data_offset:].decode("ascii", errors="strict")
    text_payload = re.sub(r"#.*", "", text_payload)
    values = [int(v) for v in text_payload.split()]

    if len(values) < pixel_count:
        raise ValueError(f"PGM pixel data is shorter than expected: {file_path}")

    if maxval < 256:
        return width, height, maxval, bytes(values[:pixel_count])

    low_bytes = bytes(v & 0xFF for v in values[:pixel_count])
    return width, height, maxval, low_bytes


def _strip_comment(line: str) -> str:
    return line.split("#", 1)[0].strip()


def _parse_origin(value: str) -> tuple[float, float, float]:
    """Parse origin from YAML line like: [x, y, yaw]."""
    text = value.strip()
    if not text.startswith("[") or not text.endswith("]"):
        raise ValueError(f"Invalid origin format: {value}")
    raw = [part.strip() for part in text[1:-1].split(",")]
    if len(raw) != 3:
        raise ValueError(f"Invalid origin list length: {value}")
    return float(raw[0]), float(raw[1]), float(raw[2])


def parse_map_yaml(yaml_path: Path) -> tuple[Path, float, float, float, float]:
    """Parse map YAML and return image path, resolution, origin x/y/yaw."""
    image_s = None
    resolution = None
    origin = None

    for line in yaml_path.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = _strip_comment(line)
        if not stripped or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        key = key.strip()
        value = value.strip()

        if key == "image":
            image_s = value.strip("\"'")
        elif key == "resolution":
            resolution = float(value)
        elif key == "origin":
            origin = _parse_origin(value)

    if image_s is None:
        raise ValueError(f"Missing 'image' in YAML: {yaml_path}")
    if resolution is None:
        raise ValueError(f"Missing 'resolution' in YAML: {yaml_path}")
    if origin is None:
        raise ValueError(f"Missing 'origin' in YAML: {yaml_path}")

    image_path = (yaml_path.parent / image_s).resolve()
    ox, oy, yaw = origin
    return image_path, resolution, ox, oy, yaw


def discover_yaml_files(inputs: list[str]) -> list[Path]:
    """Discover YAML files from files, directories, or glob patterns."""
    result: list[Path] = []

    for item in inputs:
        p = Path(item)

        if p.exists() and p.is_file() and p.suffix.lower() in {".yaml", ".yml"}:
            result.append(p.resolve())
            continue

        if p.exists() and p.is_dir():
            result.extend(sorted(x.resolve() for x in p.rglob("*.yaml")))
            result.extend(sorted(x.resolve() for x in p.rglob("*.yml")))
            continue

        for match in sorted(Path().glob(item)):
            if match.is_file() and match.suffix.lower() in {".yaml", ".yml"}:
                result.append(match.resolve())

    # Preserve order but remove duplicates.
    seen: set[Path] = set()
    unique: list[Path] = []
    for path in result:
        if path in seen:
            continue
        seen.add(path)
        unique.append(path)

    return unique


def load_maps(yaml_files: Iterable[Path], allow_yaw: bool) -> list[MapMeta]:
    """Load map metadata and pixels for each YAML."""
    maps: list[MapMeta] = []

    for yml in yaml_files:
        image_path, resolution, ox, oy, yaw = parse_map_yaml(yml)
        if not image_path.exists() or not image_path.is_file():
            raise FileNotFoundError(f"Image file from YAML not found: {image_path} (from {yml})")

        if not allow_yaw and abs(yaw) > 1e-6:
            raise ValueError(
                f"Non-zero yaw ({yaw}) in {yml}. Use --allow-yaw to ignore yaw and continue."
            )

        width, height, _maxval, pixels = read_pgm(image_path)
        maps.append(
            MapMeta(
                yaml_path=yml,
                image_path=image_path,
                resolution=resolution,
                origin_x=ox,
                origin_y=oy,
                width=width,
                height=height,
                pixels=pixels,
            )
        )

    return maps


def _nearest_resample(src: bytes, src_w: int, src_h: int, dst_w: int, dst_h: int) -> bytes:
    """Nearest-neighbor resize for 8-bit grayscale image data."""
    if src_w == dst_w and src_h == dst_h:
        return src

    out = bytearray(dst_w * dst_h)
    x_lut = [min(src_w - 1, int((x + 0.5) * src_w / dst_w)) for x in range(dst_w)]
    y_lut = [min(src_h - 1, int((y + 0.5) * src_h / dst_h)) for y in range(dst_h)]

    for y in range(dst_h):
        sy = y_lut[y]
        src_row = sy * src_w
        dst_row = y * dst_w
        for x in range(dst_w):
            out[dst_row + x] = src[src_row + x_lut[x]]

    return bytes(out)


def _save_pgm(path: Path, width: int, height: int, pixels: bytes) -> None:
    """Write raw 8-bit grayscale data as binary PGM."""
    header = f"P5\n{width} {height}\n255\n".encode("ascii")
    path.write_bytes(header + pixels)


def _save_image(path: Path, width: int, height: int, pixels: bytes, image_format: str) -> None:
    """Save image as PGM or Pillow-supported format."""
    if image_format == "pgm":
        _save_pgm(path, width, height, pixels)
        return

    try:
        from PIL import Image  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "Pillow is required for PNG/JPG output. Install with: pip install pillow"
        ) from exc

    img = Image.frombytes("L", (width, height), pixels)
    if image_format == "jpg":
        img.save(path, format="JPEG", quality=95)
    else:
        img.save(path, format="PNG")


def _compose_on_canvas(
    map_meta: MapMeta,
    canvas_w: int,
    canvas_h: int,
    min_x: float,
    max_y: float,
    target_res: float,
    background_value: int,
) -> bytes:
    """Render one map onto a common global canvas."""
    scaled_w = max(1, int(round(map_meta.width * map_meta.resolution / target_res)))
    scaled_h = max(1, int(round(map_meta.height * map_meta.resolution / target_res)))

    scaled = _nearest_resample(map_meta.pixels, map_meta.width, map_meta.height, scaled_w, scaled_h)

    # The top edge in world coordinates is origin_y + map_height * resolution.
    map_top_y = map_meta.origin_y + map_meta.height * map_meta.resolution
    x_off = int(round((map_meta.origin_x - min_x) / target_res))
    y_off = int(round((max_y - map_top_y) / target_res))

    canvas = bytearray([background_value] * (canvas_w * canvas_h))

    src_x0 = 0
    src_y0 = 0
    dst_x0 = x_off
    dst_y0 = y_off
    copy_w = scaled_w
    copy_h = scaled_h

    if dst_x0 < 0:
        src_x0 = -dst_x0
        copy_w -= src_x0
        dst_x0 = 0
    if dst_y0 < 0:
        src_y0 = -dst_y0
        copy_h -= src_y0
        dst_y0 = 0

    if dst_x0 + copy_w > canvas_w:
        copy_w = canvas_w - dst_x0
    if dst_y0 + copy_h > canvas_h:
        copy_h = canvas_h - dst_y0

    if copy_w <= 0 or copy_h <= 0:
        return bytes(canvas)

    for row in range(copy_h):
        src_row = (src_y0 + row) * scaled_w + src_x0
        dst_row = (dst_y0 + row) * canvas_w + dst_x0
        canvas[dst_row : dst_row + copy_w] = scaled[src_row : src_row + copy_w]

    return bytes(canvas)


def _ffmpeg_video(
    frames_dir: Path,
    image_ext: str,
    video_path: Path,
    fps: float,
    overwrite: bool,
    codec: str,
) -> None:
    """Encode frame sequence into a video using ffmpeg."""
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise RuntimeError("ffmpeg is required for video export but was not found in PATH")

    pattern = str((frames_dir / f"frame_%06d.{image_ext}").resolve())
    cmd = [
        ffmpeg,
        "-y" if overwrite else "-n",
        "-framerate",
        str(fps),
        "-i",
        pattern,
        "-c:v",
        codec,
        "-pix_fmt",
        "yuv420p",
        str(video_path.resolve()),
    ]

    subprocess.run(cmd, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Convert multiple Nav2 map YAML files into a common-size image sequence "
            "and optionally a video."
        )
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        help="YAML files, directories, or glob patterns (e.g. maps/*.yaml)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("map_frames"),
        help="Directory to write frame images (default: ./map_frames)",
    )
    parser.add_argument(
        "--image-format",
        choices=["pgm", "png", "jpg"],
        default="pgm",
        help="Frame image format (default: pgm)",
    )
    parser.add_argument(
        "--video",
        type=Path,
        default=None,
        help="Optional output video path (e.g. map.mp4)",
    )
    parser.add_argument(
        "--fps",
        type=float,
        default=2.0,
        help="Video frame rate when --video is set (default: 2.0)",
    )
    parser.add_argument(
        "--codec",
        default="libx264",
        help="Video codec for ffmpeg (default: libx264)",
    )
    parser.add_argument(
        "--target-resolution",
        type=float,
        default=None,
        help=(
            "Output resolution in meters/pixel (default: minimum input resolution; "
            "auto-increased if needed so canvas dimensions are divisible by 2)"
        ),
    )
    parser.add_argument(
        "--background-value",
        type=int,
        default=205,
        help="Background grayscale value for uncovered canvas areas (default: 205)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow overwriting output frame files and video",
    )
    parser.add_argument(
        "--allow-yaw",
        action="store_true",
        help="Ignore non-zero origin yaw values instead of failing",
    )

    args = parser.parse_args()

    if not (0 <= args.background_value <= 255):
        raise SystemExit("--background-value must be in [0, 255]")
    if args.fps <= 0:
        raise SystemExit("--fps must be > 0")

    yaml_files = discover_yaml_files(args.inputs)
    if not yaml_files:
        raise SystemExit("No YAML files found from provided inputs")

    maps = load_maps(yaml_files, allow_yaw=args.allow_yaw)
    if not maps:
        raise SystemExit("No maps loaded")

    target_res = args.target_resolution
    auto_target_res = target_res is None
    if target_res is None:
        target_res = min(m.resolution for m in maps)
    if target_res <= 0:
        raise SystemExit("Target resolution must be > 0")

    min_x = min(m.origin_x for m in maps)
    min_y = min(m.origin_y for m in maps)
    max_x = max(m.origin_x + m.width * m.resolution for m in maps)
    max_y = max(m.origin_y + m.height * m.resolution for m in maps)

    if auto_target_res:
        world_w = max_x - min_x
        world_h = max_y - min_y
        eps = 1e-12

        # Increase only as much as required to keep both canvas dimensions even.
        for _ in range(10):
            canvas_w = max(1, int(math.ceil(world_w / target_res)))
            canvas_h = max(1, int(math.ceil(world_h / target_res)))
            if canvas_w % 2 == 0 and canvas_h % 2 == 0:
                break

            needed_w = world_w / (canvas_w - 1) if canvas_w % 2 == 1 and canvas_w > 1 else target_res
            needed_h = world_h / (canvas_h - 1) if canvas_h % 2 == 1 and canvas_h > 1 else target_res
            target_res = max(target_res, needed_w, needed_h) + eps

    canvas_w = max(1, int(math.ceil((max_x - min_x) / target_res)))
    canvas_h = max(1, int(math.ceil((max_y - min_y) / target_res)))

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    ext = args.image_format
    existing = sorted(output_dir.glob(f"*.{ext}"))
    if existing and not args.overwrite:
        raise SystemExit(
            f"Output directory already contains *.{ext} files: {output_dir}. "
            "Use --overwrite to allow replacing."
        )

    for idx, map_meta in enumerate(maps):
        frame = _compose_on_canvas(
            map_meta=map_meta,
            canvas_w=canvas_w,
            canvas_h=canvas_h,
            min_x=min_x,
            max_y=max_y,
            target_res=target_res,
            background_value=args.background_value,
        )
        frame_path = output_dir / f"frame_{idx:06d}.{ext}"
        if frame_path.exists() and not args.overwrite:
            raise SystemExit(f"Refusing to overwrite existing frame: {frame_path}")
        _save_image(frame_path, canvas_w, canvas_h, frame, ext)

    if args.video is not None:
        _ffmpeg_video(
            frames_dir=output_dir,
            image_ext=ext,
            video_path=args.video,
            fps=args.fps,
            overwrite=args.overwrite,
            codec=args.codec,
        )

    print(f"Loaded maps: {len(maps)}")
    print(f"Canvas size: {canvas_w} x {canvas_h} pixels")
    print(f"Target resolution: {target_res:.6f} m/pixel")
    print(f"Frames written to: {output_dir}")
    if args.video is not None:
        print(f"Video written to: {args.video}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
