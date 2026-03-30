"""
Flycase White & Gold Edition - DJ Table Mariage Premium
========================================================
Variante blanche et or du Flycase Pro, concue pour les mariages
et evenements haut de gamme. Memes dimensions, meme equipement,
esthetique completement differente.

CONCEPT :
  Case blanc avec quincaillerie or champagne (#C9A962).
  Interieur mousse noire pour contraste luxe (style ecrin bijou).
  Couvercle AMOVIBLE (lift-off) — pas de charniere, pas de verin.
  Le laptop se pose A COTE du case, pas dans le couvercle.

  TRANSPORT : Case ferme, pieds ranges sous le case (sangles + boucles or).
  DEPLOIEMENT :
    1. Ouvrir les butterfly locks or, retirer le couvercle (lift-off)
    2. Deployer les 4 pieds telescopiques blancs (twist-lock R1606)
    3. Visser les pieds dans les receptacles R1606 sous le bac
    4. Poser le couvercle a cote ou contre un pied
    5. MacBook a cote du case -> pret a mixer !

  Hauteur de travail : ~1020mm (ergonomique).
  Pieds : Penn Elcom 9967 peints blanc + colliers or.

FABRICATION HYBRIDE :
  - Structure (case) : contreplaque bouleau 7mm, Tolex blanc
  - Accessoires : impression 3D (PLA blanc)
  - Mousse : noire, decoupe manuelle avec gabarits imprimes
  - Quincaillerie : Penn Elcom 9967, R1606, butterfly locks OR, coins OR

Materiel (dans le bac, face vers le haut) :
  - Reloop Mixon 8 Pro : 657 x 391 x 68 mm (centre-gauche)
  - WolfMix W1         : 195 x 220 x 62 mm (droite du Mixon)
  - t.bone Free Solo HT: 212 x 160 x 44 mm (droite, sous le WolfMix)
  - MacBook Pro 16"    : 356 x 249 x 17 mm (a cote du case, PAS dans le couvercle)

export_part:
  Vues (non-imprimables) :
  - "deployed"          : Mode table avec pieds deployes, couvercle retire
  - "transport"         : Case ferme, pieds ranges
  - "interior_layout"   : Vue de dessus equipement
  - "exploded"          : Vue eclatee

  Pieces 3D imprimables :
  - "cable_grommet"         : Passe-cable snap-in diam 30mm (blanc)
  - "logo_plate"            : Plaque logo or
  - "corner_protector"      : Protection de coin PLA blanc
  - "corner_reinforcement"  : Plaque renfort coin (remplacement style blanc+or)
  - "leg_keeper_pad"        : Patin maintien pieds en transport (blanc)
  - "divider_wall"          : Cloison interieure avec accent or
  - "cable_clip"            : Clip routage cable (blanc)
  - "power_strip_bracket"   : Support multiprise (blanc)
  - "lid_handle"            : Poignee de prehension pour le couvercle amovible
  - "lid_alignment_pin"     : Pin d'alignement couvercle/bac (4x)

  Gabarits mousse :
  - "foam_mixon"        : Gabarit mousse Mixon
  - "foam_accessories"  : Gabarit mousse WolfMix + t.bone
  - "foam_lid"          : Gabarit mousse couvercle (protection transport)

  Profils laser DXF :
  - "case_base_dxf"     : Patron 2D bac
  - "case_lid_dxf"      : Patron 2D couvercle
  - "divider_dxf"       : Patron 2D cloison
"""
import math
from solid2 import *
from ..base import ParametricModel
from ..utils import rounded_box, brand_text, mounting_hole
from ..logo import logo_3d
from ..brand import DEFAULT_TEXT_FONT

# ========================================================================
# Dimensions des appareils (mm) — identiques au Flycase Pro
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


