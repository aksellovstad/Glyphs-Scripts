# MenuTitle: HHAaAHH 
# -*- coding: utf-8 -*-
__doc__ = """
Opens a new tab with spacing strings HHAaAHH through HHZzZHH containing every possible letter combination.
"""

import GlyphsApp

def generateSpacingStrings():
    strings = []

    for uc in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        for lc in "abcdefghijklmnopqrstuvwxyz":
            strings.append(f"HH{uc}{lc}{uc}HH")

    return strings

def insertSpacingTab():
    font = Glyphs.font
    if not font:
        return

    text = "\n".join(generateSpacingStrings())
    tab = font.newTab(text)

    # Optional: set display size to 70 pt
    if tab and tab.layers:
        try:
            tab.layers[0].setDisplaySize_(70.0)
        except Exception as e:
            Glyphs.showNotification("Couldn't set size", str(e))

insertSpacingTab()
