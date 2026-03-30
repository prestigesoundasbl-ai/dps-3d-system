"""
DPS DJ Table Z-Style - Flycase + Table DJ Depliable
=====================================================
Inspire du Thon DJ Table Z-Style (Thomann #462836).

CONCEPT :
  Le materiel (Mixon 8 Pro, WolfMix, t.bone HF) est installe dans
  le bac du case et y RESTE. On n'enleve rien.

  TRANSPORT : Case ferme, couvercle par dessus, butterfly locks.
  DEPLOIEMENT :
    1. Ouvrir les butterfly locks, enlever le couvercle
    2. Poser le couvercle au sol (retourne) = base de stabilite
    3. Sortir les 2 Z-panels (ranges a plat sous le matos)
    4. Fixer les Z-panels sur le couvercle (butterfly locks)
    5. Poser le bac (avec le matos) sur les Z-panels
    6. Visser les star knobs -> pret a mixer !

  Le matos est face vers le haut, a hauteur de travail (~1020mm).
  Le couvercle retourne en bas a les memes dimensions que le bac
  donc les Z-panels s'emboitent parfaitement.

FABRICATION HYBRIDE :
  - Structure (case + Z-panels) : contreplaque bouleau, decoupe laser
  - Facade, connecteurs, accessoires : impression 3D (PLA, CityFab BigBuilder)
  - Quincaillerie : achat (butterfly locks, poignees, roulettes)
  - Mousse : decoupe manuelle avec gabarits imprimes

Materiel (dans le bac, face vers le haut) :
  - Reloop Mixon 8 Pro : 657 x 391 x 68 mm (centre)
  - WolfMix W1         : 195 x 220 x 62 mm (droite du Mixon)
  - t.bone Free Solo HT: 212 x 160 x 44 mm (droite, sous le WolfMix)
"""
import math
from solid2 import *
from ..base import ParametricModel
from ..utils import rounded_box, brand_text
from ..logo import logo_3d
from ..brand import DEFAULT_TEXT_FONT

# ========================================================================
# Dimensions des appareils (mm)
# ========================================================================
MIXON8_W = 657.0
MIXON8_D = 391.0
MIXON8_H = 68.0

WOLFMIX_W = 195.0
WOLFMIX_D = 220.0
WOLFMIX_H = 62.0

TBONE_W = 212.0
TBONE_D = 160.0
TBONE_H = 44.0


