"""
Coin Type "Flight-Case" pour Tube 25x25mm
=========================================
Connecteur d'angle cubique robuste a 3 voies (X, Y, Z).
Inspire des coins boules de flight-case mais adapte pour tube carre.
Design simple, indestructible, empilable.
"""
from solid2 import *
from ..base import ParametricModel
from ._constants import ACCORDION_TUBE, FIT_CLEARANCE, M5_HOLE

class FlightCaseCorner(ParametricModel):
    def __init__(self, **params):
        super().__init__("flight_case_corner", **params)

    def default_params(self):
        return {
            'tube_size': ACCORDION_TUBE,
            'wall_thick': 4.0,
            'fit_clearance': 0.2,
            'round_radius': 5.0, # Rayon des arêtes exterieures
        }

    def param_schema(self):
        return {'tube_size': {'type': 'float', 'min': 20, 'max': 30}}

    def build(self):
        p = self.params
        t = p['tube_size']
        w = p['wall_thick']
        r = p['round_radius']
        clr = p['fit_clearance']
        
        # Dimensions du cube exterieur
        outer_dim = t + 2*w
        
        # Cube de base avec bords arrondis (Minkowski simulé ou sphere aux coins)
        # Pour faire simple et propre : intersection de 3 cylindres ou hull de spheres
        # Ici : Hull de 8 spheres aux coins
        s_r = 2.0 # Rayon sphere
        
        # On cree un cube parfait pour la base technique
        base = cube([outer_dim, outer_dim, outer_dim])
        
        # On va créer les 3 manchons (X, Y, Z) qui partent du coin
        # Manchon Z (Vertical)
        sleeve_len = 40.0
        
        def sleeve(axis):
            sl = cube([outer_dim, outer_dim, sleeve_len])
            # Cavite tube
            cavity = translate([w, w, -1])(cube([t + 2*clr, t + 2*clr, sleeve_len + 2]))
            # Trou de vis
            hole = translate([outer_dim/2, -1, 20])(rotate([-90, 0, 0])(cylinder(d=M5_HOLE, h=outer_dim+2, _fn=24)))
            return sl - cavity - hole

        model = union()
        
        # Z Sleeve (Haut/Bas)
        model += sleeve('z')
        
        # X Sleeve (Gauche/Droite)
        model += rotate([0, 90, 0])(
            translate([-outer_dim, 0, 0])(sleeve('x'))
        )
        
        # Y Sleeve (Avant/Arriere)
        model += rotate([-90, 0, 0])(
            translate([0, -outer_dim, 0])(sleeve('y'))
        )
        
        # Renfort de coin (La "Boule" du flight case)
        # On ajoute de la matiere au coin 0,0,0
        corner_block = cube([outer_dim, outer_dim, outer_dim])
        # On le rend un peu plus "smooth"
        corner_block = intersection()(
            corner_block,
            translate([0,0,0])(sphere(r=outer_dim * 0.9, _fn=64))
        )
        # On le place au coin
        model += translate([0,0,0])(corner_block)

        # Nettoyage interieur (au cas ou le renfort deborde)
        # On re-creuse les 3 directions
        cleaner = cube([t, t, 100])
        cleaner_offset = translate([w+clr, w+clr, w])(cleaner)
        model -= cleaner_offset
        model -= rotate([0, 90, 0])(cleaner_offset)
        model -= rotate([-90, 0, 0])(cleaner_offset)

        return model

if __name__ == "__main__":
    c = FlightCaseCorner()
    c.save_scad()
