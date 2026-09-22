# Project 1 — USB-C Power & LED Board (2 layers)

> Goal: go through **every** step of the flow once on a board simple enough that nothing distracts you.
> Walkthrough: [Chapter 10](../../docs/part2-pcb-foundations/10-first-board-walkthrough.md).

## Specification

| Item | Requirement |
|------|-------------|
| Input | USB-C receptacle, sink only, 5 V default USB power |
| Outputs | 3.3 V @ 500 mA and 5 V passthrough on a 2.54 mm header (e.g. 1×6: 5V, 3V3, GND, GND, spare, spare) |
| Protection | VBUS TVS, resettable fuse (PTC) 750 mA hold, ESD on D+/D− if routed |
| Indicators | Green LED on 3V3 (≈2 mA) |
| Test | Test points: VBUS, VBUS_F, 3V3, GND (×2) |
| Board | 2 layers, 1.6 mm, 1 oz, ENIG, ≤ 30 × 25 mm, 2 × M2.5 mounting holes |

## Decisions to make and justify in your design notes
1. **CC pins:** why two separate 5.1 kΩ resistors? What happens with a C-to-C cable without them?
2. **Regulator:** LDO vs. buck. Do the thermal calc for SOT-223 and SOT-23-5 at 500 mA and 40 °C ambient.
3. **Output capacitor:** what does your LDO's stability section require? What's the effective capacitance of your chosen MLCC at 3.3 V?
4. **Trace widths:** VBUS and 3V3 at 0.5 A. Use `tools/pcb_calc.py trace-width` and also compute voltage drop over your trace length.
5. **Ground:** bottom layer as a solid pour. Where do stitching vias go?
6. **USB-C footprint:** which mechanical tabs are plated? What does the datasheet say about board edge position?

## Step list
- [ ] Design notes: requirements, power budget, calcs
- [ ] Library: USB-C receptacle, LDO, PTC, TVS, LED, header, test point (verify each footprint 1:1)
- [ ] Schematic (1 sheet), compiled clean
- [ ] Schematic review with [`checklists/schematic-review.md`](../../checklists/schematic-review.md)
- [ ] PCB: outline, stackup, rules, placement (power path in a straight line), routing, pours, stitching, silkscreen
- [ ] DRC clean → layout review with [`checklists/layout-review.md`](../../checklists/layout-review.md)
- [ ] OutJob → Gerbers/drill/BOM/PnP → independent Gerber check ([`checklists/fab-release.md`](../../checklists/fab-release.md))
- [ ] Order (bare boards + stencil, or assembled)
- [ ] Bring-up: resistance checks, current-limited power-up, measure 3V3 under 0/250/500 mA load, measure ripple, check LDO temperature

## Acceptance tests

| Test | Pass criterion |
|------|----------------|
| Enumerates power from a C-to-C charger | 5 V present on VBUS |
| 3V3 at 0 mA and 500 mA | 3.30 V ±2% |
| LDO case temperature at 500 mA, 25 °C ambient | Consistent with your calc (±10 °C) |
| Output ripple (20 MHz BW) | < 20 mV p-p |
| Reversed USB-C plug orientation | Works identically |

## Stretch goals
- Replace the LDO with a buck module and compare efficiency and ripple.
- Add a USB-to-UART bridge (e.g. CH340/CP2102N) and route D+/D− as a 90 Ω pair.
