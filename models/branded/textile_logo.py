"""
Textile Logo — DJ Prestige Sound K2 Pro
=========================================
Logo optimisé pour impression directe sur t-shirt/textile.

Deux modes :
  A) TPU mono-couleur (souple, pour grandes surfaces)
  B) PLA multi-couleur noir+or (rigide, pour petits logos)

Le modèle génère un logo très fin (0.6-1.2mm) avec une base
d'accroche de 2 couches qui sera imprimée sur le plateau AVANT
de poser le tissu (technique "sandwich").

Paramètres optimisés pour l'adhérence textile :
  - Première couche large (140%) pour maximiser l'ancrage
  - Pas de bevel/chanfrein (on veut une base plate maximale)
  - Pas de supports (le logo est plat)
  - Bords arrondis pour le confort sur la peau

Workflow OrcaSlicer :
  1. Slicer avec ce modèle
  2. Ajouter PAUSE à la couche 3 (après 2 couches base)
  3. Poser le t-shirt tendu sur les couches de base
  4. Reprendre → le plastique fusionne à travers le tissu
"""
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from build123d import *
from models.build_base import BuildParametricModel
from models.brand import LOGO_TEXT_PRIMARY


class TextileLogo(BuildParametricModel):
    """Logo ultra-fin optimisé pour impression sur textile."""

    def __init__(self, **params):
        super().__init__("textile_logo", **params)

    def default_params(self) -> dict:
        return {
            # Dimensions
            'width': 120.0,          # Largeur du logo
            'height': 30.0,          # Hauteur du logo
            'thickness': 1.0,        # Épaisseur totale (0.6-1.2mm)
            'corner_r': 3.0,         # Rayon des coins (confort peau)

            # Textile
            'base_layers': 2,        # Couches avant pause (sur plateau nu)
            'layer_height': 0.20,    # Hauteur de couche
            'mode': 'tpu_mono',      # tpu_mono ou pla_multicolor

            # Logo texte
            'text': 'PRESTIGE SOUND',
            'text_relief': 0.4,      # Relief du texte (0 = gravé, 0.4 = en relief)

            # Placement
            'placement': 'chest',    # chest, back, sleeve, collar

            'branding': True,
        }

    def build(self) -> Part:
        p = self.params
        w, h = p['width'], p['height']
        t = p['thickness']
        cr = p['corner_r']

        # Adapter les dimensions au placement
        if p['placement'] == 'chest':
            w = min(w, 120)
            h = min(h, 50)
        elif p['placement'] == 'back':
            w = min(w, 250)
            h = min(h, 100)
        elif p['placement'] == 'sleeve':
            w = min(w, 60)
            h = min(h, 25)
        elif p['placement'] == 'collar':
            w = min(w, 70)
            h = min(h, 18)

        # Épaisseur de la base (couches imprimées sur plateau nu)
        base_t = p['base_layers'] * p['layer_height']
        # Épaisseur au-dessus du tissu
        top_t = t - base_t

        with BuildPart() as logo:
            # 1. Base d'accroche (imprimée sur le plateau, SOUS le tissu)
            with BuildSketch() as base_sk:
                RectangleRounded(w, h, cr)
            extrude(amount=base_t)

            # 2. Corps principal (imprimé SUR le tissu)
            # Légèrement plus petit pour que le bord du tissu reste visible
            with BuildPart(mode=Mode.ADD):
                with Locations((0, 0, base_t)):
                    with BuildSketch() as top_sk:
                        RectangleRounded(w - 0.4, h - 0.4, cr)
                    extrude(amount=max(0.2, top_t - p['text_relief']))

            # 3. Zone texte en relief (sera en or si multi-couleur)
            if p['text_relief'] > 0 and p['branding']:
                text_zone_w = w * 0.85
                text_zone_h = h * 0.5
                with BuildPart(mode=Mode.ADD):
                    with Locations((0, 0, base_t + max(0.2, top_t - p['text_relief']))):
                        with BuildSketch() as text_sk:
                            RectangleRounded(text_zone_w, text_zone_h, 1.5)
                        extrude(amount=p['text_relief'])

        return logo.part

    def get_orca_pause_layer(self) -> int:
        """Retourne le numéro de couche où insérer PAUSE dans OrcaSlicer."""
        return self.params['base_layers'] + 1

    def get_pause_gcode(self) -> str:
        """G-code à insérer dans OrcaSlicer pour la pause tissu."""
        return """PAUSE
G91
G1 Z10 F600
G90
; === POSER LE T-SHIRT MAINTENANT ===
; 1. Papier cuisson DANS le t-shirt
; 2. Centrer sur les couches imprimées
; 3. Tendre + fixer avec pinces
; 4. Appuyer RESUME sur l'écran"""

    def get_print_settings(self) -> dict:
        """Retourne les paramètres OrcaSlicer recommandés."""
        if self.params['mode'] == 'tpu_mono':
            return {
                'material': 'TPU 95A',
                'nozzle_temp': [230, 225],
                'bed_temp': 45,
                'speed_first_layer': 12,
                'speed_walls': 20,
                'speed_infill': 25,
                'retraction': 0.8,
                'retraction_speed': 20,
                'fan_first_layers': 0,
                'fan_after': 20,
                'flow_first_layer': 105,
                'first_layer_width': 140,
            }
        else:  # pla_multicolor
            return {
                'material': 'PLA+ (Slot 1 Noir) + PLA Silk (Slot 2 Or)',
                'nozzle_temp': [215, 215],
                'bed_temp': 60,
                'speed_first_layer': 30,
                'speed_walls': 60,
                'speed_infill': 80,
                'retraction': 0.8,
                'retraction_speed': 40,
                'fan_first_layers': 0,
                'fan_after': 100,
                'flow_first_layer': 105,
                'first_layer_width': 140,
            }


# Presets par placement
PRESETS = {
    'chest_small': {
        'width': 80, 'height': 30, 'thickness': 0.8,
        'placement': 'chest', 'text': 'PRESTIGE SOUND',
    },
    'chest_logo': {
        'width': 120, 'height': 45, 'thickness': 1.0,
        'placement': 'chest', 'text': 'PRESTIGE SOUND',
    },
    'back_large': {
        'width': 200, 'height': 60, 'thickness': 1.0,
        'placement': 'back', 'mode': 'tpu_mono', 'text': 'PRESTIGE SOUND',
    },
    'sleeve_badge': {
        'width': 50, 'height': 20, 'thickness': 0.6,
        'placement': 'sleeve', 'text': 'DPS',
    },
    'collar_tag': {
        'width': 60, 'height': 15, 'thickness': 0.6,
        'placement': 'collar', 'text': 'PRESTIGE SOUND',
    },
}


if __name__ == '__main__':
    # Générer tous les presets
    for preset_name, preset_params in PRESETS.items():
        model = TextileLogo(**preset_params)
        model.name = f"textile_logo_{preset_name}"
        model.generate()

        settings = model.get_print_settings()
        pause = model.get_orca_pause_layer()
        print(f"  Pause à couche {pause}")
        print(f"  Mode: {settings['material']}")
        print()
