"""
Receptacle Quick-Release Pin pour DJ Booth
Logement imprime 3D qui recoit un ball-lock pin standard 6mm.
Permet de verrouiller le cadre en position depliee sans outil.
Montage : se fixe sur le profil 2040 via T-slot + boulon M5.
8 necessaires (2 par coin de verrouillage). ~8g chacun.
"""
from solid2 import *
from ..base import ParametricModel
from ._constants import (
    PROFILE_W, SLOT_WIDTH, SLOT_DEPTH,
    M5_HOLE, M5_HEAD, M5_HEAD_DEPTH,
    FIT_CLEARANCE, SLOT_CLEARANCE,
    BALL_LOCK_PIN_D, BALL_LOCK_BODY_D, BALL_LOCK_DEPTH
)


class BoothQuickPin(ParametricModel):

    def __init__(self, **params):
        super().__init__("booth_quick_pin", **params)

    def default_params(self):
        return {
            'pin_diameter': BALL_LOCK_PIN_D,
            'body_diameter': BALL_LOCK_BODY_D,
            'receptacle_depth': BALL_LOCK_DEPTH,
            'block_width': 20.0,
            'block_depth': 20.0,
            'block_height': 25.0,
            'wall_thickness': 4.0,
            'bolt_mount': True,
            'tslot_tab': True,
            'chamfer': 1.0,
            'fit_clearance': FIT_CLEARANCE,
        }

    def param_schema(self):
        return {
            'pin_diameter': {
                'type': 'float', 'min': 4, 'max': 10, 'unit': 'mm',
                'description': 'Diametre du ball-lock pin (6mm standard)'
            },
            'body_diameter': {
                'type': 'float', 'min': 8, 'max': 16, 'unit': 'mm',
                'description': 'Diametre du corps du pin (collerette)'
            },
            'receptacle_depth': {
                'type': 'float', 'min': 10, 'max': 25, 'unit': 'mm',
                'description': 'Profondeur du trou receptacle'
            },
            'block_width': {
                'type': 'float', 'min': 15, 'max': 30, 'unit': 'mm',
                'description': 'Largeur du bloc'
            },
            'block_depth': {
                'type': 'float', 'min': 15, 'max': 30, 'unit': 'mm',
                'description': 'Profondeur du bloc'
            },
            'block_height': {
                'type': 'float', 'min': 15, 'max': 40, 'unit': 'mm',
                'description': 'Hauteur du bloc'
            },
            'wall_thickness': {
                'type': 'float', 'min': 2, 'max': 8, 'unit': 'mm',
                'description': 'Epaisseur minimum de paroi'
            },
            'bolt_mount': {
                'type': 'bool',
                'description': 'Trou M5 pour montage sur profil via T-nut'
            },
            'tslot_tab': {
                'type': 'bool',
                'description': 'Tab d\'alignement T-slot'
            },
            'chamfer': {
                'type': 'float', 'min': 0, 'max': 3, 'unit': 'mm',
                'description': 'Chanfrein d\'entree du pin'
            },
            'fit_clearance': {
                'type': 'float', 'min': 0.1, 'max': 0.6, 'unit': 'mm',
                'description': 'Jeu d\'ajustement'
            },
        }

    def build(self):
        p = self.params
        pin_d = p['pin_diameter']
        body_d = p['body_diameter']
        rec_depth = p['receptacle_depth']
        bw = p['block_width']
        bd = p['block_depth']
        bh = p['block_height']
        wt = p['wall_thickness']
        chamfer = p['chamfer']
        clr = p['fit_clearance']

        # -- Bloc principal --
        block = cube([bw, bd, bh])

        # -- Trou receptacle pour le pin (par le haut) --
        pin_r = (pin_d + clr) / 2
        receptacle = translate([bw / 2, bd / 2, bh - rec_depth])(
            cylinder(r=pin_r, h=rec_depth + 0.1, _fn=32)
        )
        block = block - receptacle

        # -- Chanfrein d'entree (conique pour guider le pin) --
        if chamfer > 0:
            entry_cone = translate([bw / 2, bd / 2, bh - 0.01])(
                cylinder(r1=pin_r + chamfer, r2=pin_r, h=chamfer, _fn=32)
            )
            block = block - entry_cone

        # -- Rainure pour les billes du ball-lock --
        # A mi-profondeur, un elargissement annulaire pour les billes
        ball_groove_z = bh - rec_depth + rec_depth * 0.6
        ball_groove_r = (body_d + clr) / 2
        groove = translate([bw / 2, bd / 2, ball_groove_z])(
            cylinder(r=ball_groove_r, h=2.0, _fn=32)
        )
        block = block - groove

        # -- Montage sur profil 2040 --
        if p['bolt_mount']:
            # Trou M5 horizontal (traverse le bloc pour visser dans T-nut)
            bolt_hole = translate([bw / 2, -0.1, bh / 2])(
                rotate([-90, 0, 0])(
                    cylinder(d=M5_HOLE, h=bd + 0.4, _fn=32)
                )
            )
            # Fraisage
            cs = translate([bw / 2, bd - M5_HEAD_DEPTH, bh / 2])(
                rotate([-90, 0, 0])(
                    cylinder(d=M5_HEAD, h=M5_HEAD_DEPTH + 0.2, _fn=32)
                )
            )
            block = block - bolt_hole - cs

        # -- Tab T-slot --
        if p['tslot_tab']:
            tab_w = SLOT_WIDTH - 2 * SLOT_CLEARANCE
            tab_d = SLOT_DEPTH - SLOT_CLEARANCE
            tab_len = bw * 0.6
            tab = translate([(bw - tab_len) / 2, -tab_d, (bh - tab_w) / 2])(
                cube([tab_len, tab_d, tab_w])
            )
            block = block + tab

        return block


if __name__ == "__main__":
    import sys
    pin = BoothQuickPin()
    print(f"Generation receptacle quick-pin booth...")
    print(f"Parametres: {pin.params}")
    scad_path = pin.save_scad()
    print(f"SCAD: {scad_path}")
    try:
        stl_path = pin.render_stl()
        print(f"STL: {stl_path}")
        print("OK")
    except Exception as e:
        print(f"Erreur STL: {e}", file=sys.stderr)
