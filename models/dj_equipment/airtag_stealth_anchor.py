"""
Support AirTag Stealth Anchor - Sécurité Flycase Prestige
Modèle : airtag_stealth_anchor.py (Version 1.0)
Auteur : Binôme IA (Gemini Orchestrator)
Usage : Boîtier de sécurité pour tracker AirTag, à visser dans le case.
"""
import os
import sys
import math

# Ajout du chemin racine du projet au PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from build123d import *
from models.build_base import BuildParametricModel

class AirtagStealthAnchor(BuildParametricModel):
    """Boîtier ultra-bas pour AirTag avec fixation par vis."""

    def __init__(self, **params):
        super().__init__("airtag_stealth_anchor", **params)

    def default_params(self) -> dict:
        return {
            'airtag_d': 32.0,    # Diamètre AirTag
            'airtag_h': 8.0,     # Épaisseur AirTag
            'wall_t': 3.0,       # Épaisseur parois
            'hole_dist': 45.0,   # Entraxe des trous de fixation
            'screw_d': 3.5,      # Passage vis M3
        }

    def build(self) -> Part:
        p = self.params
        ar, ah = (p['airtag_d'] + 0.4)/2, p['airtag_h'] + 0.2
        wt = p['wall_t']
        
        # Dimensions du corps (Base ovale pour les trous de fixation)
        body_w = p['hole_dist'] + 12.0
        body_d = p['airtag_d'] + (2 * wt)
        body_h = ah + wt # Fond de 3mm + hauteur AirTag
        
        with BuildPart() as anchor:
            # 1. Corps principal (Rectangle arrondi)
            with BuildSketch() as s:
                RectangleRounded(body_w, body_d, 5.0)
            extrude(amount=body_h)
            
            # 2. Cavité AirTag (Soustraction)
            with BuildPart(mode=Mode.SUBTRACT):
                # On centre la cavité
                with Locations((0, 0, wt)):
                    Cylinder(radius=ar, height=ah + 5) # On débouche vers le haut
            
            # 3. Trous de fixation (Soustraction)
            with BuildPart(mode=Mode.SUBTRACT):
                for x in [-p['hole_dist']/2, p['hole_dist']/2]:
                    with Locations((x, 0, 0)):
                        # Passage de vis
                        Cylinder(radius=p['screw_d']/2, height=body_h + 2)
                        # Fraisage pour tête de vis (Y-)
                        with Locations((0, 0, 2)):
                            Cylinder(radius=3.2, height=body_h, rotation=(0, 0, 0))

            # 4. Message secret gravé au fond
            # (Visible seulement si on retire l'AirTag)
            with BuildPart(mode=Mode.SUBTRACT):
                with Locations((0, 0, 1.0)): # 1mm au dessus du fond
                    with BuildSketch(Plane.XY) as text_s:
                        Text("PRESTIGE SOUND", font_size=4, font="Arial", font_style=FontStyle.BOLD)
                    extrude(text_s.sketch, amount=1.0)

        return anchor.part

if __name__ == "__main__":
    model = AirtagStealthAnchor()
    model.generate()
