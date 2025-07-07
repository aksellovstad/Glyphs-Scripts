# MenuTitle: AaBbCcDdEeFf
# -*- coding: utf-8 -*-
__doc__ = """
Opens a new tab with a visually balanced Aa–Zz string in four lines.
"""

import GlyphsApp

def insertBalancedAlphabet():
    lines = [
        "AaBbCcDdEeFf",
        "GgHhIiJjKkLlMm",
        "NnOoPpQqRrSs",
        "TtUuVvWwXxYyZz"
    ]
    text = "\n".join(lines)

    font = Glyphs.font
    tab = font.newTab(text)

    # Optional: set text size
    if tab and tab.layers:
        try:
            tab.layers[0].setDisplaySize_(70.0)
        except Exception as e:
            Glyphs.showNotification("Couldn't set size", str(e))

insertBalancedAlphabet()
