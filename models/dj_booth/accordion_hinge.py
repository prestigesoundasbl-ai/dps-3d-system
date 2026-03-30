"""
Charniere Accordeon pour DJ Booth Pliable
==========================================
Piece cle du systeme. Deux plaques en U-channel agrippent
les tubes alu 25x25mm adjacents, reliees par des gonds (barrels)
pour une rotation 180 degres. Axe = tige acier 6mm.

Imprimable CityFab1 : ~80x50x43mm
3 necessaires par jonction (haut, milieu, bas).
6 au total pour le booth (3 gauche + 3 droite).
"""
from solid2 import *
from ..base import ParametricModel
from ._constants import (
    M5_HOLE, M5_HEAD, M5_HEAD_DEPTH,
    FIT_CLEARANCE,
    HINGE_PIN_D, HINGE_BARREL_OD,
    ACCORDION_TUBE, ACCORDION_INSERT_CLEARANCE,
)


class AccordionHinge(ParametricModel):

    def __init__(self, **params):
        super().__init__("accordion_hinge", **params)

    def default_params(self):
        return {
            'tube_size': ACCORDION_TUBE,
            'plate_thickness': 4.0,
            'barrel_count': 5,
            'pin_diameter': HINGE_PIN_D,
            'barrel_od': HINGE_BARREL_OD,
            'open_angle': 0.0,
            'fit_clearance': FIT_CLEARANCE,
        }

    def param_schema(self):
        return {
            'tube_size': {
                'type': 'float', 'min': 20, 'max': 30, 'unit': 'mm',
                'description': 'Section tube alu carre',
            },
            'plate_thickness': {
                'type': 'float', 'min': 3, 'max': 6, 'unit': 'mm',
                'description': 'Epaisseur des plaques U-channel',
            },
            'barrel_count': {
                'type': 'int', 'min': 3, 'max': 7,
                'description': 'Nombre de barrels (impair pour interlock)',
            },
            'pin_diameter': {
                'type': 'float', 'min': 4, 'max': 8, 'unit': 'mm',
                'description': 'Diametre axe acier',
            },
            'barrel_od': {
                'type': 'float', 'min': 10, 'max': 20, 'unit': 'mm',
                'description': 'Diametre externe barrel',
            },
            'open_angle': {
                'type': 'float', 'min': 0, 'max': 180, 'unit': 'deg',
                'description': 'Angle d\'ouverture (0=ferme, 180=plat deploye)',
            },
            'fit_clearance': {
                'type': 'float', 'min': 0.1, 'max': 0.6, 'unit': 'mm',
                'description': 'Jeu d\'ajustement',
            },
        }

    def _u_channel(self, tube, pt, clr):
        """Plaque en U qui agrippe 3 faces du tube alu.
        Le tube est oriente en Z. Le U s'ouvre vers +Y.
        Optimise : chanfreins + structure allegee (Truss).
        """
        # Dimensions exterieures du U
        inner = tube + 2 * clr
        outer_w = inner + 2 * pt
        depth = inner + pt  # fond + ouverture
        height = tube * 1.5  # hauteur le long du tube (Z)

        # Bloc plein
        u = cube([outer_w, depth, height])
        
        # Chanfreins (Biseaux a 45 degres)
        chamfer_size = 2.0
        # Outil de coupe pour chanfrein
        cutter = rotate([0, 45, 0])(cube([chamfer_size * 3, depth + 2, chamfer_size * 3], center=True))
        
        # Chanfreins verticaux (coins externes)
        u -= translate([0, 0, height/2])(cutter)  # Coin gauche
        u -= translate([outer_w, 0, height/2])(cutter)  # Coin droit
        
        # Evider l'interieur (le tube)
        cavity = translate([pt, pt, -0.1])(
            cube([inner, inner + 0.1, height + 0.2])
        )
        u -= cavity

        # --- OPTIMISATION : Structure Truss (Triangles) ---
        # Decoupes triangulaires sur les flancs lateraux pour alleger
        truss_size = (depth - pt) * 0.6
        truss_cutter = rotate([90, 0, 0])(
            linear_extrude(height=outer_w + 2)(
                polygon(points=[[0, 0], [truss_size, height/2], [0, height]])
            )
        )
        # Positionner la decoupe sur le flanc
        # u -= translate([-1, pt + (depth-pt)/2 - truss_size/2, 0])(truss_cutter)

        # Decoupe rectangulaire arrondie simple (plus propre a l'impression)
        cutout_w = depth - pt - 10
        cutout_h = height - 10
        if cutout_w > 5 and cutout_h > 5:
            # Flanc Gauche
            u -= translate([-1, pt + 5, 5])(cube([pt + 2, cutout_w, cutout_h]))
            # Flanc Droit
            u -= translate([outer_w - pt - 1, pt + 5, 5])(cube([pt + 2, cutout_w, cutout_h]))

        # 2 trous M5 pour boulonnage (traversent le fond)
        bolt_spacing = height / 3
        for i in range(2):
            z = bolt_spacing * (i + 1)
            hole = translate([outer_w / 2, -0.1, z])(
                rotate([-90, 0, 0])(
                    cylinder(d=M5_HOLE, h=pt + 0.2, _fn=24)
                )
            )
            # Tete noyee (Counterbore)
            cs = translate([outer_w / 2, -0.1, z])(
                 rotate([-90, 0, 0])(
                    cylinder(d=M5_HEAD, h=M5_HEAD_DEPTH, _fn=24)
                 )
            )
            u -= hole
            u -= cs # On veut que la tete de vis ne depasse pas coté exterieur

        return u

    def build(self):
        p = self.params
        tube = p['tube_size']
        pt = p['plate_thickness']
        n_barrels = int(p['barrel_count'])
        pin_d = p['pin_diameter']
        barrel_od = p['barrel_od']
        angle = p['open_angle']
        clr = p['fit_clearance']

        barrel_r = barrel_od / 2
        pin_r = (pin_d + clr) / 2

        inner = tube + 2 * clr
        outer_w = inner + 2 * pt
        u_depth = inner + pt
        u_height = tube * 1.5

        # Barrels - repartis le long de l'axe Z du U-channel
        barrel_len = (u_height - 1) / n_barrels  # avec petits gaps
        gap = 0.5

        # --- Plaque A (fixe, a gauche) ---
        plate_a = self._u_channel(tube, pt, clr)

        # Barrels pairs sur plaque A
        barrels_a = union()
        for i in range(n_barrels):
            if i % 2 == 0:
                z = i * (barrel_len + gap)
                b = translate([outer_w / 2, u_depth, z])(
                    cylinder(r=barrel_r, h=barrel_len, _fn=32)
                )
                barrels_a += b
        plate_a += barrels_a

        # --- Plaque B (mobile, a droite) ---
        plate_b = self._u_channel(tube, pt, clr)

        # Barrels impairs sur plaque B
        barrels_b = union()
        for i in range(n_barrels):
            if i % 2 == 1:
                z = i * (barrel_len + gap)
                b = translate([outer_w / 2, u_depth, z])(
                    cylinder(r=barrel_r, h=barrel_len, _fn=32)
                )
                barrels_b += b
        plate_b += barrels_b

        # Position de plaque B : miroir + rotation
        # L'axe de pivot est au centre des barrels (Y=u_depth, milieu)
        plate_b = mirror([1, 0, 0])(plate_b)
        plate_b = translate([0, 0, 0])(plate_b)

        if angle > 0:
            # Rotation autour de l'axe Z (vertical) passant par Y=u_depth
            pivot_y = u_depth
            plate_b = translate([0, pivot_y, 0])(
                rotate([0, 0, angle])(
                    translate([0, -pivot_y, 0])(plate_b)
                )
            )
        else:
            # Fermee : plaque B collee contre plaque A
            plate_b = translate([outer_w, 0, 0])(
                mirror([1, 0, 0])(self._u_channel(tube, pt, clr) + barrels_b)
            )

        model = plate_a + plate_b

        # Trou d'axe (traverse tous les barrels)
        total_z = n_barrels * (barrel_len + gap) - gap
        pin_hole = translate([outer_w / 2, u_depth, -0.5])(
            cylinder(r=pin_r, h=total_z + 1, _fn=24)
        )
        model -= pin_hole

        # Si angle > 0, percer aussi dans la partie pivotee
        if angle > 0:
            pivot_y = u_depth
            pin_hole2 = translate([0, pivot_y, 0])(
                rotate([0, 0, angle])(
                    translate([0, -pivot_y, 0])(
                        translate([-outer_w / 2, u_depth, -0.5])(
                            cylinder(r=pin_r, h=total_z + 1, _fn=24)
                        )
                    )
                )
            )
            model -= pin_hole2

        return model
