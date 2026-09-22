# Chapter 3 — Semiconductors: Diodes, BJTs, MOSFETs

> **Mentor's note:** You don't need to derive band diagrams to design boards. You *do* need a working model
> of each device that predicts heat, speed, and failure. That's what this chapter gives you.

---

## 3.1 Diodes

### Model that's good enough 95% of the time
```
I = I_S · (e^(V / (n·V_T)) − 1)        V_T = kT/q ≈ 25.9 mV at 300 K
```
Practically: current grows about **10× for every ~60 mV** (n = 1) of extra forward voltage. So a
silicon diode "turns on" at about 0.6–0.7 V, and its forward voltage falls about **2 mV/°C**. That tempco
is the basis of many temperature sensors.

### Diode types and when to use them

| Type | V_F | Key property | Typical use |
|------|-----|--------------|-------------|
| Silicon rectifier (1N4148 small-signal, 1N400x power) | 0.6–1.0 V | Cheap, slow recovery (power) | General rectification |
| **Schottky** | 0.2–0.5 V | Fast, low V_F, **high reverse leakage (rises with temperature)** | Reverse polarity, buck freewheel, OR-ing |
| **Zener** | V_Z (reverse) | Controlled breakdown | Crude references, clamps |
| **TVS** | Clamp | Very fast, absorbs surge energy | ESD/surge protection on connectors |
| LED | 1.8–3.3 V | Emits light | Indication (always add a current-limit R) |

### ⚠️ Gotcha: Schottky leakage in precision circuits
A Schottky diode can leak µA at 85 °C. In a high-impedance sensor circuit, that looks like a signal.

### ⚠️ Gotcha: diode power dissipation
A Schottky carrying 2 A at 0.45 V dissipates 0.9 W. In a SOD-123 package (θJA ≈ 300 °C/W) that is a 270 °C rise, and the part fails.
Always do **P = V_F × I_avg, then ΔT = P × θJA.**

### Reverse-polarity protection: the three options

```
1) Series diode          simple, wastes V_F·I (0.4 V × 2 A = 0.8 W)
2) P-FET high side       ~0 drop (R_DS(on)·I²), a few extra parts, the standard answer
3) Ideal-diode controller  N-FET + controller IC, lowest loss, also blocks reverse current
```

