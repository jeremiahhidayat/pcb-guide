# Chapter 15 — Mixed-Signal, Sensors & Precision Analog

> **Mentor's note:** This is the chapter most research boards live or die by. Your science depends on
> the measurement, and the measurement is limited by noise, drift, leakage and interference that the
> PCB either adds or keeps out.

---

## 15.1 Start with an error and noise budget

Before choosing parts, write down what you're measuring and the resolution you need:

| Question | Example (strain-gauge force sensor) |
|----------|-------------------------------------|
| Signal range | ±2 mV/V bridge × 5 V excitation = ±10 mV full scale |
| Required resolution | 0.01% of FS → 2 µV |
| Bandwidth | DC–10 Hz |
| Accuracy / drift | 0.05% FS over 20–30 °C |
| Sample rate | 100 SPS |

Then allocate the error budget (RSS for random, linear sum for worst-case systematic):
```
Noise (0.1–10 Hz):  INA/ADC input noise    1.0 µV p-p
                    Bridge resistor noise   0.2 µV p-p
                    Reference noise (ratiometric → cancels)
Offset drift:       ADC PGA 5 nV/°C × 10 °C = 0.05 µV  (after offset calibration)
Gain drift:         Ratiometric → excitation drift cancels; ADC gain drift 2 ppm/°C × 10 °C = 20 ppm
Thermal EMF:        Cu–Sn/Pb joints ~ 1-3 µV/°C per junction pair gradient! ← often the largest term
```
Then you design the board to meet this budget. That's the difference between a measurement instrument and a circuit that
merely "works."

## 15.2 Ratiometric measurement (a very useful trick)

If the sensor's output is proportional to its excitation (bridges, potentiometers, RTDs with a reference resistor),
**use the excitation voltage as the ADC reference.** Then reference noise and drift cancel out:
```
V_out = V_exc · (ΔR/R)       ADC code = V_out / V_ref · 2^N = (ΔR/R) · 2^N   when V_ref = V_exc
```
Precision bridge ADCs (e.g. ADS1220/ADS1262, AD7124, HX711 for low-end) support this directly with REFP/REFN inputs.
Route the reference sense lines as a pair directly from the bridge excitation points (Kelvin connection).

## 15.3 Choosing the ADC architecture

| Architecture | Speed | Resolution | Good for |
|--------------|-------|------------|----------|
| **Delta-sigma (ΔΣ)** | 1 SPS – 1 MSPS | 16–32 bit, great at DC | Sensors, bridges, thermocouples, biopotentials, audio. Built-in digital filtering (50/60 Hz rejection!) |
| **SAR** | 100 kSPS – 10 MSPS | 12–20 bit | Multiplexed channels, time-domain signals, control loops |
| **Pipeline** | 10 MSPS – GSPS | 10–16 bit | RF/IF, ultrasound, SDR |
| MCU internal ADC | ≤ few MSPS | 10–12 bit (ENOB 9–11) | Housekeeping, not precision measurement |

**ENOB** (effective number of bits) = (SINAD − 1.76) / 6.02. A "24-bit" ADC typically has 19–22 noise-free bits, depending on data rate and gain.

### Clock jitter limits SNR (for high-frequency signals)
```
SNR_jitter = −20·log10(2π · f_in · t_jitter)
f_in = 1 MHz, t_j = 10 ps → 84 dB (~13.7 bits).  Use a clean oscillator for fast ADCs.
```

## 15.4 Layout of an ADC section (the recipe)

1. **Solid ground plane under the whole AFE + ADC** (Chapter 12). The ADC straddles the analog/digital boundary.
2. **Analog inputs** enter from the analog side, **digital interface** exits on the digital side. Signals don't cross.
3. **Decoupling on AVDD, DVDD, and REF** per datasheet, at the pins. The **REF cap is the most critical:** it supplies
   charge at every conversion.
4. **Input RC filter** (Chapter 4) close to the ADC input, with a C0G cap. For differential inputs, add a differential cap
   plus two small common-mode caps (C_diff ≥ 10 × C_cm, because mismatch in the CM caps converts CM noise into differential noise).
5. **Digital lines:** series resistors (22–100 Ω) at the source to slow edges, and keep the lines short. Keep the SPI **away**
   from analog inputs and reference traces.
6. **Clock** for the ADC: short, series-terminated, away from analog inputs.
7. **The SMPS** sits on the far side of the board, or behind an LDO + filter.
8. **Symmetry for differential signals:** route the + and − lines together, the same length, through matched components.
   Any asymmetry converts common-mode noise into differential signal.

## 15.5 High-impedance and low-current circuits (pA–nA)

Photodiodes, electrochemical sensors, pH electrodes, ion-selective electrodes, piezo sensors, electrometers.
A 1 TΩ leakage path with 1 V across it is **1 pA**, and PCB surfaces leak at that level.

**Techniques:**

