#!/usr/bin/env python3
"""
Ticket Vintage — VIBRATO / UN TOUR DE MANÈGE
VERSION 2 : BICOLORE + CHAPITEAU DE CIRQUE
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
# HELPERS
# ============================
def star_pts(cx, cy, R=5.0, r=2.0, n=5):
    pts = []
    for i in range(2 * n):
        angle = math.pi / 2 + i * math.pi / n
        radius = R if i % 2 == 0 else r
        pts.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
    return pts

def tent_profile(cx, cy, half_w=11, height=16, n_pts=8):
    """Génère le profil d'un chapiteau de cirque (courbe douce)"""
    pts = []
    # Côté gauche (bas → sommet)
    for i in range(n_pts + 1):
        t = i / n_pts  # 0 → 1
        # Courbe concave (rétrécit vers le haut)
        x = -half_w * (1 - t) ** 0.65
        y = -height * 0.35 + height * t
        pts.append((cx + x, cy + y))
    # Côté droit (sommet → bas, miroir)
    for i in range(n_pts - 1, -1, -1):
        t = i / n_pts
        x = half_w * (1 - t) ** 0.65
        y = -height * 0.35 + height * t
        pts.append((cx + x, cy + y))
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
perf_spacing = (y_end - y_start) / (PERF_N - 1)

bw = W - 2 * MARGIN
bh = H - 2 * MARGIN
div_h = bh - 2 * FRAME_T - 8

# ── Positions texte (ajustées pour le chapiteau) ──
UN_TOUR_Y = 28
DE_MANEGE_Y = -20
TENT_CY = 4  # centre du chapiteau

print(f"Layout: UN TOUR y={UN_TOUR_Y}, Chapiteau cy={TENT_CY}, DE MANEGE y={DE_MANEGE_Y}")
print(f"Right section: cx={rcx:.1f}, inner={riw:.1f}x{rih:.1f}mm")

# ============================================================
# PARTIE 1 : BASE (OR / GOLD)
# ============================================================
print("\nBuilding BASE (gold)...")

with BuildPart() as base_part:
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

    # Perforations tear-off
    tear_n = 12
    tear_sp = (y_end - y_start) / (tear_n - 1)
    for i in range(tear_n):
        y = y_start + i * tear_sp
        with BuildSketch():
            with Locations([(DIV_X, y)]):
                Circle(PERF_MINI)
        extrude(amount=T, mode=Mode.SUBTRACT)

gold = base_part.part
print(f"  OK: {gold.bounding_box().max.X - gold.bounding_box().min.X:.0f}x{gold.bounding_box().max.Y - gold.bounding_box().min.Y:.0f}mm")

# ============================================================
# PARTIE 2 : TEXTE + BORDURES + CHAPITEAU (NOIR)
# ============================================================
print("Building TEXT + CHAPITEAU (black)...")

