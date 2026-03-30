# Contributing to DPS 3D System

Thanks for your interest in contributing! This project aims to build the largest open-source collection of parametric 3D models for DJ and live event equipment.

## How to Contribute

### Add a New Model

1. Fork the repo
2. Create your model in the appropriate folder:
   - `models/dj_equipment/` — Equipment accessories (mounts, covers, adapters)
   - `models/dj_booth/` — DJ booth components (panels, hinges, brackets)
   - `models/branded/` — Branded items (logos, keychains, nameplates)
   - `models/event/` — Event items (table numbers, place cards, stands)
   - `models/accessories/` — General accessories
3. Use build123d (Python) for parametric models
4. Include dimensions as parameters at the top of the file
5. Add a docstring explaining what the model is for
6. Submit a PR

### Request a Model

Open an issue with:
- Equipment name and brand
- Photos from multiple angles (front, back, top, bottom)
- Key dimensions (width, height, depth in mm)
- What you need (mount, cover, adapter, dock?)

### Report Issues

- STL export problems
- Dimension errors
- Compatibility issues with specific printers

## Code Style

- Python 3.10+
- build123d for CAD operations
- Parameters as constants at file top
- Dimensions in millimeters
- Export to STL (and STEP when possible)

## Supported Equipment Brands

We welcome models for any DJ/event equipment:
- Controllers: Pioneer, Denon, Reloop, Native Instruments, Hercules
- Mixers: Allen & Heath, Soundcraft, Behringer, Mackie
- Speakers: Bose, EV, JBL, LD Systems, QSC, RCF
- Lighting: Chauvet, ADJ, SHEHDS, JB Systems, Stairville
- Microphones: Shure, Sennheiser, AKG, Audio-Technica

## License

All contributions are under MIT License.
