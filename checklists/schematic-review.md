# Schematic Review Checklist

Copy this into your project's `docs/` and tick items off per board. Record anything you *consciously* skip.

## General
- [ ] Title block complete (name, rev, date, author, sheet N of M)
- [ ] Hierarchy readable; top sheet works as a block diagram
- [ ] Signal flow left → right; power top → bottom
- [ ] Net names meaningful; active-low convention consistent (`_N`)
- [ ] No 4-way junctions; no off-grid wires; no net labels floating off wires
- [ ] ERC clean, or every remaining warning explained
- [ ] Every part has value, package, and MPN (or approved generic)
- [ ] Design notes/calcs referenced for every non-trivial value

## Power
- [ ] Power budget table done; each regulator ≥ 1.5× margin
- [ ] Thermal calc for every regulator, FET, diode, shunt resistor (T_j at max ambient)
- [ ] Input/output caps per datasheet: value **after DC-bias derating**, voltage rating ≥ 1.5–2× working
- [ ] LDO stability requirements (ESR range) met
- [ ] Buck/boost: inductor I_sat > IC current limit; feedback divider tolerance analyzed
- [ ] Enable pins in a defined state; power-good used or left intentionally
- [ ] Sequencing requirements met (datasheet timing)
- [ ] No back-powering paths (I/O driven into unpowered ICs)
- [ ] Input protection: reverse polarity, overcurrent, TVS, hot-plug ringing considered
- [ ] Test points on every rail

## Each IC
- [ ] All power pins connected and individually decoupled
- [ ] All ground pins and **exposed pad** connected
- [ ] Analog supply (VDDA) filtered if required; VREF decoupled
- [ ] Unused inputs tied off per datasheet (no floating CMOS inputs); unused op-amp sections configured
- [ ] Reset, boot and strap pins: correct level at power-up; reset has pull-up / RC / supervisor as required
- [ ] Open-drain outputs have pull-ups (exactly one per net)
- [ ] Pin-function conflicts checked (MCU pin mux: every used peripheral maps to a real pin combination)

## Interfaces
- [ ] Voltage levels compatible on every connection (3.3 V ↔ 5 V ↔ 1.8 V); level shifters where needed
- [ ] I²C: pull-up value from bus capacitance and speed; addresses unique
- [ ] SPI: chip-selects idle high (pull-ups); CPOL/CPHA compatible
- [ ] UART: TX↔RX crossed correctly (label from the MCU's perspective)
- [ ] USB: D+/D− not swapped; USB-C CC resistors (5.1 kΩ each) on sink; ESD array; VBUS detect
- [ ] Series termination resistors on fast clocks/signals (footprints at least)
- [ ] Differential pairs named `_P`/`_N` with diff-pair directives

## Connectors
- [ ] Pinout checked **against the mating connector / cable** (draw the other side!)
- [ ] ESD protection on every externally accessible pin
- [ ] Current rating per pin adequate; keyed/polarized where mis-mating is possible
- [ ] Shield/chassis connection strategy defined

## Analog / precision
- [ ] Noise budget and error budget calculated (Chapter 15)
- [ ] Op-amp: input/output range, stability with capacitive load, GBW for the gain
- [ ] ADC driver RC per datasheet; C0G caps in signal path
- [ ] Resistor tolerances/tempco justified; precision parts where ratios matter
- [ ] Anti-aliasing adequate for sample rate

## Debug & test
- [ ] Programming/debug header (SWD/JTAG) with correct pinout
- [ ] UART console accessible
- [ ] LEDs: power-good, heartbeat
- [ ] 0 Ω isolation links between power stages and loads
- [ ] Spare GPIOs broken out; hardware revision ID straps
- [ ] Mounting holes and fiducials present as schematic parts (so they're in the BOM/PCB)
