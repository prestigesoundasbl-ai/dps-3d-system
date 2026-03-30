"""
Pivot de Pied Escamotable "Flyht-Hybrid" DPS
=============================================
Inspiré du système Thomann Flyht Pro.
Permet au pied de pivoter à 90° pour se ranger le long de la structure.
Verrouillage par goupille ou clipsage.
"""
from solid2 import *
from ..base import ParametricModel
from ._constants import (
    ACCORDION_TUBE, FIT_CLEARANCE, M5_HOLE,
)

class FoldingLegPivot(ParametricModel):
    def __init__(self, **params):
        super().__init__("folding_leg_pivot", **params)

    def default_params(self):
        return {
            'tube_size': ACCORDION_TUBE,
            'pivot_offset': 30.0,
            'thickness': 5.0,
            'fit_clearance': 0.2,
        }

    def param_schema(self):
        return {
            'tube_size': {'type': 'float', 'min': 20, 'max': 30},
            'pivot_offset': {'type': 'float', 'min': 20, 'max': 60},
        }

    def build(self):
        p = self.params
        t = p['tube_size']
        off = p['pivot_offset']
        pt = p['thickness']
        clr = p['fit_clearance']
        
        inner = t + 2*clr
        outer_w = inner + 2*pt
        
        # --- PARTIE FIXE (Sur le cadre de l'aile) ---
        base = union()
        # Manchon pour le tube horizontal de l'aile
        sleeve_h = t * 1.5
        sleeve = cube([outer_w, inner + pt, sleeve_h])
        sleeve -= translate([pt, pt, -1])(cube([inner, inner + 1, sleeve_h + 2]))
        base += sleeve
        
        # Oreilles de pivot (décalées pour laisser le pied se replier à plat)
        ear_r = (t + 10) / 2
        ear = translate([outer_w/2, inner + pt, sleeve_h/2])(
            rotate([-90, 0, 0])(
                difference()(
                    cylinder(r=ear_r + 5, h=off, _fn=32),
                    cylinder(d=8, h=off + 2, center=True, _fn=24) # Trou axe pivot
                )
            )
        )
        base += ear

        # --- PARTIE MOBILE (Embout du pied) ---
        # Cette pièce s'insère dans le tube du pied et vient se fixer sur l'oreille
        leg_insert = union()
        ins_w = t - 2.5 # Insert dans le tube alu
        leg_insert += translate([-ins_w/2, -ins_w/2, 0])(cube([ins_w, ins_w, 30]))
        # Tête de pivot
        head = translate([0, 0, -10])(
            rotate([90, 0, 0])(
                difference()(
                    cylinder(r=ear_r, h=8, center=True, _fn=32),
                    cylinder(d=8.2, h=10, center=True, _fn=24)
                )
            )
        )
        leg_insert += head
        
        # On sépare les deux pour l'impression
        model = base + translate([outer_w + 20, 0, 0])(leg_insert)

        return model

if __name__ == "__main__":
    m = FoldingLegPivot()
    m.save_scad()
    m.render_stl()
