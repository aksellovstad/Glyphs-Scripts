# MenuTitle: Class Suggester
# -*- coding: utf-8 -*-
from GlyphsApp import Glyphs
from collections import defaultdict

Glyphs.showMacroWindow()

font = Glyphs.font
if not font:
    print("No font open.")
    raise SystemExit

glyph_names = [g.name for g in font.glyphs if g.name]

groups = defaultdict(list)

for name in glyph_names:
    if "." in name:
        base = name.split(".", 1)[0]
        groups[base].append(name)

print("— Suggested classes —\n")

for base in sorted(groups):
    if base in glyph_names:
        members = [base] + sorted(groups[base])
        print(f"@{base}\t= [{' '.join(members)}];")
