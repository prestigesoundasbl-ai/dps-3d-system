"""
DPS FLYHT-MASTER ASSEMBLY
==========================
L'aboutissement de notre travail : Le meuble DJ complet hybride.
Combine : Structure Flyht Pro (pratique) + Look APEX (Prestige) + Pieces Origami.
"""
import math
from solid2 import *
from ..base import ParametricModel
from ..logo import logo_3d
from ._constants import ACCORDION_TUBE

# Import de toutes les pieces du kit final
from .double_pivot_hinge import DoublePivotHinge
from .folding_corner import FoldingCorner
from .modular_tile_clip import ModularTileClip
from .apex_folding_hub import ApexFoldingHub
from .table_support_bracket import TableSupportBracket
from .leveling_foot import LevelingFoot
from .folding_leg_pivot import FoldingLegPivot
from .tray_lock_butterfly import TrayLockButterfly

class FlyhtMasterBooth(ParametricModel):
    def __init__(self, **params):
        super().__init__("flyht_master_booth", **params)

    def default_params(self):
        return {
            'width': 1200.0,
            'depth': 600.0,
            'height': 1000.0,
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
        t = ACCORDION_TUBE
        
        model = union()

        # =========================================================
        # 1. FAÇADE AVANT (LE CŒUR)
        # =========================================================
        front_frame = union()
        # Montants verticaux
        front_frame += self._tube(h)
        front_frame += translate([w - t, 0, 0])(self._tube(h))
        # Traverses horizontales
        bl = w - 2*t
        front_frame += translate([t, 0, 100])(rotate([0, 90, 0])(self._tube(bl))) # Basse
        front_frame += translate([t, 0, h - t])(rotate([0, 90, 0])(self._tube(bl))) # Haute
        
        # Coins Pliants (Cyan)
        corner = color("cyan")(FoldingCorner(fit_clearance=0).build())
        front_frame += translate([0, 0, 100 - t])(corner)
        front_frame += translate([w, t, 100 - t])(rotate([0, 0, 180])(corner))
        
        # Logo Or Signature
        logo = color("gold")(logo_3d(width=400, height=8, quality='normal'))
        front_frame += translate([w/2, -12, h*0.6])(rotate([90, 0, 0])(logo))
        
        model += front_frame

        # =========================================================
        # 2. SOMMET APEX (POINTE)
        # =========================================================
        # Hub central (Or)
        model += translate([w/2, t/2, h - t + 5])(color("gold")(ApexFoldingHub(fit_clearance=0).build()))
        # Barres de pointe
        def apex_bar(): return color("gold")(rotate([0, 45, 0])(cube([t, t, 350])))
        model += translate([w/2 - 15, t/2, h])(apex_bar())
        model += translate([w/2 + 15, t/2, h])(rotate([0, -90, 0])(apex_bar()))

        # =========================================================
        # 3. AILES LATÉRALES (FOLDING WINGS)
        # =========================================================
        def flyht_wing():
            wng = union()
            # Cadre de l'aile
            wng += self._tube(h) # Montant vers le DJ
            wng += rotate([0, 90, 90])(self._tube(d - t)) # Traverse basse
            wng += translate([0, 0, h - t])(rotate([0, 90, 90])(self._tube(d - t))) # Traverse haute
            
            # --- INNOVATION : LE PIED PIVOTANT (Flyht Style) ---
            pivot_part = color("magenta")(FoldingLegPivot(fit_clearance=0).build())
            # On place le pivot sur la traverse haute
            wng += translate([-5, d - t - 10, h - t - 5])(pivot_part)
            # Le tube du pied qui descend
            wng += color([0.7, 0.7, 0.75])(translate([0, d - t, 0])(self._tube(h - 50)))
            # Pied niveleur au bout
            foot = color([0.2, 0.2, 0.2])(LevelingFoot(fit_clearance=0).build())
            wng += translate([t/2, d - t/2, -10])(foot)
            
            # Verrou Butterfly sur la traverse haute (Orange)
            vlock = color("orange")(TrayLockButterfly(fit_clearance=0).build())
            wng += translate([t + 10, d/2, h - t])(rotate([0, 0, 0])(vlock))
            
            return wng

        # Charnieres Origami (Rouge)
        hinge = color("red")(DoublePivotHinge(fit_clearance=0).build())
        model += translate([-5, t/2, h*0.25])(rotate([0, 0, 90])(hinge))
        model += translate([-5, t/2, h*0.75])(rotate([0, 0, 90])(hinge))
        model += translate([w + 5, t/2, h*0.25])(rotate([0, 0, 90])(hinge))
        model += translate([w + 5, t/2, h*0.75])(rotate([0, 0, 90])(hinge))

        # Placement des ailes à 90°
        model += translate([0, 0, 0])(rotate([0, 0, -90])(flyht_wing()))
        model += translate([w, 0, 0])(rotate([0, 0, 90])(mirror([1,0,0])(flyht_wing())))

        # =========================================================
        # 4. PLATEAU & MATÉRIEL
        # =========================================================
        # Plateau Principal
        model += translate([-100, -50, 950])(color([0.5, 0.3, 0.1, 0.8])(cube([w + 200, d + 150, 18])))
        
        # Platines Pioneer (Simulees)
        cdj = color([0.1, 0.1, 0.2])(cube([350, 450, 100]))
        model += translate([w/2 - 550, 50, 968])(cdj)
        model += translate([w/2 + 200, 50, 968])(cdj)
        model += translate([w/2 - 150, 50, 968])(color([0.05, 0.05, 0.1])(cube([300, 450, 100])))

        return model

if __name__ == "__main__":
    b = FlyhtMasterBooth()
    b.save_scad()
