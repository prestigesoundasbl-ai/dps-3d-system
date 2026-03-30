"""
Support Tablette/iPad Parametrique pour Booth DJ
Specifications par defaut:
  - Largeur: 200mm, Profondeur: 120mm, Hauteur arriere: 100mm
  - Angle: 15 degres
  - Texte grave: "DJ PRESTIGE SOUND"
  - Levre avant pour retenir la tablette
  - Passage cable a l'arriere
"""
import math
from solid2 import *
from ..base import ParametricModel
from ..brand import BRAND_NAME, DEFAULT_TEXT_DEPTH, DEFAULT_TEXT_FONT
from ..logo import logo_engrave


class TabletStand(ParametricModel):

    def __init__(self, **params):
        super().__init__("tablet_stand", **params)

    def default_params(self):
        return {
            'width': 200.0,
            'depth': 120.0,
            'rear_height': 100.0,
            'angle': 15.0,
            'wall': 3.0,
            'lip_height': 15.0,
            'lip_depth': 10.0,
            'cable_slot_width': 30.0,
            'cable_slot_height': 10.0,
            'engrave_text': BRAND_NAME,
            'engrave_depth': DEFAULT_TEXT_DEPTH,
            'engrave_size': 8.0,
            'use_logo': True,
            'logo_width': 0.0,
            'corner_radius': 3.0,
        }

    def param_schema(self):
        return {
            'width':       {'type': 'float', 'min': 100, 'max': 400, 'unit': 'mm',
                            'description': 'Largeur du support'},
            'depth':       {'type': 'float', 'min': 60, 'max': 250, 'unit': 'mm',
                            'description': 'Profondeur (avant-arriere)'},
            'rear_height': {'type': 'float', 'min': 40, 'max': 200, 'unit': 'mm',
                            'description': 'Hauteur a l\'arriere'},
            'angle':       {'type': 'float', 'min': 5, 'max': 45, 'unit': 'deg',
                            'description': 'Angle d\'inclinaison'},
            'wall':        {'type': 'float', 'min': 1.5, 'max': 6, 'unit': 'mm',
                            'description': 'Epaisseur des parois'},
            'lip_height':  {'type': 'float', 'min': 5, 'max': 30, 'unit': 'mm',
                            'description': 'Hauteur de la levre avant'},
            'lip_depth':   {'type': 'float', 'min': 5, 'max': 20, 'unit': 'mm',
                            'description': 'Profondeur de la levre avant'},
            'cable_slot_width': {'type': 'float', 'min': 10, 'max': 60, 'unit': 'mm',
                                 'description': 'Largeur passage cable'},
            'cable_slot_height': {'type': 'float', 'min': 5, 'max': 20, 'unit': 'mm',
                                  'description': 'Hauteur passage cable'},
            'engrave_text': {'type': 'string',
                             'description': 'Texte grave sur la face avant'},
            'engrave_size': {'type': 'float', 'min': 4, 'max': 20, 'unit': 'mm',
                             'description': 'Taille police gravure'},
            'use_logo': {'type': 'boolean',
                         'description': 'Utiliser le vrai logo SVG Prestige Sound'},
            'logo_width': {'type': 'float', 'min': 0, 'max': 100, 'unit': 'mm',
                           'description': 'Largeur du logo (0=auto)'},
        }

    def build(self):
        p = self.params
        w = p['width']
        d = p['depth']
        rh = p['rear_height']
        ang = p['angle']
        wall = p['wall']
        r = p['corner_radius']

        # Hauteur avant calculee depuis l'angle
        front_h = rh - d * math.tan(math.radians(ang))
        front_h = max(front_h, p['lip_height'] + wall + 5)

        # Corps principal : coque inclinee via hull de 2 faces
        # Face avant (basse)
        front_face = cube([w, wall, front_h])
        # Face arriere (haute)
        back_face = translate([0, d - wall, 0])(cube([w, wall, rh]))
        # Enveloppe = forme inclinee pleine
        body = hull()(front_face, back_face)

        # Evider l'interieur
        inner_front = translate([wall, wall, wall])(
            cube([w - 2 * wall, wall, front_h - wall])
        )
        inner_back = translate([wall, d - 2 * wall, wall])(
            cube([w - 2 * wall, wall, rh - wall])
        )
        inner = hull()(inner_front, inner_back)
        body = body - inner

        # Levre avant (retient la tablette)
        lip = cube([w, p['lip_depth'], p['lip_height']])
        body = body + lip

        # Passage cable a l'arriere (centre)
        csw = p['cable_slot_width']
        csh = p['cable_slot_height']
        cable_slot = translate([(w - csw) / 2, d - wall - 0.5, rh - csh - 5])(
            cube([csw, wall + 1, csh])
        )
        body = body - cable_slot

        # Gravure sur la face avant de la levre
        if p.get('use_logo', False):
            # Vrai logo SVG Prestige Sound
            logo_w = p['logo_width'] if p['logo_width'] > 0 else p['lip_height'] * 0.8
            logo_obj = logo_engrave(width=logo_w, depth=p['engrave_depth'])
            logo_obj = rotate([90, 0, 0])(logo_obj)
            logo_obj = translate([w / 2, -0.05, p['lip_height'] / 2])(logo_obj)
            body = body - logo_obj
        elif p['engrave_text']:
            # Texte simple
            txt = linear_extrude(height=p['engrave_depth'] + 0.1)(
                text(p['engrave_text'],
                     size=p['engrave_size'],
                     font=DEFAULT_TEXT_FONT,
                     halign="center",
                     valign="center")
            )
            txt = rotate([90, 0, 0])(txt)
            txt = translate([w / 2, -0.05, p['lip_height'] / 2])(txt)
            body = body - txt

        return body


if __name__ == "__main__":
    import sys
    stand = TabletStand()
    print(f"Generation du support tablette...")
    print(f"Parametres: {stand.params}")

    scad_path = stand.save_scad()
    print(f"SCAD: {scad_path}")

    try:
        stl_path = stand.render_stl()
        print(f"STL: {stl_path}")
        print("OK - Modele genere avec succes!")
    except Exception as e:
        print(f"Erreur STL (OpenSCAD requis): {e}", file=sys.stderr)
        print("Le fichier SCAD a ete genere, OpenSCAD est necessaire pour le STL.")
