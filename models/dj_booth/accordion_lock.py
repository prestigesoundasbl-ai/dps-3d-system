"""
Verrou Ball-Lock Accordion DJ Booth
=====================================
Receptacle pour goupille ball-lock 6mm.
Maintient les ailes a 180 degres (deploye) ou 0 degres (plie).
Se monte via U-clamp sur le tube alu.

Imprimable CityFab1 : ~33x25x30mm
8 necessaires (4 par jonction centre-aile x 2 jonctions).
"""
from solid2 import *
from ..base import ParametricModel
from ._constants import (
    M5_HOLE, FIT_CLEARANCE,
    BALL_LOCK_PIN_D, BALL_LOCK_DEPTH,
    ACCORDION_TUBE, ACCORDION_INSERT_CLEARANCE,
)


class AccordionLock(ParametricModel):

    def __init__(self, **params):
        super().__init__("accordion_lock", **params)

    def default_params(self):
        return {
            'tube_size': ACCORDION_TUBE,
            'pin_diameter': BALL_LOCK_PIN_D,
            'lock_depth': BALL_LOCK_DEPTH,
            'body_width': 25.0,
            'body_height': 30.0,
            'plate_thickness': 4.0,
            'fit_clearance': FIT_CLEARANCE,
        }

    def param_schema(self):
        return {
            'tube_size': {
                'type': 'float', 'min': 20, 'max': 30, 'unit': 'mm',
                'description': 'Section tube alu',
            },
            'pin_diameter': {
                'type': 'float', 'min': 4, 'max': 8, 'unit': 'mm',
                'description': 'Diametre goupille ball-lock',
            },
            'lock_depth': {
                'type': 'float', 'min': 10, 'max': 25, 'unit': 'mm',
                'description': 'Profondeur du receptacle',
            },
            'body_width': {
                'type': 'float', 'min': 20, 'max': 35, 'unit': 'mm',
                'description': 'Largeur du bloc',
            },
            'body_height': {
                'type': 'float', 'min': 20, 'max': 40, 'unit': 'mm',
                'description': 'Hauteur du bloc',
            },
            'plate_thickness': {
                'type': 'float', 'min': 3, 'max': 6, 'unit': 'mm',
                'description': 'Epaisseur de la plaque de fixation',
            },
            'fit_clearance': {
                'type': 'float', 'min': 0.1, 'max': 0.6, 'unit': 'mm',
                'description': 'Jeu d\'ajustement',
            },
        }

    def build(self):
        p = self.params
        tube = p['tube_size']
        pin_d = p['pin_diameter']
        depth = p['lock_depth']
        bw = p['body_width']
        bh = p['body_height']
        pt = p['plate_thickness']
        clr = p['fit_clearance']

        model = union()

        # --- Bloc receptacle ---
        block = translate([-bw / 2, 0, -bh / 2])(
            cube([bw, depth + pt, bh])
        )

        # Percage principal pour la goupille
        pin_hole = translate([0, pt - 0.1, 0])(
            rotate([-90, 0, 0])(
                cylinder(d=pin_d + clr, h=depth + 0.2, _fn=32)
            )
        )
        block -= pin_hole

        # Chanfrein d'entree
        chamfer = translate([0, pt - 0.1, 0])(
            rotate([-90, 0, 0])(
                cylinder(d1=pin_d + 3, d2=pin_d + clr, h=1.5, _fn=32)
            )
        )
        block -= chamfer

        # Rainure pour billes de la goupille
        ball_groove_d = pin_d + 2.0
        ball_groove = translate([0, pt + depth * 0.6, 0])(
            rotate([-90, 0, 0])(
                cylinder(d=ball_groove_d, h=3.0, _fn=32)
            )
        )
        block -= ball_groove

        model += block

        # --- U-clamp de fixation sur le tube ---
        inner = tube + 2 * clr
        clamp_w = inner + 2 * pt
        clamp_h = tube * 1.2

        clamp = translate([-clamp_w / 2, -inner - pt, -clamp_h / 2])(
            cube([clamp_w, inner + pt, clamp_h])
        )
        # Evidement pour le tube
        clamp_cavity = translate([-inner / 2, -inner, -inner / 2])(
            cube([inner, inner + 0.1, inner])
        )
        clamp -= clamp_cavity

        # Trou M5 de fixation
        m5_hole = translate([0, -inner / 2, 0])(
            rotate([0, 90, 0])(
                cylinder(d=M5_HOLE, h=clamp_w + 2, center=True, _fn=24)
            )
        )
        clamp -= m5_hole

        model += clamp

        return model
