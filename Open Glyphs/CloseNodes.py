# Open Glyphs with Close Nodes

from GlyphsApp import *
import math

THRESHOLD = 5.0  # distance in font units

font = Glyphs.font

if not font:
    print("No font open.")
else:
    glyphsToOpen = set()

    for glyph in font.glyphs:
        for master in font.masters:
            layer = glyph.layers[master.id]
            if not layer:
                continue

            for path in layer.paths:
                # Only on-curve nodes (ignore handles)
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
                            glyphsToOpen.add(glyph.name)
                            break
                    else:
                        continue
                    break
                else:
                    continue
                break

    if glyphsToOpen:
        font.newTab("/" + "/".join(sorted(glyphsToOpen)))
        print(f"Opened {len(glyphsToOpen)} glyphs with on-curve nodes closer than {THRESHOLD} units.")
    else:
        print("No glyphs found with close on-curve nodes.")
