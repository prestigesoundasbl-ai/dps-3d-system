"""
REPLIQUE FLYHT PRO - DPS EDITION (V2)
======================================
Version mécaniquement stable avec renforts et orientation logo corrigée.
"""
import math
from solid2 import *
from ..base import ParametricModel
from ..logo import logo_3d
from ._constants import ACCORDION_TUBE

# Import des pièces techniques
from .flight_case_corner import FlightCaseCorner
from .table_lock_gravity import TableLockGravity
from .leveling_foot import LevelingFoot
from .double_pivot_hinge import DoublePivotHinge
from .modular_tile_clip import ModularTileClip

class FlyhtProReplica(ParametricModel):
    def __init__(self, **params):
        super().__init__("flyht_pro_replica", **params)

    def default_params(self):
        return {
            'width': 1500.0,
            'depth': 550.0,
            'height': 930.0,
        }

    def param_schema(self):
        return {'width': {'type': 'float', 'min': 1200, 'max': 1600}}

    def _tube(self, length, col=[0.2, 0.2, 0.2]):
        return color(col)(cube([ACCORDION_TUBE, ACCORDION_TUBE, length]))

    def build(self):
        p = self.params
        w = p['width']
        d = p['depth']
        h = p['height']
        t = ACCORDION_TUBE
        
        model = union()

        # =========================================================
        # 1. FAÇADE AVANT RENFORCÉE (FRONT)
        # =========================================================
        front = union()
        
        # --- Cadre Alu Principal ---
        f_frame = union()
        f_frame += self._tube(h) # Pied Gauche
        f_frame += translate([w - t, 0, 0])(self._tube(h)) # Pied Droit
        bl = w - 2*t
        f_frame += translate([t, 0, 0])(rotate([0, 90, 0])(self._tube(bl))) # Traverse Sol
        f_frame += translate([t, 0, h - t])(rotate([0, 90, 0])(self._tube(bl))) # Traverse Haut
        
        # --- RIGIDITÉ : Croix de Renfort (X-Brace) ---
        brace_col = [0.4, 0.4, 0.4, 0.5]
        f_frame += color(brace_col)(
            hull()(translate([t, t/2, t+20])(sphere(d=8)), translate([w-t, t/2, h-t-20])(sphere(d=8)))
        )
        f_frame += color(brace_col)(
            hull()(translate([t, t/2, h-t-20])(sphere(d=8)), translate([w-t, t/2, t+20])(sphere(d=8)))
        )
        
        # Coins "Boule" (Bleu)
        fc_corner = color("royalblue")(FlightCaseCorner(fit_clearance=0).build())
        f_frame += translate([0, 0, 0])(fc_corner)
        f_frame += translate([w, 0, 0])(rotate([0, 0, 90])(fc_corner))
        f_frame += translate([0, 0, h])(rotate([0, 90, 0])(fc_corner))
        f_frame += translate([w, 0, h])(rotate([0, 90, 90])(fc_corner))
        
        # --- FIXATION DU PANNEAU (Clips Verts) ---
        panel_clip = color("green")(ModularTileClip(width=20).build())
        for z in [h*0.3, h*0.7]:
            f_frame += translate([0, t, z])(rotate([0, 0, -90])(panel_clip))
            f_frame += translate([w, 0, z])(rotate([0, 0, 90])(panel_clip))

        front += f_frame

        # --- PANNEAU NOIR & LOGO (ORIENTATION CORRIGÉE) ---
        # Le panneau est à l'arrière des tubes, le logo vers le PUBLIC (+Y)
        front += color([0.1, 0.1, 0.1])(translate([t+2, -8, t+2])(cube([w-2*t-4, 8, h-2*t-4])))
        
        # Logo face au public
        logo = color("gold")(logo_3d(width=600, height=12, quality='normal'))
        front += translate([w/2, -20, h/2])(rotate([90, 0, 0])(logo))

        model += front

        # =========================================================
        # 2. AILES LATÉRALES (LEGS)
        # =========================================================
        def wing_pro():
            wng = union()
            # Cadre
            wng += self._tube(h)
            wng += rotate([-90, 0, 0])(self._tube(d - t))
            wng += translate([0, 0, h - t])(rotate([-90, 0, 0])(self._tube(d - t)))
            wng += translate([0, 0, 0])(fc_corner)
            wng += translate([0, 0, h])(rotate([0, 90, 0])(fc_corner))
            
            # --- BLOCAGE : Bras de sécurité (Orange) ---
            wng += color("orange")(translate([5, d/2, h*0.6])(rotate([0, 90, 0])(cylinder(d=12, h=35, _fn=20))))
            
            # Verrous de plateau (Orange)
            lock = color("orange")(TableLockGravity(fit_clearance=0).build())
            wng += translate([0, d*0.3, h-t])(lock)
            wng += translate([0, d*0.7, h-t])(lock)
            
            # Pieds
            wng += translate([t/2, t/2, -10])(LevelingFoot(fit_clearance=0).build())
            wng += translate([t/2, d - t/2, -10])(LevelingFoot(fit_clearance=0).build())
            return wng

        # Charnières Origami (Rouge)
        hinge = color("red")(DoublePivotHinge(fit_clearance=0).build())
        for z_pct in [0.25, 0.75]:
            model += translate([-5, t/2, h*z_pct])(rotate([0, 0, 90])(hinge))
            model += translate([w+5, t/2, h*z_pct])(rotate([0, 0, 90])(hinge))

        model += translate([0, 0, 0])(rotate([0, 0, -90])(wing_pro()))
        model += translate([w, 0, 0])(rotate([0, 0, 90])(mirror([1,0,0])(wing_pro())))

        # =========================================================
        # 3. PLATEAU & RANGEMENT
        # =========================================================
        # Plateau Principal
        model += translate([-20, -d - 20, h-2])(color([0.15, 0.15, 0.15, 0.9])(cube([w + 40, d + 40, 18])))
        
        # Etagère Basse
        model += translate([t+5, -d+t, h*0.4])(color([0.2, 0.2, 0.2])(cube([w - 2*t - 10, d - 2*t, 12])))

        return model

if __name__ == "__main__":
    b = FlyhtProReplica()
    b.save_scad()
