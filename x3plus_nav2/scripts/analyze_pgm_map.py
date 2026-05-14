#!/usr/bin/env python3
"""Analyze a PGM map and report pixel statistics.

This script reads a PGM map file (P2 or P5), extracts map resolution from an
optional YAML map metadata file, and reports:
- Pixel size (meters per pixel, when available)
- Number of unknown pixels
- Number of free pixels
"""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Tuple


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
        raise ValueError("Invalid PGM header: expected magic, width, height, maxval")

    magic, width_s, height_s, maxval_s = tokens
    if magic not in {"P2", "P5"}:
        raise ValueError(f"Unsupported PGM format: {magic} (expected P2 or P5)")

    width = int(width_s)
    height = int(height_s)
    maxval = int(maxval_s)

    if width <= 0 or height <= 0:
        raise ValueError("Invalid image size in PGM header")
    if maxval <= 0 or maxval > 65535:
        raise ValueError("Invalid maxval in PGM header")

    pixel_count = width * height

    if magic == "P5":
        if maxval < 256:
            expected_size = pixel_count
            pixel_data = raw[data_offset : data_offset + expected_size]
            if len(pixel_data) != expected_size:
                raise ValueError("PGM pixel data is shorter than expected")
            return width, height, maxval, pixel_data

        expected_size = pixel_count * 2
        pixel_data = raw[data_offset : data_offset + expected_size]
        if len(pixel_data) != expected_size:
            raise ValueError("PGM pixel data is shorter than expected")

        # For 16-bit PGM values, keep only the low byte for threshold-based counting.
        low_bytes = pixel_data[1::2]
        return width, height, maxval, low_bytes

    text_payload = raw[data_offset:].decode("ascii", errors="strict")
    text_payload = re.sub(r"#.*", "", text_payload)
    values = [int(v) for v in text_payload.split()]

    if len(values) < pixel_count:
        raise ValueError("PGM pixel data is shorter than expected")

    if maxval < 256:
        return width, height, maxval, bytes(values[:pixel_count])

    low_bytes = bytes(v & 0xFF for v in values[:pixel_count])
    return width, height, maxval, low_bytes


def extract_resolution_from_yaml(yaml_path: Path) -> float | None:
    """Extract resolution value from a ROS map YAML file."""
    if not yaml_path.exists():
        return None

    for line in yaml_path.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.split("#", 1)[0].strip()
        if not stripped or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        if key.strip() == "resolution":
            try:
                return float(value.strip())
            except ValueError:
                return None
    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read a PGM map and report pixel size, unknown and free pixel counts."
    )
    parser.add_argument("pgm_file", type=Path, help="Path to map .pgm file")
    parser.add_argument(
        "--yaml",
        type=Path,
        default=None,
        help="Path to map .yaml file (defaults to same basename as PGM)",
    )
    parser.add_argument(
        "--unknown-value",
        type=int,
        default=205,
        help="Grayscale value considered unknown (default: 205)",
    )
    parser.add_argument(
        "--free-value",
        type=int,
        default=254,
        help="Grayscale value considered free (default: 254)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print output as JSON",
    )

    args = parser.parse_args()

    pgm_file = args.pgm_file
    if not pgm_file.exists() or not pgm_file.is_file():
        raise SystemExit(f"PGM file not found: {pgm_file}")

    yaml_file = args.yaml if args.yaml is not None else pgm_file.with_suffix(".yaml")

    width, height, _maxval, pixels = read_pgm(pgm_file)
    total_pixels = len(pixels)
    unknown_count = sum(1 for p in pixels if p == args.unknown_value)
    free_count = sum(1 for p in pixels if p == args.free_value)
    explored_count = total_pixels - unknown_count
    explored_ratio = (explored_count / total_pixels) if total_pixels else 0.0
    resolution = extract_resolution_from_yaml(yaml_file)

    pixel_area_m2 = (resolution * resolution) if resolution is not None else None
    total_area_m2 = (total_pixels * pixel_area_m2) if pixel_area_m2 is not None else None
    unknown_area_m2 = (unknown_count * pixel_area_m2) if pixel_area_m2 is not None else None
    free_area_m2 = (free_count * pixel_area_m2) if pixel_area_m2 is not None else None
    explored_area_m2 = (explored_count * pixel_area_m2) if pixel_area_m2 is not None else None

    result = {
        "file": str(pgm_file),
        "width": width,
        "height": height,
        "total_pixels": total_pixels,
        "pixel_size_m": resolution,
        "pixel_area_m2": pixel_area_m2,
        "total_area_m2": total_area_m2,
        "unknown_value": args.unknown_value,
        "unknown_pixels": unknown_count,
        "unknown_area_m2": unknown_area_m2,
        "free_value": args.free_value,
        "free_pixels": free_count,
        "free_area_m2": free_area_m2,
        "explored_pixels": explored_count,
        "explored_ratio": explored_ratio,
        "explored_area_m2": explored_area_m2,
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"File: {result['file']}")
        print(f"Image size: {width} x {height} pixels")
        if resolution is not None:
            print(f"Pixel size: {resolution} m/pixel")
            print(f"Pixel area: {pixel_area_m2:.6f} m^2/pixel")
            print(f"Map area: {total_area_m2:.3f} m^2")
        else:
            print("Pixel size: not found (no valid resolution in YAML)")
        print(f"Unknown pixels (value {args.unknown_value}): {unknown_count}")
        print(f"Free pixels (value {args.free_value}): {free_count}")
        if resolution is not None:
            print(f"Unknown area: {unknown_area_m2:.3f} m^2")
            print(f"Free area: {free_area_m2:.3f} m^2")
            print(f"Explored area: {explored_area_m2:.3f} m^2")
        print(
            f"Explored ratio (known/total): {explored_count}/{total_pixels} "
            f"({explored_ratio:.2%})"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
