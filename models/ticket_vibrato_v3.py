#!/usr/bin/env python3
"""
Ticket Vintage — VIBRATO / UN TOUR DE MANÈGE
VERSION 3 : BICOLORE + CHAPITEAU SVG RÉEL
200mm x 100mm — Impression 3D (Creality K2 Pro CFS)
"""
from build123d import *
from ocp_vscode import show, Camera
from OCP.gp import gp_Trsf, gp_Vec, gp_Pnt, gp_Ax1, gp_Dir
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
import math

# ============================
# PARAMÈTRES
# ============================
W = 200.0
H = 100.0
T = 3.0
TEXT_R = 1.5
BORDER_R = 1.0
CR = 5.0
MARGIN = 7.0
FRAME_T = 2.0
LEFT_W = 50.0
DIV_X = -W/2 + LEFT_W

PERF_R = 2.5
PERF_MINI = 1.5
PERF_N = 10

FONT = "Copperplate"
SVG_PATH = "/tmp/chapiteau_custom.svg"

# Positions texte
UN_TOUR_Y = 30
DE_MANEGE_Y = -28
TENT_CY = 2
TENT_WIDTH = 48  # largeur cible du chapiteau en mm (doublé)

# ============================
# HELPERS
# ============================
def star_pts(cx, cy, R=5.0, r=2.0, n=5):
    pts = []
    for i in range(2 * n):
        angle = math.pi / 2 + i * math.pi / n
        radius = R if i % 2 == 0 else r
        pts.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
    return pts

def transform_svg_face(face, target_w, target_cx, target_cy, flip_y=True):
    """Scale, flip Y (SVG→CAD), et positionne une face SVG"""
    bb = face.bounding_box()
    cx = (bb.min.X + bb.max.X) / 2
    cy = (bb.min.Y + bb.max.Y) / 2
    w = bb.max.X - bb.min.X
    scale = target_w / w

    # 1. Translate center → origin
    t1 = gp_Trsf()
    t1.SetTranslation(gp_Vec(-cx, -cy, 0))
    shape = BRepBuilderAPI_Transform(face.wrapped, t1, True).Shape()

    # 2. Scale
    t2 = gp_Trsf()
    t2.SetScale(gp_Pnt(0, 0, 0), scale)
    shape = BRepBuilderAPI_Transform(shape, t2, True).Shape()

    # 3. Flip Y (SVG Y pointe vers le bas, CAD Y vers le haut)
    if flip_y:
        t3 = gp_Trsf()
        t3.SetMirror(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)))  # miroir axe X → flip Y
        shape = BRepBuilderAPI_Transform(shape, t3, True).Shape()

    # 4. Translate → position cible
    t4 = gp_Trsf()
    t4.SetTranslation(gp_Vec(target_cx, target_cy, 0))
    shape = BRepBuilderAPI_Transform(shape, t4, True).Shape()

    # 5. Translate → Z = T (sur la base)
    t5 = gp_Trsf()
    t5.SetTranslation(gp_Vec(0, 0, T))
    shape = BRepBuilderAPI_Transform(shape, t5, True).Shape()

    return Face(shape)

# ============================
# CALCULS SECTIONS
# ============================
lx0 = -W/2 + MARGIN + FRAME_T + 1
lx1 = DIV_X - 3
lcx = (lx0 + lx1) / 2
liw = lx1 - lx0
lih = H - 2 * (MARGIN + FRAME_T + 4)

rx0 = DIV_X + 4
rx1 = W/2 - MARGIN - FRAME_T - 1
rcx = (rx0 + rx1) / 2
riw = rx1 - rx0
rih = H - 2 * (MARGIN + FRAME_T + 4)

y_start = -H/2 + CR + PERF_R + 3
y_end = H/2 - CR - PERF_R - 3
perf_spacing = (y_end - y_start) / (PERF_N - 1)

bw = W - 2 * MARGIN
bh = H - 2 * MARGIN
div_h = bh - 2 * FRAME_T - 8

print(f"Layout: UN TOUR y={UN_TOUR_Y}, Chapiteau cy={TENT_CY}, DE MANEGE y={DE_MANEGE_Y}")

# ============================
# IMPORT + TRANSFORM SVG CHAPITEAU
# ============================
print("Importing circus tent SVG...")
svg_faces = import_svg(SVG_PATH)
tent_face = max(svg_faces, key=lambda f: f.area)
bb_orig = tent_face.bounding_box()
print(f"  SVG: {len(svg_faces)} faces, principale: {bb_orig.max.X - bb_orig.min.X:.0f} x {bb_orig.max.Y - bb_orig.min.Y:.0f}")
tent_transformed = transform_svg_face(tent_face, TENT_WIDTH, rcx, TENT_CY, flip_y=False)
bb_t = tent_transformed.bounding_box()
print(f"  Transformé:   {bb_t.max.X - bb_t.min.X:.1f} x {bb_t.max.Y - bb_t.min.Y:.1f} mm")
print(f"  Position:     ({bb_t.min.X:.1f},{bb_t.min.Y:.1f}) → ({bb_t.max.X:.1f},{bb_t.max.Y:.1f})")
print(f"  Z offset:     {bb_t.min.Z:.1f}")

# ============================================================
# PARTIE 1 : BASE (OR / GOLD)
# ============================================================
print("\nBuilding BASE (gold)...")

