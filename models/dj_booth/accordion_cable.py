"""
Passe-Cable Snap-Fit Accordion DJ Booth
=========================================
Grommet snap-fit pour percage dans les panneaux.
Passage propre des cables entre sections du booth.

Imprimable CityFab1 : ~40x40x12mm
6-8 necessaires selon le cablage.
"""
from solid2 import *
from ..base import ParametricModel
from ._constants import FIT_CLEARANCE


class AccordionCablePort(ParametricModel):

    def __init__(self, **params):
        super().__init__("accordion_cable_port", **params)

    def default_params(self):
        return {
            'hole_diameter': 30.0,
            'cable_diameter': 20.0,
            'panel_thickness': 4.0,
            'flange_width': 5.0,
            'flange_thickness': 2.0,
            'clip_count': 4,
        }

    def param_schema(self):
        return {
            'hole_diameter': {
                'type': 'float', 'min': 20, 'max': 50, 'unit': 'mm',
                'description': 'Diametre du trou dans le panneau',
            },
            'cable_diameter': {
                'type': 'float', 'min': 10, 'max': 40, 'unit': 'mm',
                'description': 'Diametre du passage cable',
            },
            'panel_thickness': {
                'type': 'float', 'min': 2, 'max': 8, 'unit': 'mm',
                'description': 'Epaisseur du panneau a traverser',
            },
            'flange_width': {
                'type': 'float', 'min': 3, 'max': 10, 'unit': 'mm',
                'description': 'Largeur de la collerette',
            },
            'flange_thickness': {
                'type': 'float', 'min': 1, 'max': 4, 'unit': 'mm',
                'description': 'Epaisseur de la collerette',
            },
            'clip_count': {
                'type': 'int', 'min': 2, 'max': 6,
                'description': 'Nombre de clips snap-fit',
            },
        }

    def build(self):
        p = self.params
        hole_d = p['hole_diameter']
        cable_d = p['cable_diameter']
        panel_t = p['panel_thickness']
        flange_w = p['flange_width']
        flange_t = p['flange_thickness']
        n_clips = int(p['clip_count'])

        hole_r = hole_d / 2
        cable_r = cable_d / 2
        flange_r = hole_r + flange_w

        model = union()

        # --- Collerette avant (visible) ---
        flange = cylinder(r=flange_r, h=flange_t, _fn=48)
        model += flange

        # --- Corps cylindrique (dans le trou du panneau) ---
        body = translate([0, 0, flange_t])(
            cylinder(r=hole_r - 0.2, h=panel_t, _fn=48)
        )
        model += body

        # --- Clips snap-fit arriere ---
        clip_h = 3.0
        clip_overhang = 1.2
        clip_w = 6.0
        clip_t = 1.5

        for i in range(n_clips):
            angle = i * 360 / n_clips
            # Languette flexible
            clip = translate([hole_r - clip_t, -clip_w / 2, flange_t + panel_t])(
                cube([clip_t, clip_w, clip_h])
            )
            # Bosse de retention
            bump = translate([hole_r - clip_t, -clip_w / 2, flange_t + panel_t + clip_h])(
                cube([clip_t + clip_overhang, clip_w, 1.0])
            )
            clip_full = rotate([0, 0, angle])(clip + bump)
            model += clip_full

        # --- Trou central (passage cable) ---
        cable_hole = translate([0, 0, -0.1])(
            cylinder(r=cable_r, h=flange_t + panel_t + clip_h + 2, _fn=32)
        )
        model -= cable_hole

        return model
