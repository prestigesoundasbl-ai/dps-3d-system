"""
Verrou de Plateau "Butterfly" DPS
==================================
Systeme de verrouillage rotatif pour fixer le plateau bois/plexi
sur la structure alu 25x25mm.
Inspire des fermetures de flight-case.
"""
from solid2 import *
from ..base import ParametricModel
from ._constants import (
    ACCORDION_TUBE, FIT_CLEARANCE,
)

class TrayLockButterfly(ParametricModel):
    def __init__(self, **params):
        super().__init__("tray_lock_butterfly", **params)

    def default_params(self):
        return {
            'tube_size': ACCORDION_TUBE,
            'wing_span': 60.0, # Largeur du papillon
            'thickness': 25.0,
            'fit_clearance': 0.2,
        }

    def param_schema(self):
        return {
            'wing_span': {'type': 'float', 'min': 40, 'max': 80},
        }

    def build(self):
        p = self.params
        t = p['tube_size']
        ws = p['wing_span']
        h = p['thickness']
        clr = p['fit_clearance']
        
        inner = t + 2*clr
        outer_w = inner + 8
        
        # --- PARTIE 1 : Le Support Fixe (Base sur tube) ---
        base = union()
        # Clip en U pour le tube
        clip = cube([outer_w, inner + 4, h/2])
        clip -= translate([4, 4, -1])(cube([inner, inner + 1, h/2 + 2]))
        base += clip
        
        # Axe central pour le pivot
        pivot_base = translate([outer_w/2, inner + 4, h/4])(
            cylinder(d=12, h=h/2 + 5, _fn=32)
        )
        base += pivot_base

        # --- PARTIE 2 : Le Papillon (La Came mobile) ---
        butterfly = union()
        # Corps central
        butterfly += cylinder(d=25, h=6, _fn=32)
        # Les "ailes" du papillon pour la prise en main
        wing_geom = hull()(
            cylinder(d=15, h=6, _fn=24),
            translate([ws/2 - 7.5, 0, 0])(cylinder(d=10, h=10, _fn=24))
        )
        butterfly += wing_geom
        butterfly += rotate([0, 0, 180])(wing_geom)
        
        # Le "Lock" (La partie qui vient au-dessus du plateau)
        lock_tongue = translate([-10, 15, 0])(cube([20, 15, 6]))
        butterfly += lock_tongue
        
        # Trou d'axe
        butterfly -= translate([0, 0, -1])(cylinder(d=6.5, h=12, _fn=24))

        # On separe pour l'impression
        model = base + translate([outer_w + 30, 0, 0])(butterfly)

        return model

if __name__ == "__main__":
    l = TrayLockButterfly()
    l.save_scad()
    l.render_stl()
