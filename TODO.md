# Granit — TODO

## Schematic ✅

### Done
- [x] PSU: AP64501SP-13 buck + NCP1117 LDO + FDS4435BZ reverse polarity + 3A SMD fuse
- [x] CM4 Connector 1: power, GND, NC flags, global labels, Ethernet, GLOBAL_EN
- [x] CM4 Connector 2: power, GND, NC flags, global labels, USB, PCIe
- [x] Peripherals: SK6812MINI-E NeoPixel + 74AHCT1G32 level shifter
- [x] Peripherals: status LEDs (nLED_PWR, nLED_ACT, DNP)
- [x] Peripherals: tactile button (GPIO17) + pull-up
- [x] Peripherals: nRPIBOOT 2-pin header
- [x] Peripherals: UART debug 3-pin header
- [x] Peripherals: DS3231MZ RTC + CR2032 battery
- [x] Peripherals: USB-C OTG + USBLC6-2SC6 ESD protection + solder jumper
- [x] Ethernet: RB1-125B8G1A Gigabit MagJack + LEDs
- [x] SATA: ASM1061 PCIe-to-SATA bridge + 25MHz crystal
- [x] SATA: 7-pin data connector + 4-pin power connector
- [x] SATA: power switching (FDS4435BZ on 5V/12V, GPIO5 controlled, solder jumper bypass)
- [x] Wake: hardware power-off wake (2N7002 + 74AHCT1G32 OR gate, DNP for v1)
- [x] All footprints assigned
- [x] All component descriptions filled
- [x] Resistor values consolidated (9 unique)
- [x] All decoupling caps verified
- [x] ERC: 0 errors, 0 warnings
- [x] ERC enabled in CI

## PCB Layout

Side-by-side layout inside Hammond 1455L2201 (220mm length):
- HDD occupies 147mm, PCB sits in the remaining space
- SATA connector on PCB edge mates directly with HDD
- External connectors (RJ45, USB-C, barrel jack, button) on opposite end panel

Max PCB size: **71 × 101mm** (220 - 147 - 2mm gap = 71mm length, 103mm internal width - ~2mm wall clearance)

Both PCB and HDD mount to the belly plate (slide-out for servicing).

### Component floorplan

```
                    SATA edge (faces HDD)
    ┌─────────────────────────────────────────┐
    │                                         │
    │   ASM1061        SATA connector         │
    │   (7×7mm)        (42mm wide, edge)      │
    │      ↕ short SATA diff pairs            │
    │                                         │
    │   ────── PCIe diff pairs (~20mm) ────── │
    │                                         │
    │          CM4 module (55×40mm)            │
    │          (center of board)              │
    │                                         │
    │   ↕ short ETH     ↕ USB        PSU     │
    │   diff pairs       diff        area    │
    │                                         │
    │  RJ45  USB-C  Barrel  BTN  LED  CR2032 │
    │                                         │
    └─────────────────────────────────────────┘
                 Connector edge (end plate)
```

Placement rationale:
- ASM1061 near SATA edge → shortest SATA differential pairs
- CM4 center → PCIe north to ASM1061, Ethernet south to RJ45
- RJ45 + USB-C on connector edge → short diff pairs from CM4
- PSU in corner → switching noise away from high-speed signals
- DS3231 + CR2032 → quiet area near CM4 I2C pins
- Button + LED → connector edge, accessible through end plate

### Pre-routing: stackup and impedance

Before starting any routing, confirm fab house stackup and update KiCad net classes.

- [ ] Choose fab house (PCBWay or JLCPCB) and get exact 4-layer stackup
- [ ] Calculate trace geometry using fab stackup (or request impedance control):
  - 100Ω differential (PCIe, SATA, Ethernet): ~0.13mm trace, ~0.15mm gap (JLCPCB standard)
  - 90Ω differential (USB): ~0.16mm trace, ~0.15mm gap
  - 50Ω single-ended (clock, reset): ~0.22mm trace
- [ ] Update KiCad net classes with calculated values:
  - PCIe: diff_pair_width, diff_pair_gap
  - SATA: diff_pair_width, diff_pair_gap
  - Ethernet: diff_pair_width, diff_pair_gap
  - USB: diff_pair_width, diff_pair_gap
- [ ] Verify fab minimum capabilities (min trace/space, min drill, min annular ring)
- [ ] Decide PCB thickness (1.6mm standard or 1.0mm for SATA alignment)

