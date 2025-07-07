# MenuTitle: Open Glyphs by Color Label
# -*- coding: utf-8 -*-
__doc__ = """
Lets you open all glyphs of a specified color in a new tab.
"""

import vanilla
import GlyphsApp

class ColorLabelTabOpener:
    def __init__(self):
        self.colorLabels = Glyphs.defaults["GSColorNames"] or [
            "Red", "Orange", "Brown", "Yellow", "Light Green", "Dark Green",
            "Light Blue", "Dark Blue", "Purple", "Magenta", "Light Gray", "Charcoal"
        ]

        height = 30 + len(self.colorLabels) * 22 + 50
        self.w = vanilla.FloatingWindow((300, height), "Open by Color Label")

        self.w.text = vanilla.TextBox((15, 15, -15, 20), "Select color labels to include:")

        self.checkboxes = []
        for i, label in enumerate(self.colorLabels):
            cb = vanilla.CheckBox((15, 40 + i * 22, -15, 20), label)
            setattr(self.w, f"cb_{i}", cb)
            self.checkboxes.append(cb)

        self.w.openTab = vanilla.Button((-100, -40, -15, 20), "Open Tab", callback=self.openTabCallback)
        self.w.setDefaultButton(self.w.openTab)
        self.w.open()

    def openTabCallback(self, sender):
        selectedColorIndexes = {i for i, cb in enumerate(self.checkboxes) if cb.get()}
        font = Glyphs.font
        if not font:
            Message("No font open", "Please open a font first.")
            return

        glyphNames = []
        for glyph in font.glyphs:
            if glyph.color is not None and glyph.color in selectedColorIndexes:
                glyphNames.append(glyph.name)

        if glyphNames:
            font.newTab("/" + "/".join(glyphNames))
        else:
            Message("No matches", "No glyphs found with the selected color labels.")

ColorLabelTabOpener()
