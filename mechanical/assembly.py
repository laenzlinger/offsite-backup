#!/usr/bin/env python3
"""Granit mechanical assembly — FreeCAD script.

Run with: freecadcmd -c mechanical/assembly.py
Produces: mechanical/assembly.step and mechanical/assembly.FCStd
"""

import FreeCAD
import Part
import Import

# === Dimensions (mm) ===
case_wall = 1.5
belly_plate = 1.0
standoff_height = 3.0
pcb_length = 71
pcb_width = 101
gap = 2

# === File paths ===
case_file = "hardware/3d-models/1455L2201.stp"
pcb_file = "mechanical/granit-pcb.step"
hdd_file = "mechanical/3.5inch_HDD_NAS.step"
output_step = "mechanical/assembly.step"
output_fcstd = "mechanical/assembly.FCStd"

# === Create document ===
doc = FreeCAD.newDocument("GranitAssembly")

def import_and_move(filepath, label, placement):
    """Import STEP, group all new objects, apply placement."""
    before = set(obj.Name for obj in doc.Objects)
    Import.insert(filepath, doc.Name)
    after = set(obj.Name for obj in doc.Objects)
    new_names = after - before

    for name in new_names:
        obj = doc.getObject(name)
        if hasattr(obj, "Shape") and obj.Shape.Solids:
            obj.Label = label + "_" + obj.Label
            obj.Placement = placement
    return new_names

# === Import case (at origin) ===
import_and_move(case_file, "Case",
    FreeCAD.Placement(FreeCAD.Vector(0, 0, 0), FreeCAD.Rotation(0, 0, 0)))

# === Import PCB ===
# KiCad exports PCB in XY plane. Position inside case on standoffs.
# Connector edge (RJ45 etc) at x=0, SATA edge at x=71
pcb_offset = FreeCAD.Vector(
    0,                                    # connector edge at case front
    case_wall + (100 - pcb_width) / 2,   # centered in width
    belly_plate + standoff_height         # on standoffs
)
import_and_move(pcb_file, "PCB",
    FreeCAD.Placement(pcb_offset, FreeCAD.Rotation(0, 0, 0)))

# === Import HDD ===
hdd_offset = FreeCAD.Vector(
    pcb_length + gap,                     # after PCB + gap
    case_wall + (100 - 101.6) / 2,       # centered in width
    belly_plate                           # flat on belly plate
)
import_and_move(hdd_file, "HDD",
    FreeCAD.Placement(hdd_offset, FreeCAD.Rotation(0, 0, 0)))

# === Recompute and save ===
doc.recompute()

shapes = [obj for obj in doc.Objects if hasattr(obj, "Shape") and obj.Shape.Solids]
Part.export(shapes, output_step)
doc.saveAs(output_fcstd)

print(f"Assembly saved: {len(shapes)} solid parts")
print(f"PCB at: {pcb_offset}")
print(f"HDD at: {hdd_offset}")
