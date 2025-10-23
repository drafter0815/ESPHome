#!/usr/bin/env python3
import argparse
import math
import uuid
from pathlib import Path
from sexpdata import loads, Symbol, dumps

MIL_TO_MM = 0.0254
DEFAULT_FONT = (1.8, 1.8)
DEFAULT_LABEL_FONT = (1.5, 1.5)

LIB_CACHE = {}


def load_symbol(lib_name, sym_name):
    key = (lib_name, sym_name)
    if key in LIB_CACHE:
        return LIB_CACHE[key]
    lib_path = Path(f"/usr/share/kicad/symbols/{lib_name}.kicad_sym")
    if lib_path.exists():
        data = loads(lib_path.read_text())
        for item in data[1:]:
            if isinstance(item, list) and len(item) > 1 and item[0] == Symbol('symbol') and item[1] == sym_name:
                LIB_CACHE[key] = item
                return item
    # fallback placeholder symbol
    placeholder = [
        Symbol('symbol'), f'{lib_name}:{sym_name}',
        [Symbol('property'), 'Reference', 'REF**',
         [Symbol('at'), 0, 2.54, 0],
         [Symbol('effects'), [Symbol('font'), [Symbol('size'), 1.27, 1.27]]]],
        [Symbol('property'), 'Value', sym_name,
         [Symbol('at'), 0, -2.54, 0],
         [Symbol('effects'), [Symbol('font'), [Symbol('size'), 1.27, 1.27]]]],
        [Symbol('property'), 'Footprint', '',
         [Symbol('at'), 0, 0, 0],
         [Symbol('effects'), [Symbol('font'), [Symbol('size'), 1.27, 1.27]]], Symbol('hide')],
        [Symbol('property'), 'Datasheet', '',
         [Symbol('at'), 0, 0, 0],
         [Symbol('effects'), [Symbol('font'), [Symbol('size'), 1.27, 1.27]]], Symbol('hide')],
        [Symbol('pin'), Symbol('passive'), Symbol('line'),
         [Symbol('at'), -5.08, 0, 0],
         [Symbol('length'), 2.54]],
        [Symbol('pin'), Symbol('passive'), Symbol('line'),
         [Symbol('at'), 5.08, 0, 180],
         [Symbol('length'), 2.54]],
    ]
    LIB_CACHE[key] = placeholder
    return placeholder


def mil_to_mm(val):
    return round(val * MIL_TO_MM, 4)


def fmt_float(val):
    txt = f"{val:.6f}"
    txt = txt.rstrip('0').rstrip('.')
    if txt == '':
        return '0'
    return txt


def orientation_to_angle(code):
    mapping = {
        0: 0,
        1: 90,
        2: 180,
        3: 270,
    }
    return mapping.get(code, 0)


def shape_from_type(label_type):
    mapping = {
        'Input': 'input',
        'Output': 'output',
        'BiDi': 'bidirectional',
        'Passive': 'passive',
    }
    return mapping.get(label_type, 'passive')


