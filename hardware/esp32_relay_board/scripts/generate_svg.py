#!/usr/bin/env python3
"""Generate a simple SVG overview of the ESP32 relay board layout."""
from __future__ import annotations

import pathlib

def main() -> None:
    project_root = pathlib.Path(__file__).resolve().parents[1]
    svg_path = project_root / "esp32_relay_board.svg"

    width_mm = 220
    height_mm = 130

    content = f"""<?xml version='1.0' encoding='UTF-8'?>
<svg xmlns='http://www.w3.org/2000/svg' width='{width_mm}mm' height='{height_mm}mm' viewBox='0 0 {width_mm} {height_mm}' version='1.1'>
  <title>ESP32 Relay Controller Conceptual Layout</title>
  <desc>Simple overview generated without KiCad CLI for quick visualization.</desc>
  <defs>
    <style type='text/css'>
      <![CDATA[
        .outline {{ fill: none; stroke: #1f2933; stroke-width: 0.5; }}
        .zone {{ fill: none; stroke: #2563eb; stroke-width: 0.35; stroke-dasharray: 2 1; }}
        .label {{ font-family: "DejaVu Sans", Arial, sans-serif; font-size: 5px; fill: #111827; }}
        .divider {{ stroke: #ef4444; stroke-width: 0.4; stroke-dasharray: 1 1; }}
      ]]>
    </style>
  </defs>
  <!-- Board outline -->
  <rect class='outline' x='0' y='0' width='{width_mm}' height='{height_mm}' />
  <!-- Keep-out divider -->
  <line class='divider' x1='120' y1='5' x2='120' y2='{height_mm - 5}' />
  <!-- Functional zones -->
  <rect class='zone' x='5' y='5' width='105' height='60' />
  <rect class='zone' x='5' y='70' width='105' height='50' />
  <rect class='zone' x='125' y='5' width='90' height='120' />
  <rect class='zone' x='15' y='115' width='80' height='10' />
  <rect class='zone' x='135' y='115' width='70' height='10' />
  <!-- Labels -->
  <text class='label' x='18' y='30'>ESP32 + 3" Touch Display</text>
  <text class='label' x='18' y='95'>Power Entry / DC-DC / Servo PWM</text>
  <text class='label' x='138' y='30'>16x Relays (230VAC)</text>
  <text class='label' x='122' y='67' transform='rotate(-90 122 67)'>High Voltage Keep-out</text>
  <text class='label' x='20' y='123'>GPIO / I2C Expansion Headers</text>
  <text class='label' x='138' y='123'>Relay Output Terminal Blocks</text>
  <!-- Mounting holes -->
  <circle class='outline' cx='7' cy='7' r='3' />
  <circle class='outline' cx='{width_mm - 7}' cy='7' r='3' />
  <circle class='outline' cx='7' cy='{height_mm - 7}' r='3' />
  <circle class='outline' cx='{width_mm - 7}' cy='{height_mm - 7}' r='3' />
</svg>
"""

    svg_path.write_text(content, encoding="utf-8")
    print(f"Wrote conceptual SVG overview to {svg_path}")


if __name__ == "__main__":
    main()
