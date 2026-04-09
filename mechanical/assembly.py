#!/usr/bin/env python3
"""Granit mechanical assembly — FreeCAD script.

Run with: freecadcmd mechanical/assembly.py
Produces: mechanical/assembly.step and mechanical/assembly.FCStd
"""

import FreeCAD
import Part
import Import

# === Dimensions (mm) ===
standoff_height = 3.0
pcb_length = 71
pcb_width = 101
gap = 2

# === Hammond 1455L2201 model orientation (from STEP) ===
# X = width (103), centered at 0 → -51.5..51.5
# Y = height (30.5), belly at -30.5, lid at 0
# Z = length (220), centered at 0 → -110..110
# We want: X=length, Y=width, Z=height, origin at belly plate corner

case_file = "hardware/3d-models/1455L2201.stp"
pcb_file = "mechanical/granit-pcb.step"
hdd_file = "mechanical/3.5inch_HDD_NAS.step"
output_step = "mechanical/assembly.step"
output_fcstd = "mechanical/assembly.FCStd"

doc = FreeCAD.newDocument("GranitAssembly")


def import_step(filepath):
    """Import STEP, return list of new Part::Feature objects."""
    before = set(obj.Name for obj in doc.Objects)
    Import.insert(filepath, doc.Name)
    new_objs = []
    for obj in doc.Objects:
        if obj.Name not in before and hasattr(obj, "Shape") and obj.Shape.Solids:
            new_objs.append(obj)
    return new_objs


def move_objects(objs, placement):
    """Apply placement to all objects."""
    for obj in objs:
        obj.Placement = placement


# === Import and position case ===
# Rotate so: Z(length)→X, X(width)→Y, Y(height)→Z
# Then translate so belly plate corner is at origin
case_parts = import_step(case_file)
case_rot = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), 90)  # Z→X swap
case_rot2 = FreeCAD.Rotation(FreeCAD.Vector(1, 0, 0), 90)  # then tilt up
case_placement = FreeCAD.Placement(
    FreeCAD.Vector(110, 51.5, 30.5),  # shift to positive quadrant
    case_rot2.multiply(case_rot)
)
move_objects(case_parts, case_placement)
for p in case_parts:
    p.Label = "Case_" + p.Label

# === Import and position PCB ===
# KiCad PCB: origin at (20,20), board is 71x101 in XY plane
# Need to place at connector edge of case
pcb_parts = import_step(pcb_file)
pcb_placement = FreeCAD.Placement(
    FreeCAD.Vector(-20, -20, standoff_height),  # compensate KiCad origin offset
    FreeCAD.Rotation(0, 0, 0)
)
move_objects(pcb_parts, pcb_placement)
for p in pcb_parts:
    p.Label = "PCB_" + p.Label

# === Import and position HDD ===
hdd_parts = import_step(hdd_file)
hdd_placement = FreeCAD.Placement(
    FreeCAD.Vector(pcb_length + gap, 0, 0),  # next to PCB, flat on belly plate
    FreeCAD.Rotation(0, 0, 0)
)
move_objects(hdd_parts, hdd_placement)
for p in hdd_parts:
    p.Label = "HDD_" + p.Label

# === Recompute and save ===
doc.recompute()

shapes = [obj for obj in doc.Objects if hasattr(obj, "Shape") and obj.Shape.Solids]
Part.export(shapes, output_step)
doc.saveAs(output_fcstd)

print(f"Assembly saved: {len(shapes)} solid parts")
