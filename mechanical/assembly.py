#!/usr/bin/env python3
"""Granit mechanical assembly — FreeCAD script.

Run with: freecadcmd mechanical/assembly.py
Produces: mechanical/assembly.step and mechanical/assembly.FCStd
"""

import sys
sys.path.append("/usr/lib/freecad/lib")

import FreeCAD
import Part
import Import

# === Dimensions (mm) ===
# Hammond 1455L2201 internals
case_wall = 1.5
belly_plate = 1.0

# PCB
pcb_length = 71
pcb_width = 101
standoff_height = 3.0
gap = 2  # between PCB and HDD

# HDD
hdd_length = 147
hdd_width = 101.6

# === File paths ===
case_file = "hardware/3d-models/1455L2201.stp"
pcb_file = "mechanical/granit-pcb.step"
hdd_file = "mechanical/3.5inch_HDD_NAS.step"
output_step = "mechanical/assembly.step"
output_fcstd = "mechanical/assembly.FCStd"

# === Create document ===
doc = FreeCAD.newDocument("GranitAssembly")

# === Import case ===
Import.insert(case_file, doc.Name)
case = doc.Objects[-1]
case.Label = "Hammond_1455L2201"

# === Import PCB ===
Import.insert(pcb_file, doc.Name)
pcb = doc.Objects[-1]
pcb.Label = "Granit_PCB"

# Position PCB: inside case, on standoffs, connector edge at front
# Case origin is at corner; PCB sits near the front (x=0 side)
pcb_x = 0
pcb_y = (100 - pcb_width) / 2 + case_wall  # centered in case width
pcb_z = belly_plate + standoff_height
pcb.Placement = FreeCAD.Placement(
    FreeCAD.Vector(pcb_x, pcb_y, pcb_z),
    FreeCAD.Rotation(0, 0, 0)
)

# === Import HDD ===
Import.insert(hdd_file, doc.Name)
hdd = doc.Objects[-1]
hdd.Label = "NAS_HDD_3.5inch"

# Position HDD: next to PCB, flat on belly plate
hdd_x = pcb_length + gap
hdd_y = (100 - hdd_width) / 2 + case_wall  # centered
hdd_z = belly_plate
hdd.Placement = FreeCAD.Placement(
    FreeCAD.Vector(hdd_x, hdd_y, hdd_z),
    FreeCAD.Rotation(0, 0, 0)
)

# === Recompute ===
doc.recompute()

# === Export ===
shapes = [obj for obj in doc.Objects if hasattr(obj, "Shape") and obj.Shape.Solids]
Part.export(shapes, output_step)
doc.saveAs(output_fcstd)

print(f"Assembly saved to {output_step} and {output_fcstd}")
print(f"PCB position: ({pcb_x}, {pcb_y}, {pcb_z})")
print(f"HDD position: ({hdd_x}, {hdd_y}, {hdd_z})")
