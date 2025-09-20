# MenuTitle: Remove Component from Selected Glyphs
# -*- coding: utf-8 -*-
__doc__ = """
Removes a specified component from every SELECTED glyph layer (Font view: highlighted glyphs; Edit view: active glyph).
Removes ALL occurrences of the component per layer. Reports how many were removed.
"""

import GlyphsApp
import vanilla

def _component_name(comp):
    # Get the component's source glyph name across API variants
    name = getattr(comp, "componentName", None)
    if not name and hasattr(comp, "component") and comp.component is not None:
        name = comp.component.name
    return name

def _remove_component_from_layer(layer, target_name):
    """
    Remove all components with name == target_name from 'layer'.
    Uses cross-version-safe removal calls. Returns count removed.
    """
    comps = list(layer.components or [])
    if not comps:
        return 0

    removed = 0

    # Fast path: index-based remover when available
    if hasattr(layer, "removeObjectFromComponentsAtIndex_"):
        try:
            for i in range(len(comps) - 1, -1, -1):
                try:
                    if _component_name(comps[i]) == target_name:
                        layer.removeObjectFromComponentsAtIndex_(i)
                        removed += 1
                except Exception:
                    # fall back to per-shape removal if index removal fails
                    pass
        except Exception:
            pass

        # If we used index-removal, we're done; refresh
        if removed:
            try:
                layer.updateMetrics()
            except Exception:
                pass
            return removed

    # Fallback: remove each matching component as a shape
    for c in comps:
        if _component_name(c) != target_name:
            continue
        # Try several ways to remove safely
        did = False
        try:
            if hasattr(layer, "removeShape_"):
                layer.removeShape_(c)
                did = True
        except Exception:
            pass
        if not did:
            try:
                layer.components.remove(c)
                did = True
            except Exception:
                pass
        if not did:
            try:
                layer.shapes.remove(c)
                did = True
            except Exception:
                pass
        if did:
            removed += 1

    if removed:
        try:
            layer.updateMetrics()
        except Exception:
            pass

    return removed

class RemoveComponentDialog:
    def __init__(self):
        self.font = Glyphs.font
        if not self.font:
            Glyphs.showNotification("Remove Component", "Open a .glyphs file first.")
            return

        glyphNames = [g.name for g in self.font.glyphs if g is not None and g.name]

        self.w = vanilla.FloatingWindow((320, 110), "Remove Component")
        self.w.text = vanilla.TextBox((15, 14, -15, 20), "Component to remove (glyph name):")
        self.w.drop = vanilla.ComboBox((15, 36, -15, 24), glyphNames)
        self.w.drop.set("")
        self.w.runButton = vanilla.Button((15, 70, -15, 24), "Remove from Selected Glyphs", callback=self.removeComponent)
        self.w.setDefaultButton(self.w.runButton)
        self.w.open()
        try:
            self.w.center()
        except Exception:
            pass

    def _selected_layers(self):
        layers = list(self.font.selectedLayers or [])
        if layers:
            return layers
        # Fallback: active edit layer
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

    def removeComponent(self, sender):
        target_name = (self.w.drop.get() or "").strip()
        if not target_name:
            Glyphs.showNotification("Remove Component", "Please type or select a component (glyph) name.")
            return

        if self.font.glyphs[target_name] is None:
            # Still allow removal by name even if the source glyph is missing,
            # as the component may exist with a stale name. Warn but proceed.
            pass

        layers = self._selected_layers()
        if not layers:
            Glyphs.showNotification("Remove Component", "No selection found. Select glyphs or place the caret in a glyph.")
            return

        # De-dupe layers by (glyphName, layerId)
        seen = set()
        unique_layers = []
        for L in layers:
            g = getattr(L, "parent", None)
            key = (getattr(g, "name", None), getattr(L, "layerId", None))
            if key not in seen:
                seen.add(key)
                unique_layers.append(L)

        total_removed = 0
        glyphs_touched = 0

        self.font.disableUpdateInterface()
        try:
            for L in unique_layers:
                removed = _remove_component_from_layer(L, target_name)
                if removed:
                    total_removed += removed
                    glyphs_touched += 1
        finally:
            self.font.enableUpdateInterface()

        if total_removed:
            Glyphs.showNotification(
                "Remove Component",
                f"Removed '{target_name}' {total_removed} time(s) from {glyphs_touched} glyph(s)."
            )
        else:
            Glyphs.showNotification(
                "Remove Component",
                f"No occurrences of '{target_name}' found in the selected glyph(s)."
            )
        self.w.close()

RemoveComponentDialog()
