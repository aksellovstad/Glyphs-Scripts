# MenuTitle: Copy Components Across Masters
# -*- coding: utf-8 -*-
__doc__ = """
Copy component structure from a SOURCE master to a TARGET master for:
• the active glyph (Edit view), or
• all highlighted glyphs (Font view).

Options:
• Replace existing target components (checked) or append (unchecked).
Per-font preferences (stored in font.userData["sk.copycomponents"]).
Robust across Glyphs 3 builds (safe component removal, preserves transforms and auto-align flags).
"""

import GlyphsApp
from GlyphsApp import Glyphs, GSComponent
import vanilla

# -----------------------------
# Per-font preference helpers
# -----------------------------
UDK = "sk.copycomponents"  # key in font.userData

def getpref_font(font, key, default=None):
    try:
        data = font.userData.get(UDK) or {}
        return data.get(key, default)
    except Exception:
        return default

def setpref_font(font, key, value):
    try:
        data = dict(font.userData.get(UDK) or {})
        data[key] = value
        font.userData[UDK] = data
    except Exception:
        pass

# -----------------------------
# Selection helpers
# -----------------------------
def get_selected_layers(font):
    """
    Returns:
      • [GSLayer] for highlighted glyphs in Font view, or
      • [GSLayer] with the active Edit layer as a fallback.
    """
    layers = list(font.selectedLayers or [])
    if layers:
        return layers
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

# -----------------------------
# Component copy/clear helpers
# -----------------------------
def copy_component_properties(dstComp, srcComp):
    """Copy a robust set of properties from srcComp → dstComp."""
    try:
        if hasattr(srcComp, "position") and hasattr(dstComp, "position"):
            dstComp.position = srcComp.position
        if hasattr(srcComp, "scale") and hasattr(dstComp, "scale"):
            dstComp.scale = srcComp.scale
        if hasattr(srcComp, "rotation") and hasattr(dstComp, "rotation"):
            dstComp.rotation = srcComp.rotation
        if hasattr(srcComp, "transform") and hasattr(dstComp, "transform"):
            dstComp.transform = srcComp.transform

        # Auto-alignment flags across API variants
        if hasattr(srcComp, "automaticAlignment") and hasattr(dstComp, "automaticAlignment"):
            dstComp.automaticAlignment = srcComp.automaticAlignment
        elif hasattr(srcComp, "disableAlignment") and hasattr(dstComp, "setDisableAlignment_"):
            dstComp.setDisableAlignment_(srcComp.disableAlignment)

        # Smart component values
        if hasattr(srcComp, "smartComponentValues") and hasattr(dstComp, "smartComponentValues"):
            try:
                dstComp.smartComponentValues = dict(srcComp.smartComponentValues)
            except Exception:
                pass

        # Optional extras if present
        for attr in ("locked", "alignment"):
            if hasattr(srcComp, attr) and hasattr(dstComp, attr):
                try:
                    setattr(dstComp, attr, getattr(srcComp, attr))
                except Exception:
                    pass
    except Exception:
        pass

def clear_components(dstLayer):
    """
    Remove all components from dstLayer in a cross-version safe way.
    Returns number removed.
    """
    comps = list(dstLayer.components or [])
    if not comps:
        return 0

    removed = 0
    # Preferred KVC remover when available
    if hasattr(dstLayer, "removeObjectFromComponentsAtIndex_"):
        try:
            for i in range(len(comps) - 1, -1, -1):
                dstLayer.removeObjectFromComponentsAtIndex_(i)
                removed += 1
            return removed
        except Exception:
            pass

    # Fallback: remove each component as a shape
    for c in comps:
        try:
            if hasattr(dstLayer, "removeShape_"):
                dstLayer.removeShape_(c)
                removed += 1
                continue
        except Exception:
            pass
        try:
            dstLayer.shapes.remove(c)
            removed += 1
        except Exception:
            pass
    return removed

def copy_components_from_layer_to_layer(srcLayer, dstLayer, replace=True):
    """
    Copy components from srcLayer → dstLayer.
    - replace=True: remove existing components in dstLayer first
    - replace=False: append after existing components
    Returns number of components copied.
    """
    if not srcLayer or not dstLayer:
        return 0
    srcComps = list(srcLayer.components or [])
    if not srcComps:
        return 0

    if replace:
        clear_components(dstLayer)

    copied = 0
    for sc in srcComps:
        try:
            compName = getattr(sc, "componentName", None)
            if not compName and hasattr(sc, "component") and sc.component is not None:
                compName = sc.component.name
            if not compName:
                continue
            newComp = GSComponent(compName)
            copy_component_properties(newComp, sc)
            dstLayer.components.append(newComp)
            copied += 1
        except Exception:
            pass

    try:
        dstLayer.updateMetrics()
    except Exception:
        pass
    return copied

