# Chapter 27 — Component Selection & Supply Chain

> **Mentor's note:** The best part in the world is useless if you can't buy it. Since the 2021–2023
> shortages, "can I get 50 of these in 3 weeks, and again next year?" has been a first-class design criterion.

---

## 27.1 Selection criteria (in order of how often they bite)
1. **Availability:** stock at multiple distributors (Digi-Key, Mouser, Arrow, LCSC for JLC assembly), more than one manufacturer.
2. **Lifecycle:** *Active*, not *NRND* (not recommended for new designs) or *EOL/Obsolete*.
3. **Meets the specs with margin** (Chapter 5: design to min/max, not typ).
4. **Package:** manufacturable by you or your assembler. (No 0.35 mm-pitch WLCSP if you're hand-assembling.)
5. **Ecosystem:** eval board, reference design, SPICE/IBIS models, app notes, community knowledge.
6. **Cost at your volume.**

## 27.2 Second sources and alternates
- Passives: always generic, with multiple approved MPNs.
- Regulators, op-amps, logic: choose **pin-compatible parts available from several vendors** where possible (e.g. industry-standard
  SOT-23-5 LDO pinouts, standard op-amp pinouts).
- MCUs: single-source by nature, so pick families with multiple package and memory options that share a footprint.
- Record alternates in **ActiveBOM** (Altium): each BOM line can hold multiple *Manufacturer Part* choices, ranked.

## 27.3 🛠️ Supply chain in Altium
- **Manufacturer Part Search panel:** search by parametrics, see stock/pricing across distributors, and place directly with models.
- **ActiveBOM (.BomDoc):** live supply-chain data per line; flags lifecycle issues and out-of-stock items; supports *Solutions* (alternates).
  Set **BOM Checks** so that "no MPN" or "lifecycle: obsolete" become errors.
- **Workspace (A365):** components have lifecycle states and where-used, so you can find which designs are affected by an EOL notice.

## 27.4 Designing for the shortage era
- Put **footprint options** in: e.g. a regulator footprint that fits two vendors' parts, or a dual footprint (SOIC/TSSOP overlap), or
  pads for either a crystal or an oscillator.
- **Buy critical parts early** for research projects: the rare MCU or sensor you designed around, plus spares for rework.
- Check **LCSC "basic parts"** if you use JLCPCB assembly: basic parts have no setup fee, "extended" parts do.

## 27.5 Environmental & compliance
- **RoHS** (restriction of hazardous substances: lead etc.), **REACH**, conflict minerals. Pretty much everything commercial is RoHS now.
- **MSL (moisture sensitivity level):** MSL 3+ parts must be baked if exposed to humidity too long before reflow, or they "popcorn" (crack).
- **Temperature grade:** commercial (0–70 °C), industrial (−40–85 °C), automotive (AEC-Q100/200, −40–125 °C). Industrial is a good default for lab equipment that might travel into the field.

**Next:** [Chapter 28 — Version Control, Revisions & Release](28-version-control-and-release.md)
