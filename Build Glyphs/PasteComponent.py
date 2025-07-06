# MenuTitle: Add Component to Selected Glyphs
# -*- coding: utf-8 -*-
__doc__ = "Adds a specified component to every selected glyph in the font with automatic alignment. Ideal for creating fallback fonts."

import GlyphsApp
import vanilla

class PasteComponentDialog:
	def __init__(self):
		self.font = Glyphs.font
		glyphNames = [g.name for g in self.font.glyphs]
		self.w = vanilla.FloatingWindow((300, 100), "Paste Component")

		self.w.text = vanilla.TextBox((15, 15, -15, 20), "Component to paste:")
		self.w.drop = vanilla.ComboBox((15, 35, -15, 24), glyphNames)
		self.w.drop.set("")

		self.w.runButton = vanilla.Button((15, 65, -15, 24), "Paste to Selected Glyphs", callback=self.pasteComponent)
		self.w.setDefaultButton(self.w.runButton)
		self.w.open()
		self.w.center()

	def pasteComponent(self, sender):
		componentName = self.w.drop.get().strip()

		if not componentName:
			Glyphs.showNotification("No component entered", "Please type or select a glyph name.")
			return

		if componentName not in self.font.glyphs:
			Glyphs.showNotification("Component not found", f"'{componentName}' does not exist in this font.")
			return

		componentGlyph = self.font.glyphs[componentName]
		count = 0

		for layer in self.font.selectedLayers:
			targetGlyph = layer.parent
			if targetGlyph.name == componentName:
				continue  # skip if you're pasting into the component glyph itself

			component = GSComponent(componentGlyph)
			component.automaticAlignment = True
			layer.components.append(component)
			count += 1

		self.font.enableUpdateInterface()
		Glyphs.showNotification("Paste Complete", f"'{componentName}' added to {count} glyphs.")
		self.w.close()

PasteComponentDialog()
