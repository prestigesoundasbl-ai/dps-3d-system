#!/usr/bin/env python3
"""
Ticket Vintage — VIBRATO / UN TOUR DE MANÈGE
VERSION BICOLORE : base OR + texte/bordures NOIR
200mm x 100mm — Impression 3D (Creality K2 Pro CFS)
"""
from build123d import *
from ocp_vscode import show, Camera
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

# ============================
# ÉTOILE 5 BRANCHES
# ============================
def star_pts(cx, cy, R=5.0, r=2.0, n=5):
    pts = []
    for i in range(2 * n):
        angle = math.pi / 2 + i * math.pi / n
        radius = R if i % 2 == 0 else r
        pts.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
    return pts

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
perf_spacing = (y_end - y_start) / (PERF_N - 1) if PERF_N > 1 else 0

bw = W - 2 * MARGIN
bh = H - 2 * MARGIN
div_h = bh - 2 * FRAME_T - 8

# ============================================================
# PARTIE 1 : BASE (OR / GOLD) — plaque + perforations
# ============================================================
print("Building BASE (gold)...")

with BuildPart() as base_part:

    # Base rectangulaire arrondie
    with BuildSketch():
        RectangleRounded(W, H, CR)
    extrude(amount=T)

    # Perforations bord gauche
    for i in range(PERF_N):
        y = y_start + i * perf_spacing
        with BuildSketch():
            with Locations([(-W/2, y)]):
                Circle(PERF_R)
        extrude(amount=T, mode=Mode.SUBTRACT)

    # Perforations bord droit
    for i in range(PERF_N):
        y = y_start + i * perf_spacing
        with BuildSketch():
            with Locations([(W/2, y)]):
                Circle(PERF_R)
        extrude(amount=T, mode=Mode.SUBTRACT)

    # Perforations tear-off (ligne séparateur)
    tear_n = 12
    tear_spacing = (y_end - y_start) / (tear_n - 1) if tear_n > 1 else 0
    for i in range(tear_n):
        y = y_start + i * tear_spacing
        with BuildSketch():
            with Locations([(DIV_X, y)]):
                Circle(PERF_MINI)
        extrude(amount=T, mode=Mode.SUBTRACT)

gold = base_part.part
print(f"  Base: {gold.bounding_box().max.X - gold.bounding_box().min.X:.0f} x {gold.bounding_box().max.Y - gold.bounding_box().min.Y:.0f} x {gold.bounding_box().max.Z - gold.bounding_box().min.Z:.1f} mm")

# ============================================================
# PARTIE 2 : TEXTE + BORDURES (NOIR) — tout ce qui est en relief
# ============================================================
print("Building TEXT (black)...")

with BuildPart() as text_part:

    # Cadre extérieur
    with BuildSketch(Plane.XY.offset(T)):
        RectangleRounded(bw, bh, CR - 1)
        RectangleRounded(bw - 2 * FRAME_T, bh - 2 * FRAME_T,
                         max(CR - 2, 1), mode=Mode.SUBTRACT)
    extrude(amount=BORDER_R)

    # Double cadre décoratif fin
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
        with Locations([(rcx, 14)]):
            Text("UN TOUR", font_size=10, font=FONT,
                 align=(Align.CENTER, Align.CENTER))
    extrude(amount=TEXT_R)

    # Ligne décorative
    with BuildSketch(Plane.XY.offset(T)):
        with Locations([(rcx, 3)]):
            Rectangle(riw * 0.55, 0.8)
    extrude(amount=TEXT_R * 0.5)

    # DE MANEGE
    with BuildSketch(Plane.XY.offset(T)):
        with Locations([(rcx, -12)]):
            Text("DE MANEGE", font_size=16, font=FONT,
                 align=(Align.CENTER, Align.CENTER))
    extrude(amount=TEXT_R)

    # Étoiles coins
    for sx, sy in [
        (rcx - riw/2 + 10, rih/2 - 6),
        (rcx + riw/2 - 10, rih/2 - 6),
        (rcx - riw/2 + 10, -rih/2 + 6),
        (rcx + riw/2 - 10, -rih/2 + 6),
    ]:
        with BuildSketch(Plane.XY.offset(T)):
            Polygon(*star_pts(sx, sy, R=4.0, r=1.6))
        extrude(amount=TEXT_R)

    # Petites étoiles flanquant UN TOUR
    for sx, sy in [(rcx - 35, 14), (rcx + 35, 14)]:
        with BuildSketch(Plane.XY.offset(T)):
            Polygon(*star_pts(sx, sy, R=3.0, r=1.2))
        extrude(amount=TEXT_R)

black = text_part.part
print(f"  Text: {black.bounding_box().max.X - black.bounding_box().min.X:.0f} x {black.bounding_box().max.Y - black.bounding_box().min.Y:.0f} x {black.bounding_box().max.Z - black.bounding_box().min.Z:.1f} mm")

# ============================================================
# EXPORT
# ============================================================
export_stl(gold, "/tmp/ticket_vibrato_gold.stl")
export_stl(black, "/tmp/ticket_vibrato_black.stl")

print(f"\n{'='*50}")
print(f"✅ TICKET VIBRATO — VERSION BICOLORE")
print(f"   🟡 Base OR   : /tmp/ticket_vibrato_gold.stl")
print(f"   ⚫ Texte NOIR : /tmp/ticket_vibrato_black.stl")
print(f"{'='*50}")

# Visualisation bicolore
show(
    gold, black,
    names=["Base (OR)", "Texte (NOIR)"],
    colors=["#C9A962", "#1A1A1A"],
    reset_camera=Camera.RESET
)
print("✅ Viewer bicolore : http://127.0.0.1:3939")
