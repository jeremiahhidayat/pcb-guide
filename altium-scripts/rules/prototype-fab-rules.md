# Baseline Design Rules: Standard Prototype Fab (2–6 layers, 1 oz)

Enter these once in a template PcbDoc (**Design » Rules**), then right-click the rule tree →
**Export Rules** → save `prototype-fab.rul`. On new boards: **Import Rules** → select all → replace.

> ⚠️ Check your fab's current capabilities page. These values are deliberately a bit conservative, *inside*
> the standard capability of common prototype fabs, so you don't pay extra or lose yield.

| Category | Rule name | Scope (query) | Settings |
|----------|-----------|---------------|----------|
| Electrical | Clearance | All / All | 0.15 mm (track, pad, via); 0.2 mm polygon-to-anything |
| Electrical | ShortCircuit | All / All | Not allowed |
| Electrical | UnRoutedNet | All | Check |
| Routing | Width | All | Min 0.15, Pref 0.20, Max 3.0 mm |
| Routing | Width_PWR | `InNetClass('PWR')` | Min 0.30, Pref 0.50, Max 5.0 mm |
| Routing | RoutingVias | All | Hole 0.30 mm, Diameter 0.60 mm (min 0.25 / 0.50) |
| Routing | DiffPairs_USB | `InDifferentialPairClass('USB')` | Use impedance profile `DIFF90` |
| Routing | RoutingCorners | All | 45°, setback 0.1–1 mm |
| Mask | SolderMaskExpansion | All | 0.05 mm; vias tented top + bottom |
| Mask | PasteMaskExpansion | All | 0 mm |
| Plane | PlaneConnect | All | Relief, 4 conductors, 0.25 mm width, 0.25 mm air gap |
| Plane | PlaneClearance | All | 0.25 mm |
| Plane | PolygonConnect | All | Relief, 4 × 0.25 mm, 90° |
| Plane | PolygonConnect_Direct | `IsPad and HasFootprint('*EP*')` (adapt) | Direct connect for thermal/power pads, priority above the general rule |
| Manufacturing | MinimumAnnularRing | All | 0.13 mm |
| Manufacturing | AcuteAngle | All | 90° minimum |
| Manufacturing | HoleSize | All | 0.2 – 6.3 mm |
| Manufacturing | HoleToHoleClearance | All / All | 0.25 mm |
| Manufacturing | MinimumSolderMaskSliver | All / All | 0.10 mm |
| Manufacturing | SilkToSolderMaskClearance | All / All | 0.05 mm (clip silk) |
| Manufacturing | SilkToSilkClearance | All / All | 0 – 0.05 mm |
| Manufacturing | NetAntennae | All | Tolerance 0 mm |
| Manufacturing | BoardOutlineClearance | All | 0.3 mm copper-to-edge |
| Placement | ComponentClearance | All / All | 0.2 mm, 3D check |
| High Speed | MatchedLengths_USB | `InDifferentialPairClass('USB')` | Within-pair tolerance 0.15 mm |
| High Speed | MaxViaCount_Fast | `InNetClass('FAST')` | 2 |
