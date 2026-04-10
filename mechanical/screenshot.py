#!/usr/bin/env python3
"""Render assembly screenshot with software OpenGL.
Run with: LIBGL_ALWAYS_SOFTWARE=1 ASSEMBLY_FILE=... xvfb-run -a -s "-screen 0 3840x2160x24" freecad screenshot.py
"""

import os
import sys
import FreeCAD
import FreeCADGui
import Import

assembly_file = os.environ.get("ASSEMBLY_FILE", "mechanical/assembly-wide.step")
output_png = assembly_file.replace(".step", ".png")

doc = FreeCAD.newDocument("render")
Import.insert(assembly_file, doc.Name)
doc.recompute()

for obj in doc.Objects:
    if not (hasattr(obj, "Shape") and obj.Shape.Solids and hasattr(obj, "ViewObject")):
        continue
    bb = obj.Shape.BoundBox
    try:
        # PCB: 92mm X, 100mm Z, very thin Y (<5mm)
        if bb.YLength < 5 and bb.XLength > 80 and bb.XLength < 100 and bb.ZLength > 90 and bb.ZLength < 110:
            obj.ViewObject.ShapeColor = (0.0, 0.8, 0.0)
            continue
        # HDD: distinguish from case — HDD Y height is 9-27mm and Z < 150mm
        if bb.ZLength > 90 and bb.ZLength < 150 and bb.YLength > 5 and bb.YLength < 40 and bb.XLength < 110:
            obj.ViewObject.ShapeColor = (0.9, 0.15, 0.1)
            continue
        # Screws/small parts
        if bb.XLength < 15 and bb.YLength < 15 and bb.ZLength < 15:
            obj.ViewObject.ShapeColor = (0.4, 0.4, 0.4)
            obj.ViewObject.Transparency = 60
            continue
        # Hide lid (thin piece near Y=0)
        if bb.YMax > -5 and bb.YLength < 6 and bb.XLength > 80 and bb.ZLength > 80:
            obj.ViewObject.Visibility = False
            continue
        # Everything else is case — gray, very transparent
        obj.ViewObject.ShapeColor = (0.6, 0.6, 0.6)
        obj.ViewObject.Transparency = 88
    except:
        pass

view = FreeCADGui.ActiveDocument.ActiveView

# Enable anti-aliasing
from pivy import coin
cam = view.getCameraNode()

# Angled view showing inside and front (connector) edge
rot = coin.SbRotation(coin.SbVec3f(1, 0, 0), 0.45)    # tilt down
rot *= coin.SbRotation(coin.SbVec3f(0, 0, 1), 0.4)     # rotate to show connector edge (+Z)
cam.orientation.setValue(rot)
view.fitAll()

# Render at high resolution
view.saveImage(output_png, 3840, 2160, "White")

print(f"Screenshot saved to {output_png}")
sys.exit(0)
