"""
Panneau Logo pour DJ Booth - Prestige Sound
Panneau central avec texte "PRESTIGE SOUND" decoupe/translucide/relief.
Canal LED perimetrique pour retroeclairage.
Auto-split en 2 moities si >215mm (limite Big Builder CityFab1).
Trous de goujons d'alignement au joint.
"""
from solid2 import *
from ..base import ParametricModel
from ._constants import (
    PROFILE_W, SLOT_WIDTH, SLOT_DEPTH, SLOT_CLEARANCE,
    FIT_CLEARANCE, LED_CHANNEL_W, TILE_CLIP_DEPTH
)


class BoothLogoPanel(ParametricModel):

    def __init__(self, **params):
        super().__init__("booth_logo_panel", **params)

    def default_params(self):
        return {
            'panel_width': 400.0,
            'panel_height': 200.0,
            'panel_thickness': 5.0,
            'logo_width': 300.0,
            'logo_style': 'cutout',
            'led_perimeter': True,
            'led_channel_width': 14.0,
            'led_channel_depth': 5.0,
            'frame_width': 15.0,
            'auto_split': True,
            'split_overlap': 2.0,
            'dowel_holes': True,
            'dowel_diameter': 4.0,
            'dowel_depth': 8.0,
            'clip_count': 2,
            'half': 'left',
        }

    def param_schema(self):
        return {
            'panel_width': {
                'type': 'float', 'min': 100, 'max': 600, 'unit': 'mm',
                'description': 'Largeur totale du panneau logo'
            },
            'panel_height': {
                'type': 'float', 'min': 80, 'max': 400, 'unit': 'mm',
                'description': 'Hauteur du panneau'
            },
            'panel_thickness': {
                'type': 'float', 'min': 3, 'max': 10, 'unit': 'mm',
                'description': 'Epaisseur du panneau'
            },
            'logo_width': {
                'type': 'float', 'min': 50, 'max': 500, 'unit': 'mm',
                'description': 'Largeur de la zone logo/texte'
            },
            'logo_style': {
                'type': 'select',
                'options': ['cutout', 'translucent', 'relief'],
                'description': 'Style du logo (decoupe, translucide 0.8mm, relief)'
            },
            'led_perimeter': {
                'type': 'bool',
                'description': 'Canal LED perimetrique autour du logo'
            },
            'led_channel_width': {
                'type': 'float', 'min': 10, 'max': 20, 'unit': 'mm',
                'description': 'Largeur du canal LED'
            },
            'led_channel_depth': {
                'type': 'float', 'min': 3, 'max': 8, 'unit': 'mm',
                'description': 'Profondeur du canal LED'
            },
            'frame_width': {
                'type': 'float', 'min': 8, 'max': 30, 'unit': 'mm',
                'description': 'Largeur du cadre autour du panneau'
            },
            'auto_split': {
                'type': 'bool',
                'description': 'Auto-split si >215mm (limite imprimante)'
            },
            'half': {
                'type': 'select',
                'options': ['left', 'right', 'full'],
                'description': 'Moitie a generer (left/right) ou panneau complet (full)'
            },
            'clip_count': {
                'type': 'int', 'min': 1, 'max': 4,
                'description': 'Nombre de clips de fixation par cote'
            },
            'dowel_holes': {
                'type': 'bool',
                'description': 'Trous de goujons d\'alignement au joint'
            },
            'dowel_diameter': {
                'type': 'float', 'min': 2, 'max': 6, 'unit': 'mm',
                'description': 'Diametre des goujons'
            },
            'dowel_depth': {
                'type': 'float', 'min': 4, 'max': 15, 'unit': 'mm',
                'description': 'Profondeur des trous de goujons'
            },
        }

    def _build_full_panel(self):
        """Construit le panneau complet (avant split)."""
        p = self.params
        w = p['panel_width']
        h = p['panel_height']
        t = p['panel_thickness']
        fw = p['frame_width']
        logo_w = p['logo_width']

        # -- Plaque de base --
        panel = cube([w, h, t])

        # -- Cadre decoratif (bord plus epais +1mm) --
        frame_outer = cube([w, h, t + 1])
        frame_inner = translate([fw, fw, -0.1])(
            cube([w - 2 * fw, h - 2 * fw, t + 1.2])
        )
        frame_relief = frame_outer - frame_inner
        panel = panel + frame_relief

        # -- Chanfrein sur le bord avant du cadre --
        chamfer = 1.5
        chamfer_strip_top = translate([0, h - chamfer, t + 1 - chamfer])(
            rotate([45, 0, 0])(cube([w, chamfer * 1.5, chamfer * 1.5]))
        )
        chamfer_strip_bottom = translate([0, -chamfer * 0.5, t + 1 - chamfer])(
            rotate([45, 0, 0])(cube([w, chamfer * 1.5, chamfer * 1.5]))
        )

        # -- Logo texte --
        text_size = logo_w / 10
        logo_text = linear_extrude(height=t + 2)(
            text("PRESTIGE SOUND", size=text_size,
                 font="Liberation Sans:style=Bold",
                 halign="center", valign="center", _fn=64)
        )
        logo_text = translate([w / 2, h / 2, 0])(logo_text)

        if p['logo_style'] == 'cutout':
            # Texte decoupe completement (lumiere passe a travers)
            panel = panel - translate([0, 0, -0.1])(logo_text)

        elif p['logo_style'] == 'translucent':
            # Texte avec fond 0.8mm (translucide en PLA)
            trans_t = 0.8
            cut_text = linear_extrude(height=t - trans_t + 0.1)(
                text("PRESTIGE SOUND", size=text_size,
                     font="Liberation Sans:style=Bold",
                     halign="center", valign="center", _fn=64)
            )
            cut_text = translate([w / 2, h / 2, trans_t])(cut_text)
            panel = panel - cut_text

        elif p['logo_style'] == 'relief':
            # Texte en relief (+1.5mm au dessus)
            relief_h = 1.5
            relief_text = linear_extrude(height=relief_h)(
                text("PRESTIGE SOUND", size=text_size,
                     font="Liberation Sans:style=Bold",
                     halign="center", valign="center", _fn=64)
            )
            relief_text = translate([w / 2, h / 2, t + 1])(relief_text)
            panel = panel + relief_text

        # -- Canal LED perimetrique (face arriere) --
        if p['led_perimeter']:
            ch_w = p['led_channel_width']
            ch_d = p['led_channel_depth']
            wall = 1.5
            margin = fw + 2

            # Canal rectangulaire autour du logo sur la face arriere
            # Fond
            ch_outer_w = w - 2 * margin
            ch_outer_h = h - 2 * margin
            ch_inner_w = ch_outer_w - 2 * (ch_w + wall)
            ch_inner_h = ch_outer_h - 2 * (ch_w + wall)

            if ch_inner_w > 0 and ch_inner_h > 0:
                channel_base = translate([margin, margin, -ch_d])(
                    cube([ch_outer_w, ch_outer_h, ch_d])
                )
                channel_hollow = translate([margin + ch_w + wall,
                                           margin + ch_w + wall, -ch_d - 0.1])(
                    cube([ch_inner_w, ch_inner_h, ch_d + 0.2])
                )
                channel = channel_base - channel_hollow
                panel = panel + channel

        # -- Clips de fixation (haut et bas) --
        if p['clip_count'] > 0:
            clips = self._build_clips(w, h, t)
            if clips is not None:
                panel = panel + clips

        return panel

    def _build_clips(self, w, h, t):
        """Clips de fixation pour rails 2040."""
        p = self.params
        clip_count = p['clip_count']
        clips = None
        clip_w = 10.0
        clip_depth = TILE_CLIP_DEPTH
        clip_h = 6.0
        slot_engage = SLOT_WIDTH - 2 * SLOT_CLEARANCE

        spacing = w / (clip_count + 1)

        for i in range(clip_count):
            cx = spacing * (i + 1) - clip_w / 2

            # Clip bas
            clip_bottom = translate([cx, 0, -clip_h])(
                cube([clip_w, clip_depth, clip_h])
            )
            hook_bottom = translate([cx + (clip_w - slot_engage) / 2,
                                    clip_depth - 2, -clip_h - 2])(
                cube([slot_engage, 2, clip_h + 2])
            )

            # Clip haut
            clip_top = translate([cx, h - clip_depth, -clip_h])(
                cube([clip_w, clip_depth, clip_h])
            )
            hook_top = translate([cx + (clip_w - slot_engage) / 2,
                                 h - 2, -clip_h - 2])(
                cube([slot_engage, 2, clip_h + 2])
            )

            c = clip_bottom + hook_bottom + clip_top + hook_top
            clips = c if clips is None else clips + c

        return clips

    def _add_dowel_holes(self, panel, split_x, h, t):
        """Ajoute des trous de goujons sur la face de split."""
        p = self.params
        dd = p['dowel_diameter']
        depth = p['dowel_depth']

        # 2 trous espaces verticalement
        y_positions = [h * 0.3, h * 0.7]
        z_center = t / 2

        for y in y_positions:
            hole = translate([split_x - depth, y, z_center])(
                rotate([0, 90, 0])(
                    cylinder(d=dd, h=depth * 2, _fn=24)
                )
            )
            panel = panel - hole

        return panel

    def build(self):
        p = self.params
        w = p['panel_width']
        h = p['panel_height']
        half = p['half']

        # Construire le panneau complet
        full = self._build_full_panel()

        # Auto-split si necessaire
        needs_split = p['auto_split'] and w > 215.0 and half != 'full'

        if not needs_split:
            return full

        split_x = w / 2

        if half == 'left':
            # Couper la moitie gauche
            cutter = translate([-0.1, -0.1, -50])(
                cube([split_x + p['split_overlap'], h + 0.2, 200])
            )
            panel = full * cutter
            if p['dowel_holes']:
                panel = self._add_dowel_holes(panel, split_x, h, p['panel_thickness'])
            return panel

        elif half == 'right':
            # Couper la moitie droite
            cutter = translate([split_x - p['split_overlap'], -0.1, -50])(
                cube([split_x + p['split_overlap'] + 0.1, h + 0.2, 200])
            )
            panel = full * cutter
            # Recentrer a l'origine
            panel = translate([-(split_x - p['split_overlap']), 0, 0])(panel)
            if p['dowel_holes']:
                panel = self._add_dowel_holes(panel, p['split_overlap'], h,
                                              p['panel_thickness'])
            return panel

        return full


if __name__ == "__main__":
    import sys
    panel = BoothLogoPanel()
    print(f"Generation panneau logo booth (moitie gauche)...")
    print(f"Parametres: {panel.params}")
    scad_path = panel.save_scad()
    print(f"SCAD: {scad_path}")
    try:
        stl_path = panel.render_stl()
        print(f"STL: {stl_path}")
        print("OK")
    except Exception as e:
        print(f"Erreur STL: {e}", file=sys.stderr)
