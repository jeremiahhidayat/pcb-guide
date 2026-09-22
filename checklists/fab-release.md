# Fab Release Checklist

Do this every time, even for a "quick" board.

## Before generating outputs
- [ ] All review comments closed (schematic, placement, layout)
- [ ] DRC and ERC clean; validation outputs pass in the OutJob
- [ ] Design committed; git tag created (`<board>-revX`)
- [ ] Revision updated in: schematic title blocks, PCB copper text, project parameters, CHANGELOG
- [ ] BOM: every line has MPN, stock checked, alternates listed, DNP marked

## Generate (from a clean checkout of the tag)
- [ ] Gerber X2 (or RS-274X) for all used layers + board outline
- [ ] NC drill (plated + non-plated) + drill map
- [ ] (or) ODB++ / IPC-2581
- [ ] IPC-D-356 netlist
- [ ] Fab drawing PDF (stackup table, impedance table, drill table, notes)
- [ ] BOM (xlsx/csv), pick-and-place (csv), assembly drawings (PDF)
- [ ] Schematic PDF, 3D STEP
- [ ] Release notes

## Independent verification (different tool from the one that generated them)
- [ ] Every layer present and in the correct order; files named/labeled clearly
- [ ] Outline closed, dimensions correct
- [ ] Drill overlay aligns with pads; mounting holes plated/non-plated as intended
- [ ] Mask openings correct; vias tented as intended
- [ ] Paste: none on test points/fiducials/TH pads; exposed pads windowed
- [ ] Silkscreen legible and off pads
- [ ] Inner planes: correct connections/thermals; no islands
- [ ] Pick-and-place rotation/polarity preview checked at the assembler's viewer (every IC, diode, electrolytic, connector)
- [ ] Quantities: BOM designator count = PnP count

## Order
- [ ] Fab parameters: layers, thickness, copper, finish, mask/silk color, impedance control, IPC class
- [ ] Stencil ordered (if assembling yourself)
- [ ] Order recorded in `releases/rev-X/ORDER.md` (vendor, order #, date, qty, cost)
- [ ] Outputs archived in `releases/rev-X/` and committed / attached to a GitHub Release
