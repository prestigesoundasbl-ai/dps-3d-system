"""
Verrou de Plateau "Gravity-Lock"
================================
Piece qui se clipse sur le haut des cadres lateraux.
Le plateau vient s'emboiter dedans par gravite.
"""
from solid2 import *
from ..base import ParametricModel
from ._constants import ACCORDION_TUBE, FIT_CLEARANCE

class TableLockGravity(ParametricModel):
    def __init__(self, **params):
        super().__init__("table_lock_gravity", **params)

    def default_params(self):
        return {
            'tube_size': ACCORDION_TUBE,
            'plate_thickness': 18.0, # Epaisseur plateau bois
            'fit_clearance': 0.2,
        }

    def param_schema(self):
        return {
            'tube_size': {'type': 'float', 'min': 20, 'max': 30},
            'plate_thickness': {'type': 'float', 'min': 10, 'max': 30},
        }

    def build(self):
        p = self.params
        t = p['tube_size']
        pt = p['plate_thickness']
        clr = p['fit_clearance']
        
        # Le corps se clipse sur le tube (C-Shape vertical)
        outer_w = t + 10
        body = cube([outer_w, t*2, 40])
        body -= translate([5, 5, -1])(cube([t + 2*clr, t + 2*clr, 42]))
        
        # L'oreille qui retient le plateau
        # C'est un U horizontal ou le plateau vient se poser
        ear = translate([-15, 0, 20])(
            difference()(
                cube([15 + outer_w, t*2, 20]),
                translate([5, -1, 5])(cube([outer_w + 20, t*2 + 2, pt + clr]))
            )
        )
        
        model = body + ear
        return model

if __name__ == "__main__":
    t = TableLockGravity()
    t.save_scad()
