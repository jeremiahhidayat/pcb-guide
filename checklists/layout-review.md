# Layout Review Checklist

## Setup
- [ ] Stackup matches the fab quote; impedance profiles defined; board thickness correct
- [ ] Rules imported from the fab-class template; priorities sane (specific above general)
- [ ] Net classes (PWR, FAST, HV, analog) and diff-pair classes defined
- [ ] Schematic and PCB in sync (Design » Update PCB shows no changes)

## Mechanical
- [ ] Board outline, holes, and connector positions match the enclosure/mechanical drawing (3D STEP check)
- [ ] Connector overhang and orientation correct; mating side accessible
- [ ] Keep-outs respected (mounting hardware, enclosure ribs, antenna areas)
- [ ] Tall components clear lids/other boards (3D clearance)
- [ ] Parts ≥ 3–5 mm from board edge / V-score; MLCCs oriented parallel to edges near breakaways

## Placement
- [ ] Zones: power entry / SMPS / digital / analog / RF separated
- [ ] SMPS hot loops minimal: input cap at VIN/PGND pins; SW node small; feedback away from SW/L
- [ ] Decoupling caps at pins, vias at pads, on the same side as the IC where possible
- [ ] Crystal close to MCU; nothing routed underneath on adjacent layers
- [ ] ADC straddles analog/digital boundary; reference cap at pin
- [ ] Protection (TVS) at connectors, first in the signal path
- [ ] Heat sources spread out and away from sensitive parts
- [ ] Test points reachable by probes; debug header accessible

## Routing
- [ ] Every signal layer adjacent to a reference plane; no fast signal crosses a plane split/slot
- [ ] Stitching vias next to every layer-change via of fast signals; stitching caps where reference changes power↔ground
- [ ] Controlled-impedance nets use the impedance-profile widths
- [ ] Differential pairs: coupled, symmetric, length-matched, minimal vias
- [ ] Length/timing matching met (xSignals report)
- [ ] Clocks: short, series-terminated at the driver, spaced ≥ 3w from other nets
- [ ] Sensitive analog routed only over analog ground area; guard rings where needed
- [ ] Power traces/pours sized for current and voltage drop; multiple vias at power transitions
- [ ] No acute angles, no unintended stubs, no antennas (dead-end traces)
- [ ] Traces kept away from board edges (fast nets ≥ 3–5 × h)

## Planes and pours
- [ ] Ground plane solid; inspected in single-layer mode for islands and anti-pad "slots"
- [ ] Polygon pours repoured; dead copper removed; outer-layer pours stitched
- [ ] Thermal reliefs on normal pads; direct connect on thermal/power pads
- [ ] Thermal vias under exposed pads (tented/filled as specified)
- [ ] Ground planes stitched at the board edge

## Manufacturing & assembly
- [ ] DRC clean (0 violations)
- [ ] Silkscreen: readable, not on pads, polarity/pin-1 marks visible after placement
- [ ] Board name, revision, date on copper (and silk)
- [ ] Fiducials (3 global + local for fine pitch)
- [ ] Paste windows on exposed pads (50–70%)
- [ ] Teardrops added (if used), polygons repoured after
- [ ] Test point sizes/spacing per the assembler/fixture rules

## Safety / EMC
- [ ] HV clearances/creepage rules applied; isolation barrier clear on all layers
- [ ] Cables/connectors filtered at the entry point; chassis ground strategy implemented
- [ ] Unused copper/heatsinks grounded
