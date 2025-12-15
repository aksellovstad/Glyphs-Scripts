#MenuTitle: Add Custom Backup Layer
# -*- coding: utf-8 -*-
from GlyphsApp import *

font = Glyphs.font
name = AskString("Enter name for the new backup layer:", "")

if name:
	processedGlyphs = set()

	for layer in font.selectedLayers:
		g = layer.parent
		if not g or g in processedGlyphs:
			continue

		processedGlyphs.add(g)

		backup = layer.copy()
		backup.name = name
		g.layers.append(backup)

		print(f"✅ Backup layer added: {g.name}")

	Glyphs.redraw()
