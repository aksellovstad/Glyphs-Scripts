#MenuTitle: Highest & Lowest Glyphs
# -*- coding: utf-8 -*-

from GlyphsApp import Glyphs

maxY = None
minY = None
highest = None
lowest = None

font = Glyphs.font

for glyph in font.glyphs:
    for layer in glyph.layers:
        if not layer.isMasterLayer:
            continue

        top = layer.bounds.origin.y + layer.bounds.size.height
        bottom = layer.bounds.origin.y

        if maxY is None or top > maxY:
            maxY = top
            highest = layer

        if minY is None or bottom < minY:
            minY = bottom
            lowest = layer

print("highest: %s" % maxY)
print("lowest: %s" % minY)

if highest and lowest:
    font.newTab([highest, lowest])