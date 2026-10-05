# Appendix E — Finding Parts: A Search Workflow

> **Mentor's note:** A distributor search returns thousands of parts that all "match." The skill isn't
> clicking filters. It's knowing which three or four parameters actually decide whether the part works on
> *your* board, and checking those in the drawing before you fall in love with a part number.
> [Chapter 27](../part5-industry/27-component-selection-supply-chain.md) covers *what* makes a good part.
> This appendix covers *how* to find one.

---

## E.1 The workflow at a glance

```
1. Write the requirement   →  numbers, from your design notes (power budget, calcs)
2. Pick the category       →  the distributor's product category, not a keyword search
3. Filter: hard limits     →  in stock, Active, the parameters you can't compromise on
4. Sort and shortlist      →  3–5 candidates
5. Open the datasheet      →  check the "killer" parameters the filters can't see
6. Check the CAD model     →  available? verified against the drawing?
7. Record the decision     →  chosen part, alternates, and rejected parts with reasons
```

Steps 5 and 7 are the ones beginners skip. The filters only know what the distributor typed into its
database. The datasheet drawing is the truth.

## E.2 Where to search

| Site | Best for | Notes |
|------|----------|-------|
| **DigiKey** | Parametric search, the cleanest filters | Usually the best place to *find* a part, even if you buy elsewhere |
| **Mouser** | Second stock check, often has parts DigiKey doesn't | Similar filters, different category tree |
| **LCSC / JLCPCB parts library** | Parts for JLCPCB assembly | "Basic" parts have no setup fee. Check the LCSC number (e.g. `C3020560`) |
| **Octopart** | One part number → stock and price at every distributor | Use it *after* you have a candidate, to check multi-source stock |
| **Altium Manufacturer Part Search** | Searching from inside Altium, placing parts with models | Panels » Manufacturer Part Search. Data comes from the same distributors |
| **Manufacturer websites** (TI, ADI, Molex, ...) | Datasheets, drawings, app notes, eval boards, alternate variants | Their selectors are good within one brand, but they only show their own parts |

🏭 **Industry practice:** Engineers search on DigiKey or Mouser for the parametric filters, then confirm
supply with Octopart (or the company's approved-vendor list) before committing.

## E.3 Before you search: write the requirement as numbers

You can't filter on "a good LDO." Turn your design notes into a short spec first:

```
Need: 3.3 V LDO
  Output current     ≥ 0.6 A   (500 mA budget + margin)
  Dropout (max)      ≤ 0.6 V @ 0.5 A   (from the dropout-headroom calc)
  Stability          ceramic output cap OK
  Package            SOT-223 or SOT-89   (thermal calc rules out SOT-23-5)
  Input max          ≥ 6 V
```

Split it into **hard limits**, which become filters, and **preferences**, which you use to sort and choose
between the survivors.

## E.4 Filtering: how to drive the parametric search

### Go to the category first
Don't type "USB C connector" into the search box and scroll. Navigate to the category (e.g.
*Connectors » USB, DVI, HDMI Connectors*). Only a category page shows you the full parametric filter set.

### Apply filters in this order
1. **Stock status: In Stock.** Also tick **Normally Stocking** if the site offers it. No point evaluating a part you can't buy.
2. **Part Status: Active.** Exclude *NRND* (Not Recommended for New Designs), *Last Time Buy* and *Obsolete*.
3. **The hard limits from E.3**, starting with the one that removes the most parts.
4. **Package / mounting** last. It tends to be the messiest data.

### How the filter boxes combine
On DigiKey and most distributors:
- **Within one filter box, selections are OR'd.** Ticking *Horizontal* and *Vertical* shows parts that are
  either.
- **Across different filter boxes, selections are AND'd.**

So to narrow results, add filters in *more boxes*. Ticking more values in *one* box widens the results.

⚠️ **Gotcha: filter values are inconsistent.** Different manufacturers' parts get tagged differently. A
"Mounting Feature" list might include *Horizontal*, *Straddle Mount*, *Surface Mount* and *Through Hole*
side by side, even though some of those describe orientation and others describe soldering. Tick the
value that best matches what you need, then **read each result's description** to catch the rest.

### Ranges and blanks
- For numeric filters (current, voltage), select **every value above your minimum**, not just the exact one.
- Parts with a **blank** parameter often get excluded silently. If results look thin, try removing that
  filter and checking the datasheets by hand.

### Sort and shortlist
Sort by **price at your quantity** or **quantity available**. Pick 3–5 candidates and open each datasheet
in a tab.

## E.5 Check the datasheet: what the filters can't see

