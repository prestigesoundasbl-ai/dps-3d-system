#!/usr/bin/env python3
"""
Ticket Vintage — VIBRATO / UN TOUR DE MANÈGE
Style cirque / fête foraine rétro
200mm x 100mm — Impression 3D (Creality K2 Pro)
"""
from build123d import *
from ocp_vscode import show
import math

# ============================
# PARAMÈTRES
# ============================
W = 200.0        # largeur ticket (mm)
H = 100.0        # hauteur ticket (mm)
T = 3.0          # épaisseur de la base
TEXT_R = 1.5     # relief du texte
BORDER_R = 1.0   # relief des bordures
CR = 5.0         # rayon des coins arrondis

MARGIN = 7.0     # marge bord → cadre
FRAME_T = 2.0    # épaisseur trait du cadre
LEFT_W = 50.0    # largeur section gauche (VIBRATO)

DIV_X = -W/2 + LEFT_W  # = -50mm (séparateur vertical)

# Perforations
PERF_R = 2.5     # rayon trous perforations bord
PERF_MINI = 1.5  # rayon trous ligne tear-off
PERF_N = 10      # nombre de trous par côté

# Font
FONT = "Copperplate"

# ============================
# ÉTOILE 5 BRANCHES
# ============================
def star_pts(cx, cy, R=5.0, r=2.0, n=5):
    """Sommets d'une étoile à 5 branches"""
    pts = []
    for i in range(2 * n):
        angle = math.pi / 2 + i * math.pi / n
        radius = R if i % 2 == 0 else r
        pts.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
    return pts

# ============================
# CALCULS SECTIONS
# ============================
# Section gauche (VIBRATO)
lx0 = -W/2 + MARGIN + FRAME_T + 1
lx1 = DIV_X - 3
lcx = (lx0 + lx1) / 2
liw = lx1 - lx0
lih = H - 2 * (MARGIN + FRAME_T + 4)

# Section droite (UN TOUR DE MANÈGE)
rx0 = DIV_X + 4
rx1 = W/2 - MARGIN - FRAME_T - 1
rcx = (rx0 + rx1) / 2
riw = rx1 - rx0
rih = H - 2 * (MARGIN + FRAME_T + 4)

print(f"Section gauche: cx={lcx:.1f}, inner={liw:.1f}x{lih:.1f}mm")
print(f"Section droite: cx={rcx:.1f}, inner={riw:.1f}x{rih:.1f}mm")

# Positions Y des perforations (hors zone coins)
y_start = -H/2 + CR + PERF_R + 3
y_end = H/2 - CR - PERF_R - 3
perf_spacing = (y_end - y_start) / (PERF_N - 1) if PERF_N > 1 else 0

