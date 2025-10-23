#!/usr/bin/env python3
"""Generate a routed esp32_relay_board.kicad_pcb without requiring pcbnew."""
from __future__ import annotations

import pathlib
import uuid

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
BOARD_PATH = PROJECT_ROOT / "esp32_relay_board.kicad_pcb"

PITCH = 2.54  # mm spacing for 1xN pin headers


def uid() -> str:
    return str(uuid.uuid4())


def net_section(net_names: list[str]) -> tuple[str, dict[str, int]]:
    lines = ["  (net 0 \"\")"]
    mapping: dict[str, int] = {}
    for index, name in enumerate(net_names, start=1):
        mapping[name] = index
        lines.append(f"  (net {index} \"{name}\")")
    return "\n".join(lines), mapping


def net_class_section(net_names: list[str]) -> str:
    header = [
        "  (net_class \"Default\" \"This is the default net class.\"",
        "    (clearance 0.3)",
        "    (trace_width 1.0)",
        "    (via_dia 1.5)",
        "    (via_drill 0.8)",
        "    (uvia_dia 0.3)",
        "    (uvia_drill 0.1)",
    ]
    additions = [f"    (add_net \"{name}\")" for name in net_names]
    footer = ["  )"]
    return "\n".join(header + additions + footer)


def footprint_pin_header(
    ref: str,
    value: str,
    at_x: float,
    at_y: float,
    nets: list[str],
    net_map: dict[str, int],
) -> str:
    n_pins = len(nets)
    tstamp = uid()
    lines: list[str] = [
        f"  (footprint \"Custom:PinHeader_1x{n_pins}_P2.54mm\" (layer \"F.Cu\") (tstamp {tstamp})",
        f"    (at {at_x:.2f} {at_y:.2f})",
        "    (attr through_hole)",
        f"    (fp_text reference \"{ref}\" (at 0 -2.6) (layer \"F.SilkS\")",
        "      (effects (font (size 1 1) (thickness 0.15))))",
        f"    (fp_text value \"{value}\" (at 0 {PITCH * (n_pins + 1) / 2:.2f}) (layer \"F.Fab\")",
        "      (effects (font (size 1 1) (thickness 0.15))))",
        "    (fp_text user \"${REFERENCE}\" (at 0 0) (layer \"F.Fab\")",
        "      (effects (font (size 1 1) (thickness 0.15))))",
    ]

    for index, net_name in enumerate(nets, start=1):
        y_offset = PITCH * (index - 1)
        shape = "rect" if index == 1 else "oval"
        net_idx = net_map[net_name]
        pad = (
            f"    (pad \"{index}\" thru_hole {shape} (at 0 {y_offset:.2f}) (size 1.7 1.7) (drill 1) "
            "(layers \"*.Cu\" \"*.Mask\")"
            f" (net {net_idx} \"{net_name}\"))"
        )
        lines.append(pad)

    lines.append("  )")
    return "\n".join(lines)


def track_segment(net_idx: int, start: tuple[float, float], end: tuple[float, float], width: float = 1.0) -> str:
    x0, y0 = start
    x1, y1 = end
    return (
        f"  (segment (start {x0:.2f} {y0:.2f}) (end {x1:.2f} {y1:.2f}) "
        f"(width {width:.2f}) (layer \"F.Cu\") (net {net_idx}) (tstamp {uid()}))"
    )


def outline_and_guides() -> str:
    items = [
        "  (gr_rect (start 0 0) (end 220 130) (stroke (width 0.15) (type default)) (fill none) (layer \"Edge.Cuts\") (tstamp "
        f"{uid()}))",
        "  (gr_line (start 120 5) (end 120 125) (stroke (width 0.2) (type default)) (layer \"Cmts.User\") (tstamp "
        f"{uid()}))",
        "  (gr_text \"ESP32 + Touch\" (at 25 30) (layer \"Cmts.User\") (tstamp "
        f"{uid()}) (effects (font (size 3 3) (thickness 0.4))))",
        "  (gr_text \"Power & Servos\" (at 25 95) (layer \"Cmts.User\") (tstamp "
        f"{uid()}) (effects (font (size 3 3) (thickness 0.4))))",
        "  (gr_text \"16x Relay Outputs\" (at 150 40) (layer \"Cmts.User\") (tstamp "
        f"{uid()}) (effects (font (size 3 3) (thickness 0.4))))",
    ]
    for pos in [(7, 7), (213, 7), (7, 123), (213, 123)]:
        x, y = pos
        items.append(
            "  (gr_circle (center {x} {y}) (end {ex} {y}) (stroke (width 0.15) (type default)) "
            "(fill none) (layer \"Edge.Cuts\") (tstamp {tstamp}))".format(
                x=x, y=y, ex=x + 3, tstamp=uid()
            )
        )
    return "\n".join(items)


