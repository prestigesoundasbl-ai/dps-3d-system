"""
Module Logo DJ Prestige Sound pour impression 3D.
Permet d'integrer le vrai logo vectoriel dans tous les modeles parametriques.

Le logo SVG est importe directement par OpenSCAD via import().
Taille originale du SVG: 1024x1024pt (echelle interne 10240x10240).

3 niveaux de qualite pour le logo:
  - 'draft'  : texte "PRESTIGE SOUND" (instant, < 1s)
  - 'normal' : logo geometrique compose (rapide, ~1-2s additionnel)
  - 'fine'   : SVG complet 94 paths (lent, 3-5 min)

Usage dans un modele:
    from ..logo import logo_3d, logo_engrave, logo_relief

    # Logo en relief (qualite par defaut: normal)
    model = base_plate + logo_relief(width=40, depth=1.0)

    # Logo draft pour preview rapide
    model = base_plate + logo_3d(width=40, height=1.5, quality='draft')
"""
import os
import subprocess
from solid2 import *

# Chemin absolu vers le SVG du logo (sans fond noir)
LOGO_SVG = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'assets', 'logo-prestige-sound-3d.svg'
)

# Chemin vers le STL pre-compile du logo (genere automatiquement)
LOGO_STL = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'assets', 'logo-prestige-sound-3d.stl'
)

# Dimensions originales du SVG en unites internes OpenSCAD
_SVG_SIZE = 1024.0

# Hauteur de reference pour la pre-compilation SVG->STL
_PRECOMPILE_HEIGHT = 10.0


# ---------------------------------------------------------------------------
# Pre-compilation SVG -> STL (une seule fois, ~30-60s)
# ---------------------------------------------------------------------------

def _get_openscad_bin():
    """Trouve le binaire OpenSCAD."""
    user_bin = os.path.expanduser('~/bin/openscad')
    if os.path.exists(user_bin):
        return user_bin
    return 'openscad'


def ensure_logo_stl():
    """
    Pre-compile le logo SVG en STL si pas deja fait.
    Premiere execution : ~30-60s (OpenSCAD parse le SVG).
    Toutes les suivantes : instantane (STL deja sur disque).
    """
    if os.path.exists(LOGO_STL):
        return True

    scad_path = LOGO_STL.replace('.stl', '_precompile.scad')
    scad_content = (
        f'linear_extrude(height = {_PRECOMPILE_HEIGHT})\n'
        f'  translate([-{_SVG_SIZE / 2}, -{_SVG_SIZE / 2}])\n'
        f'    import("{LOGO_SVG}");\n'
    )

    with open(scad_path, 'w') as f:
        f.write(scad_content)

    openscad = _get_openscad_bin()
    try:
        result = subprocess.run(
            [openscad, '-o', LOGO_STL, scad_path],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode != 0:
            print(f"[logo] Erreur pre-compilation: {result.stderr}", flush=True)
            return False
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"[logo] Pre-compilation echouee: {e}", flush=True)
        return False


# ---------------------------------------------------------------------------
# Logo 2D/3D - version SVG originale (quality='fine')
# ---------------------------------------------------------------------------

def _raw_logo_2d():
    """Importe le SVG brut 2D (taille originale ~1024mm).
    Centre manuellement car import_() n'a pas d'option center."""
    return translate([-_SVG_SIZE / 2, -_SVG_SIZE / 2])(import_(LOGO_SVG))


def logo_2d(width=50.0):
    """Logo 2D mis a l'echelle pour une largeur donnee."""
    s = width / _SVG_SIZE
    return scale([s, s])(_raw_logo_2d())


# ---------------------------------------------------------------------------
# Logo 3D - avec niveaux de qualite
# ---------------------------------------------------------------------------

def _logo_text_fallback(width=50.0, height=1.5):
    """
    Logo en mode draft : texte "PRESTIGE SOUND" extrude.
    Ultra rapide (< 1s), utilise la police systeme.
    """
    text_size = width / 10.0
    return linear_extrude(height=height)(
        text("PRESTIGE SOUND", size=text_size,
             font="Liberation Sans:style=Bold",
             halign="center", valign="center", _fn=32)
    )


