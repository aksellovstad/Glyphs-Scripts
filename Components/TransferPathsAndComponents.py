# MenuTitle: Transfer Paths & Components
# -*- coding: utf-8 -*-

import GlyphsApp
from GlyphsApp import Glyphs, GSComponent, GSAnchor
import vanilla

# -------------------------------------------------
# Helpers
# -------------------------------------------------

def open_fonts():
    return [doc.font for doc in Glyphs.documents if doc.font]

def selected_layers():
    layers = list(Glyphs.font.selectedLayers or [])
    if layers:
        return layers
    try:
        doc = Glyphs.currentDocument
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

def resolve_layer(font, glyphName, masterID):
    g = font.glyphs[glyphName]
    if not g:
        return None
    return g.layers[masterID]

# -------------------------------------------------
# Clear
# -------------------------------------------------

def clear_components(layer):
    for c in list(layer.components or [])[::-1]:
        try:
            layer.removeShape_(c)
        except Exception:
            try:
                layer.shapes.remove(c)
            except Exception:
                pass

def clear_paths(layer):
    for s in list(layer.shapes or [])[::-1]:
        if hasattr(s, "componentName") or hasattr(s, "component"):
            continue
        try:
            layer.removeShape_(s)
        except Exception:
            try:
                layer.shapes.remove(s)
            except Exception:
                pass

def clear_anchors(layer):
    for a in list(layer.anchors or []):
        try:
            layer.removeAnchor_(a)
        except Exception:
            pass

# -------------------------------------------------
# Copy primitives
# -------------------------------------------------

def copy_paths(srcLayer, dstLayer):
    for p in srcLayer.paths or []:
        try:
            dstLayer.shapes.append(p.copy())
        except Exception:
            pass

def copy_components(srcLayer, dstLayer):
    for sc in srcLayer.components or []:
        try:
            c = GSComponent(sc.componentName)
            c.transform = sc.transform
            if hasattr(sc, "automaticAlignment"):
                c.automaticAlignment = sc.automaticAlignment
            if hasattr(sc, "smartComponentValues"):
                try:
                    c.smartComponentValues = dict(sc.smartComponentValues)
                except Exception:
                    pass
            dstLayer.components.append(c)
        except Exception:
            pass

def copy_anchors(srcLayer, dstLayer):
    clear_anchors(dstLayer)
    for a in srcLayer.anchors or []:
        na = GSAnchor()
        na.name = a.name
        na.position = a.position
        dstLayer.anchors.append(na)

# -------------------------------------------------
# Core transfer
# -------------------------------------------------

def transfer_layers(
    srcFont, srcMaster,
    dstFont, dstMaster,
    doPaths,
    doComponents,
    includeAnchors,
    inheritSB,
    clearDst
):
    layers = selected_layers()
    if not layers:
        Glyphs.showNotification("Transfer", "No glyphs selected.")
        return

    seen = set()
    affectedGlyphs = []

    dstFont.disableUpdateInterface()
    try:
        for L in layers:
            glyphName = L.parent.name
            key = (glyphName, dstMaster.id)
            if key in seen:
                continue
            seen.add(key)

            srcLayer = resolve_layer(srcFont, glyphName, srcMaster.id)
            dstLayer = resolve_layer(dstFont, glyphName, dstMaster.id)
            if not srcLayer or not dstLayer:
                continue

            if clearDst:
                if doPaths:
                    clear_paths(dstLayer)
                if doComponents:
                    clear_components(dstLayer)

            if doPaths:
                copy_paths(srcLayer, dstLayer)

            if doComponents:
                copy_components(srcLayer, dstLayer)

            if includeAnchors:
                copy_anchors(srcLayer, dstLayer)

            if inheritSB:
                try:
                    dstLayer.LSB = srcLayer.LSB
                    dstLayer.RSB = srcLayer.RSB
                    dstLayer.width = srcLayer.width
                except Exception:
                    pass

            dstLayer.updateMetrics()
            affectedGlyphs.append(glyphName)
    finally:
        dstFont.enableUpdateInterface()

    print("\nTransfer Paths & Components")
    print(f"Source: {srcFont.familyName} — {srcMaster.name}")
    print(f"Target: {dstFont.familyName} — {dstMaster.name}")
    print(f"Glyphs affected ({len(affectedGlyphs)}):")
    for g in affectedGlyphs:
        print(f"  {g}")

    Glyphs.showNotification(
        "Transfer",
        f"Glyphs updated: {len(affectedGlyphs)}"
    )

# -------------------------------------------------
# UI
# -------------------------------------------------

class TransferAcrossDocsUI(object):
    def __init__(self):
        self.fonts = open_fonts()
        if not self.fonts:
            Glyphs.showNotification("Transfer", "No open fonts.")
            return

        self.fontNames = [
            f.familyName or f"Untitled {i}"
            for i, f in enumerate(self.fonts)
        ]

        self.w = vanilla.FloatingWindow((500, 390), "Transfer Paths & Components")

        y = 12
        self.w.srcTitle = vanilla.TextBox((14, y, -14, 20), "Source")
        y += 24
        self.w.srcFont = vanilla.PopUpButton((14, y, -14, 24), self.fontNames, callback=self.updateMasters)
        y += 30
        self.w.srcMaster = vanilla.PopUpButton((14, y, -14, 24), [])
        y += 44

        self.w.dstTitle = vanilla.TextBox((14, y, -14, 20), "Target")
        y += 24
        self.w.dstFont = vanilla.PopUpButton((14, y, -14, 24), self.fontNames, callback=self.updateMasters)
        y += 30
        self.w.dstMaster = vanilla.PopUpButton((14, y, -14, 24), [])
        y += 44

        self.w.doPaths = vanilla.CheckBox((14, y, -14, 20), "Transfer paths", value=True)
        y += 24
        self.w.doComponents = vanilla.CheckBox((14, y, -14, 20), "Transfer components", value=True)
        y += 24
        self.w.clearDst = vanilla.CheckBox((14, y, -14, 20), "Clear destination first", value=False)
        y += 24
        self.w.includeAnchors = vanilla.CheckBox((14, y, -14, 20), "Include anchors", value=False)
        y += 24
        self.w.inheritSB = vanilla.CheckBox((14, y, -14, 20), "Inherit sidebearings", value=False)
        y += 34

        self.w.run = vanilla.Button((14, y, -14, 30), "Transfer", callback=self.run)

        self.updateMasters(None)
        self.w.open()

    def updateMasters(self, sender):
        sf = self.fonts[self.w.srcFont.get()]
        df = self.fonts[self.w.dstFont.get()]
        self.w.srcMaster.setItems([m.name for m in sf.masters])
        self.w.dstMaster.setItems([m.name for m in df.masters])

    def run(self, sender):
        srcFont = self.fonts[self.w.srcFont.get()]
        dstFont = self.fonts[self.w.dstFont.get()]
        srcMaster = srcFont.masters[self.w.srcMaster.get()]
        dstMaster = dstFont.masters[self.w.dstMaster.get()]

        if srcFont == dstFont and srcMaster.id == dstMaster.id:
            Glyphs.showNotification("Transfer", "Source and target are identical.")
            return

        transfer_layers(
            srcFont, srcMaster,
            dstFont, dstMaster,
            doPaths=self.w.doPaths.get(),
            doComponents=self.w.doComponents.get(),
            includeAnchors=self.w.includeAnchors.get(),
            inheritSB=self.w.inheritSB.get(),
            clearDst=self.w.clearDst.get()
        )

TransferAcrossDocsUI()
