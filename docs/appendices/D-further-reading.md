# Appendix D — Further Reading

Ordered roughly from "read first" to "reference."

## Books

| Book | Why |
|------|-----|
| Horowitz & Hill, *The Art of Electronics* (3rd ed.) | The bible of practical circuit design. Read chapters 1–5, 8, 9, 13 alongside Part 1 of this guide |
| Eric Bogatin, *Signal and Power Integrity — Simplified* | The clearest first-principles treatment of SI/PI. Pairs with Chapters 12, 14, 16 |
| Henry Ott, *Electromagnetic Compatibility Engineering* | Grounding, stackups, EMC. Pairs with Chapters 12, 18, 19 |
| Howard Johnson & Martin Graham, *High-Speed Digital Design: A Handbook of Black Magic* | Classic, practical SI measurements and formulas |
| Rick Hartley's talks (e.g. "Grounding & Return Paths", "Control of Noise") | Free on YouTube, excellent intuition |
| Bruce Archambeault, *PCB Design for Real-World EMI Control* | Practical EMC |
| Lee Ritchey, *Right the First Time* (Vols 1–2) | Industry-grade high-speed practice |
| Walt Jung (ed.), *Op Amp Applications Handbook* (ADI) | Analog design, free PDF from ADI |
| Kester (ed.), *Data Conversion Handbook* (ADI) | ADC/DAC system design, free |
| Robert Pease, *Troubleshooting Analog Circuits* | Debugging mindset |
| Pozar, *Microwave Engineering* | RF theory reference |
| Mark I. Montrose, *Printed Circuit Board Design Techniques for EMC Compliance* | EMC-focused layout |

## Application notes (free, excellent)
- **ADI MT-031** "Grounding Data Converters and Solving the Mystery of AGND and DGND"
- **ADI MT-101** "Decoupling Techniques"
- **TI SNVA021** (AN-1149) "Layout Guidelines for Switching Power Supplies"
- **TI SLVA043** "Noise Analysis in Operational Amplifier Circuits"
- **TI SPRAAR7** "High-Speed Interface Layout Guidelines"
- **TI SNVA419** (AN-2020) "Thermal Design by Insight, Not Hindsight"
- **ST AN2867** "Oscillator design guide for STM8/STM32" and **Microchip AN826** (crystal oscillator basics)
- **ST AN4488**-type "Getting started with STM32 hardware development" notes
- **Xilinx/AMD UG583** (UltraScale PCB design guide): a masterclass in PDN and high-speed rules
- **Intel/Altera** PDN tool and board design guidelines

## Standards (know they exist; your library or employer may have access)
- IPC-2221 (generic PCB design), IPC-2222 (rigid), IPC-2223 (flex), IPC-2226 (HDI)
- IPC-2152 (current-carrying capacity)
- IPC-7351 (land patterns)
- IPC-6012 (rigid board qualification), IPC-A-600 (board acceptability), IPC-A-610 (assembly acceptability), J-STD-001 (soldering)
- IEC 61010-1, IEC 60601-1, IEC 61326-1, CISPR 11/32

## Altium resources
- Altium documentation: https://www.altium.com/documentation/altium-designer
- Altium Academy (YouTube) and the "Altium Designer training" modules
- Vendor EVM design files (often Altium format): TI, ADI, ST, NXP

## Tools
- LTspice (ADI), TINA-TI, ngspice, Qucs-S
- Saturn PCB Toolkit (free calculators), Polar Si9000 (industry impedance solver), KiCad's calculator
- Gerbv / tracespace / KiCad Gerber viewer
- NanoVNA, TinySA (low-cost RF measurement)

> App note numbers are accurate as far as I know, but vendors renumber and revise documents. Search the title if a number doesn't resolve.
