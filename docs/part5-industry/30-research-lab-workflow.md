# Chapter 30 — PCB Design in a Research Lab

> **Mentor's note:** Research hardware has different constraints from products. Quantities are low,
> iteration speed matters more than unit cost, the requirements change as the science does, and the
> "customer" is you or a colleague. Here is how to take the industry practices from this guide and
> scale them down sensibly.

---

## 30.1 What to keep from industry, and what to drop

| Keep (high value, low cost) | Drop or simplify |
|-----------------------------|------------------|
| Requirements + block diagram + power budget | Formal PLM/sign-off workflows |
| Design notes with calculations | IPC Class 3, full compliance testing (unless required) |
| Schematic + placement + layout reviews (ask a labmate, or post to a forum) | Multi-sourcing every part (but buy spares!) |
| Checklists | Production test fixtures (unless > ~20 units) |
| DFT: test points, debug header, 0 Ω isolation, LEDs | Cost optimization below a few dollars |
| Git + tagged releases + bring-up logs | |
| Independent Gerber check | |

## 30.2 Strategies that speed up research iteration

1. **Modular architecture:** split the system into boards: a **motherboard** (MCU, power, comms) plus **daughterboards** (sensor front ends,
   drivers) on standard connectors. You can re-spin the analog front end without touching the digital board.
   - Consider standard form factors to leverage existing ecosystems: Arduino shield, Raspberry Pi HAT, Feather/FeatherWing,
     **Adafruit STEMMA QT / SparkFun Qwiic** (I²C over JST-SH) for sensors, or PMOD for FPGA boards.
2. **Start from eval boards and reference designs.** Prove the concept on an EVM with jumper wires, then design your own board by copying the
   EVM's schematic and layout around the critical part.
3. **Build in flexibility for rev A:** DNP footprints for alternate filter values, gain resistors, extra bypass options, 0 Ω jumpers to reconfigure,
   headers on unused MCU pins. Rev A is a lab instrument for debugging your own design, so give yourself access to everything.
4. **Two-pass strategy:** rev A is a big, debug-friendly board (0603, test points, headers). Rev B is the compact version once the circuit is proven.
5. **Use modules** for hard parts: power modules, RF modules, MCU modules (e.g. ESP32 or nRF modules), isolated DC-DC modules.
   They trade cost and size for zero risk in areas outside your research focus.
6. **Order turnkey assembly** for anything with QFN/BGA/0402. Your time is worth more than the assembly fee.
7. **Order 5–10 boards** even if you need 1: rework accidents happen, and colleagues will want them.

## 30.3 Documentation for reproducibility (and for your paper)
Your board is part of your experimental method. Document it so others can reproduce it:
- Publish the hardware (schematic PDF, BOM, Gerbers, ideally the Altium source) with the paper in a repository (Zenodo gives it a DOI).
- Record the **measured performance** (noise floor, bandwidth, linearity, temperature drift) with the test method. Reviewers will ask.
- Tag the exact hardware revision and firmware version used for each dataset.
- Open hardware licenses: CERN-OHL-P/W/S, or CC-BY for documentation.

## 30.4 Calibration and characterization
Every measurement board should come with:
- A **characterization report**: noise (shorted input), gain/offset (known references), bandwidth (sine sweep), crosstalk between channels, temperature drift (if relevant).
- A **calibration procedure** and per-board calibration constants stored in the MCU (EEPROM/flash) with the board serial number.
- Built-in self-test where possible: a known reference voltage or a test-signal injection path multiplexed to the input.

## 30.5 Common research-board patterns

| Application | Key chapters | Typical architecture |
|-------------|--------------|----------------------|
| Multi-channel biopotential (EEG/EMG/ECG) | 15, 12, 29 | ADS1299-class AFE, battery power, isolated/wireless data, driven right leg |
| Strain/force/pressure (bridges) | 15, 4 | Ratiometric 24-bit ΔΣ ADC (ADS1220/AD7124), excitation = reference |
| Photodetection | 15, 4 | TIA with guard ring, low-bias op-amp, shielded enclosure, lock-in (sync detection) in firmware |
| Electrochemistry (potentiostat) | 15, 4 | Control amp + TIA with switched gains, DAC for bias, high-Z guarded inputs |
| Temperature (RTD/thermocouple) | 15 | RTD: ratiometric with reference resistor; TC: cold-junction compensation, INA/ADC with low offset |
| Motor/actuator control | 11, 20, 19 | Gate drivers, current sensing (Kelvin shunts), hot-loop layout, isolated feedback |
| Piezo/HV drivers | 29, 11 | Boost/flyback HV supply, HV op-amp, creepage/clearance, safety |
| Data acquisition + FPGA | 17, 18, 14 | 6–8 layers, DDR/USB 3/Ethernet, strict SI/PI |
| Wireless sensor node | 21, 11 | Module-based radio, low-Iq regulators, energy budget, antenna keep-out |

## 30.6 Your personal growth path as a designer
1. **Recreate eval boards** in Altium (schematic and layout) as practice. Compare your layout with theirs.
2. **Read other people's layouts:** open-hardware projects with Altium sources, vendor EVM files.
3. **Measure everything** you design, and compare it with your predictions. The gap is where you learn.
4. **Keep a personal "lessons learned" file** and add it to your checklists.
5. Learn one simulation tool deeply (LTspice or Altium Mixed-Sim) and use it for every non-trivial analog circuit.
6. Get your layouts reviewed by someone more experienced, and review others' in return.

---

🎓 **You've reached the end of the main chapters.** Now build [the projects](../../projects/) and keep the
[appendices](../appendices/) and [checklists](../../checklists/) close while you work.
