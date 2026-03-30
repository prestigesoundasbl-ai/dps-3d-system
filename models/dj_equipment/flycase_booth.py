"""
Flycase DJ Booth - 3 Compartiments
===================================
Flycase modulaire avec emplacements pour :
  - Reloop Mixon 8 Pro (657 x 391 x 68 mm)
  - WolfMix W1 (195 x 220 x 62 mm)
  - t.bone Free Solo HT 1.8 GHz (212 x 160 x 44 mm)

Le flycase est concu pour etre imprime en sections assemblables
car les dimensions depassent le volume d'impression FDM standard.

Structure : Base tray + cloisons + couvercle
Le tout s'emboite et se fixe par vis M5.

export_part:
  - "base_left"      : Moitie gauche de la base (Mixon cote gauche)
  - "base_right"     : Moitie droite de la base (Mixon cote droit)
  - "tray_wolfmix"   : Compartiment WolfMix (lateral)
  - "tray_hf"        : Compartiment t.bone HF (lateral)
  - "divider"        : Cloison centrale entre Mixon et compartiments lateraux
  - "lid_left"       : Couvercle gauche
  - "lid_right"      : Couvercle droite
  - "lid_side"       : Couvercle lateral (couvre WolfMix + HF)
  - "full_assembly"  : Visualisation complete (non imprimable, reference)
"""
from solid2 import *
from ..base import ParametricModel
from ..utils import rounded_box, brand_text, mounting_hole
from ..brand import (
    DEFAULT_WALL_THICKNESS, DEFAULT_CORNER_RADIUS,
    BRAND_NAME, COLOR_GOLD, DEFAULT_TEXT_FONT
)

# ========================================================================
# Dimensions des appareils (mm)
# ========================================================================
MIXON8_W = 657.0    # Largeur
MIXON8_D = 391.0    # Profondeur
MIXON8_H = 68.0     # Hauteur

WOLFMIX_W = 195.0
WOLFMIX_D = 220.0
WOLFMIX_H = 62.0

TBONE_W = 212.0
TBONE_D = 160.0
TBONE_H = 44.0


