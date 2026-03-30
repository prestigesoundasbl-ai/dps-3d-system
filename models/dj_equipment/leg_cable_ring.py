"""
Prestige Cable Ring - Clip de gestion de câbles pour pieds Ø35mm
Modèle : leg_cable_ring.py (Version 1.0)
Auteur : Binôme IA (Gemini Orchestrator)
Usage : Se clipse sur les tubes Ø35mm du Flycase White & Gold.
"""
import os
import sys
import math

# Ajout du chemin racine du projet au PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from build123d import *
from models.build_base import BuildParametricModel
from models.brand import LOGO_TEXT_PRIMARY

class LegCableRing(BuildParametricModel):
    """Clip snap-on pour tube Ø35mm avec guide câble intégré."""

    def __init__(self, **params):
        super().__init__("leg_cable_ring", **params)

    def default_params(self) -> dict:
        return {
            'tube_d': 35.4,     # Diamètre intérieur du clip
            'ring_h': 25.0,     # Hauteur de l'anneau
            'wall_t': 3.5,      # Épaisseur de structure
            'cable_d': 10.0,    # Diamètre du passage câble (XLR/Power)
            'opening_a': 70.0,  # Angle d'ouverture pour le snap-on (degrés)
            'branding': False,  # Off pour validation STL initiale
        }

    def build(self) -> Part:
        p = self.params
        tr = p['tube_d'] / 2
        rh = p['ring_h']
        wt = p['wall_t']
        cr = p['cable_d'] / 2
        oa = p['opening_a']
        
        with BuildPart() as ring:
            # 1. L'Anneau Principal (Snap-on)
            with BuildSketch(Plane.XY) as s_ring:
                # Cercle extérieur
                Circle(tr + wt)
                # Cercle intérieur (Soustraction)
                Circle(tr, mode=Mode.SUBTRACT)
                # Ouverture pour le clip (Triangle de découpe)
                with BuildLine(mode=Mode.SUBTRACT):
                    p1 = (0, 0)
                    p2 = (tr + wt + 5, 0)
                    p3 = ((tr + wt + 5) * math.cos(math.radians(oa)), (tr + wt + 5) * math.sin(math.radians(oa)))
                    Line(p1, p2)
                    Line(p2, p3)
                    Line(p3, p1)
                make_face()
            
            extrude(amount=rh)
            
            # 2. Le Crochet Guide-Câble (Addition)
            # Positionné à l'opposé de l'ouverture
            with BuildPart(mode=Mode.ADD):
                with Locations((-(tr + wt + cr), 0, rh/2)):
                    # Bloc de support du crochet
                    Box(cr*2 + wt, cr*2 + wt*2, rh)
                    # Évidement pour le câble (Cylindre vertical)
                    with BuildPart(mode=Mode.SUBTRACT):
                        Cylinder(radius=cr, height=rh + 2)
                        # Fente latérale pour insérer le câble sans le débrancher
                        with Locations((cr, 0, 0)):
                            Box(wt*2, cr*1.5, rh + 2)

        return ring.part

if __name__ == "__main__":
    model = LegCableRing()
    model.generate()
