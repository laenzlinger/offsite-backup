#!/usr/bin/env python3
"""Render assembly screenshot.
Run with: xvfb-run -a freecad mechanical/screenshot.py
"""

import FreeCAD
import FreeCADGui
import Import

doc = FreeCAD.newDocument("render")
Import.insert("mechanical/assembly.step", doc.Name)
doc.recompute()

# Color parts: case=silver transparent, PCB=green, HDD=dark grey
# The assembly.step merges labels, so identify by bounding box
for obj in doc.Objects:
    if not (hasattr(obj, "Shape") and obj.Shape.Solids and hasattr(obj, "ViewObject")):
        continue
    bb = obj.Shape.BoundBox
    try:
        # PCB: ~99mm in one axis, ~1.5mm thin, ~71mm in another
        if bb.YLength < 3 and bb.XLength > 50 and bb.ZLength > 50:
            obj.ViewObject.ShapeColor = (0.0, 0.5, 0.0)
            continue
        # HDD: ~101.6 x ~26.1 x ~147
        if bb.YLength > 20 and bb.YLength < 30 and bb.ZLength > 100:
            obj.ViewObject.ShapeColor = (0.7, 0.1, 0.1)
            continue
        # Screws: small parts
        if bb.XLength < 10 and bb.YLength < 10 and bb.ZLength < 10:
            obj.ViewObject.ShapeColor = (0.4, 0.4, 0.4)
            obj.ViewObject.Transparency = 60
            continue
        # Everything else is case
        obj.ViewObject.ShapeColor = (0.75, 0.75, 0.78)
        obj.ViewObject.Transparency = 75
    except:
        pass

view = FreeCADGui.ActiveDocument.ActiveView

# Camera: look into the open bottom at an angle
# We want to see inside — look from below-front at a 3/4 angle
from pivy import coin
cam = view.getCameraNode()
rot = coin.SbRotation(coin.SbVec3f(1, 0, 0), 0.15)   # slight tilt from below
rot *= coin.SbRotation(coin.SbVec3f(0, 1, 0), 2.7)    # rotate to see PCB side
cam.orientation.setValue(rot)
view.fitAll()

view.saveImage("mechanical/assembly.png", 1920, 1080, "White")

print("Screenshot saved to mechanical/assembly.png")

import sys
sys.exit(0)
