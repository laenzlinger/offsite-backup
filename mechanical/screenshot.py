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

# Set camera to show case lying flat on a table, viewed from front-top
from pivy import coin
cam = view.getCameraNode()
rot = coin.SbRotation(coin.SbVec3f(1, 0, 0), -0.3)  # mostly from top
rot *= coin.SbRotation(coin.SbVec3f(0, 0, 1), 0.3)   # slight rotation
cam.orientation.setValue(rot)
view.fitAll()

view.saveImage("mechanical/assembly.png", 1920, 1080, "White")

print("Screenshot saved to mechanical/assembly.png")

import sys
sys.exit(0)
