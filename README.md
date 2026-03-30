# DPS 3D System — Open-Source Parametric 3D Models for DJ Equipment

Parametric 3D models designed for professional DJ and event equipment. Built with [build123d](https://github.com/gumyr/build123d) (Python), optimized for Creality K2 Pro (300x300mm, multi-color CFS).

## What is this?

A collection of parametric, customizable 3D-printable parts for professional DJ and live event equipment:

- **Equipment docks & mounts** — Custom-fit holders for LED uplighters, speakers, controllers
- **Protective accessories** — Bumpers, covers, armor lids for mixers and controllers
- **Branding elements** — 3D logos, keychains, signage with multi-color support
- **Event tools** — Cable management, stage accessories, custom flight case inserts
- **Scanner-ready workflow** — Reverse-engineer any equipment with 3D scanner integration

## Why open-source?

The DJ and live event industry lacks custom 3D-printable solutions. Commercial products are generic. Every DJ has different equipment. This project provides **parametric models** that adapt to any setup.

## Models

| Model | Description | Multi-color |
|-------|-------------|-------------|
| `shehds_6x18w_par.py` | SHEHDS 6x18W battery LED par light (full housing) | Yes |
| `keychain_prestige.py` | Branded keychain with SVG logo import | Yes |
| `ticket_vibrato.py` | Vintage circus ticket (VIBRATO event) | Yes (bicolor) |
| `logo_svg.py` | SVG logo to 3D relief converter | Yes |
| `utils.py` | Shared utilities (show, export, SVG optimize, mesh check) | - |
| `brand.py` | Brand constants (colors, fonts, K2 Pro profile) | - |
| `build_base.py` | Base class for parametric models | - |

## Tech Stack

- **CAD Engine**: [build123d](https://github.com/gumyr/build123d) (Python, OpenCascade)
- **Viewer**: [ocp-vscode](https://github.com/bernhard-42/vscode-ocp-cad-viewer) standalone (port 3939)
- **Slicer**: OrcaSlicer / Creality Print
- **Printer**: Creality K2 Pro (300x300x300mm, CFS 4-slot multi-color)
- **Scanner**: Revopoint Inspire 2 (reverse engineering workflow)
- **AI-assisted**: Designed with Claude Code + multi-AI orchestration

## Quick Start

```bash
# Clone
git clone https://github.com/prestigesoundasbl-ai/dps-3d-system.git
cd dps-3d-system

# Setup Python venv
python3 -m venv .venv
source .venv/bin/activate
pip install build123d ocp-vscode trimesh

# Run a model
python models/keychain_prestige.py

# View in browser
python -m ocp_vscode --port 3939
# Open http://127.0.0.1:3939
```

## Printer Profile (Creality K2 Pro)

| Setting | Value |
|---------|-------|
| Build volume | 300 x 300 x 300 mm |
| Layer height (draft) | 0.28 mm |
| Layer height (quality) | 0.20 mm |
| Infill | 15-20% gyroid |
| Multi-color | CFS 4-slot (PLA, PETG, ABS, ASA) |
| Flush volume | 6 cm3 |
| Flush multiplier | 0.85 |

## Reverse Engineering Workflow

```
1. Scan equipment (Revopoint Inspire 2, dual laser mode)
2. Clean mesh (Revo Scan 5)
3. Export STL reference
4. Model parametric part in build123d
5. Add tolerances (+0.3mm for fit)
6. Slice and print (K2 Pro)
```

## Contributing

PRs welcome. If you have DJ equipment you want modeled, open an issue with:
- Equipment name and brand
- Photos from multiple angles
- Key dimensions (or we can reverse-engineer from scan)

## License

MIT License — Use freely, modify, redistribute. Attribution appreciated.

## About

Created by **DJ Prestige Sound** (Brussels, Belgium) — Professional DJ and event company with 500+ events. This project combines 3D printing, scanning, and AI to build custom solutions for the live event industry.

- Website: [djprestigesound.be](https://djprestigesound.be)
- Contact: contact@prestige-sound.be
