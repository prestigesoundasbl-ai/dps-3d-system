"""
Classe de base pour tous les modeles parametriques DPS.
Chaque modele herite de ParametricModel et implemente:
  - default_params() : valeurs par defaut
  - param_schema()   : schema JSON pour l'UI (type, min, max, unite)
  - build()          : geometrie SolidPython2
"""
import hashlib
import json
import os
import shutil
import subprocess
from abc import ABC, abstractmethod

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'output')

# Chemin OpenSCAD - cherche dans ~/bin puis PATH
OPENSCAD_BIN = os.path.expanduser('~/bin/openscad')
if not os.path.exists(OPENSCAD_BIN):
    OPENSCAD_BIN = 'openscad'


class ParametricModel(ABC):
    """Classe abstraite pour modele parametrique 3D."""

    def __init__(self, name: str, **params):
        self.name = name
        self.params = self.default_params()
        self.params.update(params)
        self._validate_params()

    @abstractmethod
    def default_params(self) -> dict:
        """Retourne un dict des parametres par defaut."""
        pass

    @abstractmethod
    def param_schema(self) -> dict:
        """Retourne le schema JSON: {param: {type, min, max, unit, description}}."""
        pass

    @abstractmethod
    def build(self):
        """Construit et retourne la geometrie SolidPython2."""
        pass

    def _validate_params(self):
        """Valide les parametres selon le schema."""
        schema = self.param_schema()
        for key, rules in schema.items():
            val = self.params.get(key)
            if val is None:
                continue
            if rules.get('type') in ('float', 'int'):
                if 'min' in rules and val < rules['min']:
                    raise ValueError(f"{key} ({val}) en dessous du minimum ({rules['min']})")
                if 'max' in rules and val > rules['max']:
                    raise ValueError(f"{key} ({val}) au dessus du maximum ({rules['max']})")

    def _params_hash(self) -> str:
        """Hash 8 chars des params pour cache STL."""
        data = json.dumps(
            {'name': self.name, 'params': self.params},
            sort_keys=True, default=str,
        )
        return hashlib.sha256(data.encode()).hexdigest()[:8]

    def save_scad(self) -> str:
        """Genere le fichier .scad, retourne le chemin."""
        geometry = self.build()
        scad_dir = os.path.join(OUTPUT_DIR, 'scad')
        os.makedirs(scad_dir, exist_ok=True)
        path = os.path.join(scad_dir, f"{self.name}.scad")
        geometry.save_as_scad(path)
        return path

    def render_stl(self, use_cache=True) -> str:
        """Compile .scad en .stl via OpenSCAD CLI, avec cache optionnel."""
        stl_dir = os.path.join(OUTPUT_DIR, 'stl')
        os.makedirs(stl_dir, exist_ok=True)
        stl_path = os.path.join(stl_dir, f"{self.name}.stl")

        # Verifier le cache
        if use_cache:
            cache_key = self._params_hash()
            cached_path = os.path.join(stl_dir, f"{self.name}_{cache_key}.stl")
            if os.path.exists(cached_path):
                shutil.copy2(cached_path, stl_path)
                return stl_path

        # Generer le SCAD puis rendre en STL
        scad_path = self.save_scad()
        cmd = [OPENSCAD_BIN, '-o', stl_path, scad_path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            raise RuntimeError(f"Erreur OpenSCAD: {result.stderr}")

        # Sauvegarder dans le cache
        if use_cache:
            cache_key = self._params_hash()
            cached_path = os.path.join(stl_dir, f"{self.name}_{cache_key}.stl")
            shutil.copy2(stl_path, cached_path)

        return stl_path

    def to_dict(self) -> dict:
        """Serialise les infos du modele pour l'API."""
        return {
            'name': self.name,
            'params': self.params,
            'schema': self.param_schema()
        }
