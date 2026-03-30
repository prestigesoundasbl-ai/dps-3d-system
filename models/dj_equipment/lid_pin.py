"""
Lid Alignment Pin - Centrage couvercle Flycase Prestige
Modèle : lid_pin.py (Version 1.0)
Auteur : Binôme IA (Gemini Orchestrator)
"""
import os
import sys
import math

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from build123d import *
from models.build_base import BuildParametricModel

class LidPin(BuildParametricModel):
    """Pion de centrage conique pour couvercle amovible."""

    def __init__(self, **params):
        super().__init__("lid_pin", **params)

    def default_params(self) -> dict:
        return {
            'pin_d': 8.0,       # Diamètre nominal
            'pin_h': 12.0,      # Hauteur du pion
            'base_d': 16.0,     # Diamètre de la collerette
            'base_h': 3.0,      # Épaisseur de la base
            'screw_d': 3.5,     # Trou vis M3
        }

    def build(self) -> Part:
        p = self.params
        
        with BuildPart() as pin:
            # 1. Base collerette
            Cylinder(radius=p['base_d']/2, height=p['base_h'])
            
            # 2. Le Pion (Cylindre + Cône pour entrée facile)
            with Locations((0, 0, p['base_h'])):
                # Partie cylindrique (bas)
                Cylinder(radius=p['pin_d']/2, height=p['pin_h']*0.6, align=(Align.CENTER, Align.CENTER, Align.MIN))
                # Partie conique (haut)
                with Locations((0, 0, p['pin_h']*0.6)):
                    Cone(bottom_radius=p['pin_d']/2, top_radius=p['pin_d']/2 - 1.5, height=p['pin_h']*0.4, align=(Align.CENTER, Align.CENTER, Align.MIN))
            
            # 3. Trou de fixation central
            with BuildPart(mode=Mode.SUBTRACT):
                Cylinder(radius=p['screw_d']/2, height=p['base_h'] + p['pin_h'] + 2)
                # Fraisage tête de vis au fond
                with Locations((0, 0, 1.5)):
                    Cylinder(radius=3.2, height=p['base_h'])

        return pin.part

if __name__ == "__main__":
    model = LidPin()
    model.generate()
