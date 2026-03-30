"""
Sous-Verre (Coaster) Brande Parametrique
Sous-verre circulaire avec rebord et motif decoratif.
Specifications par defaut:
  - Diametre: 90mm
  - Rebord sureleve
  - Motif concentrique ou grille
  - Texte marque en-dessous
"""
import math
from solid2 import *
from ..base import ParametricModel
from ..brand import (
    BRAND_NAME_SHORT, DEFAULT_TEXT_DEPTH, DEFAULT_TEXT_FONT
)
from ..logo import logo_engrave


class Coaster(ParametricModel):

    def __init__(self, **params):
        super().__init__("coaster", **params)

    def default_params(self):
        return {
            'diameter': 90.0,
            'thickness': 4.0,
            'rim_height': 2.0,
            'rim_width': 3.0,
            'pattern': 'rings',
            'pattern_depth': 0.8,
            'pattern_count': 4,
            'brand_text': BRAND_NAME_SHORT,
            'brand_text_size': 5.0,
            'drain_grooves': True,
            'groove_count': 6,
            'use_logo': True,
            'logo_width': 0.0,
        }

    def param_schema(self):
        return {
            'diameter': {
                'type': 'float', 'min': 60, 'max': 120, 'unit': 'mm',
                'description': 'Diametre du sous-verre'
            },
            'thickness': {
                'type': 'float', 'min': 2, 'max': 8, 'unit': 'mm',
                'description': 'Epaisseur du disque'
            },
            'rim_height': {
                'type': 'float', 'min': 0.5, 'max': 5, 'unit': 'mm',
                'description': 'Hauteur du rebord sureleve'
            },
            'rim_width': {
                'type': 'float', 'min': 1, 'max': 8, 'unit': 'mm',
                'description': 'Largeur du rebord'
            },
            'pattern': {
                'type': 'string',
                'description': 'Motif decoratif: rings, grid, ou none'
            },
            'pattern_depth': {
                'type': 'float', 'min': 0.3, 'max': 2, 'unit': 'mm',
                'description': 'Profondeur du motif grave'
            },
            'pattern_count': {
                'type': 'int', 'min': 2, 'max': 8, 'unit': '',
                'description': 'Nombre d\'elements du motif'
            },
            'brand_text': {
                'type': 'string',
                'description': 'Texte marque sur le dessous'
            },
            'brand_text_size': {
                'type': 'float', 'min': 3, 'max': 10, 'unit': 'mm',
                'description': 'Taille du texte marque'
            },
            'drain_grooves': {
                'type': 'bool',
                'description': 'Rainures de drainage sur le dessus'
            },
            'groove_count': {
                'type': 'int', 'min': 3, 'max': 12, 'unit': '',
                'description': 'Nombre de rainures de drainage'
            },
            'use_logo': {
                'type': 'boolean',
                'description': 'Utiliser le vrai logo SVG Prestige Sound'
            },
            'logo_width': {
                'type': 'float', 'min': 0, 'max': 80, 'unit': 'mm',
                'description': 'Largeur du logo (0=auto 60% diametre)'
            },
        }

    def build(self):
        p = self.params
        d = p['diameter']
        t = p['thickness']
        rh = p['rim_height']
        rw = p['rim_width']
        pattern = p['pattern']
        pd_depth = p['pattern_depth']
        pc = p['pattern_count']

        r = d / 2

        # -- Disque principal --
        disc = cylinder(d=d, h=t, _fn=64)

        # -- Rebord sureleve --
        rim_outer = cylinder(d=d, h=t + rh, _fn=64)
        rim_inner = cylinder(d=d - 2 * rw, h=t + rh + 0.1, _fn=64)
        rim = rim_outer - rim_inner

        model = disc + rim

        # -- Motif decoratif sur le dessus --
        if pattern == 'rings':
            # Anneaux concentriques graves dans le dessus
            usable_r = r - rw - 2
            ring_spacing = usable_r / (pc + 1)
            ring_width = 1.0  # Largeur de chaque anneau

            for i in range(1, pc + 1):
                ring_r = ring_spacing * i
                ring_outer = cylinder(r=ring_r + ring_width / 2, h=pd_depth + 0.1, _fn=64)
                ring_inner = cylinder(r=ring_r - ring_width / 2, h=pd_depth + 0.2, _fn=64)
                ring = ring_outer - ring_inner
                ring = translate([0, 0, t - pd_depth])(ring)
                model = model - ring

        elif pattern == 'grid':
            # Grille de lignes croisees
            usable_size = d - 2 * rw - 4
            line_width = 1.0
            spacing = usable_size / (pc + 1)

            for i in range(1, pc + 1):
                offset = -usable_size / 2 + spacing * i
                # Lignes horizontales
                h_line = translate([offset - line_width / 2,
                                   -usable_size / 2, t - pd_depth])(
                    cube([line_width, usable_size, pd_depth + 0.1])
                )
                # Lignes verticales
                v_line = translate([-usable_size / 2,
                                   offset - line_width / 2, t - pd_depth])(
                    cube([usable_size, line_width, pd_depth + 0.1])
                )
                # Couper aux limites du cercle
                clip_cyl = cylinder(r=r - rw - 1, h=t + 1, _fn=64)
                h_clipped = h_line & clip_cyl
                v_clipped = v_line & clip_cyl
                model = model - h_clipped - v_clipped

        # -- Rainures de drainage radiales sur le dessus --
        if p['drain_grooves']:
            gc = p['groove_count']
            groove_w = 1.2
            groove_depth = pd_depth * 0.8

            for i in range(gc):
                angle = (360 / gc) * i
                groove = translate([0, -groove_w / 2, t - groove_depth])(
                    cube([r - rw - 2, groove_w, groove_depth + 0.1])
                )
                groove = rotate([0, 0, angle])(groove)
                model = model - groove

        # -- Logo ou texte marque sur le dessous --
        if p.get('use_logo', False):
            logo_w = p['logo_width'] if p['logo_width'] > 0 else d * 0.6
            logo_obj = logo_engrave(width=logo_w, depth=DEFAULT_TEXT_DEPTH)
            logo_obj = mirror([0, 0, 1])(logo_obj)
            logo_obj = translate([0, 0, DEFAULT_TEXT_DEPTH])(logo_obj)
            model = model - logo_obj
        elif p['brand_text']:
            txt = linear_extrude(height=DEFAULT_TEXT_DEPTH + 0.1)(
                text(p['brand_text'],
                     size=p['brand_text_size'],
                     font=DEFAULT_TEXT_FONT,
                     halign="center",
                     valign="center",
                     _fn=64)
            )
            txt = mirror([0, 0, 1])(txt)
            txt = translate([0, 0, DEFAULT_TEXT_DEPTH])(txt)
            model = model - txt

        return model


if __name__ == "__main__":
    import sys
    c = Coaster()
    print(f"Generation du sous-verre...")
    print(f"Parametres: {c.params}")

    scad_path = c.save_scad()
    print(f"SCAD: {scad_path}")

    try:
        stl_path = c.render_stl()
        print(f"STL: {stl_path}")
        print("OK - Modele genere avec succes!")
    except Exception as e:
        print(f"Erreur STL (OpenSCAD requis): {e}", file=sys.stderr)
        print("Le fichier SCAD a ete genere, OpenSCAD est necessaire pour le STL.")
