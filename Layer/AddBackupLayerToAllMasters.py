#MenuTitle: Add Backup Layer to All Masters
# -*- coding: utf-8 -*-
from GlyphsApp import *
import datetime

font = Glyphs.font
if not font:
    raise ValueError("No font open")

now = datetime.datetime.now()
timestamp = f"{now.day} {now.strftime('%b %y at %H:%M')}"

processedGlyphs = set()

for layer in font.selectedLayers:
    glyph = layer.parent
    if not glyph or glyph in processedGlyphs:
        continue

    processedGlyphs.add(glyph)

    for master in font.masters:
        masterLayer = glyph.layers[master.id]
        if not masterLayer:
            continue

        backup = masterLayer.copy()
        backup.name = timestamp
        glyph.layers.append(backup)

    print(f"✅Backup layers added to all masters: {glyph.name}")

Glyphs.redraw()
