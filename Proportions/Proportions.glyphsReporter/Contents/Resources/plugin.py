# encoding: utf-8

import objc
from GlyphsApp import Glyphs, GSNode, GSCallbackHandler, OFFCURVE, VIEW_MENU, DRAWFOREGROUND
from GlyphsApp.plugins import GeneralPlugin
from vanilla import Window, TextBox
from vanilla.vanillaGroup import Group
from math import degrees, atan2, tan, radians
from Foundation import NSPoint, NSMaxX, NSMaxY, NSMenuItem


# Our own patched Vanilla Group class
class PatchedGroup(Group):
    nsViewClass = objc.lookUpClass("GSInspectorView")


class ClickableTextBoxView(TextBox.nsTextFieldClass):
    def mouseUp_(self, event):
        if hasattr(self, 'mouseUpCallback') and self.mouseUpCallback:
            self.mouseUpCallback(event)


class ClickableTextBox(TextBox):
    nsTextFieldClass = ClickableTextBoxView

    def __init__(self, *args, **kwargs):
        self.mouseUpCallback = kwargs.pop('mouseUpCallback', None)
        super(ClickableTextBox, self).__init__(*args, **kwargs)
        self._nsObject.mouseUpCallback = self.mouseUpCallback


class ShowAngleAndDistance(GeneralPlugin):

    @objc.python_method
    def settings(self):
        self.isVisible = False
        self.state = False
        self.showItalicWidth = True
        self.menuName = 'Angle & Distance of Selection'
        self.name = 'Show Angle And Distance'

        viewWidth = 60
        viewHeight = 40
        self.angleWindow = Window((viewWidth, viewHeight))
        self.angleWindow.group = PatchedGroup((0, 0, viewWidth, viewHeight))

        if Glyphs.versionNumber >= 3:
            self.angleWindow.group.text = ClickableTextBox("auto", self.name, mouseUpCallback=self.mouseUpCallback)
            try:
                rules = [
                    "H:|-6-[text]-8-|",
                    "V:|-5-[text]-5-|",
                ]
                self.angleWindow.group.addAutoPosSizeRules(rules)
            except Exception as e:
                import traceback
                print(traceback.format_exc(), e)

        else:
            self.angleWindow.group.text = ClickableTextBox((3, 6, 100, 100), self.name, sizeStyle='small', mouseUpCallback=self.mouseUpCallback)

        GSCallbackHandler.addCallback_forOperation_(self, "GSInspectorViewControllersCallback")

    @objc.python_method
    def start(self):
        self.loadPreferences()
        if Glyphs.versionNumber >= 3.3:
            menuItem = NSMenuItem(self.menuName, callback=self.toggleMenu_, target=self)
        else:
            menuItem = NSMenuItem(self.menuName, self.toggleMenu_)
        Glyphs.menu[VIEW_MENU].append(menuItem)
        Glyphs.menu[VIEW_MENU].submenu().itemWithTitle_(self.menuName).setState_(self.state)
        Glyphs.addCallback(self.drawForeground, DRAWFOREGROUND)

    def toggleMenu_(self, sender):
        currentState = Glyphs.menu[VIEW_MENU].submenu().itemWithTitle_(self.menuName).state()
        self.state = not currentState
        Glyphs.menu[VIEW_MENU].submenu().itemWithTitle_(self.menuName).setState_(self.state)
        self.savePreferences()

    @objc.python_method
    def savePreferences(self):
        try:
            Glyphs.defaults['no.skriftkontoret.ShowAngleAndDistance.menu'] = self.state
            Glyphs.defaults['no.skriftkontoret.ShowAngleAndDistance.showItalicWidth'] = self.showItalicWidth
        except:
            import traceback
            print('Could not save preferences')
            print(traceback.format_exc())
            return False
        return True

    @objc.python_method
    def loadPreferences(self):
        try:
            self.state = Glyphs.defaults['no.skriftkontoret.ShowAngleAndDistance.menu']
            self.showItalicWidth = Glyphs.defaults['no.skriftkontoret.ShowAngleAndDistance.showItalicWidth']
            if not self.state:
                self.state = False
            if not self.showItalicWidth:
                self.showItalicWidth = False
        except:
            import traceback
            print(traceback.format_exc())

    def inspectorViewControllersForLayer_(self, layer):
        if self.state and self.isVisible:
            return [self]
        return []

    def view(self):
        return self.angleWindow.group.getNSView()

    @objc.python_method
    def nicelyRound(self, value):
        roundedValue = round(value, 1)
        if roundedValue == int(roundedValue):
            return int(roundedValue)
        else:
            return roundedValue

    @objc.python_method
    def getDist(self, point1, point2):
        distance = ((point2.x - point1.x)**2 + (point2.y - point1.y)**2)**0.5
        return (self.nicelyRound(distance))

    @objc.python_method
    def getAngle(self, point1, point2):
        dx = point2.x - point1.x
        dy = point2.y - point1.y
        angle_radians = atan2(dy, dx)
        angle_degrees = degrees(angle_radians)
        angle_degrees = 90 - angle_degrees
        if angle_degrees < 0:
            angle_degrees += 360
        angle_degrees = self.nicelyRound(angle_degrees)
        return angle_degrees

    @objc.python_method
    def italicize(self, thisPoint, italicAngle=0, pivotalY=0):
        x = thisPoint.x
        yOffset = thisPoint.y - pivotalY
        italicAngle = radians(italicAngle)
        tangens = tan(italicAngle)
        horizontalDeviance = tangens * yOffset
        x += horizontalDeviance
        return NSPoint(int(x), thisPoint.y)

    @objc.python_method
    def getItalicizedWidth(self, point1, point2, angle):
        angledPoint2 = self.italicize(point2, italicAngle=angle, pivotalY=point1.y)
        italicizedWidth = self.nicelyRound(abs(point1.x - angledPoint2.x))
        return italicizedWidth

    @objc.python_method
    def mouseUpCallback(self, event):
        self.showItalicWidth = not self.showItalicWidth
        self.savePreferences()
        if Glyphs.font and Glyphs.font.selectedLayers:
            self.reportAngle(Glyphs.font.selectedLayers[0])

    @objc.python_method
    def reportAngle(self, layer):
        if not layer:
            return

        selection = layer.selection
        associatedOncurve = None

        if len(selection) == 0:
            self.isVisible = False
            return

        elif len(selection) == 1:
            if isinstance(selection[0], GSNode) and selection[0].type == OFFCURVE:
                associatedOncurve = selection[0].nextNode if selection[0].nextNode.type != OFFCURVE else selection[0].prevNode
                selection.append(associatedOncurve)
            else:
                self.isVisible = False
                return

        selectionBounds = layer.selectionBounds
        point1 = selectionBounds.origin
        point2 = NSPoint(NSMaxX(selectionBounds), NSMaxY(selectionBounds))

        angle = self.getAngle(point1, point2)
        distance = self.getDist(point1, point2)
        italicAngle = layer.italicAngle if Glyphs.versionNumber >= 3 else layer.italicAngle()
        italicizedWidth = self.getItalicizedWidth(point1, point2, -italicAngle) if self.showItalicWidth and italicAngle else None

        # --- NEW: ratio calculation ---
        width = selectionBounds.size.width
        height = selectionBounds.size.height
        ratio = None
        if width != 0:
            ratio = height / float(width)
            ratio = f"1:{ratio:.3f}"
        # --------------------------------

        if associatedOncurve:
            selection.remove(associatedOncurve)

        if angle is not None:
            if italicizedWidth is not None:
                angleString = u'◿  %s°\n𝑖↔︎  %s' % (angle, italicizedWidth)
            else:
                angleString = u'◿  %s°\n⤢  %s' % (angle, distance)

            if ratio:
                angleString += u'\n⇅  %s' % ratio

            self.angleWindow.group.text.set(angleString)
            self.isVisible = True

    @objc.python_method
    def drawForeground(self, layer, info):
        self.reportAngle(layer)
