# LI-190 Pico PAR Meter

A MicroPython PAR/PPFD meter for a **LI-COR LI-190 quantum sensor**, using:

- Raspberry Pi Pico
- ADS1115 16-bit ADC
- SSD1306 128×64 I²C OLED
- Sensor calibration specifications

The program prints the raw ADC value, sensor voltage and calculated PPFD to
the MicroPython console while showing the PPFD and millivolt signal on the
OLED.

## Calibration

The calibration certificate for this particular sensor specifies:

- Output: **7.59 µA per 1000 µmol m⁻² s⁻¹**
- With the 604 Ω millivolt adapter/shunt:
  **218.09 µmol m⁻² s⁻¹ per mV**

The project therefore calculates:

```text
PPFD = measured_mV × 218.09
```



## Wiring

Pin names are **Pico GPIO numbers**. Physical header pin numbers are included
to avoid ambiguity.

### ADS1115 on I²C0

| ADS1115 | Raspberry Pi Pico |
|---|---|
| VDD | 3V3 OUT, physical pin 36 |
| GND | Any GND |
| SDA | GP0, physical pin 1 |
| SCL | GP1, physical pin 2 |

### ADS1115 on LI-190 Sensor

| ADS1115 | LI-190 Sensor |
|---|---|
| A0 | LI-190 red wire |
| A1 | LI-190 black wire |
| GND | LI-190 clear wire |

Connect the LI-190 black/reference wire to **A1 and system ground**. Connect
the clear shield to ground at the electronics end only.

Do not add another 604 Ω resistor when the sensor cable already contains the
604 Ω shunt.

### SSD1306 OLED on I²C1

| OLED | Raspberry Pi Pico |
|---|---|
| VCC | 3V3 OUT |
| GND | Any GND |
| SDA | GP2, physical pin 4 |
| SCL | GP3, physical pin 5 |

The default OLED address is `0x3C`; the program also checks `0x3D`.

## ADS1115 configuration

The included driver uses:

- Differential input: AIN0 minus AIN1
- Full-scale range: ±0.256 V
- Resolution: 7.8125 µV per count
- Single-shot mode
- 128 samples per second
- 16 conversions averaged per displayed reading

## Installation on the Pico

Copy these four files to the Pico filesystem:

```text
main.py
config.py
ads1115.py
ssd1306.py
```

Using Thonny:

1. Connect the Pico and choose its MicroPython interpreter.
2. Open each file from this repository.
3. Save each one to the Raspberry Pi Pico.
4. Reset the Pico.

Because the application is named `main.py`, it starts automatically at boot.

## Configuration

Edit `config.py` to change:

- I²C pins and addresses
- OLED dimensions
- Number of averaged samples
- Display interval
- Calibration multiplier
- Dark offset
- Signal polarity

When the sensor gives a negative voltage under illumination, either swap A0
and A1 or set:

```python
SIGNAL_SIGN = -1.0
```

## Expected console output

```text
I2C0 devices: ['0x48']
I2C1 devices: ['0x3C']
ADS1115 address: 0x48
OLED address:    0x3C
Calibration:     218.09 umol/m2/s per mV

Raw:    585.31 | Signal:   4.5727 mV | PPFD:   997.29 umol m^-2 s^-1
```

## Dark-offset correction

For greater accuracy near zero:

1. Cover the sensor completely.
2. Record the stable millivolt value shown in the console.
3. Enter that value in `config.py`:

```python
DARK_OFFSET_MV = 0.0123
```

The program subtracts this value before converting the signal to PPFD.


## License

MIT
