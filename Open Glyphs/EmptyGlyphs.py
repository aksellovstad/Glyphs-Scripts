# MenuTitle: Open Empty Glyphs in Current Master
# -*- coding: utf-8 -*-
__doc__ = """
Opens a new tab with all glyphs that are empty (no paths or components) in the current master.
"""

import GlyphsApp
from vanilla.dialogs import message

INTENTIONALLY_EMPTY = {
    "space", "nbspace", "nonbreakingspace", "zerowidthspace", "zwsp",
    "tab", "cr", "nl", "paragraph", "newline", "softhyphen",
}

def openEmptyGlyphs():
    font = Glyphs.font
    if not font:
        return

    master = font.selectedFontMaster
    emptyGlyphNames = []

    for glyph in font.glyphs:
        if not glyph.export or glyph.name in INTENTIONALLY_EMPTY:
            continue

        layer = glyph.layers[master.id]
        if not layer.paths and not layer.components:
            emptyGlyphNames.append(f"/{glyph.name}")

    if not emptyGlyphNames:
        message("No empty glyphs 🎉", "All glyphs have content in this master.")
        return

    font.newTab(" ".join(emptyGlyphNames))

openEmptyGlyphs()
