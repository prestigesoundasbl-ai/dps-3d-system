"""
APEX DJ Booth — Concept Original Prestige Sound
=================================================
Design signature : facade en pointe ("Apex") avec 7 zones LED.
Silhouette distinctive vue de face :

              /\\
             /  \\         <- Sommet APEX (logo retro-eclaire)
            / PS \\
      -----/      \\-----  <- Crown LED
      | ================|  <- Facade haute (logo)
      | — — — — — — — — |  <- Fentes ajourees (LED visible)
      | — — — — — — — — |
      | — — — — — — — — |
      |__________________|  <- Base LED
         ▓▓▓▓▓▓▓▓▓▓▓▓      <- Underglow

Cadre en U (front + 2 cotes), pliage par charnieres verticales.
Les cotes se rabattent contre la facade -> tout a plat dans la housse.

7 zones LED (WS2812B + ESP32/WLED) :
  1. Crown (arete du sommet Apex)
  2. Facade haut (sous traverse haute)
  3. Facade bas (au-dessus traverse basse)
  4. Accent cote gauche (barre verticale)
  5. Accent cote droit (barre verticale)
  6. Underglow (sous la base)
  7. Logo backlight (derriere le logo)

Pliage :
  - open_pct=100 : deploye en U, pret a jouer
  - open_pct=0   : cotes rabattus sur la facade, tout a plat (~10cm)
  - Le plateau et l'etagere se posent par-dessus (amovibles)
"""
import math
import os
from solid2 import *
from ..base import ParametricModel
from ..logo import logo_3d, logo_engrave, logo_relief
from ._constants import (
    LED_STRIP_W, LED_STRIP_H, TOP_PANEL_THICKNESS,
)

# Tube carre aluminium pour le cadre
TUBE = 25.0


