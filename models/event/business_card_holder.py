"""
Porte-Cartes de Visite Parametrique
Presentoir incline pour cartes de visite DJ Prestige Sound.
Specifications par defaut:
  - Dimensions carte standard: 88x58mm
  - Inclinaison 15 degres pour visibilite
  - Gravure marque sur la face avant
"""
import math
from solid2 import *
from ..base import ParametricModel
from ..brand import (
    BRAND_NAME, BRAND_NAME_SHORT, DEFAULT_TEXT_DEPTH, DEFAULT_TEXT_FONT
)
from ..utils import rounded_box
from ..logo import logo_engrave


class BusinessCardHolder(ParametricModel):

    def __init__(self, **params):
        super().__init__("business_card_holder", **params)

    def default_params(self):
        return {
            'card_width': 88.0,
            'card_depth': 58.0,
            'capacity_height': 20.0,
            'tilt_angle': 15.0,
            'wall_thickness': 2.0,
            'base_extra': 5.0,
            'corner_radius': 2.0,
            'front_cutout': True,
            'front_cutout_width': 30.0,
            'engrave_front': True,
            'engrave_text': BRAND_NAME,
            'engrave_text_size': 5.0,
            'use_logo': True,
            'logo_width': 0.0,
        }

    def param_schema(self):
        return {
            'card_width': {
                'type': 'float', 'min': 60, 'max': 120, 'unit': 'mm',
                'description': 'Largeur de la carte de visite'
            },
            'card_depth': {
                'type': 'float', 'min': 40, 'max': 80, 'unit': 'mm',
                'description': 'Profondeur (hauteur) de la carte'
            },
            'capacity_height': {
                'type': 'float', 'min': 10, 'max': 40, 'unit': 'mm',
                'description': 'Hauteur interne (capacite en cartes empilees)'
            },
            'tilt_angle': {
                'type': 'float', 'min': 0, 'max': 30, 'unit': 'deg',
                'description': 'Angle d\'inclinaison pour visibilite'
            },
            'wall_thickness': {
                'type': 'float', 'min': 1.2, 'max': 4, 'unit': 'mm',
                'description': 'Epaisseur des parois'
            },
            'base_extra': {
                'type': 'float', 'min': 2, 'max': 15, 'unit': 'mm',
                'description': 'Marge supplementaire autour de la carte'
            },
            'corner_radius': {
                'type': 'float', 'min': 0, 'max': 5, 'unit': 'mm',
                'description': 'Rayon des coins arrondis'
            },
            'front_cutout': {
                'type': 'bool',
                'description': 'Decoupe avant pour faciliter la prise des cartes'
            },
            'front_cutout_width': {
                'type': 'float', 'min': 15, 'max': 60, 'unit': 'mm',
                'description': 'Largeur de la decoupe avant'
            },
            'engrave_front': {
                'type': 'bool',
                'description': 'Graver le texte sur la face avant'
            },
            'engrave_text': {
                'type': 'string',
                'description': 'Texte a graver'
            },
            'engrave_text_size': {
                'type': 'float', 'min': 3, 'max': 10, 'unit': 'mm',
                'description': 'Taille du texte grave'
            },
            'use_logo': {
                'type': 'boolean',
                'description': 'Utiliser le vrai logo SVG Prestige Sound'
            },
            'logo_width': {
                'type': 'float', 'min': 0, 'max': 60, 'unit': 'mm',
                'description': 'Largeur du logo (0=auto)'
            },
        }

    def build(self):
        p = self.params
        cw = p['card_width']
        cd = p['card_depth']
        ch = p['capacity_height']
        angle = p['tilt_angle']
        wt = p['wall_thickness']
        extra = p['base_extra']
        cr = p['corner_radius']

        # Dimensions exterieures du bac
        outer_w = cw + 2 * wt + extra
        outer_d = cd + 2 * wt + extra
        outer_h = ch + wt  # Fond + hauteur interne

        # Dimensions interieures (la cavite pour les cartes)
        inner_w = cw + 1  # 1mm de tolerance
        inner_d = cd + 1
        inner_h = ch + 0.1

        # -- Bac exterieur --
        outer_box = rounded_box(outer_w, outer_d, outer_h, cr)

        # -- Cavite interieure --
        inner_box = translate([wt + extra / 2, wt + extra / 2, wt])(
            rounded_box(inner_w, inner_d, inner_h, max(0, cr - wt))
        )

        tray = outer_box - inner_box

        # -- Decoupe avant pour prise des cartes (demi-cercle) --
        if p['front_cutout']:
            cutout_w = p['front_cutout_width']
            cutout_r = cutout_w / 2
            cutout = translate([outer_w / 2, -0.1, wt + ch * 0.3])(
                rotate([-90, 0, 0])(
                    cylinder(r=cutout_r, h=wt + 0.4, _fn=32)
                )
            )
            tray = tray - cutout

        # -- Appliquer l'inclinaison --
        # On incline tout le bac vers l'arriere
        # Le pivot est au centre bas du bord avant
        if angle > 0:
            # Calculer la compensation de hauteur pour que le bord avant
            # reste sur le plan Z=0
            compensate_z = outer_d * math.sin(math.radians(angle)) / 2
            tray = translate([0, 0, compensate_z])(
                rotate([angle, 0, 0])(tray)
            )
            # Base plate sous le bac incline pour stabilite
            base_h = compensate_z + 1
            base = translate([0, 0, 0])(
                rounded_box(outer_w, outer_d, base_h, cr)
            )
            tray = tray + base

        # -- Gravure logo ou texte sur la face avant --
        if p['engrave_front']:
            if p.get('use_logo', False):
                logo_w = p['logo_width'] if p['logo_width'] > 0 else outer_w * 0.5
                logo_obj = logo_engrave(width=logo_w, depth=DEFAULT_TEXT_DEPTH)
                logo_obj = rotate([90, 0, 0])(logo_obj)
                if angle > 0:
                    logo_obj = translate([outer_w / 2, -0.05, base_h / 2])(logo_obj)
                else:
                    logo_obj = translate([outer_w / 2, -0.05, outer_h / 3])(logo_obj)
                tray = tray - logo_obj
            elif p['engrave_text']:
                txt = linear_extrude(height=DEFAULT_TEXT_DEPTH + 0.1)(
                    text(p['engrave_text'],
                         size=p['engrave_text_size'],
                         font=DEFAULT_TEXT_FONT,
                         halign="center",
                         valign="center",
                         _fn=64)
                )
                txt = rotate([90, 0, 0])(txt)
                if angle > 0:
                    txt = translate([outer_w / 2, -0.05, base_h / 2])(txt)
                else:
                    txt = translate([outer_w / 2, -0.05, outer_h / 3])(txt)
                tray = tray - txt

        return tray


if __name__ == "__main__":
    import sys
    bch = BusinessCardHolder()
    print(f"Generation du porte-cartes de visite...")
    print(f"Parametres: {bch.params}")

    scad_path = bch.save_scad()
    print(f"SCAD: {scad_path}")

    try:
        stl_path = bch.render_stl()
        print(f"STL: {stl_path}")
        print("OK - Modele genere avec succes!")
    except Exception as e:
        print(f"Erreur STL (OpenSCAD requis): {e}", file=sys.stderr)
        print("Le fichier SCAD a ete genere, OpenSCAD est necessaire pour le STL.")
