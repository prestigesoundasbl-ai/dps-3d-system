"""
Charniere Double Pivot DPS "Origami"
=====================================
Permet un pliage a 180 degres parfait (les tubes se touchent).
Design squelette pour CityFab (Big Builder).
Optimise pour tubes 25x25mm.
"""
from solid2 import *
from ..base import ParametricModel
from ._constants import (
    M5_HOLE, M5_HEAD, M5_HEAD_DEPTH,
    FIT_CLEARANCE, HINGE_PIN_D,
    ACCORDION_TUBE,
)

class DoublePivotHinge(ParametricModel):
    def __init__(self, **params):
        super().__init__("double_pivot_hinge", **params)

    def default_params(self):
        return {
            'tube_size': ACCORDION_TUBE,
            'link_length': 40.0,
            'thickness': 30.0,
            'gap': 2.0,
            'fit_clearance': 0.2,
        }

    def param_schema(self):
        return {
            'tube_size': {'type': 'float', 'min': 20, 'max': 30},
            'link_length': {'type': 'float', 'min': 30, 'max': 60},
            'thickness': {'type': 'float', 'min': 20, 'max': 50},
            'gap': {'type': 'float', 'min': 1, 'max': 5},
        }

    def _link(self, length, thickness, pin_d):
        """Le bras de liaison entre les deux pivots."""
        r = (pin_d + 10) / 2
        link = hull()(
            cylinder(r=r, h=thickness, _fn=32),
            translate([length, 0, 0])(cylinder(r=r, h=thickness, _fn=32))
        )
        # Trous pour les axes
        link -= translate([0, 0, -1])(cylinder(d=pin_d, h=thickness + 2, _fn=24))
        link -= translate([length, 0, 0])(cylinder(d=pin_d, h=thickness + 2, _fn=24))
        return link

    def build(self):
        p = self.params
        t = p['tube_size']
        l = p['link_length']
        h = p['thickness']
        clr = p['fit_clearance']
        pin_d = HINGE_PIN_D + clr
        bd = t + 2*clr + 4 # Profondeur

        # Piece de fixation sur le tube (U-Bracket)
        def bracket():
            bw = t + 2*clr + 8 # Largeur totale
            br = cube([bw, bd, h])
            # Cavite tube
            br -= translate([4, 4, -1])(cube([t+2*clr, t+2*clr+5, h+2]))
            # Oreilles pour le pivot
            ear_r = 10
            ear = translate([bw/2, bd, h/2])(
                rotate([-90, 0, 0])(cylinder(r=ear_r, h=10, _fn=32))
            )
            # Trou axe
            ear -= translate([bw/2, bd-1, h/2])(
                rotate([-90, 0, 0])(cylinder(d=pin_d, h=12, _fn=24))
            )
            return br + ear

        model = union()
        # Bracket 1
        model += color("gray")(bracket())
        
        # Le bras de liaison (Link)
        link = self._link(l, 8, pin_d)
        model += translate([ (t+2*clr+8)/2, bd + 5, h/2 - 4])(
            rotate([0, 0, 0])(link)
        )
        
        # Bracket 2 (positionne a l'autre bout du link)
        model += translate([ (t+2*clr+8)/2 + l, bd + 5 + 5, 0])(
            rotate([0, 0, 180])(color("gold")(bracket()))
        )

        return model

if __name__ == "__main__":
    h = DoublePivotHinge()
    h.save_scad()
    h.render_stl()
