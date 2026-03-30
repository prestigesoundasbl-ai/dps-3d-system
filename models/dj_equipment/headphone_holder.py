"""
Support Casque DJ Parametrique
Crochet en J pour suspendre un casque DJ.
Specifications par defaut:
  - Largeur bandeau: 40mm
  - Profondeur crochet: 60mm
  - Epaisseur: 5mm
  - Montage: bureau (pince) ou mural (vis)
"""
from solid2 import *
from ..base import ParametricModel
from ..brand import (
    BRAND_NAME_SHORT, DEFAULT_TEXT_DEPTH, DEFAULT_TEXT_FONT
)
from ..logo import logo_engrave


class HeadphoneHolder(ParametricModel):

    def __init__(self, **params):
        super().__init__("headphone_holder", **params)

    def default_params(self):
        return {
            'headband_width': 40.0,
            'hook_depth': 60.0,
            'hook_thickness': 5.0,
            'mount_type': 'desk',
            'base_width': 40.0,
            'base_depth': 50.0,
            'base_thickness': 5.0,
            'clamp_gap': 30.0,
            'clamp_depth': 50.0,
            'screw_hole_diameter': 4.0,
            'hook_tip_radius': 8.0,
            'engrave_text': BRAND_NAME_SHORT,
            'use_logo': True,
            'logo_width': 0.0,
        }

    def param_schema(self):
        return {
            'headband_width': {
                'type': 'float', 'min': 25, 'max': 60, 'unit': 'mm',
                'description': 'Largeur du bandeau du casque'
            },
            'hook_depth': {
                'type': 'float', 'min': 30, 'max': 100, 'unit': 'mm',
                'description': 'Profondeur du crochet (combien il depasse)'
            },
            'hook_thickness': {
                'type': 'float', 'min': 3, 'max': 10, 'unit': 'mm',
                'description': 'Epaisseur du crochet'
            },
            'mount_type': {
                'type': 'string',
                'description': 'Type de montage: desk (pince) ou wall (mural)'
            },
            'base_width': {
                'type': 'float', 'min': 25, 'max': 60, 'unit': 'mm',
                'description': 'Largeur de la base/plaque murale'
            },
            'base_depth': {
                'type': 'float', 'min': 30, 'max': 80, 'unit': 'mm',
                'description': 'Profondeur de la plaque de montage'
            },
            'base_thickness': {
                'type': 'float', 'min': 3, 'max': 10, 'unit': 'mm',
                'description': 'Epaisseur de la plaque de base'
            },
            'clamp_gap': {
                'type': 'float', 'min': 15, 'max': 50, 'unit': 'mm',
                'description': 'Ecartement de la pince (epaisseur du bureau)'
            },
            'clamp_depth': {
                'type': 'float', 'min': 30, 'max': 80, 'unit': 'mm',
                'description': 'Profondeur de la pince sous le bureau'
            },
            'screw_hole_diameter': {
                'type': 'float', 'min': 3, 'max': 6, 'unit': 'mm',
                'description': 'Diametre des trous de vis (montage mural)'
            },
            'hook_tip_radius': {
                'type': 'float', 'min': 4, 'max': 15, 'unit': 'mm',
                'description': 'Rayon de l\'embout du crochet'
            },
            'engrave_text': {
                'type': 'string',
                'description': 'Texte grave sur le support'
            },
            'use_logo': {
                'type': 'boolean',
                'description': 'Utiliser le vrai logo SVG Prestige Sound'
            },
            'logo_width': {
                'type': 'float', 'min': 0, 'max': 40, 'unit': 'mm',
                'description': 'Largeur du logo (0=auto)'
            },
        }

    def build(self):
        p = self.params
        hw = p['headband_width']
        hd = p['hook_depth']
        ht = p['hook_thickness']
        bw = p['base_width']
        bd = p['base_depth']
        bt = p['base_thickness']
        tip_r = p['hook_tip_radius']

        # -- Forme en J pour le crochet --
        # Le crochet est compose de segments relies par hull()

        # Segment vertical (du mur vers le bas)
        # Point haut (fixation)
        p_top = translate([0, 0, 0])(
            cube([hw, ht, ht])
        )
        # Point milieu (transition vers horizontal)
        p_mid = translate([0, 0, -hd + tip_r])(
            cube([hw, ht, ht])
        )
        # Bras vertical
        arm_vertical = hull()(p_top, p_mid)

        # Segment courbe vers l'avant (le J)
        p_curve = translate([0, hd * 0.6, -hd + tip_r])(
            cube([hw, ht, ht])
        )
        arm_curve = hull()(p_mid, p_curve)

        # Embout arrondi (bout du J) - remonte pour retenir le casque
        p_tip = translate([0, hd * 0.6, -hd + tip_r * 3])(
            cube([hw, ht, ht])
        )
        arm_tip = hull()(p_curve, p_tip)

        hook = arm_vertical + arm_curve + arm_tip

        # Arrondi a l'embout du crochet
        tip_sphere = translate([hw / 2, hd * 0.6 + ht / 2, -hd + tip_r * 3 + ht / 2])(
            resize([hw, tip_r * 2, tip_r * 2])(
                sphere(r=tip_r, _fn=32)
            )
        )
        hook = hook + tip_sphere

        # -- Section de montage --
        if p['mount_type'] == 'desk':
            # Pince de bureau: plaque superieure + plaque inferieure
            clamp_gap = p['clamp_gap']
            clamp_d = p['clamp_depth']

            # Plaque superieure (sur le bureau)
            top_plate = translate([-bt, -clamp_d + ht, -bt])(
                cube([bt, clamp_d, hw + 2 * bt])
            )
            # Renfort entre plaque et crochet
            brace_top = hull()(
                translate([-bt, 0, 0])(cube([bt, ht, ht])),
                translate([0, 0, 0])(cube([ht, ht, ht]))
            )

            # Branche descendante de la pince
            clamp_down = translate([-bt, -clamp_d, -bt])(
                cube([bt, bt, clamp_gap + bt])
            )
            # Plaque inferieure (sous le bureau)
            clamp_bottom = translate([-bt, -clamp_d, clamp_gap])(
                cube([bt, clamp_d * 0.6, bt])
            )

            mount = top_plate + clamp_down + clamp_bottom + brace_top

        else:
            # Montage mural: plaque plate avec trous de vis
            wall_plate = translate([-bt, -bd / 2 + ht / 2, -hw * 0.3])(
                cube([bt, bd, hw * 1.6])
            )

            # Trous de vis
            hole_d = p['screw_hole_diameter']
            hole1 = translate([-bt - 0.1, bd * 0.2, hw * 0.3])(
                rotate([0, 90, 0])(
                    cylinder(d=hole_d, h=bt + 0.4, _fn=32)
                )
            )
            hole2 = translate([-bt - 0.1, bd * 0.2, hw * 0.9])(
                rotate([0, 90, 0])(
                    cylinder(d=hole_d, h=bt + 0.4, _fn=32)
                )
            )

            mount = wall_plate - hole1 - hole2

        model = hook + mount

        # -- Gravure logo ou texte --
        if p.get('use_logo', False):
            logo_w = p['logo_width'] if p['logo_width'] > 0 else hw * 0.7
            logo_obj = logo_engrave(width=logo_w, depth=DEFAULT_TEXT_DEPTH)
            logo_obj = rotate([90, 0, 90])(logo_obj)
            logo_obj = translate([-0.05, ht / 2, -hd / 2])(logo_obj)
            model = model - logo_obj
        elif p['engrave_text']:
            txt = linear_extrude(height=DEFAULT_TEXT_DEPTH + 0.1)(
                text(p['engrave_text'],
                     size=6,
                     font=DEFAULT_TEXT_FONT,
                     halign="center",
                     valign="center")
            )
            txt = rotate([90, 0, 90])(txt)
            txt = translate([-0.05, ht / 2, -hd / 2])(txt)
            model = model - txt

        return model


if __name__ == "__main__":
    import sys
    holder = HeadphoneHolder()
    print(f"Generation du support casque...")
    print(f"Parametres: {holder.params}")

    scad_path = holder.save_scad()
    print(f"SCAD: {scad_path}")

    try:
        stl_path = holder.render_stl()
        print(f"STL: {stl_path}")
        print("OK - Modele genere avec succes!")
    except Exception as e:
        print(f"Erreur STL (OpenSCAD requis): {e}", file=sys.stderr)
        print("Le fichier SCAD a ete genere, OpenSCAD est necessaire pour le STL.")
