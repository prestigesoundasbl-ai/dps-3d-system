"""
Numero de Table Parametrique
Support avec numero pour tables d'evenement (mariage, gala, corporate).
Specifications par defaut:
  - Numero: 1 (de 1 a 99)
  - Style debout avec base circulaire
  - Numero extrude sur plaque verticale
  - Option gravure marque sur la base
"""
from solid2 import *
from ..base import ParametricModel
from ..brand import (
    BRAND_NAME, BRAND_NAME_SHORT, DEFAULT_TEXT_DEPTH, DEFAULT_TEXT_FONT
)
from ..logo import logo_engrave


class TableNumber(ParametricModel):

    def __init__(self, **params):
        super().__init__("table_number", **params)

    def default_params(self):
        return {
            'number': 1,
            'style': 'standing',
            'height': 100.0,
            'width': 60.0,
            'thickness': 5.0,
            'base_diameter': 50.0,
            'base_height': 5.0,
            'font_size': 30.0,
            'text_depth': 2.0,
            'engrave_brand': True,
            'brand_text_size': 4.0,
            'use_logo': True,
            'logo_width': 0.0,
        }

    def param_schema(self):
        return {
            'number': {
                'type': 'int', 'min': 1, 'max': 99, 'unit': '',
                'description': 'Numero de table a afficher'
            },
            'style': {
                'type': 'string',
                'description': 'Style: standing (debout)'
            },
            'height': {
                'type': 'float', 'min': 50, 'max': 200, 'unit': 'mm',
                'description': 'Hauteur totale du support'
            },
            'width': {
                'type': 'float', 'min': 30, 'max': 120, 'unit': 'mm',
                'description': 'Largeur de la plaque du numero'
            },
            'thickness': {
                'type': 'float', 'min': 3, 'max': 10, 'unit': 'mm',
                'description': 'Epaisseur de la plaque'
            },
            'base_diameter': {
                'type': 'float', 'min': 30, 'max': 100, 'unit': 'mm',
                'description': 'Diametre de la base circulaire'
            },
            'base_height': {
                'type': 'float', 'min': 3, 'max': 15, 'unit': 'mm',
                'description': 'Epaisseur de la base'
            },
            'font_size': {
                'type': 'float', 'min': 15, 'max': 60, 'unit': 'mm',
                'description': 'Taille du numero'
            },
            'text_depth': {
                'type': 'float', 'min': 0.5, 'max': 4, 'unit': 'mm',
                'description': 'Profondeur d\'extrusion du numero'
            },
            'engrave_brand': {
                'type': 'bool',
                'description': 'Graver le nom de marque sur la base'
            },
            'brand_text_size': {
                'type': 'float', 'min': 2, 'max': 8, 'unit': 'mm',
                'description': 'Taille du texte de marque'
            },
            'use_logo': {
                'type': 'boolean',
                'description': 'Utiliser le vrai logo SVG sur la base'
            },
            'logo_width': {
                'type': 'float', 'min': 0, 'max': 40, 'unit': 'mm',
                'description': 'Largeur du logo (0=auto)'
            },
        }

    def build(self):
        p = self.params
        num = p['number']
        height = p['height']
        width = p['width']
        thick = p['thickness']
        base_d = p['base_diameter']
        base_h = p['base_height']
        fs = p['font_size']
        td = p['text_depth']

        # -- Base circulaire --
        base = cylinder(d=base_d, h=base_h, _fn=64)

        # -- Tige verticale (relie la base a la plaque) --
        stem_width = thick * 1.5
        stem_depth = thick
        stem = translate([-stem_width / 2, -stem_depth / 2, base_h])(
            cube([stem_width, stem_depth, height - base_h - width * 0.6])
        )

        # Transition arrondie base vers tige
        fillet = translate([0, 0, base_h])(
            hull()(
                cylinder(d=stem_width * 2.5, h=0.1, _fn=32),
                translate([0, 0, stem_width])(
                    cube([stem_width, stem_depth, 0.1], center=True)
                )
            )
        )

        # -- Plaque du numero (en haut) --
        plate_bottom = height - width * 0.8
        plate = translate([-width / 2, -thick / 2, plate_bottom])(
            cube([width, thick, width * 0.8])
        )

        # Coins arrondis pour la plaque (chanfrein simple en haut)
        plate_top = plate_bottom + width * 0.8

        # -- Numero extrude en relief sur la plaque --
        num_text = str(num)
        number_extrude = linear_extrude(height=td)(
            text(num_text,
                 size=fs,
                 font=DEFAULT_TEXT_FONT,
                 halign="center",
                 valign="center",
                 _fn=64)
        )
        # Positionner sur la face avant de la plaque
        number_front = translate([0, thick / 2 - 0.1, plate_bottom + width * 0.4])(
            rotate([90, 0, 0])(
                rotate([0, 0, 0])(number_extrude)
            )
        )
        # Numero au dos aussi (miroir)
        number_back = translate([0, -thick / 2 + 0.1, plate_bottom + width * 0.4])(
            rotate([-90, 0, 0])(
                rotate([0, 0, 0])(number_extrude)
            )
        )

        model = base + fillet + stem + plate + number_front + number_back

        # -- Gravure marque sur le bord de la base --
        if p['engrave_brand']:
            if p.get('use_logo', False):
                logo_w = p['logo_width'] if p['logo_width'] > 0 else base_d * 0.5
                logo_obj = logo_engrave(width=logo_w, depth=DEFAULT_TEXT_DEPTH)
                logo_obj = translate([0, base_d / 2 - logo_w * 0.3,
                                     base_h - DEFAULT_TEXT_DEPTH])(logo_obj)
                model = model - logo_obj
            else:
                brand = linear_extrude(height=DEFAULT_TEXT_DEPTH + 0.1)(
                    text(BRAND_NAME_SHORT,
                         size=p['brand_text_size'],
                         font=DEFAULT_TEXT_FONT,
                         halign="center",
                         valign="center",
                         _fn=64)
                )
                brand = translate([0, base_d / 2 - p['brand_text_size'] - 2,
                                  base_h - DEFAULT_TEXT_DEPTH])(brand)
                model = model - brand

        return model


if __name__ == "__main__":
    import sys
    tn = TableNumber(number=7)
    print(f"Generation du numero de table...")
    print(f"Parametres: {tn.params}")

    scad_path = tn.save_scad()
    print(f"SCAD: {scad_path}")

    try:
        stl_path = tn.render_stl()
        print(f"STL: {stl_path}")
        print("OK - Modele genere avec succes!")
    except Exception as e:
        print(f"Erreur STL (OpenSCAD requis): {e}", file=sys.stderr)
        print("Le fichier SCAD a ete genere, OpenSCAD est necessaire pour le STL.")
