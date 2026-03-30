"""
Pied Reglable Accordion DJ Booth
==================================
Insert carre dans le bas du tube alu avec vis de nivelage M10.
Base cylindrique avec pad caoutchouc.

Imprimable CityFab1 : 50x50x50mm
8 necessaires au total (4 centre + 2 par aile).
"""
from solid2 import *
from ..base import ParametricModel
from ._constants import (
    FIT_CLEARANCE,
    ACCORDION_TUBE, ACCORDION_INSERT_CLEARANCE, ACCORDION_TUBE_INSERT,
    M10_THREAD_D, M10_NUT_AF,
)


class AccordionFoot(ParametricModel):

    def __init__(self, **params):
        super().__init__("accordion_foot", **params)

    def default_params(self):
        return {
            'tube_size': ACCORDION_TUBE,
            'base_diameter': 50.0,
            'insert_depth': 35.0,
            'base_height': 15.0,
            'pad_diameter': 30.0,
            'pad_recess': 2.0,
            'fit_clearance': ACCORDION_INSERT_CLEARANCE,
        }

    def param_schema(self):
        return {
            'tube_size': {
                'type': 'float', 'min': 20, 'max': 30, 'unit': 'mm',
                'description': 'Section tube alu carre',
            },
            'base_diameter': {
                'type': 'float', 'min': 35, 'max': 70, 'unit': 'mm',
                'description': 'Diametre de la base',
            },
            'insert_depth': {
                'type': 'float', 'min': 20, 'max': 50, 'unit': 'mm',
                'description': 'Profondeur d\'insertion dans le tube',
            },
            'base_height': {
                'type': 'float', 'min': 10, 'max': 25, 'unit': 'mm',
                'description': 'Hauteur de la base (sous le tube)',
            },
            'pad_diameter': {
                'type': 'float', 'min': 20, 'max': 50, 'unit': 'mm',
                'description': 'Diametre du pad caoutchouc',
            },
            'pad_recess': {
                'type': 'float', 'min': 1, 'max': 4, 'unit': 'mm',
                'description': 'Profondeur du logement pad',
            },
            'fit_clearance': {
                'type': 'float', 'min': 0.1, 'max': 0.6, 'unit': 'mm',
                'description': 'Jeu autour de l\'insert',
            },
        }

    def build(self):
        p = self.params
        tube = p['tube_size']
        base_d = p['base_diameter']
        insert_d = p['insert_depth']
        base_h = p['base_height']
        pad_d = p['pad_diameter']
        pad_r = p['pad_recess']
        clr = p['fit_clearance']

        insert_size = tube - 2 * clr  # carre qui rentre dans le tube

        model = union()

        # --- Base cylindrique avec chanfrein ---
        base = cylinder(d=base_d, h=base_h, _fn=48)
        # Chanfrein en bas
        chamfer = translate([0, 0, -0.01])(
            cylinder(d1=base_d + 4, d2=base_d, h=2, _fn=48)
        )
        base -= cylinder(d=base_d + 5, h=2, _fn=48) - chamfer

        model += base

        # --- Insert carre (monte dans le tube) ---
        insert = translate([-insert_size / 2, -insert_size / 2, base_h])(
            cube([insert_size, insert_size, insert_d])
        )

        # 4 nervures de friction sur les faces de l'insert
        rib_w = 1.5
        rib_d = 0.4  # saillie
        rib_h = insert_d - 4
        for angle in [0, 90, 180, 270]:
            rib = rotate([0, 0, angle])(
                translate([insert_size / 2, -rib_w / 2, base_h + 2])(
                    cube([rib_d, rib_w, rib_h])
                )
            )
            insert += rib

        model += insert

        # --- Logement ecrou M10 hexagonal (dans la base) ---
        nut_af = M10_NUT_AF  # across flats
        nut_h = 8.0
        nut = translate([0, 0, base_h - nut_h])(
            cylinder(d=nut_af / 0.866, h=nut_h, _fn=6)  # hex: d = af / cos(30)
        )
        model -= nut

        # Trou pour vis M10 (traverse la base)
        m10_hole = translate([0, 0, -0.1])(
            cylinder(d=M10_THREAD_D + 0.5, h=base_h + 0.2, _fn=32)
        )
        model -= m10_hole

        # --- Recess pad caoutchouc (sous la base) ---
        pad_recess = translate([0, 0, -0.1])(
            cylinder(d=pad_d, h=pad_r + 0.1, _fn=32)
        )
        model -= pad_recess

        return model
