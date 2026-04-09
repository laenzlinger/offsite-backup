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

# Color parts by size (case=large=transparent, PCB=green, HDD=dark)
for obj in doc.Objects:
    if hasattr(obj, "Shape") and obj.Shape.Solids and hasattr(obj, "ViewObject"):
        bb = obj.Shape.BoundBox
        vol = bb.XLength * bb.YLength * bb.ZLength
        try:
            if vol > 100000:  # case parts
                obj.ViewObject.Transparency = 80
                obj.ViewObject.ShapeColor = (0.8, 0.8, 0.8)
            elif bb.ZLength > 100:  # HDD (147mm along Z)
                obj.ViewObject.ShapeColor = (0.3, 0.3, 0.3)
            elif bb.XLength > 50:  # PCB (99mm along X)
                obj.ViewObject.ShapeColor = (0.0, 0.6, 0.0)
        except:
            pass

view = FreeCADGui.ActiveDocument.ActiveView

# Set camera to show case lying flat on a table
# Case Y axis is height — we want to look from above-front
from pivy import coin
cam = view.getCameraNode()
# Look from top-front-right: rotate so Y(height) points up on screen
rot = coin.SbRotation(coin.SbVec3f(1, 0, 0), -1.2)  # tilt to see top
rot *= coin.SbRotation(coin.SbVec3f(0, 0, 1), 0.5)   # rotate for 3/4 view
cam.orientation.setValue(rot)
view.fitAll()

view.saveImage("mechanical/assembly.png", 1920, 1080, "White")

print("Screenshot saved to mechanical/assembly.png")

import sys
sys.exit(0)
