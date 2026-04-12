#!/usr/bin/env python3
"""Add GND stitching vias to the Granit PCB.

Usage: python3 add-stitching-vias.py
Then open the PCB in KiCad, Fill All Zones, Run DRC.
"""

import math
import pcbnew

GRID_MM = 5.0
CLEARANCE_MM = 0.6  # min distance from any copper
EDGE_MARGIN_MM = 1.5
VIA_DIA_NM = int(0.8e6)
VIA_DRILL_NM = int(0.4e6)

board = pcbnew.LoadBoard("granit.kicad_pcb")

bb = board.GetBoardEdgesBoundingBox()
x_min, x_max = bb.GetX(), bb.GetRight()
y_min, y_max = bb.GetY(), bb.GetBottom()

gnd_net = board.GetNetInfo().GetNetItem("GND")
clearance = int(CLEARANCE_MM * 1e6)
edge_margin = int(EDGE_MARGIN_MM * 1e6)
via_r = VIA_DIA_NM // 2


def point_to_segment_dist(px, py, ax, ay, bx, by):
    """Distance from point (px,py) to line segment (ax,ay)-(bx,by)."""
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


# Collect obstacles: (type, data)
# For tracks: store as line segments with half-width
segments = []
points = []

for track in board.GetTracks():
    hw = track.GetWidth() // 2 if not isinstance(track, pcbnew.PCB_VIA) else VIA_DIA_NM // 2
    s = track.GetStart()
    if isinstance(track, pcbnew.PCB_VIA):
        points.append((s.x, s.y, hw + clearance))
    else:
        e = track.GetEnd()
        segments.append((s.x, s.y, e.x, e.y, hw + clearance))

for fp in board.GetFootprints():
    for pad in fp.Pads():
        pos = pad.GetPosition()
        pbb = pad.GetBoundingBox()
        r = max(pbb.GetWidth(), pbb.GetHeight()) // 2
        points.append((pos.x, pos.y, r + clearance))

    # Courtyard as bounding box
    for item in fp.GraphicalItems():
        if item.GetLayer() in [pcbnew.F_CrtYd, pcbnew.B_CrtYd]:
            ibb = item.GetBoundingBox()
            cx = (ibb.GetX() + ibb.GetRight()) // 2
            cy = (ibb.GetY() + ibb.GetBottom()) // 2
            r = max(ibb.GetWidth(), ibb.GetHeight()) // 2
            points.append((cx, cy, r + clearance))


def is_clear(x, y):
    for px, py, r in points:
        if math.hypot(x - px, y - py) < r + via_r:
            return False
    for ax, ay, bx, by, r in segments:
        if point_to_segment_dist(x, y, ax, ay, bx, by) < r + via_r:
            return False
    return True


grid = int(GRID_MM * 1e6)
placed = 0
skipped = 0

x = x_min + edge_margin
while x < x_max - edge_margin:
    y = y_min + edge_margin
    while y < y_max - edge_margin:
        if is_clear(int(x), int(y)):
            via = pcbnew.PCB_VIA(board)
            via.SetPosition(pcbnew.VECTOR2I(int(x), int(y)))
            via.SetWidth(pcbnew.F_Cu, VIA_DIA_NM)
            via.SetDrill(VIA_DRILL_NM)
            via.SetNet(gnd_net)
            board.Add(via)
            placed += 1
        else:
            skipped += 1
        y += grid
    x += grid

board.Save("granit.kicad_pcb")

area_cm2 = ((x_max - x_min) / 1e7) * ((y_max - y_min) / 1e7)
total_gnd = 113 + placed
print(f"Placed {placed} new GND stitching vias ({skipped} skipped)")
print(f"Total GND vias: ~{total_gnd} ({total_gnd / area_cm2:.1f} per cm²)")
print(f"Open in KiCad → Fill All Zones → Run DRC")
