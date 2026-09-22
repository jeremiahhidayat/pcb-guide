# Guided Projects

Three boards, each building on the last. Each project has a spec, design decisions to make (with
the reasoning a senior engineer would expect you to write down), and acceptance tests. They're specs
and walkthroughs, not finished Altium files, because the learning is in doing the design yourself.

| # | Project | Layers | New skills |
|---|---------|--------|------------|
| 1 | [USB-C Power & LED Board](01-usb-c-power-board/README.md) | 2 | Full flow: schematic → footprints → layout → outputs → bring-up |
| 2 | [Sensor DAQ Board](02-sensor-daq-board/README.md) | 4 | MCU, precision ADC, analog front end, grounding, noise budget, bring-up scripting |
| 3 | [High-Speed USB + Buck Board](03-high-speed-usb-board/README.md) | 4–6 | Controlled impedance, diff pairs, buck hot loop, EMC, stackup with the fab |

Use [`templates/design-notes-template.md`](templates/design-notes-template.md) for every project.

**Workflow per project:**
1. Copy the template into `your-project/docs/design-notes.md`.
2. Fill in requirements and calculations *before* opening Altium.
3. Design in Altium and review with the [checklists](../checklists/).
4. Order, bring up, and log the results.
5. Compare measured vs. predicted, and write down what you learned.
