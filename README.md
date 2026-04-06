# Offsite Backup Device

Custom carrier board for the Raspberry Pi CM4/CM5 Compute Module, designed as a minimal offsite backup appliance.

## Concept

A compact, headless device that connects to a remote network and receives encrypted backups onto an attached hard disk.
Designed to be left at a trusted offsite location (friend's house, office, etc.) and managed remotely.

This PCB is designed with [KiCad 10](https://www.kicad.org/blog/2026/03/Version-10.0.0-Released/)

## Hardware

### Core Components

| Component | Description |
|---|---|
| Raspberry Pi CM4 or CM5 | Compute module (CM5 preferred for native USB 3.0) |
| JMS578 | USB 3.0 to SATA 6Gbps bridge with SMART passthrough |
| 2.5" or 3.5" SATA HDD/SSD | Backup storage |
| 22-pin SATA connector | Combined data (7-pin) + power (15-pin) |
| RJ45 + Ethernet magnetics | Gigabit Ethernet |
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
                  ┌──────────▼───────────────────┐
  RJ45 ─────────►│  Raspberry Pi CM4/CM5        │
  (GbE)           │  (2x 100-pin connectors)     │
                  └──────────┬───────────────────┘
                             │ USB 3.0
                  ┌──────────▼───────────────────┐
                  │  JMS578 USB-to-SATA bridge   │
                  │  + 25MHz XTAL                │
                  │  + SPI Flash (firmware)       │
                  └──────────┬───────────────────┘
                             │ SATA (data + power)
                  ┌──────────▼───────────────────┐
                  │  2.5" or 3.5" HDD/SSD        │
                  │  (SMART monitoring via SAT)   │
                  └──────────────────────────────┘
```

### Key Design Decisions

- **12V DC input**: Required for 3.5" HDD support (spindle motor needs 12V).
  12V is passed through directly to the SATA power connector.
  AP64501SP-13 accepts 3.8–28V input, so 12V is well within range.
- **JMS578 over ASM1153E**: JMS578 provides reliable SMART passthrough via SAT (SCSI/ATA Translation),
  which is crucial for monitoring backup disk health with `smartctl -d sat`.
- **CM5 preferred**: Native USB 3.0 on the SoC, no PCIe bridge needed.
- **Reuse from pedalboard-hw**: CM connector, power supply (AP64501SP-13 buck + NCP1117 LDO),
  USB power switch (AP2553W6), KiCad symbol/footprint library, CI pipeline.

### Design Considerations

- **USB 3.0 routing**: 90Ω differential impedance for SuperSpeed pairs, matched length
- **Ethernet**: CM4/CM5 has built-in Ethernet PHY — route differential pairs to RJ45 with magnetics
- **SATA power**: 12V passthrough for 3.5" HDD, 5V from buck converter, 3.3V from LDO
- **Power budget**: 12V @ 2A (3.5" HDD spin-up) + 5V @ 2A (CM5 + electronics) — use a 12V/3A+ PSU
- **JMS578 firmware**: One-time SPI flash during production (tools: `jms578fwupdate`)

## PCB Design

### Project Structure

```
hardware/
├── offsite-backup.kicad_pro       # KiCad 10 project
├── offsite-backup.kicad_sch       # Top-level schematic
├── psu.kicad_sch                  # Power supply (from pedalboard-hw)
├── cm.kicad_sch                   # CM4/CM5 connector + Ethernet
├── sata.kicad_sch                 # JMS578 USB-to-SATA bridge
├── offsite-backup.kicad_pcb       # PCB layout
├── Library.pretty/                # Custom footprints
├── offsite-backup.kicad_sym       # Custom symbols
├── 3d-models/                     # 3D models for components
└── fabrication/                   # Gerber output
```

## Software

The device runs Raspberry Pi OS Lite (headless).

### Planned Stack

- LUKS full-disk encryption on the backup drive
- `smartmontools` for disk health monitoring (`smartctl -d sat`)
- Backup receiver (rsync/restic/borg — TBD)
- WireGuard VPN for remote management
- Automatic drive mount and health monitoring

## Generated Hardware Documentation

Interactive [KiCanvas](https://kicanvas.org/) viewer (link TBD after first CI run).

Downloadable assets are generated with [KiBot](https://github.com/INTI-CMNB/KiBot).

> **Note**: KiBot CI currently uses `ghcr.io/inti-cmnb/kicad9_auto`. A `kicad10_auto` image
> is expected soon. KiCad 10 files are forward-compatible for most KiBot operations.

## License

[CERN Open Hardware Licence Version 2 - Permissive](https://ohwr.org/cern_ohl_p_v2.txt)
