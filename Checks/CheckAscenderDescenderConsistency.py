#MenuTitle: Check Ascender & Descender Consistency Across Masters
# -*- coding: utf-8 -*-
__doc__ = """
Checks ascender/descender consistency across masters. 
Ignores expected metric touchpoints: baseline, x-height, cap height, ascender, descender.
Reports inconsistencies and opens a tab with problematic glyphs.
"""

import GlyphsApp

font = Glyphs.font
masters = font.masters

print("\n### METRIC-AWARE ASCENDER/DESCENDER CONSISTENCY CHECK ###\n")

# ------------------------------------------------------------
# Helper: Collect metrics per master
# ------------------------------------------------------------
metrics = {}
for m in masters:
    metrics[m.id] = {
        "asc": m.ascender,
        "desc": m.descender,
        "xheight": m.xHeight,
        "cap": m.capHeight,
        "baseline": 0,  # implicit
    }

# Optional: report master metrics
print("Master Metrics:")
for m in masters:
    mm = metrics[m.id]
    print(f"• {m.name}: asc={mm['asc']} desc={mm['desc']} xh={mm['xheight']} cap={mm['cap']}")
print("\n")

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def get_extremes(layer):
    """Return (highest, lowest) Y coordinates in layer."""
    highest = None
    lowest = None
    for p in layer.paths:
        for n in p.nodes:
            y = n.y
            if highest is None or y > highest:
                highest = y
            if lowest is None or y < lowest:
                lowest = y
    return highest or 0, lowest or 0


def normalized_extreme(value, m_id):
    """
    Normalizes an extreme point:
    - If value equals any key metric → return the metric name (string)
    - Otherwise → return numeric Y value
    """
    mm = metrics[m_id]

    if value == mm["baseline"]:
        return "baseline"
    if value == mm["desc"]:
        return "descender"
    if value == mm["xheight"]:
        return "x-height"
    if value == mm["cap"]:
        return "cap-height"
    if value == mm["asc"]:
        return "ascender"

    return float(value)


# ------------------------------------------------------------
# MAIN CHECK
# ------------------------------------------------------------

problemGlyphs = []
problemReport = []

print("Checking glyphs…\n")

for g in font.glyphs:

    ascResults = []
    descResults = []

    for m in masters:
        layer = g.layers[m.id]
        hi, lo = get_extremes(layer)

        ascResults.append(normalized_extreme(hi, m.id))
        descResults.append(normalized_extreme(lo, m.id))

    # Determine if the normalized extremes differ
    if len(set(ascResults)) > 1 or len(set(descResults)) > 1:
        # Ignore fully flat glyphs with no outlines
        if ascResults == ["baseline"] and descResults == ["baseline"]:
            continue

        problemGlyphs.append(g.name)
        problemReport.append(f"{g.name}: asc={ascResults}, desc={descResults}")

# ------------------------------------------------------------
# REPORTING
# ------------------------------------------------------------

if problemGlyphs:
    print("⚠ Inconsistent glyph ascender/descender behavior (after metric filtering):\n")
    for line in problemReport:
        print("  • " + line)

    font.newTab("/" + "/".join(problemGlyphs))
    print("\nA tab has been opened with all problematic glyphs.\n")
else:
    print("✓ All glyphs are consistent across masters when accounting for metrics.\n")

print("Done.\n")
