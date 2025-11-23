#MenuTitle: Transfer Side Bearings
# -*- coding: utf-8 -*-
import vanilla
from GlyphsApp import Glyphs, Message

font = Glyphs.font
selectedLayers = font.selectedLayers

if not selectedLayers:
    Message("No glyphs selected", "Please select or highlight some glyphs first.", OKButton="OK")
else:
    # Get all masters in the font
    allMasters = font.masters
    masterNames = [m.name for m in allMasters]

    class SideBearingsTransferWindow:
        def __init__(self):
            self.w = vanilla.FloatingWindow((340, 120), "Transfer Side Bearings")

            self.w.sourceText = vanilla.TextBox((15, 15, 120, 20), "Source Master:")
            self.w.sourcePopup = vanilla.PopUpButton((140, 10, 180, 20), masterNames)

            self.w.targetText = vanilla.TextBox((15, 50, 120, 20), "Target Master:")
            self.w.targetPopup = vanilla.PopUpButton((140, 45, 180, 20), masterNames)

            self.w.transferButton = vanilla.Button((110, 80, 120, 30), "Transfer", callback=self.transfer)
            self.w.open()

        def transfer(self, sender):
            sourceMaster = allMasters[self.w.sourcePopup.get()]
            targetMaster = allMasters[self.w.targetPopup.get()]

            for layer in selectedLayers:
                glyph = layer.parent
                sourceLayer = glyph.layers[sourceMaster.id]
                targetLayer = glyph.layers[targetMaster.id]

                targetLayer.LSB = sourceLayer.LSB
                targetLayer.RSB = sourceLayer.RSB

            Message("Done", f"Side bearings transferred from '{sourceMaster.name}' to '{targetMaster.name}' for {len(selectedLayers)} glyph(s).", OKButton="OK")
            self.w.close()

    SideBearingsTransferWindow()
