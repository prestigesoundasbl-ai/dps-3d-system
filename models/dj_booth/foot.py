"""
Pied Reglable pour DJ Booth
S'insere dans l'extremite basse d'un profil aluminium 2040.
Pad anti-vibration + niveleur optionnel.
4 necessaires pour le booth complet.
"""
from solid2 import *
from ..base import ParametricModel
from ._constants import (
    PROFILE_W, FIT_CLEARANCE
)


class BoothFoot(ParametricModel):

    def __init__(self, **params):
        super().__init__("booth_foot", **params)

    def default_params(self):
        return {
            'foot_diameter': 50.0,
            'foot_height': 12.0,
            'insert_size': 19.4,
            'insert_height': 30.0,
            'rubber_pad_recess': True,
            'rubber_pad_diameter': 30.0,
            'rubber_pad_depth': 2.0,
            'rib_count': 4,
            'rib_height': 0.5,
            'chamfer': 2.0,
        }

    def param_schema(self):
        return {
            'foot_diameter': {
                'type': 'float', 'min': 30, 'max': 80, 'unit': 'mm',
                'description': 'Diametre du pied au sol'
            },
            'foot_height': {
                'type': 'float', 'min': 5, 'max': 25, 'unit': 'mm',
                'description': 'Epaisseur du pied (hauteur visible)'
            },
            'insert_size': {
                'type': 'float', 'min': 18, 'max': 20, 'unit': 'mm',
                'description': 'Largeur de l\'insert (19.4mm pour profil 20mm)'
            },
            'insert_height': {
                'type': 'float', 'min': 15, 'max': 50, 'unit': 'mm',
                'description': 'Longueur d\'insertion dans le profil'
            },
            'rubber_pad_recess': {
                'type': 'bool',
                'description': 'Logement pour pad caoutchouc adhesif'
            },
            'rubber_pad_diameter': {
                'type': 'float', 'min': 15, 'max': 50, 'unit': 'mm',
                'description': 'Diametre du pad caoutchouc'
            },
            'rubber_pad_depth': {
                'type': 'float', 'min': 1, 'max': 4, 'unit': 'mm',
                'description': 'Profondeur du logement pad'
            },
            'rib_count': {
                'type': 'int', 'min': 0, 'max': 8,
                'description': 'Nombre de nervures de friction sur l\'insert'
            },
            'rib_height': {
                'type': 'float', 'min': 0.2, 'max': 1.0, 'unit': 'mm',
                'description': 'Hauteur des nervures (depassement)'
            },
            'chamfer': {
                'type': 'float', 'min': 0, 'max': 5, 'unit': 'mm',
                'description': 'Chanfrein sur le bord du pied'
            },
        }

    def build(self):
        p = self.params
        fd = p['foot_diameter']
        fh = p['foot_height']
        ins = p['insert_size']
        ins_h = p['insert_height']
        chamfer = p['chamfer']

        # -- Base du pied (cylindre) --
        if chamfer > 0:
            # Pied avec chanfrein bas
            base = cylinder(d=fd, h=fh - chamfer, _fn=64)
            top_ring = translate([0, 0, fh - chamfer])(
                cylinder(d1=fd, d2=fd - 2 * chamfer, h=chamfer, _fn=64)
            )
            foot = base + top_ring
        else:
            foot = cylinder(d=fd, h=fh, _fn=64)

        # Centrer le pied
        foot = translate([0, 0, 0])(foot)

        # -- Insert carre (rentre dans le profil 2040) --
        half = ins / 2
        insert = translate([-half, -half, fh])(
            cube([ins, ins, ins_h])
        )

        # Chanfrein d'entree sur l'insert (facilite l'insertion)
        entry_chamfer = 1.5
        insert_tip = translate([-half + entry_chamfer, -half + entry_chamfer,
                               fh + ins_h - entry_chamfer])(
            cube([ins - 2 * entry_chamfer, ins - 2 * entry_chamfer, entry_chamfer])
        )
        insert_full = translate([-half, -half, fh + ins_h - entry_chamfer * 2])(
            cube([ins, ins, entry_chamfer])
        )
        insert_top = hull()(insert_tip, insert_full)
        insert = translate([-half, -half, fh])(
            cube([ins, ins, ins_h - entry_chamfer])
        ) + insert_top

        model = foot + insert

        # -- Nervures de friction sur l'insert --
        if p['rib_count'] > 0:
            rib_h = p['rib_height']
            rib_size = ins + 2 * rib_h
            rib_spacing = ins_h / (p['rib_count'] + 1)

            for i in range(p['rib_count']):
                z = fh + rib_spacing * (i + 1)
                rib = translate([0, 0, z])(
                    translate([-rib_size / 2, -rib_size / 2, 0])(
                        cube([rib_size, rib_size, 1.0])
                    )
                )
                # Arrondir les coins de la nervure : on enleve les coins
                for dx in [-1, 1]:
                    for dy in [-1, 1]:
                        corner_cut = translate([dx * rib_size / 2,
                                              dy * rib_size / 2, z - 0.1])(
                            cylinder(r=rib_h, h=1.4, _fn=16)
                        )
                        # Additionner plutot que soustraire pour simplifier
                # Simplifier : nervures = cube legèrement plus grand
                rib = translate([-rib_size / 2, -rib_size / 2, z])(
                    cube([rib_size, rib_size, 0.8])
                )
                model = model + rib

        # -- Logement pad caoutchouc (sous le pied) --
        if p['rubber_pad_recess']:
            pad_d = p['rubber_pad_diameter']
            pad_depth = p['rubber_pad_depth']
            recess = translate([0, 0, -0.1])(
                cylinder(d=pad_d, h=pad_depth + 0.1, _fn=64)
            )
            model = model - recess

        return model


if __name__ == "__main__":
    import sys
    foot = BoothFoot()
    print(f"Generation pied booth...")
    print(f"Parametres: {foot.params}")
    scad_path = foot.save_scad()
    print(f"SCAD: {scad_path}")
    try:
        stl_path = foot.render_stl()
        print(f"STL: {stl_path}")
        print("OK")
    except Exception as e:
        print(f"Erreur STL: {e}", file=sys.stderr)
