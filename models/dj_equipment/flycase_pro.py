"""
Flycase Pro - DJ Table avec Pieds Telescopiques
=================================================
Flycase DJ avec deploiement rapide via pieds telescopiques
Penn Elcom 9967 + twist-lock R1606.

CONCEPT :
  Le materiel (Mixon 8 Pro, WolfMix, t.bone HF) est installe dans
  le bac du case et y RESTE. Le couvercle contient un plateau laptop
  avec risers pour le MacBook Pro.

  TRANSPORT : Case ferme, pieds ranges dans le couvercle (sangles).
  DEPLOIEMENT :
    1. Ouvrir les butterfly locks, enlever le couvercle
    2. Deployer les 4 pieds telescopiques (twist-lock R1606)
    3. Visser les pieds dans les receptacles R1606 sous le bac
    4. Ouvrir le couvercle en position inclinee (110 deg)
    5. MacBook sur le plateau laptop -> pret a mixer !

  Hauteur de travail : ~1020mm (ergonomique).
  Pieds : Penn Elcom 9967 (835mm, diam 32mm).

FABRICATION HYBRIDE :
  - Structure (case) : contreplaque bouleau 7mm, decoupe laser
  - Accessoires : impression 3D (PLA)
  - Mousse : decoupe manuelle avec gabarits imprimes
  - Quincaillerie : Penn Elcom 9967, R1606, butterfly locks, charnieres

Materiel (dans le bac, face vers le haut) :
  - Reloop Mixon 8 Pro : 657 x 391 x 68 mm (centre-gauche)
  - WolfMix W1         : 195 x 220 x 62 mm (droite du Mixon)
  - t.bone Free Solo HT: 212 x 160 x 44 mm (droite, sous le WolfMix)
  - MacBook Pro 16"    : 356 x 249 x 17 mm (plateau dans le couvercle)

export_part:
  Vues (non-imprimables) :
  - "deployed"          : Mode table avec pieds deployes
  - "transport"         : Case ferme, pieds ranges
  - "interior_layout"   : Vue de dessus equipement
  - "lid_open"          : Couvercle ouvert 110 deg avec laptop
  - "exploded"          : Vue eclatee

  Pieces 3D imprimables :
  - "cable_grommet"         : Passe-cable snap-in diam 30mm
  - "logo_plate"            : Plaque logo or
  - "corner_protector"      : Protection de coin PLA
  - "leg_keeper_pad"        : Patin maintien pieds en transport
  - "divider_wall"          : Cloison interieure (reference)
  - "cable_clip"            : Clip routage cable
  - "power_strip_bracket"   : Support multiprise
  - "laptop_riser"          : Colonne riser 60mm
  - "laptop_retainer_lip"   : Levre anti-glissement laptop
  - "latch_reinforcement"   : Plaque renfort R1606

  Gabarits mousse :
  - "foam_mixon"        : Gabarit mousse Mixon
  - "foam_accessories"  : Gabarit mousse WolfMix + t.bone
  - "foam_lid"          : Gabarit mousse couvercle

  Profils laser DXF :
  - "case_base_dxf"     : Patron 2D bac
  - "case_lid_dxf"      : Patron 2D couvercle
  - "divider_dxf"       : Patron 2D cloison
  - "laptop_shelf_dxf"  : Patron 2D plateau laptop
"""
import math
from solid2 import *
from ..base import ParametricModel
from ..utils import rounded_box, brand_text, mounting_hole
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

MACBOOK_W = 356.0
MACBOOK_D = 249.0
MACBOOK_H = 17.0


