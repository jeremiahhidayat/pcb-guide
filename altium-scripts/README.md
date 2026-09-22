# Altium Scripts

DelphiScript utilities for Altium Designer. Altium's scripting engine gives you the same object model the
tool uses internally (`PCBServer`, `SchServer`, board iterators), so small scripts can automate repetitive
checks and reports.

| File | Entry procedure | Purpose |
|------|-----------------|---------|
| `ViaReport.pas` | `RunViaReport` | CSV of all vias (net, position, drill, span) + drill-size histogram. Helps reduce drill sizes and review via usage |
| `NetLengthReport.pas` | `RunNetLengthReport` | CSV of routed track+arc length per net, for reviews or timing spreadsheets |
| [`rules/prototype-fab-rules.md`](rules/prototype-fab-rules.md) | — | The baseline rule set from Chapter 7, plus how to export/import `.rul` files |

## How to run a script
1. **File » New » Project » Script Project** (`.PrjScr`), then right-click it and **Add Existing to Project** → the `.pas` file.
2. Make the target `.PcbDoc` the focused document.
3. **File » Run Script…** → pick the script → pick the entry procedure → **OK**.

## Writing your own: the pattern
```pascal
Board := PCBServer.GetCurrentPCBBoard;              // the focused board
Iterator := Board.BoardIterator_Create;             // walk objects
Iterator.AddFilter_ObjectSet(MkSet(eTrackObject));  // kinds: eViaObject, ePadObject, eComponentObject...
Iterator.AddFilter_LayerSet(MkSet(eTopLayer));      // layers: AllLayers, SignalLayers...
Iterator.AddFilter_Method(eProcessAll);
Obj := Iterator.FirstPCBObject;
While Obj <> Nil Do Begin { ... } Obj := Iterator.NextPCBObject; End;
Board.BoardIterator_Destroy(Iterator);
```
- Coordinates are internal units. Convert with `CoordToMMs()` / `CoordToMils()` / `MMsToCoord()`.
- If you **modify** objects, wrap changes in `PCBServer.PreProcess` / `PCBServer.PostProcess` and call
  `Obj.BeginModify` / `Obj.EndModify` so undo and the database stay consistent.
- Reference: Altium's "Scripting API" documentation (PCB API, Schematic API) and the example scripts Altium publishes.

> These scripts only *read* the design. They're written against the documented PCB API but haven't been run
> on your Altium version. If a property name differs, the script editor points to the offending line.
