#MenuTitle: Open Unique Glyphs
# -*- coding: utf-8 -*-
__doc__ = """
Opens all glyphs that contain at least one path in any master layer.
"""

from GlyphsApp import Glyphs

font = Glyphs.font

if not font:
    print("No font open.\n")
else:
    glyphsWithPaths = []

    for glyph in font.glyphs:
        hasPaths = False

        for layer in glyph.layers:
            # Only check master layers (ignore special layers, backups, etc.)
            if not layer.isMasterLayer:
                continue

            if layer.paths and len(layer.paths) > 0:
                hasPaths = True
                break

        if hasPaths:
            glyphsWithPaths.append(glyph.name)

    if glyphsWithPaths:
        tabString = "/" + "/".join(glyphsWithPaths)
        font.newTab(tabString)
        print(f"Opened {len(glyphsWithPaths)} glyphs containing paths.\n")
    else:
        print("No glyphs with paths found.\n")
