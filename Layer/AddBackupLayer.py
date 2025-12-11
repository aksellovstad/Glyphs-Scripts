#MenuTitle: Add Backup Layer
# -*- coding: utf-8 -*-
from GlyphsApp import *
import datetime

font = Glyphs.font
if font:
	for layer in font.selectedLayers:
		glyph = layer.parent
		if glyph:
			backup = layer.copy()
			now = datetime.datetime.now()
			backup.name = f"{now.day} {now.strftime('%b %y at %H:%M')}"
			glyph.layers.append(backup)
			print(f"✅ Backup layer added: {glyph.name}")

	Glyphs.redraw()
