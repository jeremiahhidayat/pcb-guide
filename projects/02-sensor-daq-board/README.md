# Project 2 — Sensor DAQ Board (4 layers, mixed-signal)

> Goal: a real research instrument, a 4-channel precision data-acquisition board for bridge sensors
> (strain gauges / load cells / pressure sensors), streamed over USB. It exercises Part 3 (Chapters 11–15).

## Specification

| Item | Requirement |
|------|-------------|
| Channels | 4 differential inputs for full-bridge sensors (350 Ω–1 kΩ bridges), 2 mV/V |
| Resolution | ≤ 0.01% FS noise-free at 10 SPS (≈ 1 µV p-p input-referred for ±10 mV FS) |
| Excitation | 5 V (or 3.3 V) ratiometric, shared by all bridges, current-limited |
| ADC | 24-bit ΔΣ with PGA and ratiometric reference inputs (e.g. ADS1262, ADS124S08, AD7124-4/-8) |
| MCU | USB-capable MCU (e.g. STM32G4/RP2040/nRF52840) |
| Power | USB-C 5 V → low-noise rails (LDO for analog, buck or LDO for digital) |
| Interfaces | USB (CDC serial), SWD, UART console, 4× sensor connectors (screw terminals or JST) |
| Protection | ESD on sensor inputs and USB; input series resistors + RC filters |
| Board | 4 layers (Sig / GND / GND or PWR / Sig), 1.6 mm, ≤ 80 × 60 mm |

## Architecture (suggested)
```
USB-C ─► TVS/PTC ─► 5V ─┬─► LDO 3V3_D (MCU, USB)
                        ├─► low-noise LDO 5V_A or 3V3_A ─► ADC AVDD + bridge excitation (via current-limit)
                        └─► (optional) ferrite + π filter
Bridge ×4 ─► RC filter (diff + CM caps) ─► ADC AIN (mux) ─ SPI ─► MCU ─► USB CDC to PC
                     ▲ REFP/REFN sensed at bridge excitation (Kelvin)
```

## Decisions to justify in design notes
1. **Noise budget** (Chapter 15): ADC noise at your PGA gain and data rate (from the datasheet table), bridge thermal noise,
   excitation noise (ratiometric cancellation), and how it compares to the 1 µV p-p goal.
2. **Input filter:** differential and common-mode cap values; why C_diff ≥ 10 × C_cm; resistor values vs. ADC input current.
3. **Reference:** ratiometric (REF = excitation). Route the REF sense as a Kelvin pair from the bridge excitation point.
4. **Grounding and partitioning:** draw the zone map before placement. Where does the ADC sit? Where does USB enter?
5. **Stackup:** Sig/GND/GND/Sig vs. Sig/GND/PWR/Sig. Which one, and why?
6. **Thermal EMF:** symmetric input routing and connector choice. Keep the regulators away from the input section.
7. **Digital noise:** SPI series resistors, clock source for the ADC, MCU slew-rate settings.
8. **Ground loops:** what happens when the sensor frame is earthed and the PC is earthed? Consider isolated USB (stretch).

## Bring-up
Use [`bringup_test.py`](bringup_test.py) as a starting point. It talks to firmware over a serial port, runs the
shorted-input noise test, and computes noise statistics and an FFT so you can compare the result against your budget.

## Acceptance tests

| Test | Pass criterion |
|------|----------------|
| Shorted input noise (each channel, 10 SPS, 256 samples) | ≤ budget (p-p and rms) |
| Noise spectrum | No 50/60 Hz, SMPS, or USB (1 kHz) spurs above the noise floor |
| Gain accuracy with a precision bridge simulator / resistor | Within calibration spec |
| Channel-to-channel crosstalk (full-scale on one, short on neighbor) | < 1 LSB-equivalent of the noise floor |
| Drift over 1 h at stable temperature | Within budget |
| USB unplug/replug, ESD gun at connectors (if available) | Recovers without damage |

## Stretch goals
- Add isolated USB (ADuM3160 + isolated DC-DC) and measure the noise difference with an earthed sensor.
- Use Altium **multi-channel design** (`Repeat()`) and Rooms for identical channel layouts.
- AC bridge excitation (polarity reversal) to cancel thermal EMF.
