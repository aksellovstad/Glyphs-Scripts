#MenuTitle: Add Backup Layer
# -*- coding: utf-8 -*-
from GlyphsApp import *
import datetime

font = Glyphs.font
if font:
    processed = set()
    timestamp = datetime.datetime.now().strftime("%d %b %y at %H:%M")

    for layer in font.selectedLayers:
        glyph = layer.parent
        if glyph and glyph.name not in processed:
            backup = layer.copy()
            backup.name = timestamp
            glyph.layers.append(backup)
            processed.add(glyph.name)

    Glyphs.redraw()
