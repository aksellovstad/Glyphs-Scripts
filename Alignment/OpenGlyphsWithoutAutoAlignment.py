#MenuTitle: Find Glyphs with Components that have Auto-Alignment Disabled
# Open glyph-edit tabs for glyphs that contain components with automatic alignment disabled
# Paste into Glyphs.app Macro Panel and Run.

from GlyphsApp import *
font = Glyphs.font
if not font:
    raise Exception("Open a font first.")

def layer_is_for_master(layer, master):
    """Return True if layer corresponds to the given master (robust across Glyphs versions)."""
    # direct associatedMasterId (recommended API)
    if getattr(layer, "associatedMasterId", None) == master.id:
        return True
    # some proxies expose .master
    master_obj = getattr(layer, "master", None)
    if master_obj is not None and getattr(master_obj, "id", None) == master.id:
        return True
    # fallback: some layers expose .layerId equal to the master id in some contexts
    if getattr(layer, "layerId", None) == master.id:
        return True
    return False

def master_layer_for_glyph(glyph, master):
    """Return the layer of 'glyph' that corresponds to 'master', or None if not present."""
    # iterate all layers (Glyphs uses a layer proxy)
    for layer in glyph.layers:
        if layer_is_for_master(layer, master):
            return layer
    return None

def component_has_auto_alignment_disabled(component):
    """
    Return True if this component definitively has automatic alignment disabled.
    Handles different property names and API versions defensively.
    """
    # Newer/common property: automaticAlignment (True == enabled)
    if hasattr(component, "automaticAlignment"):
        try:
            return not bool(getattr(component, "automaticAlignment"))
        except Exception:
            pass
    # Older/alternate property: disableAutomaticAlignment (True == disabled)
    if hasattr(component, "disableAutomaticAlignment"):
        try:
            return bool(getattr(component, "disableAutomaticAlignment"))
        except Exception:
            pass
    # Could not determine -> treat as enabled (not disabled)
    return False

disabled_glyphs = []

# iterate every glyph and check every master-layer (active layers only)
for glyph in font.glyphs:
    glyph_marked = False
    for master in font.masters:
        layer = master_layer_for_glyph(glyph, master)
        if not layer:
            # glyph has no active layer for this master (skip)
            continue

        comps = getattr(layer, "components", None)
        if not comps:
            continue

        # if any component in this master-layer has auto alignment disabled -> mark glyph
        for comp in comps:
            if component_has_auto_alignment_disabled(comp):
                disabled_glyphs.append(glyph)
                glyph_marked = True
                break

        if glyph_marked:
            break  # no need to check other masters for this glyph

# dedupe while preserving order
seen = set()
unique_glyphs = []
for g in disabled_glyphs:
    if g.name not in seen:
        unique_glyphs.append(g)
        seen.add(g.name)

if not unique_glyphs:
    Glyphs.showNotification("No glyphs found", "No components with automatic alignment disabled were found in active master layers.")
    print("No glyphs with disabled component auto-alignment were found in active master layers.")
else:
    # open glyph-edit tabs, grouping up to GROUP glyphs per tab
    GROUP = 20
    chunks = [unique_glyphs[i:i+GROUP] for i in range(0, len(unique_glyphs), GROUP)]
    for chunk in chunks:
        # Always open in glyph-edit mode (prefix with slash).
        # Use a single space as separator to avoid joining glyphs.
        tab_string = " ".join("/" + g.name for g in chunk)
        font.newTab(tab_string)

    Glyphs.showNotification("Opened glyphs", "%d glyph(s) opened in %d tab(s)." % (len(unique_glyphs), len(chunks)))
    print("Opened %d glyph(s):" % len(unique_glyphs))
    print(", ".join(g.name for g in unique_glyphs))
