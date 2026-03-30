"""
WolfMix W1 Split Riser - Duo Edition
Modèle : wolfmix_riser_split.py (Version 2.0)
Optimisation : Divisé en deux pièces pour tenir sur Prusa Mini+.
"""
import os
import sys
import math

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from build123d import *
from models.build_base import BuildParametricModel
from models.brand import LOGO_TEXT_PRIMARY

class WolfmixSplitRiser(BuildParametricModel):
    def __init__(self, side="left", **params):
        name = f"wolfmix_riser_{side}"
        super().__init__(name, **params)
        self.side = side

    def default_params(self) -> dict:
        return {
            'angle': 15.0,
            'width': 25.0,      # Largeur d'un seul pied
            'depth': 210.0,     # Profondeur totale
            'lip_h': 10.0,      # Lèvre de retenue
            'wall_t': 4.0,
        }

    def build(self) -> Part:
        p = self.params
        w, d, angle = p['width'], p['depth'], p['angle']
        wt = p['wall_t']
        
        with BuildPart() as leg:
            # 1. Profil latéral (Triangle incliné)
            with BuildSketch(Plane.XZ) as profile:
                with BuildLine():
                    pts = [
                        (0, 0),
                        (d, 0),
                        (d, p['lip_h']),
                        (0, p['lip_h'] + d * math.tan(math.radians(angle))),
                        (0, 0)
                    ]
                    Polyline(pts)
                make_face()
            
            extrude(amount=w/2, both=True)
            
            # 2. Évidement central pour légèreté (Style industriel)
            with BuildPart(mode=Mode.SUBTRACT):
                with Locations((0, d/2, 0)):
                    # On crée une fenêtre latérale
                    with BuildSketch(Plane.YZ) as s:
                        RectangleRounded(w + 10, d - 40, 10)
                    extrude(amount=50, both=True)

            # 3. Branding sur le flanc extérieur
            # Si side=left, face Y-, si side=right, face Y+
            target_face = leg.faces().sort_by(Axis.Y)[0 if self.side == "left" else -1]
            with BuildSketch(Plane(target_face)) as logo:
                Text("DPS", font_size=12, font="Arial", font_style=FontStyle.BOLD)
            extrude(logo.sketch, amount=-1.5, mode=Mode.SUBTRACT)

        return leg.part

if __name__ == "__main__":
    # On génère les deux
    WolfmixSplitRiser(side="left").generate()
    WolfmixSplitRiser(side="right").generate()
