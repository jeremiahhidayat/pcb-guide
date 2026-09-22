# Chapter 17 — High-Speed Digital Design

> **Mentor's note:** High-speed design is mostly timing budgets and impedance control done carefully.
> Every interface spec (USB, Ethernet, DDR, PCIe) comes with a design guide. Your job is to understand
> *why* each rule exists, so you know which ones you can bend.

---

## 17.1 Differential signaling

```
 TX+ ────────────────────────► RX+        Receiver sees V+ − V−
 TX− ────────────────────────► RX−        Noise that hits both equally (common mode) cancels
```
Why it's used:
- **Noise immunity:** common-mode noise is rejected by the receiver.
- **Low EMI:** equal and opposite currents make fields that largely cancel at a distance (if the pair is balanced).
- **Smaller swing** (e.g. 350 mV LVDS) → faster, lower power.

### 🧠 Coupled vs. loosely coupled pairs
Z_diff = 2 × Z_odd. The coupling between the two traces lowers Z_odd, so tightly coupled pairs (gap ≈ width) need
**narrower traces** than two independent 50 Ω lines to hit 100 Ω. Tight coupling helps common-mode noise rejection and density,
but the pair's return current still flows mostly in the **reference plane**, not the partner trace. **A differential pair still
needs a solid reference plane.**

### Diff pair routing rules
1. **Match lengths within the pair** (intra-pair skew). Mismatch converts differential signal into common mode (EMI) and closes the eye.
   Typical: USB 2.0 ≤ 0.15 mm (~1 ps); PCIe/USB3 ≤ 0.1 mm or 5 mil. Compensate the mismatch **near where it occurs** (e.g. near the bend or pin),
   not at the far end.
2. **Keep the pair symmetric:** same vias, same layers, same bends. Route the pair through obstacles together.
3. **Constant spacing** along the route (the gap sets Z_diff).
4. **Via pairs** with ground-return vias placed symmetrically next to them.
5. **AC-coupling caps** (for PCIe, SATA, USB3) placed symmetrically, in small packages (0201/0402), with a **plane void under the pads**.
6. **Keep other signals ≥ 3–5× gap away** from the pair.

## 17.2 Common interfaces and their key rules

| Interface | Rate | Impedance | Key layout rules |
|-----------|------|-----------|------------------|
| **USB 2.0 FS** (12 Mbps) | Slow | 90 Ω diff (loose) | Honestly forgiving. Short, together |
| **USB 2.0 HS** (480 Mbps) | t_r ≈ 500 ps | **90 Ω ±15% diff** | Match within pair ≤ ~0.15 mm; minimize vias; ESD array with low C (< 1 pF) right at connector; no stubs; CM choke optional for EMC |
| **USB 3.x** (5–10 Gbps) | | 90 Ω diff (85 Ω for some) | AC caps on TX; tight skew; minimize via stubs; low-loss consideration > few inches |
| **Ethernet 10/100/1000** | 125 MHz symbols | 100 Ω diff (MDI) | Magnetics (transformer) + PHY placement per guide; **void planes under magnetics and between magnetics and RJ45**; Bob Smith termination |
| **RMII/RGMII** (MAC-PHY) | 50/125 MHz | 50 Ω SE | RGMII: clock-to-data timing (2 ns delay via PHY/MAC internal delay or trace); series termination |
| **SDIO/eMMC** | 50–200 MHz | 50 Ω SE | Series R at the host clock; length-match data to clock |
| **QSPI flash** | 50–133 MHz | 50 Ω SE | Short; series R on CLK |
| **LVDS / MIPI D-PHY** | 0.1–2.5 Gbps | 100 Ω diff | Pair skew tight; lane-to-lane matching per spec |
| **HDMI** | up to 6 Gbps/lane (2.0) | 100 Ω diff | Tight skew, ESD with low C |
| **PCIe Gen3/4** | 8/16 GT/s | 85 Ω diff | Loss budget, via stubs (back-drill), AC caps, low-loss materials for long reach |
| **DDR3/DDR4** | 800–3200 MT/s | 40–50 Ω SE, 80–100 Ω diff (clock/DQS) | **Byte-lane length matching**, fly-by for address/command, VTT termination, strict PDN. Follow the SoC's guide exactly |

## 17.3 Timing budgets and length matching

Length matching is about **arrival time**, not length. Convert with propagation delay:
```
Microstrip (ε_eff ≈ 3.0-3.3):  ~5.8–6.1 ps/mm  (≈ 147–155 ps/in)
Stripline (εr ≈ 4.0-4.3):      ~6.7–6.9 ps/mm  (≈ 170–175 ps/in)
```
**Note:** microstrip and stripline differ by ~15%. Altium's xSignals / length tuning can match by **delay** (propagation time)
instead of length when the stackup is defined. Use delay matching if nets change layers.

