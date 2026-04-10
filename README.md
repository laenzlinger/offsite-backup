# Granit — Offsite Backup Device

Custom carrier board for the Raspberry Pi CM4 Compute Module, designed as a minimal offsite backup appliance.

## Concept

A compact, headless device that connects to a remote network and receives encrypted backups onto an attached hard disk.
Designed to be left at a trusted offsite location (friend's house, office, etc.) and managed remotely.

This PCB is designed with [KiCad 10](https://www.kicad.org/blog/2026/03/Version-10.0.0-Released/)

## Hardware

### Core Components

| Component | Description |
|---|---|
| Raspberry Pi CM4 | Compute module (PCIe Gen 2 x1). CM5 mechanically compatible but not validated for power budget |
| ASM1061 | PCIe Gen 2 x1 to 2-port SATA III controller (no firmware blob required) |
| 2.5" or 3.5" SATA HDD/SSD | Backup storage |
| Amphenol 10029364-001LF | 22-pin SATA connector (data 7-pin + power 15-pin), right-angle |
| RJ45 + Ethernet magnetics | Gigabit Ethernet |
| DS3231 RTC | Battery-backed real-time clock with alarm wake (I2C) |
| CR2032 coin cell | RTC backup battery |
| RGB LED | Status indicator (idle/backup/error/maintenance) |
| Tactile button | Manual shutdown, trigger backup, enter maintenance mode on boot |
| Hirose DF40C-100DS-0.4V(51) | 2x CM4 board-to-board connectors |
| AP64501SP-13 | 3.5A DC-DC buck converter (reused from [pedalboard-hw](https://github.com/pedalboard/pedalboard-hw)) |
| USB-C | USB 2.0 OTG connector with USBLC6-2SC6 ESD protection |
| 2N7002 + 74AHCT1G32 | Hardware wake circuit (RTC alarm → GLOBAL_EN) |

### Block Diagram

![Architecture Diagram](diagram/architecture.drawio.svg)

### Key Design Decisions

- **ASM1061 over USB-to-SATA bridges**: Native PCIe SATA controller using the standard Linux
  `ahci` driver. No proprietary firmware blob required — the SPI flash footprint can be left
  unpopulated. SMART works natively (`smartctl /dev/sda`) without SAT translation hacks.
  Both CM4 and CM5 have PCIe Gen 2 x1, so full SATA III throughput is available on either
  module — unlike USB-to-SATA, which would be bottlenecked by CM4's USB 2.0 (~35 MB/s).
- **12V DC input**: Required for 3.5" HDD support (spindle motor needs 12V).
  12V is passed through directly to the SATA power connector.
  AP64501SP-13 accepts 3.8–28V input, so 12V is well within range.
  Both barrel jack (Würth 6941xx301002) and screw terminal (Phoenix MKDS-1,5-2) footprints
  are provided — populate one at assembly time.
- **Reuse from pedalboard-hw**: CM connector, power supply (AP64501SP-13 buck + NCP1117 LDO),
  USB power switch (AP2553W6), KiCad symbol/footprint library, CI pipeline.
- **USB-C OTG**: Single USB-C connector for eMMC flashing (`rpiboot`) and USB mass storage
  gadget mode (initial backup seeding over USB). USB 2.0 device mode only, with USBLC6-2SC6
  ESD protection.

### Design Considerations

- **PCIe routing**: 100Ω differential impedance for PCIe Gen 2 lanes, matched length,
  minimize vias and stubs. 4-layer PCB recommended (signal/GND/power/signal).
- **Ethernet**: CM4 has built-in Ethernet PHY — route differential pairs to RJ45 with magnetics
- **SATA power**: 12V passthrough for 3.5" HDD, 5V from buck converter, 3.3V from LDO
- **Power budget**: 12V @ 2A (3.5" HDD spin-up) + 5V @ 2.3A peak (CM4 + electronics) — use a 12V/3A+ PSU
- **Boot and storage strategy**: Full OS on CM4 eMMC (no SD card slot), SATA HDD dedicated
  to LUKS-encrypted backup storage only. HDD can spin down when idle. No SD card — eMMC is
  more reliable for a deploy-and-forget device. Reflashing via `nRPIBOOT` + USB-C if needed.

### Power Routing & Netclasses

PCB is fabricated with JLCPCB standard 4-layer stackup (1oz / 35µm copper on all layers).
Track widths are sized per IPC-2221 for outer-layer traces with 20°C temperature rise.

| Netclass | Track Width | Via (pad/drill) | Capacity (1oz, 20°C rise) | Worst-case Load | Nets |
|---|---|---|---|---|---|
| Power 12V | 3.0mm | 1.6mm / 0.8mm | ~3.5A | ~2.5A | `+12V*`, `fused`, `unfused` |
| Power 5V | 2.5mm | 1.6mm / 0.8mm | ~3.2A | ~2.8A | `+5VP`, `VBUS`, `switch` |
| Power 3V3 | 1.0mm | 0.8mm / 0.4mm | ~1.5A | ~0.6A | `+3V3` |

**Routing guidelines:**
- Netclass widths are the default for main runs. Neck down to pad width over the last 1–2mm at component pads.
- Use copper pours for 12V and 5V in the PSU area where space allows.
- Use 2–3 parallel vias where power traces change layers.
- Place GND return vias near every power via.
- Keep 12V and 5V routing on top/bottom layers — do not break the inner GND planes.
- Do not route power traces under or parallel to PCIe/SATA/Ethernet differential pairs.

## Software

The device runs Raspberry Pi OS Lite (headless).

### Planned Stack

- Restic backup repository (encryption built-in)
- rsync to receive backups from NAS
- `smartmontools` for disk health monitoring (`smartctl /dev/sda`)
- WireGuard VPN for remote management
- RTC-based scheduled wake: DS3231 alarm → GPIO4 interrupt → CM wakes from suspend → backup runs → suspend
  (`GLOBAL_EN` tied high via pull-up, CM4 uses Linux `rtcwake` for suspend/resume.
  Hardware power-off wake via MOSFET latch on `GLOBAL_EN` planned for v2.)
- LUKS full-disk encryption on the backup drive
- Automatic drive mount and health monitoring

### Deployment

1. Initial backup on-site: connect Granit to local network, run full backup over LAN
2. Move device to offsite location (friend's house, office, etc.)
3. Plug in Ethernet + power — done
4. Subsequent backups are incremental and run automatically over WireGuard

### Monitoring & Alerting

Monitoring must live outside the Granit device — if the device fails, it can't alert about
its own failure. The device reports in after each backup run using a dead man's switch pattern:

- After each successful backup, Granit pings a healthcheck endpoint (e.g. self-hosted or healthchecks.io)
- If the expected ping doesn't arrive, an alert is triggered (email, push notification)
- Reported metrics: backup success/failure, SMART disk health, disk space remaining
- WireGuard connectivity is implicitly monitored — no tunnel means no ping

## Enclosure

Metal enclosure designed for a plug-and-forget deployment. The device should be installable
by a non-technical person: plug in Ethernet, plug in power, done.

### Hammond 1455 Series

Same PCB (92 × 100mm) fits both cases, held by a 3D printed internal frame.
PCB and HDD sit side-by-side along the enclosure length, SATA connector direct-mates between them.

| | 1455L2201 (Slim) | 1455T2601 (Wide) |
|---|---|---|
| Dimensions | 220 × 103 × 30.5 mm | 260 × 160 × 51.5 mm |
| Internal width | ~100 mm | ~157 mm |
| Internal height | ~27 mm | ~48 mm |
| HDD support | 2.5" only | 2.5" or 3.5" |
| Material | Extruded aluminium | Extruded aluminium |
| Colors | Natural, Black, Blue, Red | Natural, Black, Blue, Red |

![Slim Assembly — 1455L2201 + 2.5" HDD](mechanical/assembly-slim.png)
![Wide Assembly — 1455T2601 + 3.5" HDD](mechanical/assembly-wide.png)

### Requirements

- Cutouts: barrel jack or screw terminal (12V), RJ45 (Ethernet), USB-C
- Tactile button accessible from outside (recessed to prevent accidental press)
- RGB LED visible through enclosure (light pipe or translucent window)
- Thermal pad or heatsink contact for CM4 SoC to enclosure lid
- Internal mounting for 2.5" or 3.5" HDD (M4 mounting holes)
- PCB standoffs (M3 mounting holes)

## Generated Hardware Documentation

Browse the latest generated outputs at **[laenzlinger.github.io/granit](https://laenzlinger.github.io/granit/)**.

Includes schematic PDF, interactive BOM, HTML BOM, and PCB prints — auto-generated on every push with [KiBot](https://github.com/INTI-CMNB/KiBot) (dev branch) running inside the official [kicad/kicad:10.0](https://hub.docker.com/r/kicad/kicad) container.

## License

[CERN Open Hardware Licence Version 2 - Permissive](https://ohwr.org/cern_ohl_p_v2.txt)
