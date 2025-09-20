# MenuTitle: Rename Selected Glyphs
# -*- coding: utf-8 -*-
__doc__ = """
Rename the selected glyphs using Find & Replace on their glyph names.

Options:
• Regex or plain text search
• Case-sensitive toggle
• Replace first match or all matches
• (Optional) Only change the suffix after the first dot (keep 'A.' etc.)

Per-font preferences are stored in font.userData["sk.renamerFR"].
"""

import re
import vanilla
from GlyphsApp import Glyphs

UDK = "sk.renamerFR"  # per-font preferences key

# -----------------------------
# Per-font prefs
# -----------------------------
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
def selected_glyphs(font):
    """Return a de-duplicated list of GSGlyphs from selection (Font or Edit view)."""
    out, seen = [], set()
    try:
        for item in (font.selection or []):
            g = getattr(item, "parent", item)  # handle layers just in case
            if g and getattr(g, "name", None) and g.name not in seen:
                out.append(g); seen.add(g.name)
    except Exception:
        pass
    try:
        for L in (font.selectedLayers or []):
            g = getattr(L, "parent", None)
            if g and getattr(g, "name", None) and g.name not in seen:
                out.append(g); seen.add(g.name)
    except Exception:
        pass
    return out

def next_available_name(font, base):
    """Return base or base.001/.002/... if base exists."""
    if font.glyphs[base] is None:
        return base
    for i in range(1, 1000):
        cand = f"{base}.{i:03d}"
        if font.glyphs[cand] is None:
            return cand
    return None

# -----------------------------
# UI + Logic
# -----------------------------
class RenameFindReplaceUI(object):
    def __init__(self):
        self.font = Glyphs.font
        if not self.font:
            Glyphs.showNotification("Rename Selected Glyphs — F&R", "Open a .glyphs file first.")
            return

        # Load prefs
        default_find     = getpref_font(self.font, "find", "")
        default_replace  = getpref_font(self.font, "replace", "")
        default_regex    = bool(getpref_font(self.font, "regex", False))
        default_case     = bool(getpref_font(self.font, "caseSensitive", False))
        default_global   = bool(getpref_font(self.font, "replaceAll", True))
        default_suffix   = bool(getpref_font(self.font, "limitToSuffix", False))

        self.w = vanilla.FloatingWindow((460, 180), "Rename Selected Glyphs — Find & Replace")

        y = 14
        self.w.findLbl = vanilla.TextBox((14, y+2, 80, 18), "Find:")
        self.w.findInp = vanilla.EditText((90, y, -14, 24), default_find)
        y += 32

        self.w.replLbl = vanilla.TextBox((14, y+2, 80, 18), "Replace:")
        self.w.replInp = vanilla.EditText((90, y, -14, 24), default_replace)
        y += 32

        self.w.regexCB = vanilla.CheckBox((14, y, 120, 20), "Use regex", value=default_regex, callback=self._save)
        self.w.caseCB  = vanilla.CheckBox((140, y, 140, 20), "Case sensitive", value=default_case, callback=self._save)
        self.w.globCB  = vanilla.CheckBox((290, y, -14, 20), "Replace all matches", value=default_global, callback=self._save)
        y += 26

        self.w.suffixCB = vanilla.CheckBox((14, y, -14, 20), "Only change suffix (after first dot)", value=default_suffix, callback=self._save)
        y += 34

        self.w.runBtn = vanilla.Button((14, y, -14, 28), "Rename Selected Glyphs", callback=self.run)
        self.w.open()

    def _save(self, sender=None):
        setpref_font(self.font, "find",         self.w.findInp.get())
        setpref_font(self.font, "replace",      self.w.replInp.get())
        setpref_font(self.font, "regex",        bool(self.w.regexCB.get()))
        setpref_font(self.font, "caseSensitive",bool(self.w.caseCB.get()))
        setpref_font(self.font, "replaceAll",   bool(self.w.globCB.get()))
        setpref_font(self.font, "limitToSuffix",bool(self.w.suffixCB.get()))

    def _compile_pattern(self, text, use_regex, case_sensitive):
        if use_regex:
            flags = 0 if case_sensitive else re.IGNORECASE
            return re.compile(text, flags)
        else:
            flags = 0 if case_sensitive else re.IGNORECASE
            return re.compile(re.escape(text), flags)

    def _sub_once_or_all(self, pattern, repl, s, replace_all):
        if replace_all:
            return pattern.sub(repl, s)
        return pattern.sub(repl, s, count=1)

    def run(self, sender):
        self._save()

        find = (self.w.findInp.get() or "")
        repl = self.w.replInp.get() or ""
        use_regex = bool(self.w.regexCB.get())
        case_sensitive = bool(self.w.caseCB.get())
        replace_all = bool(self.w.globCB.get())
        limit_suffix = bool(self.w.suffixCB.get())

        if not find:
            Glyphs.showNotification("Rename Selected Glyphs — F&R", "Enter something to find.")
            return

        try:
            pattern = self._compile_pattern(find, use_regex, case_sensitive)
        except re.error as e:
            Glyphs.showNotification("Rename Selected Glyphs — F&R", f"Regex error: {e}")
            return

        glyphs = selected_glyphs(self.font)
        if not glyphs:
            Glyphs.showNotification("Rename Selected Glyphs — F&R", "No glyphs selected.")
            return

        renamed = 0
        unchanged = 0
        skipped_no_dot = 0
        errors = 0

        self.font.disableUpdateInterface()
        try:
            for g in glyphs:
                try:
                    old = g.name or ""

                    if limit_suffix:
                        if "." not in old:
                            skipped_no_dot += 1
                            continue
                        prefix, rest = old.split(".", 1)
                        new_rest = self._sub_once_or_all(pattern, repl, rest, replace_all)
                        target = f"{prefix}.{new_rest}"
                    else:
                        target = self._sub_once_or_all(pattern, repl, old, replace_all)

                    if not target or target == old:
                        unchanged += 1
                        continue

                    finalName = next_available_name(self.font, target)
                    if not finalName:
                        # extremely unlikely; treat as unchanged
                        unchanged += 1
                        continue

                    g.name = finalName
                    renamed += 1
                except Exception:
                    errors += 1
        finally:
            self.font.enableUpdateInterface()

        msg = (
            f"Renamed: {renamed} • Unchanged: {unchanged} • "
            f"Skipped no-dot: {skipped_no_dot} • Errors: {errors}"
        )
        print("Rename Selected Glyphs — Find & Replace")
        print(msg)
        Glyphs.showNotification("Rename Selected Glyphs — F&R", msg)

RenameFindReplaceUI()
