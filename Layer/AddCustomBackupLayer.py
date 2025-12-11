#MenuTitle: Add Custom Backup Layer
# -*- coding: utf-8 -*-
from GlyphsApp import *

font = Glyphs.font
name = GlyphsApp.AskString("Enter name for the new backup layer:", "")

if name:
	for layer in font.selectedLayers:
		g = layer.parent
		if g:
			backup = layer.copy()
			backup.name = name
			g.layers.append(backup)
			print(f"✅ Backup layer added: {g.name}")

	Glyphs.redraw()
