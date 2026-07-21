"""
Minimal ADS1115 driver for MicroPython.

Configured for:
    - Differential AIN0 minus AIN1
    - +/-0.256 V full-scale range
    - Single-shot conversion
    - 128 samples per second
"""


class ADS1115:
    REG_CONVERSION = 0x00
    REG_CONFIG = 0x01

    # OS       = 1: start single conversion
    # MUX      = 000: AIN0 minus AIN1
    # PGA      = 101: +/-0.256 V
    # MODE     = 1: single-shot
    # DR       = 100: 128 samples per second
    # COMP_QUE = 11: comparator disabled
    CONFIG_A0_A1_256MV = 0x8B83

    FULL_SCALE_VOLTS = 0.256
    LSB_VOLTS = FULL_SCALE_VOLTS / 32768.0

    def __init__(self, i2c, address=0x48):
        self.i2c = i2c
        self.address = address

    def _write_register(self, register, value):
        payload = bytes((
            (value >> 8) & 0xFF,
            value & 0xFF,
        ))
        self.i2c.writeto_mem(self.address, register, payload)

    def _read_register(self, register):
        payload = self.i2c.readfrom_mem(self.address, register, 2)
        return (payload[0] << 8) | payload[1]

    def read_raw_a0_a1(self):
        """Return one signed differential ADC reading from AIN0-AIN1."""
        import time

        self._write_register(
            self.REG_CONFIG,
            self.CONFIG_A0_A1_256MV,
        )

        started_ms = time.ticks_ms()

        while True:
            status = self._read_register(self.REG_CONFIG)

            # In single-shot mode, OS returns to 1 when conversion is ready.
            if status & 0x8000:
                break

            if time.ticks_diff(time.ticks_ms(), started_ms) > 50:
                raise OSError("ADS1115 conversion timeout")

            time.sleep_ms(1)

        raw = self._read_register(self.REG_CONVERSION)

        if raw & 0x8000:
            raw -= 65536

        return raw

    def read_voltage(self):
        """Return (raw_count, differential_voltage_in_volts)."""
        raw = self.read_raw_a0_a1()
        return raw, raw * self.LSB_VOLTS

    def read_average(self, samples=16):
        """Average multiple conversions and return (raw_average, volts)."""
        if samples < 1:
            raise ValueError("samples must be at least 1")

        total = 0

        for _ in range(samples):
            total += self.read_raw_a0_a1()

        raw_average = total / samples
        voltage_average = raw_average * self.LSB_VOLTS

        return raw_average, voltage_average
