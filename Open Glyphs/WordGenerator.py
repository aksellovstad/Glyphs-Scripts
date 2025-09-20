# MenuTitle: Word Generator
# -*- coding: utf-8 -*-
__doc__ = """
Generates words using only drawn glyphs in the current selected master. Filters by word count, word length (min/max),
and must-include characters (space-separated; each string can be single or multi-letter, e.g. 's tf e').
Remembers last-used settings per font (stored in font.userData["sk.wordgen"]).
"""

from GlyphsApp import Glyphs
import GlyphsApp
import random
import vanilla
import os

# -----------------------------
# Per-font persistence (font.userData)
# -----------------------------
UDK = "sk.wordgen"  # userData key on the font

def getpref_font(font, key, default):
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
# Dictionary
# -----------------------------
DICTIONARY_PATH = "/usr/share/dict/words"

def loadWordList():
    if os.path.exists(DICTIONARY_PATH):
        try:
            with open(DICTIONARY_PATH, "r", encoding="utf-8") as f:
                return [w.strip() for w in f if w.strip().isalpha()]
        except Exception:
            pass
    return []

# -----------------------------
# Font helpers
# -----------------------------
def getDrawnCharacters(font):
    """Return the exact-case characters that have drawn content in the selected master."""
    master = font.selectedFontMaster or font.masters[0]
    chars = set()
    for g in font.glyphs:
        if not g.export or not g.unicode:
            continue
        layer = g.layers[master.id]
        if layer and (layer.paths or layer.components):
            try:
                ch = chr(int(g.unicode, 16))
                chars.add(ch)  # keep case as-is
            except Exception:
                pass
    return chars  # case-sensitive set

def _tokens_from_string(mustInclude):
    # Split on spaces; ignore empties (supports multi-letter tokens)
    return [t for t in (mustInclude or "").split() if t]

def filterWords(wordList, allowedChars, titleCase=False, upperCase=False,
                minLen=2, maxLen=20, mustInclude=""):
    tokens = _tokens_from_string(mustInclude)

    out = []
    for w in wordList:
        if not (minLen <= len(w) <= maxLen):
            continue

        # Build candidate in desired case
        if upperCase:
            cand = w.upper()
        elif titleCase:
            cand = w.capitalize()
        else:
            cand = w.lower()

        # Must be composed ONLY of characters that are actually drawn in THIS case
        if not set(cand).issubset(allowedChars):
            continue

        # Token matching: case-insensitive (user convenience)
        if tokens:
            cand_ci = cand.lower()
            if not any(tok.lower() in cand_ci for tok in tokens):
                continue

        out.append(cand)
    return out

def generateParagraph(words, wordCount=30):
    return " ".join(random.choice(words) for _ in range(wordCount)) + "."

# -----------------------------
# UI
# -----------------------------
class WordGenerator:
    def __init__(self):
        self.font = Glyphs.font
        if not self.font:
            try:
                Glyphs.showNotification("Word Generator", "No font open.")
            except Exception:
                print("Word Generator: No font open.")
            return

        # Load per-font prefs
        wordCount = int(getpref_font(self.font, "wordCount", 30))
        minLen    = int(getpref_font(self.font, "minLen", 2))
        maxLen    = int(getpref_font(self.font, "maxLen", 20))
        mustIncl  = str(getpref_font(self.font, "mustInclude", ""))
        titleOn   = bool(getpref_font(self.font, "titleCase", False))
        upperOn   = bool(getpref_font(self.font, "upperCase", False))

        self.w = vanilla.FloatingWindow((360, 240), "Word Generator")

        self.w.wordCountLabel = vanilla.TextBox((15, 18, 80, 17), "Word count:", sizeStyle="small")
        self.w.lengthInput    = vanilla.EditText((100, 16, 50, 22), str(wordCount), callback=self._save)

        self.w.minLabel  = vanilla.TextBox((15, 48, 80, 17), "Min length:", sizeStyle="small")
        self.w.minInput  = vanilla.EditText((100, 46, 40, 22), str(minLen), callback=self._save)

        self.w.maxLabel  = vanilla.TextBox((160, 48, 80, 17), "Max length:", sizeStyle="small")
        self.w.maxInput  = vanilla.EditText((245, 46, 40, 22), str(maxLen), callback=self._save)

        self.w.mustContainLabel = vanilla.TextBox((15, 78, 150, 17), "Must include (tokens):", sizeStyle="small")
        self.w.mustContainInput = vanilla.EditText((165, 76, 140, 22), mustIncl, callback=self._save)

        self.w.titleCaseToggle = vanilla.CheckBox((15, 108, -15, 20), "Use Title Case", value=titleOn, callback=self._toggleSave)
        self.w.upperCaseToggle = vanilla.CheckBox((15, 130, -15, 20), "Use UPPERCASE", value=upperOn, callback=self._toggleSave)

        self.w.button = vanilla.Button((15, 180, -15, 30), "Generate", callback=self.insert)
        self.w.open()

        # ensure mutual exclusivity on load
        self._normalizeCaseToggles(save=False)

    # ---------- Persistence ----------
    def _save(self, sender=None):
        def _int(v, default):
            try:
                return int(str(v).strip())
            except Exception:
                return default
        setpref_font(self.font, "wordCount", max(1, _int(self.w.lengthInput.get(), 30)))
        setpref_font(self.font, "minLen",    _int(self.w.minInput.get(), 2))
        setpref_font(self.font, "maxLen",    _int(self.w.maxInput.get(), 20))
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

    # ---------- Core ----------
    def insert(self, sender):
        self._save()

        try:
            wordCount = max(1, int(self.w.lengthInput.get()))
            minLen    = max(2, int(self.w.minInput.get()))
            maxLen    = max(minLen, int(self.w.maxInput.get()))
        except Exception:
            Glyphs.showNotification("Invalid input", "Please enter valid numbers.")
            return

        useTitle = bool(self.w.titleCaseToggle.get())
        useUpper = bool(self.w.upperCaseToggle.get())
        mustIncl = (self.w.mustContainInput.get() or "").strip()

        allowed = getDrawnCharacters(self.font)  # exact-case allowed set
        words   = loadWordList()
        pool    = filterWords(words, allowed, titleCase=useTitle, upperCase=useUpper,
                              minLen=minLen, maxLen=maxLen, mustInclude=mustIncl)

        if not pool:
            Glyphs.showNotification("No usable words", "No words match your filters.")
            return

        text = generateParagraph(pool, wordCount)
        self.font.newTab(text)  # no forced size

        self.w.close()

WordGenerator()
