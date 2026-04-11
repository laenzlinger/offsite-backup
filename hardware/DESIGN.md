# Hardware Design Notes

Detailed design decisions and PCB routing guidelines for the Granit carrier board.

## SATA Power Switching

12V and 5V to the SATA connector are switched by P-channel MOSFETs
(Q2, Q3 — FDS4435BZ). GPIO17 (`SATA_PWR_EN`) drives N-channel level shifters
(Q5, Q6 — 2N7002) which pull the P-FET gates low to turn them on.

```
Supply (+12V or +5VP)
  │
  JP5/JP6 pad 1 ─── [bridged default] ─── JP5/JP6 pad 2 (common)
                                              │
  JP5/JP6 pad 3 ─── GND                  R12/R13 (100K)
                                              │
                                         ┌────┴──── Q2/Q3 gate
                                         │
                                    2N7002 drain
                                         │
  SATA_PWR_EN (GPIO17) ── R14 (10K) ── 2N7002 gate
                                         │
                                    2N7002 source
                                         │
                                        GND
```

Two 3-pad solder jumpers (JP5 `SATA_12V_PWR`, JP6 `SATA_5V_PWR`) select the boot default:
- **Pads 1-2 bridged (default):** 100K pull-up to source → FETs OFF → HDD powered on by software
- **Pads 2-3 bridged:** 100K pull-down to GND → FETs ON → HDD powered at boot

GPIO17 high → N-FET on → P-FET gate low → SATA power on.
GPIO17 low or high-Z (boot default) → N-FET off → pull-up holds P-FET off.

R14 (10K) protects GPIO17 against N-FET gate-to-drain failure.

## Power Routing & Netclasses

PCB is fabricated with JLCPCB standard 4-layer stackup (1oz / 35µm copper on all layers).
Track widths are sized per IPC-2221 for outer-layer traces with 20°C temperature rise.

| Netclass | Track Width | Via (pad/drill) | Capacity (1oz, 20°C rise) | Worst-case Load | Nets |
|---|---|---|---|---|---|
| Power 12V | 3.0mm | 1.6mm / 0.8mm | ~3.5A | ~2.5A | `+12V*`, `fused`, `unfused` |
| Power 5V | 2.5mm | 1.6mm / 0.8mm | ~3.2A | ~2.8A | `+5VP`, `VBUS`, `switch` |
| Power 3V3 | 1.0mm | 0.8mm / 0.4mm | ~1.5A | ~0.6A | `+3V3` |

### Routing Guidelines

- Netclass widths are the default for main runs. Neck down to pad width over the last 1–2mm at component pads.
- Use copper pours for 12V and 5V in the PSU area where space allows.
- Use 2–3 parallel vias where power traces change layers.
- Place GND return vias near every power via.
- Keep 12V and 5V routing on top/bottom layers — do not break the inner GND planes.
- Do not route power traces under or parallel to PCIe/SATA/Ethernet differential pairs.

### Layer Strategy

- **Top layer:** PSU components and local routing, signal components
- **Inner 1 (In1.Cu):** GND plane — keep unbroken
- **Inner 2 (In2.Cu):** GND plane — keep unbroken
- **Bottom layer:** Power distribution (5V, 12V, 3.3V to rest of board), signal routing

### Signal Integrity

- **PCIe:** 100Ω differential impedance, matched length, minimize vias and stubs
- **SATA:** 100Ω differential impedance, matched length
- **Ethernet:** 100Ω differential impedance to RJ45 with magnetics
- **USB:** 90Ω differential impedance
- Power traces crossing differential pairs must cross perpendicular (90°)

## Power Budget

| Rail | Source | Capacity | Worst-case Load |
|---|---|---|---|
| 12V | External PSU | 3A+ recommended | ~2.5A (HDD spin-up + buck converter) |
| 5V | AP64501SP-13 | 3.5A | ~2.8A (CM4 + HDD + USB) |
| 3.3V | NCP1117 LDO | 1A | ~0.6A (ASM1061 + RTC + misc) |

Realistic steady state: ~1.5A (CM4) + 0.5A (HDD) = 2.0A on 5V rail.
HDD spin-up and CM4 peak don't occur simultaneously — SATA power is software-controlled.
