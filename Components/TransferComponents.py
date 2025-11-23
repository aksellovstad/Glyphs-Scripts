# MenuTitle: Transfer Components Across Masters
# -*- coding: utf-8 -*-
__doc__ = """
Copy component structure from a SOURCE master to a TARGET master for:
• the active glyph (Edit view), or
• all highlighted glyphs (Font view).

Options:
• Clear existing components in target master (checked) or keep (unchecked).
• Clear drawn shapes in target master (checked) or keep (unchecked).
• Inherit side bearings from source master (checked) or keep target side bearings (unchecked)
• Include anchors from source master (checked) or keep target anchors (unchecked)
Per-font preferences (stored in font.userData["sk.copycomponents"]).
Robust across Glyphs 3 builds (safe component & shape removal, preserves transforms and auto-align flags).
"""

import GlyphsApp
from GlyphsApp import Glyphs, GSComponent, GSAnchor
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
    try:
        if hasattr(srcComp, "position") and hasattr(dstComp, "position"):
            dstComp.position = srcComp.position
        if hasattr(srcComp, "scale") and hasattr(dstComp, "scale"):
            dstComp.scale = srcComp.scale
        if hasattr(srcComp, "rotation") and hasattr(dstComp, "rotation"):
            dstComp.rotation = srcComp.rotation
        if hasattr(srcComp, "transform") and hasattr(dstComp, "transform"):
            dstComp.transform = srcComp.transform

        # Alignment / automatic alignment
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

        for attr in ("locked", "alignment"):
            if hasattr(srcComp, attr) and hasattr(dstComp, attr):
                try:
                    setattr(dstComp, attr, getattr(srcComp, attr))
                except Exception:
                    pass
    except Exception:
        pass

def clear_components(dstLayer):
    comps = list(dstLayer.components or [])
    if not comps:
        return 0
    removed = 0
    # Try using the robust removal API when present
    if hasattr(dstLayer, "removeObjectFromComponentsAtIndex_"):
        try:
            for i in range(len(comps) - 1, -1, -1):
                dstLayer.removeObjectFromComponentsAtIndex_(i)
                removed += 1
            return removed
        except Exception:
            pass
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

def clear_drawn_shapes(dstLayer):
    shapes = list(dstLayer.shapes or [])
    if not shapes:
        return 0
    removed = 0
    for i in range(len(shapes) - 1, -1, -1):
        s = shapes[i]
        is_component = False
        try:
            if getattr(s, "__class__", None) is not None:
                if s.__class__.__name__ in ("GSComponent", "GSComponentInstance"):
                    is_component = True
        except Exception:
            pass
        if not is_component:
            if hasattr(s, "componentName") or hasattr(s, "component"):
                is_component = True
        if is_component:
            continue
        try:
            if hasattr(dstLayer, "removeShape_"):
                dstLayer.removeShape_(s)
                removed += 1
                continue
        except Exception:
            pass
        try:
            dstLayer.shapes.remove(s)
            removed += 1
        except Exception:
            pass
    try:
        dstLayer.updateMetrics()
    except Exception:
        pass
    return removed

# -----------------------------
# Anchor helpers
# -----------------------------
def remove_anchors_with_name(dstLayer, name):
    """
    Remove anchors in dstLayer that have the given name.
    """
    try:
        existing = list(dstLayer.anchors or [])
        for a in existing:
            try:
                if getattr(a, "name", None) == name:
                    # robust removal:
                    if hasattr(dstLayer, "removeAnchor_"):
                        dstLayer.removeAnchor_(a)
                    else:
                        dstLayer.anchors.remove(a)
            except Exception:
                pass
    except Exception:
        pass

def copy_anchors_from_layer_to_layer(srcLayer, dstLayer):
    """
    Copy anchors from srcLayer to dstLayer.
    If an anchor with the same name exists in dstLayer, it will be removed/replaced.
    """
    try:
        srcAnchors = list(srcLayer.anchors or [])
        if not srcAnchors:
            return 0
    except Exception:
        return 0

    copied = 0
    for sa in srcAnchors:
        try:
            name = getattr(sa, "name", None)
            if not name:
                continue
            # remove anchors with same name in destination (replace behavior)
            remove_anchors_with_name(dstLayer, name)

            # create a new anchor instance
            try:
                newA = GSAnchor()
                # set coordinates robustly
                if hasattr(sa, "position") and sa.position is not None:
                    try:
                        newA.position = sa.position
                    except Exception:
                        # fallback to x/y
                        try:
                            newA.x = sa.x
                            newA.y = sa.y
                        except Exception:
                            pass
                else:
                    # use x/y if available
                    if hasattr(sa, "x"):
                        try:
                            newA.x = sa.x
                        except Exception:
                            pass
                    if hasattr(sa, "y"):
                        try:
                            newA.y = sa.y
                        except Exception:
                            pass
                # name last
                newA.name = name

                # append anchor to destination layer
                try:
                    dstLayer.anchors.append(newA)
                except Exception:
                    # try alternative append
                    try:
                        dstLayer.addAnchor_(newA)
                    except Exception:
                        pass
                copied += 1
            except Exception:
                # if GSAnchor() construction fails, try building a dict-style fallback
                try:
                    fallback = GSAnchor()
                    fallback.name = name
                    if hasattr(sa, "x"):
                        fallback.x = sa.x
                    if hasattr(sa, "y"):
                        fallback.y = sa.y
                    dstLayer.anchors.append(fallback)
                    copied += 1
                except Exception:
                    pass
        except Exception:
            pass

    try:
        dstLayer.updateMetrics()
    except Exception:
        pass
    return copied

