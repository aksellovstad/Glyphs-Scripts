# MenuTitle: Open by Color Label
# -*- coding: utf-8 -*-
__doc__ = """
Open all glyphs with selected color labels in a new tab. Now with color swatches!
"""

import GlyphsApp
import vanilla
from AppKit import NSColor

# -----------------------------
# Palette helpers
# -----------------------------
def _nscolor_from_dict(d):
    try:
        r = float(d.get("r", 0.0))
        g = float(d.get("g", 0.0))
        b = float(d.get("b", 0.0))
        a = float(d.get("a", 1.0))
        return NSColor.colorWithCalibratedRed_green_blue_alpha_(r, g, b, a)
    except Exception:
        return NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 0, 0, 1)

def _fallback_palette():
    # Approximate classic Glyphs 12-color palette
    def C(r, g, b): return NSColor.colorWithCalibratedRed_green_blue_alpha_(r, g, b, 1.0)
    return [
        C(1.00, 0.33, 0.33),  # Red
        C(1.00, 0.60, 0.20),  # Orange
        C(0.60, 0.42, 0.26),  # Brown
        C(1.00, 0.90, 0.20),  # Yellow
        C(0.50, 0.85, 0.35),  # Light Green
        C(0.00, 0.55, 0.35),  # Dark Green
        C(0.45, 0.70, 1.00),  # Light Blue
        C(0.12, 0.32, 0.80),  # Dark Blue
        C(0.60, 0.44, 0.82),  # Purple
        C(0.98, 0.30, 0.80),  # Magenta
        C(0.82, 0.82, 0.86),  # Light Gray
        C(0.22, 0.22, 0.25),  # Charcoal
    ]

def _load_palette():
    names = Glyphs.defaults.get("GSColorNames") or [
        "Red", "Orange", "Brown", "Yellow", "Light Green", "Dark Green",
        "Light Blue", "Dark Blue", "Purple", "Magenta", "Light Gray", "Charcoal"
    ]
    values = Glyphs.defaults.get("GSColorValues")
    colors = []
    if values and isinstance(values, (list, tuple)) and len(values) >= len(names):
        for i in range(len(names)):
            try:
                colors.append(_nscolor_from_dict(values[i]))
            except Exception:
                colors.append(_fallback_palette()[i % 12])
    else:
        fp = _fallback_palette()
        for i in range(len(names)):
            colors.append(fp[i % 12])
    n = min(len(names), len(colors))
    return names[:n], colors[:n]

# -----------------------------
# UI
# -----------------------------
class ColorLabelTabOpener:
    def __init__(self):
        self.colorLabels, self.colorNSColors = _load_palette()

        row_h = 22
        content_top = 38
        bottom_pad = 52
        total_h = content_top + len(self.colorLabels) * row_h + bottom_pad
        win_h = min(max(180, total_h), 600)  # cap height for long lists

        self.w = vanilla.FloatingWindow((340, win_h), "Open by Color Label")
        self.w.text = vanilla.TextBox((15, 12, -15, 20), "Select color labels to include:")

        self.checkboxes = []

        # If everything fits, lay out directly; else, use a ScrollView
        visible_rows = int((win_h - content_top - bottom_pad) / row_h)
        if len(self.colorLabels) <= max(visible_rows, 0):
            self._buildStaticArea(content_top, row_h)
        else:
            self._buildScrollArea(content_top, row_h, bottom_pad)

        self.w.openTab = vanilla.Button((-120, -36, -15, 24), "Open Tab", callback=self.openTabCallback)
        self.w.setDefaultButton(self.w.openTab)
        self.w.open()

    def _buildStaticArea(self, y0, row_h):
        for i, label in enumerate(self.colorLabels):
            y = y0 + i * row_h
            sw = vanilla.ColorWell((15, y + 2, 18, 18), color=self.colorNSColors[i])
            sw.enable(False)  # show-only
            setattr(self.w, f"sw_{i}", sw)

            cb = vanilla.CheckBox((40, y, -15, 20), label)
            setattr(self.w, f"cb_{i}", cb)
            self.checkboxes.append(cb)

    def _buildScrollArea(self, y0, row_h, bottom_pad):
        inner_h = len(self.colorLabels) * row_h
        # Document view first (the content we scroll)
        self.w.group = vanilla.Group((0, 0, -0, inner_h))
        # Create the ScrollView by passing the document view at init
        self.w.scroll = vanilla.ScrollView(
            (10, y0, -10, -bottom_pad),
            self.w.group
        )
        # Ask for vertical scroller explicitly (robust across builds)
        try:
            nsScroll = self.w.scroll.getNSScrollView()
            nsScroll.setHasVerticalScroller_(True)
            nsScroll.setAutohidesScrollers_(True)
        except Exception:
            pass

        for i, label in enumerate(self.colorLabels):
            y = i * row_h
            sw = vanilla.ColorWell((5, y + 2, 18, 18), color=self.colorNSColors[i])
            sw.enable(False)
            setattr(self.w.group, f"sw_{i}", sw)

            cb = vanilla.CheckBox((30, y, 260, 20), label)
            setattr(self.w.group, f"cb_{i}", cb)
            self.checkboxes.append(cb)

    def openTabCallback(self, sender):
        selectedColorIndexes = {i for i, cb in enumerate(self.checkboxes) if cb.get()}

        font = Glyphs.font
        if not font:
            try:
                Glyphs.showNotification("Open by Color Label", "No font open.")
            except Exception:
                print("Open by Color Label: No font open.")
            return

        glyphNames = []
        for glyph in font.glyphs:
            c = glyph.color
            if c is not None and c in selectedColorIndexes:
                glyphNames.append(glyph.name)

        if glyphNames:
            font.newTab("/" + "/".join(glyphNames))
        else:
            try:
                Glyphs.showNotification("Open by Color Label", "No glyphs found with the selected color labels.")
            except Exception:
                print("Open by Color Label: No matches.")

ColorLabelTabOpener()
