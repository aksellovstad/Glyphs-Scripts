# MenuTitle: Enable Auto Alignment for Selected (Edit or Font View)
# -*- coding: utf-8 -*-
__doc__ = """
Enable automatic alignment for all components in the current selection.
• In Edit view: applies to the active layer of the glyph you're editing.
• In Font view: applies to the master layers of the highlighted glyphs.
Only selected layers are affected; does NOT touch other masters/layers.
"""

import GlyphsApp
from GlyphsApp import Glyphs

def set_component_auto_alignment(component):
    """
    Robustly enable auto-alignment across Glyphs 3 API variants.
    Returns True if we changed something, False otherwise.
    """
    try:
        # Preferred in Glyphs 3
        if hasattr(component, "automaticAlignment"):
            if not component.automaticAlignment:
                component.automaticAlignment = True
                return True
            return False

        # Legacy bridge
        if hasattr(component, "setAutomaticAlignment_"):
            component.setAutomaticAlignment_(True)
            return True

        # Older flag name (disableAlignment)
        if hasattr(component, "disableAlignment") and hasattr(component, "setDisableAlignment_"):
            if component.disableAlignment:
                component.setDisableAlignment_(False)
                return True
            return False

        # Last-ditch attempt
        did = False
        if hasattr(component, "setDisableAlignment_"):
            component.setDisableAlignment_(False); did = True
        if hasattr(component, "setAutomaticAlignment_"):
            component.setAutomaticAlignment_(True); did = True
        return did
    except Exception:
        return False

def selected_layers(font):
    """
    Return a list of GSLayer objects representing the user's selection:
    - Font view: master layers of highlighted glyphs
    - Edit view: the active layer of the glyph being edited
    """
    layers = list(font.selectedLayers or [])
    if layers:
        return layers

    # Fallback: try to get the active Edit view layer
    try:
        doc = Glyphs.currentDocument
        if doc:
            evc = doc.windowController().activeEditViewController()
            if evc:
                gv = evc.graphicView()
                if gv:
                    L = gv.activeLayer()
                    if L:
                        return [L]
    except Exception:
        pass

    return []

def run():
    font = Glyphs.font
    if not font:
        Glyphs.showNotification("Enable Auto Alignment", "Open a .glyphs file first.")
        return

    layers = selected_layers(font)
    if not layers:
        Glyphs.showNotification("Enable Auto Alignment", "No selection found. Select glyphs (Font view) or place the caret in a glyph (Edit view).")
        return

    # De-duplicate by (glyph, layerId)
    seen = set()
    unique_layers = []
    for L in layers:
        key = (getattr(L.parent, "name", None), L.layerId)
        if key not in seen:
            seen.add(key)
            unique_layers.append(L)

    changed_components = 0
    touched_layers = 0

    font.disableUpdateInterface()
    try:
        for L in unique_layers:
            if not L or not L.components:
                continue
            layer_changed = False
            for comp in list(L.components):
                if set_component_auto_alignment(comp):
                    changed_components += 1
                    layer_changed = True
            if layer_changed:
                touched_layers += 1
                try:
                    L.updateMetrics()
                except Exception:
                    pass
    finally:
        font.enableUpdateInterface()

    msg = f"Layers processed: {len(unique_layers)}\nLayers updated: {touched_layers}\nComponents set to auto: {changed_components}"
    print("Enable Auto Alignment — Summary")
    print(msg)
    Glyphs.showNotification("Enable Auto Alignment", msg)

run()
