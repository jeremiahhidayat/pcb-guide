# Appendix B — Altium Shortcuts & Menu Map

Altium uses **menu accelerator keys**: press the underlined letters in sequence (e.g. `D`, `R` = **D**esign » **R**ules).
Shortcuts below are for Altium Designer 20–25. Some move between versions. If one doesn't work, use the menu path.
You can view or customize all shortcuts by `Ctrl`+clicking a menu item.

## Universal

| Keys | Action |
|------|--------|
| `Ctrl+F` / `J` | Find / Jump |
| `F11` | Properties panel |
| `F12` | PCB Filter panel (PCB) |
| `Shift+F` | Find Similar Objects (select a thing, find all like it) |
| `Ctrl+Z` / `Ctrl+Y` | Undo / Redo |
| `Page Up` / `Page Down` / `Ctrl+PgDn` | Zoom in / out / fit all |
| `V`, `F` | View Fit Document |
| `Q` | Toggle mm/mil (PCB). Metric vs. imperial in schematic via Properties |
| `G` | Cycle grid / grid menu |
| `Esc` / right-click | Exit current command |
| `Ctrl`+double-click | Cross-probe (schematic ↔ PCB) |

## Schematic

| Keys | Action |
|------|--------|
| `P`, `P` | Place part |
| `P`, `W` / `Ctrl+W` | Place wire |
| `P`, `N` | Place net label |
| `P`, `O` | Place power port |
| `P`, `R` | Place port |
| `P`, `S` | Place sheet symbol |
| `P`, `V`, `N` | Place Generic No ERC |
| `Space` / `X` / `Y` | Rotate / flip X / flip Y while placing |
| `Tab` | Edit properties while placing |
| `T`, `A`, `A` | Annotate schematics |
| `D`, `U` | Update PCB Document (ECO) |
| `Alt`+click on net | Highlight the net |
| Project » Validate PCB Project | Compile/ERC |

## PCB — navigation & view

| Keys | Action |
|------|--------|
| `2` / `3` | 2D / 3D view |
| `1` | Board planning mode (board shape, rigid-flex regions) |
| `L` | View Configuration (layers, colors, visibility) |
| `Shift+S` | Single-layer mode (cycles) |
| `+` / `−` (numpad) | Next / previous layer |
| `*` (numpad) | Next signal layer (adds a via while routing) |
| `Ctrl+Click` on net | Highlight net |
| `Shift+C` | Clear filter / highlight |
| `N` | Show/hide connections (ratsnest) submenu |
| `Shift+X` | Board Insight panel |
| `Ctrl+M` | Measure distance |
| `R`, `P` | Measure primitives |
| `F5` | Toggle net colors |
| `V`, `B` (View » Flip Board) | View from bottom |

## PCB — placement

| Keys | Action |
|------|--------|
| `Space` | Rotate while dragging |
| `L` (while dragging component) | Flip to other side |
| `A` | Align submenu |
| `M` | Move submenu |
| `T`, `O`, `L` | Component placement » Arrange Within Rectangle (varies) |
| `J`, `C` | Jump to component |
| `E`, `O`, `S` | Set origin |

## PCB — routing

| Keys | Action |
|------|--------|
| `Ctrl+W` | Interactive routing |
| `U`, `I` | Interactive differential pair routing |
| `U`, `M` | Interactive multi-routing |
| `Shift+A` | ActiveRoute |
| `Tab` (while routing) | Routing properties (width, via, layer) |
| `Shift+Space` | Cycle corner style |
| `Space` | Toggle corner direction |
| `Shift+R` | Cycle conflict mode (Ignore / Walkaround / Push / HugNPush) |
| `Shift+W` / `Shift+V` | Choose width / via size from preferences |
| `3` (while routing) | Cycle min/preferred/max rule width |
| `Backspace` | Remove last segment |
| `Ctrl`+click | Auto-complete route |
| `U`, `R` / `U`, `P` | Interactive length tuning / diff-pair tuning (varies by version; see Route menu) |
| `1`/`2`, `3`/`4`, `,`/`.` (while tuning) | Tuning spacing / amplitude / amplitude increment |
| `T`, `G`, `A` | Repour all polygons |
| `T`, `D` | Design Rule Check |
| `D`, `R` | Design Rules dialog |
| `D`, `K` | Layer Stack Manager |
| `D`, `C` | Classes |

## Menu map of the key tools

| Tool | Path |
|------|------|
| IPC Footprint Wizard | (PcbLib) Tools » IPC Compliant Footprint Wizard |
| Manufacturer Part Search | Panels button (bottom-right) » Manufacturer Part Search |
| Differential Pairs Editor | PCB panel » mode dropdown: Differential Pairs Editor |
| xSignals | Design » xSignals |
| Teardrops | Tools » Teardrops |
| Via stitching / shielding | Tools » Via Stitching/Shielding |
| Polygon Manager | Tools » Polygon Pours » Polygon Manager |
| Testpoint Manager | Tools » Testpoint Manager |
| Signal Integrity | Tools » Signal Integrity |
| PDN Analyzer | Tools » PDN Analyzer (extension) |
| Board cutout | Place » Board Cutout (or a region with Kind = Board Cutout) |
| Embedded Board Array | Place » Embedded Board Array/Panelize |
| Draftsman | File » New » Draftsman Document |
| Output Job | File » New » Output Job File |
| Show Differences | Project » Show Differences |
| Smart PDF | File » Smart PDF |
| Project Releaser | Project » Project Releaser |
| Scripts | File » Run Script (DelphiScript/VBScript/JScript) |
