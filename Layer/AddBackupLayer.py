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
			backup.name = datetime.datetime.now().strftime("%d %b %y at %H:%M")
			glyph.layers.append(backup)

	Glyphs.redraw()