### Source-synchronous timing (the basis of DDR, RGMII, parallel camera buses)
```
Setup margin = T_clk/2 − t_setup − skew_budget − jitter
Skew budget includes: trace mismatch + package mismatch + driver skew
Example: DDR3-1600 DQ vs DQS: ~±5 ps trace budget per byte lane → ±0.8 mm
```
Package pin delays (**pin-package length**) matter at DDR speeds. Altium supports entering **Pin Package Length** on component pads
(Component properties → Pins → Pin Package Length) so length tuning includes it.

## 17.4 🛠️ Altium high-speed workflow

1. **Stackup and impedance profiles:** Layer Stack Manager (`D`, `K`) → **Impedance** tab → *Add Impedance Profile*:
   e.g. `DIFF90` (Differential, 90 Ω, reference layers per signal layer). The solver computes width/gap per layer.
2. **Differential pairs:** From the schematic (nets `USB_DP`/`USB_DN`... *Altium needs `_P`/`_N` suffixes*, e.g. `USB_D_P` and `USB_D_N`,
   with a Differential Pair directive), or in PCB via the **PCB panel → Differential Pairs Editor → Create From Nets** / **Create Pair**.
   Group them into a **Differential Pair Class** (`USB`).
3. **Rules:**
   - *Routing » Differential Pairs Routing* scoped `InDifferentialPairClass('USB')`: check **Use Impedance Profile** → `DIFF90`.
   - *High Speed » Matched Lengths* scoped to the class (within-pair tolerance, e.g. 0.1 mm).
   - *High Speed » Max Via Count*, *Parallel Segment* (crosstalk), *Daisy Chain Stub Length*, *Length* (min/max).
4. **Route:** **Route » Interactive Differential Pair Routing**. `Tab` for options; the pair routes together at rule gap.
5. **xSignals** (**Design » xSignals » Create xSignals**, or the xSignals Wizard for USB/DDR): define paths that span series
   resistors or AC-caps so matching is measured pad-to-pad at the true endpoints.
6. **Length tuning:** **Route » Interactive Length Tuning** (single) / **Interactive Diff Pair Length Tuning**. Adjust pattern
   (accordion, trombone, sawtooth) with `1`/`2` (spacing), `3`/`4` (amplitude) keys while tuning, and `Tab` for settings.
   Target length from rules or from a reference net.
   - **Serpentine rules:** amplitude small, spacing between loops **≥ 3–4× trace width** (otherwise the loops couple and the signal "shortcuts"),
     and in a diff pair, tune the short leg near the mismatch with small bumps.
7. **Check:** the **PCB panel → xSignals / Nets** view shows routed length and delay, and the tuning gauge shows target/actual.
   Run DRC with High Speed rules enabled.
8. **Return path:** make sure every high-speed via has a ground via within ~1 mm (a "via fence" for the pair's layer change).

## 17.5 Clocks and oscillators

- **Crystal:** place close to the MCU, keep the loop XTAL1→crystal→XTAL2 small, ground guard around it, **no signals under it** on adjacent layers.
  Load caps as computed in Chapter 5.
- **Oscillator (active):** decouple well (they have sharp current draw), series-terminate the output, route over solid ground.
- **Clock distribution:** use a buffer/fanout for multiple loads rather than a multi-drop line. Point-to-point, series terminated.
- **Jitter matters** for high-speed ADCs, SERDES reference clocks, and audio. Pick low-jitter oscillators (spec in fs–ps rms, integrated over a bandwidth).

## 17.6 High-speed connectors and cables
- Use connectors rated for the data rate, with their recommended footprint (often includes ground plane voids under signal pads).
- For cables leaving the board: common-mode chokes and ESD at the connector (Chapter 19).

## Exercises
1. Configure an impedance profile for 90 Ω differential on L1 over L2 GND with 0.1 mm prepreg (εr 4.2) in Altium. Record width and gap.
2. Route a USB 2.0 HS pair from a USB-C connector (both orientations: D+/D− appear twice on the receptacle; tie them with short, matched stubs right at the connector) to an MCU.
3. For DDR3-1600 (800 MHz clock), compute the length tolerance corresponding to ±10 ps in stripline.
   *(10 ps / 6.8 ps/mm ≈ ±1.5 mm.)*

**Next:** [Chapter 18 — Stackup Design](18-stackup-design.md)