class ThonZStyle(ParametricModel):

    def __init__(self, **params):
        super().__init__("thon_z_style", **params)

    def default_params(self):
        return {
            'case_ext_w': 960.0,
            'case_ext_d': 440.0,
            'case_ext_h': 180.0,
            'working_height': 1020.0,     # Ergonomique pour 2m de taille

            'panel_t': 7.0,              # Multiplex
            'alu_profile': 15.0,         # Corniere
            'foam_t': 15.0,              # Mousse sous le matos
            'padding': 5.0,              # Jeu autour du matos
            'divider_t': 4.0,            # Cloison Mixon / cote

            'base_ratio': 0.6,           # 60% pour le bac, 40% couvercle

            'z_panel_t': 12.0,           # Epaisseur Z-panel
            'z_foot_len': 180.0,         # Longueur pied au sol

            # Imprimante CityFab BigBuilder
            'printer_w': 215.0,
            'printer_d': 205.0,
            'printer_h': 600.0,

            # Tiling facade
            'front_tile_cols': 5,
            'front_tile_rows': 2,
            'tile_tongue_w': 1.5,
            'tile_groove_clr': 0.2,
            'tile_rib_depth': 12.0,

            'use_logo': True,
            'export_part': 'deployed',
        }

    def param_schema(self):
        return {
            'case_ext_w': {'type': 'float', 'min': 900, 'max': 1100, 'unit': 'mm'},
            'case_ext_d': {'type': 'float', 'min': 400, 'max': 600, 'unit': 'mm'},
            'case_ext_h': {'type': 'float', 'min': 150, 'max': 250, 'unit': 'mm'},
            'working_height': {'type': 'float', 'min': 800, 'max': 1200, 'unit': 'mm'},
            'export_part': {
                'type': 'string',
                'options': [
                    # --- Vues (non-imprimables) ---
                    'deployed', 'transport', 'full_assembly',
                    # --- Pieces entieres (reference, non-imprimables) ---
                    'case_bottom', 'case_lid', 'z_panel', 'front_panel', 'foam_layout',
                    # --- IMPRIMABLE : Tuiles facade (10) ---
                    'front_tile_A1', 'front_tile_A2', 'front_tile_A3',
                    'front_tile_A4', 'front_tile_A5',
                    'front_tile_B1', 'front_tile_B2', 'front_tile_B3',
                    'front_tile_B4', 'front_tile_B5',
                    # --- IMPRIMABLE : Gabarits mousse (3) ---
                    'foam_template_mixon_l', 'foam_template_mixon_r',
                    'foam_template_side',
                    # --- IMPRIMABLE : Cloison (2) ---
                    'divider_front', 'divider_rear',
                    # --- IMPRIMABLE : Connecteurs Z-panel (4) ---
                    'z_bracket_top', 'z_bracket_bottom',
                    'z_gusset', 'z_foot_pad',
                    # --- IMPRIMABLE : Accessoires (5) ---
                    'cable_grommet', 'star_knob', 'logo_plate',
                    'corner_protector', 'handle_recess',
                    # --- LASER : Profils DXF (3) ---
                    'case_bottom_dxf', 'case_lid_dxf', 'z_panel_dxf',
                ],
            },
        }

    # Couleurs
    _C = {
        'case': [0.08, 0.08, 0.08],
        'alu': [0.78, 0.78, 0.80],
        'foam': [0.12, 0.12, 0.15],
        'gold': [0.79, 0.66, 0.38],
        'pla': [0.15, 0.15, 0.18],
    }

    # ------------------------------------------------------------------
    def _d(self):
        p = self.params
        ew, ed, eh = p['case_ext_w'], p['case_ext_d'], p['case_ext_h']
        pt = p['panel_t']
        al = p['alu_profile']
        bh = eh * p['base_ratio']
        lh = eh - bh
        iw = ew - 2 * pt
        id_ = ed - 2 * pt
        return dict(ew=ew, ed=ed, eh=eh, pt=pt, al=al,
                    bh=bh, lh=lh, iw=iw, id=id_)

    # ==================================================================
    # EQUIPMENT LAYOUT (positions dans le bac)
    # ==================================================================
    def _equip_layout(self):
        p = self.params
        d = self._d()
        pad = p['padding']
        div = p['divider_t']
        foam = p['foam_t']

        mx_x = pad
        mx_y = (d['id'] - MIXON8_D) / 2
        mx_z = foam

        side_x = pad + MIXON8_W + pad + div + pad
        wm_y = pad
        wm_z = foam
        tb_y = pad + WOLFMIX_D + pad
        tb_z = foam

        return {
            'mixon': (mx_x, mx_y, mx_z),
            'wolfmix': (side_x, wm_y, wm_z),
            'tbone': (side_x, tb_y, tb_z),
            'divider_x': pad + MIXON8_W + pad,
        }

    # ==================================================================
    # BAC (contient le materiel, va EN HAUT quand deploye)
    # ==================================================================
    def _case_bottom(self):
        p = self.params
        d = self._d()
        ew, ed, bh = d['ew'], d['ed'], d['bh']
        pt = d['pt']
        al = d['al']

        shell = cube([ew, ed, bh]) - translate([pt, pt, pt])(
            cube([ew - 2*pt, ed - 2*pt, bh])
        )

        alu = self._alu_frame(ew, ed, bh, al)

        layout = self._equip_layout()
        div_x = pt + layout['divider_x']
        divider = translate([div_x, pt, pt])(
            cube([p['divider_t'], ed - 2*pt, bh - pt])
        )

        locks = self._butterfly_row(ew, ed, bh)
        handles = self._handles(ew, ed, bh)

        return (
            color(self._C['case'])(shell + divider)
            + color(self._C['alu'])(alu + locks)
            + handles
        )

    # ==================================================================
    # COUVERCLE (va EN BAS quand deploye = base de stabilite)
    # ==================================================================
    def _case_lid(self):
        d = self._d()
        ew, ed, lh = d['ew'], d['ed'], d['lh']
        pt, al = d['pt'], d['al']

        shell = cube([ew, ed, lh]) - translate([pt, pt, 0])(
            cube([ew - 2*pt, ed - 2*pt, lh - pt])
        )

        alu = self._alu_frame(ew, ed, lh, al)
        locks = self._butterfly_row(ew, ed, 0)

        castors = union()
        for cx in [ew * 0.3, ew * 0.7]:
            castors += translate([cx, ed - 10, lh + 2])(
                color([0.2, 0.2, 0.2])(cylinder(d=50, h=10, _fn=24))
            )

        feet = union()
        for fx in [30, ew - 30]:
            for fy in [30, ed - 30]:
                feet += translate([fx, fy, -4])(
                    color([0.15, 0.15, 0.15])(cylinder(d=25, h=4, _fn=20))
                )

        return (
            color(self._C['case'])(shell)
            + color(self._C['alu'])(alu + locks)
            + castors + feet
        )

    # ==================================================================
    # Z-PANEL (pieds en Z - reference pour laser cut)
    # ==================================================================
    def _z_panel(self):
        p = self.params
        d = self._d()
        zt = p['z_panel_t']
        wh = p['working_height']
        foot = p['z_foot_len']
        al = d['al']
        ed = d['ed']

        z_h = wh - d['bh']
        total_d = ed - 20
        support_len = total_d - foot
        thick = al

        pts = [
            [0, z_h],
            [support_len, z_h],
            [support_len, z_h - thick],
            [total_d - foot, thick],
            [total_d, thick],
            [total_d, 0],
            [total_d - foot - thick * 0.8, 0],
            [thick, z_h - thick],
            [0, z_h - thick],
        ]

        profile = polygon(points=pts)
        panel = linear_extrude(height=zt)(profile)
        panel = rotate([90, 0, 90])(panel)

        gusset = 35.0
        panel += translate([0, total_d - foot - gusset, 0])(
            hull()(
                cube([zt, gusset, 2]),
                translate([0, gusset, 0])(cube([zt, 2, gusset]))
            )
        )
        panel += translate([0, support_len - gusset, z_h - thick - gusset])(
            hull()(
                cube([zt, 2, gusset]),
                translate([0, 0, gusset])(cube([zt, gusset, 2]))
            )
        )

        return color(self._C['case'])(panel)

    # ==================================================================
    # MOUSSE (layout dans le bac - reference)
    # ==================================================================
    def _foam_layout(self):
        p = self.params
        d = self._d()
        foam_t = p['foam_t']
        iw, id_ = d['iw'], d['id']
        layout = self._equip_layout()

        foam = cube([iw, id_, foam_t])

        mx, my, _ = layout['mixon']
        foam -= translate([mx, my, foam_t - MIXON8_H])(
            cube([MIXON8_W + 1, MIXON8_D + 1, MIXON8_H + 1])
        )
        foam -= translate([mx + MIXON8_W/2 - 50, my - 1, foam_t - 25])(
            cube([100, 12, 26])
        )
        foam -= translate([mx + MIXON8_W/2 - 50, my + MIXON8_D - 10, foam_t - 25])(
            cube([100, 12, 26])
        )

        wx, wy, _ = layout['wolfmix']
        foam -= translate([wx, wy, foam_t - WOLFMIX_H])(
            cube([WOLFMIX_W + 1, WOLFMIX_D + 1, WOLFMIX_H + 1])
        )

        tx, ty, _ = layout['tbone']
        foam -= translate([tx, ty, foam_t - TBONE_H])(
            cube([TBONE_W + 1, TBONE_D + 1, TBONE_H + 1])
        )

        return color(self._C['foam'])(foam)

    # ==================================================================
    # FACADE AVANT (plaque logo clipsable - reference entiere)
    # ==================================================================
    def _front_panel(self):
        p = self.params
        d = self._d()
        ew = d['ew']
        al = d['al']
        zt = p['z_panel_t']
        wh = p['working_height']
        bh = d['bh']

        z_inset = al + 5
        panel_w = ew - 2 * z_inset - 2 * zt - 4
        panel_h = wh - bh - 30
        panel_t = 3.0

        panel = cube([panel_w, panel_t, panel_h])

        # Logo en relief (centre)
        logo = logo_3d(width=min(400, panel_w * 0.65), height=2.5, quality='normal')
        panel += translate([panel_w / 2, -2.5, panel_h * 0.55])(
            rotate([90, 0, 0])(color(self._C['gold'])(logo))
        )

        # Clips lateraux
        clip_h, clip_depth, clip_t = 30.0, 15.0, 3.0
        clip_gap = zt + 0.5

        for frac in [0.25, 0.75]:
            cz = panel_h * frac - clip_h / 2
            lc = cube([clip_t, panel_t + clip_depth, clip_h])
            lc += translate([0, panel_t + clip_depth - 2, clip_h * 0.3])(
                cube([clip_t, 3, clip_h * 0.4])
            )
            panel += translate([-clip_t - clip_gap, 0, cz])(lc)
            panel += translate([panel_w + clip_gap, 0, cz])(lc)

        # Nervures arriere
        rib_depth = p['tile_rib_depth']
        for i in range(5):
            rx = panel_w * (i + 1) / 6
            panel += translate([rx - 1, panel_t, 15])(
                cube([2, rib_depth, panel_h - 30])
            )

        # Ventilation
        cols = int(panel_w / 50)
        for row in range(3):
            vz = panel_h * 0.12 + panel_h * 0.08 * row
            for col_i in range(cols):
                vx = panel_w * (col_i + 1) / (cols + 1)
                panel -= translate([vx, -1, vz])(
                    rotate([-90, 0, 0])(
                        cylinder(r=3.5, h=panel_t + 10, _fn=16)
                    )
                )

        return color(self._C['case'])(panel)

    def _front_panel_dims(self):
        p = self.params
        d = self._d()
        z_inset = d['al'] + 5
        zt = p['z_panel_t']
        pw = d['ew'] - 2 * z_inset - 2 * zt - 4
        ph = p['working_height'] - d['bh'] - 30
        return pw, ph

    # ==================================================================
    # TUILES FACADE (pieces imprimables)
    # ==================================================================
    def _split_front_panel_tile(self, col, row):
        """Extrait une tuile de la grille facade.

        Construit la facade complete puis decoupe la zone de la tuile
        par intersection booleenne. Ajoute rainure-languette sur les bords.
        """
        p = self.params
        pw, ph = self._front_panel_dims()
        cols = p['front_tile_cols']
        rows = p['front_tile_rows']
        tongue_w = p['tile_tongue_w']
        groove_clr = p['tile_groove_clr']
        panel_t = 3.0
        rib_depth = p['tile_rib_depth']

        tile_w = pw / cols
        tile_h = ph / rows

        # Construire la facade entiere
        panel = self._front_panel()

        # Zone de cette tuile (intersection)
        x0 = col * tile_w
        z0 = row * tile_h
        margin = 0.5
        selector = translate([x0 - margin, -50, z0 - margin])(
            cube([tile_w + 2 * margin, 150, tile_h + 2 * margin])
        )
        tile = panel * selector

        # Recentrer a l'origine pour impression
        tile = translate([-x0, 0, -z0])(tile)

        # Languette bord droit (si pas la derniere colonne)
        if col < cols - 1:
            tile += translate([tile_w, 0, 0])(
                cube([tongue_w, panel_t, tile_h])
            )

        # Rainure bord gauche (si pas la premiere colonne)
        if col > 0:
            gw = tongue_w + groove_clr
            tile -= translate([-gw, -0.5, -0.5])(
                cube([gw + 0.1, panel_t + 1, tile_h + 1])
            )

        # Trous d'alignement (3 par joint, diam 2mm, prof 4mm)
        pin_d = 2.0
        pin_depth = 4.0
        for frac in [0.25, 0.5, 0.75]:
            pz = tile_h * frac
            # Trous cote droit
            if col < cols - 1:
                tile -= translate([tile_w + tongue_w / 2, panel_t / 2, pz])(
                    cylinder(d=pin_d, h=pin_depth, _fn=16)
                )
            # Trous cote gauche
            if col > 0:
                tile -= translate([0, panel_t / 2, pz])(
                    rotate([0, 0, 0])(cylinder(d=pin_d + groove_clr, h=pin_depth, _fn=16))
                )

        return color(self._C['pla'])(tile)

    # ==================================================================
    # GABARITS MOUSSE (templates pour decoupe manuelle)
    # ==================================================================
    def _foam_template_section(self, section):
        """Cadre plat avec decoupes equipement pour guider la decoupe mousse."""
        p = self.params
        d = self._d()
        frame_h = 8.0
        wall = 5.0
        layout = self._equip_layout()

        if section == 'mixon_l':
            # Moitie gauche du gabarit Mixon
            fw = 200.0
            fd = min(205.0, MIXON8_D + 20)
            frame = cube([fw, fd, frame_h])
            # Decoupe Mixon (moitie gauche)
            mx = 10.0
            my = (fd - MIXON8_D) / 2
            frame -= translate([mx, my, -1])(
                cube([fw - mx + 1, MIXON8_D, frame_h + 2])
            )
            # Bord exterieur
            frame += translate([0, 0, 0])(cube([wall, fd, frame_h]))
            frame += translate([0, 0, 0])(cube([fw, wall, frame_h]))
            frame += translate([0, fd - wall, 0])(cube([fw, wall, frame_h]))
            # Repere de jointure
            frame += translate([fw - 3, fd/2 - 10, 0])(cube([6, 20, frame_h]))
            return color(self._C['pla'])(frame)

        elif section == 'mixon_r':
            # Moitie droite du gabarit Mixon
            fw = 200.0
            fd = min(205.0, MIXON8_D + 20)
            frame = cube([fw, fd, frame_h])
            my = (fd - MIXON8_D) / 2
            frame -= translate([-1, my, -1])(
                cube([fw - 10 + 1, MIXON8_D, frame_h + 2])
            )
            frame += translate([fw - wall, 0, 0])(cube([wall, fd, frame_h]))
            frame += translate([0, 0, 0])(cube([fw, wall, frame_h]))
            frame += translate([0, fd - wall, 0])(cube([fw, wall, frame_h]))
            # Repere de jointure
            frame += translate([-3, fd/2 - 10, 0])(cube([6, 20, frame_h]))
            return color(self._C['pla'])(frame)

        else:  # 'side'
            # Gabarit compartiment WolfMix + t.bone
            fw = min(215.0, max(WOLFMIX_W, TBONE_W) + 30)
            fd = min(200.0, WOLFMIX_D + TBONE_D + 30)
            frame = cube([fw, fd, frame_h])
            # Decoupe WolfMix
            wx = (fw - WOLFMIX_W) / 2
            wy = 10.0
            frame -= translate([wx, wy, -1])(
                cube([WOLFMIX_W, WOLFMIX_D, frame_h + 2])
            )
            # Decoupe t.bone
            tx = (fw - TBONE_W) / 2
            ty = wy + WOLFMIX_D + 10
            frame -= translate([tx, ty, -1])(
                cube([TBONE_W, TBONE_D, frame_h + 2])
            )
            # Cadre exterieur
            frame += translate([0, 0, 0])(cube([wall, fd, frame_h]))
            frame += translate([fw - wall, 0, 0])(cube([wall, fd, frame_h]))
            frame += translate([0, 0, 0])(cube([fw, wall, frame_h]))
            frame += translate([0, fd - wall, 0])(cube([fw, wall, frame_h]))
            return color(self._C['pla'])(frame)

    # ==================================================================
    # CLOISON INTERNE (2 moities avec joints a doigts)
    # ==================================================================
    def _divider_section(self, half):
        """Moitie de la cloison interne avec joints a doigts."""
        p = self.params
        d = self._d()
        div_t = p['divider_t']
        ed = d['ed']
        pt = d['pt']
        bh = d['bh']

        full_d = ed - 2 * pt
        full_h = bh - pt
        half_d = full_d / 2

        # Piece de base
        divider = cube([div_t, half_d, full_h])

        # Joints a doigts (3 doigts alternants)
        finger_h = full_h / 6
        finger_ext = 8.0  # Extension du doigt

        if half == 'front':
            # Doigts sur le bord arriere (y = half_d)
            for i in range(3):
                fz = finger_h * (2 * i)
                # Doigt qui depasse
                divider += translate([0, half_d, fz])(
                    cube([div_t, finger_ext, finger_h])
                )
        else:  # 'rear'
            for i in range(3):
                fz = finger_h * (2 * i + 1)
                # Doigt qui depasse
                divider += translate([0, -finger_ext, fz])(
                    cube([div_t, finger_ext, finger_h])
                )
            # Encoches pour recevoir les doigts de la moitie avant
            for i in range(3):
                fz = finger_h * (2 * i)
                divider -= translate([-0.5, -0.5, fz])(
                    cube([div_t + 1, finger_ext + 1, finger_h + 0.2])
                )

        # Trous de fixation M5 (2 trous pour vis dans la coque du case)
        bolt_d = 5.3
        for fz in [full_h * 0.25, full_h * 0.75]:
            divider -= translate([-0.5, half_d / 2, fz])(
                rotate([0, 90, 0])(
                    cylinder(d=bolt_d, h=div_t + 1, _fn=24)
                )
            )

        return color(self._C['pla'])(divider)

    # ==================================================================
    # CONNECTEURS Z-PANEL (brackets pour contreplaque)
    # ==================================================================
    def _z_bracket(self, position):
        """Bracket imprime pour fixer le Z-panel en contreplaque.

        position='top': recoit le bac, poche pour star knob M8
        position='bottom': fixe le Z-panel au couvercle
        """
        p = self.params
        zt = p['z_panel_t']
        bw = 60.0
        bd = 50.0
        bh = 40.0
        wall = 4.0

        bracket = cube([bw, bd, bh])

        # Fente pour inserer le Z-panel (12mm)
        slot_clearance = 0.3
        bracket -= translate([(bw - zt - slot_clearance) / 2, -0.5, wall])(
            cube([zt + slot_clearance, bd + 1, bh - wall])
        )

        if position == 'top':
            # Poche pour ecrou M8 hex (13mm cle, 6.5mm epaisseur)
            nut_w = 15.0
            nut_h = 7.0
            bracket -= translate([bw/2 - nut_w/2, bd/2 - nut_w/2, -0.5])(
                cube([nut_w, nut_w, nut_h + 0.5])
            )
            # Trou traversant M8
            bracket -= translate([bw/2, bd/2, -0.5])(
                cylinder(d=8.5, h=bh + 1, _fn=24)
            )
            # Rebord de support pour le bac
            bracket += translate([-5, 0, bh - wall])(
                cube([bw + 10, bd, wall])
            )
        else:  # bottom
            # Trous pour vis de fixation dans le couvercle (2x M5)
            for bx in [bw * 0.25, bw * 0.75]:
                bracket -= translate([bx, bd/2, -0.5])(
                    cylinder(d=5.3, h=bh + 1, _fn=24)
                )
            # Rebord d'emboitement dans le couvercle
            lip_h = 8.0
            bracket += translate([wall, wall, -lip_h])(
                cube([bw - 2*wall, bd - 2*wall, lip_h])
            )
            bracket -= translate([wall + 3, wall + 3, -lip_h - 0.5])(
                cube([bw - 2*wall - 6, bd - 2*wall - 6, lip_h + 1])
            )

        # Trous pour vis de fixation du Z-panel (2x M5)
        slot_center_x = bw / 2
        for bz in [bh * 0.3, bh * 0.7]:
            bracket -= translate([slot_center_x, -0.5, bz])(
                rotate([-90, 0, 0])(
                    cylinder(d=5.3, h=bd + 1, _fn=24)
                )
            )

        return color(self._C['pla'])(bracket)

    def _z_gusset(self):
        """Renfort triangulaire pour jonction Z-panel. Se visse sur le contreplaque."""
        p = self.params
        zt = p['z_panel_t']
        gs = 50.0  # Cote du triangle

        # Triangle (gusset)
        pts = [[0, 0], [gs, 0], [0, gs]]
        profile = polygon(points=pts)
        gusset_body = linear_extrude(height=zt)(profile)

        # Trous de vis M4 (2 par face)
        for pos in [(15, 5), (35, 5)]:
            gusset_body -= translate([pos[0], pos[1], -0.5])(
                cylinder(d=4.3, h=zt + 1, _fn=20)
            )
        for pos in [(5, 15), (5, 35)]:
            gusset_body -= translate([pos[0], pos[1], -0.5])(
                cylinder(d=4.3, h=zt + 1, _fn=20)
            )

        return color(self._C['pla'])(gusset_body)

    def _z_foot_pad(self):
        """Patin anti-derapant pour le pied du Z-panel."""
        p = self.params
        foot = p['z_foot_len']
        zt = p['z_panel_t']
        pad_h = 8.0

        # Base avec rainure pour le Z-panel
        pad = cube([foot, zt + 20, pad_h])

        # Rainure pour inserer le contreplaque
        slot_clr = 0.3
        pad -= translate([-0.5, (zt + 20 - zt - slot_clr) / 2, pad_h - 5])(
            cube([foot + 1, zt + slot_clr, 6])
        )

        # Texture anti-derapante (rainures)
        for i in range(int(foot / 10)):
            pad -= translate([i * 10 + 3, -0.5, -0.5])(
                cube([2, zt + 21, 1.5])
            )

        # Trous de fixation M4
        for fx in [foot * 0.25, foot * 0.75]:
            pad -= translate([fx, (zt + 20) / 2, -0.5])(
                cylinder(d=4.3, h=pad_h + 1, _fn=20)
            )

        return color(self._C['pla'])(pad)

    # ==================================================================
    # ACCESSOIRES CASE (pieces imprimables)
    # ==================================================================
    def _cable_grommet(self):
        """Passe-cable snap-in pour les parois du case."""
        od = 30.0   # Diametre exterieur
        hole_d = 18.0  # Passage cable
        flange_h = 3.0
        body_h = 10.0

        # Corps cylindrique
        body = cylinder(d=od, h=body_h, _fn=32)
        body -= translate([0, 0, -0.5])(
            cylinder(d=hole_d, h=body_h + 1, _fn=32)
        )

        # Collerette (snap)
        body += translate([0, 0, body_h - flange_h])(
            cylinder(d=od + 4, h=flange_h, _fn=32)
        )

        # Languettes snap-in (4 autour)
        for angle in [0, 90, 180, 270]:
            snap = translate([od/2 - 1, -1.5, 2])(
                cube([2.5, 3, body_h - flange_h - 2])
            )
            snap += translate([od/2 + 0.5, -1.5, 2])(
                cube([1.5, 3, 2])
            )
            body += rotate([0, 0, angle])(snap)

        return color(self._C['pla'])(body)

    def _star_knob(self):
        """Molette etoile M8 pour serrage a la main."""
        knob_d = 45.0
        knob_h = 15.0
        skirt_h = 8.0
        bolt_d = 8.5
        points = 5

        # Corps (cylindre principal)
        knob = cylinder(d=knob_d, h=knob_h, _fn=48)

        # Branches de l'etoile
        for i in range(points):
            angle = i * 360 / points
            branch = translate([knob_d/2 - 5, -4, 0])(
                cube([12, 8, knob_h])
            )
            knob += rotate([0, 0, angle])(branch)

        # Jupe striee pour grip
        for i in range(24):
            angle = i * 15
            knob -= rotate([0, 0, angle])(
                translate([knob_d/2 + 2, -0.5, 0])(
                    cube([5, 1, knob_h])
                )
            )

        # Trou M8 avec poche hexagonale
        knob -= translate([0, 0, -0.5])(
            cylinder(d=bolt_d, h=knob_h + 1, _fn=24)
        )
        # Poche hex (ecrou M8 = 13mm entre plats)
        hex_r = 13.0 / 2 / math.cos(math.pi / 6)
        knob -= translate([0, 0, knob_h - 7])(
            cylinder(r=hex_r, h=8, _fn=6)
        )

        return color(self._C['gold'])(knob)

    def _logo_plate(self):
        """Plaque logo pour le couvercle du case."""
        pw = 200.0
        ph = 50.0
        pt = 5.0

        plate = cube([pw, ph, pt])

        # Coins arrondis (chanfrein)
        r = 4.0
        for cx in [0, pw]:
            for cy in [0, ph]:
                plate -= translate([cx, cy, -0.5])(
                    cube([r, r, pt + 1])
                )
                plate += translate([cx, cy, 0])(
                    cylinder(r=r, h=pt, _fn=24)
                )

        # Logo en relief
        logo = logo_3d(width=min(160, pw * 0.8), height=2.0, quality='normal')
        plate += translate([pw / 2, ph / 2, pt])(
            color(self._C['gold'])(logo)
        )

        # Trous de fixation
        for lx in [15, pw - 15]:
            plate -= translate([lx, ph / 2, -0.5])(
                cylinder(d=4.3, h=pt + 1, _fn=20)
            )

        return color(self._C['case'])(plate)

    def _corner_protector(self):
        """Protection de coin pour case en contreplaque."""
        cs = 30.0
        ct = 2.5

        # 3 faces (coin en L)
        corner = cube([cs, cs, ct])
        corner += cube([cs, ct, cs])
        corner += cube([ct, cs, cs])

        # Arrondi interne
        corner -= translate([ct, ct, ct])(
            sphere(r=2, _fn=16)
        )

        # Trous de fixation (1 par face)
        corner -= translate([cs/2, cs/2, -0.5])(
            cylinder(d=3.3, h=ct + 1, _fn=16)
        )
        corner -= translate([cs/2, -0.5, cs/2])(
            rotate([-90, 0, 0])(cylinder(d=3.3, h=ct + 1, _fn=16))
        )
        corner -= translate([-0.5, cs/2, cs/2])(
            rotate([0, 90, 0])(cylinder(d=3.3, h=ct + 1, _fn=16))
        )

        return color(self._C['alu'])(corner)

    def _handle_recess(self):
        """Cadre pour poignee encastree dans le contreplaque."""
        hw = 170.0
        hd = 50.0
        frame_h = 15.0
        wall = 4.0
        lip = 3.0

        # Cadre exterieur
        frame = cube([hw, hd, frame_h])
        frame -= translate([wall, wall, wall])(
            cube([hw - 2*wall, hd - 2*wall, frame_h])
        )

        # Rebord d'encastrement (lip)
        frame += translate([-lip, -lip, frame_h - 2])(
            cube([hw + 2*lip, hd + 2*lip, 2])
        )
        frame -= translate([wall - lip, wall - lip, frame_h - 2.5])(
            cube([hw - 2*wall + 2*lip, hd - 2*wall + 2*lip, 3])
        )

        # Trous de fixation
        for fx in [wall/2, hw - wall/2]:
            for fy in [wall/2, hd - wall/2]:
                frame -= translate([fx, fy, -0.5])(
                    cylinder(d=3.3, h=frame_h + 1, _fn=16)
                )

        return color(self._C['pla'])(frame)

    # ==================================================================
    # PROFILS LASER DXF (2D pour decoupe)
    # ==================================================================
    def _case_bottom_dxf(self):
        """Patron 2D depliant du bac pour decoupe laser contreplaque."""
        d = self._d()
        ew, ed, bh = d['ew'], d['ed'], d['bh']
        pt = d['pt']

        model = union()

        # Fond
        model += square([ew, ed])

        # Cote avant (rabattu vers le bas)
        model += translate([0, -bh - 5, 0])(square([ew, bh]))

        # Cote arriere (rabattu vers le haut)
        model += translate([0, ed + 5, 0])(square([ew, bh]))

        # Cote gauche (rabattu a gauche)
        model += translate([-bh - 5, 0, 0])(square([bh, ed]))

        # Cote droit (rabattu a droite)
        model += translate([ew + 5, 0, 0])(square([bh, ed]))

        # Tab/slot marks (petits rectangles aux jonctions)
        tab_w = 20.0
        for i in range(5):
            tx = ew * (i + 1) / 6 - tab_w / 2
            # Tabs bord avant
            model += translate([tx, -2, 0])(square([tab_w, 4]))
            # Tabs bord arriere
            model += translate([tx, ed - 2, 0])(square([tab_w, 4]))

        # Extruder en 0.1mm pour la visualisation 3D
        return linear_extrude(height=0.1)(model)

    def _case_lid_dxf(self):
        """Patron 2D depliant du couvercle."""
        d = self._d()
        ew, ed, lh = d['ew'], d['ed'], d['lh']

        model = union()
        model += square([ew, ed])
        model += translate([0, -lh - 5, 0])(square([ew, lh]))
        model += translate([0, ed + 5, 0])(square([ew, lh]))
        model += translate([-lh - 5, 0, 0])(square([lh, ed]))
        model += translate([ew + 5, 0, 0])(square([lh, ed]))

        return linear_extrude(height=0.1)(model)

    def _z_panel_dxf(self):
        """Profil Z 2D pour decoupe laser en contreplaque 12mm."""
        p = self.params
        d = self._d()
        wh = p['working_height']
        foot = p['z_foot_len']
        al = d['al']
        ed = d['ed']

        z_h = wh - d['bh']
        total_d = ed - 20
        support_len = total_d - foot
        thick = al

        pts = [
            [0, z_h],
            [support_len, z_h],
            [support_len, z_h - thick],
            [total_d - foot, thick],
            [total_d, thick],
            [total_d, 0],
            [total_d - foot - thick * 0.8, 0],
            [thick, z_h - thick],
            [0, z_h - thick],
        ]

        profile = polygon(points=pts)
        return linear_extrude(height=0.1)(profile)

    # ==================================================================
    # HARDWARE HELPERS
    # ==================================================================
    def _alu_frame(self, w, depth, h, al):
        fr = union()
        for x in [0, w - al]:
            for y in [0, depth - al]:
                fr += translate([x, y, 0])(cube([al, al, h]))
        for z in [0, h - al]:
            fr += translate([0, 0, z])(cube([w, al, al]))
            fr += translate([0, depth - al, z])(cube([w, al, al]))
        return fr

    def _butterfly_row(self, ew, ed, z_pos):
        locks = union()
        bw, bh, bd = 42.0, 27.0, 10.0
        for i in range(3):
            lx = ew * (i + 1) / 4 - bw / 2
            locks += translate([lx, -bd, z_pos])(cube([bw, bd, bh]))
            locks += translate([lx, ed, z_pos])(cube([bw, bd, bh]))
        locks += translate([-bd, ed/2 - bw/2, z_pos])(cube([bd, bw, bh]))
        locks += translate([ew, ed/2 - bw/2, z_pos])(cube([bd, bw, bh]))
        return locks

    def _handles(self, ew, ed, h):
        handles = union()
        hw, hh, hd = 150.0, 35.0, 12.0
        hz = h / 2 - hh / 2
        for i in [0.3, 0.7]:
            hx = ew * i - hw / 2
            handles += translate([hx, -hd, hz])(cube([hw, hd, hh]))
            handles += translate([hx, ed, hz])(cube([hw, hd, hh]))
        hw2 = 120.0
        handles += translate([-hd, ed/2 - hw2/2, hz])(cube([hd, hw2, hh]))
        handles += translate([ew, ed/2 - hw2/2, hz])(cube([hd, hw2, hh]))
        return color([0.25, 0.25, 0.27])(handles)

    def _steel_corners(self, ew, ed, h):
        corners = union()
        cs, ct = 30.0, 1.5
        for x in [0, ew - cs]:
            for y in [0, ed - cs]:
                for z in [0, h - cs]:
                    c = cube([cs, cs, ct]) + cube([cs, ct, cs]) + cube([ct, cs, cs])
                    corners += translate([x, y, z])(c)
        return color(self._C['alu'])(corners)

    # ==================================================================
    # GHOST EQUIPMENT
    # ==================================================================
    def _ghost_in_tray(self, offset_x=0, offset_y=0, offset_z=0):
        p = self.params
        d = self._d()
        pt = d['pt']
        layout = self._equip_layout()
        ox, oy, oz = offset_x + pt, offset_y + pt, offset_z + pt

        ghosts = union()

        mx, my, mz = layout['mixon']
        ghosts += color([0.9, 0.1, 0.1, 0.35])(
            translate([ox + mx, oy + my, oz + mz])(
                cube([MIXON8_W, MIXON8_D, MIXON8_H])
            )
        )

        wx, wy, wz = layout['wolfmix']
        ghosts += color([0.1, 0.8, 0.1, 0.35])(
            translate([ox + wx, oy + wy, oz + wz])(
                cube([WOLFMIX_W, WOLFMIX_D, WOLFMIX_H])
            )
        )

        tx, ty, tz = layout['tbone']
        ghosts += color([0.1, 0.4, 0.9, 0.35])(
            translate([ox + tx, oy + ty, oz + tz])(
                cube([TBONE_W, TBONE_D, TBONE_H])
            )
        )

        return ghosts

    # ==================================================================
    # VUE DEPLOYEE (le meuble DJ pret a mixer)
    # ==================================================================
    def _deployed_view(self):
        p = self.params
        d = self._d()
        ew, ed = d['ew'], d['ed']
        wh = p['working_height']
        bh, lh = d['bh'], d['lh']
        al = d['al']
        zt = p['z_panel_t']

        model = union()

        # 1. Couvercle retourne au sol
        model += translate([0, 0, 0])(self._case_lid())

        # 2. Z-Panels debout
        z_inset = al + 5
        z_base = lh
        model += translate([z_inset, 10, z_base])(self._z_panel())
        model += translate([ew - z_inset - zt, 10, z_base])(self._z_panel())

        # 3. Bac avec matos en haut
        tray_z = wh - bh
        model += translate([0, 0, tray_z])(self._case_bottom())

        # Mousse + materiel
        pt = d['pt']
        model += translate([pt, pt, tray_z + pt])(self._foam_layout())
        model += self._ghost_in_tray(offset_z=tray_z)

        # 4. Facade avant
        pw, ph = self._front_panel_dims()
        panel_x = z_inset + zt + 2
        panel_z = z_base + 15
        model += translate([panel_x, -3, panel_z])(self._front_panel())

        # 5. Brackets (visualisation)
        for side_x in [z_inset, ew - z_inset - zt]:
            # Top brackets
            model += translate([side_x - 5, 20, tray_z - 5])(
                color([0.3, 0.8, 0.3, 0.5])(cube([zt + 10, 50, 5]))
            )

        return model

    # ==================================================================
    # VUE TRANSPORT (case ferme)
    # ==================================================================
    def _transport_view(self):
        p = self.params
        d = self._d()
        ew, ed, eh = d['ew'], d['ed'], d['eh']
        bh, lh = d['bh'], d['lh']

        model = union()
        model += self._case_bottom()

        pt = d['pt']
        model += translate([pt, pt, pt])(self._foam_layout())
        model += self._ghost_in_tray()

        model += translate([0, 0, bh])(self._case_lid())
        model += self._steel_corners(ew, ed, eh)

        return model

    # ==================================================================
    # VUE ECLATEE
    # ==================================================================
    def _full_assembly_view(self):
        p = self.params
        d = self._d()
        ew, ed = d['ew'], d['ed']
        gap = 120.0

        model = union()

        # 1. Couvercle
        model += self._case_lid()

        # 2. Z-Panels
        model += translate([-200, 0, 0])(self._z_panel())
        model += translate([ew + 100, 0, 0])(self._z_panel())

        # 3. Facade
        pw, ph = self._front_panel_dims()
        model += translate([(ew - pw)/2, -200, 0])(self._front_panel())

        # 4. Mousse
        pt = d['pt']
        model += translate([pt, pt, d['lh'] + gap])(self._foam_layout())

        # 5. Bac avec matos
        model += translate([0, 0, d['lh'] + gap * 2])(self._case_bottom())
        model += self._ghost_in_tray(offset_z=d['lh'] + gap * 2)

        # 6. Accessoires imprimes (en bas a droite)
        acc_x = ew + 250
        model += translate([acc_x, 0, 0])(self._z_bracket('top'))
        model += translate([acc_x, 80, 0])(self._z_bracket('bottom'))
        model += translate([acc_x, 160, 0])(self._z_gusset())
        model += translate([acc_x, 230, 0])(self._star_knob())
        model += translate([acc_x + 80, 0, 0])(self._cable_grommet())
        model += translate([acc_x + 80, 50, 0])(self._corner_protector())
        model += translate([acc_x + 80, 100, 0])(self._logo_plate())

        return model

    # ==================================================================
    # BUILD DISPATCH
    # ==================================================================
    def build(self):
        part = self.params['export_part']

        # --- Vues ---
        views = {
            'deployed': self._deployed_view,
            'transport': self._transport_view,
            'full_assembly': self._full_assembly_view,
        }

        # --- Pieces entieres (reference) ---
        legacy = {
            'case_bottom': self._case_bottom,
            'case_lid': self._case_lid,
            'z_panel': self._z_panel,
            'front_panel': self._front_panel,
            'foam_layout': self._foam_layout,
        }

        # --- Tuiles facade ---
        if part.startswith('front_tile_'):
            row_letter = part[11]   # 'A' ou 'B'
            col_num = int(part[12]) - 1  # '1'-'5' -> 0-4
            row_idx = 0 if row_letter == 'A' else 1
            return self._split_front_panel_tile(col_num, row_idx)

        # --- Gabarits mousse ---
        if part.startswith('foam_template_'):
            section = part[14:]  # 'mixon_l', 'mixon_r', 'side'
            return self._foam_template_section(section)

        # --- Cloison ---
        if part.startswith('divider_'):
            half = part[8:]  # 'front', 'rear'
            return self._divider_section(half)

        # --- Connecteurs Z-panel ---
        connectors = {
            'z_bracket_top': lambda: self._z_bracket('top'),
            'z_bracket_bottom': lambda: self._z_bracket('bottom'),
            'z_gusset': self._z_gusset,
            'z_foot_pad': self._z_foot_pad,
        }

        # --- Accessoires ---
        accessories = {
            'cable_grommet': self._cable_grommet,
            'star_knob': self._star_knob,
            'logo_plate': self._logo_plate,
            'corner_protector': self._corner_protector,
            'handle_recess': self._handle_recess,
        }

        # --- Profils laser ---
        laser = {
            'case_bottom_dxf': self._case_bottom_dxf,
            'case_lid_dxf': self._case_lid_dxf,
            'z_panel_dxf': self._z_panel_dxf,
        }

        all_dispatch = {**views, **legacy, **connectors, **accessories, **laser}
        return all_dispatch.get(part, self._deployed_view)()


if __name__ == "__main__":
    b = ThonZStyle()
    d = b._d()
    print(f"Case : {d['ew']:.0f} x {d['ed']:.0f} x {d['eh']:.0f} mm")
    print(f"Bac : {d['bh']:.0f} mm / Couvercle : {d['lh']:.0f} mm")
    print(f"Hauteur travail : {b.params['working_height']:.0f} mm")
    layout = b._equip_layout()
    print(f"Mixon @ x={layout['mixon'][0]:.0f}")
    print(f"WolfMix @ x={layout['wolfmix'][0]:.0f}")
    print(f"t.bone @ x={layout['tbone'][0]:.0f}")
    b.save_scad()
