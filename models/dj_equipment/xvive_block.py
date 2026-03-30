"""
Xvive Block v13 - Edition Prestige Sound
Modèle : xvive_block.py (Version 1.1)
Optimisation : Intégration système DPS et Slicing Turbo.
"""
import os
import sys
import math

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from build123d import *
from models.build_base import BuildParametricModel
from models.brand import LOGO_TEXT_PRIMARY

class XviveBlock(BuildParametricModel):
    """Logement pour transmetteur Xvive et accessoires USB."""

    def __init__(self, **params):
        super().__init__("xvive_block", **params)

    def default_params(self) -> dict:
        return {
            'device_w': 32.0,
            'device_d': 30.0,
            'xlr_diam': 21.0,
            'rect_h': 28.0,
            'xlr_h': 12.0,
            'bottom': 2.5,
            'wall': 3.5,
            'usb_w': 35.0,
            'usb_d': 45.0,
            'branding': True,
        }

    def build(self) -> Part:
        p = self.params
        dw, dd = p['device_w'], p['device_d']
        xd = p['xlr_diam']
        rh, xh = p['rect_h'], p['xlr_h']
        bt, wt = p['bottom'], p['wall']
        uw, ud = p['usb_w'], p['usb_d']

        # Calcul du bloc total
        total_w = dw + uw + (3 * wt)
        total_d = max(dd, ud) + (2 * wt)
        total_h = rh + xh + bt

        with BuildPart() as xvive:
            # 1. Corps principal
            Box(total_w, total_d, total_h)
            
            # 2. Logement Xvive (Soustraction)
            slot_x = -(total_w/2) + dw/2 + wt
            with BuildPart(mode=Mode.SUBTRACT):
                with Locations((slot_x, 0, -total_h/2 + bt + xh/2)):
                    Cylinder(radius=xd/2, height=xh)
                with Locations((slot_x, 0, -total_h/2 + bt + xh + rh/2 + 1)):
                    Box(dw, dd, rh + 2)
                with Locations((slot_x, 0, -total_h/2)):
                    Cylinder(radius=7.0, height=bt*3) # Passage câble fond

            # 3. Rangement USB XXL (Soustraction)
            pocket_x = (total_w/2) - uw/2 - wt
            with BuildPart(mode=Mode.SUBTRACT):
                with Locations((pocket_x, 0, 5)):
                    Box(uw, ud, total_h + 10)

            # 4. BRANDING "PRESTIGE SOUND" (Longitudinal)
            if p['branding']:
                # Face Avant
                front_face = xvive.faces().sort_by(Axis.Y)[-1]
                with BuildSketch(Plane(front_face)) as s_front:
                    Text(LOGO_TEXT_PRIMARY, font_size=7.5, font="Arial", font_style=FontStyle.BOLD, rotation=-90)
                extrude(s_front.sketch, amount=-2.5, mode=Mode.SUBTRACT)

            # 5. Finition (Pas de chanfreins pour éviter les crashs OCP sur parois fines)
            pass

        return xvive.part

if __name__ == "__main__":
    model = XviveBlock()
    model.generate()