with BuildPart() as base_part:
    with BuildSketch():
        RectangleRounded(W, H, CR)
    extrude(amount=T)

    for i in range(PERF_N):
        y = y_start + i * perf_spacing
        with BuildSketch():
            with Locations([(-W/2, y)]):
                Circle(PERF_R)
        extrude(amount=T, mode=Mode.SUBTRACT)

    for i in range(PERF_N):
        y = y_start + i * perf_spacing
        with BuildSketch():
            with Locations([(W/2, y)]):
                Circle(PERF_R)
        extrude(amount=T, mode=Mode.SUBTRACT)

    tear_n = 12
    tear_sp = (y_end - y_start) / (tear_n - 1)
    for i in range(tear_n):
        y = y_start + i * tear_sp
        with BuildSketch():
            with Locations([(DIV_X, y)]):
                Circle(PERF_MINI)
        extrude(amount=T, mode=Mode.SUBTRACT)

gold = base_part.part
print(f"  OK")

# ============================================================
# PARTIE 2 : TEXTE + BORDURES + CHAPITEAU SVG (NOIR)
# ============================================================
print("Building TEXT + CHAPITEAU SVG (black)...")

with BuildPart() as text_part:

    # Cadre extérieur
    with BuildSketch(Plane.XY.offset(T)):
        RectangleRounded(bw, bh, CR - 1)
        RectangleRounded(bw - 2 * FRAME_T, bh - 2 * FRAME_T,
                         max(CR - 2, 1), mode=Mode.SUBTRACT)
    extrude(amount=BORDER_R)

    # Double cadre décoratif
    with BuildSketch(Plane.XY.offset(T)):
        RectangleRounded(bw - 6, bh - 6, max(CR - 2, 1))
        RectangleRounded(bw - 8, bh - 8, max(CR - 3, 0.5), mode=Mode.SUBTRACT)
    extrude(amount=BORDER_R * 0.5)

    # Séparateur vertical
    with BuildSketch(Plane.XY.offset(T)):
        with Locations([(DIV_X, 0)]):
            Rectangle(1.5, div_h)
    extrude(amount=BORDER_R)

    # Cadre intérieur gauche
    with BuildSketch(Plane.XY.offset(T)):
        with Locations([(lcx, 0)]):
            RectangleRounded(liw + 2, lih + 2, 1.5)
            RectangleRounded(liw - 2, lih - 2, 0.5, mode=Mode.SUBTRACT)
    extrude(amount=BORDER_R * 0.5)

    # Cadre intérieur droit
    with BuildSketch(Plane.XY.offset(T)):
        with Locations([(rcx, 0)]):
            RectangleRounded(riw + 2, rih + 2, 1.5)
            RectangleRounded(riw - 2, rih - 2, 0.5, mode=Mode.SUBTRACT)
    extrude(amount=BORDER_R * 0.5)

    # VIBRATO vertical
    with BuildSketch(Plane.XY.offset(T)):
        with Locations([(lcx, 0)]):
            Text("VIBRATO", font_size=10, font=FONT,
                 align=(Align.CENTER, Align.CENTER), rotation=90)
    extrude(amount=TEXT_R)

    # UN TOUR
    with BuildSketch(Plane.XY.offset(T)):
        with Locations([(rcx, UN_TOUR_Y)]):
            Text("UN TOUR", font_size=16, font=FONT,
                 align=(Align.CENTER, Align.CENTER))
    extrude(amount=TEXT_R)

    # DE MANEGE
    with BuildSketch(Plane.XY.offset(T)):
        with Locations([(rcx, DE_MANEGE_Y)]):
            Text("DE MANEGE", font_size=16, font=FONT,
                 align=(Align.CENTER, Align.CENTER))
    extrude(amount=TEXT_R)

    # ═══ CHAPITEAU SVG (extrudé directement depuis la face transformée) ═══
    extrude(tent_transformed, amount=TEXT_R)

    # Étoiles coins section droite
    for sx, sy in [
        (rcx - riw/2 + 10, rih/2 - 6),
        (rcx + riw/2 - 10, rih/2 - 6),
        (rcx - riw/2 + 10, -rih/2 + 6),
        (rcx + riw/2 - 10, -rih/2 + 6),
    ]:
        with BuildSketch(Plane.XY.offset(T)):
            Polygon(*star_pts(sx, sy, R=4.0, r=1.6))
        extrude(amount=TEXT_R)

    # Étoiles flanquant UN TOUR
    for sx, sy in [(rcx - 35, UN_TOUR_Y), (rcx + 35, UN_TOUR_Y)]:
        with BuildSketch(Plane.XY.offset(T)):
            Polygon(*star_pts(sx, sy, R=3.0, r=1.2))
        extrude(amount=TEXT_R)

black = text_part.part
print(f"  OK")

# ============================================================
# EXPORT
# ============================================================
export_stl(gold, "/tmp/ticket_v3_gold.stl", tolerance=0.05, angular_tolerance=0.5)
export_stl(black, "/tmp/ticket_v3_black.stl", tolerance=0.05, angular_tolerance=0.5)

combined = gold.fuse(black)
export_stl(combined, "/tmp/ticket_v3_combined.stl", tolerance=0.05, angular_tolerance=0.5)

bb = combined.bounding_box()
dims = f"{bb.max.X - bb.min.X:.1f} x {bb.max.Y - bb.min.Y:.1f} x {bb.max.Z - bb.min.Z:.1f}"

print(f"\n{'='*55}")
print(f"  ✅ TICKET VIBRATO V3 — CHAPITEAU SVG RÉEL")
print(f"  Dimensions: {dims} mm")
print(f"  🟡 Base OR    : /tmp/ticket_v3_gold.stl")
print(f"  ⚫ Texte NOIR  : /tmp/ticket_v3_black.stl")
print(f"  🔗 Combiné    : /tmp/ticket_v3_combined.stl")
print(f"{'='*55}")

show(
    gold, black,
    names=["Base (OR)", "Texte + Chapiteau SVG (NOIR)"],
    colors=["#C9A962", "#1A1A1A"],
    reset_camera=Camera.RESET
)
