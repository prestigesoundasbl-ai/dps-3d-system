"""
Adaptateur de Pied Télescopique Ø35/Ø30 - Flycase Prestige
Modèle : leg_adapter_35_30.py (Version 1.1)
Optimisation : Ajout de chanfreins d'insertion et renforcement du logement écrou.
"""
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from build123d import *
from models.build_base import BuildParametricModel

class LegAdapter(BuildParametricModel):
    def __init__(self, **params):
        super().__init__("leg_adapter_35_30", **params)

    def default_params(self) -> dict:
        return {
            'ext_tube_d': 34.8,
            'int_tube_d': 30.4,
            'insert_len': 50.0,
            'collar_h': 15.0,
            'collar_d': 45.0,
            'nut_size': 10.2, # Légèrement plus grand pour l'écrou M6
            'bolt_d': 6.5,
        }

    def build(self) -> Part:
        p = self.params
        er, ir = p['ext_tube_d']/2, p['int_tube_d']/2
        cl, ch, cd = p['insert_len'], p['collar_h'], p['collar_d']
        
        with BuildPart() as adapter:
            # 1. Corps
            with BuildSketch() as s:
                Circle(cd/2)
            extrude(amount=ch)
            
            with BuildSketch(adapter.faces().sort_by(Axis.Z)[0]) as s2:
                Circle(er)
            extrude(amount=-cl)
            
            # 2. Évidement Central
            with BuildPart(mode=Mode.SUBTRACT):
                Cylinder(radius=ir, height=cl + ch + 10)
            
            # 3. Logement Écrou M6 (Renforcé)
            with BuildPart(mode=Mode.SUBTRACT):
                with Locations((0, cd/2 - 6, ch/2)):
                    Cylinder(radius=p['bolt_d']/2, height=30, rotation=(90, 0, 0))
                    with BuildSketch(Plane.XZ) as nut_s:
                        RegularPolygon(radius=p['nut_size']/1.732, side_count=6) # Rayon circonscrit
                    extrude(amount=6)

            # 4. OPTIMISATION : Chanfreins d'insertion
            # Sur le bas de la tige d'insertion
            chamfer(adapter.edges().sort_by(Axis.Z)[0], length=2.0)
            # Sur le haut de la collerette pour le look
            chamfer(adapter.edges().sort_by(Axis.Z)[-1], length=1.5)

        return adapter.part

if __name__ == "__main__":
    model = LegAdapter()
    model.generate()
