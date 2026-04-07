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

### TODO
- [ ] PSU: replace polyfuse with 3A slow-blow SMD fuse
- [ ] SATA: ASM1061 PCIe-to-SATA bridge (QFN-64)
- [ ] SATA: 22-pin SATA connector (data + power)
- [ ] SATA: 12V passthrough to SATA power
- [ ] Ethernet: RJ45 connector + magnetics
- [ ] USB-C: OTG connector + USBLC6-2SC6 ESD protection
- [ ] RTC alarm → GLOBAL_EN wake circuit
- [ ] Resolve remaining ERC errors (8 undriven inputs)
- [ ] Assign footprints to all components
- [ ] Review component values (resistors, caps)

## PCB Layout
- [ ] Define board outline and mounting holes
- [ ] 4-layer stackup (signal/GND/power/signal)
- [ ] Place connectors (SATA, RJ45, USB-C, barrel jack, screw terminal)
- [ ] Place CM4 connectors
- [ ] Route PCIe differential pairs (100Ω impedance)
- [ ] Route Ethernet differential pairs
- [ ] Route USB differential pairs
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
