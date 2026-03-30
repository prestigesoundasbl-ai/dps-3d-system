"""
Pivot Pied Rabattable Accordion DJ Booth
==========================================
Connecte le pied rabattable de chaque aile au cadre.
Pivot avec cran detent a 90 degres (deploye) et 0 degres (replie).

Piece fixe : clamp sur traverse horizontale du cadre.
Piece mobile : tient le tube du pied.
Pivot : tige acier 6mm.

Imprimable CityFab1 : ~50x40x50mm
4 necessaires (2 par aile).
"""
from solid2 import *
from ..base import ParametricModel
from ._constants import (
    M5_HOLE, FIT_CLEARANCE,
    HINGE_PIN_D,
    ACCORDION_TUBE, ACCORDION_INSERT_CLEARANCE,
)


class AccordionLegBracket(ParametricModel):

    def __init__(self, **params):
        super().__init__("accordion_leg_bracket", **params)

    def default_params(self):
        return {
            'tube_size': ACCORDION_TUBE,
            'plate_thickness': 4.0,
            'pin_diameter': HINGE_PIN_D,
            'deploy_angle': 90.0,
            'fit_clearance': FIT_CLEARANCE,
        }

    def param_schema(self):
        return {
            'tube_size': {
                'type': 'float', 'min': 20, 'max': 30, 'unit': 'mm',
                'description': 'Section tube alu',
            },
            'plate_thickness': {
                'type': 'float', 'min': 3, 'max': 6, 'unit': 'mm',
                'description': 'Epaisseur des pieces',
            },
            'pin_diameter': {
                'type': 'float', 'min': 4, 'max': 8, 'unit': 'mm',
                'description': 'Diametre axe pivot',
            },
            'deploy_angle': {
                'type': 'float', 'min': 0, 'max': 90, 'unit': 'deg',
                'description': 'Angle du pied (0=replie, 90=deploye)',
            },
            'fit_clearance': {
                'type': 'float', 'min': 0.1, 'max': 0.6, 'unit': 'mm',
                'description': 'Jeu d\'ajustement',
            },
        }

    def build(self):
        p = self.params
        tube = p['tube_size']
        pt = p['plate_thickness']
        pin_d = p['pin_diameter']
        angle = p['deploy_angle']
        clr = p['fit_clearance']

        inner = tube + 2 * clr
        model = union()

        # --- Piece fixe (clamp sur traverse horizontale) ---
        # U-channel autour du tube
        clamp_w = inner + 2 * pt
        clamp_d = inner + pt
        clamp_h = tube * 1.5

        fixed = cube([clamp_w, clamp_d, clamp_h])
        # Evidement tube
        fixed -= translate([pt, pt, -0.1])(
            cube([inner, inner + 0.1, clamp_h + 0.2])
        )

        # Oreilles de pivot de chaque cote
        ear_h = 15.0
        ear_w = pt
        ear_d = 20.0
        pivot_z = clamp_h + ear_h / 2

        for side in [0, clamp_w - ear_w]:
            ear = translate([side, (clamp_d - ear_d) / 2, clamp_h])(
                cube([ear_w, ear_d, ear_h])
            )
            # Trou pivot
            ear -= translate([side - 0.1, clamp_d / 2, pivot_z])(
                rotate([0, 90, 0])(
                    cylinder(d=pin_d + clr, h=ear_w + 0.2, _fn=24)
                )
            )
            fixed += ear

        # Trou M5 fixation
        fixed -= translate([clamp_w / 2, -0.1, clamp_h / 2])(
            rotate([-90, 0, 0])(
                cylinder(d=M5_HOLE, h=pt + 0.2, _fn=24)
            )
        )

        model += fixed

        # --- Piece mobile (tient le tube du pied) ---
        mobile_w = clamp_w - 2 * pt - 2 * clr  # rentre entre les oreilles
        mobile_d = 20.0
        mobile_h = tube * 2

        mobile = union()

        # Bras avec U-channel pour le tube du pied
        arm = cube([mobile_w, mobile_d, pt])
        # Canal pour tube du pied (perpendiculaire)
        arm += translate([(mobile_w - inner - 2 * pt) / 2, 0, pt])(
            cube([inner + 2 * pt, mobile_d, inner + pt])
        )
        arm -= translate([(mobile_w - inner) / 2, -0.1, pt + pt])(
            cube([inner, mobile_d + 0.2, inner + 0.1])
        )

        # Trou pivot dans le bras
        arm -= translate([-0.1, mobile_d / 2, 0])(
            rotate([0, 90, 0])(
                cylinder(d=pin_d + clr, h=mobile_w + 0.2, _fn=24)
            )
        )

        # Positionner la piece mobile avec rotation
        mobile += arm
        # Translater au point de pivot et tourner
        px = pt + clr
        py = (clamp_d - mobile_d) / 2
        pz = pivot_z

        mobile = translate([px, py + mobile_d / 2, pz])(
            rotate([angle, 0, 0])(
                translate([0, -mobile_d / 2, 0])(mobile)
            )
        )

        model += color([0.3, 0.3, 0.8, 0.7])(mobile)

        # --- Flexure detent (cran a 0 et 90 degres) ---
        # Petite bosse sur l'oreille qui s'engage dans une encoche du bras
        detent = translate([pt / 2, clamp_d / 2, pivot_z + ear_h / 2 - 1])(
            sphere(r=1.2, _fn=16)
        )
        model += detent

        return model
