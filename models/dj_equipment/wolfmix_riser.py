"""
Support Incliné WolfMix W1 - Edition Prestige Sound
Modèle : wolfmix_riser.py (Version 1.1)
Optimisation : Imports corrigés pour exécution globale.
"""
import os
import sys
import math

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from build123d import *
from models.build_base import BuildParametricModel
from models.brand import LOGO_TEXT_PRIMARY

class WolfmixRiser(BuildParametricModel):
    def __init__(self, **params):
        super().__init__("wolfmix_riser", **params)

    def default_params(self) -> dict:
        return {
            'device_w': 195.0,
            'device_d': 220.0,
            'angle': 15.0,
            'wall_t': 4.0,
            'lip_h': 8.0,
            'clearance': 0.5,
            'branding': False,
        }

    def build(self) -> Part:
        p = self.params
        dw, dd, wt, angle = p['device_w'] + (2*p['clearance']), p['device_d'] + (2*p['clearance']), p['wall_t'], p['angle']
        
        # Dimensions simplifiées pour stabilité
        tw = dw + (2 * wt)
        td = dd + (2 * wt)
        th = 30.0 # Hauteur de base

        with BuildPart() as riser:
            # 1. Base inclinée (Box découpée)
            Box(tw, td, th)
            with BuildPart(mode=Mode.SUBTRACT):
                with Locations((0, 0, th/2)):
                    with BuildSketch(Plane.XY.rotated((angle, 0, 0))) as s:
                        Rectangle(tw + 10, td + 100)
                    extrude(amount=50)
            
            # 2. Poche pour le WolfMix
            with BuildPart(mode=Mode.SUBTRACT):
                with Locations((0, 0, 10)): # On s'enfonce
                    with BuildSketch(Plane.XY.rotated((angle, 0, 0))) as s2:
                        Rectangle(dw, dd)
                    extrude(amount=100)

        return riser.part

if __name__ == "__main__":
    model = WolfmixRiser()
    model.generate()
