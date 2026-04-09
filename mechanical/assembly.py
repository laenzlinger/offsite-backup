#!/usr/bin/env python3
"""Granit mechanical assembly — FreeCAD script.

Run with: freecadcmd mechanical/assembly.py
Produces: mechanical/assembly.step and mechanical/assembly.FCStd

Case native orientation (Hammond 1455L2201 STEP):
  X = width (103mm), centered: -51.5 to 51.5
  Y = height (30.5mm): belly=-30.5, lid=0
  Z = length (220mm), centered: -110 to 110
"""

import FreeCAD
import Part
import Import

# === Layout parameters ===
standoff_height = 3.0
belly_y = -30.5  # belly plate inner surface
pcb_length = 71
gap = 2  # between PCB and HDD

# PCB sits at one end (Z=-110 side = connector edge)
# HDD sits next to it (toward Z=+110)
pcb_z_start = -110  # connector edge at case end
hdd_z_start = pcb_z_start + pcb_length + gap

# === File paths ===
case_file = "hardware/3d-models/1455L2201.stp"
pcb_file = "mechanical/granit-pcb.step"
hdd_file = "mechanical/3.5inch_HDD_NAS.step"
output_step = "mechanical/assembly.step"
output_fcstd = "mechanical/assembly.FCStd"

doc = FreeCAD.newDocument("GranitAssembly")


def import_step(filepath):
    before = set(obj.Name for obj in doc.Objects)
    Import.insert(filepath, doc.Name)
    return [obj for obj in doc.Objects
            if obj.Name not in before and hasattr(obj, "Shape") and obj.Shape.Solids]


def move_objects(objs, placement):
    for obj in objs:
        obj.Placement = placement


# === Case: keep at native position ===
case_parts = import_step(case_file)
for p in case_parts:
    p.Label = "Case_" + p.Label

# === PCB ===
# KiCad exports PCB in XY plane, origin at (20,20), board 71x101
# Need to rotate into case orientation:
#   PCB X (0..71 length) → case Z
#   PCB Y (0..101 width) → case X
#   PCB Z (thickness) → case Y (up)
# Then position inside case
pcb_parts = import_step(pcb_file)
pcb_rot = FreeCAD.Rotation(FreeCAD.Vector(1, 0, 0), -90)  # tilt PCB up (Y→Z)
pcb_rot2 = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), -90)  # rotate in plane
pcb_placement = FreeCAD.Placement(
    FreeCAD.Vector(
        50.5,                          # center PCB in case width (shift from KiCad Y)
        belly_y + standoff_height,     # on standoffs above belly
        pcb_z_start + 20               # compensate KiCad origin offset (board starts at 20)
    ),
    pcb_rot
)
move_objects(pcb_parts, pcb_placement)
for p in pcb_parts:
    p.Label = "PCB_" + p.Label

# === HDD ===
# HDD model: X=length(147), Y=width(101.6), Z=height(26.1), origin at corner
# Need: X(length)→Z(case), Y(width)→X(case), Z(height)→Y(case)
hdd_parts = import_step(hdd_file)
hdd_rot = FreeCAD.Rotation(FreeCAD.Vector(1, 0, 0), -90)
hdd_placement = FreeCAD.Placement(
    FreeCAD.Vector(
        50.8,                          # center HDD in case width
        belly_y,                       # flat on belly plate
        hdd_z_start                    # after PCB + gap
    ),
    hdd_rot
)
move_objects(hdd_parts, hdd_placement)
for p in hdd_parts:
    p.Label = "HDD_" + p.Label

# === Save ===
doc.recompute()
shapes = [obj for obj in doc.Objects if hasattr(obj, "Shape") and obj.Shape.Solids]
Part.export(shapes, output_step)
doc.saveAs(output_fcstd)

print(f"Assembly saved: {len(shapes)} solid parts")
