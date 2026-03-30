"""
Support de Plateau "Slide-Lock" DPS
====================================
Support coulissant pour le plateau DJ et l'etagere.
Se fixe sur les montants verticaux 25x25mm.
Inclut un guide-cable integre.
"""
from solid2 import *
from ..base import ParametricModel
from ._constants import (
    M5_HOLE, FIT_CLEARANCE, ACCORDION_TUBE,
)

class TableSupportBracket(ParametricModel):
    def __init__(self, **params):
        super().__init__("table_support_bracket", **params)

    def default_params(self):
        return {
            'tube_size': ACCORDION_TUBE,
            'shelf_depth': 60.0,  # Largeur du support pour le plateau
            'height': 80.0,       # Hauteur de la zone de serrage
            'thickness': 4.0,
            'fit_clearance': 0.2,
        }

    def param_schema(self):
        return {
            'shelf_depth': {'type': 'float', 'min': 40, 'max': 100},
            'height': {'type': 'float', 'min': 60, 'max': 120},
        }

    def build(self):
        p = self.params
        t = p['tube_size']
        sd = p['shelf_depth']
        h = p['height']
        pt = p['thickness']
        clr = p['fit_clearance']
        
        inner = t + 2*clr
        outer_w = inner + 2*pt
        
        model = union()
        
        # --- PARTIE 1 : Le Fourreau (Sleeve) ---
        # La partie qui entoure le tube
        sleeve = cube([outer_w, inner + pt, h])
        # Cavite tube
        sleeve -= translate([pt, pt, -1])(cube([inner, inner + 1, h + 2]))
        
        # Trous de verrouillage (pour vis ou goupille)
        sleeve -= translate([outer_w/2, -1, h * 0.2])(rotate([-90, 0, 0])(cylinder(d=M5_HOLE, h=pt+2, _fn=20)))
        sleeve -= translate([outer_w/2, -1, h * 0.8])(rotate([-90, 0, 0])(cylinder(d=M5_HOLE, h=pt+2, _fn=20)))
        
        model += sleeve
        
        # --- PARTIE 2 : La Console (Support plateau) ---
        # Une aile qui part vers l'arriere pour tenir le bois
        console = translate([0, -sd, 0])(
            cube([outer_w, sd, pt]) # La base plate
        )
        # Nervure de renfort triangulaire (Gusset)
        nervure = hull()(
            translate([0, -sd + 5, 0])(cube([outer_w, 5, pt])),
            translate([0, -5, h - 10])(cube([outer_w, 5, pt]))
        )
        
        # On evide la nervure pour le style et le poids
        nervure -= translate([-1, -sd/2, h/3])(
            rotate([0, 90, 0])(cylinder(d=sd/2, h=outer_w + 2, _fn=24))
        )
        
        model += console + nervure
        
        # --- PARTIE 3 : Guide-Cable "C-Hook" ---
        # Petit crochet sur le cote pour ranger les cables
        hook = translate([outer_w, inner/2, h/2])(
            rotate([0, 0, 0])(
                difference()(
                    cylinder(d=25, h=15, center=True, _fn=32),
                    cylinder(d=18, h=17, center=True, _fn=32),
                    translate([10, 0, 0])(cube([20, 30, 20], center=True)) # Ouverture
                )
            )
        )
        model += hook

        # --- FINITION : Chanfreins ---
        # (Simplifie ici pour la performance du rendu)
        
        return model

if __name__ == "__main__":
    b = TableSupportBracket()
    b.save_scad()
    b.render_stl()
