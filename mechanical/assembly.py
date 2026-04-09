#!/usr/bin/env python3
"""Granit mechanical assembly — FreeCAD script.

Run with: freecadcmd mechanical/assembly.py

Hammond 1455T2201 STEP orientation:
  X = width (160mm extrusion), centered at 0
  Y = height (51.5mm), belly at -51.5, lid at 0
  Z = length (220mm), centered: -110 to 110

PCB (KiCad): X=20..91(71), Y=-121..-20(101), Z=0..1.5
HDD: X=0..147, Y=0..101.6, Z=0..26.1
"""

import FreeCAD
import Part
import Import
import math

standoff = 5.0
gap = 2.0
belly_y = -51.5

case_file = "hardware/3d-models/1455T2201.stp"
pcb_file = "mechanical/granit-pcb.step"
hdd_file = "mechanical/3.5inch_HDD_NAS.step"
output_step = "mechanical/assembly.step"

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


def place(parts, x, y, z, ax=0, ay=0, az=0):
    """Place parts with position and Euler angles (degrees)."""
    rot = FreeCAD.Rotation(az, ay, ax)  # FreeCAD Rotation(yaw, pitch, roll)
    pl = FreeCAD.Placement(FreeCAD.Vector(x, y, z), rot)
    for p in parts:
        p.Placement = pl


# === Case at origin ===
import_step(case_file, "Case")

# === PCB ===
# Native: X=20..91, Y=-121..-20, Z=0..1.5 (flat in XY, KiCad has -Y)
# Target: flat in XZ plane (length along Z, width along X)
# Rotation: 90° around X axis flips Y→-Z, Z→Y
# After rot: X=20..91, Y=0..1.5, Z=20..121
# Then translate to position inside case
pcb_parts = import_step(pcb_file, "PCB")
place(pcb_parts,
    x=0,
    y=belly_y + standoff,
    z=-110,
    ax=90, ay=0, az=0  # 90° around X
)
# Adjust: after rotation PCB X is 20..91, need to center in case (X=0)
# PCB center X = (20+91)/2 = 55.5, shift by -55.5
# PCB Z after rot+translate: need to start at -110
# After 90° around X: original Y(-121..-20) maps to Z(20..121)
# So Z = 20..121, need shift of -110-20 = -130
for p in pcb_parts:
    p.Placement.Base = FreeCAD.Vector(-55.5, belly_y + standoff, -130)

# === HDD ===
# Native: X=0..147(length), Y=0..101.6(width), Z=0..26.1(height)
# Target: length along Z, width along X, height along -Y (hanging from belly+standoff)
# Rotation: 90° around X (Z→-Y, Y→Z), then -90° around new Z (X→Z)
# Simpler: use Euler angles
# yaw=-90 (rotate in XZ plane: X→-Z), pitch=0, roll=90 (tilt: Z→-Y)
hdd_parts = import_step(hdd_file, "HDD")

# After yaw=-90: X→-Z(0..-147), Y→Y(0..101.6), Z→X(0..26.1)
# After roll=90: Y→-Z, Z→Y ... getting complicated
# Let me just use rotation vectors
# Want: X→Z, Y→X, Z→-Y
# That's: rotate -90° around Y (X→Z, Z→-X), then -90° around Z (Y→-X→... no)
# 
# Direct approach: Rotation from axes
# New X = old Y direction = (0,1,0)
# New Y = old -Z direction = (0,0,-1)  
# New Z = old X direction = (1,0,0)
rot = FreeCAD.Rotation(
    FreeCAD.Vector(0, 1, 0),   # new X = old Y
    FreeCAD.Vector(0, 0, -1),  # new Y = old -Z
    FreeCAD.Vector(1, 0, 0),   # new Z = old X
    "ZXY"
)

# PCB ends at Z = -130 + 121 = about -9... let me recalculate
# PCB after placement: Z range needs checking
# PCB connector edge at Z=-110, SATA edge at Z=-110+71=-39
# HDD starts at Z = -39 + gap = -37
# HDD length 147 along Z: -37 to -37+147 = 110 ✓ (fits exactly!)

hdd_z_start = -110 + 71 + gap  # -37

# Position: centered in X, on standoffs in Y, starting at hdd_z_start in Z
# After rotation: HDD_Y(101.6)→X, center at 0: shift X by -101.6/2 = -50.8
# HDD_Z(26.1)→-Y: top at belly+standoff, so Y = belly+standoff
# HDD_X(147)→Z: starts at hdd_z_start
place(hdd_parts,
    x=-50.8,
    y=belly_y + standoff,
    z=hdd_z_start,
    ax=0, ay=0, az=0
)
# Apply the custom rotation
for p in hdd_parts:
    # Manual rotation matrix approach: just use two sequential rotations
    # -90° around Y: (x,y,z) → (z,y,-x) so X→Z, Z→-X
    r1 = FreeCAD.Rotation(FreeCAD.Vector(0, 1, 0), -90)
    # -90° around X: (x,y,z) → (x,-z,y) so Y→Z, Z→-Y  
    r2 = FreeCAD.Rotation(FreeCAD.Vector(1, 0, 0), -90)
    combined = r2.multiply(r1)
    p.Placement = FreeCAD.Placement(
        FreeCAD.Vector(-50.8, belly_y + standoff, hdd_z_start),
        combined
    )

# === Save ===
doc.recompute()
shapes = [obj for obj in doc.Objects if hasattr(obj, "Shape") and obj.Shape.Solids]
Part.export(shapes, output_step)

print(f"Assembly STEP saved: {len(shapes)} solid parts")
