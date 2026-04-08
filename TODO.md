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
- [ ] Define board outline and mounting holes
- [ ] 4-layer stackup (signal/GND/power/signal)
- [ ] Place connectors (SATA, RJ45, USB-C, barrel jack, screw terminal)
- [ ] Place CM4 connectors
- [ ] Place ASM1061 + decoupling
- [ ] Route PCIe differential pairs (100Ω impedance)
- [ ] Route SATA differential pairs
- [ ] Route Ethernet differential pairs
- [ ] Route USB differential pairs
- [ ] Power planes
- [ ] DRC clean

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
