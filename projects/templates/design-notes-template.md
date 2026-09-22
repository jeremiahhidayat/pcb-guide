# Design Notes — <Board name> Rev <X>

**Author:** · **Reviewer(s):** · **Date started:** · **Repo tag:**

## 1. Purpose
One sentence: what this board does and for which experiment/system.

## 2. Requirements

| ID | Requirement | Value | Source / rationale | Verified by |
|----|-------------|-------|--------------------|-------------|
| R1 | Input voltage | 5 V ±5% (USB) | USB spec | Bench test |
| R2 | Measurement noise | < 2 µV rms (0.1–10 Hz) | Science need: ... | Shorted-input test |

## 3. Block diagram
(Image or ASCII.)

## 4. Power budget

| Rail | Source | Loads | Typ mA | Max mA | Regulator rating | Margin | Thermal (T_j at max T_a) |
|------|--------|-------|--------|--------|------------------|--------|--------------------------|

## 5. Key component selection

| Function | Part | Why this part | Alternates | Datasheet |
|----------|------|---------------|------------|-----------|

## 6. Calculations
For each: the equation, the numbers, the result, the chosen value, and the datasheet page it depends on.
```
e.g. LED resistor: R = (3.3 − 2.0)/2 mA = 650 Ω → 680 Ω (E12), I = 1.9 mA
```

## 7. Noise / error budget (analog boards)

| Source | Value (input-referred) | Notes |
|--------|------------------------|-------|
| Total (RSS) | | vs. requirement R2 |

## 8. Layout constraints
- Stackup:
- Impedance-controlled nets:
- Critical placement:
- Keep-outs / mechanical:

## 9. Risks and open questions

| Risk | Mitigation | Status |
|------|------------|--------|

## 10. Review log

| Date | Review | Reviewer | Findings (link) |
|------|--------|----------|-----------------|

## 11. Bring-up results (after build)

| Test | Expected | Measured | Pass? |
|------|----------|----------|-------|

## 12. Lessons learned / changes for next revision
-
