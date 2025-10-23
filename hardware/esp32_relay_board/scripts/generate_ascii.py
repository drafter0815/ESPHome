#!/usr/bin/env python3
"""Generate an ASCII-art blueprint of the ESP32 relay board layout."""
from __future__ import annotations

import pathlib
from typing import Iterable, Tuple

BOARD_WIDTH_MM = 220.0
BOARD_HEIGHT_MM = 130.0
CELL_SIZE_MM = 2.0  # resolution of the ASCII grid
MARGIN_MM = 5.0


def draw_header(
    canvas: list[list[str]],
    x_mm: float,
    y_mm: float,
    pins: int,
    label: str,
    left_offset: int,
    top_offset: int,
) -> None:
    """Render a simple representation of a vertical pin header."""
    x = left_offset + mm_to_units(x_mm)
    y0 = top_offset + mm_to_units(y_mm)
    for pin in range(pins):
        y = y0 + pin
        if 0 <= y < len(canvas):
            canvas[y][x] = "|"
    place_label(canvas, x + 2, y0, label)


def mm_to_units(value_mm: float) -> int:
    """Convert a millimetre value to integer grid units."""
    return int(round(value_mm / CELL_SIZE_MM))


def create_canvas(cols: int, rows: int) -> list[list[str]]:
    """Create an empty ASCII canvas."""
    return [[" " for _ in range(cols)] for _ in range(rows)]


def draw_horizontal(canvas: list[list[str]], y: int, x0: int, x1: int, char: str) -> None:
    for x in range(x0, x1 + 1):
        canvas[y][x] = char


def draw_vertical(canvas: list[list[str]], x: int, y0: int, y1: int, char: str) -> None:
    for y in range(y0, y1 + 1):
        canvas[y][x] = char


def draw_rectangle(canvas: list[list[str]], left: int, top: int, right: int, bottom: int, border_char: str) -> None:
    draw_horizontal(canvas, top, left, right, border_char)
    draw_horizontal(canvas, bottom, left, right, border_char)
    draw_vertical(canvas, left, top, bottom, border_char)
    draw_vertical(canvas, right, top, bottom, border_char)
    canvas[top][left] = "+"
    canvas[top][right] = "+"
    canvas[bottom][left] = "+"
    canvas[bottom][right] = "+"


def place_label(canvas: list[list[str]], x: int, y: int, text: str) -> None:
    cols = len(canvas[0])
    for i, ch in enumerate(text):
        xx = x + i
        if 0 <= xx < cols:
            canvas[y][xx] = ch


def mark_points(canvas: list[list[str]], points: Iterable[Tuple[int, int]], marker: str) -> None:
    cols = len(canvas[0])
    rows = len(canvas)
    for x, y in points:
        if 0 <= x < cols and 0 <= y < rows:
            canvas[y][x] = marker


def build_layout() -> list[str]:
    cols = mm_to_units(BOARD_WIDTH_MM) + 1
    rows = mm_to_units(BOARD_HEIGHT_MM) + 1
    margin = mm_to_units(MARGIN_MM)

    canvas = create_canvas(cols, rows)

    left = margin
    right = cols - margin - 1
    top = margin
    bottom = rows - margin - 1

    draw_rectangle(canvas, left, top, right, bottom, "-")

    divider_x = left + mm_to_units(120.0)
    draw_vertical(canvas, divider_x, top, bottom, "|")
    place_label(canvas, divider_x - 5, top + 2, "HV KEEP-OUT")

    def zone_rect(x_mm: float, y_mm: float, w_mm: float, h_mm: float) -> tuple[int, int, int, int]:
        return (
            left + mm_to_units(x_mm),
            top + mm_to_units(y_mm),
            left + mm_to_units(x_mm + w_mm),
            top + mm_to_units(y_mm + h_mm),
        )

    zones = [
        (zone_rect(0, 0, 105, 60), "ESP32 + Touch"),
        (zone_rect(0, 65, 105, 55), "Power/Servos"),
        (zone_rect(110, 0, 90, 120), "16x Relays"),
        (zone_rect(5, 18, 30, 60), "J1"),
        (zone_rect(75, 18, 30, 60), "J2"),
        (zone_rect(145, 32, 30, 45), "J3"),
    ]

    for rect, label in zones:
        l, t, r, b = rect
        draw_rectangle(canvas, l, t, r, b, "=")
        label_x = l + 2
        label_y = t + (b - t) // 2
        place_label(canvas, label_x, label_y, label)

    hole_offset = mm_to_units(3.0)
    hole_points = [
        (left + hole_offset, top + hole_offset),
        (right - hole_offset, top + hole_offset),
        (left + hole_offset, bottom - hole_offset),
        (right - hole_offset, bottom - hole_offset),
    ]
    mark_points(canvas, hole_points, "O")

    legend_left = left + mm_to_units(135.0)
    legend_top = top + mm_to_units(5.0)
    legend_right = legend_left + mm_to_units(70.0)
    legend_bottom = legend_top + mm_to_units(40.0)
    draw_rectangle(canvas, legend_left, legend_top, legend_right, legend_bottom, ":")

    legend_entries = [
        "Legend:",
        "- Board outline",
        "= Zones",
        "| Keep-out / headers",
        "O Mount holes",
        "- Routed buses",
    ]
    for idx, entry in enumerate(legend_entries):
        place_label(canvas, legend_left + 2, legend_top + 2 + idx * 2, entry)

    # Illustrate routed headers and buses
    draw_header(canvas, 25.0, 20.0, 21, "J1 ESP32 ctrl", left, top)
    draw_header(canvas, 95.0, 20.0, 21, "J2 Driver", left, top)
    draw_header(canvas, 165.0, 32.7, 16, "J3 Load", left, top)

    bus_offsets_mm = [0, 2.54, 5.08, 7.62, 10.16] + [12.70 + 2.54 * i for i in range(16)]
    x_start = left + mm_to_units(25.0)
    x_mid = left + mm_to_units(95.0)
    x_end = left + mm_to_units(165.0)
    for offset_mm in bus_offsets_mm:
        y = top + mm_to_units(20.0 + offset_mm)
        draw_horizontal(canvas, y, x_start, x_mid, "-")
        if offset_mm >= 12.70:
            draw_horizontal(canvas, y, x_mid, x_end, "-")

    lines = ["".join(row).rstrip() for row in canvas]
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    return lines


def main() -> None:
    project_root = pathlib.Path(__file__).resolve().parents[1]
    output_path = project_root / "esp32_relay_board_detail.txt"
    lines = build_layout()
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote ASCII blueprint to {output_path}")


if __name__ == "__main__":
    main()
