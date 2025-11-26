# MenuTitle: Open Incompatible Glyphs
# -*- coding: utf-8 -*-

import GlyphsApp

font = Glyphs.font
if not font:
    Glyphs.showNotification("No Font Open", "Open a font first.")
else:
    incompatible = [g for g in font.glyphs if not g.mastersCompatible]

    if incompatible:
        tabString = " ".join("/" + g.name for g in incompatible)
        font.newTab(tabString)
    else:
        Glyphs.showNotification("No Incompatible Glyphs", "All glyphs are compatible across masters.")
