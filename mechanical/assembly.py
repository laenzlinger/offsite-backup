#!/usr/bin/env python3
"""Granit mechanical assembly — FreeCAD script.

Run with: freecadcmd mechanical/assembly.py
Produces: mechanical/assembly.step and mechanical/assembly.FCStd

Hammond 1455T2201 native orientation:
  X = width (165mm with bezels), extrusion 160mm, centered
  Y = height (51.5mm), belly=-51.5, lid=0
  Z = length (220mm), centered: -110 to 110

PCB (KiCad export):
  X = 20..91 (71mm), Y = -121..-20 (101mm), Z = 0..1.5

HDD:
  X = 0..147, Y = 0..101.6, Z = 0..26.1
"""

import FreeCAD
import Part
import Import

# === Layout parameters ===
standoff = 5.0  # mm, both PCB and HDD
gap = 2.0       # between PCB and HDD along case length (Z)

# Case interior reference points
belly_y = -51.5
case_z_min = -110  # one end
case_z_max = 110   # other end

# === File paths ===
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


# === Case: keep at origin ===
case_parts = import_step(case_file, "Case")

# === PCB ===
# KiCad PCB is in XY plane: X=20..91, Y=-121..-20, Z=0..1.5
# Target in case: length along Z, width along X, standing on Y
# Rotation: none needed if we map PCB_X→case_Z, PCB_Y→case_X
# Actually PCB is already flat — we need to keep it flat but reorient:
#   PCB X (length 71) → case Z (length axis)
#   PCB Y (width 101) → case X (width axis)
#   PCB Z (thickness) → case Y (height axis)
# This means rotate 90° around Z to swap X↔Y, but KiCad Y is negative...
# Simplest: just translate to correct position, PCB stays in XY plane
# but case Y is height. So we need PCB flat in XZ plane.
#
# Rotation: -90° around X axis (PCB XY plane → XZ plane, Z becomes Y)
pcb_parts = import_step(pcb_file, "PCB")
for p in pcb_parts:
    # Step 1: rotate -90° around X to lay flat in case (Y→Z, Z→-Y)
    rot = FreeCAD.Rotation(FreeCAD.Vector(1, 0, 0), 90)
    p.Placement = FreeCAD.Placement(FreeCAD.Vector(0, 0, 0), rot)

# Now PCB is: X=20..91, Y=-1.5..0, Z=-121..-20 (after rotation)
# Need to translate so:
#   PCB center X → case center X (0): shift by -(20+91)/2 = -55.5
#   PCB Y → belly + standoff: shift by belly_y + standoff - 0 = -46.5
#   PCB Z → near case_z_min end: shift so PCB starts near Z=-110
#     PCB Z is currently -121..-20, want it at -110..-39
#     shift = -110 - (-121) = 11
pcb_shift = FreeCAD.Vector(-55.5, belly_y + standoff, 11)
for p in pcb_parts:
    old = p.Placement
    p.Placement = FreeCAD.Placement(
        old.Base + pcb_shift,
        old.Rotation
    )

# === HDD ===
# HDD model: X=0..147, Y=0..101.6, Z=0..26.1
# Same rotation as PCB: -90° around X (lay flat, Z→height)
hdd_parts = import_step(hdd_file, "HDD")
for p in hdd_parts:
    rot = FreeCAD.Rotation(FreeCAD.Vector(1, 0, 0), 90)
    p.Placement = FreeCAD.Placement(FreeCAD.Vector(0, 0, 0), rot)

# After rotation: X=0..147, Y=-26.1..0, Z=0..101.6 → but actually Z flips
# HDD needs to be:
#   X centered in case width → shift X by -147/2 = -73.5... no, HDD length along case Z
# 
# Actually HDD X(length) should map to case Z(length), same as PCB
# So we also need 90° around Y to swap X→Z
# Let's do both rotations
for p in hdd_parts:
    # Rotate to align: X→Z (length along case), Y→X (width across case), Z→Y (height)
    rot1 = FreeCAD.Rotation(FreeCAD.Vector(1, 0, 0), 90)   # Z→-Y (height up)
    rot2 = FreeCAD.Rotation(FreeCAD.Vector(0, 1, 0), -90)   # X→Z (length along case)
    rot = rot1.multiply(rot2)
    p.Placement = FreeCAD.Placement(FreeCAD.Vector(0, 0, 0), rot)

# Position HDD: after PCB along Z axis, centered in X
# PCB occupies Z = -110 to about -39 (71mm from -110)
# HDD starts at PCB end + gap
hdd_z_start = -110 + 71 + gap  # = -37
# HDD is 147mm long along Z after rotation
# Center HDD width (101.6mm) in case X (centered at 0)
hdd_shift = FreeCAD.Vector(0, belly_y + standoff, hdd_z_start + 73.5)
for p in hdd_parts:
    old = p.Placement
    p.Placement = FreeCAD.Placement(
        old.Base + hdd_shift,
        old.Rotation
    )

# === Save ===
doc.recompute()
shapes = [obj for obj in doc.Objects if hasattr(obj, "Shape") and obj.Shape.Solids]
Part.export(shapes, output_step)
doc.saveAs(output_fcstd)

print(f"Assembly saved: {len(shapes)} solid parts")
