# MenuTitle: Open All Permutations
# -*- coding: utf-8 -*-

from GlyphsApp import Glyphs
from itertools import product
from AppKit import NSAlert, NSAlertFirstButtonReturn

PAIR_WARNING_THRESHOLD = 3000


def main():
    font = Glyphs.font
    if not font:
        print("No font open.")
        return

    layers = font.selectedLayers
    if not layers:
        print("No glyphs selected.")
        return

    # collect unique glyph names while preserving order
    glyphNames = list(dict.fromkeys(layer.parent.name for layer in layers))

    n = len(glyphNames)
    pairCount = n * n

    # warn user if the result will be large
    if pairCount > PAIR_WARNING_THRESHOLD:
        alert = NSAlert.alloc().init()
        alert.setMessageText_("Large Permutation Set")
        alert.setInformativeText_(
            f"You are about to generate {pairCount} glyph pairs "
            f"from {n} unique glyphs.\n\n"
            "This may take some time or make Glyphs unresponsive.\n\n"
            "Do you want to continue?"
        )
        alert.addButtonWithTitle_("Continue")
        alert.addButtonWithTitle_("Cancel")

        response = alert.runModal()

        if response != NSAlertFirstButtonReturn:
            print("Operation cancelled.")
            return

    # generate permutations efficiently
    tabText = " ".join(
        f"/{left}/{right}" for left, right in product(glyphNames, glyphNames)
    )

    font.newTab(tabText)

    print(f"Opened tab with {pairCount} pairs from {n} glyphs.")


main()