def _logo_geometric(width=50.0, height=1.5):
    """
    Logo geometrique compose en SolidPython2 pur (pas d'import SVG/STL).
    Reproduit le vrai logo Prestige Sound :
      - Clef de sol simplifiee en haut
      - "PRESTIGE" en gros, "SOUND" en dessous
      - Double cadre art deco avec coins decoratifs
      - Lignes horizontales decoratives
      - Losanges et ornements
    Rendu rapide (~2-3s additionnel) tout en etant visuellement fidele.
    Centre a l'origine (comme les autres modes).
    """
    logo = union()
    hw = width / 2.0

    # Proportions basees sur le vrai logo (ratio ~1:1)
    logo_h = width  # logo carre comme l'original
    t = width * 0.012  # epaisseur des lignes
    fn = 36  # qualite des courbes

    # --- Texte "PRESTIGE" (principal, plus gros) ---
    prestige_size = width / 7.0
    prestige_y = -logo_h * 0.05
    logo += linear_extrude(height=height)(
        text("PRESTIGE", size=prestige_size,
             font="Liberation Sans:style=Bold",
             halign="center", valign="center", _fn=fn)
    )

    # --- Texte "SOUND" (en dessous, un peu plus petit) ---
    sound_size = prestige_size * 0.85
    sound_y = prestige_y - prestige_size * 1.3
    logo += translate([0, sound_y, 0])(
        linear_extrude(height=height)(
            text("SOUND", size=sound_size,
                 font="Liberation Sans:style=Bold",
                 halign="center", valign="center", _fn=fn)
        )
    )

    # --- Ligne decorative entre les textes ---
    line_w = width * 0.55
    logo += translate([-line_w / 2, prestige_y - prestige_size * 0.6, 0])(
        cube([line_w, t, height])
    )

    # --- Ligne decorative au-dessus de PRESTIGE ---
    line_top_y = prestige_y + prestige_size * 0.7
    logo += translate([-line_w / 2, line_top_y, 0])(
        cube([line_w, t, height])
    )
    # Double ligne
    logo += translate([-line_w * 0.45, line_top_y + t * 3, 0])(
        cube([line_w * 0.9, t * 0.7, height])
    )

    # --- Ligne decorative sous SOUND ---
    line_bot_y = sound_y - sound_size * 0.7
    logo += translate([-line_w / 2, line_bot_y, 0])(
        cube([line_w, t, height])
    )

    # --- Losanges decoratifs aux extremites des lignes ---
    diamond_s = t * 4
    for line_y in [line_top_y + t * 0.5, line_bot_y + t * 0.5]:
        for dx in [-line_w / 2, line_w / 2]:
            logo += translate([dx, line_y, 0])(
                linear_extrude(height=height)(
                    rotate([0, 0, 45])(
                        square([diamond_s, diamond_s], center=True)
                    )
                )
            )

    # --- Clef de sol simplifiee (au-dessus du cadre) ---
    # Tige verticale
    clef_x = 0
    clef_base_y = line_top_y + t * 6
    clef_h = logo_h * 0.22
    stem_w = t * 2.0
    logo += translate([-stem_w / 2, clef_base_y, 0])(
        cube([stem_w, clef_h, height])
    )
    # Boucle superieure (cercle avec trou)
    loop_r = clef_h * 0.18
    loop_y = clef_base_y + clef_h - loop_r
    logo += translate([0, loop_y, 0])(
        linear_extrude(height=height)(
            circle(r=loop_r, _fn=fn) - circle(r=loop_r * 0.55, _fn=fn)
        )
    )
    # Boucle inferieure plus petite
    loop2_r = loop_r * 0.6
    loop2_y = clef_base_y + clef_h * 0.2
    logo += translate([loop2_r * 0.4, loop2_y, 0])(
        linear_extrude(height=height)(
            circle(r=loop2_r, _fn=fn) - circle(r=loop2_r * 0.5, _fn=fn)
        )
    )
    # Petit cercle en bas de la clef
    dot_r = t * 1.5
    logo += translate([0, clef_base_y - dot_r, 0])(
        linear_extrude(height=height)(
            circle(r=dot_r, _fn=fn)
        )
    )
    # Courbe en S (approximee par 2 arcs)
    s_r = loop_r * 0.7
    logo += translate([-s_r * 0.3, clef_base_y + clef_h * 0.55, 0])(
        linear_extrude(height=height)(
            circle(r=s_r, _fn=fn) - circle(r=s_r * 0.5, _fn=fn)
            - translate([-s_r * 1.5, 0])(square([s_r * 3, s_r * 3], center=True))
        )
    )
    logo += translate([s_r * 0.3, clef_base_y + clef_h * 0.38, 0])(
        linear_extrude(height=height)(
            circle(r=s_r, _fn=fn) - circle(r=s_r * 0.5, _fn=fn)
            - translate([s_r * 1.5, 0])(square([s_r * 3, s_r * 3], center=True))
        )
    )

    # --- Cadre exterieur art deco ---
    frame_w = width * 0.82
    frame_h = logo_h * 0.72
    frame_cy = (line_top_y + line_bot_y) / 2.0
    frame_bot = frame_cy - frame_h / 2
    # Cadre exterieur
    outer = cube([frame_w, frame_h, height])
    inner = cube([frame_w - 2 * t, frame_h - 2 * t, height + 0.1])
    cadre = outer - translate([t, t, -0.05])(inner)
    logo += translate([-frame_w / 2, frame_bot, 0])(cadre)

    # --- Cadre interieur (double cadre art deco) ---
    margin = t * 4
    inner_w = frame_w - 2 * margin
    inner_h = frame_h - 2 * margin
    outer2 = cube([inner_w, inner_h, height])
    inner2 = cube([inner_w - 2 * t, inner_h - 2 * t, height + 0.1])
    cadre2 = outer2 - translate([t, t, -0.05])(inner2)
    logo += translate([-inner_w / 2, frame_bot + margin, 0])(cadre2)

    # --- Coins decoratifs art deco (petits carres aux 4 coins) ---
    corner_s = t * 3.5
    corners = [
        [-frame_w / 2 + margin, frame_bot + margin],
        [frame_w / 2 - margin, frame_bot + margin],
        [-frame_w / 2 + margin, frame_bot + frame_h - margin],
        [frame_w / 2 - margin, frame_bot + frame_h - margin],
    ]
    for cx, cy in corners:
        logo += translate([cx - corner_s / 2, cy - corner_s / 2, 0])(
            cube([corner_s, corner_s, height])
        )

    return logo


