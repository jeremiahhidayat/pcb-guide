# Chapter 28 — Version Control, Revisions & Release Process

> **Mentor's note:** Six months from now someone (probably you) will ask, "which version of the board is
> in the setup that took the data for Figure 3?" Plan now so you can answer that.

---

## 28.1 Git for Altium projects

Altium files are binary (SchDoc/PcbDoc can be ASCII-saved, but diffs still aren't meaningful), so:
- **Commit often, with descriptive messages**: "Swap U3 LDO for TPS7A20 (lower noise); update C12 to 1 µF per datasheet."
- Use Altium's **Project » Show Differences** to review changes between commits (it compares documents semantically).
- **Don't let two people edit the same PcbDoc in parallel.** Binary files can't merge. Use git LFS locks, or agree who "owns" the layout.
- Use the repo's [`.gitignore`](../../.gitignore) to exclude history, previews and generated outputs.
- **Git LFS** is useful if files are large (STEP models, big PcbDocs): `git lfs track "*.PcbDoc" "*.step"`.

Altium supports git directly: **Projects panel → right-click → History & Version Control** (commit, push, and see status icons).

## 28.2 Revision scheme
- **Board revision letters:** Rev A, B, C... for fabricated hardware changes. Rev A is the first build (some use Rev 0 / X1, X2 for prototypes).
- **Tag releases in git:** `git tag -a myboard-revA -m "Released to fab 2026-10-01"`.
- **Firmware and hardware compatibility:** have firmware read a **hardware revision ID** (resistor-divider on an ADC pin, or GPIO straps)
  so one firmware image can support multiple board revisions.

## 28.3 Engineering Change Orders (ECO) in a lab
Keep `CHANGELOG.md` in the hardware folder:
```markdown
## Rev B (2026-11-15)
- FIX: Swapped USB D+/D- at J3 (bring-up issue #1)
- FIX: C22 changed 10 µF 0402 → 10 µF 0805 X7R (DC-bias derating caused LDO instability)
- ADD: Test points on VREF, AIN0
- CHANGE: Moved buck converter U5 20 mm further from AFE (noise floor improved in rev A rework test)
```
Each entry traces back to a bring-up log entry (Chapter 26).

## 28.4 The release process (lightweight version of an industry process)
1. Freeze design → all review comments closed.
2. DRC/ERC clean (validation outputs pass).
3. Generate outputs from a **clean checkout of the tagged commit**.
4. Independent Gerber/BOM check (Chapter 25 checklist).
5. Archive outputs in `releases/rev-X/` (commit them, or attach them to a GitHub Release).
6. Order. Record the order number, fab, date, and quantities in `releases/rev-X/ORDER.md`.

🏭 **Industry practice:** A PLM system (Arena, Windchill, Altium 365 + Octopart) holds the released data, with approvals by signature.
The principle is the same: **released data is immutable and traceable.**

**Next:** [Chapter 29 — Safety, Compliance, Creepage & Clearance](29-safety-and-compliance.md)