class FlycaseBooth(ParametricModel):
    """Flycase DJ Booth modulaire a 3 compartiments."""

    def __init__(self, **params):
        super().__init__("flycase_booth", **params)

    def default_params(self):
        return {
            'wall_thickness': 4.0,          # Epaisseur paroi (mm)
            'base_thickness': 5.0,          # Epaisseur fond (mm)
            'padding': 8.0,                 # Mousse/jeu autour des appareils
            'corner_radius': 3.0,           # Rayon des coins
            'lid_height': 30.0,             # Hauteur du couvercle
            'lid_overlap': 5.0,             # Chevauchement couvercle/base
            'divider_thickness': 4.0,       # Epaisseur cloison
            'handle_width': 120.0,          # Largeur poignee
            'handle_depth': 25.0,           # Profondeur poignee
            'use_logo': True,               # Gravure logo sur couvercle
            'export_part': 'full_assembly', # Piece a exporter
        }

    def param_schema(self):
        return {
            'wall_thickness': {
                'type': 'float', 'min': 2.5, 'max': 8.0,
                'unit': 'mm', 'description': 'Epaisseur des parois',
            },
            'base_thickness': {
                'type': 'float', 'min': 3.0, 'max': 10.0,
                'unit': 'mm', 'description': 'Epaisseur du fond',
            },
            'padding': {
                'type': 'float', 'min': 3.0, 'max': 15.0,
                'unit': 'mm', 'description': 'Jeu autour des appareils (mousse)',
            },
            'corner_radius': {
                'type': 'float', 'min': 0.0, 'max': 10.0,
                'unit': 'mm', 'description': 'Rayon des coins arrondis',
            },
            'lid_height': {
                'type': 'float', 'min': 15.0, 'max': 50.0,
                'unit': 'mm', 'description': 'Hauteur du couvercle',
            },
            'export_part': {
                'type': 'string',
                'options': [
                    'base_left', 'base_right',
                    'tray_wolfmix', 'tray_hf',
                    'divider',
                    'lid_left', 'lid_right', 'lid_side',
                    'full_assembly',
                ],
                'description': 'Piece a exporter pour impression',
            },
        }

    def _dims(self):
        """Calcule les dimensions internes et externes du flycase."""
        p = self.params
        wall = p['wall_thickness']
        base_t = p['base_thickness']
        pad = p['padding']
        div = p['divider_thickness']

        # Espace interne pour le Mixon (compartiment principal)
        mixon_slot_w = MIXON8_W + 2 * pad
        mixon_slot_d = MIXON8_D + 2 * pad
        mixon_slot_h = MIXON8_H + pad  # Pas de pad en bas (mousse separee)

        # Espace interne lateral (WolfMix + HF empiles verticalement)
        # Les deux sont cote a cote dans le compartiment lateral
        side_slot_w = max(WOLFMIX_W, TBONE_W) + 2 * pad
        side_slot_d = max(WOLFMIX_D + TBONE_D + pad, mixon_slot_d)
        side_slot_h = max(WOLFMIX_H, TBONE_H) + pad

        # Dimensions externes totales
        total_w = mixon_slot_w + div + side_slot_w + 2 * wall
        total_d = max(mixon_slot_d, side_slot_d) + 2 * wall
        total_h = max(mixon_slot_h, side_slot_h) + base_t

        return {
            'mixon_slot': (mixon_slot_w, mixon_slot_d, mixon_slot_h),
            'side_slot': (side_slot_w, side_slot_d, side_slot_h),
            'total': (total_w, total_d, total_h),
            'wolfmix_slot': (WOLFMIX_W + 2*pad, WOLFMIX_D + 2*pad, WOLFMIX_H + pad),
            'tbone_slot': (TBONE_W + 2*pad, TBONE_D + 2*pad, TBONE_H + pad),
        }

    def _base_tray(self):
        """Construit le bac de base complet (avant decoupe en sections)."""
        p = self.params
        wall = p['wall_thickness']
        base_t = p['base_thickness']
        pad = p['padding']
        div = p['divider_thickness']
        r = p['corner_radius']
        dims = self._dims()

        tw, td, th = dims['total']
        mw, md, mh = dims['mixon_slot']
        sw, sd, sh = dims['side_slot']

        # Coque exterieure
        outer = rounded_box(tw, td, th, r)

        # Evidement interieur Mixon (compartiment gauche)
        mixon_cavity = translate([wall, wall, base_t])(
            cube([mw, md, mh + 1])
        )

        # Evidement interieur lateral (compartiment droite)
        side_x = wall + mw + div
        side_cavity = translate([side_x, wall, base_t])(
            cube([sw, md, sh + 1])
        )

        # Cavite WolfMix (dans le compartiment lateral, devant)
        wolfmix_cw, wolfmix_cd, wolfmix_ch = dims['wolfmix_slot']
        wolfmix_cut = translate([side_x + (sw - wolfmix_cw)/2, wall + pad/2, base_t])(
            cube([wolfmix_cw, wolfmix_cd, wolfmix_ch + 0.5])
        )

        # Cavite t.bone (dans le compartiment lateral, derriere)
        tbone_cw, tbone_cd, tbone_ch = dims['tbone_slot']
        tbone_y = wall + wolfmix_cd + pad
        tbone_cut = translate([side_x + (sw - tbone_cw)/2, tbone_y, base_t])(
            cube([tbone_cw, tbone_cd, tbone_ch + 0.5])
        )

        # Trous de ventilation (4 trous oblongs sous le Mixon)
        vent_holes = union()
        vent_w = 60.0
        vent_d = 8.0
        for i in range(4):
            vx = wall + mw * (i + 1) / 5 - vent_w / 2
            vy = wall + md / 2 - vent_d / 2
            vent_holes += translate([vx, vy, -0.5])(
                hull()(
                    cylinder(d=vent_d, h=base_t + 1, _fn=24),
                    translate([vent_w, 0, 0])(
                        cylinder(d=vent_d, h=base_t + 1, _fn=24)
                    ),
                )
            )

        # Trous de fixation M5 dans les coins (pour vis de couvercle)
        bolt_d = 5.3
        bolt_inset = 12.0
        bolt_holes = union()
        for bx in [bolt_inset, tw - bolt_inset]:
            for by in [bolt_inset, td - bolt_inset]:
                bolt_holes += translate([bx, by, -0.5])(
                    cylinder(d=bolt_d, h=th + 1, _fn=24)
                )
        # Vis centrales pour assemblage des deux moities
        mid_x = mw + wall
        for by in [bolt_inset, td / 2, td - bolt_inset]:
            bolt_holes += translate([mid_x, by, -0.5])(
                cylinder(d=bolt_d, h=th + 1, _fn=24)
            )

        tray = outer - mixon_cavity - side_cavity - vent_holes - bolt_holes

        return tray

    def _divider(self):
        """Cloison entre compartiment Mixon et compartiment lateral."""
        p = self.params
        wall = p['wall_thickness']
        base_t = p['base_thickness']
        div = p['divider_thickness']
        dims = self._dims()
        tw, td, th = dims['total']
        mw, md, mh = dims['mixon_slot']

        # Cloison verticale
        divider_h = th - base_t
        divider = translate([wall + mw, wall, base_t])(
            cube([div, td - 2 * wall, divider_h])
        )

        # Encoches d'alignement en haut (pour le couvercle)
        notch_w = 3.0
        notch_h = 5.0
        notch_d = 20.0
        for i in range(3):
            ny = wall + (td - 2*wall) * (i + 1) / 4 - notch_d / 2
            divider += translate([wall + mw - notch_w/2, ny, th - notch_h])(
                cube([div + notch_w, notch_d, notch_h])
            )

        return divider

    def _lid_section(self, width, depth, height, with_logo=False):
        """Construit une section de couvercle."""
        p = self.params
        wall = p['wall_thickness']
        r = p['corner_radius']
        overlap = p['lid_overlap']

        # Coque exterieure du couvercle
        outer = rounded_box(width, depth, height, r)

        # Evidement interieur (le couvercle se pose par dessus)
        inner_margin = wall
        inner = translate([inner_margin, inner_margin, wall])(
            cube([
                width - 2 * inner_margin + 0.1,
                depth - 2 * inner_margin + 0.1,
                height,
            ])
        )

        # Rebord d'emboitement (descend dans la base)
        lip_w = wall - 0.4  # Jeu de 0.4mm
        lip = translate([inner_margin, inner_margin, -overlap])(
            cube([width - 2*inner_margin, depth - 2*inner_margin, overlap])
        )
        lip_inner = translate([inner_margin + lip_w, inner_margin + lip_w, -overlap - 0.1])(
            cube([
                width - 2*inner_margin - 2*lip_w,
                depth - 2*inner_margin - 2*lip_w,
                overlap + 0.2,
            ])
        )
        lip_shell = lip - lip_inner

        lid = outer - inner + lip_shell

        # Logo grave sur le couvercle
        if with_logo and p['use_logo']:
            logo = brand_text(
                "DJ PRESTIGE SOUND",
                size=min(12.0, width / 20),
                depth=1.2,
            )
            lid -= translate([width / 2, depth / 2, height - 0.8])(logo)

        # Poignee encastree
        hw = p['handle_width']
        hd = p['handle_depth']
        if hw < width - 2 * wall:
            handle_cutout = hull()(
                translate([width/2 - hw/2, depth/2 - hd/2, height - 3])(
                    cylinder(d=6, h=4, _fn=24)
                ),
                translate([width/2 + hw/2, depth/2 - hd/2, height - 3])(
                    cylinder(d=6, h=4, _fn=24)
                ),
                translate([width/2 + hw/2, depth/2 + hd/2, height - 3])(
                    cylinder(d=6, h=4, _fn=24)
                ),
                translate([width/2 - hw/2, depth/2 + hd/2, height - 3])(
                    cylinder(d=6, h=4, _fn=24)
                ),
            )
            lid -= handle_cutout

        # Trous de vis dans les coins du couvercle
        bolt_d = 5.3
        bolt_inset = 12.0
        for bx in [bolt_inset, width - bolt_inset]:
            for by in [bolt_inset, depth - bolt_inset]:
                lid -= translate([bx, by, -overlap - 0.5])(
                    cylinder(d=bolt_d, h=height + overlap + 1, _fn=24)
                )

        return lid

    def _ghost_equipment(self):
        """Fantomes transparents des appareils pour visualisation."""
        p = self.params
        wall = p['wall_thickness']
        base_t = p['base_thickness']
        pad = p['padding']
        div = p['divider_thickness']
        dims = self._dims()
        mw = dims['mixon_slot'][0]

        ghosts = union()

        # Mixon 8 Pro (rouge transparent)
        ghosts += color([1, 0, 0, 0.3])(
            translate([wall + pad, wall + pad, base_t])(
                cube([MIXON8_W, MIXON8_D, MIXON8_H])
            )
        )

        # WolfMix (vert transparent)
        side_x = wall + mw + div
        sw = dims['side_slot'][0]
        wolfmix_cw = dims['wolfmix_slot'][0]
        ghosts += color([0, 1, 0, 0.3])(
            translate([
                side_x + (sw - wolfmix_cw)/2 + pad,
                wall + pad,
                base_t,
            ])(
                cube([WOLFMIX_W, WOLFMIX_D, WOLFMIX_H])
            )
        )

        # t.bone HF (bleu transparent)
        tbone_cw = dims['tbone_slot'][0]
        tbone_y = wall + dims['wolfmix_slot'][1] + pad
        ghosts += color([0, 0, 1, 0.3])(
            translate([
                side_x + (sw - tbone_cw)/2 + pad,
                tbone_y + pad,
                base_t,
            ])(
                cube([TBONE_W, TBONE_D, TBONE_H])
            )
        )

        return ghosts

    def build(self):
        p = self.params
        part = p['export_part']
        dims = self._dims()
        tw, td, th = dims['total']
        mw = dims['mixon_slot'][0]
        sw = dims['side_slot'][0]
        wall = p['wall_thickness']
        div = p['divider_thickness']
        lid_h = p['lid_height']

        # ================================================================
        # Export par piece
        # ================================================================

        if part == 'base_left':
            # Moitie gauche de la base (compartiment Mixon gauche)
            base = self._base_tray()
            cut_x = wall + mw / 2
            cutter = translate([cut_x, -1, -1])(cube([tw, td + 2, th + 2]))
            return base - cutter

        elif part == 'base_right':
            # Moitie droite de la base (compartiment Mixon droit + lateral)
            base = self._base_tray()
            cut_x = wall + mw / 2
            cutter = translate([-1, -1, -1])(cube([cut_x + 1, td + 2, th + 2]))
            result = base - cutter
            # Re-centrer pour l'impression
            return translate([-cut_x, 0, 0])(result)

        elif part == 'tray_wolfmix':
            # Insert amovible pour le WolfMix
            return self._equipment_insert(
                WOLFMIX_W, WOLFMIX_D, WOLFMIX_H, "WOLFMIX"
            )

        elif part == 'tray_hf':
            # Insert amovible pour le t.bone HF
            return self._equipment_insert(
                TBONE_W, TBONE_D, TBONE_H, "HF RECEIVER"
            )

        elif part == 'divider':
            return self._divider()

        elif part == 'lid_left':
            lid_w = mw / 2 + wall
            return self._lid_section(lid_w, td, lid_h, with_logo=True)

        elif part == 'lid_right':
            lid_w = mw / 2 + div + sw + wall
            return self._lid_section(lid_w, td, lid_h, with_logo=True)

        elif part == 'lid_side':
            lid_w = sw + wall + div
            return self._lid_section(lid_w, td, lid_h)

        else:
            # full_assembly : visualisation complete
            return self._full_assembly()

    def _equipment_insert(self, eq_w, eq_d, eq_h, label=""):
        """Insert amovible pour un appareil (tray qui se depose dans le flycase)."""
        p = self.params
        pad = p['padding']
        wall = 2.5  # Paroi fine pour l'insert
        r = 2.0

        insert_w = eq_w + 2 * pad
        insert_d = eq_d + 2 * pad
        insert_h = eq_h + 5.0  # 5mm de bord au dessus de l'appareil

        # Coque de l'insert
        outer = rounded_box(insert_w, insert_d, insert_h, r)
        inner = translate([wall, wall, wall])(
            cube([insert_w - 2*wall, insert_d - 2*wall, insert_h])
        )
        insert = outer - inner

        # Decoupe forme de l'appareil dans la mousse (fond plat)
        # L'appareil repose sur le fond, centre
        eq_x = (insert_w - eq_w) / 2
        eq_y = (insert_d - eq_d) / 2

        # Biseaux sur les bords pour faciliter la prise
        finger_slot_w = 30.0
        finger_slot_h = 15.0
        for side_y in [0, insert_d]:
            insert -= translate([insert_w/2 - finger_slot_w/2, side_y - 5, insert_h - finger_slot_h])(
                cube([finger_slot_w, 10, finger_slot_h + 1])
            )

        # Label grave dans le fond
        if label:
            lbl = linear_extrude(height=0.8)(
                text(label, size=8, font=DEFAULT_TEXT_FONT,
                     halign="center", valign="center", _fn=48)
            )
            insert -= translate([insert_w/2, insert_d/2, -0.1])(lbl)

        return insert

    def _full_assembly(self):
        """Assemblage complet pour visualisation (non imprimable)."""
        p = self.params
        dims = self._dims()
        tw, td, th = dims['total']
        lid_h = p['lid_height']

        model = union()

        # Base complete
        model += color([0.2, 0.2, 0.2])(self._base_tray())

        # Cloison
        model += color([0.3, 0.3, 0.3])(self._divider())

        # Appareils fantomes
        model += self._ghost_equipment()

        # Couvercle (positionne au dessus, translucide)
        lid_full = self._lid_section(tw, td, lid_h, with_logo=True)
        model += color([0.15, 0.15, 0.15, 0.5])(
            translate([0, 0, th + 2])(lid_full)
        )

        return model


if __name__ == "__main__":
    # Test rapide : generer le SCAD de l'assemblage complet
    booth = FlycaseBooth()
    booth.save_scad()
    print(f"Dimensions totales: {booth._dims()['total']}")
