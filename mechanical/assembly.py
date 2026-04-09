#!/usr/bin/env python3
"""Granit mechanical assembly — FreeCAD script.

Run with: freecadcmd mechanical/assembly.py

Case: X=width(centered), Y=height(belly=-51.5,lid=0), Z=length(-110..110)
Rotation for PCB and HDD: 90°Z then -90°X → X=width, Y=height, Z=length
"""

import FreeCAD
import Part
import Import

standoff = 5.0
gap = 2.0
belly_y = -51.5

case_file = "hardware/3d-models/1455T2201.stp"
pcb_file = "mechanical/granit-pcb.step"
hdd_file = "mechanical/3.5inch_HDD_NAS.step"
output_step = "mechanical/assembly.step"

doc = FreeCAD.newDocument("GranitAssembly")

# Common rotation: 90°Z then -90°X maps (length,width,height) → (width,height,length)
r1 = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), 90)
r2 = FreeCAD.Rotation(FreeCAD.Vector(1, 0, 0), -90)
rot = r2.multiply(r1)


def import_step(filepath, label_prefix):
    before = set(obj.Name for obj in doc.Objects)
    Import.insert(filepath, doc.Name)
    parts = []
    for obj in doc.Objects:
        if obj.Name not in before and hasattr(obj, "Shape") and obj.Shape.Solids:
            obj.Label = label_prefix + "_" + obj.Label
            parts.append(obj)
    return parts


# === Case at origin (skip lid for visibility) ===
case_parts = import_step(case_file, "Case")
# Remove the top extrusion cap to see inside
for p in list(case_parts):
    if "Cap" in p.Label:
        doc.removeObject(p.Name)
        case_parts.remove(p)

# === PCB ===
# After rotation: X=20..121(101), Y=0..1.5, Z=-91..-20(71)
# Translate to: X centered at 0, Y at belly+standoff, Z starting at -110
# X shift: -(20+121)/2 = -70.5
# Y shift: belly+standoff = -51.5+5 = -46.5
# Z shift: -110-(-91) = -19
pcb_parts = import_step(pcb_file, "PCB")
pcb_pos = FreeCAD.Vector(-70.5, belly_y + standoff, -19)
for p in pcb_parts:
    p.Placement = FreeCAD.Placement(pcb_pos, rot)

# PCB now at: X=-50.5..50.5, Y=-46.5..-45, Z=-110..-39

# === HDD ===
# After rotation: X=-101.6..0, Y=0..26.1, Z=-147..0
# SATA connector is at Z=-147 end (was X=147, the far end)
# We want SATA end facing PCB (at Z=-39), so HDD goes from Z=-39 toward Z=+110
# But Z=-147..0 after rotation means SATA is at Z=-147
# We need to flip: SATA at high Z, body toward +110
# Actually: HDD origin corner (X=0,Y=0,Z=0 native = no SATA) maps to Z=0 after rot
# SATA end (X=147 native) maps to Z=-147 after rot
# So translate Z so that Z=-147 aligns with Z=-39 (PCB SATA edge)
# Z shift: -39 - (-147) = 108
# X shift: center 101.6 at 0: -(-101.6)/2 = 50.8... X goes -101.6..0, center at -50.8
# shift = 0 - (-50.8) = 50.8
# Y shift: belly+standoff, but Y goes 0..26.1, need bottom at belly+standoff
# shift = belly+standoff - 0 = -46.5
hdd_parts = import_step(hdd_file, "HDD")
hdd_pos = FreeCAD.Vector(50.8, belly_y + standoff, 108)
for p in hdd_parts:
    p.Placement = FreeCAD.Placement(hdd_pos, rot)

# HDD now at: X=-50.8..50.8, Y=-46.5..-20.4, Z=-39..108

# === Save ===
doc.recompute()
shapes = [obj for obj in doc.Objects if hasattr(obj, "Shape") and obj.Shape.Solids]
Part.export(shapes, output_step)
print(f"Assembly STEP saved: {len(shapes)} solid parts")
