"""
Hub de Couronne APEX "Transformer" DPS
========================================
Piece centrale du sommet du meuble.
Relie les traverses horizontales aux montants de la pointe.
Inclut un support de logo et un canal LED.
"""
from solid2 import *
from ..base import ParametricModel
from ._constants import (
    ACCORDION_TUBE, FIT_CLEARANCE, LED_STRIP_W, LED_STRIP_H,
)

class ApexFoldingHub(ParametricModel):
    def __init__(self, **params):
        super().__init__("apex_folding_hub", **params)

    def default_params(self):
        return {
            'tube_size': ACCORDION_TUBE,
            'apex_angle': 45.0,  # Angle de la pointe
            'logo_slot_w': 150.0,
            'thickness': 30.0,
            'fit_clearance': 0.2,
        }

    def param_schema(self):
        return {
            'apex_angle': {'type': 'float', 'min': 30, 'max': 60},
            'logo_slot_w': {'type': 'float', 'min': 100, 'max': 300},
        }

    def build(self):
        p = self.params
        t = p['tube_size']
        angle = p['apex_angle']
        h = p['thickness']
        clr = p['fit_clearance']
        
        inner = t + 2*clr
        outer_w = inner + 10
        
        # --- CORPS CENTRAL (Le "V" inversé) ---
        hub = union()
        
        # Base qui se pose sur le tube horizontal
        base = cube([outer_w + 20, inner + 6, h], center=True)
        # Cavite pour le tube horizontal 25x25
        base -= cube([outer_w + 22, inner, h + 2], center=True)
        hub += base
        
        # Sockets pour les barres de la pointe (diagonales)
        def socket():
            s = cube([t + 8, t + 8, 40], center=True)
            s -= translate([0, 0, 5])(cube([inner, inner, 42], center=True))
            return s

        # Socket Gauche
        hub += translate([-20, 0, 15])(
            rotate([0, -angle, 0])(socket())
        )
        # Socket Droit
        hub += translate([20, 0, 15])(
            rotate([0, angle, 0])(socket())
        )
        
        # --- SUPPORT LOGO (Fente verticale) ---
        # Une plaque qui monte au milieu pour tenir le logo
        logo_mount = translate([0, inner/2 + 5, 20])(
            cube([60, 4, 50], center=True)
        )
        # Fente pour glisser l'acrylique du logo (3mm)
        logo_mount -= translate([0, 0, 5])(
            cube([55, 3.2, 45], center=True)
        )
        hub += logo_mount
        
        # --- CANAL LED "CROWN" ---
        # Rainure tout le long du hub pour les LED
        hub -= translate([0, -inner/2 - 2, 0])(
            cube([outer_w + 10, LED_STRIP_W + 1, LED_STRIP_H + 1], center=True)
        )

        # --- OPTIMISATION STYLE (Skeleton) ---
        # On evide le bloc central avec un losange pour le look
        hub -= rotate([90, 0, 0])(
            cylinder(d=25, h=inner + 20, center=True, _fn=6)
        )

        return hub

if __name__ == "__main__":
    h = ApexFoldingHub()
    h.save_scad()
    h.render_stl()
