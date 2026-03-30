"""
Accordion DJ Booth — Concept Pliable Multi-Pieces DJ Prestige Sound
=====================================================================
Meuble DJ pliable en accordeon : centre + 2 ailes laterales.
Se plie comme un accordeon pour transport (~700x500x100mm),
se deploie en ~5 min en booth complet (~1400x500mm, hauteur 1000mm).

Structure : tubes alu 25x25mm + pieces 3D imprimees (connecteurs, charnieres).
Panneaux : contreplaque 18mm (plateau) + 12mm (etagere).
Facade : Lycra noir + LED WS2812B.

Pliage ACCORDEON (vue du dessus) :

  DEPLOYE (open_pct=100):
      AILE G ──charniere── CENTRE ──charniere── AILE D
      ←350mm→              ←700mm→              ←350mm→

  MI-PLIE (open_pct=50):
               AILE G
              ╱
      CENTRE ╱
              ╲
               AILE D

  PLIE (open_pct=0):
      ┌──────────────┐
      │ AILE G (face)│
      │ CENTRE       │  → ~100mm d'epaisseur totale
      │ AILE D (face)│
      └──────────────┘

Les ailes pivotent autour de l'axe vertical (Z) a la jonction
avec le centre, comme les pages d'un livre qui se ferment.
"""
import math
from solid2 import *
from ..base import ParametricModel
from ..logo import logo_3d
from ._constants import (
    LED_STRIP_W, LED_STRIP_H, LED_CHANNEL_W,
    M5_HOLE, M5_HEAD, M5_HEAD_DEPTH,
    FIT_CLEARANCE,
    HINGE_PIN_D, HINGE_BARREL_OD,
    BALL_LOCK_PIN_D, BALL_LOCK_DEPTH,
    ACCORDION_TUBE, ACCORDION_PANEL_T, ACCORDION_INSERT_CLEARANCE,
    TOP_PANEL_THICKNESS,
)

TUBE = ACCORDION_TUBE