class ApexBooth(ParametricModel):

    def __init__(self, **params):
        super().__init__("apex_booth", **params)

    def default_params(self):
        return {
            'width': 1200.0,
            'height': 1050.0,
            'depth': 600.0,
            'apex_rise': 150.0,
            'build_step': 6.0,
            'open_pct': 100.0,
            'show_facade': True,
            'show_leds': True,
            'show_top': True,
            'show_shelf': True,
            'export_part': 'all',
            'logo_quality': 'normal',
        }

    def param_schema(self):
        return {
            'width': {'type': 'float', 'min': 1000, 'max': 1800, 'unit': 'mm',
                      'description': 'Largeur facade'},
            'height': {'type': 'float', 'min': 900, 'max': 1200, 'unit': 'mm',
                       'description': 'Hauteur du cadre'},
            'depth': {'type': 'float', 'min': 400, 'max': 800, 'unit': 'mm',
                      'description': 'Profondeur (cotes)'},
            'apex_rise': {'type': 'float', 'min': 50, 'max': 300, 'unit': 'mm',
                          'description': 'Hauteur du sommet Apex'},
            'build_step': {'type': 'float', 'min': 1, 'max': 6, 'unit': '',
                           'description': 'Etape montage (1=plie 2=deploye 3=facade 4=LED 5=etagere 6=plateau)'},
            'open_pct': {'type': 'float', 'min': 0, 'max': 100, 'unit': '%',
                         'description': 'Deploiement manuel (ignore si etape < 3)'},
            'show_facade': {'type': 'bool', 'description': 'Panneaux facade'},
            'show_leds': {'type': 'bool', 'description': 'Zones LED'},
            'show_top': {'type': 'bool', 'description': 'Plateau de travail'},
            'show_shelf': {'type': 'bool', 'description': 'Etagere intermediaire'},
            'export_part': {'type': 'select',
                            'options': ['all', 'frame', 'facade', 'top', 'shelf',
                                        'facade_body', 'facade_logo'],
                            'description': 'Partie a exporter (facade_body/facade_logo pour multi-couleur)'},
            'logo_quality': {'type': 'select',
                             'options': ['draft', 'normal', 'fine'],
                             'description': 'Qualite logo (draft=texte, normal=geometrique, fine=SVG)'},
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _tube_v(self, length):
        """Tube carre vertical (le long de Z)."""
        return cube([TUBE, TUBE, length])

    def _tube_h(self, length):
        """Tube carre horizontal (le long de X)."""
        return cube([length, TUBE, TUBE])

    def _tube_y(self, length):
        """Tube carre horizontal (le long de Y)."""
        return cube([TUBE, length, TUBE])

    def _foot(self):
        """Pied reglable avec pad anti-vibration."""
        pad = cylinder(r=18, h=5, _fn=24)
        stem = translate([0, 0, 5])(cylinder(r=7, h=12, _fn=12))
        return translate([0, 0, -5])(pad + stem)

    def _hinge_barrel(self, height):
        """Charniere cylindrique (gond visible)."""
        return cylinder(r=7, h=height, _fn=20)

    def _rotate_around_z(self, obj, angle_deg, px, py):
        """Rotation autour d'un axe vertical passant par (px, py)."""
        return translate([px, py, 0])(
            rotate([0, 0, angle_deg])(
                translate([-px, -py, 0])(obj)
            )
        )

    # ------------------------------------------------------------------
    # Panneau avant (avec sommet Apex)
    # ------------------------------------------------------------------

    def _build_front(self, w, h, apex_rise):
        """Cadre avant : 2 montants + traverses + sommet Apex en pointe."""
        f = union()

        # --- Montants verticaux ---
        f += self._tube_v(h)
        f += translate([w - TUBE, 0, 0])(self._tube_v(h))

        # --- Traverses horizontales ---
        rail = w - 2 * TUBE
        beam = self._tube_h(rail)
        f += translate([TUBE, 0, 80])(beam)               # basse
        f += translate([TUBE, 0, h * 0.42])(beam)          # milieu
        f += translate([TUBE, 0, h - TUBE])(beam)           # haute

        # --- APEX PEAK : 2 poutres inclinées convergent au centre ---
        peak_z = h + apex_rise
        half_w = w / 2.0

        # Poutre gauche (de la traverse haute vers le sommet)
        f += hull()(
            translate([TUBE, 0, h - TUBE])(cube([TUBE, TUBE, TUBE])),
            translate([half_w - TUBE / 2, 0, peak_z - TUBE])(cube([TUBE, TUBE, TUBE]))
        )
        # Poutre droite
        f += hull()(
            translate([half_w - TUBE / 2, 0, peak_z - TUBE])(cube([TUBE, TUBE, TUBE])),
            translate([w - 2 * TUBE, 0, h - TUBE])(cube([TUBE, TUBE, TUBE]))
        )

        # Montant vertical au sommet (pilier central de l'apex)
        f += translate([half_w - TUBE / 2, 0, h - TUBE])(
            cube([TUBE, TUBE, apex_rise + TUBE])
        )

        # --- Pieds ---
        f += translate([TUBE / 2, TUBE / 2, 0])(self._foot())
        f += translate([w - TUBE / 2, TUBE / 2, 0])(self._foot())

        return f

    # ------------------------------------------------------------------
    # Panneau lateral (construit le long de Y)
    # ------------------------------------------------------------------

    def _build_side(self, d, h):
        """Panneau lateral : 2 montants + traverses, oriente le long de Y."""
        s = union()

        # 2 montants (a Y=0 et Y=D-TUBE)
        s += cube([TUBE, TUBE, h])
        s += translate([0, d - TUBE, 0])(cube([TUBE, TUBE, h]))

        # Traverses le long de Y
        rail = d - 2 * TUBE
        beam = self._tube_y(rail)
        s += translate([0, TUBE, 80])(beam)                # basse
        s += translate([0, TUBE, h * 0.42])(beam)           # milieu
        s += translate([0, TUBE, h - TUBE])(beam)            # haute

        # Pieds
        s += translate([TUBE / 2, TUBE / 2, 0])(self._foot())
        s += translate([TUBE / 2, d - TUBE / 2, 0])(self._foot())

        return s

    # ------------------------------------------------------------------
    # Facade decorative
    # ------------------------------------------------------------------

    def _build_facade(self, w, h, apex_rise, logo_quality='draft',
                      split_logo=False):
        """
        Facade avec fentes ajourees, logo Prestige Sound, et panneau apex.

        Si split_logo=True, retourne un dict:
            {'body': facade_sans_logo, 'logo': logo_parts_seuls}
        pour l'export multi-couleur (body=noir, logo=or).
        """
        facade_body = union()
        facade_logo = union()

        panel_t = 4.0
        facade_z = 150                     # debut facade (au-dessus des pieds)
        facade_top = h - TUBE              # haut du panneau droit
        facade_h = facade_top - facade_z
        panel_w = w - 2 * TUBE - 20       # largeur utile

        # --- Panneau principal ---
        panel = cube([panel_w, panel_t, facade_h])

        # Fentes ajourees (zone basse : 15% a 48% de la hauteur)
        slot_start = facade_h * 0.15
        slot_end = facade_h * 0.48
        slot_h = 5
        slot_gap = 20
        slot_w = panel_w - 80
        n_slots = int((slot_end - slot_start) / slot_gap)
        for i in range(n_slots):
            z = slot_start + i * slot_gap
            panel -= translate([40, -0.5, z])(
                cube([slot_w, panel_t + 1, slot_h])
            )

        # ==========================================================
        # ZONE LOGO PRESTIGE SOUND (zone 52-92% hauteur)
        # Double technique : logo en relief + gravure retroeclairee
        # ==========================================================

        # --- Dimensions logo ---
        logo_w = min(500, panel_w * 0.50)       # logo large et visible
        logo_h = logo_w                          # logo est 1:1
        logo_zone_z = facade_h * 0.52            # debut de la zone logo
        logo_zone_h = facade_h * 0.40            # hauteur zone

        # Position centree
        logo_cx = panel_w / 2.0
        logo_cz = logo_zone_z + logo_zone_h / 2.0

        # --- 1. CADRE DECORATIF autour de la zone logo ---
        frame_margin = 15
        frame_w = logo_w + 2 * frame_margin
        frame_h_total = logo_zone_h + 2 * frame_margin
        frame_thick = 3.0  # saillie du cadre

        # Cadre exterieur (bandeau en relief)
        frame_band = 6
        outer_frame = cube([frame_w, frame_thick, frame_h_total])
        inner_cut = cube([frame_w - 2 * frame_band, frame_thick + 1, frame_h_total - 2 * frame_band])
        cadre = outer_frame - translate([frame_band, -0.5, frame_band])(inner_cut)
        panel += translate([
            logo_cx - frame_w / 2,
            -(frame_thick),
            logo_zone_z - frame_margin
        ])(cadre)

        # Filet interieur (fine ligne en relief, 4mm a l'interieur du cadre)
        inner_margin = frame_band + 4
        filet_w = frame_w - 2 * inner_margin
        filet_h = frame_h_total - 2 * inner_margin
        filet_band = 1.5
        filet_outer = cube([filet_w, 1.5, filet_h])
        filet_inner = cube([filet_w - 2 * filet_band, 2, filet_h - 2 * filet_band])
        filet = filet_outer - translate([filet_band, -0.25, filet_band])(filet_inner)
        panel += translate([
            logo_cx - filet_w / 2,
            -(1.5),
            logo_zone_z - frame_margin + inner_margin
        ])(filet)

        # --- 2. FOND TRANSLUCIDE (zone fine derriere le logo pour LED backlight) ---
        backlight_w = logo_w + 10
        backlight_h = logo_zone_h + 10
        translucent_thickness = 0.8
        cavity_depth = panel_t - translucent_thickness
        backlight_cavity = cube([backlight_w, cavity_depth + 0.1, backlight_h])
        panel -= translate([
            logo_cx - backlight_w / 2,
            translucent_thickness,
            logo_cz - backlight_h / 2
        ])(backlight_cavity)

        # --- 3. LOGO EN RELIEF (3mm saillie) ---
        relief_depth = 3.0
        logo_solid = logo_3d(width=logo_w * 0.85, height=relief_depth, quality=logo_quality)
        logo_on_facade = rotate([90, 0, 0])(logo_solid)
        logo_relief_positioned = translate([
            TUBE + 10 + logo_cx, -panel_t - relief_depth, facade_z + logo_cz
        ])(logo_on_facade)

        if not split_logo:
            panel += translate([logo_cx, -(relief_depth), logo_cz])(logo_on_facade)
        else:
            facade_logo += logo_relief_positioned

        # --- 4. LOGO GRAVE EN CREUX (decoupe dans le fond translucide) ---
        engrave_depth = translucent_thickness + 0.1
        logo_cutout = logo_3d(width=logo_w * 0.82, height=engrave_depth, quality=logo_quality)
        logo_cut_facade = rotate([90, 0, 0])(logo_cutout)
        panel -= translate([logo_cx, translucent_thickness + 0.05, logo_cz])(
            rotate([180, 0, 0])(logo_cut_facade)
        )

        # --- 5. LIGNES DECORATIVES ---
        line_w = panel_w * 0.7
        line_sup = cube([line_w, 2, 2])
        panel += translate([
            (panel_w - line_w) / 2,
            -2,
            logo_zone_z + logo_zone_h + frame_margin + 8
        ])(line_sup)
        panel += translate([
            (panel_w - line_w) / 2,
            -2,
            logo_zone_z - frame_margin - 10
        ])(line_sup)

        # --- 6. FENTES DECORATIVES au-dessus du logo ---
        top_slot_start = logo_zone_z + logo_zone_h + frame_margin + 20
        top_slot_end = facade_h - 15
        if top_slot_end > top_slot_start:
            n_top_slots = min(4, int((top_slot_end - top_slot_start) / slot_gap))
            for i in range(n_top_slots):
                z = top_slot_start + i * slot_gap
                panel -= translate([60, -0.5, z])(
                    cube([panel_w - 120, panel_t + 1, slot_h])
                )

        facade_body += translate([TUBE + 10, -panel_t, facade_z])(panel)

        # --- Panneau triangulaire APEX ---
        tri_t = 3.0
        tri = hull()(
            translate([TUBE + 10, 0, 0])(cube([panel_w, tri_t, 1])),
            translate([w / 2 - 25, 0, apex_rise - TUBE])(cube([50, tri_t, 1]))
        )

        # --- Mini logo dans le triangle apex (grave) ---
        apex_logo_w = min(120, panel_w * 0.12)
        apex_logo_depth = tri_t + 0.1
        apex_logo_3d = logo_3d(width=apex_logo_w, height=apex_logo_depth, quality=logo_quality)
        apex_logo_oriented = rotate([90, 0, 0])(apex_logo_3d)
        apex_cz = (apex_rise - TUBE) * 0.45
        tri -= translate([w / 2, 0.05, apex_cz])(apex_logo_oriented)

        facade_body += translate([0, -tri_t, facade_top])(tri)

        if split_logo:
            return {'body': facade_body, 'logo': facade_logo}
        return facade_body

    # ------------------------------------------------------------------
    # Panneaux lateraux decoratifs
    # ------------------------------------------------------------------

    def _build_side_panels(self, d, h):
        """Panneaux decoratifs sur les cotes (fentes + accent)."""
        panels = union()
        panel_t = 3.0
        panel_z = 200
        panel_h = h - TUBE - panel_z
        panel_d = d - 2 * TUBE - 20

        side_panel = cube([panel_t, panel_d, panel_h])

        # Fentes horizontales
        slot_h = 4
        slot_gap = 25
        slot_d = panel_d - 40
        n_slots = min(8, int(panel_h * 0.4 / slot_gap))
        for i in range(n_slots):
            z = panel_h * 0.2 + i * slot_gap
            side_panel -= translate([-0.5, 20, z])(
                cube([panel_t + 1, slot_d, slot_h])
            )

        # Cote gauche (X=0, face vers -X)
        panels += translate([-panel_t, TUBE + 10, panel_z])(side_panel)
        # Cote droit (X=W, face vers +X)
        # -> sera positionne dans build() selon open_pct

        return side_panel, panels

    # ------------------------------------------------------------------
    # 7 zones LED
    # ------------------------------------------------------------------

    def _build_leds(self, w, h, d, apex_rise):
        """7 zones LED distinctes."""
        leds = union()
        sw = LED_STRIP_W
        sh = LED_STRIP_H

        # --- Zone 1 : CROWN (le long de l'apex, 60% de la largeur) ---
        crown_w = w * 0.5
        leds += translate([(w - crown_w) / 2, -sw - 3, h + apex_rise * 0.35])(
            cube([crown_w, sw, sh])
        )

        # --- Zone 2 : FACADE HAUT (sous la traverse haute) ---
        bar_w = w - 4 * TUBE
        leds += translate([2 * TUBE, -sw - 3, h - TUBE - sh - 5])(
            cube([bar_w, sw, sh])
        )

        # --- Zone 3 : FACADE BAS (au-dessus de la traverse basse facade) ---
        leds += translate([2 * TUBE, -sw - 3, 160])(
            cube([bar_w, sw, sh])
        )

        # --- Zone 4 : ACCENT COTE GAUCHE (barre verticale) ---
        side_h = h * 0.55
        leds += translate([TUBE + 3, TUBE + 3, 220])(
            cube([sw, sh, side_h])
        )

        # --- Zone 5 : ACCENT COTE DROIT (barre verticale) ---
        leds += translate([w - TUBE - sw - 3, TUBE + 3, 220])(
            cube([sw, sh, side_h])
        )

        # --- Zone 6 : UNDERGLOW (bande sous la base, perimetrique) ---
        ug_w = w - 4 * TUBE
        leds += translate([2 * TUBE, TUBE / 2 - sw / 2, 8])(
            cube([ug_w, sw, sh])
        )
        # Cotes underglow
        ug_d = d - 2 * TUBE
        leds += translate([TUBE / 2 - sw / 2, TUBE, 8])(
            cube([sw, ug_d, sh])
        )
        leds += translate([w - TUBE / 2 - sw / 2, TUBE, 8])(
            cube([sw, ug_d, sh])
        )

        # --- Zone 7 : LOGO BACKLIGHT (derriere le logo) ---
        logo_w = min(350, w * 0.35)
        logo_z = 150 + (h - TUBE - 150) * 0.70 + 15
        leds += translate([(w - logo_w) / 2, 3, logo_z])(
            cube([logo_w, sw, sh])
        )

        return leds

    # ------------------------------------------------------------------
    # Plateau de travail
    # ------------------------------------------------------------------

    def _build_top(self, w, d, h, apex_rise):
        """Plateau contreplaque avec feutre + LED sous le bord avant."""
        top = union()

        ovh = 15  # debord
        top_w = w + 2 * ovh
        top_d = d + ovh

        # Panneau
        panel = cube([top_w, top_d, TOP_PANEL_THICKNESS])
        top += translate([-ovh, -ovh, h])(panel)

        # Feutre anti-derapant
        felt = cube([top_w - 30, top_d - 30, 1.5])
        top += translate([-ovh + 15, -ovh + 15, h + TOP_PANEL_THICKNESS])(felt)

        # Goupilles de positionnement (sous le plateau)
        pin = cylinder(r=4, h=12, _fn=12)
        for px in [TUBE, w / 2, w - TUBE]:
            for py in [TUBE, d - TUBE]:
                top += translate([px, py, h - 12])(pin)

        # LED sous le bord avant du plateau (eclairage vers le bas)
        led_w = w - 4 * TUBE
        top += translate([2 * TUBE, -ovh + 2, h - LED_STRIP_H - 2])(
            cube([led_w, LED_STRIP_W, LED_STRIP_H])
        )

        return top

    # ------------------------------------------------------------------
    # Etagere
    # ------------------------------------------------------------------

    def _build_shelf(self, w, d, h):
        """Etagere amovible (rangement cables/accessoires)."""
        shelf_z = h * 0.38
        shelf_t = 12
        shelf_w = w - 4 * TUBE
        shelf_d = d - 2 * TUBE

        shelf = cube([shelf_w, shelf_d, shelf_t])
        shelf = translate([2 * TUBE, TUBE, shelf_z])(shelf)

        # Tasseaux de fixation (boulons lateraux)
        bolt = rotate([0, 90, 0])(cylinder(r=3.5, h=12, _fn=12))
        for side_x in [2 * TUBE - 12, w - 2 * TUBE]:
            for sy in [TUBE + 40, d - TUBE - 40]:
                shelf += translate([side_x, sy, shelf_z + shelf_t / 2])(bolt)

        return shelf

    # ------------------------------------------------------------------
    # Charnieres visibles
    # ------------------------------------------------------------------

    def _build_hinges(self, w, h):
        """Charnieres aux 2 coins avant (gauche et droite)."""
        hinges = union()
        barrel_h = 55
        positions_z = [100, h * 0.45, h - 80]

        for hz in positions_z:
            # Charniere gauche
            hinges += translate([TUBE / 2, TUBE / 2, hz])(
                self._hinge_barrel(barrel_h)
            )
            # Charniere droite
            hinges += translate([w - TUBE / 2, TUBE / 2, hz])(
                self._hinge_barrel(barrel_h)
            )

        return hinges

    # ------------------------------------------------------------------
    # Assemblage principal
    # ------------------------------------------------------------------

    def build(self):
        p = self.params
        w = p['width']
        h = p['height']
        d = p['depth']
        apex_rise = p['apex_rise']
        mode = p['export_part']

        # ============================================================
        # ETAPES DE MONTAGE
        # 1 = Cadre plie a plat (dans la housse)
        # 2 = Cadre deploye (structure seule)
        # 3 = + Panneaux facade + triangle Apex
        # 4 = + LED strips (7 zones)
        # 5 = + Etagere intermediaire
        # 6 = + Plateau de travail (montage complet)
        # ============================================================
        step = int(p['build_step'])
        step = max(1, min(6, step))

        # Le pliage est automatique selon l'etape
        if step == 1:
            open_pct = 0.0
        elif step >= 2:
            open_pct = p['open_pct'] if step == 2 else 100.0
        else:
            open_pct = 100.0

        fold_angle = 90.0 * (1.0 - open_pct / 100.0)
        is_deployed = open_pct >= 95

        # ============================
        # ETAPE 1-2 : CADRE (toujours present)
        # ============================
        front = self._build_front(w, h, apex_rise)

        left_side = self._build_side(d, h)
        if fold_angle > 0.1:
            left_side = self._rotate_around_z(left_side, -fold_angle, 0, 0)

        right_side = translate([w - TUBE, 0, 0])(self._build_side(d, h))
        if fold_angle > 0.1:
            right_side = self._rotate_around_z(right_side, fold_angle, w - TUBE, 0)

        frame = front + left_side + right_side
        frame += self._build_hinges(w, h)

        if mode == 'frame':
            return frame

        model = frame

        # ============================
        # ETAPE 3 : + FACADE
        # ============================
        if step >= 3 and is_deployed and p['show_facade']:
            logo_q = p.get('logo_quality', 'draft')
            if mode in ('facade_body', 'facade_logo'):
                parts = self._build_facade(w, h, apex_rise,
                                           logo_quality=logo_q, split_logo=True)
                if mode == 'facade_body':
                    return parts['body']
                return parts['logo']
            facade = self._build_facade(w, h, apex_rise, logo_quality=logo_q)
            if mode == 'facade':
                return facade
            model += facade

        # ============================
        # ETAPE 4 : + LED (7 zones)
        # ============================
        if step >= 4 and is_deployed and p['show_leds']:
            leds = self._build_leds(w, h, d, apex_rise)
            model += leds

        # ============================
        # ETAPE 5 : + ETAGERE
        # ============================
        if step >= 5 and is_deployed and p['show_shelf']:
            shelf = self._build_shelf(w, d, h)
            if mode == 'shelf':
                return shelf
            model += shelf

        # ============================
        # ETAPE 6 : + PLATEAU (montage complet)
        # ============================
        if step >= 6 and is_deployed and p['show_top']:
            top = self._build_top(w, d, h, apex_rise)
            if mode == 'top':
                return top
            model += top

        return model


if __name__ == "__main__":
    import sys
    booth = ApexBooth(open_pct=100)
    print("Generation APEX Booth (deploye)...")
    print(f"Params: {booth.params}")
    scad_path = booth.save_scad()
    print(f"SCAD: {scad_path}")
    try:
        stl_path = booth.render_stl()
        print(f"STL: {stl_path}")
        print("OK")
    except Exception as e:
        print(f"Erreur STL: {e}", file=sys.stderr)
