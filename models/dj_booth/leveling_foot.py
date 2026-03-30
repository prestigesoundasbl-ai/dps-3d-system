"""
Pied Niveleur "All-Terrain" DPS
================================
Embout pour tube alu 25x25mm avec reglage de hauteur.
Accepte une tige filetee M10 ou un boulon de nivelage standard.
Optimise pour CityFab.
"""
import math
from solid2 import *
from ..base import ParametricModel
from ._constants import (
    ACCORDION_TUBE, ACCORDION_INSERT_CLEARANCE,
    M10_THREAD_D, M10_NUT_AF,
)

class LevelingFoot(ParametricModel):
    def __init__(self, **params):
        super().__init__("leveling_foot", **params)

    def default_params(self):
        return {
            'tube_size': ACCORDION_TUBE,
            'insert_length': 30.0,
            'base_diameter': 45.0,
            'nut_size': M10_NUT_AF, # Largeur de l'ecrou M10
            'fit_clearance': ACCORDION_INSERT_CLEARANCE,
        }

    def param_schema(self):
        return {
            'insert_length': {'type': 'float', 'min': 20, 'max': 50},
            'base_diameter': {'type': 'float', 'min': 30, 'max': 60},
        }

    def build(self):
        p = self.params
        t = p['tube_size']
        l = p['insert_length']
        bd = p['base_diameter']
        ns = p['nut_size']
        clr = p['fit_clearance']
        
        # --- PARTIE 1 : L'Insert (Dans le tube) ---
        # On fait un insert en croix pour la solidite et economiser du plastique
        ins_w = t - 2.0 - 2*clr # Largeur avec jeu pour les parois du tube
        
        insert = union()
        # Corps de l'insert (Croix)
        insert += translate([-ins_w/2, -ins_w/2, 0])(cube([ins_w, ins_w, l]))
        
        # Collerette (Arret contre le bord du tube)
        collet = translate([-t/2, -t/2, -4])(cube([t, t, 4]))
        
        # --- PARTIE 2 : Logement Ecrou M10 ---
        # On creuse l'insert pour y mettre l'ecrou M10
        nut_h = 8.0 # Epaisseur standard ecrou M10
        nut_pocket = cylinder(d=ns / math.cos(math.pi / 6), h=nut_h + 0.5, _fn=6)
        
        # On soustrait le logement de l'ecrou et le trou de la vis
        foot_top = insert + collet
        foot_top -= translate([0, 0, -5])(nut_pocket)
        foot_top -= translate([0, 0, -5])(cylinder(d=M10_THREAD_D + 1, h=l + 10, _fn=24))

        # --- PARTIE 3 : La Base (Le pied reglable) ---
        # Note: Dans la realite c'est une vis M10, mais on dessine la base 3D ici
        base = union()
        base_h = 12.0
        # Disque de base
        base += cylinder(d=bd, h=base_h, _fn=64)
        # Chanfrein superieur sur la base
        base -= difference()(
            translate([0, 0, base_h])(cylinder(d=bd+2, h=5, _fn=64)),
            translate([0, 0, base_h-0.1])(cylinder(d1=bd, d2=bd-10, h=5.1, _fn=64))
        )
        # Logement pour vis M10 (Tete de vis hexagonale)
        base -= translate([0, 0, 2])(cylinder(d=ns + 0.5, h=base_h, _fn=6))
        
        # On separe les deux pour l'impression (Imprimer a plat)
        model = foot_top + translate([bd + 10, 0, 0])(base)

        return model

if __name__ == "__main__":
    f = LevelingFoot()
    f.save_scad()
    f.render_stl()