class FlycasePro(ParametricModel):
    """Flycase DJ Pro avec pieds telescopiques Penn Elcom 9967."""

    def __init__(self, **params):
        super().__init__("flycase_pro", **params)

    def default_params(self):
        return {
            'case_int_w': 894.0,
            'case_int_d': 470.0,
            'case_int_h': 93.0,
            'wall_t': 7.0,
            'tray_ext_h': 107.0,
            'lid_ext_h': 78.0,
            'divider_t': 5.0,
            'padding': 5.0,
            'foam_t': 15.0,
            'working_height': 1020.0,
            'leg_length': 835.0,
            'leg_diameter': 32.0,
            'leg_inset': 50.0,
            'r1606_hole_d': 35.0,
            'grommet_d': 30.0,
            'laptop_shelf_w': 370.0,
            'laptop_shelf_d': 260.0,
            'riser_h': 60.0,
            'use_logo': True,
            'export_part': 'deployed',
        }

    def param_schema(self):
        return {
            'case_int_w': {
                'type': 'float', 'min': 800, 'max': 1000,
                'unit': 'mm', 'description': 'Largeur interieure du case',
            },
            'case_int_d': {
                'type': 'float', 'min': 400, 'max': 550,
                'unit': 'mm', 'description': 'Profondeur interieure du case',
            },
            'case_int_h': {
                'type': 'float', 'min': 70, 'max': 120,
                'unit': 'mm', 'description': 'Hauteur interieure utile',
            },
            'wall_t': {
                'type': 'float', 'min': 5, 'max': 12,
                'unit': 'mm', 'description': 'Epaisseur paroi contreplaque bouleau',
            },
            'tray_ext_h': {
                'type': 'float', 'min': 80, 'max': 150,
                'unit': 'mm', 'description': 'Hauteur exterieure du bac',
            },
            'lid_ext_h': {
                'type': 'float', 'min': 50, 'max': 120,
                'unit': 'mm', 'description': 'Hauteur exterieure du couvercle',
            },
            'divider_t': {
                'type': 'float', 'min': 3, 'max': 10,
                'unit': 'mm', 'description': 'Epaisseur cloison interieure',
            },
            'padding': {
                'type': 'float', 'min': 3, 'max': 15,
                'unit': 'mm', 'description': 'Jeu autour des appareils (mousse)',
            },
            'foam_t': {
                'type': 'float', 'min': 10, 'max': 30,
                'unit': 'mm', 'description': 'Epaisseur mousse sous le matos',
            },
            'working_height': {
                'type': 'float', 'min': 800, 'max': 1200,
                'unit': 'mm', 'description': 'Hauteur de travail ergonomique',
            },
            'leg_length': {
                'type': 'float', 'min': 600, 'max': 1000,
                'unit': 'mm', 'description': 'Longueur pieds Penn Elcom 9967',
            },
            'leg_diameter': {
                'type': 'float', 'min': 25, 'max': 40,
                'unit': 'mm', 'description': 'Diametre pieds',
            },
            'leg_inset': {
                'type': 'float', 'min': 30, 'max': 80,
                'unit': 'mm', 'description': 'Retrait des pieds depuis les bords',
            },
            'r1606_hole_d': {
                'type': 'float', 'min': 30, 'max': 42,
                'unit': 'mm', 'description': 'Diametre percage twist-lock R1606',
            },
            'grommet_d': {
                'type': 'float', 'min': 20, 'max': 40,
                'unit': 'mm', 'description': 'Diametre passe-cable',
            },
            'laptop_shelf_w': {
                'type': 'float', 'min': 300, 'max': 450,
                'unit': 'mm', 'description': 'Largeur plateau laptop',
            },
            'laptop_shelf_d': {
                'type': 'float', 'min': 200, 'max': 350,
                'unit': 'mm', 'description': 'Profondeur plateau laptop',
            },
            'riser_h': {
                'type': 'float', 'min': 30, 'max': 100,
                'unit': 'mm', 'description': 'Hauteur risers plateau laptop',
            },
            'use_logo': {
                'type': 'bool',
                'description': 'Inclure le logo sur le couvercle',
            },
            'export_part': {
                'type': 'string',
                'options': [
                    # --- Vues (non-imprimables) ---
                    'deployed', 'transport', 'interior_layout',
                    'lid_open', 'exploded',
                    # --- IMPRIMABLE : Accessoires 3D ---
                    'cable_grommet', 'logo_plate', 'corner_protector',
                    'leg_keeper_pad', 'divider_wall', 'cable_clip',
                    'power_strip_bracket', 'laptop_riser',
                    'laptop_retainer_lip', 'latch_reinforcement',
                    # --- Gabarits mousse ---
                    'foam_mixon', 'foam_accessories', 'foam_lid',
                    # --- LASER : Profils DXF ---
                    'case_base_dxf', 'case_lid_dxf',
                    'divider_dxf', 'laptop_shelf_dxf',
                ],
                'description': 'Piece ou vue a exporter',
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
    # DIMENSIONS DERIVEES
    # ------------------------------------------------------------------
    def _dims(self):
        """Calcule toutes les dimensions derivees du case."""
        p = self.params
        wt = p['wall_t']
        iw = p['case_int_w']
        id_ = p['case_int_d']
        ih = p['case_int_h']
        pad = p['padding']
        div = p['divider_t']
        foam = p['foam_t']

        # Dimensions exterieures
        ew = iw + 2 * wt   # 894 + 14 = 908 -> ~910
        ed = id_ + 2 * wt  # 470 + 14 = 484
        tray_h = p['tray_ext_h']
        lid_h = p['lid_ext_h']
        total_h = tray_h + lid_h

        # Layout equipement dans le bac
        # Mixon a gauche, WolfMix + t.bone a droite
        mx_slot_w = MIXON8_W + 2 * pad
        mx_slot_d = MIXON8_D + 2 * pad

        side_slot_w = max(WOLFMIX_W, TBONE_W) + 2 * pad
        side_slot_d = id_  # toute la profondeur

        # Position cloison
        divider_x = pad + MIXON8_W + pad

        # Positions equipement (relatives a l'interieur du bac)
        mx_x = pad
        mx_y = (id_ - MIXON8_D) / 2
        mx_z = foam

        side_x = divider_x + div + pad
        wm_y = pad
        wm_z = foam
        tb_y = pad + WOLFMIX_D + pad
        tb_z = foam

        return {
            'ew': ew, 'ed': ed,
            'tray_h': tray_h, 'lid_h': lid_h, 'total_h': total_h,
            'iw': iw, 'id': id_, 'ih': ih,
            'wt': wt,
            'mx_slot_w': mx_slot_w, 'mx_slot_d': mx_slot_d,
            'side_slot_w': side_slot_w, 'side_slot_d': side_slot_d,
            'divider_x': divider_x,
            'mx': (mx_x, mx_y, mx_z),
            'wm': (side_x, wm_y, wm_z),
            'tb': (side_x, tb_y, tb_z),
        }

    # ==================================================================
    # BAC (contient le materiel)
    # ==================================================================
    def _case_tray(self):
        """Construit le bac avec trous R1606, butterfly locks, poignees."""
        p = self.params
        d = self._dims()
        ew, ed = d['ew'], d['ed']
        tray_h = d['tray_h']
        wt = d['wt']
        iw, id_ = d['iw'], d['id']
        div_t = p['divider_t']

        # Coque exterieure
        shell = cube([ew, ed, tray_h]) - translate([wt, wt, wt])(
            cube([iw, id_, tray_h])
        )

        # Cloison interieure
        div_x = wt + d['divider_x']
        divider = translate([div_x, wt, wt])(
            cube([div_t, id_, tray_h - wt])
        )

        # Trous R1606 twist-lock sous le fond (4 coins)
        r1606_d = p['r1606_hole_d']
        leg_inset = p['leg_inset']
        r1606_holes = union()
        for lx in [leg_inset, ew - leg_inset]:
            for ly in [leg_inset, ed - leg_inset]:
                r1606_holes += translate([lx, ly, -0.5])(
                    cylinder(d=r1606_d, h=wt + 1, _fn=32)
                )

        # Butterfly locks (3 devant, 3 derriere, 1 par cote)
        locks = self._butterfly_row(ew, ed, tray_h)

        # Poignees laterales
        handles = self._handles(ew, ed, tray_h)

        # Trous de ventilation (4 oblongs sous le Mixon)
        vents = union()
        vent_w, vent_d = 60.0, 8.0
        mx_x = wt + d['mx'][0]
        mx_slot_w = d['mx_slot_w']
        for i in range(4):
            vx = mx_x + mx_slot_w * (i + 1) / 5 - vent_w / 2
            vy = ed / 2 - vent_d / 2
            vents += translate([vx, vy, -0.5])(
                hull()(
                    cylinder(d=vent_d, h=wt + 1, _fn=24),
                    translate([vent_w, 0, 0])(
                        cylinder(d=vent_d, h=wt + 1, _fn=24)
                    ),
                )
            )

        # Passe-cables (2 a l'arriere)
        grommet_d = p['grommet_d']
        grommets = union()
        for gx_frac in [0.35, 0.7]:
            grommets += translate([ew * gx_frac, ed - wt / 2, tray_h * 0.55])(
                rotate([90, 0, 0])(
                    cylinder(d=grommet_d, h=wt + 2, center=True, _fn=32)
                )
            )

        tray = (
            color(self._C['case'])(shell + divider - r1606_holes - vents - grommets)
            + color(self._C['alu'])(locks)
            + handles
        )
        return tray

    # ==================================================================
    # COUVERCLE (contient plateau laptop + mousse protection)
    # ==================================================================
    def _case_lid(self):
        """Construit le couvercle avec charnieres et verin a gaz."""
        p = self.params
        d = self._dims()
        ew, ed = d['ew'], d['ed']
        lid_h = d['lid_h']
        wt = d['wt']
        iw, id_ = d['iw'], d['id']

        # Coque exterieure
        shell = cube([ew, ed, lid_h]) - translate([wt, wt, 0])(
            cube([iw, id_, lid_h - wt])
        )

        # Charnieres arriere (2 positions)
        hinges = union()
        hinge_w, hinge_h, hinge_d = 80.0, 12.0, 25.0
        for hx in [ew * 0.25 - hinge_w / 2, ew * 0.75 - hinge_w / 2]:
            hinges += translate([hx, ed, lid_h - hinge_h])(
                cube([hinge_w, hinge_d, hinge_h])
            )

        # Points de fixation verin a gaz (2 cotes)
        gas_strut = union()
        for sx in [wt + 20, ew - wt - 20]:
            gas_strut += translate([sx, ed - wt - 10, lid_h * 0.3])(
                cylinder(d=8, h=15, _fn=16)
            )

        # Logo sur le dessus
        logo_geo = union()
        if p['use_logo']:
            logo = logo_3d(width=min(250, ew * 0.3), height=2.0, quality='normal')
            logo_geo = translate([ew / 2, ed / 2, lid_h])(
                color(self._C['gold'])(logo)
            )

        return (
            color(self._C['case'])(shell)
            + color(self._C['alu'])(hinges + gas_strut)
            + logo_geo
        )

    # ==================================================================
    # PIEDS TELESCOPIQUES (Penn Elcom 9967)
    # ==================================================================
    def _legs(self, extended=True):
        """4 pieds telescopiques avec twist-lock R1606."""
        p = self.params
        d = self._dims()
        ew, ed = d['ew'], d['ed']
        leg_d = p['leg_diameter']
        leg_len = p['leg_length'] if extended else 100.0
        leg_inset = p['leg_inset']

        legs = union()
        for lx in [leg_inset, ew - leg_inset]:
            for ly in [leg_inset, ed - leg_inset]:
                # Tube principal
                leg = cylinder(d=leg_d, h=leg_len, _fn=24)
                leg -= translate([0, 0, -0.5])(
                    cylinder(d=leg_d - 4, h=leg_len + 1, _fn=24)
                )
                # Embout twist-lock R1606 en haut
                r1606 = translate([0, 0, leg_len])(
                    cylinder(d=leg_d + 6, h=8, _fn=32)
                )
                # Pied anti-derapant en bas
                foot_pad = translate([0, 0, -5])(
                    cylinder(d=leg_d + 10, h=5, _fn=24)
                )
                legs += translate([lx, ly, -leg_len - 5])(
                    color(self._C['alu'])(leg + r1606)
                    + color([0.15, 0.15, 0.15])(foot_pad)
                )
        return legs

    # ==================================================================
    # MOUSSE (layout dans le bac)
    # ==================================================================
    def _foam_layout(self):
        """Mousse interieure du bac avec empreintes equipement."""
        p = self.params
        d = self._dims()
        foam_t = p['foam_t']
        iw, id_ = d['iw'], d['id']

        foam = cube([iw, id_, foam_t])

        # Empreinte Mixon
        mx_x, mx_y, _ = d['mx']
        foam -= translate([mx_x, mx_y, foam_t - MIXON8_H])(
            cube([MIXON8_W + 1, MIXON8_D + 1, MIXON8_H + 1])
        )
        # Encoches doigts devant/derriere Mixon
        foam -= translate([mx_x + MIXON8_W / 2 - 50, mx_y - 1, foam_t - 25])(
            cube([100, 12, 26])
        )
        foam -= translate([mx_x + MIXON8_W / 2 - 50, mx_y + MIXON8_D - 10, foam_t - 25])(
            cube([100, 12, 26])
        )

        # Empreinte WolfMix
        wx, wy, _ = d['wm']
        foam -= translate([wx, wy, foam_t - WOLFMIX_H])(
            cube([WOLFMIX_W + 1, WOLFMIX_D + 1, WOLFMIX_H + 1])
        )

        # Empreinte t.bone
        tx, ty, _ = d['tb']
        foam -= translate([tx, ty, foam_t - TBONE_H])(
            cube([TBONE_W + 1, TBONE_D + 1, TBONE_H + 1])
        )

        return color(self._C['foam'])(foam)

    # ==================================================================
    # PLATEAU LAPTOP (dans le couvercle)
    # ==================================================================
    def _laptop_platform(self):
        """Plateau laptop sur risers dans le couvercle."""
        p = self.params
        d = self._dims()
        shelf_w = p['laptop_shelf_w']
        shelf_d = p['laptop_shelf_d']
        shelf_t = 3.0
        riser_h = p['riser_h']
        iw, id_ = d['iw'], d['id']

        platform = union()

        # Position centree dans le couvercle
        sx = (iw - shelf_w) / 2
        sy = (id_ - shelf_d) / 2

        # Plateau
        shelf = translate([sx, sy, riser_h])(
            cube([shelf_w, shelf_d, shelf_t])
        )
        platform += color(self._C['case'])(shelf)

        # 4 risers cylindriques
        riser_d = 25.0
        riser_inset = 20.0
        for rx in [sx + riser_inset, sx + shelf_w - riser_inset]:
            for ry in [sy + riser_inset, sy + shelf_d - riser_inset]:
                riser = cylinder(d=riser_d, h=riser_h, _fn=24)
                riser -= translate([0, 0, -0.5])(
                    cylinder(d=5.3, h=riser_h + 1, _fn=24)
                )
                platform += translate([rx, ry, 0])(
                    color(self._C['pla'])(riser)
                )

        # Levre anti-glissement (3 cotes)
        lip_h = 8.0
        lip_t = 2.0
        lip_z = riser_h + shelf_t
        # Arriere
        platform += translate([sx, sy, lip_z])(
            color(self._C['pla'])(cube([shelf_w, lip_t, lip_h]))
        )
        # Gauche
        platform += translate([sx, sy, lip_z])(
            color(self._C['pla'])(cube([lip_t, shelf_d, lip_h]))
        )
        # Droite
        platform += translate([sx + shelf_w - lip_t, sy, lip_z])(
            color(self._C['pla'])(cube([lip_t, shelf_d, lip_h]))
        )

        return platform

    # ==================================================================
    # GHOST EQUIPMENT (transparents pour visualisation)
    # ==================================================================
    def _ghost_equipment(self, offset_x=0, offset_y=0, offset_z=0):
        """Fantomes transparents des appareils dans le bac."""
        p = self.params
        d = self._dims()
        wt = d['wt']
        ox, oy, oz = offset_x + wt, offset_y + wt, offset_z + wt

        ghosts = union()

        # Mixon 8 Pro (rouge)
        mx_x, mx_y, mx_z = d['mx']
        ghosts += color([0.9, 0.1, 0.1, 0.35])(
            translate([ox + mx_x, oy + mx_y, oz + mx_z])(
                cube([MIXON8_W, MIXON8_D, MIXON8_H])
            )
        )

        # WolfMix (vert)
        wx, wy, wz = d['wm']
        ghosts += color([0.1, 0.8, 0.1, 0.35])(
            translate([ox + wx, oy + wy, oz + wz])(
                cube([WOLFMIX_W, WOLFMIX_D, WOLFMIX_H])
            )
        )

        # t.bone (bleu)
        tx, ty, tz = d['tb']
        ghosts += color([0.1, 0.4, 0.9, 0.35])(
            translate([ox + tx, oy + ty, oz + tz])(
                cube([TBONE_W, TBONE_D, TBONE_H])
            )
        )

        return ghosts

    def _ghost_laptop(self, offset_x=0, offset_y=0, offset_z=0):
        """Fantome du MacBook Pro sur le plateau laptop."""
        p = self.params
        d = self._dims()
        shelf_w = p['laptop_shelf_w']
        shelf_d = p['laptop_shelf_d']
        riser_h = p['riser_h']
        iw, id_ = d['iw'], d['id']

        sx = (iw - shelf_w) / 2
        sy = (id_ - shelf_d) / 2
        laptop_x = sx + (shelf_w - MACBOOK_W) / 2
        laptop_y = sy + (shelf_d - MACBOOK_D) / 2
        laptop_z = riser_h + 3.0  # au-dessus du plateau

        return color([0.6, 0.6, 0.65, 0.4])(
            translate([offset_x + laptop_x, offset_y + laptop_y, offset_z + laptop_z])(
                cube([MACBOOK_W, MACBOOK_D, MACBOOK_H])
            )
        )

    # ==================================================================
    # HARDWARE HELPERS
    # ==================================================================
    def _butterfly_row(self, ew, ed, z_pos):
        """Butterfly locks autour du case."""
        locks = union()
        bw, bh, bd = 42.0, 27.0, 10.0
        # 3 devant, 3 derriere
        for i in range(3):
            lx = ew * (i + 1) / 4 - bw / 2
            locks += translate([lx, -bd, z_pos - bh])(cube([bw, bd, bh]))
            locks += translate([lx, ed, z_pos - bh])(cube([bw, bd, bh]))
        # 1 par cote
        locks += translate([-bd, ed / 2 - bw / 2, z_pos - bh])(cube([bd, bw, bh]))
        locks += translate([ew, ed / 2 - bw / 2, z_pos - bh])(cube([bd, bw, bh]))
        return locks

    def _handles(self, ew, ed, h):
        """Poignees laterales du case."""
        handles = union()
        hw, hh, hd = 150.0, 35.0, 12.0
        hz = h / 2 - hh / 2
        # Devant/derriere
        for frac in [0.3, 0.7]:
            hx = ew * frac - hw / 2
            handles += translate([hx, -hd, hz])(cube([hw, hd, hh]))
            handles += translate([hx, ed, hz])(cube([hw, hd, hh]))
        # Cotes
        hw2 = 120.0
        handles += translate([-hd, ed / 2 - hw2 / 2, hz])(cube([hd, hw2, hh]))
        handles += translate([ew, ed / 2 - hw2 / 2, hz])(cube([hd, hw2, hh]))
        return color([0.25, 0.25, 0.27])(handles)

    def _steel_corners(self, ew, ed, h):
        """Coins acier pour le case."""
        corners = union()
        cs, ct = 30.0, 1.5
        for x in [0, ew - cs]:
            for y in [0, ed - cs]:
                for z in [0, h - cs]:
                    c = cube([cs, cs, ct]) + cube([cs, ct, cs]) + cube([ct, cs, cs])
                    corners += translate([x, y, z])(c)
        return color(self._C['alu'])(corners)

    # ==================================================================
    # VUE DEPLOYEE (mode table avec pieds)
    # ==================================================================
    def _deployed_view(self):
        """Table DJ prete a mixer : pieds deployes, bac en haut."""
        p = self.params
        d = self._dims()
        ew, ed = d['ew'], d['ed']
        tray_h = d['tray_h']
        wt = d['wt']

        model = union()

        # Pieds deployes (partent du bas du bac vers le sol)
        model += self._legs(extended=True)

        # Bac a z=0 (le haut des pieds arrive au fond du bac)
        model += self._case_tray()

        # Mousse dans le bac
        model += translate([wt, wt, wt])(self._foam_layout())

        # Equipement fantome
        model += self._ghost_equipment()

        return model

    # ==================================================================
    # VUE TRANSPORT (case ferme, pieds ranges)
    # ==================================================================
    def _transport_view(self):
        """Case ferme avec pieds ranges dans le couvercle."""
        p = self.params
        d = self._dims()
        ew, ed = d['ew'], d['ed']
        tray_h = d['tray_h']
        lid_h = d['lid_h']
        wt = d['wt']

        model = union()

        # Bac
        model += self._case_tray()

        # Mousse + matos
        model += translate([wt, wt, wt])(self._foam_layout())
        model += self._ghost_equipment()

        # Couvercle par dessus
        model += translate([0, 0, tray_h])(self._case_lid())

        # Coins acier
        model += self._steel_corners(ew, ed, tray_h + lid_h)

        # Pieds ranges (a plat dans le couvercle, fantome)
        leg_d = p['leg_diameter']
        leg_inset = p['leg_inset']
        for i, lx in enumerate([wt + 20, wt + 60, ew - wt - 60, ew - wt - 20]):
            model += color([0.5, 0.5, 0.52, 0.3])(
                translate([lx, wt + 10, tray_h + wt + 5])(
                    rotate([0, 90, 90])(
                        cylinder(d=leg_d, h=ed - 2 * wt - 20, _fn=16)
                    )
                )
            )

        return model

    # ==================================================================
    # VUE INTERIEURE (top-down equipment layout)
    # ==================================================================
    def _interior_layout(self):
        """Vue de dessus du placement des equipements."""
        p = self.params
        d = self._dims()
        wt = d['wt']
        iw, id_ = d['iw'], d['id']

        model = union()

        # Fond du bac (plat, pas les parois)
        model += color(self._C['case'])(
            cube([iw, id_, wt])
        )

        # Mousse
        model += translate([0, 0, wt])(self._foam_layout())

        # Equipement (fantome, sans offset wt car deja relatif)
        mx_x, mx_y, mx_z = d['mx']
        model += color([0.9, 0.1, 0.1, 0.5])(
            translate([mx_x, mx_y, wt + mx_z])(
                cube([MIXON8_W, MIXON8_D, MIXON8_H])
            )
        )

        wx, wy, wz = d['wm']
        model += color([0.1, 0.8, 0.1, 0.5])(
            translate([wx, wy, wt + wz])(
                cube([WOLFMIX_W, WOLFMIX_D, WOLFMIX_H])
            )
        )

        tx, ty, tz = d['tb']
        model += color([0.1, 0.4, 0.9, 0.5])(
            translate([tx, ty, wt + tz])(
                cube([TBONE_W, TBONE_D, TBONE_H])
            )
        )

        # Cloison
        div_x = d['divider_x']
        model += color([0.3, 0.3, 0.3])(
            translate([div_x, 0, wt])(
                cube([p['divider_t'], id_, p['case_int_h']])
            )
        )

        # Labels texte
        lbl_h = 0.8
        for label, lx, ly in [
            ("MIXON 8 PRO", mx_x + MIXON8_W / 2, mx_y + MIXON8_D / 2),
            ("WOLFMIX", wx + WOLFMIX_W / 2, wy + WOLFMIX_D / 2),
            ("t.bone HF", tx + TBONE_W / 2, ty + TBONE_D / 2),
        ]:
            model += translate([lx, ly, wt + p['foam_t'] + 70])(
                color(self._C['gold'])(
                    linear_extrude(height=lbl_h)(
                        text(label, size=12, font=DEFAULT_TEXT_FONT,
                             halign="center", valign="center", _fn=32)
                    )
                )
            )

        return model

    # ==================================================================
    # VUE COUVERCLE OUVERT (110 deg avec laptop)
    # ==================================================================
    def _lid_open_view(self):
        """Couvercle ouvert a 110 deg avec laptop sur plateau."""
        p = self.params
        d = self._dims()
        ew, ed = d['ew'], d['ed']
        tray_h = d['tray_h']
        lid_h = d['lid_h']
        wt = d['wt']

        model = union()

        # Bac
        model += self._case_tray()
        model += translate([wt, wt, wt])(self._foam_layout())
        model += self._ghost_equipment()

        # Couvercle pivote a 110 deg autour de l'arete arriere
        lid_angle = 110.0
        pivot_y = ed
        pivot_z = tray_h

        lid_group = union()
        lid_group += self._case_lid()

        # Plateau laptop + MacBook dans le couvercle
        lid_group += translate([wt, wt, wt])(self._laptop_platform())
        lid_group += self._ghost_laptop(offset_x=wt, offset_y=wt, offset_z=wt)

        # Rotation du couvercle autour de la charniere arriere
        model += translate([0, pivot_y, pivot_z])(
            rotate([lid_angle, 0, 0])(
                translate([0, -ed, 0])(lid_group)
            )
        )

        return model

    # ==================================================================
    # VUE ECLATEE
    # ==================================================================
    def _exploded_view(self):
        """Vue eclatee de tous les composants."""
        p = self.params
        d = self._dims()
        ew, ed = d['ew'], d['ed']
        tray_h = d['tray_h']
        lid_h = d['lid_h']
        wt = d['wt']
        gap = 150.0

        model = union()

        # 1. Pieds (en bas)
        model += translate([0, 0, -gap * 2])(self._legs(extended=False))

        # 2. Bac
        model += self._case_tray()

        # 3. Mousse dans le bac
        model += translate([wt, wt, wt + gap * 0.3])(self._foam_layout())

        # 4. Equipement
        model += translate([0, 0, gap * 0.5])(self._ghost_equipment())

        # 5. Couvercle
        model += translate([0, 0, tray_h + gap])(self._case_lid())

        # 6. Plateau laptop
        model += translate([wt, wt, tray_h + gap + wt + gap * 0.5])(
            self._laptop_platform()
        )

        # 7. MacBook
        model += translate([0, 0, tray_h + gap * 2.5])(
            self._ghost_laptop(offset_x=wt, offset_y=wt, offset_z=0)
        )

        # 8. Accessoires imprimes (a droite)
        acc_x = ew + 200
        model += translate([acc_x, 0, 0])(self._cable_grommet())
        model += translate([acc_x, 60, 0])(self._logo_plate())
        model += translate([acc_x, 130, 0])(self._corner_protector())
        model += translate([acc_x, 200, 0])(self._leg_keeper_pad())
        model += translate([acc_x + 100, 0, 0])(self._cable_clip())
        model += translate([acc_x + 100, 60, 0])(self._power_strip_bracket())
        model += translate([acc_x + 100, 140, 0])(self._laptop_riser())
        model += translate([acc_x + 100, 210, 0])(self._laptop_retainer_lip())
        model += translate([acc_x + 200, 0, 0])(self._latch_reinforcement())

        return model

    # ==================================================================
    # PIECES 3D IMPRIMABLES
    # ==================================================================
    def _cable_grommet(self):
        """Passe-cable snap-in diametre 30mm pour paroi du case."""
        p = self.params
        od = p['grommet_d']
        hole_d = od - 12.0
        flange_h = 3.0
        body_h = 10.0

        body = cylinder(d=od, h=body_h, _fn=32)
        body -= translate([0, 0, -0.5])(
            cylinder(d=hole_d, h=body_h + 1, _fn=32)
        )

        # Collerette
        body += translate([0, 0, body_h - flange_h])(
            cylinder(d=od + 4, h=flange_h, _fn=32)
        )

        # Languettes snap-in (4 autour)
        for angle in [0, 90, 180, 270]:
            snap = translate([od / 2 - 1, -1.5, 2])(
                cube([2.5, 3, body_h - flange_h - 2])
            )
            snap += translate([od / 2 + 0.5, -1.5, 2])(
                cube([1.5, 3, 2])
            )
            body += rotate([0, 0, angle])(snap)

        # Fente pour passage cable
        body -= translate([-hole_d / 2, -1.5, -0.5])(
            cube([hole_d, 3, body_h + 1])
        )

        return color(self._C['pla'])(body)

    def _logo_plate(self):
        """Plaque logo pour le couvercle du case."""
        pw = 200.0
        ph = 50.0
        pt = 5.0

        plate = cube([pw, ph, pt])

        # Coins arrondis
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
        """Protection de coin PLA pour case en contreplaque."""
        cs = 30.0
        ct = 2.5

        corner = cube([cs, cs, ct])
        corner += cube([cs, ct, cs])
        corner += cube([ct, cs, cs])

        corner -= translate([ct, ct, ct])(
            sphere(r=2, _fn=16)
        )

        for face_args in [
            ([cs / 2, cs / 2, -0.5], [0, 0, 0]),
            ([cs / 2, -0.5, cs / 2], [-90, 0, 0]),
            ([-0.5, cs / 2, cs / 2], [0, 90, 0]),
        ]:
            pos, rot = face_args
            corner -= translate(pos)(
                rotate(rot)(cylinder(d=3.3, h=ct + 1, _fn=16))
            )

        return color(self._C['alu'])(corner)

    def _leg_keeper_pad(self):
        """Patin de maintien pour pieds ranges dans le couvercle."""
        p = self.params
        leg_d = p['leg_diameter']
        pad_w = leg_d + 20
        pad_d = leg_d + 16
        pad_h = 15.0

        pad = cube([pad_w, pad_d, pad_h])

        # Gorge demi-cylindrique pour accueillir le pied
        pad -= translate([pad_w / 2, -0.5, pad_h - leg_d / 2])(
            rotate([-90, 0, 0])(
                cylinder(d=leg_d + 1, h=pad_d + 1, _fn=32)
            )
        )

        # Languette de retenue (sangle velcro)
        strap_w = 15.0
        strap_slot_h = 3.0
        for sy in [pad_d * 0.25, pad_d * 0.75]:
            pad -= translate([-0.5, sy - strap_w / 2, pad_h - strap_slot_h])(
                cube([pad_w + 1, strap_w, strap_slot_h + 0.5])
            )

        # Trous de fixation M4
        for fx in [8, pad_w - 8]:
            pad -= translate([fx, pad_d / 2, -0.5])(
                cylinder(d=4.3, h=pad_h + 1, _fn=20)
            )

        return color(self._C['pla'])(pad)

    def _divider_wall(self):
        """Cloison interieure du case (reference pour decoupe)."""
        p = self.params
        d = self._dims()
        div_t = p['divider_t']
        id_ = d['id']
        ih = d['ih']

        divider = cube([div_t, id_, ih])

        # Encoches doigts pour prise (3 encoches en haut)
        notch_w = 20.0
        notch_h = 8.0
        for i in range(3):
            ny = id_ * (i + 1) / 4 - notch_w / 2
            divider -= translate([-0.5, ny, ih - notch_h])(
                cube([div_t + 1, notch_w, notch_h + 0.5])
            )

        # Trous de fixation M5 (4 trous)
        bolt_d = 5.3
        for fz in [ih * 0.25, ih * 0.75]:
            for fy in [id_ * 0.25, id_ * 0.75]:
                divider -= translate([-0.5, fy, fz])(
                    rotate([0, 90, 0])(
                        cylinder(d=bolt_d, h=div_t + 1, _fn=24)
                    )
                )

        return color(self._C['pla'])(divider)

    def _cable_clip(self):
        """Clip de routage cable a clipser sur le bord du case."""
        clip_w = 20.0
        clip_d = 15.0
        clip_h = 12.0
        wall = 2.0
        cable_d = 8.0

        clip = cube([clip_w, clip_d, clip_h])

        # Canal cable
        clip -= translate([clip_w / 2, -0.5, clip_h / 2])(
            rotate([-90, 0, 0])(
                cylinder(d=cable_d, h=clip_d + 1, _fn=24)
            )
        )

        # Fente d'ouverture pour inserer le cable
        clip -= translate([clip_w / 2 - cable_d / 4, -0.5, clip_h / 2])(
            cube([cable_d / 2, clip_d + 1, clip_h])
        )

        # Patte de fixation (clip sur le bord)
        clip_patte = cube([clip_w, wall, clip_h + 8])
        clip_patte += translate([0, wall, clip_h])(
            cube([clip_w, 4, 3])
        )
        clip += translate([0, clip_d, -8])(clip_patte)

        return color(self._C['pla'])(clip)

    def _power_strip_bracket(self):
        """Support multiprise a fixer dans le couvercle."""
        bw = 60.0
        bd = 50.0
        bh = 25.0
        wall = 3.0
        strip_w = 45.0

        bracket = cube([bw, bd, bh])
        bracket -= translate([wall, wall, wall])(
            cube([bw - 2 * wall, bd - 2 * wall, bh])
        )

        # Fente pour passer la multiprise
        bracket -= translate([(bw - strip_w) / 2, -0.5, wall])(
            cube([strip_w, bd + 1, bh])
        )

        # Languettes de retenue
        for fx in [(bw - strip_w) / 2 - 2, (bw + strip_w) / 2]:
            bracket += translate([fx, wall, wall + 5])(
                cube([2, bd - 2 * wall, 3])
            )

        # Trous de fixation M4
        for fx in [bw * 0.25, bw * 0.75]:
            bracket -= translate([fx, bd / 2, -0.5])(
                cylinder(d=4.3, h=wall + 1, _fn=20)
            )

        return color(self._C['pla'])(bracket)

    def _laptop_riser(self):
        """Colonne riser 60mm pour plateau laptop."""
        p = self.params
        riser_h = p['riser_h']
        riser_d = 25.0
        base_d = 35.0
        base_h = 3.0

        # Base elargie
        riser = cylinder(d=base_d, h=base_h, _fn=32)
        # Corps
        riser += cylinder(d=riser_d, h=riser_h, _fn=32)
        # Tete (collerette de support)
        riser += translate([0, 0, riser_h - 2])(
            cylinder(d=riser_d + 6, h=2, _fn=32)
        )

        # Trou de vis central M5
        riser -= translate([0, 0, -0.5])(
            cylinder(d=5.3, h=riser_h + 1, _fn=24)
        )
        # Fraisage tete de vis en bas
        riser -= translate([0, 0, -0.5])(
            cylinder(d=10, h=4, _fn=24)
        )

        return color(self._C['pla'])(riser)

    def _laptop_retainer_lip(self):
        """Levre anti-glissement pour plateau laptop."""
        p = self.params
        lip_l = 100.0
        lip_h = 8.0
        lip_t = 2.0
        base_w = 15.0
        base_t = 3.0

        # Levre verticale
        lip = cube([lip_l, lip_t, lip_h])

        # Base de fixation (a plat)
        lip += translate([0, lip_t, 0])(
            cube([lip_l, base_w, base_t])
        )

        # Trous de fixation M3
        for fx in [15, lip_l - 15]:
            lip -= translate([fx, lip_t + base_w / 2, -0.5])(
                cylinder(d=3.3, h=base_t + 1, _fn=16)
            )

        return color(self._C['pla'])(lip)

    def _latch_reinforcement(self):
        """Plaque de renfort pour receptacle twist-lock R1606."""
        p = self.params
        r1606_d = p['r1606_hole_d']
        plate_d = r1606_d + 30
        plate_t = 4.0

        plate = cylinder(d=plate_d, h=plate_t, _fn=32)

        # Trou central R1606
        plate -= translate([0, 0, -0.5])(
            cylinder(d=r1606_d, h=plate_t + 1, _fn=32)
        )

        # Trous de fixation M4 (4 autour)
        bolt_r = (plate_d / 2) - 8
        for i in range(4):
            angle = i * 90 + 45
            bx = bolt_r * math.cos(math.radians(angle))
            by = bolt_r * math.sin(math.radians(angle))
            plate -= translate([bx, by, -0.5])(
                cylinder(d=4.3, h=plate_t + 1, _fn=20)
            )

        # Nervures de renfort (croix)
        rib_w = 3.0
        rib_h = 2.0
        for angle in [0, 90]:
            rib = translate([-plate_d / 2, -rib_w / 2, plate_t])(
                cube([plate_d, rib_w, rib_h])
            )
            # Soustraire le trou central des nervures
            rib -= translate([0, 0, -0.5])(
                cylinder(d=r1606_d + 2, h=plate_t + rib_h + 1, _fn=32)
            )
            plate += rotate([0, 0, angle])(rib)

        return color(self._C['pla'])(plate)

    # ==================================================================
    # GABARITS MOUSSE (templates pour decoupe manuelle)
    # ==================================================================
    def _foam_template(self, section):
        """Gabarit mousse pour decoupe manuelle."""
        p = self.params
        d = self._dims()
        frame_h = 8.0
        wall = 5.0

        if section == 'mixon':
            fw = min(215.0, MIXON8_W / 2 + 30)
            fd = min(205.0, MIXON8_D + 20)
            frame = cube([fw, fd, frame_h])
            mx = 10.0
            my = (fd - MIXON8_D) / 2
            frame -= translate([mx, my, -1])(
                cube([fw - mx + 1, MIXON8_D, frame_h + 2])
            )
            # Cadre
            frame += cube([wall, fd, frame_h])
            frame += cube([fw, wall, frame_h])
            frame += translate([0, fd - wall, 0])(cube([fw, wall, frame_h]))
            # Repere
            frame += translate([fw - 3, fd / 2 - 10, 0])(cube([6, 20, frame_h]))
            # Label
            frame -= translate([wall + 5, fd / 2, frame_h - 0.5])(
                linear_extrude(height=1)(
                    text("MIXON 8", size=8, font=DEFAULT_TEXT_FONT,
                         halign="left", valign="center", _fn=32)
                )
            )
            return color(self._C['pla'])(frame)

        elif section == 'accessories':
            fw = min(215.0, max(WOLFMIX_W, TBONE_W) + 30)
            fd = min(200.0, WOLFMIX_D + TBONE_D + 30)
            frame = cube([fw, fd, frame_h])
            # WolfMix
            wx = (fw - WOLFMIX_W) / 2
            wy = 10.0
            frame -= translate([wx, wy, -1])(
                cube([WOLFMIX_W, WOLFMIX_D, frame_h + 2])
            )
            # t.bone
            tx = (fw - TBONE_W) / 2
            ty = wy + WOLFMIX_D + 10
            frame -= translate([tx, ty, -1])(
                cube([TBONE_W, TBONE_D, frame_h + 2])
            )
            # Cadre
            frame += cube([wall, fd, frame_h])
            frame += translate([fw - wall, 0, 0])(cube([wall, fd, frame_h]))
            frame += cube([fw, wall, frame_h])
            frame += translate([0, fd - wall, 0])(cube([fw, wall, frame_h]))
            return color(self._C['pla'])(frame)

        else:  # 'lid'
            fw = min(215.0, MACBOOK_W / 2 + 30)
            fd = min(205.0, MACBOOK_D + 20)
            frame = cube([fw, fd, frame_h])
            lx = 10.0
            ly = (fd - MACBOOK_D) / 2
            frame -= translate([lx, ly, -1])(
                cube([fw - lx + 1, MACBOOK_D, frame_h + 2])
            )
            frame += cube([wall, fd, frame_h])
            frame += cube([fw, wall, frame_h])
            frame += translate([0, fd - wall, 0])(cube([fw, wall, frame_h]))
            frame += translate([fw - 3, fd / 2 - 10, 0])(cube([6, 20, frame_h]))
            return color(self._C['pla'])(frame)

    # ==================================================================
    # PROFILS LASER DXF (2D pour decoupe)
    # ==================================================================
    def _case_base_dxf(self):
        """Patron 2D depliant du bac pour decoupe laser contreplaque."""
        d = self._dims()
        ew, ed = d['ew'], d['ed']
        tray_h = d['tray_h']
        wt = d['wt']

        model = union()

        # Fond
        model += square([ew, ed])

        # Cote avant
        model += translate([0, -tray_h - 5, 0])(square([ew, tray_h]))

        # Cote arriere
        model += translate([0, ed + 5, 0])(square([ew, tray_h]))

        # Cote gauche
        model += translate([-tray_h - 5, 0, 0])(square([tray_h, ed]))

        # Cote droit
        model += translate([ew + 5, 0, 0])(square([tray_h, ed]))

        # Tabs (marques de pliage)
        tab_w = 20.0
        for i in range(5):
            tx = ew * (i + 1) / 6 - tab_w / 2
            model += translate([tx, -2, 0])(square([tab_w, 4]))
            model += translate([tx, ed - 2, 0])(square([tab_w, 4]))

        # Trous R1606 dans le fond
        r1606_d = self.params['r1606_hole_d']
        leg_inset = self.params['leg_inset']
        for lx in [leg_inset, ew - leg_inset]:
            for ly in [leg_inset, ed - leg_inset]:
                model -= translate([lx, ly, 0])(
                    circle(d=r1606_d, _fn=32)
                )

        return linear_extrude(height=0.1)(model)

    def _case_lid_dxf(self):
        """Patron 2D depliant du couvercle."""
        d = self._dims()
        ew, ed = d['ew'], d['ed']
        lid_h = d['lid_h']

        model = union()
        model += square([ew, ed])
        model += translate([0, -lid_h - 5, 0])(square([ew, lid_h]))
        model += translate([0, ed + 5, 0])(square([ew, lid_h]))
        model += translate([-lid_h - 5, 0, 0])(square([lid_h, ed]))
        model += translate([ew + 5, 0, 0])(square([lid_h, ed]))

        return linear_extrude(height=0.1)(model)

    def _divider_dxf(self):
        """Patron 2D de la cloison interieure."""
        d = self._dims()
        div_t = self.params['divider_t']
        id_ = d['id']
        ih = d['ih']

        model = square([id_, ih])

        # Encoches doigts en haut
        notch_w = 20.0
        notch_h = 8.0
        for i in range(3):
            nx = id_ * (i + 1) / 4 - notch_w / 2
            model -= translate([nx, ih - notch_h, 0])(
                square([notch_w, notch_h + 1])
            )

        return linear_extrude(height=0.1)(model)

    def _laptop_shelf_dxf(self):
        """Patron 2D du plateau laptop."""
        p = self.params
        sw = p['laptop_shelf_w']
        sd = p['laptop_shelf_d']

        model = square([sw, sd])

        # Trous de vis pour les risers (4 coins)
        riser_inset = 20.0
        for rx in [riser_inset, sw - riser_inset]:
            for ry in [riser_inset, sd - riser_inset]:
                model -= translate([rx, ry, 0])(
                    circle(d=5.3, _fn=24)
                )

        return linear_extrude(height=0.1)(model)

    # ==================================================================
    # BUILD DISPATCH
    # ==================================================================
    def build(self):
        part = self.params['export_part']

        # --- Vues ---
        views = {
            'deployed': self._deployed_view,
            'transport': self._transport_view,
            'interior_layout': self._interior_layout,
            'lid_open': self._lid_open_view,
            'exploded': self._exploded_view,
        }

        # --- Accessoires 3D ---
        accessories = {
            'cable_grommet': self._cable_grommet,
            'logo_plate': self._logo_plate,
            'corner_protector': self._corner_protector,
            'leg_keeper_pad': self._leg_keeper_pad,
            'divider_wall': self._divider_wall,
            'cable_clip': self._cable_clip,
            'power_strip_bracket': self._power_strip_bracket,
            'laptop_riser': self._laptop_riser,
            'laptop_retainer_lip': self._laptop_retainer_lip,
            'latch_reinforcement': self._latch_reinforcement,
        }

        # --- Gabarits mousse ---
        foam_templates = {
            'foam_mixon': lambda: self._foam_template('mixon'),
            'foam_accessories': lambda: self._foam_template('accessories'),
            'foam_lid': lambda: self._foam_template('lid'),
        }

        # --- Profils laser ---
        laser = {
            'case_base_dxf': self._case_base_dxf,
            'case_lid_dxf': self._case_lid_dxf,
            'divider_dxf': self._divider_dxf,
            'laptop_shelf_dxf': self._laptop_shelf_dxf,
        }

        all_dispatch = {**views, **accessories, **foam_templates, **laser}
        return all_dispatch.get(part, self._deployed_view)()


if __name__ == "__main__":
    fp = FlycasePro()
    d = fp._dims()
    print(f"Case ext: {d['ew']:.0f} x {d['ed']:.0f} x {d['total_h']:.0f} mm")
    print(f"Bac: {d['tray_h']:.0f} mm / Couvercle: {d['lid_h']:.0f} mm")
    print(f"Interieur: {d['iw']:.0f} x {d['id']:.0f} x {d['ih']:.0f} mm")
    print(f"Hauteur travail: {fp.params['working_height']:.0f} mm")
    print(f"Pieds: {fp.params['leg_length']:.0f} mm (Penn Elcom 9967)")
    print(f"Mixon @ x={d['mx'][0]:.0f}, y={d['mx'][1]:.0f}")
    print(f"WolfMix @ x={d['wm'][0]:.0f}, y={d['wm'][1]:.0f}")
    print(f"t.bone @ x={d['tb'][0]:.0f}, y={d['tb'][1]:.0f}")
    print(f"Export parts: {len(fp.param_schema()['export_part']['options'])}")
    fp.save_scad()
