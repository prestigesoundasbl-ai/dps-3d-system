"""
Logo SVG Helper — Import du vrai logo Prestige Sound vectoriel
================================================================
Utilise le fichier SVG assets/logo-prestige-sound-3d.svg
pour créer une géométrie 3D du vrai logo (94 faces vectorielles).

Usage dans un modèle build123d :
    from models.logo_svg import extrude_logo_on_face
    extrude_logo_on_face(part, target_width=100, relief=1.0)
"""
import os
from build123d import *

LOGO_SVG = os.path.join(os.path.dirname(__file__), "assets", "logo-prestige-sound-3d.svg")


def get_logo_faces():
    """Import les faces du logo SVG."""
    return import_svg(LOGO_SVG)


def get_logo_bounds():
    """Retourne (min_x, min_y, max_x, max_y, width, height) du logo SVG."""
    faces = get_logo_faces()
    all_bb = [f.bounding_box() for f in faces]
    min_x = min(bb.min.X for bb in all_bb)
    min_y = min(bb.min.Y for bb in all_bb)
    max_x = max(bb.max.X for bb in all_bb)
    max_y = max(bb.max.Y for bb in all_bb)
    return min_x, min_y, max_x, max_y, max_x - min_x, max_y - min_y


def extrude_logo(target_width=100.0, relief=1.0, z_offset=0.0):
    """
    Extrude le vrai logo SVG à la taille voulue.
    
    Args:
        target_width: Largeur finale du logo en mm
        relief: Hauteur de l'extrusion en mm
        z_offset: Position Z de la base du logo
    
    Returns:
        Les faces sont extrudées dans le BuildPart courant.
    """
    faces = get_logo_faces()
    min_x, min_y, max_x, max_y, svg_w, svg_h = get_logo_bounds()
    
    scale = target_width / svg_w
    cx = (min_x + max_x) / 2
    cy = (min_y + max_y) / 2
    
    for face in faces:
        centered = face.moved(Location((-cx * scale, -cy * scale, z_offset)))
        scaled = centered.scale(scale)
        extrude(scaled, amount=relief)


def logo_dimensions(target_width=100.0):
    """Retourne (width, height) du logo à la taille cible."""
    _, _, _, _, svg_w, svg_h = get_logo_bounds()
    scale = target_width / svg_w
    return target_width, svg_h * scale
