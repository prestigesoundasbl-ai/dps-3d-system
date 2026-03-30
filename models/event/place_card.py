"""
Porte-Carton de Placement Parametrique
Support pour carte de placement invites (mariage, gala).
Specifications par defaut:
  - Largeur carte: 85mm (standard)
  - Fente anglee pour insertion carte papier
  - Base rectangulaire stable
"""
from solid2 import *
from ..base import ParametricModel
from ..brand import (
    BRAND_NAME_SHORT, DEFAULT_TEXT_DEPTH, DEFAULT_TEXT_FONT
)
from ..utils import rounded_box
from ..logo import logo_engrave


class PlaceCard(ParametricModel):

    def __init__(self, **params):
        super().__init__("place_card", **params)

    def default_params(self):
        return {
            'card_width': 85.0,
            'slot_width': 1.5,
            'slot_depth': 25.0,
            'slot_angle': 80.0,
            'base_width': 90.0,
            'base_depth': 30.0,
            'base_height': 15.0,
            'corner_radius': 2.0,
            'style': 'rectangle',
            'engrave_brand': True,
            'brand_text_size': 3.5,
            'use_logo': True,
            'logo_width': 0.0,
        }

    def param_schema(self):
        return {
            'card_width': {
                'type': 'float', 'min': 50, 'max': 120, 'unit': 'mm',
                'description': 'Largeur de la carte a inserer'
            },
            'slot_width': {
                'type': 'float', 'min': 0.8, 'max': 3, 'unit': 'mm',
                'description': 'Largeur de la fente pour la carte'
            },
            'slot_depth': {
                'type': 'float', 'min': 10, 'max': 40, 'unit': 'mm',
                'description': 'Profondeur de la fente (combien la carte s\'enfonce)'
            },
            'slot_angle': {
                'type': 'float', 'min': 60, 'max': 90, 'unit': 'deg',
                'description': 'Angle de la fente par rapport a l\'horizontale'
            },
            'base_width': {
                'type': 'float', 'min': 50, 'max': 130, 'unit': 'mm',
                'description': 'Largeur de la base'
            },
            'base_depth': {
                'type': 'float', 'min': 15, 'max': 60, 'unit': 'mm',
                'description': 'Profondeur de la base'
            },
            'base_height': {
                'type': 'float', 'min': 8, 'max': 30, 'unit': 'mm',
                'description': 'Hauteur de la base'
            },
            'corner_radius': {
                'type': 'float', 'min': 0, 'max': 5, 'unit': 'mm',
                'description': 'Rayon des coins arrondis'
            },
            'style': {
                'type': 'string',
                'description': 'Style de la base: rectangle'
            },
            'engrave_brand': {
                'type': 'bool',
                'description': 'Graver la marque sur le cote'
            },
            'brand_text_size': {
                'type': 'float', 'min': 2, 'max': 6, 'unit': 'mm',
                'description': 'Taille du texte de marque'
            },
            'use_logo': {
                'type': 'boolean',
                'description': 'Utiliser le vrai logo SVG Prestige Sound'
            },
            'logo_width': {
                'type': 'float', 'min': 0, 'max': 30, 'unit': 'mm',
                'description': 'Largeur du logo (0=auto)'
            },
        }

    def build(self):
        p = self.params
        cw = p['card_width']
        sw = p['slot_width']
        sd = p['slot_depth']
        sa = p['slot_angle']
        bw = p['base_width']
        bd = p['base_depth']
        bh = p['base_height']
        cr = p['corner_radius']

        # -- Base avec coins arrondis --
        base = rounded_box(bw, bd, bh, cr)

        # -- Fente anglee pour la carte --
        # La fente traverse le bloc de gauche a droite (axe X)
        # On cree un bloc fin, incline, qu'on soustrait
        # Largeur de coupe = largeur carte + tolerance
        cut_width = cw + 2
        # Hauteur de coupe suffisante pour depasser la base
        cut_height = sd + 5

        slot_cut = translate([0, 0, 0])(
            cube([cut_width, sw, cut_height])
        )

        # Incliner la fente selon l'angle
        # Centrer la fente en X sur la base
        x_offset = (bw - cut_width) / 2
        # Positionner au centre de la profondeur
        y_offset = bd / 2 - sw / 2

        # Rotation autour de l'axe X (l'axe de la largeur de la carte)
        # L'angle est par rapport a la verticale, donc on rotate de (90 - angle)
        import math
        rot_angle = 90 - sa  # 10 degres pour un angle de 80

        slot = translate([x_offset, y_offset, bh * 0.4])(
            rotate([rot_angle, 0, 0])(
                translate([0, -sw / 2, 0])(slot_cut)
            )
        )

        model = base - slot

        # -- Gravure logo ou marque sur la face avant --
        if p['engrave_brand']:
            if p.get('use_logo', False):
                logo_w = p['logo_width'] if p['logo_width'] > 0 else bw * 0.25
                logo_obj = logo_engrave(width=logo_w, depth=DEFAULT_TEXT_DEPTH)
                logo_obj = rotate([90, 0, 0])(logo_obj)
                logo_obj = translate([bw / 2, -0.05, bh / 3])(logo_obj)
                model = model - logo_obj
            else:
                txt = linear_extrude(height=DEFAULT_TEXT_DEPTH + 0.1)(
                    text(BRAND_NAME_SHORT,
                         size=p['brand_text_size'],
                         font=DEFAULT_TEXT_FONT,
                         halign="center",
                         valign="center",
                         _fn=64)
                )
                txt = rotate([90, 0, 0])(txt)
                txt = translate([bw / 2, -0.05, bh / 3])(txt)
                model = model - txt

        return model


if __name__ == "__main__":
    import sys
    pc = PlaceCard()
    print(f"Generation du porte-carton de placement...")
    print(f"Parametres: {pc.params}")

    scad_path = pc.save_scad()
    print(f"SCAD: {scad_path}")

    try:
        stl_path = pc.render_stl()
        print(f"STL: {stl_path}")
        print("OK - Modele genere avec succes!")
    except Exception as e:
        print(f"Erreur STL (OpenSCAD requis): {e}", file=sys.stderr)
        print("Le fichier SCAD a ete genere, OpenSCAD est necessaire pour le STL.")
