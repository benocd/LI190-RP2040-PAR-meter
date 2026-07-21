"""
LI-COR LI-190 quantum sensor / PAR meter
Raspberry Pi Pico + ADS1115 + SSD1306 OLED

The Pico runs this file automatically when it is saved as main.py.

Sensor calibration:
    Serial number: Q42893
    218.09 umol m^-2 s^-1 per mV
"""

from machine import I2C, Pin
import time

import config
from ads1115 import ADS1115
from ssd1306 import SSD1306_I2C


def format_i2c_addresses(addresses):
    return ["0x{:02X}".format(address) for address in addresses]


def find_oled_address(i2c):
    devices = i2c.scan()

    if config.OLED_ADDRESS in devices:
        return config.OLED_ADDRESS

    # Common fallback address for SSD1306 displays.
    alternative = 0x3D if config.OLED_ADDRESS == 0x3C else 0x3C
    if alternative in devices:
        return alternative

    return None


def show_startup(oled):
    oled.fill(0)
    oled.text("LI-190 PAR METER", 0, 8)
    oled.text("Starting...", 0, 26)
    oled.text("Sensor Q42893", 0, 44)
    oled.show()


def show_reading(oled, ppfd, signal_mv):
    oled.fill(0)
    oled.text("LI-190 PAR SENSOR", 0, 0)
    oled.hline(0, 10, config.OLED_WIDTH, 1)

    oled.text("PPFD", 0, 16)
    oled.text("{:8.1f}".format(ppfd), 0, 28)
    oled.text("umol m-2 s-1", 0, 40)
    oled.text("{:8.3f} mV".format(signal_mv), 0, 54)

    oled.show()


def show_error(oled, message):
    message = str(message)

    oled.fill(0)
    oled.text("SENSOR ERROR", 0, 0)
    oled.text(message[0:16], 0, 18)
    oled.text(message[16:32], 0, 30)
    oled.text(message[32:48], 0, 42)
    oled.show()


def initialise_devices():
    ads_i2c = I2C(
        config.ADS_I2C_ID,
        sda=Pin(config.ADS_SDA_PIN),
        scl=Pin(config.ADS_SCL_PIN),
        freq=config.I2C_FREQUENCY_HZ,
    )

    oled_i2c = I2C(
        config.OLED_I2C_ID,
        sda=Pin(config.OLED_SDA_PIN),
        scl=Pin(config.OLED_SCL_PIN),
        freq=config.I2C_FREQUENCY_HZ,
    )

    ads_devices = ads_i2c.scan()
    oled_devices = oled_i2c.scan()

    print("I2C{} devices: {}".format(
        config.ADS_I2C_ID,
        format_i2c_addresses(ads_devices),
    ))
    print("I2C{} devices: {}".format(
        config.OLED_I2C_ID,
        format_i2c_addresses(oled_devices),
    ))

    if config.ADS_ADDRESS not in ads_devices:
        raise OSError(
            "ADS1115 not detected at 0x{:02X}".format(config.ADS_ADDRESS)
        )

    oled_address = find_oled_address(oled_i2c)
    if oled_address is None:
        raise OSError(
            "SSD1306 OLED not detected at 0x3C or 0x3D"
        )

    ads = ADS1115(ads_i2c, address=config.ADS_ADDRESS)
    oled = SSD1306_I2C(
        config.OLED_WIDTH,
        config.OLED_HEIGHT,
        oled_i2c,
        address=oled_address,
    )

    return ads, oled, oled_address


def calculate_ppfd(signal_mv):
    corrected_mv = (
        config.SIGNAL_SIGN * signal_mv
        - config.DARK_OFFSET_MV
    )

    ppfd = corrected_mv * config.PPFD_PER_MV

    # Very small negative values are expected around darkness because of
    # electrical offset and noise. A physical PPFD reading cannot be negative.
    return corrected_mv, max(0.0, ppfd)


def main():
    print()
    print("LI-COR LI-190 PAR meter")
    print("-----------------------")

    try:
        ads, oled, oled_address = initialise_devices()
    except Exception as error:
        print("Initialisation error:", error)
        raise

    show_startup(oled)
    time.sleep_ms(1000)

    print("ADS1115 address: 0x{:02X}".format(config.ADS_ADDRESS))
    print("OLED address:    0x{:02X}".format(oled_address))
    print(
        "Calibration:     {:.2f} umol/m2/s per mV".format(
            config.PPFD_PER_MV
        )
    )
    print()

    while True:
        try:
            raw_average, voltage_v = ads.read_average(
                config.SAMPLES_PER_READING
            )

            signal_mv = voltage_v * 1000.0
            corrected_mv, ppfd = calculate_ppfd(signal_mv)

            print(
                "Raw: {:9.2f} | "
                "Signal: {:8.4f} mV | "
                "PPFD: {:8.2f} umol m^-2 s^-1".format(
                    raw_average,
                    corrected_mv,
                    ppfd,
                )
            )

            show_reading(oled, ppfd, corrected_mv)

        except Exception as error:
            print("Measurement error:", error)
            show_error(oled, error)

        time.sleep_ms(config.DISPLAY_INTERVAL_MS)


main()