For each candidate, find the **mechanical drawing** (often a separate "sales drawing" or "customer
drawing" PDF linked from the product page) and the **recommended PCB layout**. Then check the killer
parameters for that part type:

| Part type | Check in the datasheet / drawing |
|-----------|----------------------------------|
| **Any connector** | Mounting style (top-mount vs. mid-mount/straddle), **recommended PCB thickness**, through-hole shell or retention legs, which pins are actually populated, board-edge position |
| **Regulator** | Dropout at *your* current (max column), output-cap stability requirements, θJA and the test board it assumes, input voltage absolute max |
| **MLCC** | DC-bias derating curve at your voltage, temperature characteristic (X7R/X5R/C0G) |
| **MOSFET / diode / TVS** | Pinout for that exact package (SOT-23 pinouts vary!), ratings at temperature, clamping voltage at your surge current |
| **Any IC** | Package variant suffix, exposed pad, errata, eval-board schematic you can copy |

Use **max/min values, not typical** (Chapter 5). And check the **exact orderable part number**. Suffixes
change plating, packaging, temperature grade or pin count.

## E.6 Check the CAD model

Before committing, check whether you can get a footprint, symbol and 3D model. Look in this order:

1. **Altium Manufacturer Part Search**, which places the part directly with models.
2. **SnapEDA (SnapMagic), Ultra Librarian, SamacSys / Component Search Engine**. Download the Altium format.
   Many distributor pages link to these ("ECAD Models").
3. **The manufacturer's site**, which usually has a STEP model even when there's no footprint.
4. **Build it yourself** from the recommended PCB layout ([Chapter 9](../part2-pcb-foundations/09-libraries-and-footprints.md)).

A missing model isn't a reason to reject a good part. Building one takes about an hour. A *downloaded*
model must still be verified against the drawing (Chapter 9.6): pad positions, pin numbering, slot sizes,
and a 1:1 print.

## E.7 Check supply

For your top pick:
- **Octopart:** stock at two or more distributors? More than one manufacturer making something pin-compatible?
- **Packaging:** *Cut Tape* or *Digi-Reel* for small quantities. *Tape & Reel* often has a minimum order of
  hundreds or thousands.
- **Assembly house:** if JLCPCB or another house will assemble it, is the part in *their* library, and is
  it a basic or an extended part?
- **Lead time** if stock is low. Buy spares of anything critical (Chapter 27.4).

## E.8 Record the decision

Fill in the **Key component selection** table in your design notes
([template](../../projects/templates/design-notes-template.md)), including the parts you **rejected**:

| Function | Part | Why this part | Alternates | Datasheet |
|----------|------|---------------|------------|-----------|
| USB-C | GCT USB4105-GF-A | Top-mount, 16-pin USB 2.0, THT shell legs, widely stocked | — | link |

> Rejected: Molex 2169900003 (mid-mount, needs 0.8 mm PCB and an edge cutout);
> Molex 1054500101 (24-pin dual-row USB 3.1, recommended PCB 0.7/0.8 mm).

Reviewers ask "why not X?" Writing down the rejects answers that before it's asked, and stops you
from re-evaluating the same parts next revision.

## E.9 Worked example: the USB-C receptacle for Project 1

**Requirement** ([Project 1](../../projects/01-usb-c-power-board/README.md)): USB-C receptacle, sink, power + optional USB 2.0 data, on a **1.6 mm** board, hand-solderable,
strong enough to survive repeated plugging.

**Search** (DigiKey, *Connectors » USB, DVI, HDMI Connectors*):

| Filter | Value | Why |
|--------|-------|-----|
| Stock / Status | In Stock, Active | Buyable |
| Connector Type | USB-C (USB TYPE-C) | |
| Gender | Receptacle | The board side |
| Standard / Specification | USB 2.0 | 16-pin parts. USB 3.x parts have 24 pins in two rows of fine-pitch pads |
| Mounting Type | Surface Mount, Right Angle (incl. "; Through Hole") | Flat at the board edge. The THT shell legs give strength |
| Mounting Feature | Horizontal | Cable plugs in parallel to the board. Not *Vertical*, *Panel*, *Cable* or *Straddle* |

**Shortlist and datasheet check:** read each description and drawing, and reject:
- **Mid-Mount / Straddle**, or "Center Height −x mm": the part sits in an edge cutout.
- **Recommended PCB thickness 0.7–0.8 mm**: the retention legs are sized for thin boards.
- **24 positions, 2 rows** unless you need USB 3.x. "24 (16+8 dummy)" is a 16-pin part and is fine.

**Model:** the GCT USB4105-GF-A has no model in Altium's content, but SnapEDA has an Altium footprint.
Download it, then verify the slotted shell pads and A/B pin numbering against GCT's drawing.

**Lesson:** two of the first three candidates passed every filter and still failed the datasheet check.
That's normal, and it's why step 5 exists.

## E.10 Common mistakes

| Mistake | Consequence | Fix |
|---------|-------------|-----|
| Searching by keyword instead of category | You miss most of the parametric filters | Navigate the category tree |
| Trusting the filters | Wrong mounting style, PCB thickness or pinout | Read the drawing for every finalist |
| Picking the cheapest part with 12 in stock | It's gone by the time you order | Prefer parts stocked at several distributors |
| Ignoring the part-number suffix | Wrong package, plating, temperature grade or reel size arrives | Copy the *exact* orderable MPN into the BOM |
| Choosing NRND parts | Redesign at the next revision | Filter Part Status = Active |
| Not recording rejects | Re-evaluating the same parts every revision | Rejected-alternates line in the design notes |

## Exercises
1. Find three 3.3 V LDOs that meet the E.3 spec. Record the dropout at 0.5 A (max column) and θJA for each.
2. Find a 10 µF 0805 MLCC and, using the manufacturer's DC-bias tool, report its effective capacitance at 3.3 V.
   Then find the smallest 10 µF part (case size) that still gives ≥ 5 µF at 3.3 V.
3. Take any connector on your board and find its recommended PCB thickness and board-edge position in the drawing.