### Checklist
PCB standoff height must match HDD SATA connector vertical position (~3.5mm above belly plate).

- [ ] Board outline: 71 × 101mm
- [ ] Verify PCB standoff height aligns SATA connector with HDD receptacle
- [ ] 4-layer stackup (signal/GND/power/signal)
- [ ] SATA connector on HDD-facing edge (`Connector_SATA:SATA_7-15_Plug_Vertical`, Molex 87779-1001)
  - Verify "L" key orientation matches male plug — may need to flip to bottom layer
- [ ] External connectors (RJ45, USB-C, barrel jack, button, LED) on opposite edge
- [ ] Place CM4 module and all components on top side (facing lid, for thermal contact)
- [ ] SATA connector vertical alignment: HDD connector center is 3.50mm above mounting surface (SFF-8301)
  - 1.6mm PCB + 2.7mm standoff = 3.5mm ✓ (non-standard standoff)
  - 1.0mm PCB + 3.0mm standoff = 3.5mm ✓ (standard standoff, thinner PCB)
  - 1.6mm PCB + 3.0mm standoff = 3.8mm (0.3mm off, likely within tolerance)
- [ ] CR2032 holder on top side (fallback: CR1220 on bottom side if space is tight — fits under 3mm standoffs, ~4.5 years DS3231 backup)
- [ ] Place ASM1061 near SATA connector (short differential pairs)
- [ ] HDD mounting holes: M4 (4.3mm drill, `MountingHole:MountingHole_4.3mm_M4_Pad_Via`)
- [ ] PCB standoff holes: M3 (3.2mm drill, `MountingHole:MountingHole_3.2mm_M3_Pad_Via`)
- [ ] Mounting hole keepout: 7.0mm clearance on pads (prevent screw heads shorting 12V traces)
- [ ] Route PCIe differential pairs (100Ω impedance)
- [ ] Route SATA differential pairs
- [ ] Route Ethernet differential pairs
- [ ] Route USB differential pairs
- [ ] Power trace width: ≥1.0mm (40 mil) for short branches to pads
- [ ] Power planes on L3: split into 5V and 3.3V zones
- [ ] 12V: copper pour on L4 from barrel jack to SATA power (2A+ spin-up)
- [ ] GND: solid plane on L2, stitching vias throughout
- [ ] DRC clean

## Enclosure
- [ ] Choose case: Hammond 1455L2201 (slim, 30.5mm) or 1455N2201 (roomy, 53mm)
  - Both share 103mm width — PCB is cross-compatible
  - 1455L: zero clearance with 3.5" HDD — mount PCB + HDD to belly plate
  - 1455N: 20mm+ extra height — fits 40mm fan or tall CM4 heatsink
- [ ] CNC belly plate: drill M3 holes for PCB standoffs + M4 holes for HDD mounts
- [ ] CNC end plate: cutouts for RJ45, USB-C, barrel jack, button, LED
- [ ] Thermal pad from CM4 SoC to enclosure lid
- [ ] Include Hammond 1455L2201 as default 3D reference model in KiCad

## Future Improvements
- [ ] TPM/crypto chip (e.g. ATECC608) for secure LUKS key storage (I2C)
- [ ] Evaluate CM5 compatibility (power budget validation)

## CI/CD
- [x] KiBot artifact generation with KiCad 10
- [x] GitHub Pages deployment (https://laenzlinger.github.io/granit/)
- [x] ERC check in KiBot preflight
- [ ] Enable DRC check when PCB layout is complete
- [ ] Switch to kicad10_auto container when available

## Software
- [ ] Raspberry Pi OS Lite base image
- [ ] Device tree overlay for ASM1061
- [ ] DS3231 RTC driver + alarm configuration
- [ ] DS3231 OSF flag check on boot (warn if battery failed, report via healthcheck)
- [ ] GPIO_HOLD (GPIO6) assertion on boot
- [ ] SATA_PWR_EN (GPIO5) control
- [ ] NeoPixel status daemon
- [ ] Button handler (shutdown/backup/maintenance)
- [ ] WireGuard VPN configuration
- [ ] Restic backup automation
- [ ] LUKS encrypted backup partition
- [ ] Healthcheck dead man's switch
- [ ] SMART disk monitoring
- [ ] rtcwake integration for scheduled power-off/wake
