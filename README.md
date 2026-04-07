# Granit — Offsite Backup Device

Custom carrier board for the Raspberry Pi CM4/CM5 Compute Module, designed as a minimal offsite backup appliance.

## Concept

A compact, headless device that connects to a remote network and receives encrypted backups onto an attached hard disk.
Designed to be left at a trusted offsite location (friend's house, office, etc.) and managed remotely.

This PCB is designed with [KiCad 10](https://www.kicad.org/blog/2026/03/Version-10.0.0-Released/)

## Hardware

### Core Components

| Component | Description |
|---|---|
| Raspberry Pi CM4 or CM5 | Compute module (both have PCIe Gen 2 x1) |
| ASM1061 | PCIe Gen 2 x1 to 2-port SATA III controller (no firmware blob required) |
| 2.5" or 3.5" SATA HDD/SSD | Backup storage |
| 22-pin SATA connector | Combined data (7-pin) + power (15-pin) |
| RJ45 + Ethernet magnetics | Gigabit Ethernet |
| DS3231 RTC | Battery-backed real-time clock with alarm wake (I2C) |
| CR2032 coin cell | RTC backup battery |
| Hirose DF40C-100DS-0.4V(51) | 2x CM4/CM5 board-to-board connectors |
| AP64501SP-13 | 3.5A DC-DC buck converter (reused from [pedalboard-hw](https://github.com/pedalboard/pedalboard-hw)) |

### Block Diagram

```
                  ┌──────────────────────────────┐
  12V DC In ─────►│  Power Supply                │
  (barrel jack)   │  12V passthrough → SATA 12V  │
                  │  AP64501SP-13 → 5V → SATA 5V │
                  │  NCP1117 → 3.3V              │
                  └──────────┬───────────────────┘
                             │ 5V / 3.3V
  ┌───────────┐   ┌──────────▼───────────────────┐
  │ DS3231 RTC├──►│  Raspberry Pi CM4/CM5        │
  │ (CR2032)  │I2C│  (2x 100-pin connectors)     │
  │  alarm────┼──►│  GLOBAL_EN (wake)            │
  └───────────┘   └──────────┬───────────────────┘
                             │ PCIe Gen 2 x1
                  ┌──────────▼───────────────────┐
                  │  ASM1061 PCIe-to-SATA        │
                  │  (QFN-64, native AHCI)       │
                  └──────────┬───────────────────┘
                             │ SATA (data + power)
                  ┌──────────▼───────────────────┐
                  │  2.5" or 3.5" HDD/SSD        │
                  │  (native SMART via AHCI)     │
                  └──────────────────────────────┘
```

### Key Design Decisions

- **ASM1061 over USB-to-SATA bridges**: Native PCIe SATA controller using the standard Linux
  `ahci` driver. No proprietary firmware blob required — the SPI flash footprint can be left
  unpopulated. SMART works natively (`smartctl /dev/sda`) without SAT translation hacks.
  Both CM4 and CM5 have PCIe Gen 2 x1, so full SATA III throughput is available on either
  module — unlike USB-to-SATA, which would be bottlenecked by CM4's USB 2.0 (~35 MB/s).
- **12V DC input**: Required for 3.5" HDD support (spindle motor needs 12V).
  12V is passed through directly to the SATA power connector.
  AP64501SP-13 accepts 3.8–28V input, so 12V is well within range.
- **Reuse from pedalboard-hw**: CM connector, power supply (AP64501SP-13 buck + NCP1117 LDO),
  USB power switch (AP2553W6), KiCad symbol/footprint library, CI pipeline.

### Design Considerations

- **PCIe routing**: 100Ω differential impedance for PCIe Gen 2 lanes, matched length,
  minimize vias and stubs. 4-layer PCB recommended (signal/GND/power/signal).
- **Ethernet**: CM4/CM5 has built-in Ethernet PHY — route differential pairs to RJ45 with magnetics
- **SATA power**: 12V passthrough for 3.5" HDD, 5V from buck converter, 3.3V from LDO
- **Power budget**: 12V @ 2A (3.5" HDD spin-up) + 5V @ 2A (CM5 + electronics) — use a 12V/3A+ PSU

## PCB Design

### Project Structure

```
hardware/
├── granit.kicad_pro       # KiCad 10 project
├── granit.kicad_sch       # Top-level schematic
├── psu.kicad_sch                  # Power supply (from pedalboard-hw)
├── cm.kicad_sch                   # CM4/CM5 connector + Ethernet
├── sata.kicad_sch                 # ASM1061 PCIe-to-SATA bridge
├── granit.kicad_pcb       # PCB layout
├── Library.pretty/                # Custom footprints
├── granit.kicad_sym       # Custom symbols
├── 3d-models/                     # 3D models for components
└── fabrication/                   # Gerber output
```

## Software

The device runs Raspberry Pi OS Lite (headless).

### Planned Stack

- Restic backup repository (encryption built-in)
- rsync to receive backups from NAS
- `smartmontools` for disk health monitoring (`smartctl /dev/sda`)
- WireGuard VPN for remote management
- RTC-based scheduled wake: DS3231 alarm → `GLOBAL_EN` → CM boots → backup runs → shutdown
- LUKS full-disk encryption on the backup drive
- Automatic drive mount and health monitoring

## Enclosure

Metal enclosure designed for a plug-and-forget deployment. The device should be installable
by a non-technical person: plug in Ethernet, plug in power, done.

### Requirements

- Aluminum or steel enclosure (shielding, durability, passive heatsinking)
- Internal mounting for 2.5" or 3.5" HDD
- Cutouts: barrel jack (12V), RJ45 (Ethernet)
- No user-facing controls or displays needed
- Compact form factor suitable for a shelf or behind a router
- 3D-printable or off-the-shelf enclosure (e.g. Hammond 1455 series)

## Generated Hardware Documentation

Interactive [KiCanvas](https://kicanvas.org/) viewer (link TBD after first CI run).

Downloadable assets are generated with [KiBot](https://github.com/INTI-CMNB/KiBot).

> **Note**: KiBot CI currently uses `ghcr.io/inti-cmnb/kicad9_auto`. A `kicad10_auto` image
> is expected soon. KiCad 10 files are forward-compatible for most KiBot operations.

## License

[CERN Open Hardware Licence Version 2 - Permissive](https://ohwr.org/cern_ohl_p_v2.txt)