| Technique | How |
|-----------|-----|
| **Guard ring** | Surround the high-Z input node with a copper ring (mask removed or not) driven at the *same potential* as the node (e.g. by the op-amp's non-inverting input or a buffer of it). No voltage across the leakage path → no leakage current |
| **Minimize node area** | Connect the sensitive input directly to the op-amp pin, or run it through air (teflon standoff / "flying" connection) for fA work |
| **Cleanliness** | Flux residue is conductive and hygroscopic. **Clean with IPA + ultrasonic**, bake dry, consider conformal coating |
| **Slots/cut-outs** | Milled slot under the high-Z path increases the surface leakage path |
| **Material** | Better laminates (PTFE, Rogers) have higher surface/volume resistivity than FR-4 |
| **Choose parts** | Op-amps with fA bias current (e.g. LMP7721, ADA4530-1 with integrated guard buffer) |
| **Shielding** | A grounded metal can over the input stage stops electrostatic pickup |

```
 Top view, guard ring around the inverting input of a TIA:
        ┌────────────────────────┐
        │ ┌──────────────┐       │   guard ring = copper trace, connected
 PD ────┼─┤ IN− pad (Hi-Z)├── Rf  │   to IN+ (= virtual ground potential)
        │ └──────────────┘       │   → zero volts across the leakage path
        └──────── GUARD ─────────┘
```

## 15.6 Thermal EMF (thermocouple effects)

Every junction of dissimilar metals is a thermocouple: copper–tin/lead solder (~3 µV/°C), copper–kovar (IC leads, ~40 µV/°C!),
resistor terminations. If the two sides of a differential signal path see different temperatures, you get a DC offset.

**Fixes:** symmetric layout (both legs of a signal through the same type and number of junctions, placed close together
so they sit at the same temperature), keep heat sources away, shield from airflow (even a small plastic cover helps),
use a chopper amp, and alternate excitation polarity (AC excitation of bridges) to cancel thermal EMFs.

## 15.7 Mechanical stress and drift

Precision references and some sensors shift output under board flex (piezoresistive effect in silicon).
- Place them away from mounting holes, connectors, and board edges.
- Orient along the board's neutral axis, or cut a **U-shaped slot** around the reference to mechanically isolate it.
- Use package types that are less stress-sensitive (e.g. LCC, or references specified for low hysteresis).

## 15.8 Biopotential and "human-connected" boards (EEG/ECG/EMG)

- **Safety first:** anything connected to a person must be isolated from mains-powered equipment (IEC 60601-1 has
  strict limits on patient leakage currents). For research prototypes: **battery power, or medical-grade isolated supplies plus
  digital isolation** of the data link. Never connect electrodes to a board powered from a wall-powered laptop without isolation.
- Signals are µV-mV riding on large common-mode (50/60 Hz) interference. Use: an INA or ΔΣ AFE (ADS1299-class), a
  **right-leg drive** (driven common-mode feedback), and **input protection resistors + RC filters**.
- **Shielded electrode leads with driven shields** reduce cable capacitance and pickup.

## 15.9 Isolation (for safety and for breaking ground loops)

| Need | Part types |
|------|------------|
| Digital isolation (SPI/UART/I²C) | Digital isolators (ADuM, ISO77xx, Si86xx), ISO1540 (I²C) |
| Isolated power | Isolated DC-DC modules (1–2 W), or isolated converters with integrated transformer (ADuM5020, UCC12050) |
| Isolated analog | Isolated amplifiers (AMC1300), isolated ΔΣ modulators (AMC1306) |
| Isolated USB | ADuM3160/4160 |

Layout: **nothing crosses the isolation barrier except the isolator.** Keep the barrier gap free of copper on *all* layers,
and meet creepage/clearance (Chapter 29). Isolated DC-DC converters are noisy EMI sources. Follow their layout guides, and
consider the stitching capacitance across the barrier (a small Y-cap) that EMC may need.

## 15.10 Shielding

- **Electric field (capacitive) pickup:** grounded conductive shield (a board-mounted shield can, or the enclosure). Easy.
- **Magnetic field (low-frequency) pickup:** difficult. Minimize loop area (twisted pairs, tight layout), increase distance,
  or use mu-metal. A copper can does almost nothing at 60 Hz.
- Board-level shield cans (e.g. from Würth, Laird) need a ring of grounded pads with stitching vias.

## 15.11 🛠️ In Altium: precision analog tricks
- **Net ties** to create Kelvin connections and single-point joins.
- **Polygon cutouts** (**Place » Polygon Pour Cutout**) or keep-outs to clear copper around high-Z nodes on *all* layers,
  including inner planes (reduces capacitance and leakage).
- **Board cutouts** (**Place » Board Cutout**, or a region with Board Cutout kind) for slots around references and under Hi-Z nodes.
- **Rooms** for each identical analog channel so they're laid out identically (matching matters).
- **Differential pair routing** for analog differential signals too (without impedance control, but it keeps them together).
- **Solder mask openings** for guard rings: add a region on the Solder Mask layer to expose the ring if you want it bare.

## Exercises
1. Build a noise budget for a thermocouple (41 µV/°C) front end needing 0.1 °C resolution. What noise-free resolution do you need? (≈ 4 µV.)
2. Design the guard ring for a photodiode TIA with a 1 GΩ feedback resistor. Where does the guard connect?
3. Sketch the board partition for: USB-C power, a 1 MHz buck, an MCU with BLE, and a 24-bit ΔΣ ADC measuring a bridge.
4. Study the ADS1299EEG-FE or AD7124 eval board layout, and identify every technique in this chapter.

**Next part:** [Part 4 — Chapter 16: Transmission Lines & Signal Integrity](../part4-advanced/16-transmission-lines-and-signal-integrity.md)
