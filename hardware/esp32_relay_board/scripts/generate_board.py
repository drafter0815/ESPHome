#!/usr/bin/env python3
"""Generate the esp32_relay_board.kicad_pcb layout using KiCad's pcbnew python API."""
from __future__ import annotations

import pathlib
import sys

sys.path.append("/usr/lib/python3/dist-packages")

import pcbnew

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
BOARD_PATH = PROJECT_ROOT / "esp32_relay_board.kicad_pcb"

MM = 1_000_000  # internal KiCad units (nm) per mm


def mm(value: float) -> int:
    return int(round(value * MM))


def add_rect(board: pcbnew.BOARD, layer: int, origin: tuple[float, float], size: tuple[float, float]) -> pcbnew.PCB_SHAPE:
    shape = pcbnew.PCB_SHAPE(board)
    shape.SetShape(pcbnew.SHAPE_T_RECT)
    shape.SetLayer(layer)
    start_x, start_y = origin
    width, height = size
    shape.SetStart(pcbnew.VECTOR2I(mm(start_x), mm(start_y)))
    shape.SetEnd(pcbnew.VECTOR2I(mm(start_x + width), mm(start_y + height)))
    board.Add(shape)
    return shape


def add_text(board: pcbnew.BOARD, text: str, position: tuple[float, float], layer: int = pcbnew.Cmts_User, size: float = 3.0, thickness: float = 0.4) -> pcbnew.PCB_TEXT:
    text_item = pcbnew.PCB_TEXT(board)
    text_item.SetLayer(layer)
    text_item.SetText(text)
    text_item.SetPosition(pcbnew.VECTOR2I(mm(position[0]), mm(position[1])))
    text_item.SetTextHeight(mm(size))
    text_item.SetTextWidth(mm(size))
    text_item.SetTextThickness(mm(thickness))
    board.Add(text_item)
    return text_item


def add_mounting_hole(board: pcbnew.BOARD, position: tuple[float, float], drill: float = 3.2, diameter: float = 6.0) -> pcbnew.PCB_SHAPE:
    hole = pcbnew.PCB_SHAPE(board)
    hole.SetShape(pcbnew.SHAPE_T_CIRCLE)
    hole.SetLayer(pcbnew.Edge_Cuts)
    hole.SetStart(pcbnew.VECTOR2I(mm(position[0]), mm(position[1])))
    hole.SetEnd(pcbnew.VECTOR2I(mm(position[0] + diameter / 2), mm(position[1])))
    hole.SetWidth(mm(0.15))
    board.Add(hole)
    return hole


def configure_board_metadata(board: pcbnew.BOARD) -> None:
    title = board.GetTitleBlock()
    title.SetTitle("ESP32 Relay Controller (Concept)")
    title.SetDate("Generated via kicad-cli")
    title.SetComment(0, "Auto-generated placement and keep-out guide")
    board.GetDesignSettings().m_AuxOrigin = pcbnew.VECTOR2I(mm(10), mm(10))
    board.GetDesignSettings().SetBoardThickness(mm(1.6))


def build_board() -> pcbnew.BOARD:
    board = pcbnew.BOARD()
    configure_board_metadata(board)

    # Define board outline 220mm x 130mm starting at origin (0,0)
    outline = add_rect(board, pcbnew.Edge_Cuts, (0.0, 0.0), (220.0, 130.0))
    outline.SetWidth(mm(0.15))

    # Draw keep-out divider between high voltage and logic domains
    hv_divider = pcbnew.PCB_SHAPE(board)
    hv_divider.SetShape(pcbnew.SHAPE_T_SEGMENT)
    hv_divider.SetLayer(pcbnew.Cmts_User)
    hv_divider.SetStart(pcbnew.VECTOR2I(mm(120.0), mm(5.0)))
    hv_divider.SetEnd(pcbnew.VECTOR2I(mm(120.0), mm(125.0)))
    hv_divider.SetWidth(mm(0.2))
    board.Add(hv_divider)

    # Zones for major functional blocks
    add_rect(board, pcbnew.Cmts_User, (5.0, 5.0), (105.0, 60.0)).SetWidth(mm(0.12))  # ESP32 + Display
    add_rect(board, pcbnew.Cmts_User, (5.0, 70.0), (105.0, 50.0)).SetWidth(mm(0.12))  # Power + Servo
    add_rect(board, pcbnew.Cmts_User, (125.0, 5.0), (90.0, 120.0)).SetWidth(mm(0.12))  # Relays / AC

    # Annotate text labels
    add_text(board, "ESP32 + 3\" Touch Display", (15.0, 30.0))
    add_text(board, "Power Entry / DC-DC / Servo PWM", (15.0, 95.0))
    add_text(board, "16x Relays (230VAC)", (145.0, 30.0))
    add_text(board, "High Voltage Keep-out", (120.0, 65.0), layer=pcbnew.Cmts_User, size=2.5)

    # Mounting holes at corners
    add_mounting_hole(board, (7.0, 7.0))
    add_mounting_hole(board, (213.0, 7.0))
    add_mounting_hole(board, (7.0, 123.0))
    add_mounting_hole(board, (213.0, 123.0))

    # Indicate header rows for I/O and servos
    add_rect(board, pcbnew.Cmts_User, (15.0, 115.0), (80.0, 10.0)).SetWidth(mm(0.1))
    add_text(board, "GPIO / I2C Expansion Headers", (20.0, 120.0), size=2.5)

    add_rect(board, pcbnew.Cmts_User, (135.0, 115.0), (70.0, 10.0)).SetWidth(mm(0.1))
    add_text(board, "Relay Output Terminal Blocks", (138.0, 120.0), size=2.5)

    hv_keepout = add_rect(board, pcbnew.Cmts_User, (125.0, 5.0), (90.0, 120.0))
    hv_keepout.SetWidth(mm(0.15))

    return board


def main() -> None:
    board = build_board()
    pcbnew.SaveBoard(str(BOARD_PATH), board)
    print(f"Generated board at {BOARD_PATH}")


if __name__ == "__main__":
    main()
