# Open Layers with Close Nodes

from GlyphsApp import *
import math

THRESHOLD = 5.0

font = Glyphs.font

if not font:
    print("No font open.")
else:
    layersToOpen = []

    for glyph in font.glyphs:
        for master in font.masters:
            layer = glyph.layers[master.id]
            if not layer:
                continue

            foundCloseNodes = False

            for path in layer.paths:
                nodes = [n for n in path.nodes if n.type != OFFCURVE]
                nodeCount = len(nodes)

                for i in range(nodeCount):
                    n1 = nodes[i]
                    for j in range(i + 1, nodeCount):
                        n2 = nodes[j]

                        dx = n1.position.x - n2.position.x
                        dy = n1.position.y - n2.position.y
                        distance = math.hypot(dx, dy)

                        if distance < THRESHOLD:
                            layersToOpen.append(layer)
                            foundCloseNodes = True
                            break
                    if foundCloseNodes:
                        break
                if foundCloseNodes:
                    break

    if layersToOpen:
        font.newTab(layersToOpen)
        print(f"Opened {len(layersToOpen)} layers with on-curve nodes closer than {THRESHOLD} units.")
    else:
        print("No layers found with close on-curve nodes.")