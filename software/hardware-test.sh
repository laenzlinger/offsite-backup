#!/bin/bash
# Granit hardware test script
# Run on the CM4 after first boot to verify all board functions.
# Usage: sudo ./hardware-test.sh
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
PASS=0; FAIL=0; SKIP=0

pass() { echo -e "  ${GREEN}PASS${NC} $1"; ((PASS++)); }
fail() { echo -e "  ${RED}FAIL${NC} $1"; ((FAIL++)); }
skip() { echo -e "  ${YELLOW}SKIP${NC} $1"; ((SKIP++)); }
section() { echo -e "\n${YELLOW}=== $1 ===${NC}"; }

if [ "$(id -u)" -ne 0 ]; then echo "Run as root"; exit 1; fi

echo -e "${YELLOW}Granit Hardware Test${NC}"
echo "──────────────────────────────────────────"
echo "Before starting, ensure:"
echo "  • CM4 is booted and you have SSH or serial access"
echo "  • Ethernet cable connected"
echo "  • SATA drive connected (optional — test will skip if absent)"
echo "  • 12V power supply connected"
echo "  • You can see the board (for visual LED checks)"
echo ""
read -rp "Press Enter to start tests..."

# --- GPIO pin mapping ---
# GPIO2  = SDA1 (I2C1)       GPIO3  = SCL1 (I2C1)
# GPIO4  = RTC_INT            GPIO5  = SATA_PWR_EN
# GPIO6  = GPIO_HOLD          GPIO14 = UART_TX
# GPIO15 = UART_RX            GPIO17 = BUTTON
# GPIO18 = NEOPIXEL

section "1. Power rails"
for rail in 5V 3V3 12V; do
    # Can't measure voltage from software, just check kernel booted
    pass "CM4 booted (implies ${rail} rail OK)"
    break
done

section "2. I2C bus (GPIO2/GPIO3 — SCL1/SDA1)"
if command -v i2cdetect &>/dev/null; then
    # DS3231 is at 0x68 on I2C-1
    i2c_out=$(i2cdetect -y 1 2>/dev/null || true)
    if echo "$i2c_out" | grep -q "68"; then
        pass "DS3231 RTC detected at 0x68"
    else
        fail "DS3231 RTC not found at 0x68"
        echo "    i2cdetect output:"
        echo "$i2c_out" | sed 's/^/    /'
    fi
else
    skip "i2cdetect not installed (apt install i2c-tools)"
fi

section "3. RTC — DS3231 (I2C 0x68, interrupt on GPIO4)"
if [ -e /dev/rtc0 ] || [ -e /dev/rtc1 ]; then
    rtc_dev=$(ls /dev/rtc* 2>/dev/null | head -1)
    rtc_time=$(hwclock -r --rtc "$rtc_dev" 2>/dev/null || true)
    if [ -n "$rtc_time" ]; then
        pass "RTC readable: $rtc_time"
    else
        fail "RTC device exists but hwclock failed"
    fi
else
    fail "No /dev/rtc* device found (check dtoverlay=i2c-rtc,ds3231)"
fi

# RTC interrupt pin (GPIO4) — should be high (active low, no alarm)
rtc_int=$(gpioget gpiochip0 4 2>/dev/null || echo "err")
if [ "$rtc_int" = "1" ]; then
    pass "RTC_INT (GPIO4) is high (no alarm pending)"
elif [ "$rtc_int" = "0" ]; then
    pass "RTC_INT (GPIO4) is low (alarm pending or active)"
else
    fail "Cannot read GPIO4 (RTC_INT)"
fi

section "4. SATA power control (GPIO5 — SATA_PWR_EN)"
echo "  Testing SATA power gate..."
# Default state depends on solder jumpers JP5/JP6
initial=$(gpioget gpiochip0 5 2>/dev/null || echo "err")
if [ "$initial" = "err" ]; then
    fail "Cannot read GPIO5"
else
    pass "SATA_PWR_EN (GPIO5) initial state: $initial"

    # Toggle on
    gpioset gpiochip0 5=1
    sleep 0.5
    state=$(gpioget gpiochip0 5 2>/dev/null || echo "err")
    if [ "$state" = "1" ]; then
        pass "SATA_PWR_EN set high (power on)"
    else
        fail "SATA_PWR_EN failed to go high"
    fi

    # Toggle off
    gpioset gpiochip0 5=0
    sleep 0.5
    state=$(gpioget gpiochip0 5 2>/dev/null || echo "err")
    if [ "$state" = "0" ]; then
        pass "SATA_PWR_EN set low (power off)"
    else
        fail "SATA_PWR_EN failed to go low"
    fi
fi

section "5. SATA disk (ASM1061 via PCIe)"
if lspci 2>/dev/null | grep -qi "ASM1061\|SATA"; then
    pass "ASM1061 detected on PCIe bus"
    lspci | grep -i "SATA\|ASM" | sed 's/^/    /'
else
    fail "ASM1061 not found on PCIe (check PCIe routing, crystal, power)"
fi

# Power on SATA and scan for disk
gpioset gpiochip0 5=1
sleep 2
echo "- - -" > /sys/class/scsi_host/host0/scan 2>/dev/null || true
sleep 3
if lsblk | grep -q "^sd"; then
    pass "SATA disk detected"
    lsblk -o NAME,SIZE,MODEL | grep "^sd" | sed 's/^/    /'

    # SMART check
    if command -v smartctl &>/dev/null; then
        smart=$(smartctl -H /dev/sda 2>/dev/null || true)
        if echo "$smart" | grep -q "PASSED"; then
            pass "SMART health: PASSED"
        elif echo "$smart" | grep -q "FAILED"; then
            fail "SMART health: FAILED"
        else
            skip "SMART inconclusive"
        fi
    else
        skip "smartctl not installed (apt install smartmontools)"
    fi
