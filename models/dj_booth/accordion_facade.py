"""
Clip Facade/LED Accordion DJ Booth
=====================================
Se clipse sur le tube alu 25mm. Retient le tissu Lycra
et integre un canal pour LED strip WS2812B au dos.

Imprimable CityFab1 : ~40x33x25mm
12-16 necessaires (espaces tous les ~100mm sur la facade).
"""
from solid2 import *
from ..base import ParametricModel
from ._constants import (
    FIT_CLEARANCE,
    LED_CHANNEL_W, LED_STRIP_H,
    ACCORDION_TUBE,
)


class AccordionFacadeClip(ParametricModel):

    def __init__(self, **params):
        super().__init__("accordion_facade_clip", **params)

    def default_params(self):
        return {
            'tube_size': ACCORDION_TUBE,
            'clip_width': 25.0,
            'lycra_slot': 2.0,
            'led_channel': True,
            'fit_clearance': FIT_CLEARANCE,
        }

    def param_schema(self):
        return {
            'tube_size': {
                'type': 'float', 'min': 20, 'max': 30, 'unit': 'mm',
                'description': 'Section tube alu',
            },
            'clip_width': {
                'type': 'float', 'min': 15, 'max': 40, 'unit': 'mm',
                'description': 'Largeur du clip (le long du tube)',
            },
            'lycra_slot': {
                'type': 'float', 'min': 1, 'max': 4, 'unit': 'mm',
                'description': 'Ouverture fente Lycra',
            },
            'led_channel': {
                'type': 'bool',
                'description': 'Ajouter un canal LED au dos',
            },
            'fit_clearance': {
                'type': 'float', 'min': 0.1, 'max': 0.6, 'unit': 'mm',
                'description': 'Jeu d\'ajustement',
            },
        }

    def build(self):
        p = self.params
        tube = p['tube_size']
        clip_w = p['clip_width']
        slot = p['lycra_slot']
        clr = p['fit_clearance']

        inner = tube + 2 * clr
        wall = 3.0  # epaisseur paroi du C-clip

        # Dimensions du clip
        outer_w = inner + 2 * wall
        outer_h = inner + wall  # fond + ouverture en haut

        model = union()

        # --- C-clip (profil en C autour du tube) ---
        # Bloc plein
        body = cube([clip_w, outer_w, outer_h])
        # Evidement pour le tube
        cavity = translate([-0.1, wall, wall])(
            cube([clip_w + 0.2, inner, inner + 0.1])
        )
        body -= cavity

        # Ouverture snap-fit (fente en haut pour enfiler sur le tube)
        snap_gap = inner * 0.5  # ouverture = 50% du tube
        snap = translate([-0.1, (outer_w - snap_gap) / 2, outer_h - wall])(
            cube([clip_w + 0.2, snap_gap, wall + 0.1])
        )
        body -= snap

        # Levres de retention (depassent vers l'interieur)
        lip_h = 1.5
        lip_d = 1.0
        for y_off in [(outer_w - snap_gap) / 2, (outer_w + snap_gap) / 2 - lip_d]:
            lip = translate([0, y_off, outer_h - wall - lip_h])(
                cube([clip_w, lip_d, lip_h])
            )
            body += lip

        model += body

        # --- Fente Lycra (cote avant, perpendiculaire au tube) ---
        lycra_z = outer_h * 0.3  # a 30% de la hauteur
        lycra_fente = translate([-0.1, -0.1, lycra_z])(
            cube([clip_w + 0.2, wall + 0.2, slot])
        )
        model -= lycra_fente

        # --- Canal LED au dos ---
        if p['led_channel']:
            led_w = LED_CHANNEL_W
            led_h = LED_STRIP_H + 2  # profondeur du canal
            led_canal = translate([(clip_w - led_w) / 2, outer_w - led_h, 2])(
                cube([led_w, led_h + 0.1, outer_h - 4])
            )
            model -= led_canal

        return model
