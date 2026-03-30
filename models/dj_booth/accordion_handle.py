"""
Poignee Transport Accordion DJ Booth
======================================
Poignee ergonomique montee sous le cadre pour transport du booth plie.
Grip cylindrique creux (legere), 2 montants + plaque de fixation M5.

Imprimable CityFab1 : ~120x40x55mm
2 necessaires (une de chaque cote du booth plie).
"""
from solid2 import *
from ..base import ParametricModel
from ._constants import (
    M5_HOLE, M5_HEAD, M5_HEAD_DEPTH,
    FIT_CLEARANCE,
)


class AccordionHandle(ParametricModel):

    def __init__(self, **params):
        super().__init__("accordion_handle", **params)

    def default_params(self):
        return {
            'grip_length': 120.0,
            'grip_diameter': 28.0,
            'grip_wall': 3.0,
            'standoff_height': 35.0,
            'plate_width': 40.0,
            'plate_thickness': 4.0,
        }

    def param_schema(self):
        return {
            'grip_length': {
                'type': 'float', 'min': 80, 'max': 160, 'unit': 'mm',
                'description': 'Longueur du grip',
            },
            'grip_diameter': {
                'type': 'float', 'min': 22, 'max': 35, 'unit': 'mm',
                'description': 'Diametre du grip',
            },
            'grip_wall': {
                'type': 'float', 'min': 2, 'max': 5, 'unit': 'mm',
                'description': 'Epaisseur paroi grip (creux)',
            },
            'standoff_height': {
                'type': 'float', 'min': 20, 'max': 60, 'unit': 'mm',
                'description': 'Hauteur des montants',
            },
            'plate_width': {
                'type': 'float', 'min': 30, 'max': 60, 'unit': 'mm',
                'description': 'Largeur de la plaque de fixation',
            },
            'plate_thickness': {
                'type': 'float', 'min': 3, 'max': 6, 'unit': 'mm',
                'description': 'Epaisseur plaque de fixation',
            },
        }

    def build(self):
        p = self.params
        gl = p['grip_length']
        gd = p['grip_diameter']
        gw = p['grip_wall']
        sh = p['standoff_height']
        pw = p['plate_width']
        pt = p['plate_thickness']

        gr = gd / 2

        model = union()

        # --- Plaque de fixation (en haut) ---
        plate = translate([-gl / 2, -pw / 2, sh + gr])(
            cube([gl, pw, pt])
        )
        # 4 trous M5 (coins)
        bolt_inset = 10
        for dx in [-gl / 2 + bolt_inset, gl / 2 - bolt_inset]:
            for dy in [-pw / 2 + bolt_inset, pw / 2 - bolt_inset]:
                hole = translate([dx, dy, sh + gr - 0.1])(
                    cylinder(d=M5_HOLE, h=pt + 0.2, _fn=24)
                )
                plate -= hole
        model += plate

        # --- 2 montants verticaux ---
        standoff_w = gd
        standoff_t = gw + 2
        for dx in [-gl / 2 + standoff_w / 2, gl / 2 - standoff_w / 2]:
            # Hull entre base du grip et bas de la plaque
            base = translate([dx - standoff_t / 2, -standoff_t / 2, 0])(
                cube([standoff_t, standoff_t, 1])
            )
            top = translate([dx - standoff_t / 2, -standoff_t / 2, sh + gr - 1])(
                cube([standoff_t, standoff_t, 1])
            )
            standoff = hull()(base, top)
            model += standoff

        # --- Grip cylindrique (creux pour legerte) ---
        grip = translate([-gl / 2, 0, 0])(
            rotate([0, 90, 0])(
                cylinder(d=gd, h=gl, _fn=32)
            )
        )
        # Evidement interieur
        grip_inner = translate([-gl / 2 + gw, 0, 0])(
            rotate([0, 90, 0])(
                cylinder(d=gd - 2 * gw, h=gl - 2 * gw, _fn=32)
            )
        )
        grip -= grip_inner

        model += grip

        return model