with BuildPart() as text_part:

    # ── Cadre extérieur ──
    with BuildSketch(Plane.XY.offset(T)):
        RectangleRounded(bw, bh, CR - 1)
        RectangleRounded(bw - 2 * FRAME_T, bh - 2 * FRAME_T,
                         max(CR - 2, 1), mode=Mode.SUBTRACT)
    extrude(amount=BORDER_R)

    # ── Double cadre décoratif ──
    with BuildSketch(Plane.XY.offset(T)):
        RectangleRounded(bw - 6, bh - 6, max(CR - 2, 1))
        RectangleRounded(bw - 8, bh - 8, max(CR - 3, 0.5), mode=Mode.SUBTRACT)
    extrude(amount=BORDER_R * 0.5)

    # ── Séparateur vertical ──
    with BuildSketch(Plane.XY.offset(T)):
        with Locations([(DIV_X, 0)]):
            Rectangle(1.5, div_h)
    extrude(amount=BORDER_R)

    # ── Cadre intérieur gauche ──
    with BuildSketch(Plane.XY.offset(T)):
        with Locations([(lcx, 0)]):
            RectangleRounded(liw + 2, lih + 2, 1.5)
            RectangleRounded(liw - 2, lih - 2, 0.5, mode=Mode.SUBTRACT)
    extrude(amount=BORDER_R * 0.5)

    # ── Cadre intérieur droit ──
    with BuildSketch(Plane.XY.offset(T)):
        with Locations([(rcx, 0)]):
            RectangleRounded(riw + 2, rih + 2, 1.5)
            RectangleRounded(riw - 2, rih - 2, 0.5, mode=Mode.SUBTRACT)
    extrude(amount=BORDER_R * 0.5)

    # ── VIBRATO vertical ──
    with BuildSketch(Plane.XY.offset(T)):
        with Locations([(lcx, 0)]):
            Text("VIBRATO", font_size=10, font=FONT,
                 align=(Align.CENTER, Align.CENTER), rotation=90)
    extrude(amount=TEXT_R)

    # ── UN TOUR (repositionné plus haut) ──
    with BuildSketch(Plane.XY.offset(T)):
        with Locations([(rcx, UN_TOUR_Y)]):
            Text("UN TOUR", font_size=10, font=FONT,
                 align=(Align.CENTER, Align.CENTER))
    extrude(amount=TEXT_R)

    # ── DE MANEGE (repositionné plus bas) ──
    with BuildSketch(Plane.XY.offset(T)):
        with Locations([(rcx, DE_MANEGE_Y)]):
            Text("DE MANEGE", font_size=16, font=FONT,
                 align=(Align.CENTER, Align.CENTER))
    extrude(amount=TEXT_R)

    # ══════════════════════════════════════════════
    # ══  CHAPITEAU DE CIRQUE (centre droit)     ══
    # ══════════════════════════════════════════════

    tcx = rcx
    tcy = TENT_CY
    tent_hw = 11     # demi-largeur base
    tent_h = 16      # hauteur base → sommet

    # 1. Corps du chapiteau (profil courbe)
    tent = tent_profile(tcx, tcy, half_w=tent_hw, height=tent_h, n_pts=8)
    with BuildSketch(Plane.XY.offset(T)):
        Polygon(*tent)
    extrude(amount=TEXT_R)

    # 2. Festons / scallops au bas du chapiteau
    tent_base_y = tcy - tent_h * 0.35
    scallop_r = 1.8
    n_scallops = 7
    scallop_span = tent_hw * 2 - 2
    for i in range(n_scallops):
        sx = tcx - scallop_span / 2 + i * scallop_span / (n_scallops - 1)
        with BuildSketch(Plane.XY.offset(T)):
            with Locations([(sx, tent_base_y)]):
                Circle(scallop_r)
        extrude(amount=TEXT_R)

    # 3. Mât (poteau fin au-dessus du sommet)
    tent_peak_y = tcy + tent_h * 0.65
    pole_h = 4
    with BuildSketch(Plane.XY.offset(T)):
        with Locations([(tcx, tent_peak_y + pole_h / 2)]):
            Rectangle(1.2, pole_h)
    extrude(amount=TEXT_R)

    # 4. Drapeau / fanion
    flag_base_y = tent_peak_y + pole_h - 0.5
    flag_pts = [
        (tcx, flag_base_y),
        (tcx, flag_base_y + 3),
        (tcx + 4, flag_base_y + 1.5),
    ]
    with BuildSketch(Plane.XY.offset(T)):
        Polygon(*flag_pts)
    extrude(amount=TEXT_R)

    # ══════════════════════════════════════════════

    # ── Étoiles coins section droite ──
    for sx, sy in [
        (rcx - riw/2 + 10, rih/2 - 6),
        (rcx + riw/2 - 10, rih/2 - 6),
        (rcx - riw/2 + 10, -rih/2 + 6),
        (rcx + riw/2 - 10, -rih/2 + 6),
    ]:
        with BuildSketch(Plane.XY.offset(T)):
            Polygon(*star_pts(sx, sy, R=4.0, r=1.6))
        extrude(amount=TEXT_R)

    # ── Étoiles flanquant "UN TOUR" ──
    for sx, sy in [(rcx - 35, UN_TOUR_Y), (rcx + 35, UN_TOUR_Y)]:
        with BuildSketch(Plane.XY.offset(T)):
            Polygon(*star_pts(sx, sy, R=3.0, r=1.2))
        extrude(amount=TEXT_R)

black = text_part.part
print(f"  OK: {black.bounding_box().max.X - black.bounding_box().min.X:.0f}x{black.bounding_box().max.Y - black.bounding_box().min.Y:.0f}mm")

# ============================================================
# EXPORT
# ============================================================
export_stl(gold, "/tmp/ticket_vibrato_v2_gold.stl")
export_stl(black, "/tmp/ticket_vibrato_v2_black.stl")

# Version combinée aussi
combined = gold.fuse(black)
export_stl(combined, "/tmp/ticket_vibrato_v2_combined.stl")

print(f"\n{'='*55}")
print(f"  ✅ TICKET VIBRATO V2 — BICOLORE + CHAPITEAU")
print(f"  🟡 Base OR    : /tmp/ticket_vibrato_v2_gold.stl")
print(f"  ⚫ Texte NOIR  : /tmp/ticket_vibrato_v2_black.stl")
print(f"  🔗 Combiné    : /tmp/ticket_vibrato_v2_combined.stl")
print(f"{'='*55}")

# Visualisation bicolore
show(
    gold, black,
    names=["Base (OR)", "Texte + Chapiteau (NOIR)"],
    colors=["#C9A962", "#1A1A1A"],
    reset_camera=Camera.RESET
)