def parse_legacy(path: Path):
    data = {
        'title': None,
        'comments': {},
        'components': [],
        'texts': [],
        'glabels': [],
        'wires': [],
        'junctions': [],
        'sheets': [],
    }
    lines = path.read_text().splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith('Title '):
            data['title'] = line.split('"')[1]
        elif line.startswith('Comment'):
            parts = line.split()
            idx = int(parts[0][7:])
            data['comments'][idx] = line.split('"')[1]
        elif line.startswith('$Comp'):
            comp = {'fields': {}}
            i += 1
            while i < len(lines) and not lines[i].startswith('$EndComp'):
                parts = lines[i].split()
                tag = parts[0]
                if tag == 'L':
                    comp['lib_id'] = parts[1]
                    comp['ref'] = parts[2]
                elif tag == 'U':
                    comp['unit'] = parts[1]
                elif tag == 'P':
                    comp['pos'] = (int(parts[1]), int(parts[2]))
                elif tag == 'F':
                    idx = parts[1]
                    value = lines[i].split('"')[1]
                    comp['fields'][idx] = value
                i += 1
            data['components'].append(comp)
        elif line.startswith('Text Notes'):
            parts = line.split()
            x, y = int(parts[2]), int(parts[3])
            orientation = int(parts[4])
            text = lines[i+1]
            data['texts'].append({'pos': (x, y), 'orientation': orientation, 'text': text})
            i += 1
        elif line.startswith('Text GLabel'):
            parts = line.split()
            x, y = int(parts[2]), int(parts[3])
            orientation = int(parts[4])
            size = int(parts[5])
            ltype = parts[6]
            text = lines[i+1]
            data['glabels'].append({'pos': (x, y), 'orientation': orientation, 'size': size, 'kind': ltype, 'text': text})
            i += 1
        elif line.startswith('Wire Wire Line'):
            coords = list(map(int, lines[i+1].split()))
            data['wires'].append(coords)
            i += 1
        elif line.startswith('Connection ~'):
            parts = line.split()
            x, y = int(parts[2]), int(parts[3])
            data['junctions'].append((x, y))
        elif line.startswith('$Sheet'):
            sheet = {'pins': []}
            i += 1
            while i < len(lines) and not lines[i].startswith('$EndSheet'):
                parts = lines[i].split()
                tag = parts[0]
                if tag == 'S':
                    sheet['rect'] = tuple(map(int, parts[1:]))
                elif tag == 'U':
                    sheet['legacy_id'] = parts[1]
                elif tag == 'F0':
                    sheet['name'] = lines[i].split('"')[1]
                elif tag == 'F1':
                    sheet['file'] = lines[i].split('"')[1]
                elif tag.startswith('F') and tag not in ('F0', 'F1'):
                    pin_name = lines[i].split('"')[1]
                    pparts = lines[i].split()
                    pin_kind = pparts[3]
                    side = pparts[4]
                    px, py = int(pparts[5]), int(pparts[6])
                    sheet['pins'].append({'name': pin_name, 'kind': pin_kind, 'side': side, 'pos': (px, py)})
                i += 1
            data['sheets'].append(sheet)
        i += 1
    return data