# ============================
# CONSTRUCTION
# ============================
with BuildPart() as ticket:

    # ── 1. BASE RECTANGULAIRE ARRONDIE ──
    with BuildSketch():
        RectangleRounded(W, H, CR)
    extrude(amount=T)

    # ── 2. PERFORATIONS BORD GAUCHE (scalloped edge) ──
    for i in range(PERF_N):
        y = y_start + i * perf_spacing
        with BuildSketch():
            with Locations([(-W/2, y)]):
                Circle(PERF_R)
        extrude(amount=T, mode=Mode.SUBTRACT)

    # ── 3. PERFORATIONS BORD DROIT ──
    for i in range(PERF_N):
        y = y_start + i * perf_spacing
        with BuildSketch():
            with Locations([(W/2, y)]):
                Circle(PERF_R)
        extrude(amount=T, mode=Mode.SUBTRACT)

    # ── 4. PERFORATIONS TEAR-OFF (ligne du séparateur) ──
    tear_n = 12
    tear_spacing = (y_end - y_start) / (tear_n - 1) if tear_n > 1 else 0
    for i in range(tear_n):
        y = y_start + i * tear_spacing
        with BuildSketch():
            with Locations([(DIV_X, y)]):
                Circle(PERF_MINI)
        extrude(amount=T, mode=Mode.SUBTRACT)

    # ── 5. CADRE EXTÉRIEUR (bordure en relief) ──
    bw = W - 2 * MARGIN
    bh = H - 2 * MARGIN
    with BuildSketch(Plane.XY.offset(T)):
        RectangleRounded(bw, bh, CR - 1)
        RectangleRounded(bw - 2 * FRAME_T, bh - 2 * FRAME_T,
                         max(CR - 2, 1), mode=Mode.SUBTRACT)
    extrude(amount=BORDER_R)

    # ── 6. DOUBLE CADRE EXTÉRIEUR (cadre décoratif fin) ──
    with BuildSketch(Plane.XY.offset(T)):
        RectangleRounded(bw - 6, bh - 6, max(CR - 2, 1))
        RectangleRounded(bw - 8, bh - 8, max(CR - 3, 0.5), mode=Mode.SUBTRACT)
    extrude(amount=BORDER_R * 0.5)

    # ── 7. SÉPARATEUR VERTICAL (trait en relief) ──
    div_h = bh - 2 * FRAME_T - 8
    with BuildSketch(Plane.XY.offset(T)):
        with Locations([(DIV_X, 0)]):
            Rectangle(1.5, div_h)
    extrude(amount=BORDER_R)

    # ── 8. CADRE INTÉRIEUR GAUCHE ──
    with BuildSketch(Plane.XY.offset(T)):
        with Locations([(lcx, 0)]):
            RectangleRounded(liw + 2, lih + 2, 1.5)
            RectangleRounded(liw - 2, lih - 2, 0.5, mode=Mode.SUBTRACT)
    extrude(amount=BORDER_R * 0.5)

    # ── 9. CADRE INTÉRIEUR DROIT ──
    with BuildSketch(Plane.XY.offset(T)):
        with Locations([(rcx, 0)]):
            RectangleRounded(riw + 2, rih + 2, 1.5)
            RectangleRounded(riw - 2, rih - 2, 0.5, mode=Mode.SUBTRACT)
    extrude(amount=BORDER_R * 0.5)

    # ── 10. TEXTE "VIBRATO" (vertical, section gauche) ──
    with BuildSketch(Plane.XY.offset(T)):
        with Locations([(lcx, 0)]):
            Text("VIBRATO", font_size=10, font=FONT,
                 align=(Align.CENTER, Align.CENTER), rotation=90)
    extrude(amount=TEXT_R)

    # ── 11. TEXTE "UN TOUR" (section droite, haut) ──
    with BuildSketch(Plane.XY.offset(T)):
        with Locations([(rcx, 14)]):
            Text("UN TOUR", font_size=10, font=FONT,
                 align=(Align.CENTER, Align.CENTER))
    extrude(amount=TEXT_R)

    # ── 12. LIGNE DÉCORATIVE (entre les deux textes) ──
    with BuildSketch(Plane.XY.offset(T)):
        with Locations([(rcx, 3)]):
            Rectangle(riw * 0.55, 0.8)
    extrude(amount=TEXT_R * 0.5)

    # ── 13. TEXTE "DE MANÈGE" (section droite, gros, principal) ──
    with BuildSketch(Plane.XY.offset(T)):
        with Locations([(rcx, -12)]):
            Text("DE MANEGE", font_size=16, font=FONT,
                 align=(Align.CENTER, Align.CENTER))
    extrude(amount=TEXT_R)

    # ── 14. ÉTOILES DÉCORATIVES (4 coins section droite) ──
    stars = [
        (rcx - riw/2 + 10, rih/2 - 6),
        (rcx + riw/2 - 10, rih/2 - 6),
        (rcx - riw/2 + 10, -rih/2 + 6),
        (rcx + riw/2 - 10, -rih/2 + 6),
    ]
    for sx, sy in stars:
        with BuildSketch(Plane.XY.offset(T)):
            Polygon(*star_pts(sx, sy, R=4.0, r=1.6))
        extrude(amount=TEXT_R)

    # ── 15. PETITES ÉTOILES flanquant "UN TOUR" ──
    for sx, sy in [(rcx - 35, 14), (rcx + 35, 14)]:
        with BuildSketch(Plane.XY.offset(T)):
            Polygon(*star_pts(sx, sy, R=3.0, r=1.2))
        extrude(amount=TEXT_R)

# ============================
# EXPORT
# ============================
part = ticket.part
bb = part.bounding_box()
dims = f"{bb.max.X - bb.min.X:.1f} x {bb.max.Y - bb.min.Y:.1f} x {bb.max.Z - bb.min.Z:.1f}"
vol = part.volume

print(f"\n{'='*40}")
print(f"✅ TICKET VIBRATO")
print(f"   Dimensions : {dims} mm")
print(f"   Volume     : {vol:.0f} mm³")
print(f"{'='*40}")

export_stl(part, "/tmp/ticket_vibrato.stl")
print("✅ Export STL  : /tmp/ticket_vibrato.stl")

# Visualisation
show(part, names=["Ticket VIBRATO - Un Tour de Manège"], colors=["#C9A962"])
print("✅ Viewer      : http://127.0.0.1:3939")
