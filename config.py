"""
Hardware and calibration settings for the LI-190 Pico PAR meter.

Pin numbers below are Raspberry Pi Pico GPIO numbers, not physical header
pin numbers.
"""

# ---------------------------------------------------------------------------
# ADS1115 on hardware I2C0
# GP0 = physical pin 1
# GP1 = physical pin 2
# ---------------------------------------------------------------------------

ADS_I2C_ID = 0
ADS_SDA_PIN = 0
ADS_SCL_PIN = 1
ADS_ADDRESS = 0x48

# ---------------------------------------------------------------------------
# SSD1306 OLED on hardware I2C1
# GP2 = physical pin 4
# GP3 = physical pin 5
# ---------------------------------------------------------------------------

OLED_I2C_ID = 1
OLED_SDA_PIN = 2
OLED_SCL_PIN = 3
OLED_ADDRESS = 0x3C
OLED_WIDTH = 128
OLED_HEIGHT = 64

# Both buses are normally reliable at 400 kHz with short wiring.
I2C_FREQUENCY_HZ = 400_000

# ---------------------------------------------------------------------------
# Measurement settings
# ---------------------------------------------------------------------------

SAMPLES_PER_READING = 16
DISPLAY_INTERVAL_MS = 1000

# LI-COR LI-190 serial Q42893 calibration certificate:
# 7.59 microamps per 1000 umol m^-2 s^-1
# With the 604-ohm millivolt adapter/shunt:
# 218.09 umol m^-2 s^-1 per millivolt
PPFD_PER_MV = 218.09

# Measure A0 minus A1. Set this to -1.0 if the signal is reversed.
SIGNAL_SIGN = 1.0

# Optional measured dark offset. Leave at zero for initial operation.
DARK_OFFSET_MV = 0.0
