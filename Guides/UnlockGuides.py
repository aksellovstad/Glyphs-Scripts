#MenuTitle: Unlock guides
# -*- coding: utf-8 -*-
from GlyphsApp import Glyphs

font = Glyphs.font
if not font:
    try:
        Glyphs.showNotification("Unlock Guides", "No font open.")
    except Exception:
        pass
    print("No font open.")
else:
    selected_layers = getattr(font, "selectedLayers", []) or []
    if not selected_layers:
        try:
            Glyphs.showNotification("Unlock Guides", "No glyph/layer selected.")
        except Exception:
            pass
        print("No glyph/layer selected.")
    else:
        selected_layer = selected_layers[0]
        glyph = selected_layer.parent
        current_master = getattr(font, "selectedFontMaster", None)

        # Find the layer that corresponds to the current master (robustly)
        target_layer = None
        if current_master is not None:
            for layer in glyph.layers:
                try:
                    if getattr(layer, "associatedMasterId", None) == getattr(current_master, "id", None):
                        target_layer = layer
                        break
                except Exception:
                    pass
            # fallback: try matching names
            if target_layer is None:
                for layer in glyph.layers:
                    try:
                        if getattr(layer, "name", None) == getattr(current_master, "name", None):
                            target_layer = layer
                            break
                    except Exception:
                        pass

        if target_layer is None:
            target_layer = selected_layer

        guides = list(getattr(target_layer, "guides", []))

        if not guides:
            msg = f"No guides found in glyph '{glyph.name}' for the current master."
            try:
                Glyphs.showNotification("Unlock Guides", msg)
            except Exception:
                pass
            print(msg)
        else:
            # Try to disable UI updates (if the method exists) — safe guards around every call
            try:
                if hasattr(Glyphs, "disableUpdate"):
                    Glyphs.disableUpdate()
                elif hasattr(Glyphs, "disableUpdates"):
                    Glyphs.disableUpdates()
            except Exception:
                pass

            # Try to begin an undo group if available
            try:
                if hasattr(font, "beginUndo"):
                    font.beginUndo()
            except Exception:
                pass

            unlocked = 0
            try:
                for g in guides:
                    try:
                        if hasattr(g, "locked"):
                            if g.locked:
                                g.locked = False
                                unlocked += 1
                        elif hasattr(g, "lock"):
                            if g.lock:
                                g.lock = False
                                unlocked += 1
                        else:
                            # best-effort fallback
                            try:
                                setattr(g, "locked", False)
                                unlocked += 1
                            except Exception:
                                pass
                    except Exception:
                        # skip any guide that errors
                        pass
            finally:
                # end undo group if available
                try:
                    if hasattr(font, "endUndo"):
                        font.endUndo()
                except Exception:
                    pass

                # Re-enable UI updates if we disabled them
                try:
                    if hasattr(Glyphs, "enableUpdate"):
                        Glyphs.enableUpdate()
                    elif hasattr(Glyphs, "enableUpdates"):
                        Glyphs.enableUpdates()
                except Exception:
                    pass

            msg = f"Unlocked {unlocked} guide{'s' if unlocked != 1 else ''} in '{glyph.name}'."
            try:
                Glyphs.showNotification("Unlock Guides", msg)
            except Exception:
                pass
            print(msg)
