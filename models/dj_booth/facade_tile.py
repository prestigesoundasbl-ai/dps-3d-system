"""
Tuile de Facade pour DJ Booth - Panneau decoratif modulaire
200x200mm avec patterns multiples, canal LED, zones translucides et clips T-slot.
Se clipse sur les rails 2040. ~24 necessaires (6 colonnes x 4 rangees).
"""
import math
from solid2 import *
from ..base import ParametricModel
from ._constants import (
    PROFILE_W, SLOT_WIDTH, SLOT_DEPTH, SLOT_CLEARANCE,
    FIT_CLEARANCE, LED_STRIP_W, LED_CHANNEL_W,
    TILE_SIZE, TILE_THICKNESS, TILE_CLIP_DEPTH
)


class BoothFacadeTile(ParametricModel):

    def __init__(self, **params):
        super().__init__("booth_facade_tile", **params)

    def default_params(self):
        return {
            'width': TILE_SIZE,
            'height': TILE_SIZE,
            'thickness': TILE_THICKNESS,
            'pattern': 'geometric',
            'translucent_zones': True,
            'translucent_thickness': 0.8,
            'led_channel': True,
            'clip_count': 2,
            'frame_width': 8.0,
            'corner_radius': 3.0,
        }

    def param_schema(self):
        return {
            'width': {
                'type': 'float', 'min': 50, 'max': 300, 'unit': 'mm',
                'description': 'Largeur de la tuile'
            },
            'height': {
                'type': 'float', 'min': 50, 'max': 300, 'unit': 'mm',
                'description': 'Hauteur de la tuile'
            },
            'thickness': {
                'type': 'float', 'min': 2, 'max': 10, 'unit': 'mm',
                'description': 'Epaisseur de base'
            },
            'pattern': {
                'type': 'select',
                'options': ['geometric', 'hexagonal', 'perforated', 'waves', 'plain'],
                'description': 'Motif decoratif de la facade'
            },
            'translucent_zones': {
                'type': 'bool',
                'description': 'Zones minces (0.8mm) pour passage lumiere LED'
            },
            'translucent_thickness': {
                'type': 'float', 'min': 0.4, 'max': 1.6, 'unit': 'mm',
                'description': 'Epaisseur des zones translucides (2 couches = 0.8mm)'
            },
            'led_channel': {
                'type': 'bool',
                'description': 'Canal arriere pour bande LED WS2812B'
            },
            'clip_count': {
                'type': 'int', 'min': 1, 'max': 4,
                'description': 'Nombre de clips de fixation par cote (haut+bas)'
            },
            'frame_width': {
                'type': 'float', 'min': 4, 'max': 15, 'unit': 'mm',
                'description': 'Largeur du cadre autour du motif'
            },
            'corner_radius': {
                'type': 'float', 'min': 0, 'max': 10, 'unit': 'mm',
                'description': 'Rayon des coins arrondis'
            },
        }

    def _build_frame(self, w, h, t, fw):
        """Construit le cadre exterieur de la tuile."""
        outer = cube([w, h, t])
        inner_w = w - 2 * fw
        inner_h = h - 2 * fw
        if inner_w > 0 and inner_h > 0:
            cutout = translate([fw, fw, -0.1])(
                cube([inner_w, inner_h, t + 0.2])
            )
            return outer - cutout, inner_w, inner_h
        return outer, 0, 0

    def _pattern_geometric(self, iw, ih, t, fw, trans_t):
        """Motif geometrique : grille de losanges."""
        cell = 25.0
        diamond_size = cell * 0.65
        pattern = None
        floor_t = trans_t if self.params['translucent_zones'] else 0

        cols = int(iw / cell) + 1
        rows = int(ih / cell) + 1

        # Base fine dans la zone de pattern
        base = translate([fw, fw, 0])(
            cube([iw, ih, floor_t])
        ) if floor_t > 0 else None

        for ix in range(cols):
            for iy in range(rows):
                cx = fw + cell / 2 + ix * cell
                cy = fw + cell / 2 + iy * cell
                if cx > fw + iw or cy > fw + ih:
                    continue
                diamond = translate([cx, cy, 0])(
                    rotate([0, 0, 45])(
                        translate([-diamond_size / 2, -diamond_size / 2, 0])(
                            cube([diamond_size, diamond_size, t])
                        )
                    )
                )
                pattern = diamond if pattern is None else pattern + diamond

        if pattern is not None:
            # Clipper au cadre interieur
            mask = translate([fw, fw, -0.1])(cube([iw, ih, t + 0.2]))
            pattern = pattern * mask
            if base is not None:
                pattern = pattern + base
        return pattern

    def _pattern_hexagonal(self, iw, ih, t, fw, trans_t):
        """Motif nid d'abeille : hexagones en grille decalee."""
        hex_d = 22.0
        wall = 2.5
        hex_r = (hex_d - wall) / 2
        floor_t = trans_t if self.params['translucent_zones'] else 0

        # Plaque pleine comme base
        base = translate([fw, fw, 0])(cube([iw, ih, t]))

        # Soustraire les hexagones
        holes = None
        step_x = hex_d * 0.866
        step_y = hex_d * 0.75

        cols = int(iw / step_x) + 2
        rows = int(ih / step_y) + 2

        for ix in range(cols):
            for iy in range(rows):
                offset_x = (iy % 2) * (step_x / 2)
                cx = fw + step_x / 2 + ix * step_x + offset_x
                cy = fw + step_y / 2 + iy * step_y
                if cx < fw or cx > fw + iw or cy < fw or cy > fw + ih:
                    continue
                cut_depth = t - floor_t if floor_t > 0 else t + 0.2
                cut_z = floor_t if floor_t > 0 else -0.1
                hole = translate([cx, cy, cut_z])(
                    cylinder(r=hex_r, h=cut_depth + 0.1, _fn=6)
                )
                holes = hole if holes is None else holes + hole

        if holes is not None:
            mask = translate([fw, fw, -0.1])(cube([iw, ih, t + 0.2]))
            holes = holes * mask
            base = base - holes

        return base

    def _pattern_perforated(self, iw, ih, t, fw, trans_t):
        """Motif perfore : grille reguliere de trous circulaires."""
        hole_d = 8.0
        spacing = 14.0
        floor_t = trans_t if self.params['translucent_zones'] else 0

        base = translate([fw, fw, 0])(cube([iw, ih, t]))
        holes = None

        cols = int(iw / spacing) + 1
        rows = int(ih / spacing) + 1

        for ix in range(cols):
            for iy in range(rows):
                cx = fw + spacing / 2 + ix * spacing
                cy = fw + spacing / 2 + iy * spacing
                if cx > fw + iw - spacing / 4 or cy > fw + ih - spacing / 4:
                    continue
                cut_depth = t - floor_t if floor_t > 0 else t + 0.2
                cut_z = floor_t if floor_t > 0 else -0.1
                hole = translate([cx, cy, cut_z])(
                    cylinder(d=hole_d, h=cut_depth + 0.1, _fn=24)
                )
                holes = hole if holes is None else holes + hole

        if holes is not None:
            mask = translate([fw, fw, -0.1])(cube([iw, ih, t + 0.2]))
            holes = holes * mask
            base = base - holes

        return base

    def _pattern_waves(self, iw, ih, t, fw, trans_t):
        """Motif vagues : nervures horizontales ondulees."""
        wave_count = 5
        wave_width = 3.0
        amplitude = 6.0
        floor_t = trans_t if self.params['translucent_zones'] else 0
        segments = 20

        # Base fine
        base = translate([fw, fw, 0])(
            cube([iw, ih, floor_t if floor_t > 0 else t])
        )

        if floor_t > 0:
            # Construire les nervures comme des series de hull() entre cylindres
            wave_spacing = ih / (wave_count + 1)

            for w_idx in range(wave_count):
                cy_base = fw + wave_spacing * (w_idx + 1)
                points = []
                for s in range(segments + 1):
                    x = fw + (iw * s / segments)
                    y = cy_base + amplitude * math.sin(2 * math.pi * s / segments)
                    points.append((x, y))

                for s in range(segments):
                    x1, y1 = points[s]
                    x2, y2 = points[s + 1]
                    seg = hull()(
                        translate([x1, y1, 0])(
                            cylinder(d=wave_width, h=t, _fn=12)
                        ),
                        translate([x2, y2, 0])(
                            cylinder(d=wave_width, h=t, _fn=12)
                        )
                    )
                    base = base + seg

            # Clipper
            mask = translate([fw - 0.1, fw - 0.1, -0.1])(
                cube([iw + 0.2, ih + 0.2, t + 0.2])
            )
            base = base * mask

        return base

    def _pattern_plain(self, iw, ih, t, fw):
        """Motif plain : panneau plat avec cadre."""
        return translate([fw, fw, 0])(cube([iw, ih, t]))

    def _build_clips(self, w, h, t, clip_count):
        """Construit les clips de fixation pour rails 2040."""
        clips = None
        clip_w = 10.0
        clip_depth = TILE_CLIP_DEPTH
        clip_h = 6.0
        hook_h = 2.0
        slot_engage = SLOT_WIDTH - 2 * SLOT_CLEARANCE

        spacing = w / (clip_count + 1)

        for edge in ['top', 'bottom']:
            for i in range(clip_count):
                cx = spacing * (i + 1) - clip_w / 2

                # Corps du clip (derriere la tuile)
                body = translate([cx, 0, 0])(
                    cube([clip_w, clip_depth, clip_h])
                )
                # Crochet (retour qui s'accroche dans le slot)
                hook = translate([cx + (clip_w - slot_engage) / 2,
                                 clip_depth - hook_h, 0])(
                    cube([slot_engage, hook_h, clip_h + 2])
                )

                clip = body + hook

                if edge == 'top':
                    clip = translate([0, -clip_depth, t])(clip)
                    clip = translate([0, 0, 0])(clip)
                    # Positionner en haut de la tuile, face arriere
                    clip = translate([0, h - 1, 0])(
                        mirror([0, 0, 0])(clip)
                    )
                    # Simplifier : clip sur le bord superieur arriere
                    clip = translate([cx, 0, t])(
                        cube([clip_w, clip_depth, clip_h])
                    )
                    hook_part = translate([cx + (clip_w - slot_engage) / 2,
                                          clip_depth - hook_h, t])(
                        cube([slot_engage, hook_h, clip_h + hook_h])
                    )
                    clip = clip + hook_part
                    clip = translate([0, h, 0])(
                        mirror([0, 1, 0])(clip)
                    )
                else:
                    # Clip sur le bord inferieur arriere
                    clip = translate([cx, 0, t])(
                        cube([clip_w, clip_depth, clip_h])
                    )
                    hook_part = translate([cx + (clip_w - slot_engage) / 2,
                                          clip_depth - hook_h, t])(
                        cube([slot_engage, hook_h, clip_h + hook_h])
                    )
                    clip = clip + hook_part

                clips = clip if clips is None else clips + clip

        return clips

    def _build_led_channel(self, w, t):
        """Canal LED sur la face arriere, le long du bord inferieur."""
        ch_w = LED_CHANNEL_W
        ch_depth = 5.0
        wall = 1.5

        # U-channel : deux murs + fond
        channel = translate([0, 0, t])(
            cube([w, ch_w + 2 * wall, wall])  # fond
        )
        channel += translate([0, 0, t + wall])(
            cube([w, wall, ch_depth])  # mur avant
        )
        channel += translate([0, ch_w + wall, t + wall])(
            cube([w, wall, ch_depth])  # mur arriere
        )

        # Ouvertures aux extremites pour routage LED
        cutout_w = 8.0
        channel -= translate([-0.1, wall, t + wall])(
            cube([cutout_w, ch_w, ch_depth + 0.1])
        )
        channel -= translate([w - cutout_w + 0.1, wall, t + wall])(
            cube([cutout_w, ch_w, ch_depth + 0.1])
        )

        return channel

    def build(self):
        p = self.params
        w = p['width']
        h = p['height']
        t = p['thickness']
        fw = p['frame_width']
        trans_t = p['translucent_thickness']
        pattern = p['pattern']

        # -- Cadre exterieur --
        frame, iw, ih = self._build_frame(w, h, t, fw)

        # -- Remplissage selon le pattern --
        fill = None
        if iw > 0 and ih > 0:
            if pattern == 'geometric':
                fill = self._pattern_geometric(iw, ih, t, fw, trans_t)
            elif pattern == 'hexagonal':
                fill = self._pattern_hexagonal(iw, ih, t, fw, trans_t)
            elif pattern == 'perforated':
                fill = self._pattern_perforated(iw, ih, t, fw, trans_t)
            elif pattern == 'waves':
                fill = self._pattern_waves(iw, ih, t, fw, trans_t)
            elif pattern == 'plain':
                fill = self._pattern_plain(iw, ih, t, fw)

        model = frame
        if fill is not None:
            model = model + fill

        # -- Clips de fixation --
        if p['clip_count'] > 0:
            clips = self._build_clips(w, h, t, p['clip_count'])
            if clips is not None:
                model = model + clips

        # -- Canal LED arriere --
        if p['led_channel']:
            led_ch = self._build_led_channel(w, t)
            model = model + led_ch

        return model


if __name__ == "__main__":
    import sys
    tile = BoothFacadeTile()
    print(f"Generation tuile facade booth...")
    print(f"Parametres: {tile.params}")
    scad_path = tile.save_scad()
    print(f"SCAD: {scad_path}")
    try:
        stl_path = tile.render_stl()
        print(f"STL: {stl_path}")
        print("OK")
    except Exception as e:
        print(f"Erreur STL: {e}", file=sys.stderr)
