"""
Porte-Cles Brande Parametrique
Porte-cles rectangulaire arrondi avec anneau et texte.
Specifications par defaut:
  - Dimensions: 45x25x4mm
  - Coins arrondis
  - Trou pour anneau porte-cles
  - Texte "DPS" en relief
"""
from solid2 import *
from ..base import ParametricModel
from ..brand import (
    BRAND_NAME_SHORT, DEFAULT_TEXT_DEPTH, DEFAULT_TEXT_FONT
)
from ..logo import logo_engrave, logo_relief


class Keychain(ParametricModel):

    def __init__(self, **params):
        super().__init__("keychain", **params)

    def default_params(self):
        return {
            'width': 45.0,
            'height': 25.0,
            'thickness': 4.0,
            'hole_diameter': 5.0,
            'hole_margin': 4.0,
            'text': BRAND_NAME_SHORT,
            'text_size': 8.0,
            'text_depth': 1.0,
            'text_style': 'relief',
            'corner_radius': 3.0,
            'border_line': True,
            'border_offset': 2.0,
            'border_depth': 0.5,
            'use_logo': True,
            'logo_width': 0.0,
        }

    def param_schema(self):
        return {
            'width': {
                'type': 'float', 'min': 25, 'max': 80, 'unit': 'mm',
                'description': 'Largeur du porte-cles'
            },
            'height': {
                'type': 'float', 'min': 15, 'max': 50, 'unit': 'mm',
                'description': 'Hauteur du porte-cles'
            },
            'thickness': {
                'type': 'float', 'min': 2, 'max': 8, 'unit': 'mm',
                'description': 'Epaisseur'
            },
            'hole_diameter': {
                'type': 'float', 'min': 3, 'max': 10, 'unit': 'mm',
                'description': 'Diametre du trou pour l\'anneau'
            },
            'hole_margin': {
                'type': 'float', 'min': 2, 'max': 8, 'unit': 'mm',
                'description': 'Distance du trou au bord'
            },
            'text': {
                'type': 'string',
                'description': 'Texte a afficher'
            },
            'text_size': {
                'type': 'float', 'min': 4, 'max': 15, 'unit': 'mm',
                'description': 'Taille du texte'
            },
            'text_depth': {
                'type': 'float', 'min': 0.3, 'max': 2, 'unit': 'mm',
                'description': 'Profondeur/hauteur du texte'
            },
            'text_style': {
                'type': 'string',
                'description': 'Style du texte: relief ou engrave'
            },
            'corner_radius': {
                'type': 'float', 'min': 1, 'max': 10, 'unit': 'mm',
                'description': 'Rayon des coins arrondis'
            },
            'border_line': {
                'type': 'bool',
                'description': 'Ligne de bordure decorative gravee'
            },
            'border_offset': {
                'type': 'float', 'min': 1, 'max': 5, 'unit': 'mm',
                'description': 'Distance de la bordure au bord exterieur'
            },
            'border_depth': {
                'type': 'float', 'min': 0.2, 'max': 1, 'unit': 'mm',
                'description': 'Profondeur de la ligne de bordure'
            },
            'use_logo': {
                'type': 'boolean',
                'description': 'Utiliser le vrai logo SVG Prestige Sound'
            },
            'logo_width': {
                'type': 'float', 'min': 0, 'max': 50, 'unit': 'mm',
                'description': 'Largeur du logo (0=auto)'
            },
        }

    def build(self):
        p = self.params
        w = p['width']
        h = p['height']
        t = p['thickness']
        hole_d = p['hole_diameter']
        hole_m = p['hole_margin']
        cr = p['corner_radius']
        td = p['text_depth']

        # -- Corps principal : rectangle arrondi --
        # Utiliser minkowski d'un rectangle reduit + cylindre pour coins arrondis
        body_inner_w = w - 2 * cr
        body_inner_h = h - 2 * cr

        if cr > 0:
            body = translate([cr, cr, 0])(
                minkowski()(
                    cube([body_inner_w, body_inner_h, t / 2]),
                    cylinder(r=cr, h=t / 2, _fn=32)
                )
            )
        else:
            body = cube([w, h, t])

        # -- Trou pour anneau porte-cles --
        # Positionne a une extremite (cote gauche)
        hole_x = hole_m + hole_d / 2
        hole_y = h / 2
        hole = translate([hole_x, hole_y, -0.1])(
            cylinder(d=hole_d, h=t + 0.4, _fn=32)
        )
        # Renfort autour du trou (anneau plus epais)
        reinforce_outer = translate([hole_x, hole_y, 0])(
            cylinder(d=hole_d + hole_m, h=t, _fn=32)
        )

        body = body + reinforce_outer - hole

        # -- Logo ou Texte --
        text_area_start = hole_x + hole_d / 2 + hole_m
        text_center_x = text_area_start + (w - text_area_start) / 2
        text_center_y = h / 2

        if p.get('use_logo', False):
            logo_w = p['logo_width'] if p['logo_width'] > 0 else (w - text_area_start) * 0.8
            if p['text_style'] == 'relief':
                logo_obj = logo_relief(width=logo_w, depth=td)
                logo_obj = translate([text_center_x, text_center_y, t])(logo_obj)
                body = body + logo_obj
            else:
                logo_obj = logo_engrave(width=logo_w, depth=td)
                logo_obj = translate([text_center_x, text_center_y, t - td])(logo_obj)
                body = body - logo_obj
        elif p['text']:
            txt = linear_extrude(height=td + 0.1)(
                text(p['text'],
                     size=p['text_size'],
                     font=DEFAULT_TEXT_FONT,
                     halign="center",
                     valign="center",
                     _fn=64)
            )

            if p['text_style'] == 'relief':
                txt = translate([text_center_x, text_center_y, t])(txt)
                body = body + txt
            else:
                txt = translate([text_center_x, text_center_y, t - td])(txt)
                body = body - txt

        # -- Ligne de bordure decorative --
        if p['border_line']:
            bo = p['border_offset']
            bd_depth = p['border_depth']
            line_w = 0.6  # Largeur de la ligne gravee

            # Bordure exterieure (rectangle arrondi plus petit, en creux)
            inner_cr = max(0, cr - bo)
            if inner_cr > 0:
                border_outer = translate([bo + inner_cr, bo + inner_cr, t - bd_depth])(
                    minkowski()(
                        cube([w - 2 * bo - 2 * inner_cr,
                              h - 2 * bo - 2 * inner_cr, bd_depth / 2]),
                        cylinder(r=inner_cr, h=bd_depth / 2, _fn=32)
                    )
                )
                border_inner = translate([bo + line_w + inner_cr, bo + line_w + inner_cr,
                                         t - bd_depth - 0.1])(
                    minkowski()(
                        cube([w - 2 * bo - 2 * line_w - 2 * inner_cr,
                              h - 2 * bo - 2 * line_w - 2 * inner_cr,
                              bd_depth / 2]),
                        cylinder(r=max(0, inner_cr - line_w), h=bd_depth / 2 + 0.1, _fn=32)
                    )
                )
                border_line = border_outer - border_inner
            else:
                border_outer = translate([bo, bo, t - bd_depth])(
                    cube([w - 2 * bo, h - 2 * bo, bd_depth + 0.1])
                )
                border_inner = translate([bo + line_w, bo + line_w, t - bd_depth - 0.1])(
                    cube([w - 2 * bo - 2 * line_w,
                          h - 2 * bo - 2 * line_w, bd_depth + 0.2])
                )
                border_line = border_outer - border_inner

            body = body - border_line

        return body


if __name__ == "__main__":
    import sys
    kc = Keychain()
    print(f"Generation du porte-cles...")
    print(f"Parametres: {kc.params}")

    scad_path = kc.save_scad()
    print(f"SCAD: {scad_path}")

    try:
        stl_path = kc.render_stl()
        print(f"STL: {stl_path}")
        print("OK - Modele genere avec succes!")
    except Exception as e:
        print(f"Erreur STL (OpenSCAD requis): {e}", file=sys.stderr)
        print("Le fichier SCAD a ete genere, OpenSCAD est necessaire pour le STL.")
