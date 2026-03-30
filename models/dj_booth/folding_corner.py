"""
Coin Pliant "Quick-Lock" DPS
=============================
Permet aux traverses horizontales de se replier le long des montants verticaux.
Utilise une goupille rapide pour le verrouillage.
"""
from solid2 import *
from ..base import ParametricModel
from ._constants import (
    M5_HOLE, FIT_CLEARANCE,
    ACCORDION_TUBE,
)

class FoldingCorner(ParametricModel):
    def __init__(self, **params):
        super().__init__("folding_corner", **params)

    def default_params(self):
        return {
            'tube_size': ACCORDION_TUBE,
            'arm_length': 50.0,
            'pin_d': 6.0,
            'thickness': 4.0,
            'fit_clearance': 0.2,
        }

    def param_schema(self):
        return {
            'tube_size': {'type': 'float', 'min': 20, 'max': 30},
            'arm_length': {'type': 'float', 'min': 40, 'max': 80},
            'pin_d': {'type': 'float', 'min': 5, 'max': 8},
        }

    def build(self):
        p = self.params
        t = p['tube_size']
        pt = p['thickness']
        clr = p['fit_clearance']
        pin_d = p['pin_d'] + clr
        
        inner = t + 2*clr
        outer_w = inner + 2*pt
        
        # --- PARTIE A : Fixe sur le tube vertical ---
        vertical_base = union()
        # Bloc de base
        base_h = t * 2
        base = cube([outer_w, inner + pt, base_h])
        # Cavite pour tube vertical
        base -= translate([pt, pt, -1])(cube([inner, inner + 1, base_h + 2]))
        # Trous de fixation
        base -= translate([outer_w/2, -1, base_h * 0.25])(rotate([-90, 0, 0])(cylinder(d=M5_HOLE, h=pt+2, _fn=20)))
        base -= translate([outer_w/2, -1, base_h * 0.75])(rotate([-90, 0, 0])(cylinder(d=M5_HOLE, h=pt+2, _fn=20)))
        
        # Oreilles de pivot (en saillie vers l'avant)
        ear_h = t + 10
        ear = translate([0, inner + pt, base_h - ear_h])(
            cube([outer_w, t + 10, ear_h])
        )
        # Cavite entre les oreilles pour laisser passer le tube horizontal
        ear -= translate([pt, -1, -1])(cube([inner, t + 12, ear_h + 2]))
        # Trou du pivot (Axe constant)
        ear -= translate([-1, inner + pt + t/2, base_h - t/2])(rotate([0, 90, 0])(cylinder(d=pin_d, h=outer_w + 2, _fn=24)))
        # Trou de verrouillage (Quick Pin)
        ear -= translate([-1, inner + pt + t/2, base_h - t/2 - t])(rotate([0, 90, 0])(cylinder(d=pin_d, h=outer_w + 2, _fn=24)))
        
        vertical_base += ear

        # --- OPTIMISATION TECH (Evidements) ---
        # Alleger les flancs de la base
        vertical_base -= translate([-1, pt + 5, 5])(cube([pt + 2, inner - 10, base_h - 10]))
        vertical_base -= translate([outer_w - pt - 1, pt + 5, 5])(cube([pt + 2, inner - 10, base_h - 10]))

        return vertical_base

if __name__ == "__main__":
    c = FoldingCorner()
    c.save_scad()
    c.render_stl()
