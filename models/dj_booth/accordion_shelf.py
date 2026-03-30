"""
Support Etagere Accordion DJ Booth
=====================================
Equerre L pour etagere equipement.
Plaque verticale fixee au cadre (M5) + plaque horizontale (vis a bois).
Gusset diagonal de renfort.

Supporte 25kg repartis sur 4 brackets.

Imprimable CityFab1 : ~60x40x65mm
4 necessaires.
"""
from solid2 import *
from ..base import ParametricModel
from ._constants import (
    M5_HOLE, M5_HEAD, M5_HEAD_DEPTH,
    WOOD_SCREW_HOLE,
    FIT_CLEARANCE,
)


class AccordionShelfBracket(ParametricModel):

    def __init__(self, **params):
        super().__init__("accordion_shelf_bracket", **params)

    def default_params(self):
        return {
            'vertical_height': 60.0,
            'horizontal_depth': 40.0,
            'width': 40.0,
            'plate_thickness': 5.0,
            'gusset': True,
        }

    def param_schema(self):
        return {
            'vertical_height': {
                'type': 'float', 'min': 40, 'max': 80, 'unit': 'mm',
                'description': 'Hauteur plaque verticale (fixation cadre)',
            },
            'horizontal_depth': {
                'type': 'float', 'min': 30, 'max': 60, 'unit': 'mm',
                'description': 'Profondeur plaque horizontale (support etagere)',
            },
            'width': {
                'type': 'float', 'min': 25, 'max': 60, 'unit': 'mm',
                'description': 'Largeur du bracket',
            },
            'plate_thickness': {
                'type': 'float', 'min': 4, 'max': 8, 'unit': 'mm',
                'description': 'Epaisseur des plaques',
            },
            'gusset': {
                'type': 'bool',
                'description': 'Ajouter un renfort diagonal',
            },
        }

    def build(self):
        p = self.params
        vh = p['vertical_height']
        hd = p['horizontal_depth']
        w = p['width']
        pt = p['plate_thickness']

        model = union()

        # --- Plaque verticale (fixation M5 sur cadre) ---
        vert = cube([w, pt, vh])

        # 2 trous M5 pour fixation sur le tube du cadre
        spacing = vh / 3
        for i in range(2):
            z = spacing * (i + 1)
            hole = translate([w / 2, -0.1, z])(
                rotate([-90, 0, 0])(
                    cylinder(d=M5_HOLE, h=pt + 0.2, _fn=24)
                )
            )
            cs = translate([w / 2, pt - M5_HEAD_DEPTH, z])(
                rotate([-90, 0, 0])(
                    cylinder(d=M5_HEAD, h=M5_HEAD_DEPTH + 0.1, _fn=24)
                )
            )
            vert -= hole
            vert -= cs

        model += vert

        # --- Plaque horizontale (vis a bois pour etagere) ---
        horiz = translate([0, pt, 0])(
            cube([w, hd, pt])
        )

        # 2 trous vis a bois
        for i in range(2):
            x = w * (i + 1) / 3
            hole = translate([x, pt + hd / 2, -0.1])(
                cylinder(d=WOOD_SCREW_HOLE, h=pt + 0.2, _fn=24)
            )
            horiz -= hole

        model += horiz

        # --- Gusset diagonal ---
        if p['gusset']:
            gusset_h = min(vh * 0.6, hd * 0.8)
            # Triangle via hull
            p1 = translate([0, pt, pt])(cube([w, 3, 3]))
            p2 = translate([0, pt, gusset_h])(cube([w, 3, 3]))
            p3 = translate([0, pt + gusset_h * 0.8, pt])(cube([w, 3, 3]))
            gusset = hull()(p1, p2, p3)
            model += gusset

        return model