# -----------------------------
# Copy main function
# -----------------------------
def copy_components_from_layer_to_layer(srcLayer, dstLayer, clearComps=False, clearShapes=False, inheritSB=False, includeAnchors=False):
    if not srcLayer or not dstLayer:
        return 0

    if clearShapes:
        clear_drawn_shapes(dstLayer)
    if clearComps:
        clear_components(dstLayer)

    srcComps = list(srcLayer.components or [])
    if not srcComps and not includeAnchors:
        # nothing to copy
        return 0

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
            try:
                dstLayer.components.append(newComp)
            except Exception:
                # fallback: some builds require addShape_/addObject_
                try:
                    dstLayer.shapes.append(newComp)
                except Exception:
                    pass
            copied += 1
        except Exception:
            pass

    # Inherit side bearings if requested
    if inheritSB:
        try:
            dstLayer.LSB = srcLayer.LSB
            dstLayer.RSB = srcLayer.RSB
            dstLayer.width = srcLayer.width
        except Exception:
            pass

    # Copy anchors if requested
    if includeAnchors:
        try:
            copy_anchors_from_layer_to_layer(srcLayer, dstLayer)
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

        storedSrcID = getpref_font(self.font, "srcMasterID", None)
        storedTgtID = getpref_font(self.font, "tgtMasterID", None)
        if storedSrcID:
            defaultSrcIndex = next((i for i, m in enumerate(self.masters) if m.id == storedSrcID), defaultSrcIndex)
        if storedTgtID:
            defaultTgtIndex = next((i for i, m in enumerate(self.masters) if m.id == storedTgtID), defaultTgtIndex)

        savedClearComps = bool(getpref_font(self.font, "clearComponents", False))
        savedClearShapes = bool(getpref_font(self.font, "clearShapes", False))
        savedInheritSB  = bool(getpref_font(self.font, "inheritSideBearings", False))
        savedIncludeAnchors = bool(getpref_font(self.font, "includeAnchors", False))

        self.w = vanilla.FloatingWindow((460, 240), "Transfer Components Across Masters")
        y = 12
        self.w.srcLabel = vanilla.TextBox((14, y, 140, 20), "Source master:")
        self.w.srcPop   = vanilla.PopUpButton((140, y, -14, 24), self.masterNames)
        self.w.srcPop.set(min(defaultSrcIndex, len(self.masters)-1))
        y += 34

        self.w.tgtLabel = vanilla.TextBox((14, y, 140, 20), "Target master:")
        self.w.tgtPop   = vanilla.PopUpButton((140, y, -14, 24), self.masterNames)
        self.w.tgtPop.set(min(defaultTgtIndex, len(self.masters)-1))
        y += 34

        self.w.clearCompsCheck = vanilla.CheckBox((14, y, -14, 20), "⚠️ Clear existing components in target master", value=int(savedClearComps))
        y += 26
        self.w.clearShapesCheck = vanilla.CheckBox((14, y, -14, 20), "⚠️ Clear drawn shapes in target master", value=int(savedClearShapes))
        y += 26
        self.w.inheritSBCheck = vanilla.CheckBox((14, y, -14, 20), "Inherit side bearings from source master", value=int(savedInheritSB))
        y += 26
        self.w.includeAnchorsCheck = vanilla.CheckBox((14, y, -14, 20), "Include anchors from source master (replace same-name anchors)", value=int(savedIncludeAnchors))
        y += 34

        self.w.runButton = vanilla.Button((14, y, -14, 28), "Copy Components", callback=self.run)
        self.w.open()

    def run(self, sender):
        try:
            srcIdx = int(self.w.srcPop.get())
            tgtIdx = int(self.w.tgtPop.get())
            clearComps = bool(self.w.clearCompsCheck.get())
            clearShapes = bool(self.w.clearShapesCheck.get())
            inheritSB  = bool(self.w.inheritSBCheck.get())
            includeAnchors = bool(self.w.includeAnchorsCheck.get())

            if srcIdx == tgtIdx:
                Glyphs.showNotification("Copy Components", "Source and target master are the same.")
                return

            srcMaster = self.masters[srcIdx]
            tgtMaster = self.masters[tgtIdx]
            srcID = srcMaster.id
            tgtID = tgtMaster.id

            setpref_font(self.font, "srcMasterID", srcID)
            setpref_font(self.font, "tgtMasterID", tgtID)
            setpref_font(self.font, "srcIndex", srcIdx)
            setpref_font(self.font, "tgtIndex", tgtIdx)
            setpref_font(self.font, "clearComponents", clearComps)
            setpref_font(self.font, "clearShapes", clearShapes)
            setpref_font(self.font, "inheritSideBearings", inheritSB)
            setpref_font(self.font, "includeAnchors", includeAnchors)

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
                    copied = copy_components_from_layer_to_layer(
                        srcLayer, tgtLayer,
                        clearComps=clearComps,
                        clearShapes=clearShapes,
                        inheritSB=inheritSB,
                        includeAnchors=includeAnchors
                    )
                    if copied:
                        totalGlyphs += 1
                        totalCopied += copied
                    else:
                        # still may have copied anchors even if components==0
                        if includeAnchors:
                            # try copying anchors separately and count them toward totalCopied (best-effort)
                            try:
                                a_copied = copy_anchors_from_layer_to_layer(srcLayer, tgtLayer)
                                if a_copied:
                                    totalGlyphs += 1
                            except Exception:
                                pass
            finally:
                self.font.enableUpdateInterface()

            msg = f"Source: {srcMaster.name} → Target: {tgtMaster.name}\nGlyphs updated: {totalGlyphs}\nComponents copied: {totalCopied}"
            print("Copy Components — Summary")
            print(msg)
            Glyphs.showNotification("Copy Components", msg)
        except Exception as e:
            Glyphs.showNotification("Copy Components — Error", f"{e.__class__.__name__}: {e}")

CopyComponentsUI()
