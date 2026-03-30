"""
DPS APEX BOOTH V2 - MASTER INTEGRATION
=======================================
Fichier d'assemblage final haute-fidelite.
Combine le design signature APEX avec les nouvelles pieces 3D "Origami".
"""
import math
from solid2 import *
from ..base import ParametricModel
from ..logo import logo_3d
from ._constants import ACCORDION_TUBE, LED_STRIP_W, LED_STRIP_H

# Import des pieces techniques du kit
from .double_pivot_hinge import DoublePivotHinge
from .folding_corner import FoldingCorner
from .modular_tile_clip import ModularTileClip
from .apex_folding_hub import ApexFoldingHub
from .table_support_bracket import TableSupportBracket
from .leveling_foot import LevelingFoot

class ApexBoothV2(ParametricModel):
    def __init__(self, **params):
        super().__init__("apex_booth_v2", **params)

    def default_params(self):
        return {
            'width': 1200.0,
            'depth': 600.0,
            'height': 1050.0,
            'apex_rise': 150.0,
            'open_pct': 100.0,
        }

    def param_schema(self):
        return {'width': {'type': 'float', 'min': 1000, 'max': 1500}}

    def _tube(self, length, col=[0.7, 0.7, 0.75]):
        return color(col)(cube([ACCORDION_TUBE, ACCORDION_TUBE, length]))

    def build(self):
        p = self.params
        w = p['width']
        d = p['depth']
        h = p['height']
        ar = p['apex_rise']
        t = ACCORDION_TUBE
        
        model = union()

        # =========================================================
        # 1. LE CADRE AVANT (FRONT FRAME)
        # =========================================================
        front = union()
        # Montants
        front += self._tube(h)
        front += translate([w - t, 0, 0])(self._tube(h))
        # Traverses
        bl = w - 2*t
        front += translate([t, 0, 100])(rotate([0, 90, 0])(self._tube(bl)))
        front += translate([t, 0, h - t])(rotate([0, 90, 0])(self._tube(bl)))
        
        # Pieces 3D du Kit (Coins Cyan)
        corner = color("cyan")(FoldingCorner(fit_clearance=0).build())
        front += translate([0, 0, 100 - t])(corner)
        front += translate([w, t, 100 - t])(rotate([0, 0, 180])(corner))
        front += translate([0, t, h - t])(rotate([180, 0, 0])(corner))
        front += translate([w, 0, h - t])(rotate([180, 0, 180])(corner))
        
        # Pieds Niveleurs (Noir)
        foot = color([0.2, 0.2, 0.2])(LevelingFoot(fit_clearance=0).build())
        front += translate([t/2, t/2, -10])(foot)
        front += translate([w - t/2, t/2, -10])(foot)

        model += front

        # =========================================================
        # 2. LES AILES LATÉRALES (SIDE WINGS)
        # =========================================================
        def wing():
            wng = union()
            # Structure alu
            wng += self._tube(h) # Montant arriere
            wng += translate([0, d - t, 0])(self._tube(h)) # Montant jonction
            wng += rotate([0, 90, 90])(self._tube(d - t)) # Basse
            wng += translate([0, 0, h - t])(rotate([0, 90, 90])(self._tube(d - t))) # Haute
            # Pied
            wng += translate([t/2, t/2, -10])(foot)
            return wng

        # Charnieres Origami (Rouge)
        hinge = color("red")(DoublePivotHinge(fit_clearance=0).build())
        
        # Montage Aile Gauche
        model += translate([-5, t/2, h*0.2])(rotate([0, 0, 90])(hinge))
        model += translate([-5, t/2, h*0.8])(rotate([0, 0, 90])(hinge))
        model += translate([-t, 0, 0])(rotate([0, 0, -90])(wing()))

        # Montage Aile Droite
        model += translate([w + 5, t/2, h*0.2])(rotate([0, 0, 90])(hinge))
        model += translate([w + 5, t/2, h*0.8])(rotate([0, 0, 90])(hinge))
        model += translate([w, 0, 0])(rotate([0, 0, 90])(mirror([1,0,0])(wing())))

        # =========================================================
        # 3. LA FAÇADE APEX SIGNATURE (Noir & Or)
        # =========================================================
        facade = union()
        # Panneau Noir Translucide (Plexi)
        facade += color([0.1, 0.1, 0.1, 0.8])(
            translate([t + 5, -8, 150])(cube([w - 2*t - 10, 4, h - 200]))
        )
        
        # Logo Prestige Sound (Le vrai logo 3D en Or)
        logo = color("gold")(logo_3d(width=400, height=10, quality='normal'))
        facade += translate([w/2, -15, h*0.6])(rotate([90, 0, 0])(logo))
        
        # Clips de fixation (Vert)
        clip = color("green")(ModularTileClip(fit_clearance=0).build())
        for z in [250, 500, 750]:
            facade += translate([0, t, z])(rotate([0, 0, -90])(clip))
            facade += translate([w, 0, z])(rotate([0, 0, 90])(clip))
            
        model += facade

        # =========================================================
        # 4. LE SOMMET APEX (POINTE)
        # =========================================================
        # Hub central
        model += translate([w/2, t/2, h - t + 5])(color("gold")(ApexFoldingHub(fit_clearance=0).build()))
        # Barres de pointe
        def apex_bar():
            return color("gold")(rotate([0, 45, 0])(cube([t, t, 350])))
        
        model += translate([w/2 - 15, t/2, h])(apex_bar())
        model += translate([w/2 + 15, t/2, h])(rotate([0, -90, 0])(apex_bar()))

        # =========================================================
        # 5. PLATEAU & MATÉRIEL
        # =========================================================
        # Supports plateau (Violet)
        supp = color("purple")(TableSupportBracket(fit_clearance=0).build())
        model += translate([0, t, 900])(rotate([0, 0, -90])(supp))
        model += translate([w, 0, 900])(rotate([0, 0, 90])(mirror([1,0,0])(supp)))
        
        # Plateau Bois
        model += translate([-50, -50, 950])(color([0.5, 0.3, 0.1, 0.9])(cube([w + 100, d + 100, 18])))
        
        # Etagere rangement
        model += translate([t, t, 400])(color([0.4, 0.2, 0.1, 0.7])(cube([w - 2*t, d - t, 12])))

        # Simulation Platines (Bleu nuit)
        cdj = color([0.1, 0.1, 0.2])(cube([320, 450, 100]))
        model += translate([w/2 - 500, 50, 968])(cdj)
        model += translate([w/2 + 180, 50, 968])(cdj)
        model += translate([w/2 - 150, 50, 968])(color([0.05, 0.05, 0.1])(cube([300, 450, 100])))

        return model

if __name__ == "__main__":
    b = ApexBoothV2()
    b.save_scad()
