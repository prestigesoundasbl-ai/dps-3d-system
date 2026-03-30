"""
Plaque Logo Bicolore Accordion DJ Booth
=========================================
Panneau central avec logo Prestige Sound.
Support multi-couleur (noir + or) via export multi-part.

Export:
  - plate_body (noir) : plaque + cadre + cavite
  - plate_logo (or)   : logo en relief

Imprimable CityFab1 : 200x150x5mm (dans limite 215mm).
1 necessaire.
"""
from solid2 import *
from ..base import ParametricModel
from ..logo import logo_3d
from ._constants import (
    M5_HOLE,
    ACCORDION_PANEL_T,
)


class AccordionLogoPlate(ParametricModel):

    def __init__(self, **params):
        super().__init__("accordion_logo_plate", **params)

    def default_params(self):
        return {
            'plate_width': 200.0,
            'plate_height': 150.0,
            'plate_thickness': 5.0,
            'logo_quality': 'normal',
            'frame_width': 5.0,
            'frame_height': 2.0,
            'backlight': True,
            'export_part': 'all',
        }

    def param_schema(self):
        return {
            'plate_width': {
                'type': 'float', 'min': 100, 'max': 215, 'unit': 'mm',
                'description': 'Largeur de la plaque (max 215 pour CityFab)',
            },
            'plate_height': {
                'type': 'float', 'min': 80, 'max': 205, 'unit': 'mm',
                'description': 'Hauteur de la plaque',
            },
            'plate_thickness': {
                'type': 'float', 'min': 3, 'max': 8, 'unit': 'mm',
                'description': 'Epaisseur totale de la plaque',
            },
            'logo_quality': {
                'type': 'string',
                'options': ['draft', 'normal', 'fine'],
                'description': 'Qualite du logo',
            },
            'frame_width': {
                'type': 'float', 'min': 3, 'max': 10, 'unit': 'mm',
                'description': 'Largeur du cadre decoratif',
            },
            'frame_height': {
                'type': 'float', 'min': 1, 'max': 4, 'unit': 'mm',
                'description': 'Hauteur relief du cadre',
            },
            'backlight': {
                'type': 'bool',
                'description': 'Cavite LED backlight (0.8mm translucide)',
            },
            'export_part': {
                'type': 'string',
                'options': ['all', 'plate_body', 'plate_logo'],
                'description': 'Piece a exporter (all, plate_body, plate_logo)',
            },
        }

    def build(self):
        p = self.params
        pw = p['plate_width']
        ph = p['plate_height']
        pt = p['plate_thickness']
        fw = p['frame_width']
        fh = p['frame_height']
        mode = p['export_part']
        logo_q = p['logo_quality']

        # --- Plaque de base ---
        base = cube([pw, ph, pt])

        # 4 trous M5 aux coins
        inset = 8
        for x in [inset, pw - inset]:
            for y in [inset, ph - inset]:
                hole = translate([x, y, -0.1])(
                    cylinder(d=M5_HOLE, h=pt + 0.2, _fn=24)
                )
                base -= hole

        # --- Cadre art deco en relief ---
        frame_outer = translate([0, 0, pt])(
            cube([pw, ph, fh])
        )
        frame_inner = translate([fw, fw, pt - 0.1])(
            cube([pw - 2 * fw, ph - 2 * fw, fh + 0.2])
        )
        frame = frame_outer - frame_inner

        # Second cadre interieur (art deco double)
        inner_margin = fw + 3
        frame2_outer = translate([inner_margin, inner_margin, pt])(
            cube([pw - 2 * inner_margin, ph - 2 * inner_margin, fh * 0.6])
        )
        frame2_inner = translate([inner_margin + 2, inner_margin + 2, pt - 0.1])(
            cube([pw - 2 * inner_margin - 4, ph - 2 * inner_margin - 4, fh * 0.6 + 0.2])
        )
        frame += frame2_outer - frame2_inner

        # Ornements de coins (petits carres aux coins du cadre exterieur)
        corner_size = fw * 1.5
        corner_h = fh * 0.8
        for x in [-corner_size / 4, pw - corner_size * 3 / 4]:
            for y in [-corner_size / 4, ph - corner_size * 3 / 4]:
                corner = translate([x, y, pt])(
                    cube([corner_size, corner_size, corner_h])
                )
                frame += corner

        # --- Cavite LED backlight ---
        if p['backlight']:
            # Evidement au dos pour LED, laisse 0.8mm de PLA translucide
            backlight_margin = fw + 5
            shell_thickness = 0.8
            base -= translate([backlight_margin, backlight_margin, -0.1])(
                cube([
                    pw - 2 * backlight_margin,
                    ph - 2 * backlight_margin,
                    pt - shell_thickness + 0.1,
                ])
            )

        # --- Logo ---
        logo_w = pw * 0.55
        logo_h = 1.5
        logo_obj = logo_3d(width=logo_w, height=logo_h, quality=logo_q)
        # Centrer le logo sur la plaque
        logo_placed = translate([pw / 2, ph / 2, pt + fh])(
            logo_obj
        )

        # --- Export multi-part ---
        if mode == 'plate_body':
            return base + frame
        if mode == 'plate_logo':
            return logo_placed
        # mode == 'all'
        return base + frame + logo_placed
