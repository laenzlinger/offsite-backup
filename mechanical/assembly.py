#!/usr/bin/env python3
"""Granit mechanical assembly — FreeCAD script.

Generates two assembly variants:
  - Slim: 1455L2201 + 2.5" HDD
  - Wide: 1455T2601 + 3.5" HDD

Run with: freecadcmd mechanical/assembly.py

Case coordinate system (from STEP models):
  X = width (centered at 0), Y = height (belly negative, lid ~0), Z = length (centered)

PCB native: X=20..112 (92mm), Y=-120..-20 (100mm), Z=0..1.5
PCB rotation: -90° around X → X=92(width), Y=1.5(thickness), Z=100(length)
  After rot: X=20..112, Y=0..1.5, Z=20..120
  SATA edge at native X=112 → stays at X=112

HDD native: X=0..L (length), Y=0..W (width), Z=0..H (height)
HDD rotation: 90°Z then -90°X → X=W(width), Y=H(height), Z=L(length)
  After rot: X=-W..0, Y=0..H, Z=-L..0
  SATA at Z=0 (native X=0)
"""

import sys
import FreeCAD
import Part
import Import

# PCB rotation: just -90° around X
pcb_rot = FreeCAD.Rotation(FreeCAD.Vector(1, 0, 0), -90)
# PCB after rot (no shift): X=20..112, Y=0..1.5, Z=20..120
# SATA edge at X=112 side — but SATA is along the short edge (X axis)
# The SATA connector faces +Z direction (the Z=120 end, native Y=-20)
# Actually: native Y=-20 maps to Z=20, native Y=-120 maps to Z=120
# The SATA connector is at the PCB edge where the connector footprint is placed
# In KiCad the SATA connector is at the bottom of the board (high Y magnitude = Y=-120 → Z=120)

# HDD rotation: 90°Z then -90°X
r1 = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), 90)
r2 = FreeCAD.Rotation(FreeCAD.Vector(1, 0, 0), -90)
hdd_rot = r2.multiply(r1)
# HDD after rot (no shift): X=-W..0, Y=0..H, Z=-L..0, SATA at Z=0

STANDOFF = 5.0
GAP = 2.0

VARIANTS = {
    "slim": {
        "case_file": "hardware/3d-models/1455L2201.stp",
        "hdd_file": "mechanical/2.5inch_HDD.step",
        "hdd_dims": (100.2, 69.85, 9.5),  # length, width, height
        "case_belly_y": -32.5,
        "hdd_flip": True,  # SATA at native X=L
        "output": "mechanical/assembly-slim.step",
    },
    "wide": {
        "case_file": "hardware/3d-models/1455T2601.stp",
        "hdd_file": "mechanical/3.5inch_HDD_NAS.step",
        "hdd_dims": (147.0, 101.6, 26.1),
        "case_belly_y": -53.6,
        "hdd_flip": True,  # SATA at native X=147 instead of X=0
        "output": "mechanical/assembly-wide.step",
    },
}

PCB_FILE = "mechanical/granit-pcb.step"


def import_step(doc, filepath, label_prefix):
    before = set(obj.Name for obj in doc.Objects)
    Import.insert(filepath, doc.Name)
    parts = []
    for obj in doc.Objects:
        if obj.Name not in before and hasattr(obj, "Shape") and obj.Shape.Solids:
            obj.Label = label_prefix + "_" + obj.Label
            parts.append(obj)
    return parts


def build_variant(name, cfg):
    doc = FreeCAD.newDocument(f"Granit_{name}")

    belly_y = cfg["case_belly_y"]
    hdd_length, hdd_width, hdd_height = cfg["hdd_dims"]

    # === Case (centered at origin) ===
    case_parts = import_step(doc, cfg["case_file"], "Case")

    # === Layout along Z axis ===
    # [HDD far end ... HDD SATA] [GAP] [PCB SATA ... PCB far end]
    #  ←  -Z                                              +Z  →
    pcb_len = 100.0  # PCB length along Z after rotation
    total_z = hdd_length + GAP + pcb_len
    hdd_z_far = -total_z / 2
    hdd_z_sata = hdd_z_far + hdd_length
    pcb_z_sata = hdd_z_sata + GAP
    pcb_z_far = pcb_z_sata + pcb_len

    # === PCB ===
    pcb_parts = import_step(doc, PCB_FILE, "PCB")
    # After rot (no shift): X=20..112, Y=0..1.5, Z=20..120
    # SATA connector is at Z=20 (native Y=-20, near board top in KiCad)
    # Non-SATA edge at Z=120 (native Y=-120, board bottom in KiCad)
    # We want SATA at pcb_z_sata (facing HDD toward -Z)
    pcb_z_shift = pcb_z_sata - 20.0
    # Center X: X=20..112, center=66, shift = -66
    pcb_x_shift = -66.0
    # Y: bottom at belly + standoff
    pcb_y_shift = belly_y + STANDOFF

    for p in pcb_parts:
        p.Placement = FreeCAD.Placement(
            FreeCAD.Vector(pcb_x_shift, pcb_y_shift, pcb_z_shift), pcb_rot)

    # === HDD ===
    hdd_parts = import_step(doc, cfg["hdd_file"], "HDD")

    if cfg.get("hdd_flip"):
        # SATA at native X=L: flip 180° around Z (preserves Y orientation)
        r_flip = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), 180)
        this_hdd_rot = hdd_rot.multiply(r_flip)
        # After rot+flip: X=0..W, Y=0..H, Z=0..L, SATA at Z=L
        hdd_z_shift = hdd_z_sata - hdd_length
        hdd_x_shift = -hdd_width / 2
        hdd_y_shift = belly_y + STANDOFF
    else:
        # SATA at native X=0: after rot Z=0
        this_hdd_rot = hdd_rot
        # After rot: X=-W..0, Y=0..H, Z=-L..0, SATA at Z=0
        hdd_z_shift = hdd_z_sata
        hdd_x_shift = hdd_width / 2
        hdd_y_shift = belly_y + STANDOFF

    for p in hdd_parts:
        p.Placement = FreeCAD.Placement(
            FreeCAD.Vector(hdd_x_shift, hdd_y_shift, hdd_z_shift), this_hdd_rot)

    # === Save ===
    doc.recompute()
    shapes = [obj for obj in doc.Objects if hasattr(obj, "Shape") and obj.Shape.Solids]
    Part.export(shapes, cfg["output"])
    sys.stdout.write(f"{name}: saved {cfg['output']} ({len(shapes)} solids)\n")
    sys.stdout.write(f"  PCB  X:{-66+20:.1f}..{-66+112:.1f}  Z:{pcb_z_sata:.1f}..{pcb_z_sata+pcb_len:.1f}\n")
    sys.stdout.write(f"  HDD  X:{-hdd_width/2:.1f}..{hdd_width/2:.1f}  Z:{hdd_z_far:.1f}..{hdd_z_sata:.1f}\n")
    sys.stdout.flush()
    FreeCAD.closeDocument(doc.Name)


for name, cfg in VARIANTS.items():
    build_variant(name, cfg)
