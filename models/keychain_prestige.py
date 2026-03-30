"""
Porte-clés Prestige Sound V4 — Plaque de fond + Logo en relief + Anse
======================================================================
- Plaque noire arrondie = fond qui tient tout ensemble
- Logo SVG en relief or par-dessus
- Petite anse en haut avec trou pour anneau métal
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from build123d import *

PROJECT_ROOT = "/Users/prestigesound/Projects/3D/Active/DPS_3D_SYSTEM"
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'output')
LOGO_SVG = os.path.join(PROJECT_ROOT, "models", "assets", "logo-prestige-sound-v2.svg")

# Dimensions
TARGET_WIDTH = 50.0     # largeur du logo
BASE_THICK = 2.0        # plaque de fond noire
LOGO_RELIEF = 1.5       # relief logo or (bien visible)
PLATE_MARGIN = 2.5      # marge autour du logo
PLATE_CORNER_R = 3.0    # coins arrondis plaque

# Anse pour anneau
TAB_WIDTH = 10.0        # largeur de l'anse
TAB_HEIGHT = 10.0       # hauteur de l'anse au-dessus de la plaque
RING_HOLE_DIA = 4.0     # trou pour anneau métal


def build():
    # 1. Import SVG + mesures
    print("   Import SVG...")
    faces = import_svg(LOGO_SVG)
    all_bb = [f.bounding_box() for f in faces]
    min_x = min(bb.min.X for bb in all_bb)
    min_y = min(bb.min.Y for bb in all_bb)
    max_x = max(bb.max.X for bb in all_bb)
    max_y = max(bb.max.Y for bb in all_bb)
    svg_w, svg_h = max_x - min_x, max_y - min_y
    cx, cy = (min_x + max_x) / 2, (min_y + max_y) / 2

    s = TARGET_WIDTH / svg_w
    final_w = svg_w * s
    final_h = svg_h * s
    print(f"   Logo : {final_w:.0f} x {final_h:.0f}mm")

    # Dimensions plaque
    plate_w = final_w + 2 * PLATE_MARGIN
    plate_h = final_h + 2 * PLATE_MARGIN
    print(f"   Plaque : {plate_w:.0f} x {plate_h:.0f}mm")

    # =============================================
    # 2. PLAQUE DE FOND (noire) — disque rond
    # =============================================
    DISC_RADIUS = max(plate_w, plate_h) / 2 + 1.0  # rayon du disque

    with BuildPart() as base_builder:
        # Disque rond
        with BuildSketch():
            Circle(DISC_RADIUS)
        extrude(amount=BASE_THICK)

        # Bordure en relief (anneau)
        with BuildSketch(Plane.XY.offset(BASE_THICK)):
            Circle(DISC_RADIUS)
            Circle(DISC_RADIUS - 1.5, mode=Mode.SUBTRACT)
        extrude(amount=0.8, mode=Mode.ADD)

        # Anse en haut (petit disque qui dépasse)
        with BuildSketch():
            with Locations([(0, DISC_RADIUS + TAB_HEIGHT / 2 - 2)]):
                RectangleRounded(TAB_WIDTH, TAB_HEIGHT, TAB_WIDTH / 2 - 0.1)
        extrude(amount=BASE_THICK, mode=Mode.ADD)

        # Trou pour anneau métal dans l'anse
        with BuildSketch(Plane.XY.offset(BASE_THICK)):
            with Locations([(0, DISC_RADIUS + TAB_HEIGHT / 2 - 2)]):
                Circle(RING_HOLE_DIA / 2)
        extrude(amount=-BASE_THICK, mode=Mode.SUBTRACT)

    base_part = base_builder.part
    print(f"   ✅ Plaque + anse construite")

    # =============================================
    # 3. LOGO EN RELIEF (or) — par-dessus la plaque
    # =============================================
    from OCP.gp import gp_Vec, gp_Trsf
    from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform

    print("   Extrusion logo...")
    logo_parts = []
    for face in faces:
        try:
            moved = face.moved(Location((-cx, -cy, 0)))
            scaled = moved.scale(s)
            # PAS de mirror (casse le Z) — on extrude direct
            solid = extrude(scaled, LOGO_RELIEF)
            # Translater juste au-dessus de la plaque
            trsf = gp_Trsf()
            trsf.SetTranslation(gp_Vec(0, 0, BASE_THICK))
            builder = BRepBuilderAPI_Transform(solid.wrapped, trsf, True)
            builder.Build()
            logo_parts.append(Solid(builder.Shape()))
        except Exception:
            continue

    print(f"   {len(logo_parts)}/{len(faces)} faces OK")

    if not logo_parts:
        print("   ⚠️ Aucun logo")
        return base_part, None

    # Compound au lieu de fuse (préserve les positions)
    logo = Compound(children=logo_parts)
    bb = logo.bounding_box()
    print(f"   ✅ Logo Compound: Z={bb.min.Z:.1f}→{bb.max.Z:.1f}")

    return base_part, logo


def export_all():
    dirs = {'stl': os.path.join(OUTPUT_DIR, 'stl'), 'step': os.path.join(OUTPUT_DIR, 'step')}
    for d in dirs.values():
        os.makedirs(d, exist_ok=True)

    print(f"🔨 Porte-clés Prestige Sound V4")
    base, logo = build()

    # Base noire (Slot 1)
    stl_base = os.path.join(dirs['stl'], 'keychain_prestige_base.stl')
    export_stl(base, stl_base, angular_tolerance=0.3, tolerance=0.05)
    print(f"  ✅ base.stl ({os.path.getsize(stl_base)/1024:.0f} KB) — plaque noire + anse")

    if logo:
        # Logo or (Slot 2)
        stl_gold = os.path.join(dirs['stl'], 'keychain_prestige_gold.stl')
        export_stl(logo, stl_gold, angular_tolerance=0.3, tolerance=0.05)
        print(f"  ✅ gold.stl ({os.path.getsize(stl_gold)/1024:.0f} KB) — logo or en relief")

        # Combiné = écrire les 2 meshes dans le même STL
        stl_comb = os.path.join(dirs['stl'], 'keychain_prestige_combined.stl')
        with open(stl_comb, 'wb') as f:
            # Lire les 2 STL binaires et les concaténer
            # Plus simple : exporter via Mesher
            pass
        from OCP.StlAPI import StlAPI_Writer
        from OCP.BRep import BRep_Builder
        from OCP.TopoDS import TopoDS_Compound
        builder = BRep_Builder()
        compound = TopoDS_Compound()
        builder.MakeCompound(compound)
        builder.Add(compound, base.wrapped)
        builder.Add(compound, logo.wrapped)
        writer = StlAPI_Writer()
        writer.ASCIIMode = False
        writer.Write(compound, stl_comb)
        print(f"  ✅ combined.stl ({os.path.getsize(stl_comb)/1024:.0f} KB)")

        step = os.path.join(dirs['step'], 'keychain_prestige.step')
        from build123d import Compound
        cmpd = Compound(children=[base, logo])
        export_step(cmpd, step)
        print(f"  ✅ STEP")

    print(f"\n🎯 CONCEPT :")
    print(f"   Plaque noire arrondie = fond solide")
    print(f"   Logo Prestige Sound en relief or ({LOGO_RELIEF}mm)")
    print(f"   Petite anse en haut avec trou Ø{RING_HOLE_DIA}mm pour anneau métal")
    print(f"   K2 Pro CFS : Slot1=Noir mat, Slot2=Or Silk")


if __name__ == '__main__':
    export_all()
