"""
Prestige Business Vault - Distributeur de cartes de visite luxe
Modèle : business_vault.py (Version 1.0)
Auteur : Binôme IA (Gemini Orchestrator)
"""
import os
import sys
import math

# Ajout du chemin racine du projet au PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from build123d import *
from models.build_base import BuildParametricModel
from models.brand import LOGO_TEXT_PRIMARY

class BusinessVault(BuildParametricModel):
    """Distributeur de cartes vertical avec accent or."""

    def __init__(self, **params):
        super().__init__("business_vault", **params)

    def default_params(self) -> dict:
        return {
            'card_w': 86.0,     # Largeur carte (85 + jeu)
            'card_d': 56.0,     # Hauteur carte (55 + jeu)
            'stack_h': 40.0,    # Capacité (~100 cartes)
            'wall_t': 4.0,      # Épaisseur parois
            'slot_h': 2.0,      # Fente de sortie
            'branding': False,  # Off pour validation géométrie
        }

    def build(self) -> Part:
        p = self.params
        cw, cd, sh = p['card_w'], p['card_d'], p['slot_h']
        wt = p['wall_t']
        th = p['stack_h'] + wt
        
        # Dimensions totales
        total_w = cw + (2 * wt)
        total_d = wt + 25.0 # Base inclinée pour la prise
        
        with BuildPart() as vault:
            # 1. Corps principal (Boîte verticale)
            Box(total_w, cd + (2 * wt), th)
            
            # 2. Poche pour les cartes (Soustraction)
            with BuildPart(mode=Mode.SUBTRACT):
                with Locations((0, 0, wt/2)):
                    Box(cw, cd, th + 2)
            
            # 3. Fente de distribution frontale (Bas)
            with BuildPart(mode=Mode.SUBTRACT):
                # Fente pour sortir la carte
                with Locations((0, -(cd/2 + wt), -(th/2 - wt - sh/2))):
                    Box(cw - 20, wt * 3, sh + 1)
                # Évidement pour le doigt (ergonomie)
                with Locations((0, -(cd/2 + wt), -(th/2 - wt))):
                    Cylinder(radius=15, height=wt*4, rotation=(90, 0, 0))

            # 4. Inclinaison supérieure pour le branding
            with BuildPart(mode=Mode.SUBTRACT):
                with Locations((0, 0, th/2)):
                    with BuildSketch(Plane.XY.rotated((15, 0, 0))) as s:
                        Rectangle(total_w + 10, total_d + 100)
                    extrude(amount=20)

        return vault.part

if __name__ == "__main__":
    model = BusinessVault()
    model.generate()