def build_s_expr(data, include_sheets=True):
    out = []
    indent = 0

    def write(line=""):
        out.append("  " * indent + line)

    def start(line):
        nonlocal indent
        write(line)
        indent += 1

    def end():
        nonlocal indent
        indent -= 1
        write(")")

    write('(kicad_sch (version 20230121) (generator "legacy-upgrade"))')
    indent = 1
    write(f'(uuid {uuid.uuid4()})')
    write('(paper "A3")')
    start('(title_block)')
    if data['title']:
        write(f'(title "{data["title"]}")')
    for idx, text in sorted(data['comments'].items()):
        write(f'(comment (number {idx}) (value "{text}"))')
    end()

    # lib symbols
    start('(lib_symbols)')
    seen = set()
    for comp in data['components']:
        lib_name, sym_name = comp['lib_id'].split(':')
        if (lib_name, sym_name) in seen:
            continue
        seen.add((lib_name, sym_name))
        symbol_expr = load_symbol(lib_name, sym_name)
        symbol_text = dumps(symbol_expr)
        for line in symbol_text.split('\n'):
            write(line)
    end()

    # components
    for comp in data['components']:
        lib_id = comp['lib_id']
        x, y = comp['pos']
        x_mm, y_mm = fmt_float(mil_to_mm(x)), fmt_float(mil_to_mm(y))
        start(f'(symbol (lib_id "{lib_id}") (at {x_mm} {y_mm} 0) (unit 1)')
        write('(in_bom yes) (on_board yes) (dnp no)')
        write(f'(uuid {uuid.uuid4()})')
        ref = comp['ref']
        value = comp['fields'].get('1', '')
        ref_y = fmt_float(mil_to_mm(y - 300))
        val_y = fmt_float(mil_to_mm(y + 300))
        write(f'(property "Reference" "{ref}" (at {x_mm} {ref_y} 0) (effects (font (size 1.27 1.27)))))')
        write(f'(property "Value" "{value}" (at {x_mm} {val_y} 0) (effects (font (size 1.27 1.27)))))')
        end()

    # wires
    for (x1, y1, x2, y2) in data['wires']:
        start(f'(wire (pts (xy {fmt_float(mil_to_mm(x1))} {fmt_float(mil_to_mm(y1))}) (xy {fmt_float(mil_to_mm(x2))} {fmt_float(mil_to_mm(y2))}))')
        write('(stroke (width 0) (type solid))')
        write(f'(uuid {uuid.uuid4()})')
        end()

    # junctions
    for (jx, jy) in data['junctions']:
        write(f'(junction (at {fmt_float(mil_to_mm(jx))} {fmt_float(mil_to_mm(jy))}) (uuid {uuid.uuid4()}))')

    # texts
    for text in data['texts']:
        x_mm = fmt_float(mil_to_mm(text['pos'][0]))
        y_mm = fmt_float(mil_to_mm(text['pos'][1]))
        write(f'(text "{text["text"]}" (at {x_mm} {y_mm} {orientation_to_angle(text["orientation"])})')
        indent += 1
        write('(effects (font (size 2 2)) (justify left bottom))')
        write(f'(uuid {uuid.uuid4()})')
        indent -= 1
        write(')')

    # global labels
    for label in data['glabels']:
        x_mm = fmt_float(mil_to_mm(label['pos'][0]))
        y_mm = fmt_float(mil_to_mm(label['pos'][1]))
        angle = orientation_to_angle(label['orientation'])
        shape = shape_from_type(label['kind'])
        write(f'(global_label "{label["text"]}" (shape {shape}) (at {x_mm} {y_mm} {angle}))')
        indent += 1
        write('(effects (font (size 1.524 1.524)) (justify left))')
        write(f'(uuid {uuid.uuid4()})')
        write('(property "Intersheetrefs" "${INTERSHEET_REFS}" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
        indent -= 1
        write(')')

    if include_sheets and data['sheets']:
        for sheet in data['sheets']:
            rect = sheet.get('rect', (0, 0, 4000, 3000))
            at_x = fmt_float(mil_to_mm(rect[0]))
            at_y = fmt_float(mil_to_mm(rect[1]))
            size_w = fmt_float(mil_to_mm(rect[2]))
            size_h = fmt_float(mil_to_mm(rect[3]))
            start(f'(sheet (at {at_x} {at_y}) (size {size_w} {size_h})')
            write('(stroke (width 0) (type solid))')
            write('(fill (color 0 0 0 0))')
            write(f'(uuid {uuid.uuid4()})')
            write(f'(property "Sheetname" "{sheet.get("name", "Sheet")}" (at {at_x} {at_y} 0) (effects (font (size 1.524 1.524)) (justify left bottom)))')
            write(f'(property "Sheetfile" "{sheet.get("file", "")}" (at {at_x} {fmt_float(mil_to_mm(rect[1] + rect[3]))} 0) (effects (font (size 1.524 1.524)) (justify left top)))')
            write('(instances')
            indent += 1
            write('(project "legacy-upgrade")')
            indent += 1
            write(f'(path "/{uuid.uuid4()}" (page "2"))')
            indent -= 2
            write(')')
            # pins as text labels on sheet edge
            for pin in sheet['pins']:
                px = fmt_float(mil_to_mm(pin['pos'][0]))
                py = fmt_float(mil_to_mm(pin['pos'][1]))
                write(f'(text "{pin["name"]}" (at {px} {py} 0) (effects (font (size 1.5 1.5)) (justify left)))')
            end()

    start('(sheet_instances)')
    write('(path "/" (page "1"))')
    end()

    return '\n'.join(out) + '\n'


def main():
    parser = argparse.ArgumentParser(description="Convert legacy KiCad V4 schematics to KiCad 7 S-expr format")
    parser.add_argument('input', type=Path)
    parser.add_argument('-o', '--output', type=Path)
    parser.add_argument('--root', action='store_true', help='treat as root sheet and preserve hierarchical sheet blocks')
    args = parser.parse_args()
    data = parse_legacy(args.input)
    text = build_s_expr(data, include_sheets=args.root)
    out_path = args.output or args.input
    out_path.write_text(text)


if __name__ == '__main__':
    main()