P-FET reverse-polarity circuit (add a Zener gate clamp if Vin > the FET's V_GS(max)):
```
 VIN ──┬──────D  S──────┬── VOUT
       │     └─P-FET─┘  │
       │         G      │
       │         │      │
       │        [R 100k]│   (+ 12V Zener from G to S if VIN > ~15 V)
       │         │
      GND ───────┘
```
Normal polarity: the body diode conducts first, pulling S up to about VIN; then G sits at GND, so
V_GS = −VIN and the FET turns fully on. Reversed: G is higher than S, so the FET stays off and the body
diode is reverse-biased, and the load is protected.

---

## 3.2 Bipolar Junction Transistors (BJTs)

Current-controlled: I_C ≈ β · I_B (β spreads widely, 100–800, and varies with temperature). **Never
design a circuit whose behavior depends on the exact value of β.**

### The one BJT circuit every board uses: low-side switch
```
 +V ──[LOAD]──┐
              C
 MCU ──[R_B]──B   NPN (e.g. MMBT3904 / BC817)
              E
              GND
```
Design procedure (first principles):
1. Load current I_C = 100 mA (for example a relay coil).
2. Saturate hard with a **forced β of 10–20**, independent of datasheet β: I_B = 100 mA/10 = 10 mA.
3. R_B = (V_MCU − V_BE)/I_B = (3.3 − 0.8)/0.01 = 250 Ω → use 220 Ω. Check that the MCU pin can source 10 mA.
4. **Inductive load? Add a flyback diode across the load.** Without it, V = L·di/dt at turn-off
   produces a large spike and kills the transistor.

---

## 3.3 MOSFETs — the workhorse of modern boards

Voltage-controlled: the gate is a capacitor. No DC gate current, but significant **gate charge Q_g**
has to be moved every time the FET switches.

### Key parameters and what they physically mean

| Parameter | Physical meaning | Design consequence |
|-----------|------------------|--------------------|
| **V_GS(th)** | Gate voltage where the channel *barely* starts (often at 250 µA!) | **Not** the voltage for full turn-on. Look at R_DS(on) specified at V_GS = 2.5 V / 4.5 V |
| **R_DS(on)** | Channel resistance when fully on (rises about 1.5× from 25 °C to 125 °C) | Conduction loss I²R |
| **Q_g** | Total charge to move the gate | Switching time t = Q_g / I_gate; driver power = Q_g·V·f |
| **C_iss, C_oss, C_rss** | Input, output, and Miller capacitances | Switching speed and dv/dt coupling |
| **SOA** | Safe operating area in the linear region | Hot-swap/linear use can kill a FET that looks fine on paper |
| **Body diode** | Intrinsic diode S→D (N-channel) | Conducts in synchronous bucks; reverse-recovery losses |

### ⚠️ Gotcha: "logic-level" FET selection
A FET with V_GS(th) = 2 V driven from a 3.3 V MCU may still have high R_DS(on) because it isn't fully
enhanced. **Choose a FET with R_DS(on) specified at V_GS ≤ 2.5 V** for 3.3 V logic drive.

### Low-side N-FET switch with the right resistors
```
 +V ──[LOAD]──D
 MCU ──[R_G 22-100Ω]──G     N-FET
               │      S
            [R_PD 100k]
               │      │
 GND ──────────┴──────┘
```
- **R_G** (series gate resistor) slows edges a little, damps ringing between gate capacitance and trace
  inductance, and limits MCU pin current.
- **R_PD** (pull-down) keeps the FET **off while the MCU is in reset**, when GPIOs float. Forget it and the
  heater or motor turns on at power-up.

### Switching loss estimate (first-order)
```
P_cond = I² · R_DS(on)
P_sw   ≈ ½ · V · I · (t_r + t_f) · f_sw
P_gate = Q_g · V_drive · f_sw        (dissipated in the driver + gate resistor)
```

---

## 3.4 Protection devices you'll put on every research board

| Threat | Device | Placement rule |
|--------|--------|----------------|
| ESD at connectors (USB, headers, probes) | TVS diode arrays (e.g. TPD4E05U06, low capacitance for data) | **As close to the connector as possible**, before anything else. Short, direct path to ground |
| Overcurrent | PTC resettable fuse, eFuse IC, or a regular fuse | At power entry |
| Reverse polarity | P-FET or ideal diode | At power entry |
| Overvoltage/surge | TVS (SMAJ/SMBJ series), rated above max normal V | At power entry |
| Inrush | NTC, soft-start, hot-swap controller | Power entry |

🧠 **Why TVS placement matters:** ESD rise times are sub-nanosecond. The inductance of a 10 mm trace
(~10 nH) with a 30 A ESD current rising in 1 ns gives V = L·di/dt = 10e-9 × 30/1e-9 = **300 V** on
top of the TVS clamp voltage. The TVS only protects what sits *behind* it, and only if the path to
the TVS is short.

---

## 3.5 🛠️ In Altium

- Use **Manufacturer Part Search** to pull real FETs with parametrics, and compare R_DS(on) at your V_GS.
- For power components, add a `Power_Dissipation` parameter and review the thermal budget in the BOM
  (ActiveBOM lets you add custom columns).
- For FETs in SOT-23 or DFN packages, the drain tab is the heatsink: in layout you'll add copper
  pours and thermal vias (Chapter 20).

## Exercises

1. An N-FET with R_DS(on) = 20 mΩ switches 5 A at 100 kHz with t_r = t_f = 20 ns, V = 12 V. Compute conduction and switching losses.
   *(P_cond = 0.5 W; P_sw = 0.5 × 12 × 5 × 40e-9 × 1e5 = 0.12 W.)*
2. Design a P-FET reverse-polarity circuit for a 24 V input. What protects the gate?
3. Why must the flyback diode across a relay coil be *right at the coil or the transistor*, and not at the far end of a cable?

**Next:** [Chapter 4 — Op-Amps and Analog Building Blocks](04-op-amps-and-analog-blocks.md)
