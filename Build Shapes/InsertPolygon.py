#MenuTitle: Insert Polygon
# -*- coding: utf-8 -*-
from math import pi, cos, sin
from GlyphsApp import GSPath, GSNode, GSLINE
from vanilla import FloatingWindow, TextBox, EditText, Button
from AppKit import NSTextField

# ---------------------------------------------------------
# Geometry
# ---------------------------------------------------------

def polygon_points_int(sides, size, cx, cy):
    sides = max(3, int(sides))
    size  = max(1, int(size))
    R = float(size) / (2.0 * cos(pi / sides))
    rotation = (pi/2.0) - (pi / sides)

    for _ in range(20):
        pts_f = []
        for i in range(sides):
            a = 2.0 * pi * i / sides + rotation
            x = cx + R * cos(a)
            y = cy + R * sin(a)
            pts_f.append((x, y))

        ys_int = [int(round(y)) for (_, y) in pts_f]
        h_int = max(ys_int) - min(ys_int)

        if h_int == size or h_int == 0:
            return [(int(round(x)), int(round(y))) for (x, y) in pts_f]

        scale = float(size) / float(h_int)
        if abs(scale - 1.0) < 1e-6:
            return [(int(round(x)), int(round(y))) for (x, y) in pts_f]

        R *= scale

    return [(int(round(x)), int(round(y))) for (x, y) in pts_f]

# ---------------------------------------------------------
# Drawing
# ---------------------------------------------------------

def draw_preview(layer, pts, prev):
    try:
        if prev and prev in layer.shapes:
            layer.shapes.remove(prev)
    except Exception:
        pass

    p = GSPath()
    for (x, y) in pts:
        p.nodes.append(GSNode((x, y), type=GSLINE))

    p.closed = True
    layer.shapes.append(p)
    Glyphs.redraw()
    return p

# ---------------------------------------------------------
# Delegate (live change + end editing)
# ---------------------------------------------------------

class LiveDelegate(object):
    """
    Calls the callback on every keystroke (controlTextDidChange_)
    and also validates sides >= 3 when editing ends.
    """
    def __init__(self, field, isSidesField, callback):
        self.field = field
        self.isSidesField = isSidesField
        self.callback = callback

    def controlTextDidChange_(self, notification):
        # live change event
        self.callback(None)

    def controlTextDidEndEditing_(self, notification):
        # fix invalid sides on exit
        if self.isSidesField:
            text = self.field.get().strip()
            if text in ("0", "1", "2", ""):
                self.field.set("3")
        self.callback(None)

# ---------------------------------------------------------
# UI
# ---------------------------------------------------------

class LivePolygon:
    def __init__(self):
        self.w = FloatingWindow((320,130), "Insert Polygon")

        # Sides
        self.w.sidesLabel = TextBox((10,10,60,18), "Sides:")
        self.w.sides = EditText((80,10,80,22), "5", callback=self.changed)
        self.w.sidesMinus = Button((165,10,24,18), "−", callback=lambda s: self.step('sides', -1))
        self.w.sidesPlus  = Button((193,10,24,18), "+", callback=lambda s: self.step('sides', +1))

        # Attach live delegate
        sidesDel = LiveDelegate(self.w.sides, True, self.changed)
        self.w.sides._nsObject.setDelegate_(sidesDel)

        # Size
        self.w.sizeLabel = TextBox((10,36,60,18), "Size:")
        self.w.size = EditText((80,36,80,22), "200", callback=self.changed)

        # Live delegate for size
        sizeDel = LiveDelegate(self.w.size, False, self.changed)
        self.w.size._nsObject.setDelegate_(sizeDel)

        # Done button
        self.w.done = Button((110,76,100,28), "Done", callback=self.done)

        self.preview = None
        self.changed(None)
        self.w.open()

    # -----------------------------------------------------

    def get_layer(self):
        f = Glyphs.font
        if not f:
            return None
        try:
            return f.selectedLayers[0]
        except Exception:
            return None

    def compute_center(self, layer):
        try:
            cx = layer.width / 2.0
        except:
            cx = 0.0
        cy = 0.0
        return cx, cy

    # -----------------------------------------------------

    def changed(self, sender):
        layer = self.get_layer()
        if not layer:
            return

        # sides
        try:
            sides = int(self.w.sides.get().strip())
        except:
            sides = 5
        sides = max(3, sides)

        # size
        try:
            size = int(self.w.size.get().strip())
        except:
            size = 200
        size = max(1, size)

        cx, cy = self.compute_center(layer)
        pts = polygon_points_int(sides, size, cx, cy)
        self.preview = draw_preview(layer, pts, self.preview)

    # -----------------------------------------------------

    def step(self, field, delta):
        if field == 'sides':
            try:
                v = int(float(self.w.sides.get()))
            except:
                v = 5
            v = max(3, v + delta)
            self.w.sides.set(str(v))
        self.changed(None)

    # -----------------------------------------------------

    def done(self, sender):
        try:
            self.w.close()
        except:
            pass

# ---------------------------------------------------------

LivePolygon()
