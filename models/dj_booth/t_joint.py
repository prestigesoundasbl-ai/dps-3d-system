"""
Connecteur en T pour DJ Booth - Joint intermediaire 2040
Relie un profil principal a une branche perpendiculaire.
10 necessaires pour le booth complet (traverses intermediaires).
"""
from solid2 import *
from ..base import ParametricModel
from ._constants import (
    PROFILE_W, SLOT_WIDTH, SLOT_DEPTH,
    M5_HOLE, M5_HEAD, M5_HEAD_DEPTH,
    FIT_CLEARANCE, SLOT_CLEARANCE
)


class BoothTJoint(ParametricModel):

    def __init__(self, **params):
        super().__init__("booth_t_joint", **params)

    def default_params(self):
        return {
            'main_arm_length': 60.0,
            'branch_arm_length': 50.0,
            'wall_thickness': 4.0,
            'profile_face': 20.0,
            'bolt_count_main': 2,
            'bolt_count_branch': 1,
            'gusset': True,
            'gusset_thickness': 4.0,
            'tslot_tab': True,
            'fit_clearance': FIT_CLEARANCE,
            'mirror': False,
        }

    def param_schema(self):
        return {
            'main_arm_length': {
                'type': 'float', 'min': 30, 'max': 120, 'unit': 'mm',
                'description': 'Longueur du bras principal le long du profil (axe X)'
            },
            'branch_arm_length': {
                'type': 'float', 'min': 25, 'max': 100, 'unit': 'mm',
                'description': 'Longueur de la branche perpendiculaire (axe Y)'
            },
            'wall_thickness': {
                'type': 'float', 'min': 3, 'max': 8, 'unit': 'mm',
                'description': 'Epaisseur de la plaque'
            },
            'profile_face': {
                'type': 'float', 'min': 15, 'max': 40, 'unit': 'mm',
                'description': 'Largeur de face du profil alu (20 pour 2040)'
            },
            'bolt_count_main': {
                'type': 'int', 'min': 1, 'max': 4,
                'description': 'Nombre de boulons M5 sur le bras principal'
            },
            'bolt_count_branch': {
                'type': 'int', 'min': 1, 'max': 3,
                'description': 'Nombre de boulons M5 sur la branche'
            },
            'gusset': {
                'type': 'bool',
                'description': 'Ajouter des renforts triangulaires aux jonctions'
            },
            'gusset_thickness': {
                'type': 'float', 'min': 2, 'max': 8, 'unit': 'mm',
                'description': 'Epaisseur des renforts'
            },
            'tslot_tab': {
                'type': 'bool',
                'description': 'Ajouter des tabs d\'alignement T-slot'
            },
            'fit_clearance': {
                'type': 'float', 'min': 0.1, 'max': 0.6, 'unit': 'mm',
                'description': 'Jeu d\'ajustement (0.3mm standard FDM)'
            },
            'mirror': {
                'type': 'bool',
                'description': 'Version miroir (pour le cote oppose)'
            },
        }

    def build(self):
        p = self.params
        main_len = p['main_arm_length']
        branch_len = p['branch_arm_length']
        wt = p['wall_thickness']
        face = p['profile_face']
        n_main = p['bolt_count_main']
        n_branch = p['bolt_count_branch']
        clr = p['fit_clearance']

        # Le bras principal est centre sur X : de -main_len/2 a +main_len/2
        # La branche part du milieu vers +Y
        # Origine : centre du bras principal en X, bord inferieur en Y

        # -- Bras principal : le long de X --
        arm_main = translate([-main_len / 2, 0, 0])(
            cube([main_len, face, wt])
        )

        # -- Branche perpendiculaire : le long de Y --
        arm_branch = translate([-wt / 2, 0, 0])(
            cube([wt, branch_len, face])
        )

        # -- Zone de jonction (intersection T) --
        junction = translate([-face / 2, 0, 0])(
            cube([face, face, face])
        )

        model = arm_main + arm_branch + junction

        # -- Renforts triangulaires (gussets) --
        if p['gusset']:
            gt = p['gusset_thickness']
            gusset_x = min(main_len / 2 * 0.6, 30)
            gusset_y = min(branch_len * 0.5, 25)

            # Renfort cote droit (+X vers +Y)
            g_right = hull()(
                translate([wt / 2, face, 0])(cube([gusset_x, gt, wt])),
                translate([wt / 2 - gt, face, 0])(cube([gt, gusset_y, wt]))
            )
            # Placer au milieu en Z de la face
            g_right = translate([0, 0, (face - wt) / 2])(g_right)

            # Renfort cote gauche (-X vers +Y)
            g_left = hull()(
                translate([-wt / 2 - gusset_x, face, 0])(cube([gusset_x, gt, wt])),
                translate([-wt / 2, face, 0])(cube([gt, gusset_y, wt]))
            )
            g_left = translate([0, 0, (face - wt) / 2])(g_left)

            model = model + g_right + g_left

        # -- Trous de boulons M5 sur bras principal (cote droit, +X) --
        usable_main_right = main_len / 2 - face / 2
        if usable_main_right > 0 and n_main > 0:
            spacing_r = usable_main_right / (n_main + 1)
            for i in range(n_main):
                x_pos = face / 2 + spacing_r * (i + 1)
                # Trou traversant en Z
                hole = translate([x_pos, face / 2, -0.1])(
                    cylinder(d=M5_HOLE, h=wt + 0.4, _fn=32)
                )
                countersink = translate([x_pos, face / 2, wt - M5_HEAD_DEPTH])(
                    cylinder(d=M5_HEAD, h=M5_HEAD_DEPTH + 0.2, _fn=32)
                )
                model = model - hole - countersink

        # -- Trous de boulons M5 sur bras principal (cote gauche, -X) --
        usable_main_left = main_len / 2 - face / 2
        if usable_main_left > 0 and n_main > 0:
            spacing_l = usable_main_left / (n_main + 1)
            for i in range(n_main):
                x_pos = -(face / 2 + spacing_l * (i + 1))
                hole = translate([x_pos, face / 2, -0.1])(
                    cylinder(d=M5_HOLE, h=wt + 0.4, _fn=32)
                )
                countersink = translate([x_pos, face / 2, wt - M5_HEAD_DEPTH])(
                    cylinder(d=M5_HEAD, h=M5_HEAD_DEPTH + 0.2, _fn=32)
                )
                model = model - hole - countersink

        # -- Trous de boulons M5 sur branche perpendiculaire --
        usable_branch = branch_len - face
        if usable_branch > 0 and n_branch > 0:
            spacing_b = usable_branch / (n_branch + 1)
            for i in range(n_branch):
                y_pos = face + spacing_b * (i + 1)
                # Trou traversant en X a travers la branche
                hole = translate([-0.1 - wt / 2, y_pos, face / 2])(
                    rotate([0, 90, 0])(
                        cylinder(d=M5_HOLE, h=wt + 0.4, _fn=32)
                    )
                )
                countersink = translate([wt / 2 - M5_HEAD_DEPTH, y_pos, face / 2])(
                    rotate([0, 90, 0])(
                        cylinder(d=M5_HEAD, h=M5_HEAD_DEPTH + 0.2, _fn=32)
                    )
                )
                model = model - hole - countersink

        # -- Tabs T-slot (alignement dans la rainure) --
        if p['tslot_tab']:
            tab_w = SLOT_WIDTH - 2 * SLOT_CLEARANCE
            tab_d = SLOT_DEPTH - SLOT_CLEARANCE
            tab_len_main = (main_len - face) * 0.4

            # Tab sur la face interne du bras principal (sous le bras, cote profil)
            # Cote droit
            if tab_len_main > 5:
                tab_main_r = translate([face / 2 + (usable_main_right - tab_len_main) / 2,
                                        (face - tab_w) / 2, -tab_d])(
                    cube([tab_len_main, tab_w, tab_d])
                )
                model = model + tab_main_r

                # Cote gauche
                tab_main_l = translate([-(face / 2 + (usable_main_left - tab_len_main) / 2
                                          + tab_len_main),
                                        (face - tab_w) / 2, -tab_d])(
                    cube([tab_len_main, tab_w, tab_d])
                )
                model = model + tab_main_l

            # Tab sur la face interne de la branche
            tab_len_branch = branch_len * 0.5
            if tab_len_branch > 5:
                tab_branch = translate([-(tab_d + wt / 2),
                                        face + (usable_branch - tab_len_branch) / 2,
                                        (face - tab_w) / 2])(
                    cube([tab_d, tab_len_branch, tab_w])
                )
                model = model + tab_branch

        # -- Miroir si necessaire --
        if p['mirror']:
            model = mirror([1, 0, 0])(model)

        return model


if __name__ == "__main__":
    import sys
    joint = BoothTJoint()
    print(f"Generation connecteur en T booth...")
    print(f"Parametres: {joint.params}")
    scad_path = joint.save_scad()
    print(f"SCAD: {scad_path}")
    try:
        stl_path = joint.render_stl()
        print(f"STL: {stl_path}")
        print("OK")
    except Exception as e:
        print(f"Erreur STL: {e}", file=sys.stderr)
