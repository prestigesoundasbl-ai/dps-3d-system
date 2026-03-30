"""
Charniere 180° pour DJ Booth - Pliage rapide du cadre
Se monte sur 2 profiles 2040 adjacents, permet le pliage a plat du cadre.
Axe en tige acier 6mm (vendue en magasin bricolage).
Impression sans support, orientation a plat.
4 necessaires (2 par cote du booth).
"""
from solid2 import *
from ..base import ParametricModel
from ._constants import (
    PROFILE_W, PROFILE_H, SLOT_WIDTH, SLOT_DEPTH,
    M5_HOLE, M5_HEAD, M5_HEAD_DEPTH,
    FIT_CLEARANCE, SLOT_CLEARANCE,
    HINGE_PIN_D, HINGE_BARREL_OD, HINGE_BARREL_LEN
)


class BoothHinge(ParametricModel):

    def __init__(self, **params):
        super().__init__("booth_hinge", **params)

    def default_params(self):
        return {
            'plate_length': 60.0,
            'plate_width': 40.0,
            'plate_thickness': 4.0,
            'barrel_count': 3,
            'barrel_length': 12.0,
            'pin_diameter': HINGE_PIN_D,
            'barrel_od': HINGE_BARREL_OD,
            'bolt_count': 2,
            'tslot_tab': True,
            'open_angle': 0.0,
            'fit_clearance': FIT_CLEARANCE,
        }

    def param_schema(self):
        return {
            'plate_length': {
                'type': 'float', 'min': 40, 'max': 100, 'unit': 'mm',
                'description': 'Longueur de chaque plaque le long du profil'
            },
            'plate_width': {
                'type': 'float', 'min': 20, 'max': 60, 'unit': 'mm',
                'description': 'Largeur de la plaque (perpendiculaire au profil)'
            },
            'plate_thickness': {
                'type': 'float', 'min': 3, 'max': 8, 'unit': 'mm',
                'description': 'Epaisseur des plaques'
            },
            'barrel_count': {
                'type': 'int', 'min': 3, 'max': 7,
                'description': 'Nombre total de barrels (impair recommande)'
            },
            'barrel_length': {
                'type': 'float', 'min': 8, 'max': 20, 'unit': 'mm',
                'description': 'Longueur de chaque barrel'
            },
            'pin_diameter': {
                'type': 'float', 'min': 4, 'max': 8, 'unit': 'mm',
                'description': 'Diametre de l\'axe (tige acier standard)'
            },
            'barrel_od': {
                'type': 'float', 'min': 10, 'max': 20, 'unit': 'mm',
                'description': 'Diametre externe du barrel'
            },
            'bolt_count': {
                'type': 'int', 'min': 1, 'max': 3,
                'description': 'Nombre de boulons M5 par plaque'
            },
            'tslot_tab': {
                'type': 'bool',
                'description': 'Ajouter des tabs T-slot d\'alignement'
            },
            'open_angle': {
                'type': 'float', 'min': 0, 'max': 180, 'unit': 'deg',
                'description': 'Angle d\'ouverture pour visualisation (0=ferme, 90=L, 180=plat)'
            },
            'fit_clearance': {
                'type': 'float', 'min': 0.1, 'max': 0.6, 'unit': 'mm',
                'description': 'Jeu d\'ajustement'
            },
        }

    def _build_plate(self, pl, pw, pt, n_bolts):
        """Construit une plaque avec trous de boulons."""
        plate = cube([pl, pw, pt])

        # Trous M5
        bolt_spacing = pl / (n_bolts + 1)
        for i in range(n_bolts):
            x = bolt_spacing * (i + 1)
            hole = translate([x, pw / 2, -0.1])(
                cylinder(d=M5_HOLE, h=pt + 0.4, _fn=32)
            )
            cs = translate([x, pw / 2, pt - M5_HEAD_DEPTH])(
                cylinder(d=M5_HEAD, h=M5_HEAD_DEPTH + 0.2, _fn=32)
            )
            plate = plate - hole - cs

        # Tab T-slot
        if self.params['tslot_tab']:
            tab_w = SLOT_WIDTH - 2 * SLOT_CLEARANCE
            tab_d = SLOT_DEPTH - SLOT_CLEARANCE
            tab_len = pl * 0.5
            tab = translate([(pl - tab_len) / 2, (pw - tab_w) / 2, -tab_d])(
                cube([tab_len, tab_w, tab_d])
            )
            plate = plate + tab

        return plate

    def _build_barrels(self, pl, pt, barrel_count, barrel_len, pin_d, barrel_od):
        """Construit les barrels (gonds) de la charniere."""
        clr = self.params['fit_clearance']
        pin_r = (pin_d + clr) / 2  # trou pour l'axe avec jeu
        barrel_r = barrel_od / 2

        # Espacement total
        gap = 0.5  # espace entre barrels
        total_barrel_len = barrel_count * barrel_len + (barrel_count - 1) * gap
        start_x = (pl - total_barrel_len) / 2

        barrels_a = None  # barrels pour plaque A (indices pairs)
        barrels_b = None  # barrels pour plaque B (indices impairs)

        for i in range(barrel_count):
            x = start_x + i * (barrel_len + gap)

            # Barrel cylindrique avec trou pour l'axe
            barrel = translate([x, 0, pt + barrel_r])(
                rotate([0, 90, 0])(
                    rotate([0, 0, 0])(
                        cylinder(r=barrel_r, h=barrel_len, _fn=32)
                    )
                )
            )
            # Percer le trou de l'axe (traverse tous les barrels)
            # On le fera a la fin sur le modele complet

            if i % 2 == 0:
                barrels_a = barrel if barrels_a is None else barrels_a + barrel
            else:
                barrels_b = barrel if barrels_b is None else barrels_b + barrel

        return barrels_a, barrels_b

    def build(self):
        p = self.params
        pl = p['plate_length']
        pw = p['plate_width']
        pt = p['plate_thickness']
        n_bolts = p['bolt_count']
        barrel_count = p['barrel_count']
        barrel_len = p['barrel_length']
        pin_d = p['pin_diameter']
        barrel_od = p['barrel_od']
        angle = p['open_angle']
        clr = p['fit_clearance']

        barrel_r = barrel_od / 2
        pin_r = (pin_d + clr) / 2

        # -- Plaque A (fixe) --
        plate_a = self._build_plate(pl, pw, pt, n_bolts)

        # -- Barrels pour plaque A (indices pairs) et B (impairs) --
        barrels_a, barrels_b = self._build_barrels(
            pl, pt, barrel_count, barrel_len, pin_d, barrel_od
        )

        # Attacher les barrels pairs a la plaque A
        plate_a_full = plate_a
        if barrels_a is not None:
            plate_a_full = plate_a_full + barrels_a

        # -- Plaque B (mobile) --
        plate_b = self._build_plate(pl, pw, pt, n_bolts)

        # Attacher les barrels impairs a la plaque B
        plate_b_full = plate_b
        if barrels_b is not None:
            plate_b_full = plate_b_full + barrels_b

        # -- Positionner plaque B avec rotation --
        # L'axe de rotation est au centre des barrels: Y=0, Z=pt+barrel_r
        pivot_y = 0
        pivot_z = pt + barrel_r

        # Plaque B : miroir par rapport a l'axe Y=0, puis rotation
        plate_b_full = mirror([0, 1, 0])(plate_b_full)

        if angle > 0:
            # Rotation autour de l'axe des barrels (axe X)
            plate_b_full = translate([0, pivot_y, pivot_z])(
                rotate([angle, 0, 0])(
                    translate([0, -pivot_y, -pivot_z])(plate_b_full)
                )
            )
        else:
            # Position fermee (angle=0) : les deux plaques sont cote a cote
            pass

        model = plate_a_full + plate_b_full

        # -- Trou d'axe (traverse tous les barrels) --
        gap_count = barrel_count - 1
        total_len = barrel_count * barrel_len + gap_count * 0.5
        start_x = (pl - total_len) / 2
        pin_hole = translate([start_x - 1, 0, pt + barrel_r])(
            rotate([0, 90, 0])(
                rotate([0, 0, 0])(
                    cylinder(r=pin_r, h=total_len + 2, _fn=32)
                )
            )
        )
        model = model - pin_hole

        return model


if __name__ == "__main__":
    import sys
    # Version fermee (90 degres = position L)
    hinge = BoothHinge(open_angle=90)
    print(f"Generation charniere booth (90 deg)...")
    print(f"Parametres: {hinge.params}")
    scad_path = hinge.save_scad()
    print(f"SCAD: {scad_path}")
    try:
        stl_path = hinge.render_stl()
        print(f"STL: {stl_path}")
        print("OK")
    except Exception as e:
        print(f"Erreur STL: {e}", file=sys.stderr)
