"""
Clip de Cable DPS Prestige — Style KLAMMA modifie
Clip verrouillable avec base plate pour Dual Lock adhesif.
Rainure accent or sur les bords, gravure DPS optionnelle.
Specifications par defaut:
  - 2 tailles: petit (5mm) et grand (8mm)
  - Base plate pour fixation Dual Lock
  - Levre snap-fit pour verrouillage cable
  - Coins arrondis R=3mm
  - Rainure accent 0.5mm sur les bords
"""
import math
from solid2 import *
from ..base import ParametricModel
from ..brand import (
    BRAND_NAME_SHORT, DEFAULT_TEXT_DEPTH, DEFAULT_TEXT_FONT,
    DEFAULT_CORNER_RADIUS, COLOR_GOLD
)
from ..utils import rounded_box, brand_text


class DPSCableClip(ParametricModel):

    def __init__(self, **params):
        super().__init__("dps_cable_clip", **params)

    def default_params(self):
        return {
            'cable_diameter': 8.0,       # Grand par defaut (alim ~7mm + marge)
            'wall_thickness': 2.0,
            'length': 20.0,
            'base_width': 25.0,
            'base_depth': 20.0,
            'base_thickness': 2.5,
            'corner_radius': 3.0,
            'opening_angle': 80.0,       # Ouverture snap-fit
            'lip_thickness': 0.8,        # Levre de retention
            'accent_groove_depth': 0.5,  # Rainure accent or
            'accent_groove_width': 0.8,
            'engrave_dps': False,        # Gravure DPS sur la base
            'export_part': 'all',        # 'all', 'small', 'large'
        }

    def param_schema(self):
        return {
            'cable_diameter': {
                'type': 'float', 'min': 3, 'max': 15, 'unit': 'mm',
                'description': 'Diametre du cable (petit=5, grand=8)'
            },
            'wall_thickness': {
                'type': 'float', 'min': 1.2, 'max': 4, 'unit': 'mm',
                'description': 'Epaisseur de la paroi du clip'
            },
            'length': {
                'type': 'float', 'min': 10, 'max': 40, 'unit': 'mm',
                'description': 'Longueur du clip (axe du cable)'
            },
            'base_width': {
                'type': 'float', 'min': 15, 'max': 40, 'unit': 'mm',
                'description': 'Largeur de la base Dual Lock'
            },
            'base_depth': {
                'type': 'float', 'min': 15, 'max': 35, 'unit': 'mm',
                'description': 'Profondeur de la base Dual Lock'
            },
            'base_thickness': {
                'type': 'float', 'min': 1.5, 'max': 5, 'unit': 'mm',
                'description': 'Epaisseur de la base'
            },
            'corner_radius': {
                'type': 'float', 'min': 0, 'max': 5, 'unit': 'mm',
                'description': 'Rayon des coins arrondis'
            },
            'opening_angle': {
                'type': 'float', 'min': 60, 'max': 120, 'unit': 'deg',
                'description': 'Angle d\'ouverture pour insertion cable'
            },
            'lip_thickness': {
                'type': 'float', 'min': 0.4, 'max': 1.5, 'unit': 'mm',
                'description': 'Epaisseur de la levre snap-fit'
            },
            'accent_groove_depth': {
                'type': 'float', 'min': 0, 'max': 1, 'unit': 'mm',
                'description': 'Profondeur de la rainure accent or'
            },
            'accent_groove_width': {
                'type': 'float', 'min': 0, 'max': 2, 'unit': 'mm',
                'description': 'Largeur de la rainure accent'
            },
            'engrave_dps': {
                'type': 'bool',
                'description': 'Graver DPS sur la base'
            },
            'export_part': {
                'type': 'string',
                'description': 'Piece a exporter: all, small, large'
            },
        }

    def _build_clip(self, cable_d):
        """Construit un clip pour un diametre de cable donne."""
        p = self.params
        wt = p['wall_thickness']
        length = p['length']
        bw = p['base_width']
        bd = p['base_depth']
        bt = p['base_thickness']
        cr = p['corner_radius']
        opening = p['opening_angle']
        lip_t = p['lip_thickness']
        groove_d = p['accent_groove_depth']
        groove_w = p['accent_groove_width']

        outer_r = cable_d / 2 + wt
        inner_r = cable_d / 2 + 0.2  # 0.2mm clearance pour le cable

        # -- Anneau C (clip principal) --
        outer_cyl = cylinder(r=outer_r, h=length, _fn=64)
        inner_cyl = cylinder(r=inner_r, h=length + 0.2, _fn=64)

        # Couper l'ouverture en haut (secteur angulaire)
        half_angle = opening / 2
        cut_size = outer_r + 2
        cut_block = translate([0, 0, -0.1])(
            cube([cut_size, cut_size, length + 0.4])
        )
        cut1 = rotate([0, 0, 90 - half_angle])(cut_block)
        cut2 = rotate([0, 0, 90 + half_angle])(
            mirror([1, 0, 0])(cut_block)
        )
        clip_ring = outer_cyl - inner_cyl - cut1 - cut2

        # -- Levres snap-fit a l'entree de l'ouverture --
        lip_r = inner_r + lip_t
        lip_cyl = cylinder(r=lip_r, h=length, _fn=64) - cylinder(
            r=inner_r, h=length + 0.2, _fn=64
        )
        lip_sector_angle = 12
        # Levre gauche
        lk1 = rotate([0, 0, 90 - half_angle - lip_sector_angle])(
            translate([0, 0, -0.1])(cube([cut_size, cut_size, length + 0.4]))
        )
        lk2 = rotate([0, 0, 90 - half_angle])(
            mirror([1, 0, 0])(
                translate([0, 0, -0.1])(cube([cut_size, cut_size, length + 0.4]))
            )
        )
        lip_left = lip_cyl & lk1 & lk2
        # Levre droite
        lk3 = rotate([0, 0, 90 + half_angle])(
            translate([0, 0, -0.1])(cube([cut_size, cut_size, length + 0.4]))
        )
        lk4 = rotate([0, 0, 90 + half_angle + lip_sector_angle])(
            mirror([1, 0, 0])(
                translate([0, 0, -0.1])(cube([cut_size, cut_size, length + 0.4]))
            )
        )
        lip_right = lip_cyl & lk3 & lk4

        clip = clip_ring + lip_left + lip_right

        # Positionner le clip au-dessus de la base
        # Le centre du clip est a z=0 de l'anneau, on le monte
        clip = translate([0, 0, bt])(clip)

        # -- Base plate avec coins arrondis --
        base = translate([-bw / 2, -bd / 2, 0])(
            rounded_box(bw, bd, bt, cr)
        )

        # Transition: petits renforts entre base et anneau
        fillet_w = wt
        fillet_h = 3.0
        fillet_l = translate([-outer_r - fillet_w / 2, -fillet_w / 2, bt])(
            hull()(
                cube([fillet_w, fillet_w, 0.1]),
                translate([fillet_w / 2, 0, fillet_h])(
                    cube([0.1, fillet_w, 0.1])
                )
            )
        )
        fillet_r = translate([outer_r - fillet_w / 2, -fillet_w / 2, bt])(
            hull()(
                cube([fillet_w, fillet_w, 0.1]),
                translate([-fillet_w / 2 + fillet_w, 0, fillet_h])(
                    cube([0.1, fillet_w, 0.1])
                )
            )
        )

        model = clip + base + fillet_l + fillet_r

        # -- Rainures accent or sur les bords longitudinaux de la base --
        if groove_d > 0 and groove_w > 0:
            # Rainure avant
            groove_front = translate([-bw / 2 + cr, -bd / 2 - 0.1,
                                      bt - groove_d])(
                cube([bw - 2 * cr, groove_w + 0.1, groove_d + 0.1])
            )
            # Rainure arriere
            groove_back = translate([-bw / 2 + cr, bd / 2 - groove_w,
                                     bt - groove_d])(
                cube([bw - 2 * cr, groove_w + 0.1, groove_d + 0.1])
            )
            model = model - groove_front - groove_back

        # -- Gravure DPS optionnelle sur le dessus de la base --
        if p['engrave_dps']:
            dps_text = linear_extrude(height=0.6 + 0.1)(
                text("DPS", size=4, font=DEFAULT_TEXT_FONT,
                     halign="center", valign="center", _fn=32)
            )
            # Positionner sur la base, devant le clip
            dps_text = translate([0, -bd / 2 + 5, bt - 0.6])(dps_text)
            model = model - dps_text

        return model

    def build(self):
        p = self.params
        export = p['export_part']

        if export == 'small':
            return self._build_clip(5.0)
        elif export == 'large':
            return self._build_clip(8.0)
        else:
            # Par defaut: utiliser le diametre parametre
            return self._build_clip(p['cable_diameter'])


if __name__ == "__main__":
    import sys

    # Generer les deux tailles
    for size_name, diameter in [('small', 5.0), ('large', 8.0)]:
        clip = DPSCableClip(cable_diameter=diameter, export_part=size_name)
        clip.name = f"dps_cable_clip_{size_name}"
        print(f"Generation clip {size_name} (Ø{diameter}mm)...")
        scad_path = clip.save_scad()
        print(f"  SCAD: {scad_path}")
        try:
            stl_path = clip.render_stl()
            print(f"  STL: {stl_path}")
        except Exception as e:
            print(f"  Erreur STL: {e}", file=sys.stderr)

    print("OK - Clips DPS generes!")
