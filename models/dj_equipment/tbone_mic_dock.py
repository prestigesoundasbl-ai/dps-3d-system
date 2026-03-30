"""
Prestige Mic Dock - Support Micro Clipsable pour Flycase
Modèle : tbone_mic_dock.py (Version 1.0)
Auteur : Binôme IA (Gemini Orchestrator)
Usage : Se clipse sur la paroi de 7mm du Flycase pour accueillir le micro t.bone.
"""
import os
import sys
import math

# Ajout du chemin racine du projet au PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from build123d import *
from models.build_base import BuildParametricModel
from models.brand import BRAND_NAME_SHORT

class TboneMicDock(BuildParametricModel):
    """Support micro clipsable et incliné."""

    def __init__(self, **params):
        super().__init__("tbone_mic_dock", **params)

    def default_params(self) -> dict:
        return {
            'wall_t': 7.0,      # Épaisseur Flycase
            'mic_d': 37.0,      # Diamètre corps micro t.bone
            'angle': 15.0,      # Inclinaison sécurité
            'clip_depth': 35.0, # Profondeur clip
            'dock_h': 40.0,     # Hauteur du berceau
            'wall_struct': 4.0, # Épaisseur structure
        }

    def build(self) -> Part:
        p = self.params
        wt = p['wall_t'] + 0.4
        md = p['mic_d']
        st = p['wall_struct']
        ch = p['dock_h']
        cdepth = p['clip_depth']
        angle = p['angle']
        
        # Largeur de l'objet (un peu plus que le micro)
        tw = md + (2 * st)

        with BuildPart() as dock:
            # 1. Le Clip Arrière (U inversé par primitives pour stabilité)
            # Pont supérieur
            with Locations((0, 0, (md/2 + st + st)/2)):
                Box(tw, wt + (2 * st), st)
            # Bras intérieur (dans le case)
            with Locations((0, -(wt/2 + st/2), -(cdepth/2 - st/2))):
                Box(tw, st, cdepth)
            # Bras extérieur (support du dock)
            with Locations((0, (wt/2 + st/2), -(cdepth/2 - st/2))):
                Box(tw, st, cdepth)

            # 2. Le Berceau Micro (Cylindre incliné)
            # On le décale vers l'avant pour ne pas gêner le clip
            with BuildPart(mode=Mode.ADD):
                with Locations((0, wt/2 + st + md/2, 0)):
                    # On crée une rotation pour l'inclinaison de sécurité
                    with Locations(Rotation(angle, 0, 0)):
                        # Corps du berceau
                        Cylinder(radius=md/2 + st, height=ch)
                        # Évidement interne pour le micro (Soustraction)
                        with BuildPart(mode=Mode.SUBTRACT):
                            Cylinder(radius=md/2, height=ch + 2)
                            # Ouverture frontale pour glisser le micro par le côté
                            with Locations((0, md/2, 0)):
                                Box(md * 0.8, md, ch + 2)

        return dock.part

if __name__ == "__main__":
    model = TboneMicDock()
    model.generate()