class AccordionBooth(ParametricModel):

    def __init__(self, **params):
        super().__init__("accordion_booth", **params)

    def default_params(self):
        return {
            'width': 1400.0,
            'depth': 500.0,
            'height': 1000.0,
            'wing_width': 350.0,
            'tube_size': 25.0,
            'build_step': 7,
            'open_pct': 100.0,
            'show_facade': True,
            'show_leds': True,
            'show_shelf': True,
            'show_top': True,
            'logo_quality': 'draft',
            'export_part': 'all',
        }

    def param_schema(self):
        return {
            'width': {'type': 'float', 'min': 1200, 'max': 1800, 'unit': 'mm',
                      'description': 'Largeur totale deployee'},
            'depth': {'type': 'float', 'min': 400, 'max': 700, 'unit': 'mm',
                      'description': 'Profondeur du booth'},
            'height': {'type': 'float', 'min': 900, 'max': 1100, 'unit': 'mm',
                       'description': 'Hauteur de travail'},
            'wing_width': {'type': 'float', 'min': 250, 'max': 500, 'unit': 'mm',
                           'description': 'Largeur de chaque aile laterale'},
            'tube_size': {'type': 'float', 'min': 20, 'max': 30, 'unit': 'mm',
                          'description': 'Section tube alu carre'},
            'build_step': {'type': 'int', 'min': 1, 'max': 7,
                           'description': 'Etape montage (1=plie, 7=complet)'},
            'open_pct': {'type': 'float', 'min': 0, 'max': 100, 'unit': '%',
                         'description': 'Deploiement accordeon (0=plie, 100=deploye)'},
            'show_facade': {'type': 'bool', 'description': 'Afficher les panneaux facade'},
            'show_leds': {'type': 'bool', 'description': 'Afficher les zones LED'},
            'show_shelf': {'type': 'bool', 'description': 'Afficher l\'etagere'},
            'show_top': {'type': 'bool', 'description': 'Afficher le plateau'},
            'logo_quality': {
                'type': 'string', 'options': ['draft', 'normal', 'fine'],
                'description': 'Qualite du logo',
            },
            'export_part': {
                'type': 'string',
                'options': ['all', 'frame', 'center', 'left_wing', 'right_wing',
                            'facade', 'top', 'shelf', 'facade_body', 'facade_logo'],
                'description': 'Piece a exporter',
            },
        }

    # =================================================================
    # Tube alu carre
    # =================================================================
    def _tube(self, length, axis='x'):
        t = self.params['tube_size']
        wall = 2.0
        if axis == 'x':
            outer = cube([length, t, t])
            inner = translate([0, wall, wall])(cube([length, t - 2 * wall, t - 2 * wall]))
        elif axis == 'y':
            outer = cube([t, length, t])
            inner = translate([wall, 0, wall])(cube([t - 2 * wall, length, t - 2 * wall]))
        else:
            outer = cube([t, t, length])
            inner = translate([wall, wall, 0])(cube([t - 2 * wall, t - 2 * wall, length]))
        return outer - inner

    # =================================================================
    # Panneau de facade (surface pleine avec fentes)
    # Donne un aspect "meuble reel" et pas juste des tubes
    # =================================================================
    def _panel(self, w, h, thickness=3.0):
        """Panneau de facade avec fentes ajourees horizontales."""
        panel = cube([w, thickness, h])
        # Fentes decoratives
        slot_h = 3.0
        slot_gap = 15.0
        margin_x = w * 0.04
        start_z = h * 0.15
        end_z = h * 0.7
        z = start_z
        while z < end_z:
            panel -= translate([margin_x, -0.1, z])(
                cube([w - 2 * margin_x, thickness + 0.2, slot_h])
            )
            z += slot_h + slot_gap
        return panel

    # =================================================================
    # Section complete (cadre + panneaux)
    # =================================================================
    def _build_section(self, w, h, d, has_panel=True):
        """Section complete : cadre tubes + panneau facade avant."""
        t = self.params['tube_size']
        section = union()

        # -- 4 montants verticaux --
        for (cx, cy) in [(0, 0), (w - t, 0), (0, d - t), (w - t, d - t)]:
            section += translate([cx, cy, 0])(self._tube(h, axis='z'))

        # -- Traverses basses (Z=0) --
        section += translate([t, 0, 0])(self._tube(w - 2 * t, axis='x'))       # avant
        section += translate([t, d - t, 0])(self._tube(w - 2 * t, axis='x'))   # arriere
        section += translate([0, t, 0])(self._tube(d - 2 * t, axis='y'))        # gauche
        section += translate([w - t, t, 0])(self._tube(d - 2 * t, axis='y'))    # droit

        # -- Traverses hautes (Z=h-t) --
        section += translate([t, 0, h - t])(self._tube(w - 2 * t, axis='x'))
        section += translate([t, d - t, h - t])(self._tube(w - 2 * t, axis='x'))
        section += translate([0, t, h - t])(self._tube(d - 2 * t, axis='y'))
        section += translate([w - t, t, h - t])(self._tube(d - 2 * t, axis='y'))

        # -- Traverse milieu (renfort, Z=h*0.5) --
        section += translate([t, 0, h * 0.5])(self._tube(w - 2 * t, axis='x'))
        section += translate([t, d - t, h * 0.5])(self._tube(w - 2 * t, axis='x'))

        # -- Panneau facade avant --
        if has_panel:
            panel_h = h - 2 * t
            panel = self._panel(w - 2 * t, panel_h)
            section += translate([t, -1, t])(panel)

        return section

    # =================================================================
    # Charnieres verticales (3 cylindres le long de l'axe Z)
    # =================================================================
    def _hinge_column(self, h):
        """Colonne de 3 charnieres le long de l'axe vertical."""
        t = self.params['tube_size']
        col = union()
        barrel_h = t * 2
        positions = [t * 2, h / 2 - barrel_h / 2, h - t * 2 - barrel_h]
        for z in positions:
            col += translate([0, 0, z])(
                cylinder(d=HINGE_BARREL_OD + 4, h=barrel_h, _fn=24)
            )
            # Trou axe
            col -= translate([0, 0, z - 0.1])(
                cylinder(d=HINGE_PIN_D + 0.3, h=barrel_h + 0.2, _fn=24)
            )
        return col

    # =================================================================
    # Pieds
    # =================================================================
    def _foot(self):
        t = self.params['tube_size']
        ins = t - 2 * ACCORDION_INSERT_CLEARANCE
        f = union()
        f += translate([-ins / 2, -ins / 2, 0])(cube([ins, ins, t]))
        f += translate([0, 0, -12])(cylinder(d=45, h=12, _fn=32))
        return f

    # =================================================================
    # Build principal
    # =================================================================
    def build(self):
        p = self.params
        w = p['width']
        d = p['depth']
        h = p['height']
        wing_w = p['wing_width']
        t = p['tube_size']
        step = int(p['build_step'])
        open_pct = p['open_pct']
        mode = p['export_part']
        logo_q = p['logo_quality']

        center_w = w - 2 * wing_w

        # --- Export pieces individuelles ---
        if mode == 'center':
            return self._build_section(center_w, h, d)
        if mode == 'left_wing':
            return self._build_section(wing_w, h, d)
        if mode == 'right_wing':
            return self._build_section(wing_w, h, d)
        if mode == 'top':
            return translate([0, 0, h])(cube([w, d, TOP_PANEL_THICKNESS]))
        if mode == 'shelf':
            margin = t + 5
            return translate([margin, margin, h * 0.4])(
                cube([center_w - 2 * margin, d - 2 * margin, 12])
            )
        if mode == 'facade':
            return self._build_facade_full(w, h, logo_q)
        if mode in ('facade_body', 'facade_logo'):
            return self._build_facade_full(w, h, logo_q, split=mode)
        if mode == 'frame':
            return self._assemble(center_w, wing_w, h, d, t, open_pct, step, frame_only=True)

        # --- Mode 'all' ---
        return self._assemble(center_w, wing_w, h, d, t, open_pct, step, frame_only=False)

    # =================================================================
    # Facade complete (pour export individuel)
    # =================================================================
    def _build_facade_full(self, w, h, logo_q, split=None):
        panel_t = 3.0
        body = self._panel(w, h, panel_t)
        logo_w = min(w * 0.25, 200)
        logo_obj = logo_3d(width=logo_w, height=1.5, quality=logo_q)
        logo_placed = translate([w / 2, panel_t, h * 0.82])(
            rotate([90, 0, 0])(logo_obj)
        )
        if split == 'facade_body':
            return body
        if split == 'facade_logo':
            return logo_placed
        return body + logo_placed

    # =================================================================
    # Assemblage avec pliage accordeon
    # =================================================================
    def _assemble(self, center_w, wing_w, h, d, t, open_pct, step, frame_only=False):
        """
        Assemblage complet du booth avec pliage accordeon.

        Le pliage se fait autour de l'axe VERTICAL (Z).
        Les ailes pivotent comme des portes/pages autour des charnieres.

        open_pct=100 : deploye a plat (ailes a 180 deg du centre)
        open_pct=50  : ailes a 90 deg (en V)
        open_pct=0   : plie a plat (ailes collees contre le centre)
        """
        fold_angle = 180.0 * (open_pct / 100.0)
        show_panels = not frame_only and self.params['show_facade']

        model = union()

        # ============================================================
        # CENTRE (toujours present)
        # ============================================================
        center = self._build_section(center_w, h, d, has_panel=show_panels)

        # Pieds du centre (4 coins)
        for cx in [t / 2, center_w - t / 2]:
            for cy in [t / 2, d - t / 2]:
                center += translate([cx, cy, 0])(self._foot())

        model += center

        # ============================================================
        # CHARNIERES - colonnes verticales aux jonctions
        # ============================================================
        # Charniere gauche (X=0, Y=d/2)
        hinge_left = color([0.6, 0.2, 0.2, 0.9])(
            translate([0, d / 2, 0])(self._hinge_column(h))
        )
        model += hinge_left

        # Charniere droite (X=center_w, Y=d/2)
        hinge_right = color([0.6, 0.2, 0.2, 0.9])(
            translate([center_w, d / 2, 0])(self._hinge_column(h))
        )
        model += hinge_right

        # ============================================================
        # AILE GAUCHE - pivot autour de X=0 (axe Z vertical)
        # ============================================================
        if step >= 2:
            wing_l = self._build_section(wing_w, h, d, has_panel=show_panels)
            # Pieds aile gauche
            wing_l += translate([wing_w / 2, t / 2, 0])(self._foot())
            wing_l += translate([wing_w / 2, d - t / 2, 0])(self._foot())

            # L'aile est construite avec X de 0 a wing_w.
            # Deploye (180°): elle doit se placer de X=-wing_w a X=0
            # Plie (0°): elle se colle contre le centre (memes X que le centre)
            #
            # Pivot: on place l'aile avec son bord droit (X=wing_w) au point
            # de pivot X=0, puis on la tourne de fold_angle autour de Z.
            # A 180°, l'aile pointe vers -X. A 0°, elle pointe vers +X (sur le centre).

            wing_l_positioned = translate([0, 0, 0])(
                rotate([0, 0, fold_angle])(  # rotation autour de Z a l'origine
                    translate([-wing_w, 0, 0])(wing_l)  # bord droit a X=0
                )
            )
            model += wing_l_positioned

        # ============================================================
        # AILE DROITE - pivot autour de X=center_w (axe Z vertical)
        # ============================================================
        if step >= 3:
            wing_r = self._build_section(wing_w, h, d, has_panel=show_panels)
            # Pieds aile droite
            wing_r += translate([wing_w / 2, t / 2, 0])(self._foot())
            wing_r += translate([wing_w / 2, d - t / 2, 0])(self._foot())

            # Pivot a X=center_w. Deploye (180°): de center_w a center_w+wing_w.
            # On place le bord gauche (X=0) au pivot, tourne de -fold_angle.

            wing_r_positioned = translate([center_w, 0, 0])(
                rotate([0, 0, -fold_angle])(  # sens oppose a l'aile gauche
                    wing_r  # bord gauche (X=0) au pivot
                )
            )
            model += wing_r_positioned

        # ============================================================
        # VERROUS (step 4+, seulement deploye)
        # ============================================================
        if step >= 4 and open_pct > 95:
            for pivot_x in [0, center_w]:
                for cy in [t * 2, d - t * 2]:
                    for cz in [t * 3, h - t * 3]:
                        lock = translate([pivot_x, cy, cz])(
                            color([0.9, 0.15, 0.15, 0.85])(
                                cube([8, 8, BALL_LOCK_DEPTH], center=True)
                            )
                        )
                        model += lock

        # ============================================================
        # ETAGERE (step 5+, deploye)
        # ============================================================
        if step >= 5 and not frame_only and self.params['show_shelf'] and open_pct > 95:
            total_w = center_w + 2 * wing_w
            margin = t + 5
            shelf = color([0.55, 0.35, 0.18, 0.75])(
                translate([-wing_w + margin, margin, h * 0.4])(
                    cube([total_w - 2 * margin, d - 2 * margin, 12])
                )
            )
            model += shelf

        # ============================================================
        # PLATEAU (step 6+, deploye)
        # ============================================================
        if step >= 6 and not frame_only and self.params['show_top'] and open_pct > 95:
            total_w = center_w + 2 * wing_w
            top = color([0.55, 0.35, 0.18, 0.85])(
                translate([-wing_w, 0, h])(
                    cube([total_w, d, TOP_PANEL_THICKNESS])
                )
            )
            model += top

        # ============================================================
        # LOGO (step 7, deploye)
        # ============================================================
        if step >= 7 and not frame_only and open_pct > 95:
            logo_q = self.params['logo_quality']
            total_w = center_w + 2 * wing_w
            logo_w = min(total_w * 0.2, 180)
            logo_obj = logo_3d(width=logo_w, height=1.5, quality=logo_q)
            model += translate([center_w / 2, -4, h * 0.8])(
                rotate([90, 0, 0])(logo_obj)
            )

        # ============================================================
        # LED (step 7, deploye)
        # ============================================================
        if step >= 7 and not frame_only and self.params['show_leds'] and open_pct > 95:
            total_w = center_w + 2 * wing_w
            led_t = LED_STRIP_H
            # LED haut facade
            model += color([0.9, 0.7, 0.1, 0.5])(
                translate([-wing_w + t, -led_t - 2, h - t * 2])(
                    cube([total_w - 2 * t, led_t, LED_CHANNEL_W])
                )
            )
            # LED bas facade
            model += color([0.9, 0.7, 0.1, 0.5])(
                translate([-wing_w + t, -led_t - 2, t * 2])(
                    cube([total_w - 2 * t, led_t, LED_CHANNEL_W])
                )
            )
            # Underglow
            model += color([0.9, 0.7, 0.1, 0.3])(
                translate([-wing_w + t * 2, t, -led_t])(
                    cube([total_w - 4 * t, d - 2 * t, led_t])
                )
            )

        return model
