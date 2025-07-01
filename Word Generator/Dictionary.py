# MenuTitle: Word Generator
# -*- coding: utf-8 -*-
__doc__ = """
Generates words using only drawn glyphs in the current master. Lets you filter by word count, word length (min/max), and must-include characters. Sets size to 70pt.
"""

import GlyphsApp
import random
import vanilla
import os

DICTIONARY_PATH = "/usr/share/dict/words"

def loadWordList():
    if os.path.exists(DICTIONARY_PATH):
        with open(DICTIONARY_PATH, "r", encoding="utf-8") as f:
            return [w.strip() for w in f if w.strip().isalpha()]
    return []

def getDrawnCharacters(font):
    master = font.selectedFontMaster or font.masters[0]
    chars = set()
    for glyph in font.glyphs:
        if not glyph.export or not glyph.unicode:
            continue
        layer = glyph.layers[master.id]
        if layer.paths or layer.components:
            try:
                char = chr(int(glyph.unicode, 16))
                chars.add(char)
            except:
                continue
    return chars

def filterWords(wordList, allowedChars, titleCase=False, upperCase=False, minLen=2, maxLen=20, mustInclude=""):
    filtered = []
    mustIncludeSet = set(mustInclude)
    for w in wordList:
        if not (minLen <= len(w) <= maxLen):
            continue

        if upperCase:
            candidate = w.upper()
        elif titleCase:
            candidate = w.capitalize()
        else:
            candidate = w.lower()

        if set(candidate).issubset(allowedChars):
            if not mustIncludeSet or any(c in candidate for c in mustIncludeSet):
                filtered.append(candidate)
    return filtered

def generateParagraph(words, wordCount=30):
    selectedWords = [random.choice(words) for _ in range(wordCount)]
    return " ".join(selectedWords) + "."

class WordGenerator:
    def __init__(self):
        self.font = Glyphs.font
        self.w = vanilla.FloatingWindow((360, 240), "Word Generator")

        self.w.wordCountLabel = vanilla.TextBox((15, 18, 80, 17), "Word count:", sizeStyle="small")
        self.w.lengthInput = vanilla.EditText((100, 16, 50, 22), "30", callback=self.inputChanged)

        self.w.minLabel = vanilla.TextBox((15, 48, 80, 17), "Min length:", sizeStyle="small")
        self.w.minInput = vanilla.EditText((100, 46, 40, 22), "2", callback=self.inputChanged)

        self.w.maxLabel = vanilla.TextBox((160, 48, 80, 17), "Max length:", sizeStyle="small")
        self.w.maxInput = vanilla.EditText((245, 46, 40, 22), "20", callback=self.inputChanged)

        self.w.mustContainLabel = vanilla.TextBox((15, 78, 140, 17), "Must include char(s):", sizeStyle="small")
        self.w.mustContainInput = vanilla.EditText((160, 76, 125, 22), "", callback=self.inputChanged)

        self.w.titleCaseToggle = vanilla.CheckBox((15, 108, -15, 20), "Use Title Case", value=False, callback=self.syncToggles)
        self.w.upperCaseToggle = vanilla.CheckBox((15, 130, -15, 20), "Use UPPERCASE", value=False, callback=self.syncToggles)

        self.w.button = vanilla.Button((15, 180, -15, 30), "Generate", callback=self.insert)
        self.w.open()

    def syncToggles(self, sender):
        if sender == self.w.titleCaseToggle and sender.get():
            self.w.upperCaseToggle.set(False)
        elif sender == self.w.upperCaseToggle and sender.get():
            self.w.titleCaseToggle.set(False)

    def inputChanged(self, sender):
        pass  # validation handled in insert

    def insert(self, sender):
        try:
            wordCount = int(self.w.lengthInput.get())
            minLen = max(2, int(self.w.minInput.get()))
            maxLen = min(20, int(self.w.maxInput.get()))
        except ValueError:
            Glyphs.showNotification("Invalid input", "Please enter valid numbers.")
            return

        if minLen > maxLen:
            Glyphs.showNotification("Invalid range", "Minimum length cannot be greater than maximum.")
            return

        useTitleCase = self.w.titleCaseToggle.get()
        useUpperCase = self.w.upperCaseToggle.get()
        mustInclude = self.w.mustContainInput.get().strip()

        drawnChars = getDrawnCharacters(self.font)
        wordList = filterWords(
            loadWordList(),
            drawnChars,
            titleCase=useTitleCase,
            upperCase=useUpperCase,
            minLen=minLen,
            maxLen=maxLen,
            mustInclude=mustInclude
        )

        if not wordList:
            Glyphs.showNotification("No usable words", "No words match your filters.")
            return

        text = generateParagraph(wordList, wordCount)
        tab = self.font.newTab(text)

        if tab and tab.layers:
            try:
                tab.layers[0].setDisplaySize_(70.0)
            except Exception as e:
                Glyphs.showNotification("Couldn't set size", str(e))

        self.w.close()

WordGenerator()
