# MenuTitle: Transfer Paths Across Masters
# -*- coding: utf-8 -*-
__doc__ = """
Copy drawn paths (and optionally anchors) from a SOURCE master to a TARGET master for:
• the active glyph (Edit view), or
• all highlighted glyphs (Font view).

Options:
• Clear existing paths in target master (checked) or keep (unchecked)
• Include anchors in the transfer (checked) or skip (unchecked)
• Inherit side bearings from source master (checked) or keep target's (unchecked)
Per-font preferences stored in font.userData["sk.transferPaths"]
"""

import GlyphsApp
from GlyphsApp import Glyphs, GSAnchor
import vanilla

UDK = "sk.transferPaths"

def getpref_font(font, key, default=None):
    try:
        return (font.userData.get(UDK) or {}).get(key, default)
    except Exception:
        return default

def setpref_font(font, key, value):
    try:
        data = dict(font.userData.get(UDK) or {})
        data[key] = value
        font.userData[UDK] = data
    except Exception:
        pass

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
                L = gv.activeLayer()
                if L:
                    return [L]
    except Exception:
        pass
    return []

def clear_drawn_shapes(dstLayer):
    for s in list(dstLayer.shapes or [])[::-1]:
        # skip components
        if hasattr(s, "componentName") or hasattr(s, "component"): continue
        try: dstLayer.removeShape_(s)
        except Exception:
            try: dstLayer.shapes.remove(s)
            except Exception: pass
    try: dstLayer.updateMetrics()
    except Exception: pass

def copy_paths(srcLayer, dstLayer):
    copied = 0
    for path in srcLayer.paths or []:
        try:
            dstLayer.shapes.append(path.copy())
            copied += 1
        except Exception: pass
    try: dstLayer.updateMetrics()
    except Exception: pass
    return copied

def copy_anchors(srcLayer, dstLayer):
    copied = 0
    for a in srcLayer.anchors or []:
        try: dstLayer.anchors.append(GSAnchor(a.name, a.position))
        except Exception: pass
    return copied

def copy_sidebearings(srcLayer, dstLayer):
    try:
        dstLayer.LSB = srcLayer.LSB
        dstLayer.RSB = srcLayer.RSB
    except Exception:
        pass

class TransferPathsUI(object):
    def __init__(self):
        self.font = Glyphs.font
        if not self.font:
            Glyphs.showNotification("Transfer Paths","Open a .glyphs file first.")
            return

        self.masters = list(self.font.masters)
        self.masterNames = [m.name for m in self.masters]

        curMasterId = getattr(self.font.selectedFontMaster, "id", None)
        defaultSrcIndex, defaultTgtIndex = 0, 0
        if curMasterId:
            for i,m in enumerate(self.masters):
                if m.id==curMasterId:
                    defaultSrcIndex, defaultTgtIndex = i, (i+1)%len(self.masters)

        storedSrcID = getpref_font(self.font,"srcMasterID")
        storedTgtID = getpref_font(self.font,"tgtMasterID")
        if storedSrcID: defaultSrcIndex = next((i for i,m in enumerate(self.masters) if m.id==storedSrcID), defaultSrcIndex)
        if storedTgtID: defaultTgtIndex = next((i for i,m in enumerate(self.masters) if m.id==storedTgtID), defaultTgtIndex)

        savedClearPaths = bool(getpref_font(self.font,"clearPaths", True))
        savedIncludeAnchors = bool(getpref_font(self.font,"includeAnchors", True))
        savedInheritSB = bool(getpref_font(self.font,"inheritSidebearings", False))

        self.w = vanilla.FloatingWindow((420, 210), "Transfer Paths")
        y = 12
        self.w.srcLabel = vanilla.TextBox((14,y,140,20),"Source master:")
        self.w.srcPop   = vanilla.PopUpButton((140,y,-14,24),self.masterNames)
        self.w.srcPop.set(min(defaultSrcIndex,len(self.masters)-1))
        y+=34
        self.w.tgtLabel = vanilla.TextBox((14,y,140,20),"Target master:")
        self.w.tgtPop   = vanilla.PopUpButton((140,y,-14,24),self.masterNames)
        self.w.tgtPop.set(min(defaultTgtIndex,len(self.masters)-1))
        y+=34
        self.w.clearPathsCheck = vanilla.CheckBox((14,y,-14,20),"⚠️ Clear existing paths in target master",value=int(savedClearPaths))
        y+=26
        self.w.includeAnchorsCheck = vanilla.CheckBox((14,y,-14,20),"Include anchors",value=int(savedIncludeAnchors))
        y+=26
        self.w.inheritSBCheck = vanilla.CheckBox((14,y,-14,20),"Inherit side bearings",value=int(savedInheritSB))
        y+=34
        self.w.runButton = vanilla.Button((14,y,-14,28),"Transfer",callback=self.run)
        self.w.open()

    def run(self,sender):
        try:
            srcIdx = int(self.w.srcPop.get())
            tgtIdx = int(self.w.tgtPop.get())
            clearPaths = bool(self.w.clearPathsCheck.get())
            includeAnchors = bool(self.w.includeAnchorsCheck.get())
            inheritSB = bool(self.w.inheritSBCheck.get())

            if srcIdx==tgtIdx: Glyphs.showNotification("Transfer Paths","Source and target master are the same."); return

            srcMaster, tgtMaster = self.masters[srcIdx], self.masters[tgtIdx]
            setpref_font(self.font,"srcMasterID",srcMaster.id)
            setpref_font(self.font,"tgtMasterID",tgtMaster.id)
            setpref_font(self.font,"clearPaths",clearPaths)
            setpref_font(self.font,"includeAnchors",includeAnchors)
            setpref_font(self.font,"inheritSidebearings",inheritSB)

            layers = get_selected_layers(self.font)
            if not layers: Glyphs.showNotification("Transfer Paths","No selection found."); return

            seen, work = set(), []
            for L in layers:
                g = getattr(L,"parent",None)
                if not g: continue
                srcLayer, tgtLayer = g.layers[srcMaster.id], g.layers[tgtMaster.id]
                if not srcLayer or not tgtLayer: continue
                key=(g.name,tgtLayer.layerId)
                if key in seen: continue
                seen.add(key)
                work.append((g, srcLayer, tgtLayer))

            totalGlyphs, totalPaths, totalAnchors, totalSB = 0,0,0,0
            self.font.disableUpdateInterface()
            try:
                for g,srcLayer,tgtLayer in work:
                    if clearPaths: clear_drawn_shapes(tgtLayer)
                    totalPaths += copy_paths(srcLayer,tgtLayer)
                    if includeAnchors: totalAnchors += copy_anchors(srcLayer,tgtLayer)
                    if inheritSB: copy_sidebearings(srcLayer,tgtLayer); totalSB+=1
                    if totalPaths or totalAnchors or (inheritSB and totalSB>0): totalGlyphs+=1
            finally:
                self.font.enableUpdateInterface()

            msg=f"Source: {srcMaster.name} → Target: {tgtMaster.name}\nGlyphs updated: {totalGlyphs}\nPaths copied: {totalPaths}\nAnchors copied: {totalAnchors if includeAnchors else 'Skipped'}\nSide bearings inherited: {totalSB if inheritSB else 'Skipped'}"
            print("Transfer Paths — Summary\n"+msg)
            Glyphs.showNotification("Transfer Paths",msg)

        except Exception as e:
            Glyphs.showNotification("Transfer Paths — Error",f"{e.__class__.__name__}: {e}")

TransferPathsUI()