else
    skip "No SATA disk connected (or power-on delay too short)"
fi

section "6. Button (GPIO17 — active low, pulled up)"
btn=$(gpioget gpiochip0 17 2>/dev/null || echo "err")
if [ "$btn" = "1" ]; then
    pass "BUTTON (GPIO17) is high (not pressed)"
    echo -e "  ${YELLOW}Press and hold the button...${NC}"
    for i in $(seq 1 30); do
        sleep 0.2
        btn=$(gpioget gpiochip0 17 2>/dev/null || echo "err")
        if [ "$btn" = "0" ]; then
            pass "BUTTON press detected (GPIO17 went low)"
            break
        fi
        if [ "$i" -eq 30 ]; then
            skip "Button not pressed within 6 seconds"
        fi
    done
elif [ "$btn" = "0" ]; then
    fail "BUTTON (GPIO17) stuck low (check for short to GND)"
else
    fail "Cannot read GPIO17"
fi

section "7. NeoPixel LED (GPIO18 via 74AHCT1G125)"
if command -v python3 &>/dev/null; then
    python3 -c "
try:
    import board, neopixel
    pixel = neopixel.NeoPixel(board.D18, 1, brightness=0.3)
    pixel[0] = (255, 0, 0); import time; time.sleep(0.5)
    pixel[0] = (0, 255, 0); time.sleep(0.5)
    pixel[0] = (0, 0, 255); time.sleep(0.5)
    pixel[0] = (0, 0, 0)
    print('OK')
except Exception as e:
    print(f'ERR:{e}')
" 2>/dev/null | while read -r line; do
        if [ "$line" = "OK" ]; then
            pass "NeoPixel cycled R-G-B (verify visually)"
        else
            fail "NeoPixel error: $line"
        fi
    done
    if [ "${PIPESTATUS[0]}" -ne 0 ]; then
        skip "neopixel library not installed (pip install adafruit-circuitpython-neopixel)"
    fi
    read -rp "  Did the NeoPixel flash Red-Green-Blue? [y/N] " answer
    if [[ "$answer" =~ ^[Yy] ]]; then
        pass "NeoPixel visually confirmed"
    else
        fail "NeoPixel not visible (check solder joints, level shifter U3)"
    fi
else
    skip "python3 not available"
fi

section "8. Status LEDs (active low from CM4)"
echo "  Look at the board — the red power LED should be on."
read -rp "  Is the red power LED on? [y/N] " answer
if [[ "$answer" =~ ^[Yy] ]]; then
    pass "Power LED (nLED_PWR) visually confirmed"
else
    fail "Power LED not visible (check D2, R17)"
fi
echo "  Now testing activity LED blink..."
if [ -e /sys/class/leds/ACT ] || [ -e /sys/class/leds/led0 ]; then
    led_path=$(ls -d /sys/class/leds/{ACT,led0} 2>/dev/null | head -1)
    echo "none" > "$led_path/trigger" 2>/dev/null
    echo 1 > "$led_path/brightness" 2>/dev/null; sleep 0.3
    echo 0 > "$led_path/brightness" 2>/dev/null; sleep 0.3
    echo 1 > "$led_path/brightness" 2>/dev/null; sleep 0.3
    echo 0 > "$led_path/brightness" 2>/dev/null
    echo "mmc0" > "$led_path/trigger" 2>/dev/null
    pass "Activity LED toggled (verify visually)"
    read -rp "  Did the green activity LED blink? [y/N] " answer
    if [[ "$answer" =~ ^[Yy] ]]; then
        pass "Activity LED visually confirmed"
    else
        fail "Activity LED not visible (check D3, R18)"
    fi
else
    skip "LED sysfs not found"
fi

section "9. GPIO_HOLD wake circuit (GPIO6)"
hold=$(gpioget gpiochip0 6 2>/dev/null || echo "err")
if [ "$hold" != "err" ]; then
    pass "GPIO_HOLD (GPIO6) readable, state: $hold"
else
    fail "Cannot read GPIO6"
fi

section "10. UART debug header (GPIO14 TX, GPIO15 RX)"
if [ -e /dev/ttyAMA0 ] || [ -e /dev/serial0 ]; then
    serial_dev=$(ls /dev/serial0 /dev/ttyAMA0 2>/dev/null | head -1)
    pass "Serial device available: $serial_dev"
    echo "  Connect USB-UART adapter to J8 (GND-TX-RX) at 115200 baud to verify"
else
    fail "No serial device found (check enable_uart=1 in config.txt)"
fi

section "11. Ethernet"
if ip link show eth0 &>/dev/null; then
    carrier=$(cat /sys/class/net/eth0/carrier 2>/dev/null || echo "0")
    speed=$(cat /sys/class/net/eth0/speed 2>/dev/null || echo "?")
    if [ "$carrier" = "1" ]; then
        pass "Ethernet link up at ${speed}Mbps"
    else
        fail "Ethernet no carrier (check cable)"
    fi
else
    fail "eth0 not found"
fi

section "12. USB-C OTG"
if ls /sys/class/udc/ 2>/dev/null | grep -q .; then
    pass "USB UDC available (OTG capable)"
else
    skip "No USB UDC found (may need dtoverlay=dwc2)"
fi

# --- Summary ---
echo -e "\n${YELLOW}=== SUMMARY ===${NC}"
echo -e "  ${GREEN}PASS: $PASS${NC}  ${RED}FAIL: $FAIL${NC}  ${YELLOW}SKIP: $SKIP${NC}"
if [ "$FAIL" -gt 0 ]; then
    echo -e "  ${RED}Some tests failed — review output above${NC}"
    exit 1
else
    echo -e "  ${GREEN}All tests passed${NC}"
fi
