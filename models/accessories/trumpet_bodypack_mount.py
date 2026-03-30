"""
Trumpet Bodypack Mount — Support Sennheiser SK 100 G4 pour trompette

Systeme 2 pieces + Dual Lock 3M pour fixer un emetteur sans fil
directement sur la coulisse d'accord d'une trompette.

Piece A — Trumpet Clamp:
  - Double clamp C-ring sur les 2 tubes de la coulisse d'accord
  - Pont rigide avec surface Dual Lock 25x25mm
  - Vis M3 pour serrage (insert thermique)
  - Rainure pour bande caoutchouc (protection laque)
  - Gussets 12mm aux jonctions pont-clamp

Piece B — Bodypack Cradle:
  - Berceau en U aux dimensions du SK 100 G4 (82x64x24mm)
  - Decoupes: jack 3.5mm (droite), antenne (gauche), dessus ouvert
  - 2 fentes pour sangle velcro 20mm
  - Surface Dual Lock 25x25mm sous la base
  - Gravure "PRESTIGE" sur la paroi avant

Export parts: 'clamp', 'cradle', 'assembly', 'test_ring'
"""
import math
import sys
from solid2 import *
from ..base import ParametricModel

# L'assembly avec trompette fantome genere un arbre CSG profond
if sys.getrecursionlimit() < 3000:
    sys.setrecursionlimit(3000)
from ..brand import (
    BRAND_NAME_SHORT, DEFAULT_TEXT_DEPTH, DEFAULT_TEXT_FONT,
    DEFAULT_CORNER_RADIUS, COLOR_GOLD
)
from ..utils import rounded_box, brand_text, gusset_triangle


