"""
Equerre de Tablette pour DJ Booth - Support Plateau Bois
Bracket en L pour fixer le plateau contreplaque 18mm sur le cadre aluminium 2040.
Plaque verticale boulonnee au profil, plaque horizontale vissee dans le bois.
10 necessaires pour le booth complet.
"""
from solid2 import *
from ..base import ParametricModel
from ._constants import (
    PROFILE_W, SLOT_WIDTH, SLOT_DEPTH,
    M5_HOLE, M5_HEAD, M5_HEAD_DEPTH,
    WOOD_SCREW_HOLE, WOOD_SCREW_HEAD,
    FIT_CLEARANCE, SLOT_CLEARANCE
)


class BoothShelfBracket(ParametricModel):

    def __init__(self, **params):
        super().__init__("booth_shelf_bracket", **params)

    def default_params(self):
        return {
            'bracket_width': 40.0,
            'vertical_height': 40.0,
            'horizontal_depth': 50.0,
            'wall_thickness': 5.0,
            'gusset': True,
            'gusset_thickness': 4.0,
            'bolt_count': 1,
            'screw_count': 2,
            'fit_clearance': FIT_CLEARANCE,
        }

    def param_schema(self):
        return {
            'bracket_width': {
                'type': 'float', 'min': 20, 'max': 80, 'unit': 'mm',
                'description': 'Largeur le long du profil aluminium'
            },
            'vertical_height': {
                'type': 'float', 'min': 20, 'max': 80, 'unit': 'mm',
                'description': 'Hauteur de la plaque verticale (face du profil)'
            },
            'horizontal_depth': {
                'type': 'float', 'min': 30, 'max': 100, 'unit': 'mm',
                'description': 'Profondeur de la tablette horizontale'
            },
            'wall_thickness': {
                'type': 'float', 'min': 3, 'max': 8, 'unit': 'mm',
                'description': 'Epaisseur des plaques'
            },
            'gusset': {
                'type': 'bool',
                'description': 'Ajouter un renfort triangulaire entre les plaques'
            },
            'gusset_thickness': {
                'type': 'float', 'min': 2, 'max': 8, 'unit': 'mm',
                'description': 'Epaisseur du renfort'
            },
            'bolt_count': {
                'type': 'int', 'min': 1, 'max': 3,
                'description': 'Nombre de boulons M5 sur la plaque verticale (T-nut)'
            },
            'screw_count': {
                'type': 'int', 'min': 1, 'max': 4,
                'description': 'Nombre de vis a bois sur la plaque horizontale'
            },
            'fit_clearance': {
                'type': 'float', 'min': 0.1, 'max': 0.6, 'unit': 'mm',
                'description': 'Jeu d\'ajustement (0.3mm standard FDM)'
            },
        }

    def build(self):
        p = self.params
        bw = p['bracket_width']
        vh = p['vertical_height']
        hd = p['horizontal_depth']
        wt = p['wall_thickness']
        n_bolts = p['bolt_count']
        n_screws = p['screw_count']
        clr = p['fit_clearance']

        # -- Plaque verticale : se boulonne contre la face du profil --
        # Orientee en X=largeur, Y=epaisseur, Z=hauteur
        vertical = cube([bw, wt, vh])

        # -- Plaque horizontale : supporte le plateau bois --
        # Positionnee en haut de la plaque verticale
        horizontal = translate([0, 0, vh - wt])(
            cube([bw, hd, wt])
        )

        model = vertical + horizontal

        # -- Renfort triangulaire (gusset) entre vertical et horizontal --
        if p['gusset']:
            gt = p['gusset_thickness']
            # Triangle dans le plan Y-Z reliant les deux plaques
            gusset_h = min(vh * 0.6, 30)
            gusset_d = min(hd * 0.6, 30)
            g = hull()(
                # Base le long de la plaque verticale
                translate([(bw - gt) / 2, wt, vh - wt - gusset_h])(
                    cube([gt, 0.1, gusset_h])
                ),
                # Sommet le long de la plaque horizontale
                translate([(bw - gt) / 2, wt, vh - wt])(
                    cube([gt, gusset_d, 0.1])
                )
            )
            model = model + g

        # -- Trous de boulons M5 sur plaque verticale (pour T-nut profil) --
        bolt_spacing = vh / (n_bolts + 1)
        for i in range(n_bolts):
            z_pos = bolt_spacing * (i + 1)
            # Trou traversant en Y
            hole = translate([bw / 2, -0.1, z_pos])(
                rotate([-90, 0, 0])(
                    cylinder(d=M5_HOLE, h=wt + 0.4, _fn=32)
                )
            )
            # Fraisage tete de boulon cote exterieur
            countersink = translate([bw / 2, wt - M5_HEAD_DEPTH, z_pos])(
                rotate([-90, 0, 0])(
                    cylinder(d=M5_HEAD, h=M5_HEAD_DEPTH + 0.2, _fn=32)
                )
            )
            model = model - hole - countersink

        # -- Trous de vis a bois sur plaque horizontale (avec fraisage) --
        screw_spacing = hd / (n_screws + 1)
        for i in range(n_screws):
            y_pos = screw_spacing * (i + 1)
            # Trou traversant en Z depuis le dessous
            hole = translate([bw / 2, y_pos, vh - wt - 0.1])(
                cylinder(d=WOOD_SCREW_HOLE, h=wt + 0.4, _fn=32)
            )
            # Fraisage tete vis a bois (cote dessous = entree de la vis)
            countersink = translate([bw / 2, y_pos, vh - wt - 0.1])(
                cylinder(d=WOOD_SCREW_HEAD, h=1.5, _fn=32)
            )
            model = model - hole - countersink

        # -- Tab T-slot d'alignement sur l'arriere de la plaque verticale --
        tab_w = SLOT_WIDTH - 2 * SLOT_CLEARANCE
        tab_d = SLOT_DEPTH - SLOT_CLEARANCE
        tab_len = bw * 0.6
        tab = translate([(bw - tab_len) / 2, -tab_d, (vh - tab_w) / 2])(
            cube([tab_len, tab_d, tab_w])
        )
        model = model + tab

        return model


if __name__ == "__main__":
    import sys
    bracket = BoothShelfBracket()
    print(f"Generation equerre de tablette booth...")
    print(f"Parametres: {bracket.params}")
    scad_path = bracket.save_scad()
    print(f"SCAD: {scad_path}")
    try:
        stl_path = bracket.render_stl()
        print(f"STL: {stl_path}")
        print("OK")
    except Exception as e:
        print(f"Erreur STL: {e}", file=sys.stderr)
