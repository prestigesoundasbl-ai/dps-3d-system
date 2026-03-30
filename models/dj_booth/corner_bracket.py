"""
Equerre d'Angle pour DJ Booth - Connecteur L 2040
Joint 2 profiles aluminium 2040 a 90 degres.
8 necessaires pour le booth complet (4 haut + 4 bas).
"""
from solid2 import *
from ..base import ParametricModel
from ._constants import (
    PROFILE_W, SLOT_WIDTH, SLOT_DEPTH,
    M5_HOLE, M5_HEAD, M5_HEAD_DEPTH,
    FIT_CLEARANCE, SLOT_CLEARANCE
)


class BoothCornerBracket(ParametricModel):

    def __init__(self, **params):
        super().__init__("booth_corner_bracket", **params)

    def default_params(self):
        return {
            'arm_length': 60.0,
            'wall_thickness': 4.0,
            'profile_face': 20.0,
            'bolt_count_per_arm': 2,
            'gusset': True,
            'gusset_thickness': 4.0,
            'tslot_tab': True,
            'fit_clearance': FIT_CLEARANCE,
            'mirror': False,
        }

    def param_schema(self):
        return {
            'arm_length': {
                'type': 'float', 'min': 30, 'max': 120, 'unit': 'mm',
                'description': 'Longueur de chaque bras le long du profil'
            },
            'wall_thickness': {
                'type': 'float', 'min': 3, 'max': 8, 'unit': 'mm',
                'description': 'Epaisseur de la plaque'
            },
            'profile_face': {
                'type': 'float', 'min': 15, 'max': 40, 'unit': 'mm',
                'description': 'Largeur de face du profil alu (20 pour 2040)'
            },
            'bolt_count_per_arm': {
                'type': 'int', 'min': 1, 'max': 4,
                'description': 'Nombre de boulons M5 par bras'
            },
            'gusset': {
                'type': 'bool',
                'description': 'Ajouter un renfort triangulaire diagonal'
            },
            'gusset_thickness': {
                'type': 'float', 'min': 2, 'max': 8, 'unit': 'mm',
                'description': 'Epaisseur du renfort'
            },
            'tslot_tab': {
                'type': 'bool',
                'description': 'Ajouter des tabs d\'alignement T-slot'
            },
            'fit_clearance': {
                'type': 'float', 'min': 0.1, 'max': 0.6, 'unit': 'mm',
                'description': 'Jeu d\'ajustement (0.3mm standard FDM)'
            },
            'mirror': {
                'type': 'bool',
                'description': 'Version miroir (pour le cote oppose)'
            },
        }

    def build(self):
        p = self.params
        arm = p['arm_length']
        wt = p['wall_thickness']
        face = p['profile_face']
        n_bolts = p['bolt_count_per_arm']
        clr = p['fit_clearance']

        # -- Bras A : le long de X --
        arm_a = cube([arm, face, wt])

        # -- Bras B : le long de Y (perpendiculaire) --
        arm_b = cube([wt, arm, face])

        # -- Zone de jonction (coin) --
        corner = cube([wt, face, face])

        model = arm_a + arm_b + corner

        # -- Renfort diagonal (gusset) --
        if p['gusset']:
            gt = p['gusset_thickness']
            # Triangle reliant le bras A (X) au bras B (Y)
            gusset_size = min(arm * 0.6, 40)
            g = hull()(
                translate([wt, 0, 0])(cube([gusset_size, gt, wt])),
                translate([0, wt, 0])(cube([gt, gusset_size, wt]))
            )
            # Placer au milieu en Z de la face
            g = translate([0, 0, (face - wt) / 2])(g)
            model = model + g

        # -- Trous de boulons M5 sur bras A --
        bolt_spacing_a = (arm - wt) / (n_bolts + 1)
        for i in range(n_bolts):
            x_pos = wt + bolt_spacing_a * (i + 1)
            hole = translate([x_pos, face / 2, -0.1])(
                cylinder(d=M5_HOLE, h=wt + 0.4, _fn=32)
            )
            # Fraisage
            countersink = translate([x_pos, face / 2, wt - M5_HEAD_DEPTH])(
                cylinder(d=M5_HEAD, h=M5_HEAD_DEPTH + 0.2, _fn=32)
            )
            model = model - hole - countersink

        # -- Trous de boulons M5 sur bras B --
        bolt_spacing_b = (arm - face) / (n_bolts + 1)
        for i in range(n_bolts):
            y_pos = face + bolt_spacing_b * (i + 1)
            hole = translate([-0.1, y_pos, face / 2])(
                rotate([0, 90, 0])(
                    cylinder(d=M5_HOLE, h=wt + 0.4, _fn=32)
                )
            )
            countersink = translate([wt - M5_HEAD_DEPTH, y_pos, face / 2])(
                rotate([0, 90, 0])(
                    cylinder(d=M5_HEAD, h=M5_HEAD_DEPTH + 0.2, _fn=32)
                )
            )
            model = model - hole - countersink

        # -- Tabs T-slot (alignement dans la rainure) --
        if p['tslot_tab']:
            tab_w = SLOT_WIDTH - 2 * SLOT_CLEARANCE
            tab_d = SLOT_DEPTH - SLOT_CLEARANCE
            tab_len = arm * 0.6

            # Tab sur la face interne du bras A (sous le bras, cote profil)
            tab_a = translate([(arm - tab_len) / 2, (face - tab_w) / 2, -tab_d])(
                cube([tab_len, tab_w, tab_d])
            )
            model = model + tab_a

            # Tab sur la face interne du bras B
            tab_b = translate([-(tab_d), (arm - tab_len) / 2 + face - arm,
                              (face - tab_w) / 2])(
                rotate([0, 0, 0])(
                    cube([tab_d, tab_len, tab_w])
                )
            )
            # Simplifier : tab le long du bras B face interne
            tab_b = translate([-tab_d, face + (arm - face - tab_len) / 2,
                              (face - tab_w) / 2])(
                cube([tab_d, tab_len, tab_w])
            )
            model = model + tab_b

        # -- Miroir si necessaire --
        if p['mirror']:
            model = mirror([1, 0, 0])(model)

        return model


if __name__ == "__main__":
    import sys
    bracket = BoothCornerBracket()
    print(f"Generation equerre d'angle booth...")
    print(f"Parametres: {bracket.params}")
    scad_path = bracket.save_scad()
    print(f"SCAD: {scad_path}")
    try:
        stl_path = bracket.render_stl()
        print(f"STL: {stl_path}")
        print("OK")
    except Exception as e:
        print(f"Erreur STL: {e}", file=sys.stderr)