class TrumpetBodypackMount(ParametricModel):

    def __init__(self, **params):
        super().__init__("trumpet_bodypack_mount", **params)

    def default_params(self):
        return {
            # --- Clamp (Piece A) ---
            'tube_od': 14.0,              # Diametre ext tube coulisse (a mesurer)
            'tube_spacing': 27.0,         # Entre-axe des 2 tubes coulisse
            'clamp_wall': 3.2,            # Epaisseur paroi clamp (8 perimetres)
            'clamp_height': 20.0,         # Hauteur du clamp le long du tube
            'clamp_opening_angle': 55.0,  # Angle ouverture C-ring
            'fit_clearance': 0.2,         # Jeu tube-clamp
            'rubber_groove_depth': 1.2,   # Rainure pour bande caoutchouc
            'rubber_groove_width': 3.0,   # Largeur rainure caoutchouc
            'screw_diameter': 3.0,        # M3
            'screw_head_diameter': 5.5,   # Tete M3
            'nut_width': 5.5,             # M3 ecrou (plat a plat)
            'nut_height': 2.4,            # Hauteur ecrou M3
            'gusset_size': 12.0,          # Taille des renforts
            'dual_lock_size': 25.0,       # Surface Dual Lock (carre)

            # --- Cradle (Piece B) ---
            'bp_width': 64.0,             # Bodypack largeur
            'bp_depth': 24.0,             # Bodypack profondeur
            'bp_height': 82.0,            # Bodypack hauteur
            'cradle_clearance': 0.5,      # Jeu vibration
            'cradle_wall': 2.5,           # Epaisseur paroi berceau
            'cradle_wall_height': 15.0,   # Hauteur parois laterales
            'cradle_base_thickness': 3.0, # Epaisseur fond berceau
            'jack_cutout_width': 12.0,    # Largeur decoupe jack (cote droit)
            'jack_cutout_height': 10.0,   # Hauteur decoupe jack
            'antenna_cutout_width': 10.0, # Largeur decoupe antenne (cote gauche)
            'antenna_cutout_height': 12.0,# Hauteur decoupe antenne
            'velcro_slot_width': 22.0,    # Largeur fente velcro
            'velcro_slot_height': 2.5,    # Hauteur fente velcro
            'corner_radius': 2.0,

            # --- Commun ---
            'engrave_prestige': True,     # Gravure PRESTIGE sur le berceau
            'accent_groove_depth': 0.5,
            'accent_groove_width': 0.8,
            'export_part': 'assembly',    # 'clamp', 'cradle', 'assembly', 'test_ring'
        }

    def param_schema(self):
        return {
            'tube_od': {
                'type': 'float', 'min': 8, 'max': 25, 'unit': 'mm',
                'description': 'Diametre exterieur tube coulisse d\'accord'
            },
            'tube_spacing': {
                'type': 'float', 'min': 15, 'max': 50, 'unit': 'mm',
                'description': 'Entre-axe des 2 tubes de la coulisse'
            },
            'clamp_wall': {
                'type': 'float', 'min': 2.0, 'max': 5.0, 'unit': 'mm',
                'description': 'Epaisseur paroi clamp'
            },
            'clamp_height': {
                'type': 'float', 'min': 10, 'max': 35, 'unit': 'mm',
                'description': 'Hauteur du clamp le long du tube'
            },
            'clamp_opening_angle': {
                'type': 'float', 'min': 30, 'max': 90, 'unit': 'deg',
                'description': 'Angle d\'ouverture du C-ring'
            },
            'fit_clearance': {
                'type': 'float', 'min': 0.1, 'max': 0.5, 'unit': 'mm',
                'description': 'Jeu entre le tube et le clamp'
            },
            'rubber_groove_depth': {
                'type': 'float', 'min': 0, 'max': 2.0, 'unit': 'mm',
                'description': 'Profondeur rainure caoutchouc'
            },
            'rubber_groove_width': {
                'type': 'float', 'min': 0, 'max': 6.0, 'unit': 'mm',
                'description': 'Largeur rainure caoutchouc'
            },
            'screw_diameter': {
                'type': 'float', 'min': 2.5, 'max': 5.0, 'unit': 'mm',
                'description': 'Diametre vis de serrage'
            },
            'gusset_size': {
                'type': 'float', 'min': 5, 'max': 20, 'unit': 'mm',
                'description': 'Taille des gussets de renfort'
            },
            'dual_lock_size': {
                'type': 'float', 'min': 15, 'max': 35, 'unit': 'mm',
                'description': 'Dimension carre du pad Dual Lock'
            },
            'bp_width': {
                'type': 'float', 'min': 50, 'max': 80, 'unit': 'mm',
                'description': 'Largeur bodypack (64mm pour SK 100 G4)'
            },
            'bp_depth': {
                'type': 'float', 'min': 15, 'max': 40, 'unit': 'mm',
                'description': 'Profondeur bodypack (24mm pour SK 100 G4)'
            },
            'bp_height': {
                'type': 'float', 'min': 60, 'max': 100, 'unit': 'mm',
                'description': 'Hauteur bodypack (82mm pour SK 100 G4)'
            },
            'cradle_clearance': {
                'type': 'float', 'min': 0.2, 'max': 1.5, 'unit': 'mm',
                'description': 'Jeu autour du bodypack (vibrations)'
            },
            'cradle_wall': {
                'type': 'float', 'min': 1.5, 'max': 4.0, 'unit': 'mm',
                'description': 'Epaisseur parois berceau'
            },
            'cradle_wall_height': {
                'type': 'float', 'min': 8, 'max': 25, 'unit': 'mm',
                'description': 'Hauteur des parois laterales du berceau'
            },
            'cradle_base_thickness': {
                'type': 'float', 'min': 2.0, 'max': 5.0, 'unit': 'mm',
                'description': 'Epaisseur du fond du berceau'
            },
            'jack_cutout_width': {
                'type': 'float', 'min': 8, 'max': 20, 'unit': 'mm',
                'description': 'Largeur decoupe jack 3.5mm'
            },
            'jack_cutout_height': {
                'type': 'float', 'min': 6, 'max': 16, 'unit': 'mm',
                'description': 'Hauteur decoupe jack'
            },
            'antenna_cutout_width': {
                'type': 'float', 'min': 6, 'max': 16, 'unit': 'mm',
                'description': 'Largeur decoupe antenne'
            },
            'antenna_cutout_height': {
                'type': 'float', 'min': 8, 'max': 20, 'unit': 'mm',
                'description': 'Hauteur decoupe antenne'
            },
            'velcro_slot_width': {
                'type': 'float', 'min': 15, 'max': 30, 'unit': 'mm',
                'description': 'Largeur fente pour sangle velcro'
            },
            'velcro_slot_height': {
                'type': 'float', 'min': 1.5, 'max': 4, 'unit': 'mm',
                'description': 'Hauteur fente velcro'
            },
            'corner_radius': {
                'type': 'float', 'min': 0, 'max': 5, 'unit': 'mm',
                'description': 'Rayon des coins arrondis'
            },
            'engrave_prestige': {
                'type': 'bool',
                'description': 'Graver PRESTIGE sur le berceau'
            },
            'accent_groove_depth': {
                'type': 'float', 'min': 0, 'max': 1, 'unit': 'mm',
                'description': 'Profondeur rainure accent or'
            },
            'accent_groove_width': {
                'type': 'float', 'min': 0, 'max': 2, 'unit': 'mm',
                'description': 'Largeur rainure accent'
            },
            'export_part': {
                'type': 'string',
                'description': 'Piece a exporter: clamp, cradle, assembly, test_ring'
            },
        }

    # ====================================================================
    # Piece A — Trumpet Clamp
    # ====================================================================

    def _build_single_clamp(self):
        """Construit un C-ring avec oreilles de serrage M3."""
        p = self.params
        tube_r = p['tube_od'] / 2
        inner_r = tube_r + p['fit_clearance']
        outer_r = inner_r + p['clamp_wall']
        h = p['clamp_height']
        opening = p['clamp_opening_angle']
        screw_d = p['screw_diameter']
        screw_hd = p['screw_head_diameter']
        nut_w = p['nut_width']
        nut_h = p['nut_height']
        rg_depth = p['rubber_groove_depth']
        rg_width = p['rubber_groove_width']

        # -- Anneau C principal --
        outer_cyl = cylinder(r=outer_r, h=h, _fn=64)
        inner_cyl = cylinder(r=inner_r, h=h + 0.2, _fn=64)

        # Couper l'ouverture (secteur angulaire en bas)
        half_angle = opening / 2
        cut_size = outer_r + 5
        cut_block = translate([0, 0, -0.1])(
            cube([cut_size, cut_size, h + 0.4])
        )
        # Ouverture vers le bas (-Y) pour insertion du tube
        cut1 = rotate([0, 0, -90 - half_angle])(cut_block)
        cut2 = rotate([0, 0, -90 + half_angle])(
            mirror([1, 0, 0])(cut_block)
        )
        ring = outer_cyl - inner_cyl - cut1 - cut2

        # -- Oreilles de serrage (2 extensions plates pour la vis M3) --
        ear_thick = p['clamp_wall']
        ear_length = screw_hd + 3  # Longueur de l'oreille
        ear_width = h  # Meme hauteur que le clamp

        # Calculer la position des extremites de l'ouverture
        # L'ouverture est centree sur -Y (270 degres)
        angle_left = math.radians(-90 - half_angle)
        angle_right = math.radians(-90 + half_angle)

        # Oreille gauche : part du bord gauche de l'ouverture
        ear_x_l = outer_r * math.cos(angle_left)
        ear_y_l = outer_r * math.sin(angle_left)
        ear_dir_l = math.degrees(angle_left) - 90  # Tangente vers l'ext

        # Extension plate vers l'exterieur
        ear_left = translate([ear_x_l, ear_y_l, 0])(
            rotate([0, 0, ear_dir_l])(
                translate([-ear_thick / 2, 0, 0])(
                    cube([ear_thick, ear_length, ear_width])
                )
            )
        )

        # Oreille droite : symetrique
        ear_x_r = outer_r * math.cos(angle_right)
        ear_y_r = outer_r * math.sin(angle_right)
        ear_dir_r = math.degrees(angle_right) + 90

        ear_right = translate([ear_x_r, ear_y_r, 0])(
            rotate([0, 0, ear_dir_r])(
                translate([-ear_thick / 2, 0, 0])(
                    cube([ear_thick, ear_length, ear_width])
                )
            )
        )

        clamp = ring + ear_left + ear_right

        # -- Trou de vis M3 traversant les 2 oreilles --
        # Le trou traverse horizontalement au centre des oreilles
        screw_y = outer_r + ear_length / 2 + 2
        screw_z = h / 2

        # Trou de vis (traverse les 2 cotes)
        screw_hole = translate([0, -screw_y - 2, screw_z])(
            rotate([0, 0, 0])(
                rotate([-90, 0, 0])(
                    cylinder(d=screw_d + 0.3, h=screw_y * 2 + 4, _fn=32)
                )
            )
        )
        clamp = clamp - screw_hole

        # Fraisage tete de vis (cote gauche)
        head_recess = translate([0, screw_y - 1, screw_z])(
            rotate([-90, 0, 0])(
                cylinder(d=screw_hd + 0.5, h=3, _fn=32)
            )
        )
        clamp = clamp - head_recess

        # Piege a ecrou M3 hexagonal (cote droit)
        # Ecrou hex inscrit dans un cercle de nut_w / cos(30)
        nut_r = nut_w / 2 / math.cos(math.radians(30))
        nut_trap = translate([0, -screw_y + 1 - nut_h, screw_z])(
            rotate([-90, 0, 0])(
                cylinder(r=nut_r, h=nut_h + 0.2, _fn=6)
            )
        )
        clamp = clamp - nut_trap

        # -- Rainure caoutchouc interieure --
        if rg_depth > 0 and rg_width > 0:
            groove_r_outer = inner_r + 0.1
            groove_r_inner = inner_r - rg_depth
            groove = cylinder(r=groove_r_outer, h=rg_width, _fn=64) - \
                     cylinder(r=groove_r_inner, h=rg_width + 0.2, _fn=64)
            # Centrer la rainure en Z
            groove = translate([0, 0, (h - rg_width) / 2])(groove)
            # Ne garder que la partie du C-ring (pas l'ouverture)
            clamp = clamp - groove

        return clamp

    def _build_tube_clamp(self):
        """Construit le double clamp + pont + surface Dual Lock."""
        p = self.params
        spacing = p['tube_spacing']
        h = p['clamp_height']
        cw = p['clamp_wall']
        tube_r = p['tube_od'] / 2
        outer_r = tube_r + p['fit_clearance'] + cw
        dl = p['dual_lock_size']
        gs = p['gusset_size']

        # 2 clamps positionnes avec l'entre-axe
        clamp_left = translate([-spacing / 2, 0, 0])(self._build_single_clamp())
        clamp_right = translate([spacing / 2, 0, 0])(self._build_single_clamp())

        # -- Pont rigide entre les 2 clamps --
        bridge_width = spacing - 2 * outer_r + 2 * cw
        bridge_depth = outer_r * 2
        bridge_height = cw

        # Le pont est sur le dessus des clamps (Z = h)
        bridge = translate([-bridge_width / 2, -bridge_depth / 2, h])(
            cube([bridge_width, bridge_depth, bridge_height])
        )

        # -- Gussets aux jonctions pont-clamp --
        # Gusset gauche (renfort triangulaire)
        gusset_l = translate([-bridge_width / 2, -cw / 2, h])(
            rotate([0, 0, 180])(
                gusset_triangle(gs, gs, cw)
            )
        )
        # Gusset droit
        gusset_r = translate([bridge_width / 2, -cw / 2, h])(
            gusset_triangle(gs, gs, cw)
        )

        # -- Surface plate pour Dual Lock au-dessus du pont --
        dl_pad_thickness = 1.5
        dl_pad = translate([-dl / 2, -dl / 2, h + bridge_height])(
            cube([dl, dl, dl_pad_thickness])
        )

        # Indicateur visuel: carre en creux pour positionner le Dual Lock
        dl_marker = translate([-dl / 2 + 1, -dl / 2 + 1,
                               h + bridge_height + dl_pad_thickness - 0.3])(
            cube([dl - 2, dl - 2, 0.4])
        )

        model = clamp_left + clamp_right + bridge + gusset_l + gusset_r + dl_pad
        model = model - dl_marker

        return model

    # ====================================================================
    # Piece B — Bodypack Cradle
    # ====================================================================

    def _build_bodypack_cradle(self):
        """Construit le berceau en U pour le Sennheiser SK 100 G4."""
        p = self.params
        bw = p['bp_width']
        bd = p['bp_depth']
        bh = p['bp_height']
        cl = p['cradle_clearance']
        wt = p['cradle_wall']
        wh = p['cradle_wall_height']
        bt = p['cradle_base_thickness']
        cr = p['corner_radius']
        dl = p['dual_lock_size']
        groove_d = p['accent_groove_depth']
        groove_w = p['accent_groove_width']

        # Dimensions interieures
        inner_w = bw + 2 * cl
        inner_h = bh + 2 * cl

        # Dimensions exterieures
        total_w = inner_w + 2 * wt
        total_h = inner_h + 2 * wt
        total_d = bd + 2 * cl + wt  # Fond + 1 cote (berceau en U ouvert dessus)

        # -- Base (fond du berceau) --
        base = rounded_box(total_w, total_h, bt, cr)

        # -- Parois laterales (gauche et droite sur la largeur) --
        # Paroi gauche (cote antenne)
        wall_left = translate([0, 0, bt])(
            cube([wt, total_h, wh])
        )
        # Paroi droite (cote jack)
        wall_right = translate([total_w - wt, 0, bt])(
            cube([wt, total_h, wh])
        )

        # -- Paroi avant (face courte, bh = 82mm est le long Y) --
        wall_front = translate([0, 0, bt])(
            cube([total_w, wt, wh])
        )
        # Paroi arriere
        wall_back = translate([0, total_h - wt, bt])(
            cube([total_w, wt, wh])
        )

        model = base + wall_left + wall_right + wall_front + wall_back

        # -- Decoupe jack 3.5mm (paroi droite, vers le haut du bodypack) --
        jack_w = p['jack_cutout_width']
        jack_h = p['jack_cutout_height']
        # Le jack est en haut du bodypack, cote droit
        jack_cutout = translate([total_w - wt - 0.1,
                                 total_h - wt - jack_w - cl,
                                 bt])(
            cube([wt + 0.2, jack_w, jack_h + 0.1])
        )
        model = model - jack_cutout

        # -- Decoupe antenne (paroi gauche, vers le haut du bodypack) --
        ant_w = p['antenna_cutout_width']
        ant_h = p['antenna_cutout_height']
        # L'antenne est en haut du bodypack, cote gauche
        ant_cutout = translate([-0.1,
                                total_h - wt - ant_w - cl,
                                bt])(
            cube([wt + 0.2, ant_w, ant_h + 0.1])
        )
        model = model - ant_cutout

        # -- Fentes pour sangle velcro 20mm (2 fentes, face avant et arriere) --
        vs_w = p['velcro_slot_width']
        vs_h = p['velcro_slot_height']

        # Fente avant (traverse la paroi avant)
        velcro_front = translate([total_w / 2 - vs_w / 2, -0.1,
                                  bt + wh / 2 - vs_h / 2])(
            cube([vs_w, wt + 0.2, vs_h])
        )
        # Fente arriere
        velcro_back = translate([total_w / 2 - vs_w / 2, total_h - wt - 0.1,
                                 bt + wh / 2 - vs_h / 2])(
            cube([vs_w, wt + 0.2, vs_h])
        )
        model = model - velcro_front - velcro_back

        # -- Surface Dual Lock sous la base --
        # Indicateur visuel: carre en creux sur le dessous
        dl_marker = translate([total_w / 2 - dl / 2 + 1,
                               total_h / 2 - dl / 2 + 1,
                               -0.1])(
            cube([dl - 2, dl - 2, 0.4])
        )
        model = model - dl_marker

        # -- Conges interieurs fond-paroi --
        fillet_r = 1.5
        # Conge fond-paroi gauche
        fillet_profile_y = difference()(
            cube([fillet_r, total_h - 2 * cr, fillet_r]),
            translate([fillet_r, -0.1, fillet_r])(
                rotate([-90, 0, 0])(
                    cylinder(r=fillet_r, h=total_h - 2 * cr + 0.2, _fn=32)
                )
            )
        )
        f_left = translate([wt, cr, bt])(fillet_profile_y)
        f_right = translate([total_w - wt - fillet_r, cr, bt])(fillet_profile_y)
        model = model + f_left + f_right

        # Conge fond-paroi avant/arriere
        fillet_profile_x = difference()(
            cube([total_w - 2 * cr, fillet_r, fillet_r]),
            translate([-0.1, fillet_r, fillet_r])(
                rotate([0, 90, 0])(
                    cylinder(r=fillet_r, h=total_w - 2 * cr + 0.2, _fn=32)
                )
            )
        )
        f_front = translate([cr, wt, bt])(fillet_profile_x)
        f_back = translate([cr, total_h - wt - fillet_r, bt])(fillet_profile_x)
        model = model + f_front + f_back

        # -- Rainures accent or sur les parois --
        if groove_d > 0 and groove_w > 0:
            # Rainures sur le dessus des parois gauche et droite
            g_l = translate([-0.1, cr, bt + wh - groove_d])(
                cube([groove_w + 0.1, total_h - 2 * cr, groove_d + 0.1])
            )
            g_r = translate([total_w - groove_w, cr, bt + wh - groove_d])(
                cube([groove_w + 0.1, total_h - 2 * cr, groove_d + 0.1])
            )
            model = model - g_l - g_r

        # -- Gravure PRESTIGE sur la paroi avant --
        if p['engrave_prestige']:
            txt = linear_extrude(height=0.6 + 0.1)(
                text("PRESTIGE", size=4.5, font=DEFAULT_TEXT_FONT,
                     halign="center", valign="center", _fn=32)
            )
            txt = translate([total_w / 2, -0.1, bt + wh / 2])(
                rotate([90, 0, 0])(
                    mirror([0, 0, 1])(txt)
                )
            )
            model = model - txt

        return model

    # ====================================================================
    # Test Ring — Anneau de calibration rapide
    # ====================================================================

    def _build_test_ring(self):
        """Anneau test simple pour verifier l'ajustement sur la coulisse."""
        p = self.params
        tube_r = p['tube_od'] / 2
        inner_r = tube_r + p['fit_clearance']
        outer_r = inner_r + p['clamp_wall']
        ring_h = 5.0  # Seulement 5mm de haut (~5 min d'impression)
        opening = p['clamp_opening_angle']
        rg_depth = p['rubber_groove_depth']
        rg_width = p['rubber_groove_width']

        # Anneau C basique
        outer_cyl = cylinder(r=outer_r, h=ring_h, _fn=64)
        inner_cyl = cylinder(r=inner_r, h=ring_h + 0.2, _fn=64)

        half_angle = opening / 2
        cut_size = outer_r + 5
        cut_block = translate([0, 0, -0.1])(
            cube([cut_size, cut_size, ring_h + 0.4])
        )
        cut1 = rotate([0, 0, -90 - half_angle])(cut_block)
        cut2 = rotate([0, 0, -90 + half_angle])(
            mirror([1, 0, 0])(cut_block)
        )
        ring = outer_cyl - inner_cyl - cut1 - cut2

        # Rainure caoutchouc (pour tester aussi)
        if rg_depth > 0 and rg_width > 0 and rg_width < ring_h:
            groove_r_outer = inner_r + 0.1
            groove_r_inner = inner_r - rg_depth
            groove = cylinder(r=groove_r_outer, h=rg_width, _fn=64) - \
                     cylinder(r=groove_r_inner, h=rg_width + 0.2, _fn=64)
            groove = translate([0, 0, (ring_h - rg_width) / 2])(groove)
            ring = ring - groove

        # Texte indicateur du diametre
        label = linear_extrude(height=0.5)(
            text(f"D{p['tube_od']:.0f}", size=3, font=DEFAULT_TEXT_FONT,
                 halign="center", valign="center", _fn=32)
        )
        label = translate([0, outer_r + 1, 0])(label)
        ring = ring + label

        return ring

    # ====================================================================
    # Trumpet Ghost — Trompette simplifiee pour visualisation
    # ====================================================================

    def _build_trumpet_ghost(self):
        """Modele simplifie d'une trompette Bb pour contexte visuel.
        Orientation : tubes de la coulisse d'accord le long de Z,
        le pavillon part vers +X, l'embouchure vers -X.
        Le mount est centre sur les tubes de la coulisse (origine).
        Utilise union() pour eviter la recursion profonde de l'arbre CSG.
        """
        p = self.params
        tube_r = p['tube_od'] / 2
        spacing = p['tube_spacing']

        # Dimensions trompette Bb standard (approximation)
        slide_tube_len = 120.0
        valve_block_w = 75.0
        valve_block_h = 55.0
        valve_block_d = 42.0
        valve_r = 10.0
        valve_h = 65.0
        valve_cap_h = 8.0
        bell_length = 200.0
        bell_end_r = 60.0
        bell_start_r = tube_r + 1
        leadpipe_len = 140.0
        mp_receiver_r = 6.5
        mp_receiver_len = 25.0
        piston_spacing = 24.0
        slide_bottom = -15
        vb_z = slide_tube_len
        bell_start_x = valve_block_w / 2
        bell_z = vb_z + valve_block_h / 2
        lp_z = vb_z + valve_block_h * 0.7
        straight_len = 60.0

        parts = []

        # -- Tubes coulisse d'accord --
        parts.append(translate([-spacing / 2, 0, slide_bottom])(
            cylinder(r=tube_r, h=slide_tube_len - slide_bottom, _fn=32)))
        parts.append(translate([spacing / 2, 0, slide_bottom])(
            cylinder(r=tube_r, h=slide_tube_len - slide_bottom, _fn=32)))

        # -- Coude en U en bas --
        parts.append(translate([0, 0, slide_bottom])(
            rotate([0, 90, 0])(
                rotate_extrude(angle=180, _fn=32)(
                    translate([spacing / 2, 0, 0])(
                        circle(r=tube_r, _fn=24))))))

        # -- Bloc pistons --
        parts.append(translate([-valve_block_w / 2, -valve_block_d / 2, vb_z])(
            cube([valve_block_w, valve_block_d, valve_block_h])))

        # -- 3 pistons + capuchons --
        for i in range(3):
            px = -piston_spacing + i * piston_spacing
            parts.append(translate([px, 0, vb_z + valve_block_h])(
                cylinder(r=valve_r, h=valve_h, _fn=24)))
            parts.append(translate([px, 0, vb_z + valve_block_h + valve_h])(
                cylinder(r=valve_r + 2, h=valve_cap_h, _fn=24)))

        # -- Pavillon (tube + cone) --
        parts.append(translate([bell_start_x, 0, bell_z])(
            rotate([0, 90, 0])(
                cylinder(r=bell_start_r, h=straight_len, _fn=24))))

        bell_cone = translate([bell_start_x + straight_len, 0, bell_z])(
            rotate([0, 90, 0])(
                cylinder(r1=bell_start_r, r2=bell_end_r,
                         h=bell_length, _fn=48)))
        bell_hollow = translate([bell_start_x + straight_len - 0.1, 0, bell_z])(
            rotate([0, 90, 0])(
                cylinder(r1=max(bell_start_r - 1.5, 1), r2=bell_end_r - 1.5,
                         h=bell_length + 0.2, _fn=48)))
        parts.append(bell_cone - bell_hollow)

        # Bord du pavillon
        rim_x = bell_start_x + straight_len + bell_length
        parts.append(translate([rim_x, 0, bell_z])(
            rotate([0, 90, 0])(
                cylinder(r=bell_end_r + 2, h=3, _fn=48) -
                cylinder(r=bell_end_r - 2, h=3.2, _fn=48))))

        # -- Branche d'embouchure --
        parts.append(translate([-valve_block_w / 2 - leadpipe_len, 0, lp_z])(
            rotate([0, 90, 0])(
                cylinder(r=tube_r, h=leadpipe_len, _fn=24))))
        parts.append(translate([-valve_block_w / 2 - leadpipe_len - mp_receiver_len,
                                 0, lp_z])(
            rotate([0, 90, 0])(
                cylinder(r=mp_receiver_r, h=mp_receiver_len, _fn=24))))

        # -- Coulisses pistons 1 et 3 --
        for sx, slen in [(-piston_spacing, 35), (piston_spacing, 65)]:
            sz = vb_z + (15 if sx < 0 else 10)
            parts.append(translate([sx, valve_block_d / 2, sz])(
                rotate([-90, 0, 0])(
                    cylinder(r=tube_r * 0.6, h=slen, _fn=16))))
            parts.append(translate([sx + (10 if sx < 0 else -10),
                                     valve_block_d / 2, sz])(
                rotate([-90, 0, 0])(
                    cylinder(r=tube_r * 0.6, h=slen, _fn=16))))

        # -- Trigger ring (3eme coulisse) --
        parts.append(translate([piston_spacing - 5,
                                 valve_block_d / 2 + 60, vb_z + 10])(
            rotate([-90, 0, 0])(
                cylinder(r=8, h=3, _fn=24) -
                cylinder(r=5, h=3.2, _fn=24))))

        # -- Water key --
        parts.append(translate([-spacing / 4, tube_r + 2, slide_bottom + 5])(
            rotate([0, 90, 0])(
                cylinder(r=2, h=15, _fn=12))))

        return color([0.80, 0.68, 0.21, 0.25])(union()(*parts))

    # ====================================================================
    # Assembly — Vue complete avec fantomes
    # ====================================================================

    def _build_assembly(self):
        """Vue assembly avec trompette complete, clamp, cradle, et bodypack."""
        p = self.params
        dl = p['dual_lock_size']
        bw = p['bp_width']
        bd = p['bp_depth']
        bh = p['bp_height']
        cl = p['cradle_clearance']
        wt = p['cradle_wall']
        bt = p['cradle_base_thickness']
        cw = p['clamp_wall']
        h = p['clamp_height']
        bridge_h = cw
        dl_pad_h = 1.5
        dl_gap = 3.0  # Epaisseur Dual Lock 3M (~3mm les 2 faces)

        # ====== Trompette fantome ======
        trumpet = self._build_trumpet_ghost()

        # ====== Piece A — Clamp (sur les tubes, centre en Z) ======
        # Positionner le clamp au milieu des tubes de la coulisse
        clamp_z_offset = 30.0  # Position du clamp sur les tubes
        clamp = color([1, 1, 1, 0.9])(
            translate([0, 0, clamp_z_offset])(
                self._build_tube_clamp()
            )
        )

        # ====== Piece B — Cradle (au-dessus du clamp, separee par Dual Lock) ======
        cradle_total_w = bw + 2 * cl + 2 * wt
        cradle_total_h = bh + 2 * cl + 2 * wt
        cradle_z = clamp_z_offset + h + bridge_h + dl_pad_h + dl_gap
        cradle = color([1, 1, 1, 0.9])(
            translate([-cradle_total_w / 2,
                        -cradle_total_h / 2,
                        cradle_z])(
                self._build_bodypack_cradle()
            )
        )

        # ====== Fantome bodypack Sennheiser SK 100 G4 ======
        bp_ghost = color([0.25, 0.25, 0.28, 0.5])(
            translate([-bw / 2, -bh / 2,
                       cradle_z + bt + cl])(
                cube([bw, bh, bd])
            )
        )

        # Ecran LCD (petit rectangle sur la face avant)
        screen = color([0.1, 0.4, 0.1, 0.6])(
            translate([-15, -bh / 2 - 0.5, cradle_z + bt + cl + 8])(
                cube([30, 0.5, 12])
            )
        )

        # Antenne (fil flexible, cote gauche en haut)
        antenna = color([0.2, 0.2, 0.2, 0.5])(
            translate([-bw / 2 - 1, bh / 2 - 10,
                       cradle_z + bt + cl])(
                cylinder(r=1, h=103, _fn=12)  # 103mm antenne bande G
            )
        )

        # Cable DPA (simulation, sort du jack cote droit)
        cable_start_x = bw / 2 + 2
        cable_start_y = bh / 2 - 15
        cable_z = cradle_z + bt + cl + 5
        dpa_cable = color([0.1, 0.1, 0.1, 0.4])(
            translate([cable_start_x, cable_start_y, cable_z])(
                rotate([0, 90, 0])(
                    cylinder(r=1.5, h=30, _fn=12)
                )
            )
        )

        return union()(trumpet, clamp, cradle, bp_ghost, screen, antenna, dpa_cable)

    # ====================================================================
    # build() — Point d'entree principal
    # ====================================================================

    def build(self):
        export = self.params['export_part']

        if export == 'clamp':
            return self._build_tube_clamp()
        elif export == 'cradle':
            return self._build_bodypack_cradle()
        elif export == 'test_ring':
            return self._build_test_ring()
        else:
            return self._build_assembly()


if __name__ == "__main__":
    import sys

    parts = ['clamp', 'cradle', 'test_ring', 'assembly']

    for part in parts:
        mount = TrumpetBodypackMount(export_part=part)
        mount.name = f"trumpet_bodypack_mount_{part}"
        print(f"Generation {part}...")
        try:
            scad_path = mount.save_scad()
            print(f"  SCAD: {scad_path}")
        except Exception as e:
            print(f"  Erreur: {e}", file=sys.stderr)

    print("OK - Trumpet Bodypack Mount genere!")
