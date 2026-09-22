# Chapter 23 — Design Reviews

> **Mentor's note:** A review is not a test you pass. It's the cheapest bug-finding tool in hardware.
> Finding a bug in review costs an hour. Finding it on the fabricated board costs a respin: weeks and
> thousands of dollars. Ask for reviews early and often, and give them generously.

---

## 23.1 The review cadence used in industry

| Review | When | Focus | Artifacts |
|--------|------|-------|-----------|
| **Concept / architecture review** | Before schematic | Block diagram, power tree, part choices, interfaces, risks | Block diagram, power budget, key parts list |
| **Schematic review** | Schematic "complete" | Correctness, protection, calculations | PDF schematic + design-notes calcs + BOM |
| **Placement review** | After placement, before routing | Mechanical fit, zones, critical parts placement, thermal | PCB screenshots/3D, placement PDF |
| **Layout review** | Routing complete, DRC clean | SI/PI/EMC, DFM, silkscreen | Gerbers + layer PDFs, DRC report |
| **Release review (fab release)** | Before ordering | Outputs complete and consistent | Release package |
| **Post-mortem / bring-up review** | After first boards | What went wrong/right; feed the checklists | Bring-up log |

The **placement review** is the one juniors skip and seniors insist on. Most layout problems are placement problems, and they're
cheap to fix before routing and expensive after.

## 23.2 How to run a review

1. **Send materials 2+ days early** (PDF schematic, design notes, and for layout, a viewer link or PDFs of each layer).
2. **Use checklists** ([`checklists/`](../../checklists/)) so reviewers cover the basics and spend their thinking on the hard parts.
3. **Track every comment** in a spreadsheet or issue tracker: ID, location, description, severity, owner, resolution. Close every one explicitly
   ("fixed", "won't fix because...").
4. **Walk through the design by function**, not sheet by sheet: "Let's follow power from the connector to every rail." "Let's trace the ADC data path."
5. **The designer explains; reviewers question.** Explaining your own design out loud catches bugs too.

🛠️ **Altium tools for reviews:**
- **Altium 365 / A365 Viewer:** web-based schematic and PCB viewer with **comments pinned to objects**, so reviewers don't need a license.
- **Smart PDF** (File » Smart PDF): exports schematic + PCB with net/component bookmarks. Works for anyone.
- **Project » Show Differences** (compare two revisions of schematic/PCB). Essential for reviewing changes.
- **Reports » Board Information / Bill of Materials / Net Status.**

## 23.3 Severity scale (use one)
- **S1 — Board won't work / safety:** must fix before release.
- **S2 — Degraded performance / risk:** should fix.
- **S3 — Improvement / cosmetic:** fix if cheap.

## 23.4 What senior reviewers actually look for (the "sniff test")
- A power budget that adds up, and a thermal calc for every regulator and power device.
- Every connector: pinout checked against the mating part, ESD, keying, current rating.
- Every IC: all power/ground pins connected, exposed pad connected, decoupling present, strap pins defined.
- Every interface: voltage levels compatible, pull-ups present once (not zero times and not three).
- Reset and power sequencing, and what happens during power-up, power-down and brown-out.
- **Debuggability:** test points, debug header, LEDs, 0 Ω jumpers to isolate sections, spare GPIOs brought out.
- **What happens if the user plugs things in wrong?** (reverse polarity, wrong voltage, hot-plugging)
- Layout: hot loops, return paths, plane integrity, and what's under the crystal and the ADC.

## 23.5 Self-review before anyone else sees it
- Print the schematic. Go through it with a highlighter, marking every net once you've checked it.
- **Walk away for a day**, then review again.
- Run the checklist yourself first. Reviewers should find *design* issues, not missing decoupling caps.

**Next:** [Chapter 24 — DFM, DFA and DFT](24-dfm-dfa-dft.md)
