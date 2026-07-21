# Calibration notes — LI-COR LI-190 Q42893

Certificate details used by this project:

- Model: LI-190
- Serial number: Q42893
- Manufacture date: 18 December 2009
- Output sensitivity: 7.59 µA per 1000 µmol m⁻² s⁻¹
- 604 Ω millivolt multiplier magnitude:
  218.09 µmol m⁻² s⁻¹ per mV

The LI-COR certificate presents a negative multiplier for one connector and
meter polarity convention. This project measures ADS1115 A0 minus A1 with the
sensor red conductor on A0 and black/reference on A1. The expected illuminated
signal is therefore positive. Signal polarity can be inverted in `config.py`.
