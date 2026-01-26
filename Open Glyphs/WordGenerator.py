# MenuTitle: Word Generator
# -*- coding: utf-8 -*-
from GlyphsApp import Glyphs
import random
import vanilla
import os
import traceback

_WORD_CACHE = None
UDK = "sk.wordgen"
DICTIONARY_PATH = "/usr/share/dict/words"

# -----------------------------
# Persistence
# -----------------------------
def getpref_font(font, key, default):
    try:
        return (font.userData.get(UDK) or {}).get(key, default)
    except:
        return default

def setpref_font(font, key, value):
    try:
        data = dict(font.userData.get(UDK) or {})
        data[key] = value
        font.userData[UDK] = data
    except:
        pass

# -----------------------------
# Dictionary
# -----------------------------
def loadWordList():
    global _WORD_CACHE

    if _WORD_CACHE is not None:
        return _WORD_CACHE

    if not os.path.exists(DICTIONARY_PATH):
        _WORD_CACHE = []
        return _WORD_CACHE

    try:
        with open(DICTIONARY_PATH, "r", encoding="utf-8") as f:
            _WORD_CACHE = [w.strip() for w in f if w.strip().isalpha()]
    except:
        _WORD_CACHE = []

    return _WORD_CACHE

# -----------------------------
# Font helpers
# -----------------------------
def getDrawnCharacters(font):
    master = font.selectedFontMaster or font.masters[0]
    chars = set()

    for g in font.glyphs:
        if not g.export or not g.unicode:
            continue

        layer = g.layers[master.id]
        if layer and (layer.paths or layer.components):
            try:
                chars.add(chr(int(g.unicode, 16)))
            except:
                pass

    return chars

# -----------------------------
# Filtering
# -----------------------------
def filterWords(
    wordList,
    allowedChars,
    *,
    titleCase=False,
    upperCase=False,
    minLen=2,
    maxLen=20,
    mustInclude=""
):
    out = []

    if titleCase:
        required_initials = {c for c in mustInclude if c.isupper()}
        required_body     = {c.lower() for c in mustInclude if c.islower()}
    else:
        required_any = {c.lower() for c in mustInclude}

    for w in wordList:
        if not (minLen <= len(w) <= maxLen):
            continue

        base = w.lower()

        # ----- semantic constraints -----
        if titleCase:
            # initial constraint
            if required_initials:
                if base[0].upper() not in required_initials:
                    continue

            # body constraint
            if required_body:
                if not (set(base[1:]) & required_body):
                    continue
        else:
            if mustInclude:
                if not (set(base) & required_any):
                    continue

        # ----- casing -----
        if upperCase:
            cand = base.upper()
        elif titleCase:
            cand = base.capitalize()
        else:
            cand = base

        # ----- glyph coverage -----
        if not set(cand).issubset(allowedChars):
            continue

        out.append(cand)

    return out

# -----------------------------
# Output
# -----------------------------
def generateParagraph(words, wordCount):
    return " ".join(random.choice(words) for _ in range(wordCount)) + "."

# -----------------------------
# UI
# -----------------------------
class WordGenerator:
    def __init__(self):
        self.font = Glyphs.font
        if not self.font:
            Glyphs.showNotification("Word Generator", "No font open.")
            return

        wordCount = int(getpref_font(self.font, "wordCount", 30))
        minLen    = int(getpref_font(self.font, "minLen", 2))
        maxLen    = int(getpref_font(self.font, "maxLen", 20))
        mustIncl  = str(getpref_font(self.font, "mustInclude", ""))
        titleOn   = bool(getpref_font(self.font, "titleCase", False))
        upperOn   = bool(getpref_font(self.font, "upperCase", False))

        self.w = vanilla.FloatingWindow((360, 240), "Word Generator")

        self.w.wordCountLabel = vanilla.TextBox((15, 18, 80, 17), "Word count:", sizeStyle="small")
        self.w.lengthInput    = vanilla.EditText((100, 16, 50, 22), str(wordCount), callback=self._save)

        self.w.minLabel = vanilla.TextBox((15, 48, 80, 17), "Min length:", sizeStyle="small")
        self.w.minInput = vanilla.EditText((100, 46, 40, 22), str(minLen), callback=self._save)

        self.w.maxLabel = vanilla.TextBox((160, 48, 80, 17), "Max length:", sizeStyle="small")
        self.w.maxInput = vanilla.EditText((245, 46, 40, 22), str(maxLen), callback=self._save)

        self.w.mustContainLabel = vanilla.TextBox((15, 78, 150, 17), "Must include:", sizeStyle="small")
        self.w.mustContainInput = vanilla.EditText((165, 76, 140, 22), mustIncl, callback=self._save)

        self.w.titleCaseToggle = vanilla.CheckBox(
            (15, 108, -15, 20), "Use Title Case", value=titleOn, callback=self._toggleSave
        )
        self.w.upperCaseToggle = vanilla.CheckBox(
            (15, 130, -15, 20), "Use UPPERCASE", value=upperOn, callback=self._toggleSave
        )

        self.w.button = vanilla.Button((15, 180, -15, 30), "Generate", callback=self.insert)
        self.w.open()

        self._normalizeCaseToggles(save=False)

    def _save(self, sender=None):
        def _int(v, d):
            try:
                return int(str(v).strip())
            except:
                return d

        setpref_font(self.font, "wordCount", max(1, _int(self.w.lengthInput.get(), 30)))
        setpref_font(self.font, "minLen", _int(self.w.minInput.get(), 2))
        setpref_font(self.font, "maxLen", _int(self.w.maxInput.get(), 20))
        setpref_font(self.font, "mustInclude", self.w.mustContainInput.get() or "")
        setpref_font(self.font, "titleCase", bool(self.w.titleCaseToggle.get()))
        setpref_font(self.font, "upperCase", bool(self.w.upperCaseToggle.get()))

    def _normalizeCaseToggles(self, save=True):
        if self.w.titleCaseToggle.get() and self.w.upperCaseToggle.get():
            self.w.upperCaseToggle.set(False)
        if save:
            self._save()

    def _toggleSave(self, sender):
        if sender == self.w.titleCaseToggle and sender.get():
            self.w.upperCaseToggle.set(False)
        elif sender == self.w.upperCaseToggle and sender.get():
            self.w.titleCaseToggle.set(False)
        self._save()

    def insert(self, sender):
        self._save()

        try:
            wordCount = max(1, int(self.w.lengthInput.get()))
            minLen    = max(1, int(self.w.minInput.get()))
            maxLen    = max(minLen, int(self.w.maxInput.get()))
        except:
            Glyphs.showNotification("Invalid input", "Length values must be numbers.")
            return

        useTitle = bool(self.w.titleCaseToggle.get())
        useUpper = bool(self.w.upperCaseToggle.get())
        mustIncl = self.w.mustContainInput.get() or ""

        try:
            allowed = getDrawnCharacters(self.font)
            words = loadWordList()

            pool = filterWords(
                words,
                allowed,
                titleCase=useTitle,
                upperCase=useUpper,
                minLen=minLen,
                maxLen=maxLen,
                mustInclude=mustIncl
            )

            if not pool:
                print("WORD GENERATOR — NO RESULTS")
                print("mustInclude:", mustIncl)
                Glyphs.showNotification("No usable words", "No words satisfy the current constraints.")
                return

            self.font.newTab(generateParagraph(pool, wordCount))
            self.w.close()

        except Exception:
            traceback.print_exc()
            Glyphs.showNotification(
                "Word Generator error",
                "An internal error occurred. See Macro Window."
            )

WordGenerator()
