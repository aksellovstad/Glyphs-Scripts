#MenuTitle: Check .case Diacritics in Uppercase Letters
# -*- coding: utf-8 -*-
__doc__ = """
Checks uppercase precomposed letters with diacritics and verifies whether
their diacritic components should use .case variants. If a .case version
exists but the composite uses the regular accent, the glyph is flagged.
A report is printed, and a new tab opens with all affected glyphs.

Configuration:
- MASTER_NAMES: List master names to limit the check.
  Empty list = check all masters.
"""

import GlyphsApp

font = Glyphs.font
masters = font.masters

# ---------- CONFIGURATION ----------

MASTER_NAMES = [] 
# -----------------------------------

def glyph_by_name(name):
    """Reliable lookup for a glyph object by name."""
    if not name:
        return None
    try:
        g = font.glyphs[name]
        if g:
            return g
    except Exception:
        pass
    for g in font.glyphs:
        if g.name == name:
            return g
    return None

def is_uppercase_glyph(glyph):
    """Uppercase = starts with A–Z and category is Letter."""
    if not glyph or not glyph.name:
        return False
    n = glyph.name
    return ("A" <= n[0] <= "Z") and glyph.category == "Letter"

# Determine which masters to check
if MASTER_NAMES:
    master_ids_to_check = [m.id for m in masters if m.name in MASTER_NAMES]
    if not master_ids_to_check:
        print("Warning: No masters matched the names in MASTER_NAMES. Checking all masters instead.\n")
        master_ids_to_check = [m.id for m in masters]
else:
    master_ids_to_check = [m.id for m in masters]

print("### Checking uppercase letters for correct case-sensitive diacritics ###\n")

problems = {}    # masterID → set of glyph names
tabGlyphs = []   # for the tab

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
            compName = getattr(comp, "componentName", None) or getattr(comp, "name", None)
            if not compName:
                continue

            compGlyph = glyph_by_name(compName)
            if not compGlyph:
                continue

            # Only check diacritic marks
            if compGlyph.category != "Mark":
                continue

            # Already a .case mark → OK
            if compName.endswith(".case"):
                continue

            # Check if a .case version exists
            caseName = compName + ".case"
            caseGlyph = glyph_by_name(caseName)

            if caseGlyph:
                problems.setdefault(masterID, set()).add(glyph.name)
                if glyph.name not in tabGlyphs:
                    tabGlyphs.append(glyph.name)
                break  # No need to check more components in this layer

# Output report
if not problems:
    print("All uppercase glyphs use correct case-sensitive accents. ✓\n")
else:
    print("The following masters contain uppercase glyphs that do NOT use .case accents even though .case versions exist:\n")
    for m in masters:
        if m.id in problems:
            affected = sorted(problems[m.id])
            print(f"• {m.name}: {', '.join(affected)}")
    if tabGlyphs:
        font.newTab("/" + "/".join(tabGlyphs))
        print("\nA new tab has been opened with all affected glyphs.\n")

print("Done.\n")