def logo_3d(width=50.0, height=1.5, quality='normal'):
    """
    Logo 3D extrude avec 3 niveaux de qualite.

    Args:
        width: Largeur du logo en mm
        height: Epaisseur d'extrusion en mm
        quality: 'draft' (texte), 'normal' (STL cache), 'fine' (SVG complet)

    Returns:
        Objet SolidPython2 3D
    """
    if quality == 'draft':
        return _logo_text_fallback(width, height)

    if quality == 'normal':
        return _logo_geometric(width, height)

    # quality == 'fine' : SVG complet (lent mais fidele)
    return linear_extrude(height=height)(logo_2d(width))


def logo_relief(width=50.0, depth=1.0, quality='normal'):
    """Logo en relief (a ajouter sur une surface avec +)."""
    return logo_3d(width, depth, quality=quality)


def logo_engrave(width=50.0, depth=0.8, quality='normal'):
    """Logo pour gravure (a soustraire d'une surface avec -)."""
    return logo_3d(width, depth + 0.1, quality=quality)


def logo_on_face(width=50.0, depth=1.0, style="engrave",
                 face="front", surface_offset=0, quality='normal'):
    """
    Logo positionne sur une face specifique, pret a etre
    ajoute (+) ou soustrait (-) du modele.
    """
    if style == "engrave":
        obj = logo_engrave(width, depth, quality=quality)
    else:
        obj = logo_relief(width, depth, quality=quality)

    if face == "front":
        obj = rotate([90, 0, 0])(obj)
        obj = translate([0, surface_offset - depth, 0])(obj)
    elif face == "back":
        obj = rotate([-90, 0, 0])(obj)
        obj = translate([0, surface_offset + depth, 0])(obj)
    elif face == "top":
        obj = translate([0, 0, surface_offset])(obj)
    elif face == "bottom":
        obj = rotate([180, 0, 0])(obj)
        obj = translate([0, 0, surface_offset])(obj)

    return obj


# Copier le logo dans le web pour l'affichage UI
def copy_logo_to_web():
    """Copie le logo PNG vers web/assets/ pour l'interface."""
    import shutil
    src = os.path.join(os.path.expanduser("~"), "Desktop", "PRESTIGE_BUSINESS", "LOGOS_ET_MEDIA", "Logo_Prestige_Sound", "PNG", "logo-512-transparent.png")
    dst = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       '..', 'web', 'assets', 'logo.png')
    if os.path.exists(src):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        return dst
    return None


if __name__ == "__main__":
    """Test: genere un logo 3D de test a 50mm de large."""
    import sys

    print("=== Test module logo ===\n")

    # Test pre-compilation
    print("1. Pre-compilation SVG -> STL...")
    ok = ensure_logo_stl()
    print(f"   STL pre-compile: {'OK' if ok else 'ECHEC'}")
    if ok:
        size = os.path.getsize(LOGO_STL)
        print(f"   Taille: {size / 1024:.1f} KB")

    scad_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            '..', 'output', 'scad')
    os.makedirs(scad_dir, exist_ok=True)

    # Test 3 niveaux de qualite
    for q in ('draft', 'normal', 'fine'):
        obj = logo_3d(width=50, height=1.5, quality=q)
        path = os.path.join(scad_dir, f"logo_test_{q}.scad")
        obj.save_as_scad(path)
        print(f"2. Logo {q}: {path}")

    # Test engrave sur plaque
    base = cube([60, 60, 5])
    engraved = base - translate([30, 30, 5 - 0.8])(logo_engrave(width=50, depth=0.8))
    path2 = os.path.join(scad_dir, "logo_engrave_test.scad")
    engraved.save_as_scad(path2)
    print(f"3. Logo grave sur plaque: {path2}")

    # Copier logo web
    web_logo = copy_logo_to_web()
    if web_logo:
        print(f"4. Logo copie vers UI: {web_logo}")

    print("\nOK - Module logo fonctionnel!")