def build_board() -> str:
    relay_nets = [f"RELAY{i:02d}" for i in range(1, 17)]
    net_names = ["GND", "V5", "V12", "SCL", "SDA"] + relay_nets
    net_section_str, net_map = net_section(net_names)

    # Connector definitions
    j1_nets = ["GND", "V5", "V12", "SCL", "SDA"] + relay_nets
    j2_nets = j1_nets.copy()
    j3_nets = relay_nets

    footprints = [
        footprint_pin_header("J1", "ESP32_CTRL", 25.0, 20.0, j1_nets, net_map),
        footprint_pin_header("J2", "RELAY_DRIVER", 95.0, 20.0, j2_nets, net_map),
        footprint_pin_header("J3", "LOAD_HEADER", 165.0, 32.70, j3_nets, net_map),
    ]

    # Track routing
    tracks: list[str] = []

    def pad_position(x: float, y: float, index: int) -> tuple[float, float]:
        return x, y + PITCH * (index - 1)

    # Route shared control nets between J1 and J2
    for idx, net_name in enumerate(["GND", "V5", "V12", "SCL", "SDA"], start=1):
        net_idx = net_map[net_name]
        start = pad_position(25.0, 20.0, idx)
        end = pad_position(95.0, 20.0, idx)
        tracks.append(track_segment(net_idx, start, end, width=1.2 if net_name in {"GND", "V5", "V12"} else 0.8))

    # Route each relay signal across all headers
    for relay_index, net_name in enumerate(relay_nets, start=6):
        net_idx = net_map[net_name]
        start = pad_position(25.0, 20.0, relay_index)
        mid = pad_position(95.0, 20.0, relay_index)
        end = pad_position(165.0, 32.70, relay_index - 5)
        tracks.append(track_segment(net_idx, start, mid, width=0.9))
        tracks.append(track_segment(net_idx, mid, end, width=0.9))

    board_elements = "\n".join(footprints + [outline_and_guides()] + tracks)

    header = "\n".join(
        [
            "(kicad_pcb (version 20221018) (generator \"generate_board.py\")",
            "  (general",
            "    (thickness 1.6)",
            "  )",
            "  (paper \"A4\")",
            "  (title_block",
            "    (title \"ESP32 Relay Controller Routed Concept\")",
            "    (company \"Auto-generated in container\")",
            "    (rev \"A1\")",
            "  )",
            "  (layers",
            "    (0 \"F.Cu\" signal)",
            "    (31 \"B.Cu\" signal)",
            "    (44 \"Edge.Cuts\" user)",
            "    (49 \"F.Fab\" user)",
            "    (51 \"User.2\" user)",
            "    (52 \"User.3\" user)",
            "    (53 \"User.4\" user)",
            "    (54 \"User.5\" user)",
            "    (55 \"User.6\" user)",
            "    (56 \"User.7\" user)",
            "    (57 \"User.8\" user)",
            "    (58 \"User.9\" user)",
            "  )",
            "  (setup",
            "    (pad_to_mask_clearance 0)",
            "    (pcbplotparams",
            "      (layerselection 0x00010fc_ffffffff)",
            "      (plot_on_all_layers_selection 0x0000000_00000000)",
            "      (disableapertmacros false)",
            "      (usegerberextensions false)",
            "      (usegerberattributes true)",
            "      (usegerberadvancedattributes true)",
            "      (creategerberjobfile true)",
            "      (svgprecision 4)",
            "      (plotreference true)",
            "      (plotvalue true)",
            "      (plotinvisibletext false)",
            "      (sketchpadsonfab false)",
            "      (subtractmaskfromsilk false)",
            "      (outputformat 1)",
            "      (mirror false)",
            "      (drillshape 1)",
            "      (scaleselection 1)",
            "      (outputdirectory \"\")",
            "    )",
            "  )",
            net_section_str,
            net_class_section(net_names),
        ]
    )

    return header + "\n" + board_elements + "\n)\n"


def main() -> None:
    board_text = build_board()
    BOARD_PATH.write_text(board_text, encoding="utf-8")
    print(f"Wrote {BOARD_PATH}")


if __name__ == "__main__":
    main()
