# MenuTitle: HHHAHHH HHHaHHH
# -*- coding: utf-8 -*-
__doc__ = """
Opens two tabs with spacing strings: one with uppercase A–Z in the center (e.g. HHHAHHH), and one with lowercase a–z (e.g. HHHaHHH).
"""

import GlyphsApp

def insertSpacingStrings():
    uppercase_lines = [f"HHH{chr(i)}HHH" for i in range(ord("A"), ord("Z") + 1)]
    lowercase_lines = [f"HHH{chr(i)}HHH" for i in range(ord("a"), ord("z") + 1)]
    figure_lines = [f"HHH{chr(i)}HHH" for i in range(ord("0"), ord("9") + 1)]

    font = Glyphs.font
    if not font:
        return

    tab1 = font.newTab("\n".join(uppercase_lines))
    tab2 = font.newTab("\n".join(lowercase_lines))
    tab2 = font.newTab("\n".join(figure_lines))

insertSpacingStrings()
