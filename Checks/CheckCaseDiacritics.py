#MenuTitle: Check .case Diacritics in Uppercase Letters
# -*- coding: utf-8 -*-
__doc__ = """
Checks uppercase precomposed letters with diacritics and verifies whether
their diacritic components should use .case variants.

If problems are found:
- Opens a new tab with affected glyphs.
- Offers the option to replace regular accents with .case accents where available (for relevant glyphs).
"""

import GlyphsApp
from GlyphsApp import Glyphs
from AppKit import NSAlert, NSAlertFirstButtonReturn

font = Glyphs.font
masters = font.masters

# ---------- CONFIGURATION ----------
MASTER_NAMES = []  # Empty = check all masters
# -----------------------------------

def glyph_by_name(name):
    if not name:
        return None
    try:
        return font.glyphs[name]
    except Exception:
        pass
    for g in font.glyphs:
        if g.name == name:
            return g
    return None

def is_uppercase_glyph(glyph):
    if not glyph or not glyph.name:
        return False
    n = glyph.name
    return ("A" <= n[0] <= "Z") and glyph.category == "Letter"

# Determine masters to check
if MASTER_NAMES:
    master_ids_to_check = [m.id for m in masters if m.name in MASTER_NAMES]
    if not master_ids_to_check:
        print("Warning: No masters matched. Checking all masters.\n")
        master_ids_to_check = [m.id for m in masters]
else:
    master_ids_to_check = [m.id for m in masters]

print("### Checking uppercase letters for correct case-sensitive diacritics ###\n")

problems = {}     # masterID → set of glyph names
tabGlyphs = []    # for tab

for glyph in font.glyphs:
    if not is_uppercase_glyph(glyph):
        continue

    for layer in glyph.layers:
        masterID = layer.associatedMasterId
        if masterID not in master_ids_to_check:
            continue

        if not layer.components:
            continue

        for comp in layer.components:
            compName = comp.componentName
            if not compName:
                continue

            compGlyph = glyph_by_name(compName)
            if not compGlyph or compGlyph.category != "Mark":
                continue

            # Skip if already .case
            if compName.endswith(".case"):
                continue

            caseName = compName + ".case"
            if glyph_by_name(caseName):
                problems.setdefault(masterID, set()).add(glyph.name)
                if glyph.name not in tabGlyphs:
                    tabGlyphs.append(glyph.name)
                break

# Reporting
if not problems:
    print("All uppercase glyphs use correct case-sensitive accents. ✓\n")
    print("Done.\n")
else:
    print("The following masters contain uppercase glyphs that do NOT use .case accents:\n")
    for m in masters:
        if m.id in problems:
            print(f"• {m.name}: {', '.join(sorted(problems[m.id]))}")

    if tabGlyphs:
        font.newTab("/" + "/".join(tabGlyphs))
        print("\nA new tab has been opened with all affected glyphs.\n")

    # Confirmation dialog
    alert = NSAlert.alloc().init()
    alert.setMessageText_("Swap to .case accents?")
    alert.setInformativeText_("Replace regular diacritic components with their .case equivalents in affected glyphs?")
    alert.addButtonWithTitle_("Swap")
    alert.addButtonWithTitle_("Cancel")

    response = alert.runModal()

    if response == NSAlertFirstButtonReturn:
        font.disableUpdateInterface()

        for glyphName in tabGlyphs:
            glyph = font.glyphs[glyphName]

            for layer in glyph.layers:
                if layer.associatedMasterId not in master_ids_to_check:
                    continue

                for comp in layer.components:
                    compName = comp.componentName
                    if not compName or compName.endswith(".case"):
                        continue

                    caseName = compName + ".case"
                    if glyph_by_name(caseName):
                        transform = comp.transform
                        comp.componentName = caseName
                        comp.transform = transform

        font.enableUpdateInterface()
        print("Swapped regular accents to .case where available.\n")
    else:
        print("No changes made.\n")

    print("Done.\n")
