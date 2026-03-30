"""
Leg Keeper Pad - Maintien des pieds en transport
Modèle : leg_keeper.py (Version 1.0)
Auteur : Binôme IA (Gemini Orchestrator)
"""
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from build123d import *
from models.build_base import BuildParametricModel

class LegKeeper(BuildParametricModel):
    """Patin de maintien pour tube Ø32mm."""

    def __init__(self, **params):
        super().__init__("leg_keeper", **params)

    def default_params(self) -> dict:
        return {
            'leg_d': 32.5,      # Diamètre du pied avec jeu
            'pad_w': 50.0,      # Largeur du patin
            'pad_h': 15.0,      # Épaisseur totale
            'strap_w': 20.0,    # Largeur passage sangle
        }

    def build(self) -> Part:
        p = self.params
        pw, ph = p['pad_w'], p['pad_h']
        lr = p['leg_d'] / 2
        
        with BuildPart() as keeper:
            # 1. Bloc de base
            Box(pw, pw, ph)
            
            # 2. Berceau pour le pied (Soustraction)
            with BuildPart(mode=Mode.SUBTRACT):
                with Locations((0, 0, ph/2)):
                    Cylinder(radius=lr, height=pw + 2, rotation=(0, 90, 0))
            
            # 3. Passages pour sangles (Soustraction)
            with BuildPart(mode=Mode.SUBTRACT):
                for x in [-pw/4, pw/4]:
                    with Locations((x, 0, -ph/2 + 2)):
                        Box(p['strap_w'], pw + 2, 4)

        return keeper.part

if __name__ == "__main__":
    model = LegKeeper()
    model.generate()
