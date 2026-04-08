# Granit — TODO

## Schematic

### Done
- [x] PSU: AP64501SP-13 buck + NCP1117 LDO + FDS4435BZ reverse polarity (from pedalboard-hw)
- [x] CM4 Connector 1: power, GND, NC flags, global labels
- [x] CM4 Connector 2: power, GND, NC flags, global labels
- [x] Peripherals: status LEDs (nLED_PWR, nLED_ACT, DNP)
- [x] Peripherals: SK6812MINI-E NeoPixel + 74AHCT1G125 level shifter
- [x] Peripherals: tactile button (GPIO17) + pull-up
- [x] Peripherals: nRPIBOOT 2-pin header
- [x] Peripherals: UART debug 3-pin header
- [x] Peripherals: DS3231MZ RTC + CR2032 battery
- [x] Peripherals: USB-C OTG + USBLC6-2SC6 ESD protection
- [x] Peripherals: USB_OTG_ID solder jumper (device/host mode)
- [x] Ethernet: RB1-125B8G1A Gigabit MagJack + LEDs
- [x] SATA: ASM1061 PCIe-to-SATA bridge (QFN-48+EP)
- [x] SATA: 25MHz crystal + load caps
- [x] SATA: 7-pin data connector (Port A)
- [x] SATA: PCIe global labels (CLK, TX, RX, nRST)
- [x] ERC: 0 errors, 0 warnings

### TODO
- [ ] PSU: replace polyfuse with 3A slow-blow SMD fuse (2410 package)
- [ ] SATA: 15-pin SATA power connector (12V passthrough, 5V, 3.3V)
- [ ] RTC alarm → GLOBAL_EN wake circuit
- [ ] Assign footprints to all components
- [ ] Review component values (resistors, caps)
- [ ] Re-enable ERC check in CI

### Missing Footprints
- [ ] BT1 (Battery_Cell) — CR2032 holder
- [ ] D1, D2 (LED R, LED G) — 0805 LED
- [ ] J1 (Conn_01x02) — 2-pin header (nRPIBOOT)
- [ ] J2 (Conn_01x03) — 3-pin header (UART)
- [ ] R1, R2 (2K2) — 0805 resistor
- [ ] R3 (220R) — 0805 resistor
- [ ] R4, R7, R8 (10K) — 0805 resistor
- [ ] R5, R6 (4K7) — 0805 resistor
- [ ] R9, R10 (5K1) — 0805 resistor
- [ ] SW1 (SW_Push) — tactile switch
- [ ] U1 (74AHCT1G125) — SOT-23-5
- [ ] JP1 (SolderJumper_2_Bridged) — solder jumper
- [ ] J3 (USB_C_Receptacle) — USB-C connector
- [ ] U3 (USBLC6-2SC6) — SOT-23-6
- [ ] Y1 (Crystal 25MHz) — crystal footprint
- [ ] J5 (SATA data) — 7-pin SATA data connector

## PCB Layout
- [ ] Define board outline and mounting holes
- [ ] 4-layer stackup (signal/GND/power/signal)
- [ ] Place connectors (SATA, RJ45, USB-C, barrel jack, screw terminal)
- [ ] Place CM4 connectors
- [ ] Route PCIe differential pairs (100Ω impedance)
- [ ] Route Ethernet differential pairs
- [ ] Route USB differential pairs
- [ ] Route SATA differential pairs
- [ ] Power planes
- [ ] DRC clean

## CI/CD
- [x] KiBot artifact generation with KiCad 10
- [x] GitHub Pages deployment
- [ ] Re-enable ERC/DRC checks when schematics are complete
- [ ] Switch to kicad10_auto container when available

## Software
- [ ] Raspberry Pi OS Lite base image
- [ ] Device tree overlay for ASM1061
- [ ] DS3231 RTC driver + alarm wake
- [ ] NeoPixel status daemon
- [ ] Button handler (shutdown/backup/maintenance)
- [ ] WireGuard VPN configuration
- [ ] Restic backup automation
- [ ] LUKS encrypted backup partition
- [ ] Healthcheck dead man's switch
- [ ] SMART disk monitoring
