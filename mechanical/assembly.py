#!/usr/bin/env python3
"""Granit mechanical assembly — FreeCAD script.

Run with: freecadcmd mechanical/assembly.py
Produces: mechanical/assembly.step and mechanical/assembly.FCStd

Case native orientation (Hammond 1455L2201 STEP):
  X = width (103mm), centered: -51.5 to 51.5
  Y = height (30.5mm): belly=-30.5, lid=0
  Z = length (220mm), centered: -110 to 110

Adjust placements interactively in FreeCAD, then copy values back here.
"""

import FreeCAD
import Part
import Import

case_file = "hardware/3d-models/1455T2201.stp"
pcb_file = "mechanical/granit-pcb.step"
hdd_file = "mechanical/3.5inch_HDD_NAS.step"
output_step = "mechanical/assembly.step"
output_fcstd = "mechanical/assembly.FCStd"

doc = FreeCAD.newDocument("GranitAssembly")


def import_step(filepath, label_prefix):
    before = set(obj.Name for obj in doc.Objects)
    Import.insert(filepath, doc.Name)
    parts = []
    for obj in doc.Objects:
        if obj.Name not in before and hasattr(obj, "Shape") and obj.Shape.Solids:
            obj.Label = label_prefix + "_" + obj.Label
            parts.append(obj)
    return parts


# === Case: at origin, no transform ===
case_parts = import_step(case_file, "Case")

# === PCB: no transform, adjust in FreeCAD GUI ===
pcb_parts = import_step(pcb_file, "PCB")

# === HDD: no transform, adjust in FreeCAD GUI ===
hdd_parts = import_step(hdd_file, "HDD")

# === Save ===
doc.recompute()
shapes = [obj for obj in doc.Objects if hasattr(obj, "Shape") and obj.Shape.Solids]
Part.export(shapes, output_step)
doc.saveAs(output_fcstd)

print(f"Assembly saved: {len(shapes)} solid parts")
print("All parts at origin — adjust placement in FreeCAD GUI")
