"""
Etagere pour Pied d'Enceinte Parametrique
Se fixe sur le tube d'un pied d'enceinte standard.
Specifications par defaut:
  - Diametre tube: 35mm (standard)
  - Largeur etagere: 200mm
  - Profondeur etagere: 150mm
  - Pince fendue avec vis de serrage
"""
import math
from solid2 import *
from ..base import ParametricModel
from ..brand import (
    BRAND_NAME_SHORT, DEFAULT_TEXT_DEPTH, DEFAULT_TEXT_FONT,
    DEFAULT_WALL_THICKNESS
)
from ..utils import pole_mount, brand_text
from ..logo import logo_engrave


class SpeakerShelf(ParametricModel):

    def __init__(self, **params):
        super().__init__("speaker_shelf", **params)

    def default_params(self):
        return {
            'pole_diameter': 35.0,
            'shelf_width': 200.0,
            'shelf_depth': 150.0,
            'shelf_thickness': 5.0,
            'clamp_height': 40.0,
            'clamp_wall': 4.0,
            'clamp_gap': 3.0,
            'bolt_hole_diameter': 6.0,
            'reinforcement_height': 20.0,
            'engrave_text': BRAND_NAME_SHORT,
            'use_logo': True,
            'logo_width': 0.0,
        }

    def param_schema(self):
        return {
            'pole_diameter': {
                'type': 'float', 'min': 20, 'max': 50, 'unit': 'mm',
                'description': 'Diametre du tube du pied d\'enceinte'
            },
            'shelf_width': {
                'type': 'float', 'min': 100, 'max': 400, 'unit': 'mm',
                'description': 'Largeur de l\'etagere'
            },
            'shelf_depth': {
                'type': 'float', 'min': 80, 'max': 300, 'unit': 'mm',
                'description': 'Profondeur de l\'etagere'
            },
            'shelf_thickness': {
                'type': 'float', 'min': 3, 'max': 10, 'unit': 'mm',
                'description': 'Epaisseur du plateau'
            },
            'clamp_height': {
                'type': 'float', 'min': 20, 'max': 80, 'unit': 'mm',
                'description': 'Hauteur de la pince de fixation'
            },
            'clamp_wall': {
                'type': 'float', 'min': 2, 'max': 8, 'unit': 'mm',
                'description': 'Epaisseur de la paroi de pince'
            },
            'clamp_gap': {
                'type': 'float', 'min': 1, 'max': 5, 'unit': 'mm',
                'description': 'Largeur de la fente de la pince'
            },
            'bolt_hole_diameter': {
                'type': 'float', 'min': 3, 'max': 10, 'unit': 'mm',
                'description': 'Diametre du trou de boulon de serrage'
            },
            'reinforcement_height': {
                'type': 'float', 'min': 10, 'max': 40, 'unit': 'mm',
                'description': 'Hauteur des renforts sous l\'etagere'
            },
            'engrave_text': {
                'type': 'string',
                'description': 'Texte grave sur l\'etagere'
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
        pd = p['pole_diameter']
        sw = p['shelf_width']
        sd = p['shelf_depth']
        st = p['shelf_thickness']
        ch = p['clamp_height']
        cw = p['clamp_wall']
        gap = p['clamp_gap']
        bolt_d = p['bolt_hole_diameter']
        rh = p['reinforcement_height']

        outer_r = pd / 2 + cw
        inner_r = pd / 2

        # -- Pince cylindrique pour le tube --
        clamp_outer = cylinder(r=outer_r, h=ch, _fn=64)
        clamp_inner = cylinder(r=inner_r, h=ch + 0.2, _fn=64)
        clamp = clamp_outer - clamp_inner

        # Fente de la pince (pour serrage)
        slit = translate([-gap / 2, outer_r * 0.3, -0.1])(
            cube([gap, outer_r + 1, ch + 0.4])
        )
        clamp = clamp - slit

        # Oreilles de serrage de chaque cote de la fente
        ear_width = 15
        ear_depth = cw
        ear = translate([-ear_width / 2 - gap / 2, outer_r, 0])(
            cube([ear_width, ear_depth, ch])
        )
        ear_r = translate([gap / 2 - ear_width / 2 + ear_width, outer_r, 0])(
            cube([ear_width, ear_depth, ch])
        )

        # Trous de boulons dans les oreilles
        bolt1 = translate([-gap / 2 - ear_width / 2, outer_r + ear_depth / 2, ch / 2])(
            rotate([0, 90, 0])(
                cylinder(d=bolt_d, h=gap + ear_width * 2 + 1, _fn=32, center=True)
            )
        )

        clamp = clamp + ear + ear_r - bolt1

        # Positionner la pince : centre a l'origine, etagere part vers X positif
        # La pince est dans le plan XY, etagere vers Y negatif (devant)

        # -- Plateau de l'etagere --
        # L'etagere s'etend depuis la pince vers un cote
        shelf_x_offset = -sw / 2
        shelf_y_offset = -outer_r
        shelf = translate([shelf_x_offset, shelf_y_offset - sd, ch - st])(
            cube([sw, sd, st])
        )

        # -- Renforts triangulaires sous l'etagere --
        # Nervure gauche
        rib_thickness = cw
        rib_l = translate([shelf_x_offset + sw * 0.15, shelf_y_offset - sd * 0.6, ch - st - rh])(
            hull()(
                cube([rib_thickness, 1, rh]),
                translate([0, sd * 0.6, rh])(cube([rib_thickness, 1, 0.1]))
            )
        )
        # Nervure droite
        rib_r = translate([shelf_x_offset + sw * 0.85 - rib_thickness,
                           shelf_y_offset - sd * 0.6, ch - st - rh])(
            hull()(
                cube([rib_thickness, 1, rh]),
                translate([0, sd * 0.6, rh])(cube([rib_thickness, 1, 0.1]))
            )
        )

        # -- Connexion pince-etagere --
        # Bloc de jonction entre la pince et le plateau
        junction_width = outer_r * 2
        junction = translate([-junction_width / 2, shelf_y_offset, ch - st - rh])(
            cube([junction_width, outer_r, rh + st])
        )

        model = clamp + shelf + rib_l + rib_r + junction

        # -- Gravure logo ou texte sur le bord avant de l'etagere --
        if p.get('use_logo', False):
            logo_w = p['logo_width'] if p['logo_width'] > 0 else sw * 0.3
            logo_obj = logo_engrave(width=logo_w, depth=DEFAULT_TEXT_DEPTH)
            logo_obj = rotate([90, 0, 0])(logo_obj)
            logo_obj = translate([0, shelf_y_offset - sd - 0.05, ch - st / 2])(logo_obj)
            model = model - logo_obj
        elif p['engrave_text']:
            txt = linear_extrude(height=DEFAULT_TEXT_DEPTH + 0.1)(
                text(p['engrave_text'],
                     size=6,
                     font=DEFAULT_TEXT_FONT,
                     halign="center",
                     valign="center")
            )
            txt = rotate([90, 0, 0])(txt)
            txt = translate([0, shelf_y_offset - sd - 0.05, ch - st / 2])(txt)
            model = model - txt

        return model


if __name__ == "__main__":
    import sys
    shelf = SpeakerShelf()
    print(f"Generation de l'etagere pied d'enceinte...")
    print(f"Parametres: {shelf.params}")

    scad_path = shelf.save_scad()
    print(f"SCAD: {scad_path}")

    try:
        stl_path = shelf.render_stl()
        print(f"STL: {stl_path}")
        print("OK - Modele genere avec succes!")
    except Exception as e:
        print(f"Erreur STL (OpenSCAD requis): {e}", file=sys.stderr)
        print("Le fichier SCAD a ete genere, OpenSCAD est necessaire pour le STL.")
