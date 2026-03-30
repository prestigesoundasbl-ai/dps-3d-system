"""
Porte-Menu Parametrique
Support pour carte de menu ou document de table.
Specifications par defaut:
  - Largeur menu: 100mm
  - Profil triangulaire avec fente(s) anglee(s)
  - Option double face pour deux menus
"""
import math
from solid2 import *
from ..base import ParametricModel
from ..brand import (
    BRAND_NAME_SHORT, DEFAULT_TEXT_DEPTH, DEFAULT_TEXT_FONT
)
from ..utils import rounded_box


class MenuHolder(ParametricModel):

    def __init__(self, **params):
        super().__init__("menu_holder", **params)

    def default_params(self):
        return {
            'menu_width': 100.0,
            'base_width': 110.0,
            'base_depth': 50.0,
            'slot_angle': 75.0,
            'height': 60.0,
            'wall_thickness': 3.0,
            'slot_width': 2.0,
            'slot_depth': 30.0,
            'dual_sided': False,
            'corner_radius': 2.0,
            'engrave_brand': True,
            'brand_text_size': 4.0,
        }

    def param_schema(self):
        return {
            'menu_width': {
                'type': 'float', 'min': 60, 'max': 220, 'unit': 'mm',
                'description': 'Largeur du menu/document'
            },
            'base_width': {
                'type': 'float', 'min': 60, 'max': 230, 'unit': 'mm',
                'description': 'Largeur de la base'
            },
            'base_depth': {
                'type': 'float', 'min': 25, 'max': 100, 'unit': 'mm',
                'description': 'Profondeur de la base'
            },
            'slot_angle': {
                'type': 'float', 'min': 45, 'max': 90, 'unit': 'deg',
                'description': 'Angle de la fente par rapport a l\'horizontale'
            },
            'height': {
                'type': 'float', 'min': 30, 'max': 100, 'unit': 'mm',
                'description': 'Hauteur du support'
            },
            'wall_thickness': {
                'type': 'float', 'min': 2, 'max': 6, 'unit': 'mm',
                'description': 'Epaisseur des parois'
            },
            'slot_width': {
                'type': 'float', 'min': 1, 'max': 4, 'unit': 'mm',
                'description': 'Largeur de la fente'
            },
            'slot_depth': {
                'type': 'float', 'min': 15, 'max': 50, 'unit': 'mm',
                'description': 'Profondeur de la fente'
            },
            'dual_sided': {
                'type': 'bool',
                'description': 'Deux fentes (recto-verso) pour deux menus'
            },
            'corner_radius': {
                'type': 'float', 'min': 0, 'max': 5, 'unit': 'mm',
                'description': 'Rayon des coins arrondis'
            },
            'engrave_brand': {
                'type': 'bool',
                'description': 'Graver la marque sur le cote'
            },
            'brand_text_size': {
                'type': 'float', 'min': 2, 'max': 8, 'unit': 'mm',
                'description': 'Taille du texte de marque'
            },
        }

    def build(self):
        p = self.params
        mw = p['menu_width']
        bw = p['base_width']
        bd = p['base_depth']
        angle = p['slot_angle']
        height = p['height']
        wt = p['wall_thickness']
        sw = p['slot_width']
        sd = p['slot_depth']
        dual = p['dual_sided']

        # -- Corps principal: profil triangulaire extrude --
        # On cree un profil 2D (trapeze/triangle) puis on l'extrude en largeur
        # Vue de profil (plan YZ): base plate, puis remontee vers un sommet

        if dual:
            # Forme en A : deux pentes symetriques
            # Points du profil (Y, Z)
            profile = polygon(points=[
                [0, 0],           # Bas gauche
                [bd, 0],          # Bas droite
                [bd / 2 + wt / 2, height],  # Haut droite
                [bd / 2 - wt / 2, height],  # Haut gauche
            ])
        else:
            # Forme en coin : base plate + pente arriere
            # La fente est du cote de la pente
            back_y = bd - wt
            profile = polygon(points=[
                [0, 0],          # Bas avant
                [bd, 0],         # Bas arriere
                [bd, height * 0.3],  # Arriere monte un peu
                [wt, height],    # Sommet avant
                [0, height * 0.8],   # Avant haut
            ])

        body = linear_extrude(height=bw)(profile)
        # Rotation pour que l'extrusion soit le long de X (largeur)
        body = rotate([90, 0, 90])(body)
        # Centrer en X
        body = translate([(bw - bw) / 2, 0, 0])(body)

        # -- Fente(s) pour le menu --
        # Fente = bloc fin incline
        slot_cut_length = mw + 4
        slot_block = cube([slot_cut_length, sw, sd + 5])

        if dual:
            # Fente gauche (pente gauche)
            rot = 90 - angle
            slot1 = translate([(bw - slot_cut_length) / 2, bd / 2 - wt, height * 0.2])(
                rotate([rot, 0, 0])(
                    translate([0, -sw / 2, 0])(slot_block)
                )
            )
            # Fente droite (pente droite, symetrique)
            slot2 = translate([(bw - slot_cut_length) / 2, bd / 2 + wt, height * 0.2])(
                rotate([-rot, 0, 0])(
                    translate([0, -sw / 2, 0])(slot_block)
                )
            )
            body = body - slot1 - slot2
        else:
            # Une seule fente du cote de la pente
            rot = 90 - angle
            slot = translate([(bw - slot_cut_length) / 2, wt * 0.5, height * 0.15])(
                rotate([rot, 0, 0])(
                    translate([0, -sw / 2, 0])(slot_block)
                )
            )
            body = body - slot

        model = body

        # -- Gravure marque sur le cote --
        if p['engrave_brand']:
            txt = linear_extrude(height=DEFAULT_TEXT_DEPTH + 0.1)(
                text(BRAND_NAME_SHORT,
                     size=p['brand_text_size'],
                     font=DEFAULT_TEXT_FONT,
                     halign="center",
                     valign="center",
                     _fn=64)
            )
            # Face laterale droite (X = bw)
            txt = rotate([0, 0, 90])(rotate([90, 0, 0])(txt))
            txt = translate([bw - DEFAULT_TEXT_DEPTH, bd / 2, height * 0.3])(txt)
            model = model - txt

        return model


if __name__ == "__main__":
    import sys
    mh = MenuHolder()
    print(f"Generation du porte-menu...")
    print(f"Parametres: {mh.params}")

    scad_path = mh.save_scad()
    print(f"SCAD: {scad_path}")

    try:
        stl_path = mh.render_stl()
        print(f"STL: {stl_path}")
        print("OK - Modele genere avec succes!")
    except Exception as e:
        print(f"Erreur STL (OpenSCAD requis): {e}", file=sys.stderr)
        print("Le fichier SCAD a ete genere, OpenSCAD est necessaire pour le STL.")
