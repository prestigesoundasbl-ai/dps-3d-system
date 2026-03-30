"""
Clip de Façade Modulaire "Snap-Lock" DPS
=========================================
Se clipse sur le tube 25x25mm.
Permet de fixer/enlever des tuiles de façade en 1 seconde.
Optimise pour impression rapide et economie de matiere.
"""
from solid2 import *
from ..base import ParametricModel
from ._constants import (
    FIT_CLEARANCE, ACCORDION_TUBE,
)

class ModularTileClip(ParametricModel):
    def __init__(self, **params):
        super().__init__("modular_tile_clip", **params)

    def default_params(self):
        return {
            'tube_size': ACCORDION_TUBE,
            'tile_thickness': 3.0, # Epaisseur de la plaque laser (acrylique/bois)
            'grip_strength': 0.5,  # Facteur de serrage sur le tube
            'width': 20.0,
        }

    def param_schema(self):
        return {
            'tube_size': {'type': 'float', 'min': 20, 'max': 30},
            'tile_thickness': {'type': 'float', 'min': 2, 'max': 6},
        }

    def build(self):
        p = self.params
        t = p['tube_size']
        tw = p['tile_thickness']
        w = p['width']
        clr = 0.1 # On veut que ca "claque" sur le tube
        
        # --- PARTIE 1 : Le C-Clip (Fixation tube) ---
        inner = t + clr
        outer = inner + 6 # Parois de 3mm
        
        c_clip = union()
        # Corps du clip
        body = cube([outer, outer, w])
        # Cavite pour le tube
        body -= translate([3, 3, -1])(cube([inner, inner + 5, w + 2]))
        # Ouverture pour laisser passer le tube au clipsage
        body -= translate([3 + 2, outer - 5, -1])(cube([inner - 4, 10, w + 2]))
        
        # Bords arrondis pour le "Snap"
        body += translate([3 + 2, outer - 2, 0])(cylinder(d=4, h=w, _fn=16))
        body += translate([3 + inner - 2, outer - 2, 0])(cylinder(d=4, h=w, _fn=16))
        
        c_clip += body

        # --- PARTIE 2 : Le Support de Tuile (Interface Laser) ---
        # On cree une rainure en "T" ou un simple ergot
        # Ici on va faire un systeme de glissiere simple pour la tuile
        
        mount = translate([outer/2 - 10, -5, 0])(
            cube([20, 5, w])
        )
        # Rainure pour la plaque laser
        mount -= translate([outer/2 - 10 - 1, -1, -1])(
            cube([22, tw + clr, w + 2])
        )
        # Trou pour petite vis de blocage ou goupille si besoin
        mount -= translate([outer/2, -6, w/2])(
            rotate([-90, 0, 0])(cylinder(d=3, h=10, _fn=12))
        )

        model = c_clip + mount
        
        # --- OPTIMISATION MATIERE ---
        # Evidement central pour gagner 20% de plastique
        model -= translate([-1, outer/2, w/2])(
            rotate([0, 90, 0])(cylinder(d=w*0.6, h=outer+2, _fn=20))
        )

        return model

if __name__ == "__main__":
    m = ModularTileClip()
    m.save_scad()
    m.render_stl()