# -----------------------------
# UI
# -----------------------------
class CopyComponentsUI(object):
    def __init__(self):
        self.font = Glyphs.font
        if not self.font:
            Glyphs.showNotification("Copy Components", "Open a .glyphs file first.")
            return

        self.masters = list(self.font.masters)
        self.masterNames = [m.name for m in self.masters]

        curMasterId = getattr(self.font.selectedFontMaster, "id", None)
        defaultSrcIndex = 0
        defaultTgtIndex = 0
        if curMasterId:
            for i, m in enumerate(self.masters):
                if m.id == curMasterId:
                    defaultSrcIndex = i
                    defaultTgtIndex = (i + 1) % len(self.masters)
                    break

        # Prefer stored master IDs (stable if master order changes)
        storedSrcID = getpref_font(self.font, "srcMasterID", None)
        storedTgtID = getpref_font(self.font, "tgtMasterID", None)

        if storedSrcID:
            defaultSrcIndex = next((i for i, m in enumerate(self.masters) if m.id == storedSrcID), defaultSrcIndex)
        if storedTgtID:
            defaultTgtIndex = next((i for i, m in enumerate(self.masters) if m.id == storedTgtID), defaultTgtIndex)

        savedReplace = bool(getpref_font(self.font, "replace", True))

        self.w = vanilla.FloatingWindow((380, 160), "Copy Components Master → Master")
        y = 12
        self.w.srcLabel = vanilla.TextBox((14, y, 140, 20), "Source master:")
        self.w.srcPop   = vanilla.PopUpButton((140, y, -14, 24), self.masterNames)
        self.w.srcPop.set(min(defaultSrcIndex, len(self.masters)-1))
        y += 34

        self.w.tgtLabel = vanilla.TextBox((14, y, 140, 20), "Target master:")
        self.w.tgtPop   = vanilla.PopUpButton((140, y, -14, 24), self.masterNames)
        self.w.tgtPop.set(min(defaultTgtIndex, len(self.masters)-1))
        y += 34

        self.w.replaceCheck = vanilla.CheckBox((14, y, -14, 20), "Replace existing target components", value=savedReplace)
        y += 34

        self.w.runButton = vanilla.Button((14, y, -14, 28), "Copy Components", callback=self.run)
        self.w.open()

    def run(self, sender):
        try:
            srcIdx = int(self.w.srcPop.get())
            tgtIdx = int(self.w.tgtPop.get())
            replace = bool(self.w.replaceCheck.get())

            if srcIdx == tgtIdx:
                Glyphs.showNotification("Copy Components", "Source and target master are the same.")
                return

            srcMaster = self.masters[srcIdx]
            tgtMaster = self.masters[tgtIdx]
            srcID = srcMaster.id
            tgtID = tgtMaster.id

            # Persist per-font (store both IDs and indices for convenience)
            setpref_font(self.font, "srcMasterID", srcID)
            setpref_font(self.font, "tgtMasterID", tgtID)
            setpref_font(self.font, "srcIndex", srcIdx)
            setpref_font(self.font, "tgtIndex", tgtIdx)
            setpref_font(self.font, "replace", replace)

            layers = get_selected_layers(self.font)
            if not layers:
                Glyphs.showNotification("Copy Components", "No selection found. Select glyphs (Font view) or place the caret in a glyph (Edit view).")
                return

            seen = set()
            work = []
            for L in layers:
                g = getattr(L, "parent", None)
                if not g:
                    continue
                srcLayer = g.layers[srcID]
                tgtLayer = g.layers[tgtID]
                if not srcLayer or not tgtLayer:
                    continue
                key = (g.name, tgtLayer.layerId)
                if key in seen:
                    continue
                seen.add(key)
                work.append((g, srcLayer, tgtLayer))

            totalGlyphs = 0
            totalCopied = 0

            self.font.disableUpdateInterface()
            try:
                for g, srcLayer, tgtLayer in work:
                    copied = copy_components_from_layer_to_layer(srcLayer, tgtLayer, replace=replace)
                    if copied:
                        totalGlyphs += 1
                        totalCopied += copied
            finally:
                self.font.enableUpdateInterface()

            msg = f"Source: {srcMaster.name} → Target: {tgtMaster.name}\nGlyphs updated: {totalGlyphs}\nComponents copied: {totalCopied}"
            print("Copy Components — Summary")
            print(msg)
            Glyphs.showNotification("Copy Components", msg)
        except Exception as e:
            Glyphs.showNotification("Copy Components — Error", f"{e.__class__.__name__}: {e}")

CopyComponentsUI()
