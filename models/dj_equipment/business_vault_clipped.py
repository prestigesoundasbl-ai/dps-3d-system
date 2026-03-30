"""
Prestige Business Vault - Clipped Edition
Modèle : business_vault_clipped.py (Version 1.1)
Approche : Assemblage de primitives pour stabilité maximale.
"""
import os
import sys

# Ajout du chemin racine du projet au PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from build123d import *
from models.build_base import BuildParametricModel

class BusinessVaultClipped(BuildParametricModel):
    def __init__(self, **params):
        super().__init__("business_vault_clipped", **params)

    def default_params(self) -> dict:
        return {
            'wall_t': 7.0,
            'card_w': 86.0,
            'card_d': 56.0,
            'stack_h': 30.0,
            'st': 4.0, # wall_struct
            'cdepth': 35.0, # clip_depth
        }

    def build(self) -> Part:
        p = self.params
        wt, cw, cd, th, st, cdepth = p['wall_t']+0.4, p['card_w'], p['card_d'], p['stack_h']+4.0, p['st'], p['cdepth']
        
        # Largeur totale
        tw = cw + (2 * st)
        # Hauteur totale boîtier
        vh = cd + (2 * st)

        with BuildPart() as vault:
            # 1. Le Corps du Boîtier (Horizontal sur le bord)
            Box(tw, th, vh)
            
            # 2. Le Réservoir (Soustraction)
            with BuildPart(mode=Mode.SUBTRACT):
                Box(cw, th + 2, cd)
            
            # 3. Le Clip (U inversé à l'arrière)
            # Positionnement à l'arrière du boîtier
            with BuildPart(mode=Mode.ADD):
                with Locations((0, -th/2 - st/2, 0)):
                    # Bras arrière du clip
                    with Locations((0, -st/2 - wt, -vh/2 + cdepth/2)):
                        Box(tw, st, cdepth)
                    # Pont supérieur
                    with Locations((0, -wt/2, vh/2 - st/2)):
                        Box(tw, wt + (2*st), st)
            
            # 4. Encoche pour le pouce (Face avant)
            with BuildPart(mode=Mode.SUBTRACT):
                with Locations((0, th/2, -vh/2 + st)):
                    Cylinder(radius=15, height=st*4, rotation=(90, 0, 0))

        return vault.part

if __name__ == "__main__":
    model = BusinessVaultClipped()
    model.generate()
