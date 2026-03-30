"""
Amplificateur Acoustique Passif pour Telephone Parametrique
Amplifie le son du telephone par un pavillon acoustique (sans electricite).
Specifications par defaut:
  - Fente pour telephone a l'arriere
  - Pavillon qui s'elargit vers l'avant
  - Texte marque sur l'exterieur du pavillon
"""
import math
from solid2 import *
from ..base import ParametricModel
from ..brand import (
    BRAND_NAME, BRAND_NAME_SHORT, DEFAULT_TEXT_DEPTH, DEFAULT_TEXT_FONT
)
from ..utils import rounded_box
from ..logo import logo_engrave


class PhoneAmplifier(ParametricModel):

    def __init__(self, **params):
        super().__init__("phone_amplifier", **params)

    def default_params(self):
        return {
            'phone_width': 75.0,
            'phone_thickness': 10.0,
            'phone_depth_insert': 20.0,
            'horn_length': 120.0,
            'horn_mouth_width': 100.0,
            'horn_mouth_height': 60.0,
            'base_width': 130.0,
            'base_depth': 140.0,
            'base_height': 5.0,
            'wall_thickness': 3.0,
            'horn_throat_width': 30.0,
            'horn_throat_height': 15.0,
            'brand_text': BRAND_NAME,
            'brand_text_size': 6.0,
            'use_logo': True,
            'logo_width': 0.0,
        }

    def param_schema(self):
        return {
            'phone_width': {
                'type': 'float', 'min': 60, 'max': 90, 'unit': 'mm',
                'description': 'Largeur du telephone'
            },
            'phone_thickness': {
                'type': 'float', 'min': 7, 'max': 15, 'unit': 'mm',
                'description': 'Epaisseur du telephone (avec coque)'
            },
            'phone_depth_insert': {
                'type': 'float', 'min': 10, 'max': 40, 'unit': 'mm',
                'description': 'Profondeur d\'insertion du telephone'
            },
            'horn_length': {
                'type': 'float', 'min': 80, 'max': 200, 'unit': 'mm',
                'description': 'Longueur du pavillon acoustique'
            },
            'horn_mouth_width': {
                'type': 'float', 'min': 60, 'max': 160, 'unit': 'mm',
                'description': 'Largeur de l\'ouverture du pavillon'
            },
            'horn_mouth_height': {
                'type': 'float', 'min': 30, 'max': 100, 'unit': 'mm',
                'description': 'Hauteur de l\'ouverture du pavillon'
            },
            'base_width': {
                'type': 'float', 'min': 80, 'max': 200, 'unit': 'mm',
                'description': 'Largeur de la base'
            },
            'base_depth': {
                'type': 'float', 'min': 100, 'max': 250, 'unit': 'mm',
                'description': 'Profondeur de la base'
            },
            'base_height': {
                'type': 'float', 'min': 3, 'max': 10, 'unit': 'mm',
                'description': 'Epaisseur de la base'
            },
            'wall_thickness': {
                'type': 'float', 'min': 2, 'max': 5, 'unit': 'mm',
                'description': 'Epaisseur des parois du pavillon'
            },
            'horn_throat_width': {
                'type': 'float', 'min': 15, 'max': 50, 'unit': 'mm',
                'description': 'Largeur de la gorge (cote telephone)'
            },
            'horn_throat_height': {
                'type': 'float', 'min': 8, 'max': 30, 'unit': 'mm',
                'description': 'Hauteur de la gorge'
            },
            'brand_text': {
                'type': 'string',
                'description': 'Texte marque sur le pavillon'
            },
            'brand_text_size': {
                'type': 'float', 'min': 4, 'max': 12, 'unit': 'mm',
                'description': 'Taille du texte marque'
            },
            'use_logo': {
                'type': 'boolean',
                'description': 'Utiliser le vrai logo SVG Prestige Sound'
            },
            'logo_width': {
                'type': 'float', 'min': 0, 'max': 80, 'unit': 'mm',
                'description': 'Largeur du logo (0=auto)'
            },
        }

    def build(self):
        p = self.params
        pw = p['phone_width']
        pt = p['phone_thickness']
        pdi = p['phone_depth_insert']
        hl = p['horn_length']
        hmw = p['horn_mouth_width']
        hmh = p['horn_mouth_height']
        bw = p['base_width']
        bd = p['base_depth']
        bh = p['base_height']
        wt = p['wall_thickness']
        htw = p['horn_throat_width']
        hth = p['horn_throat_height']

        # Le systeme est oriente:
        # - Y+ = vers l'avant (direction du son)
        # - Le telephone est insere a l'arriere (Y = 0)
        # - Le pavillon s'ouvre vers l'avant (Y = horn_length)

        # Hauteur totale du pavillon = hauteur bouche + base
        total_h = hmh + bh

        # -- Pavillon acoustique (forme exterieure) --
        # Arriere (gorge, pres du telephone) - rectangle petit
        throat_outer_w = htw + 2 * wt
        throat_outer_h = hth + 2 * wt

        # Cote gorge (arriere, Y=0)
        throat_face = translate([
            -throat_outer_w / 2, 0, bh
        ])(
            cube([throat_outer_w, wt, throat_outer_h])
        )

        # Cote bouche (avant, Y=horn_length)
        mouth_face = translate([
            -hmw / 2, hl - wt, bh
        ])(
            cube([hmw, wt, hmh])
        )

        # Enveloppe exterieure du pavillon
        horn_outer = hull()(throat_face, mouth_face)

        # -- Canal interieur (a soustraire) --
        # Gorge interieure
        throat_inner = translate([
            -htw / 2, -0.1, bh + wt
        ])(
            cube([htw, wt + 0.2, hth])
        )

        # Bouche interieure
        mouth_inner = translate([
            -(hmw - 2 * wt) / 2, hl - wt - 0.1, bh + wt
        ])(
            cube([hmw - 2 * wt, wt + 0.2, hmh - 2 * wt])
        )

        horn_inner = hull()(throat_inner, mouth_inner)
        horn = horn_outer - horn_inner

        # -- Fente pour le telephone (a l'arriere) --
        # Le telephone s'insere verticalement dans une fente
        slot_tolerance = 1.0  # mm de jeu
        slot_w = pw + slot_tolerance
        slot_t = pt + slot_tolerance
        slot_h = pdi + 5  # Depassement au-dessus

        # La fente est centree en X, positionnee a l'arriere (Y~0)
        phone_slot = translate([
            -slot_w / 2,
            -slot_t / 2,
            bh + wt - 1  # Commence juste au-dessus de la base
        ])(
            cube([slot_w, slot_t, slot_h + hth + wt])
        )

        # Parois autour de la fente pour maintenir le telephone
        slot_wall = 3.0
        slot_outer_w = slot_w + 2 * slot_wall
        slot_outer_t = slot_t + 2 * slot_wall
        slot_outer_h = slot_h + hth + wt - 2

        slot_housing_outer = translate([
            -slot_outer_w / 2,
            -slot_outer_t / 2,
            bh
        ])(
            cube([slot_outer_w, slot_outer_t, slot_outer_h])
        )

        slot_housing_inner = translate([
            -slot_w / 2,
            -slot_t / 2,
            bh - 0.1
        ])(
            cube([slot_w, slot_t, slot_outer_h + 0.2])
        )

        phone_housing = slot_housing_outer - slot_housing_inner

        # -- Base plate --
        base = translate([-bw / 2, -slot_outer_t / 2, 0])(
            cube([bw, bd, bh])
        )

        # -- Pieds anti-derapants (petits cylindres sous la base) --
        foot_d = 8
        foot_h = 1.5
        foot_positions = [
            [-bw / 2 + foot_d, foot_d],
            [bw / 2 - foot_d, foot_d],
            [-bw / 2 + foot_d, bd - slot_outer_t / 2 - foot_d],
            [bw / 2 - foot_d, bd - slot_outer_t / 2 - foot_d],
        ]
        feet = None
        for fx, fy in foot_positions:
            foot = translate([fx, fy, -foot_h])(
                cylinder(d=foot_d, h=foot_h, _fn=32)
            )
            if feet is None:
                feet = foot
            else:
                feet = feet + foot

        # -- Assemblage --
        model = base + horn + phone_housing - phone_slot
        if feet is not None:
            model = model + feet

        # -- Logo ou texte marque sur l'exterieur du pavillon --
        if p.get('use_logo', False):
            logo_w = p['logo_width'] if p['logo_width'] > 0 else hmw * 0.5
            logo_obj = logo_engrave(width=logo_w, depth=DEFAULT_TEXT_DEPTH)
            logo_obj = rotate([90, 0, 0])(logo_obj)
            logo_obj = translate([0, hl - 0.05, bh + hmh / 2])(logo_obj)
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
            txt = rotate([90, 0, 0])(txt)
            txt = translate([0, hl - 0.05, bh + hmh / 2])(txt)
            model = model - txt

        return model


if __name__ == "__main__":
    import sys
    pa = PhoneAmplifier()
    print(f"Generation de l'amplificateur acoustique...")
    print(f"Parametres: {pa.params}")

    scad_path = pa.save_scad()
    print(f"SCAD: {scad_path}")

    try:
        stl_path = pa.render_stl()
        print(f"STL: {stl_path}")
        print("OK - Modele genere avec succes!")
    except Exception as e:
        print(f"Erreur STL (OpenSCAD requis): {e}", file=sys.stderr)
        print("Le fichier SCAD a ete genere, OpenSCAD est necessaire pour le STL.")
