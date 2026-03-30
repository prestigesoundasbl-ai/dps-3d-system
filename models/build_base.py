"""
Classe de base pour les modèles build123d DPS (Version Moderne).
Workflow : Python -> build123d -> STL + STEP + SCAD + G-Code.
"""
import os
from abc import ABC, abstractmethod
from build123d import *

PROJECT_ROOT = "/Users/prestigesound/Projects/3D/Active/DPS_3D_SYSTEM"
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'output')

class BuildParametricModel(ABC):
    """Classe abstraite pour modèle build123d avec multi-export."""

    def __init__(self, name: str, **params):
        self.name = name
        self.params = self.default_params()
        self.params.update(params)
        self.part = None

    @abstractmethod
    def default_params(self) -> dict:
        pass

    @abstractmethod
    def build(self) -> Part:
        pass

    def generate(self):
        """Génère tous les formats de fichiers requis."""
        self.part = self.build()
        
        # Dossiers de sortie
        dirs = {
            'stl': os.path.join(OUTPUT_DIR, 'stl'),
            'step': os.path.join(OUTPUT_DIR, 'step'),
            'scad': os.path.join(OUTPUT_DIR, 'scad'),
        }
        for d in dirs.values():
            os.makedirs(d, exist_ok=True)

        # 1. Export STL
        stl_path = os.path.join(dirs['stl'], f"{self.name}.stl")
        export_stl(self.part, stl_path)
        
        # 2. Export STEP
        step_path = os.path.join(dirs['step'], f"{self.name}.step")
        export_step(self.part, step_path)
        
        # 3. Export SCAD (Wrapper pour compatibilité)
        scad_path = os.path.join(dirs['scad'], f"{self.name}.scad")
        with open(scad_path, 'w') as f:
            f.write(f"// Wrapper SCAD pour modèle build123d\n")
            f.write(f"// Pièce : {self.name}\n")
            f.write(f"import(\"../stl/{self.name}.stl\");\n")
        
        print(f"✅ Modèle '{self.name}' exporté : STL, STEP, SCAD.")
        return self.part