class FlycaseWhiteGold(ParametricModel):
    """Flycase White & Gold Edition — variante mariage/premium.

    Case blanc Tolex, quincaillerie or champagne, mousse noire interieure.
    Couvercle amovible (lift-off) sans charniere ni verin a gaz.
    Le laptop se pose a cote du case, pas dans le couvercle.
    """

    def __init__(self, **params):
        super().__init__("flycase_white_gold", **params)

    def default_params(self):
        return {
            # --- Dimensions case ---
            'case_int_w': 894.0,
            'case_int_d': 470.0,
            'case_int_h': 93.0,
            'wall_t': 7.0,
            'tray_ext_h': 107.0,
            'lid_ext_h': 78.0,
            'divider_t': 5.0,
            'padding': 5.0,
            'foam_t': 15.0,
            # --- Pieds ---
            'working_height': 1020.0,
            'leg_length': 835.0,
            'leg_diameter': 32.0,
            'leg_inset': 50.0,
            'r1606_hole_d': 35.0,
            # --- Accessoires ---
            'grommet_d': 30.0,
            'lid_pin_d': 8.0,
            'lid_pin_h': 12.0,
            # --- Options ---
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
                'unit': 'mm', 'description': 'Hauteur exterieure du couvercle amovible',
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
            'lid_pin_d': {
                'type': 'float', 'min': 5, 'max': 12,
                'unit': 'mm', 'description': 'Diametre pin alignement couvercle',
            },
            'lid_pin_h': {
                'type': 'float', 'min': 8, 'max': 20,
                'unit': 'mm', 'description': 'Hauteur pin alignement couvercle',
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
                    'exploded',
                    # --- IMPRIMABLE : Accessoires 3D ---
                    'cable_grommet', 'logo_plate', 'corner_protector',
                    'corner_reinforcement', 'leg_keeper_pad',
                    'divider_wall', 'cable_clip', 'power_strip_bracket',
                    'lid_handle', 'lid_alignment_pin',
                    'dps_cable_clip_small', 'dps_cable_clip_large',
                    'dps_cable_highway', 'dps_plug_holder',
                    'mixon_riser_front', 'mixon_riser_rear',
                    'mixon_risers_assembly',
                    # --- Gabarits mousse ---
                    'foam_mixon', 'foam_accessories', 'foam_lid',
                    # --- LASER : Profils DXF ---
                    'case_base_dxf', 'case_lid_dxf', 'divider_dxf',
                ],
                'description': 'Piece ou vue a exporter',
            },
        }

    # Couleurs — White & Gold Edition
    _C = {
        'case': [0.95, 0.95, 0.93],          # Blanc Tolex
        'gold': [0.79, 0.66, 0.38],           # Or champagne #C9A962
        'foam': [0.08, 0.08, 0.08],           # Mousse noire
        'alu_white': [0.92, 0.92, 0.90],      # Pieds blancs
        'pla': [0.93, 0.93, 0.91],            # PLA blanc mat
        'accent_gold': [0.85, 0.72, 0.42],    # Or clair accents
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
        mx_slot_w = MIXON8_W + 2 * pad
        mx_slot_d = MIXON8_D + 2 * pad

        side_slot_w = max(WOLFMIX_W, TBONE_W) + 2 * pad
        side_slot_d = id_

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
        """Construit le bac blanc avec trous R1606, butterfly locks or, poignees or."""
        p = self.params
        d = self._dims()
        ew, ed = d['ew'], d['ed']
        tray_h = d['tray_h']
        wt = d['wt']
        iw, id_ = d['iw'], d['id']
        div_t = p['divider_t']

        # Coque exterieure blanche
        shell = cube([ew, ed, tray_h]) - translate([wt, wt, wt])(
            cube([iw, id_, tray_h])
        )

        # Cloison interieure avec accent or sur le dessus
        div_x = wt + d['divider_x']
        divider = translate([div_x, wt, wt])(
            cube([div_t, id_, tray_h - wt])
        )
        # Bande or sur le dessus de la cloison
        divider_accent = translate([div_x, wt, tray_h - 1.5])(
            cube([div_t, id_, 1.5])
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

        # Receptacles pour pins d'alignement du couvercle (4 coins du dessus)
        pin_d = p['lid_pin_d']
        pin_inset = 25.0
        pin_holes = union()
        for px in [pin_inset, ew - pin_inset]:
            for py in [pin_inset, ed - pin_inset]:
                pin_holes += translate([px, py, tray_h - 8])(
                    cylinder(d=pin_d + 0.5, h=9, _fn=24)
                )

        # Butterfly locks or (3 devant, 3 derriere, 1 par cote)
        locks = self._butterfly_row(ew, ed, tray_h)

        # Poignees laterales or
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
            color(self._C['case'])(shell + divider - r1606_holes - vents - grommets - pin_holes)
            + color(self._C['gold'])(locks + divider_accent)
            + handles
        )
        return tray

    # ==================================================================
    # COUVERCLE AMOVIBLE (lift-off, pas de charniere)
    # ==================================================================
    def _case_lid(self):
        """Construit le couvercle amovible blanc — PAS de charniere ni verin."""
        p = self.params
        d = self._dims()
        ew, ed = d['ew'], d['ed']
        lid_h = d['lid_h']
        wt = d['wt']
        iw, id_ = d['iw'], d['id']

        # Coque exterieure blanche
        shell = cube([ew, ed, lid_h]) - translate([wt, wt, 0])(
            cube([iw, id_, lid_h - wt])
        )

        # Pins d'alignement (depasent sous le couvercle pour emboitement)
        pin_d = p['lid_pin_d']
        pin_h = p['lid_pin_h']
        pin_inset = 25.0
        pins = union()
        for px in [pin_inset, ew - pin_inset]:
            for py in [pin_inset, ed - pin_inset]:
                pins += translate([px, py, -pin_h])(
                    cylinder(d=pin_d, h=pin_h, _fn=24)
                )

        # Logo or sur le dessus
        logo_geo = union()
        if p['use_logo']:
            logo = logo_3d(width=min(250, ew * 0.3), height=2.0, quality='normal')
            logo_geo = translate([ew / 2, ed / 2, lid_h])(
                color(self._C['gold'])(logo)
            )

        return (
            color(self._C['case'])(shell)
            + color(self._C['pla'])(pins)
            + logo_geo
        )

    # ==================================================================
    # PIEDS TELESCOPIQUES (Penn Elcom 9967 peints blanc)
    # ==================================================================
    def _legs(self, extended=True):
        """4 pieds telescopiques blancs avec colliers or et twist-lock R1606."""
        p = self.params
        d = self._dims()
        ew, ed = d['ew'], d['ed']
        leg_d = p['leg_diameter']
        leg_len = p['leg_length'] if extended else 100.0
        leg_inset = p['leg_inset']

        legs = union()
        for lx in [leg_inset, ew - leg_inset]:
            for ly in [leg_inset, ed - leg_inset]:
                # Tube principal blanc
                leg = cylinder(d=leg_d, h=leg_len, _fn=24)
                leg -= translate([0, 0, -0.5])(
                    cylinder(d=leg_d - 4, h=leg_len + 1, _fn=24)
                )
                # Collier de serrage or (split-collar)
                collar = translate([0, 0, leg_len * 0.6])(
                    cylinder(d=leg_d + 4, h=10, _fn=32)
                )
                # Embout twist-lock R1606 or en haut
                r1606 = translate([0, 0, leg_len])(
                    cylinder(d=leg_d + 6, h=8, _fn=32)
                )
                # Pied anti-derapant blanc en bas
                foot_pad = translate([0, 0, -5])(
                    cylinder(d=leg_d + 10, h=5, _fn=24)
                )
                legs += translate([lx, ly, -leg_len - 5])(
                    color(self._C['alu_white'])(leg)
                    + color(self._C['gold'])(r1606 + collar)
                    + color([0.90, 0.90, 0.88])(foot_pad)
                )
        return legs

    # ==================================================================
    # MOUSSE NOIRE (layout dans le bac)
    # ==================================================================
    def _foam_layout(self):
        """Mousse noire interieure du bac avec empreintes equipement."""
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
    # GHOST EQUIPMENT (transparents pour visualisation)
    # ==================================================================
    def _ghost_equipment(self, offset_x=0, offset_y=0, offset_z=0):
        """Fantomes transparents des appareils dans le bac."""
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

    def _ghost_macbook_beside(self, offset_x=0, offset_y=0, offset_z=0):
        """Fantome du MacBook Pro POSE A COTE du case (pas dans le couvercle)."""
        d = self._dims()
        ew = d['ew']
        # MacBook a droite du case, decale de 30mm
        laptop_x = ew + 30
        laptop_y = (d['ed'] - MACBOOK_D) / 2
        laptop_z = 0  # meme niveau que le dessus du bac

        return color([0.6, 0.6, 0.65, 0.4])(
            translate([offset_x + laptop_x, offset_y + laptop_y, offset_z + laptop_z])(
                cube([MACBOOK_W, MACBOOK_D, MACBOOK_H])
            )
        )

    # ==================================================================
    # HARDWARE HELPERS
    # ==================================================================
    def _butterfly_row(self, ew, ed, z_pos):
        """Butterfly locks or autour du case."""
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
        """Poignees laterales or du case."""
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
        return color(self._C['gold'])(handles)

    def _steel_corners(self, ew, ed, h):
        """Coins or pour le case (remplacement des coins chrome)."""
        corners = union()
        cs, ct = 30.0, 1.5
        for x in [0, ew - cs]:
            for y in [0, ed - cs]:
                for z in [0, h - cs]:
                    c = cube([cs, cs, ct]) + cube([cs, ct, cs]) + cube([ct, cs, cs])
                    corners += translate([x, y, z])(c)
        return color(self._C['gold'])(corners)

    # ==================================================================
    # VUE DEPLOYEE (mode table, couvercle retire)
    # ==================================================================
    def _deployed_view(self):
        """Table DJ prete a mixer : pieds deployes, couvercle retire et pose a cote."""
        p = self.params
        d = self._dims()
        ew, ed = d['ew'], d['ed']
        tray_h = d['tray_h']
        lid_h = d['lid_h']
        wt = d['wt']

        model = union()

        # Pieds deployes blancs
        model += self._legs(extended=True)

        # Bac blanc a z=0
        model += self._case_tray()

        # Mousse noire dans le bac
        model += translate([wt, wt, wt])(self._foam_layout())

        # Equipement fantome
        model += self._ghost_equipment()

        # Cable management
        model += self._cable_management()

        # Mixon corner risers (platine surelevee)
        model += self._mixon_risers_assembly()

        # MacBook a cote
        model += self._ghost_macbook_beside()

        # Couvercle retire, pose au sol a cote (debout contre un pied arriere)
        leg_len = p['leg_length']
        lid_on_floor_x = ew + 50
        lid_on_floor_y = ed - lid_h - 10
        lid_on_floor_z = -(leg_len + 5)
        model += translate([lid_on_floor_x, lid_on_floor_y, lid_on_floor_z])(
            rotate([0, -85, 0])(  # Presque vertical, appuye
                self._case_lid()
            )
        )

        return model

    # ==================================================================
    # VUE TRANSPORT (case ferme, pieds ranges)
    # ==================================================================
    def _transport_view(self):
        """Case ferme blanc+or avec pieds ranges sous le bac."""
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

        # Couvercle pose par dessus (lift-off, alignement par pins)
        model += translate([0, 0, tray_h])(self._case_lid())

        # Coins or
        model += self._steel_corners(ew, ed, tray_h + lid_h)

        # Pieds ranges a plat SOUS le case (pas dans le couvercle)
        leg_d = p['leg_diameter']
        for i, ly in enumerate([wt + 20, wt + 60, ed - wt - 60, ed - wt - 20]):
            model += color([0.88, 0.88, 0.86, 0.3])(
                translate([wt + 10, ly, -leg_d - 10])(
                    rotate([0, 90, 0])(
                        cylinder(d=leg_d, h=ew - 2 * wt - 20, _fn=16)
                    )
                )
            )

        # Sangles blanches avec boucles or (simplifiees)
        strap_w = 25.0
        strap_t = 2.0
        for sx in [ew * 0.3, ew * 0.7]:
            model += color(self._C['case'])(
                translate([sx - strap_w / 2, wt, -leg_d - 15])(
                    cube([strap_w, ed - 2 * wt, strap_t])
                )
            )
            # Boucle or
            model += color(self._C['gold'])(
                translate([sx - 10, ed / 2 - 10, -leg_d - 17])(
                    cube([20, 20, 4])
                )
            )

        return model

    # ==================================================================
    # VUE INTERIEURE (top-down equipment layout)
    # ==================================================================
    def _interior_layout(self):
        """Vue de dessus du placement des equipements — noir dans blanc."""
        p = self.params
        d = self._dims()
        wt = d['wt']
        iw, id_ = d['iw'], d['id']

        model = union()

        # Fond du bac blanc
        model += color(self._C['case'])(
            cube([iw, id_, wt])
        )

        # Mousse noire
        model += translate([0, 0, wt])(self._foam_layout())

        # Equipement fantome
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

        # Cloison avec accent or
        div_x = d['divider_x']
        model += color([0.3, 0.3, 0.3])(
            translate([div_x, 0, wt])(
                cube([p['divider_t'], id_, p['case_int_h']])
            )
        )
        model += color(self._C['gold'])(
            translate([div_x, 0, wt + p['case_int_h'] - 1.5])(
                cube([p['divider_t'], id_, 1.5])
            )
        )

        # Labels texte or
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

        # Cable management
        model += self._cable_management()

        # Mixon corner risers
        model += self._mixon_risers_assembly()

        return model

    # ==================================================================
    # VUE ECLATEE
    # ==================================================================
    def _exploded_view(self):
        """Vue eclatee de tous les composants White & Gold."""
        p = self.params
        d = self._dims()
        ew, ed = d['ew'], d['ed']
        tray_h = d['tray_h']
        lid_h = d['lid_h']
        wt = d['wt']
        gap = 150.0

        model = union()

        # 1. Pieds blancs (en bas)
        model += translate([0, 0, -gap * 2])(self._legs(extended=False))

        # 2. Bac blanc
        model += self._case_tray()

        # 3. Mousse noire
        model += translate([wt, wt, wt + gap * 0.3])(self._foam_layout())

        # 4. Equipement
        model += translate([0, 0, gap * 0.5])(self._ghost_equipment())

        # 4b. Cable management (avec l'equipement)
        model += translate([0, 0, gap * 0.5])(self._cable_management())

        # 5. Couvercle amovible (au dessus, sans charniere)
        model += translate([0, 0, tray_h + gap])(self._case_lid())

        # 6. Accessoires imprimes blancs (a droite)
        acc_x = ew + 200
        model += translate([acc_x, 0, 0])(self._cable_grommet())
        model += translate([acc_x, 60, 0])(self._logo_plate())
        model += translate([acc_x, 130, 0])(self._corner_protector())
        model += translate([acc_x, 200, 0])(self._corner_reinforcement())
        model += translate([acc_x + 100, 0, 0])(self._leg_keeper_pad())
        model += translate([acc_x + 100, 70, 0])(self._cable_clip())
        model += translate([acc_x + 100, 130, 0])(self._power_strip_bracket())
        model += translate([acc_x + 100, 210, 0])(self._lid_handle())
        model += translate([acc_x + 200, 0, 0])(self._lid_alignment_pin())
        # Cable management pieces individuelles
        model += translate([acc_x + 200, 80, 0])(self._dps_clip(5.0))
        model += translate([acc_x + 200, 130, 0])(self._dps_clip(8.0))
        model += translate([acc_x + 200, 180, 0])(self._dps_plug_holder())
        model += translate([acc_x + 300, 0, 0])(self._dps_highway_section(200.0))
        # Mixon corner risers
        model += translate([acc_x + 300, 250, 0])(
            self._mixon_corner_riser(is_rear=False, mirror_x=False))
        model += translate([acc_x + 400, 250, 0])(
            self._mixon_corner_riser(is_rear=True, mirror_x=False))

        return model

    # ==================================================================
    # PIECES 3D IMPRIMABLES (PLA blanc)
    # ==================================================================
    def _cable_grommet(self):
        """Passe-cable snap-in diametre 30mm (PLA blanc)."""
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
        """Plaque logo or pour le couvercle du case."""
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

        # Logo en relief or
        logo = logo_3d(width=min(160, pw * 0.8), height=2.0, quality='normal')
        plate += translate([pw / 2, ph / 2, pt])(
            color(self._C['gold'])(logo)
        )

        # Trous de fixation
        for lx in [15, pw - 15]:
            plate -= translate([lx, ph / 2, -0.5])(
                cylinder(d=4.3, h=pt + 1, _fn=20)
            )

        return color(self._C['gold'])(plate)

    def _corner_protector(self):
        """Protection de coin PLA blanc pour case en contreplaque."""
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

        return color(self._C['pla'])(corner)

    def _corner_reinforcement(self):
        """Plaque de renfort coin — specifique White & Gold (remplace latch_reinforcement)."""
        cs = 50.0
        ct = 4.0
        corner_r = 6.0

        # Plaque en L pour renfort de coin
        plate = cube([cs, cs, ct])
        # Arrondi coin exterieur
        plate -= translate([cs, cs, -0.5])(
            cube([corner_r, corner_r, ct + 1])
        )
        plate += translate([cs - corner_r, cs - corner_r, 0])(
            cylinder(r=corner_r, h=ct, _fn=32)
        )

        # Evidement interieur (alleger)
        inner_offset = 12.0
        plate -= translate([inner_offset, inner_offset, -0.5])(
            cube([cs - inner_offset - 8, cs - inner_offset - 8, ct + 1])
        )

        # Trous de fixation M4 (3 trous en L)
        for pos in [(8, cs / 2), (cs / 2, 8), (cs * 0.7, cs * 0.7)]:
            plate -= translate([pos[0], pos[1], -0.5])(
                cylinder(d=4.3, h=ct + 1, _fn=20)
            )

        # Nervure de renfort diagonale
        rib_w = 3.0
        rib_h = 2.0
        rib = translate([0, 0, ct])(
            hull()(
                translate([5, 5, 0])(cylinder(d=rib_w, h=rib_h, _fn=16)),
                translate([cs - 10, cs - 10, 0])(cylinder(d=rib_w, h=rib_h, _fn=16)),
            )
        )
        plate += rib

        # Accent or sur le bord exterieur
        accent = translate([0, cs - 1.5, 0])(cube([cs, 1.5, ct]))
        accent += translate([cs - 1.5, 0, 0])(cube([1.5, cs, ct]))

        return color(self._C['pla'])(plate) + color(self._C['gold'])(accent)

    def _leg_keeper_pad(self):
        """Patin de maintien pour pieds ranges sous le case (PLA blanc)."""
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

        # Fentes pour sangles
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
        """Cloison interieure du case avec accent or sur le dessus."""
        p = self.params
        d = self._dims()
        div_t = p['divider_t']
        id_ = d['id']
        ih = d['ih']

        divider = cube([div_t, id_, ih])

        # Encoches doigts (3 en haut)
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

        # Accent or sur le dessus
        accent = translate([0, 0, ih - 1.5])(
            cube([div_t, id_, 1.5])
        )

        return color(self._C['pla'])(divider) + color(self._C['gold'])(accent)

    def _cable_clip(self):
        """Clip de routage cable blanc a clipser sur le bord du case."""
        clip_w = 20.0
        clip_d = 15.0
        clip_h = 12.0
        cable_d = 8.0

        clip = cube([clip_w, clip_d, clip_h])

        # Canal cable
        clip -= translate([clip_w / 2, -0.5, clip_h / 2])(
            rotate([-90, 0, 0])(
                cylinder(d=cable_d, h=clip_d + 1, _fn=24)
            )
        )

        # Fente d'ouverture
        clip -= translate([clip_w / 2 - cable_d / 4, -0.5, clip_h / 2])(
            cube([cable_d / 2, clip_d + 1, clip_h])
        )

        # Patte de fixation
        wall = 2.0
        clip_patte = cube([clip_w, wall, clip_h + 8])
        clip_patte += translate([0, wall, clip_h])(
            cube([clip_w, 4, 3])
        )
        clip += translate([0, clip_d, -8])(clip_patte)

        return color(self._C['pla'])(clip)

    def _power_strip_bracket(self):
        """Support multiprise blanc a fixer dans le bac."""
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

    def _lid_handle(self):
        """Poignee de prehension pour le couvercle amovible (blanc + or)."""
        hw = 140.0
        hh = 30.0
        hd = 20.0
        grip_d = 12.0
        wall = 3.0

        # Base de fixation blanche
        base = cube([hw, hd, wall])

        # Arche de prehension
        arch = hull()(
            translate([wall, hd / 2, wall])(
                rotate([0, 90, 0])(
                    cylinder(d=grip_d, h=hw - 2 * wall, _fn=24)
                )
            ),
            translate([wall, hd / 2, hh])(
                rotate([0, 90, 0])(
                    cylinder(d=grip_d, h=hw - 2 * wall, _fn=24)
                )
            ),
        )
        # Evidement interieur de l'arche
        arch -= hull()(
            translate([wall + 4, hd / 2, wall + 4])(
                rotate([0, 90, 0])(
                    cylinder(d=grip_d - 6, h=hw - 2 * wall - 8, _fn=24)
                )
            ),
            translate([wall + 4, hd / 2, hh - 2])(
                rotate([0, 90, 0])(
                    cylinder(d=grip_d - 6, h=hw - 2 * wall - 8, _fn=24)
                )
            ),
        )

        # Trous de fixation M4 (4 trous)
        for fx in [15, hw - 15]:
            for fy in [5, hd - 5]:
                base -= translate([fx, fy, -0.5])(
                    cylinder(d=4.3, h=wall + 1, _fn=20)
                )

        # Accent or sur le dessus de l'arche
        accent = translate([wall + 2, hd / 2 - 1, hh - 1])(
            cube([hw - 2 * wall - 4, 2, 1.5])
        )

        return color(self._C['pla'])(base + arch) + color(self._C['gold'])(accent)

    def _lid_alignment_pin(self):
        """Pin d'alignement couvercle/bac (4 necessaires, PLA blanc)."""
        p = self.params
        pin_d = p['lid_pin_d']
        pin_h = p['lid_pin_h']
        base_d = pin_d + 8
        base_h = 3.0

        # Base elargie
        pin = cylinder(d=base_d, h=base_h, _fn=32)

        # Pin cylindrique avec leger conique pour insertion facile
        pin += translate([0, 0, base_h])(
            cylinder(d1=pin_d, d2=pin_d - 1, h=pin_h, _fn=24)
        )

        # Trou de vis central M3
        pin -= translate([0, 0, -0.5])(
            cylinder(d=3.3, h=base_h + pin_h + 1, _fn=20)
        )

        # Fraisage tete de vis
        pin -= translate([0, 0, -0.5])(
            cylinder(d=6, h=2.5, _fn=20)
        )

        return color(self._C['pla'])(pin)

    # ==================================================================
    # MIXON CORNER RISERS — Coins sureleves pour Reloop Mixon 8 Pro
    # ==================================================================
    # Concept : 4 coins en L qui surelement la platine de 15mm.
    #   - Espace sous la platine pour cable routing
    #   - Platine avancee (mini-jack casque accessible devant)
    #   - En transport, platine touche presque la mousse du couvercle
    #   - Fixation Dual Lock sur le plancher du bac
    # Recherche multi-IA : Gemini (specs) + Groq (calcul hauteur) — 17/03/2026
    # ==================================================================

    def _mixon_corner_riser(self, is_rear=True, mirror_x=False):
        """Coin sureleve pour Mixon 8 Pro.

        Args:
            is_rear: True = coin arriere (levre sur 2 bords), False = coin avant
                     (levre cote seulement, pas devant = acces mini-jack)
            mirror_x: True = coin droit (miroir en X)
        """
        # Parametres coin
        grip_x = 60.0      # Longueur le long du bord X (lateral) du Mixon
        grip_y = 50.0      # Longueur le long du bord Y (avant/arriere)
        plat_inset = 18.0   # Le plateau depasse sous le Mixon
        wall_t = 3.2        # Epaisseur paroi (8 perimetres @ 0.4mm)
        lip_h = 8.0         # Hauteur levre de retention
        lip_t = 3.0         # Epaisseur levre
        base_t = 3.0        # Epaisseur base (pour Dual Lock)
        riser_h = 15.0      # Hauteur du riser (validee multi-IA)
        cr = 3.0            # Rayon coins arrondis (charte Prestige)
        cable_slot_w = 12.0  # Passage cable sous la platine
        cable_slot_h = 10.0
        groove_d = 0.5       # Rainure accent or
        groove_w = 0.8

        total_h = base_t + riser_h + lip_h

        # -- Base plate (assise sur le plancher du bac) --
        base = rounded_box(grip_x, grip_y, base_t, cr)

        # -- Piliers verticaux (les montants du riser) --
        # Pilier exterieur X (le long du bord lateral du Mixon)
        pillar_x = translate([0, 0, base_t])(
            cube([wall_t, grip_y, riser_h])
        )
        # Pilier exterieur Y (le long du bord avant/arriere)
        pillar_y = translate([0, 0, base_t])(
            cube([grip_x, wall_t, riser_h])
        )
        # Le pilier Y est cote arriere du coin (y=grip_y-wall_t) pour rear,
        # cote avant (y=0) pour front
        if is_rear:
            pillar_y = translate([0, grip_y - wall_t, base_t])(
                cube([grip_x, wall_t, riser_h])
            )
        else:
            pillar_y = translate([0, 0, base_t])(
                cube([grip_x, wall_t, riser_h])
            )

        # Le pilier X est toujours cote exterieur (x=0)
        pillar_x = translate([0, 0, base_t])(
            cube([wall_t, grip_y, riser_h])
        )

        # Renfort diagonal (gusset) pour rigidite
        gusset_size = 12.0
        gusset = hull()(
            translate([wall_t, 0, base_t])(cube([0.1, wall_t, riser_h])),
            translate([wall_t, 0, base_t])(cube([gusset_size, wall_t, 0.1]))
        )
        if is_rear:
            gusset_y = hull()(
                translate([0, grip_y - wall_t, base_t])(
                    cube([wall_t, 0.1, riser_h])
                ),
                translate([0, grip_y - wall_t - gusset_size, base_t])(
                    cube([wall_t, gusset_size, 0.1])
                )
            )
        else:
            gusset_y = hull()(
                translate([0, wall_t, base_t])(cube([wall_t, 0.1, riser_h])),
                translate([0, wall_t, base_t])(cube([wall_t, gusset_size, 0.1]))
            )

        # -- Plateau (ou le Mixon repose) --
        plat_z = base_t + riser_h
        # Plateau en L : bande le long de X + bande le long de Y
        plat_band_x = translate([0, 0, plat_z])(
            cube([grip_x, plat_inset, wall_t])
        )
        if is_rear:
            plat_band_x = translate([0, grip_y - plat_inset, plat_z])(
                cube([grip_x, plat_inset, wall_t])
            )

        plat_band_y = translate([0, 0, plat_z])(
            cube([plat_inset, grip_y, wall_t])
        )

        # -- Levre de retention (empeche le Mixon de glisser) --
        # Levre sur le bord X exterieur (toujours presente)
        lip_x = translate([0, 0, plat_z + wall_t])(
            cube([lip_t, grip_y, lip_h])
        )

        # Levre sur le bord Y (seulement pour coin arriere)
        lip_y = union()
        if is_rear:
            lip_y = translate([0, grip_y - lip_t, plat_z + wall_t])(
                cube([grip_x, lip_t, lip_h])
            )

        # -- Canal passage cable dans la base --
        # Ouverture sur le cote interieur pour laisser passer les cables
        cable_cut = translate([grip_x - cable_slot_w - 5, wall_t + 2,
                              -0.1])(
            cube([cable_slot_w, grip_y - 2 * wall_t - 2, cable_slot_h])
        )

        # -- Rainures accent or --
        grooves = union()
        # Sur le haut de la levre X
        grooves += translate([-0.1, cr, plat_z + wall_t + lip_h - groove_d])(
            cube([groove_w + 0.1, grip_y - 2 * cr, groove_d + 0.1])
        )
        # Sur le bord du plateau
        grooves += translate([cr, -0.1 if not is_rear else grip_y - groove_w,
                             plat_z - groove_d])(
            cube([grip_x - 2 * cr, groove_w + 0.1, groove_d + 0.1])
        )

        # -- Gravure DPS sur la levre --
        dps_text = linear_extrude(height=0.6 + 0.1)(
            text("DPS", size=4, font=DEFAULT_TEXT_FONT,
                 halign="center", valign="center", _fn=32)
        )
        dps_engrave = translate([-0.1, grip_y / 2,
                                plat_z + wall_t + lip_h / 2])(
            rotate([0, -90, 0])(rotate([0, 0, 90])(dps_text))
        )

        # Assemblage
        model = base + pillar_x + pillar_y + gusset + gusset_y
        model += plat_band_x + plat_band_y
        model += lip_x + lip_y
        model -= cable_cut
        model -= grooves
        model -= dps_engrave

        # Miroir si coin droit
        if mirror_x:
            model = mirror([1, 0, 0])(model)

        return color(self._C['pla'])(model)

    def _mixon_risers_assembly(self):
        """Les 4 coins risers positionnes autour du Mixon dans le bac."""
        d = self._dims()
        wt = d['wt']

        # Position Mixon AVANCEE (sureleve = peut aller plus pres du bord avant)
        mx_x = self.params['padding']
        mx_y = 10.0  # Avance (au lieu de ~39.5mm centre)

        grip_x = 60.0
        grip_y = 50.0

        risers = union()

        # Coin avant-gauche (pas de levre devant = acces mini-jack)
        risers += translate([wt + mx_x, wt + mx_y, wt])(
            self._mixon_corner_riser(is_rear=False, mirror_x=False)
        )
        # Coin avant-droit
        risers += translate([wt + mx_x + MIXON8_W, wt + mx_y, wt])(
            self._mixon_corner_riser(is_rear=False, mirror_x=True)
        )
        # Coin arriere-gauche (levre sur 2 bords)
        risers += translate([wt + mx_x, wt + mx_y + MIXON8_D - grip_y, wt])(
            self._mixon_corner_riser(is_rear=True, mirror_x=False)
        )
        # Coin arriere-droit
        risers += translate([wt + mx_x + MIXON8_W,
                            wt + mx_y + MIXON8_D - grip_y, wt])(
            self._mixon_corner_riser(is_rear=True, mirror_x=True)
        )

        # Fantome Mixon sureleve (pour visualisation)
        riser_h = 15.0
        base_t = 3.0
        plat_t = 3.2
        mixon_z = wt + base_t + riser_h + plat_t
        risers += color([0.9, 0.1, 0.1, 0.25])(
            translate([wt + mx_x, wt + mx_y, mixon_z])(
                cube([MIXON8_W, MIXON8_D, MIXON8_H])
            )
        )

        return risers

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
            frame += cube([wall, fd, frame_h])
            frame += cube([fw, wall, frame_h])
            frame += translate([0, fd - wall, 0])(cube([fw, wall, frame_h]))
            frame += translate([fw - 3, fd / 2 - 10, 0])(cube([6, 20, frame_h]))
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
            wx = (fw - WOLFMIX_W) / 2
            wy = 10.0
            frame -= translate([wx, wy, -1])(
                cube([WOLFMIX_W, WOLFMIX_D, frame_h + 2])
            )
            tx = (fw - TBONE_W) / 2
            ty = wy + WOLFMIX_D + 10
            frame -= translate([tx, ty, -1])(
                cube([TBONE_W, TBONE_D, frame_h + 2])
            )
            frame += cube([wall, fd, frame_h])
            frame += translate([fw - wall, 0, 0])(cube([wall, fd, frame_h]))
            frame += cube([fw, wall, frame_h])
            frame += translate([0, fd - wall, 0])(cube([fw, wall, frame_h]))
            return color(self._C['pla'])(frame)

        else:  # 'lid' — mousse de protection transport dans le couvercle
            fw = min(215.0, d['iw'] / 2 + 30)
            fd = min(205.0, d['id'] / 2 + 30)
            frame = cube([fw, fd, frame_h])
            # Empreinte rectangulaire simple (protection surfaces)
            inset = 15.0
            frame -= translate([inset, inset, -1])(
                cube([fw - 2 * inset, fd - 2 * inset, frame_h + 2])
            )
            frame += cube([wall, fd, frame_h])
            frame += translate([fw - wall, 0, 0])(cube([wall, fd, frame_h]))
            frame += cube([fw, wall, frame_h])
            frame += translate([0, fd - wall, 0])(cube([fw, wall, frame_h]))
            return color(self._C['pla'])(frame)

    # ==================================================================
    # PROFILS LASER DXF (2D pour decoupe)
    # ==================================================================
    def _case_base_dxf(self):
        """Patron 2D depliant du bac pour decoupe laser contreplaque."""
        d = self._dims()
        ew, ed = d['ew'], d['ed']
        tray_h = d['tray_h']

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

        # Trous pour pins d'alignement couvercle (4 coins)
        pin_d = self.params['lid_pin_d']
        pin_inset = 25.0
        for px in [pin_inset, ew - pin_inset]:
            for py in [pin_inset, ed - pin_inset]:
                model -= translate([px, py, 0])(
                    circle(d=pin_d + 0.5, _fn=24)
                )

        return linear_extrude(height=0.1)(model)

    def _case_lid_dxf(self):
        """Patron 2D depliant du couvercle amovible."""
        d = self._dims()
        ew, ed = d['ew'], d['ed']
        lid_h = d['lid_h']

        model = union()
        model += square([ew, ed])
        model += translate([0, -lid_h - 5, 0])(square([ew, lid_h]))
        model += translate([0, ed + 5, 0])(square([ew, lid_h]))
        model += translate([-lid_h - 5, 0, 0])(square([lid_h, ed]))
        model += translate([ew + 5, 0, 0])(square([lid_h, ed]))

        # Trous pour pins d'alignement (4 coins)
        pin_d = self.params['lid_pin_d']
        pin_inset = 25.0
        for px in [pin_inset, ew - pin_inset]:
            for py in [pin_inset, ed - pin_inset]:
                model -= translate([px, py, 0])(
                    circle(d=pin_d, _fn=24)
                )

        return linear_extrude(height=0.1)(model)

    def _divider_dxf(self):
        """Patron 2D de la cloison interieure."""
        d = self._dims()
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

    # ==================================================================
    # CABLE MANAGEMENT — Prestige Cable Highway
    # ==================================================================
    # 3 types de pieces : clips KLAMMA, goulotte highway, berceaux transfo
    # Fixation Dual Lock. Materiau PLA blanc.
    # Zones : A (highway arriere), B (clips droit), C (clips sortie arriere)
    # ==================================================================

    def _dps_clip(self, cable_d=8.0):
        """Clip verrouillable DPS (KLAMMA modifie) pour un diametre cable donne."""
        wt = 2.0
        length = 20.0
        bw, bd, bt = 25.0, 20.0, 2.5
        cr = 3.0
        opening = 80.0
        half_a = opening / 2
        lip_t = 0.8

        inner_r = cable_d / 2 + 0.2
        outer_r = inner_r + wt
        cut = outer_r + 2

        # Anneau C
        ring = cylinder(r=outer_r, h=length, _fn=64)
        ring -= cylinder(r=inner_r, h=length + 0.2, _fn=64)
        # Ouverture
        cut_block = translate([0, 0, -0.1])(cube([cut, cut, length + 0.4]))
        ring -= rotate([0, 0, 90 - half_a])(cut_block)
        ring -= rotate([0, 0, 90 + half_a])(mirror([1, 0, 0])(cut_block))

        # Levres snap-fit
        lip_cyl = cylinder(r=inner_r + lip_t, h=length, _fn=64) - \
                  cylinder(r=inner_r, h=length + 0.2, _fn=64)
        lip_sec = 12
        for side_a in [90 - half_a, 90 + half_a]:
            mask_a = translate([0, 0, -0.1])(cube([cut, cut, length + 0.4]))
            mask_b = translate([0, 0, -0.1])(cube([cut, cut, length + 0.4]))
            if side_a == 90 - half_a:
                k1 = rotate([0, 0, side_a - lip_sec])(mask_a)
                k2 = rotate([0, 0, side_a])(mirror([1, 0, 0])(mask_b))
            else:
                k1 = rotate([0, 0, side_a])(mask_a)
                k2 = rotate([0, 0, side_a + lip_sec])(mirror([1, 0, 0])(mask_b))
            ring += lip_cyl & k1 & k2

        # Base Dual Lock
        base = translate([-bw / 2, -bd / 2, 0])(
            rounded_box(bw, bd, bt, cr)
        )
        # Rainures accent or
        base -= translate([-bw / 2 + cr, -bd / 2 - 0.1, bt - 0.5])(
            cube([bw - 2 * cr, 0.9, 0.6])
        )
        base -= translate([-bw / 2 + cr, bd / 2 - 0.8, bt - 0.5])(
            cube([bw - 2 * cr, 0.9, 0.6])
        )

        clip = base + translate([0, 0, bt])(ring)
        return color(self._C['pla'])(clip)

    def _dps_highway_section(self, length=200.0):
        """Section de goulotte U pour cable highway."""
        cw, ch = 30.0, 12.0
        wt, bt = 2.0, 2.5
        tw = cw + 2 * wt
        th = ch + bt
        cl = 8.0    # connecteur
        cc = 0.3    # jeu

        # Corps U
        body = cube([tw, length, th])
        body -= translate([wt, -0.1, bt])(cube([cw, length + 0.2, ch + 0.1]))

        # Tenon male (+Y)
        body += translate([wt + cc, length, bt + cc])(
            cube([cw - 2 * cc, cl, ch - 2 * cc])
        )
        # Mortaise femelle (-Y)
        body -= translate([wt, -cl, bt])(cube([cw, cl + 0.1, ch]))

        # Encoches laterales (2 entrees cable sur paroi gauche)
        slot_w = 10.0
        spacing = length / 3
        for i in range(2):
            y = spacing * (i + 1) - slot_w / 2
            body -= translate([-0.1, y, bt])(cube([wt + 0.2, slot_w, ch + 0.1]))

        # Rainures accent or (bord superieur)
        body -= translate([-0.1, 3, th - 0.5])(cube([0.9, length - 6, 0.6]))
        body -= translate([tw - 0.8, 3, th - 0.5])(cube([0.9, length - 6, 0.6]))

        # Gravure DPS face droite
        dps = linear_extrude(height=0.9)(
            text("DPS", size=6, font=DEFAULT_TEXT_FONT,
                 halign="center", valign="center", _fn=32)
        )
        body -= translate([tw + 0.1, length / 2, th / 2])(
            rotate([0, -90, 0])(rotate([0, 0, 90])(dps))
        )

        return color(self._C['pla'])(body)

    def _dps_plug_holder(self):
        """Berceau pour bloc d'alimentation / transformateur."""
        pw, pd, ph = 45.0, 30.0, 25.0
        cl = 1.0
        wt, bt = 2.5, 3.0
        cr = 3.0
        iw = pw + 2 * cl
        id_ = pd + 2 * cl
        tw = iw + 2 * wt
        td = id_ + 2 * wt
        wall_h = ph * 0.6
        th = bt + wall_h

        # Base + parois
        body = rounded_box(tw, td, bt, cr)
        body += translate([0, 0, bt])(cube([wt, td, wall_h]))
        body += translate([tw - wt, 0, bt])(cube([wt, td, wall_h]))
        body += translate([0, td - wt, bt])(cube([tw, wt, wall_h]))
        # Paroi avant avec ouverture cable
        cable_w = 15.0
        body += translate([0, 0, bt])(cube([tw / 2 - cable_w / 2, wt, wall_h]))
        body += translate([tw / 2 + cable_w / 2, 0, bt])(
            cube([tw / 2 - cable_w / 2, wt, wall_h])
        )

        # Pattes de retention (4 coins)
        pt_t, pt_w = 2.0, 10.0
        ret_h, lip = 8.0, 3.0
        eps = 0.5
        for fx in [0, 1]:
            for fy in [0, 1]:
                px = wt if fx == 0 else tw - wt - pt_t
                py = wt if fy == 0 else td - wt - pt_w
                body += translate([px, py, th - eps])(
                    cube([pt_t, pt_w, ret_h + eps])
                )
                lx = 0 if fx == 0 else -lip
                body += translate([px + lx, py, th - eps + ret_h])(
                    cube([lip + pt_t, pt_w, pt_t])
                )

        # Rainures accent or
        body -= translate([-0.1, cr, th - 0.5])(
            cube([0.9, td - 2 * cr, 0.6])
        )
        body -= translate([tw - 0.8, cr, th - 0.5])(
            cube([0.9, td - 2 * cr, 0.6])
        )

        return color(self._C['pla'])(body)

    def _cable_management(self):
        """Systeme complet cable management positionne dans le flycase.
        Retourne la geometrie a ajouter aux vues deployed/interior."""
        d = self._dims()
        wt = d['wt']
        iw, id_ = d['iw'], d['id']
        foam = self.params['foam_t']
        pad = self.params['padding']

        mx_x, mx_y, mx_z = d['mx']
        wx, wy, wz = d['wm']
        tx, ty, tz = d['tb']

        model = union()

        # Offset : tout est relatif a l'interieur du bac (wt, wt, wt)
        # La mousse est a z=0 (relatif interieur), appareils a z=foam

        # ============================================================
        # ZONE A — Cable Highway (3 sections le long paroi arriere)
        # Entre les appareils et la paroi arriere, sur la mousse
        # ============================================================
        hw_w = 34.0   # 30 + 2*2
        hw_h = 14.5   # 12 + 2.5
        # Y position : juste devant la paroi arriere, apres les appareils
        hw_y = id_ - 60  # ~60mm de la paroi arriere (espace power strip)

        # 3 sections de 200mm, orientees le long de X
        for i, x_start in enumerate([50, 260, 470]):
            model += translate([wt + x_start, wt + hw_y, wt + foam])(
                rotate([0, 0, 0])(
                    # La highway est modelee X=largeur, Y=longueur, Z=haut
                    # On veut longueur le long de X du flycase
                    rotate([0, 0, -90])(
                        translate([0, 0, 0])(self._dps_highway_section(200.0))
                    )
                )
            )

        # ============================================================
        # ZONE B — 2 clips XLR Shure (paroi droite)
        # ============================================================
        clip_z = wt + foam + 5

        # Clip 1 pres du Shure
        model += translate([wt + iw - 30, wt + ty + 30, clip_z])(
            rotate([0, 0, 90])(self._dps_clip(8.0))
        )
        # Clip 2 plus bas
        model += translate([wt + iw - 30, wt + ty + 90, clip_z])(
            rotate([0, 0, 90])(self._dps_clip(8.0))
        )

        # ============================================================
        # ZONE C — 2 clips sortie arriere (USB + DMX)
        # ============================================================
        # Clip USB Mixon
        model += translate([wt + mx_x + MIXON8_W / 2, wt + id_ - 25, clip_z])(
            self._dps_clip(5.0)
        )
        # Clip DMX WolfMix
        model += translate([wt + wx + WOLFMIX_W / 2, wt + id_ - 25, clip_z])(
            self._dps_clip(8.0)
        )

        # ============================================================
        # PLUG HOLDERS — Berceaux transformateurs
        # ============================================================
        ph_z = wt + foam

        # Holder transfo Mixon (entre Mixon et highway)
        model += translate([wt + mx_x + MIXON8_W - 60, wt + hw_y - 45, ph_z])(
            self._dps_plug_holder()
        )
        # Holder transfo Shure (zone droite)
        model += translate([wt + wx + 10, wt + ty - 50, ph_z])(
            self._dps_plug_holder()
        )

        return model

    # ==================================================================
    # BUILD DISPATCH
    # ==================================================================
    def build(self):
        part = self.params['export_part']

        # --- Vues (PAS de lid_open car couvercle amovible) ---
        views = {
            'deployed': self._deployed_view,
            'transport': self._transport_view,
            'interior_layout': self._interior_layout,
            'exploded': self._exploded_view,
        }

        # --- Accessoires 3D (PLA blanc) ---
        accessories = {
            'cable_grommet': self._cable_grommet,
            'logo_plate': self._logo_plate,
            'corner_protector': self._corner_protector,
            'corner_reinforcement': self._corner_reinforcement,
            'leg_keeper_pad': self._leg_keeper_pad,
            'divider_wall': self._divider_wall,
            'cable_clip': self._cable_clip,
            'power_strip_bracket': self._power_strip_bracket,
            'lid_handle': self._lid_handle,
            'lid_alignment_pin': self._lid_alignment_pin,
            # Cable management Prestige
            'dps_cable_clip_small': lambda: self._dps_clip(5.0),
            'dps_cable_clip_large': lambda: self._dps_clip(8.0),
            'dps_cable_highway': lambda: self._dps_highway_section(200.0),
            'dps_plug_holder': self._dps_plug_holder,
            # Mixon corner risers
            'mixon_riser_front': lambda: self._mixon_corner_riser(
                is_rear=False, mirror_x=False),
            'mixon_riser_rear': lambda: self._mixon_corner_riser(
                is_rear=True, mirror_x=False),
            'mixon_risers_assembly': self._mixon_risers_assembly,
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
        }

        all_dispatch = {**views, **accessories, **foam_templates, **laser}
        return all_dispatch.get(part, self._deployed_view)()


if __name__ == "__main__":
    fwg = FlycaseWhiteGold()
    d = fwg._dims()
    print(f"Case ext: {d['ew']:.0f} x {d['ed']:.0f} x {d['total_h']:.0f} mm")
    print(f"Bac: {d['tray_h']:.0f} mm / Couvercle amovible: {d['lid_h']:.0f} mm")
    print(f"Interieur: {d['iw']:.0f} x {d['id']:.0f} x {d['ih']:.0f} mm")
    print(f"Hauteur travail: {fwg.params['working_height']:.0f} mm")
    print(f"Pieds: {fwg.params['leg_length']:.0f} mm (Penn Elcom 9967 blanc)")
    print(f"Mixon @ x={d['mx'][0]:.0f}, y={d['mx'][1]:.0f}")
    print(f"WolfMix @ x={d['wm'][0]:.0f}, y={d['wm'][1]:.0f}")
    print(f"t.bone @ x={d['tb'][0]:.0f}, y={d['tb'][1]:.0f}")
    print(f"Export parts: {len(fwg.param_schema()['export_part']['options'])}")
    print("Design: White case + Gold hardware + Black foam interior")
    print("Lid: REMOVABLE (lift-off, no hinge, no gas struts)")
    fwg.save_scad()
