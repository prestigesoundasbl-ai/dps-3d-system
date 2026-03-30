"""
Clip de Gestion de Cables Parametrique
Clip en forme de C pour maintenir les cables DJ.
Specifications par defaut:
  - Diametre cable: 6mm
  - Epaisseur paroi: 2mm
  - Longueur: 20mm
  - Type de montage: vis ou adhesif
  - Ouverture ~90 degres pour insertion snap-fit
"""
import math
from solid2 import *
from ..base import ParametricModel
from ..brand import (
    BRAND_NAME_SHORT, DEFAULT_TEXT_DEPTH, DEFAULT_TEXT_FONT,
    DEFAULT_WALL_THICKNESS
)


class CableClip(ParametricModel):

    def __init__(self, **params):
        super().__init__("cable_clip", **params)

    def default_params(self):
        return {
            'cable_diameter': 6.0,
            'wall_thickness': 2.0,
            'length': 20.0,
            'mount_type': 'screw',
            'screw_hole_diameter': 3.5,
            'base_width': 20.0,
            'base_thickness': 3.0,
            'opening_angle': 90.0,
        }

    def param_schema(self):
        return {
            'cable_diameter': {
                'type': 'float', 'min': 3, 'max': 20, 'unit': 'mm',
                'description': 'Diametre du cable a maintenir'
            },
            'wall_thickness': {
                'type': 'float', 'min': 1, 'max': 5, 'unit': 'mm',
                'description': 'Epaisseur de la paroi du clip'
            },
            'length': {
                'type': 'float', 'min': 10, 'max': 60, 'unit': 'mm',
                'description': 'Longueur du clip'
            },
            'mount_type': {
                'type': 'string',
                'description': 'Type de montage: screw ou adhesive'
            },
            'screw_hole_diameter': {
                'type': 'float', 'min': 2, 'max': 6, 'unit': 'mm',
                'description': 'Diametre du trou de vis (si montage vis)'
            },
            'base_width': {
                'type': 'float', 'min': 10, 'max': 40, 'unit': 'mm',
                'description': 'Largeur de la base plate'
            },
            'base_thickness': {
                'type': 'float', 'min': 2, 'max': 6, 'unit': 'mm',
                'description': 'Epaisseur de la base'
            },
            'opening_angle': {
                'type': 'float', 'min': 60, 'max': 120, 'unit': 'deg',
                'description': 'Angle d\'ouverture du clip pour insertion'
            },
        }

    def build(self):
        p = self.params
        cd = p['cable_diameter']
        wt = p['wall_thickness']
        length = p['length']
        bw = p['base_width']
        bt = p['base_thickness']
        opening = p['opening_angle']

        outer_r = cd / 2 + wt
        inner_r = cd / 2

        # -- Clip en forme de C --
        # Cylindre exterieur plein
        outer_cyl = cylinder(r=outer_r, h=length, _fn=64)
        # Cylindre interieur a soustraire (le passage cable)
        inner_cyl = cylinder(r=inner_r, h=length + 0.2, _fn=64)

        # Bloc pour creer l'ouverture du clip (coupe un secteur)
        # L'ouverture est centree en haut, on coupe un secteur de opening_angle
        half_angle = opening / 2
        cut_size = outer_r + 2
        # On cree deux plans de coupe qui forment le secteur d'ouverture
        cut_block = translate([0, 0, -0.1])(
            cube([cut_size, cut_size, length + 0.4])
        )
        # Premier plan de coupe (rotation depuis le haut)
        cut1 = rotate([0, 0, 90 - half_angle])(cut_block)
        # Deuxieme plan de coupe (symetrique)
        cut2 = rotate([0, 0, 90 + half_angle])(
            mirror([1, 0, 0])(cut_block)
        )

        # Assemblage du clip: anneau complet moins l'ouverture
        clip_ring = outer_cyl - inner_cyl - cut1 - cut2

        # Petites levres a l'interieur de l'ouverture pour snap-fit
        lip_r = inner_r + wt * 0.3
        lip_thickness = wt * 0.4
        lip = cylinder(r=lip_r, h=length, _fn=64) - cylinder(
            r=lip_r - lip_thickness, h=length + 0.2, _fn=64
        )
        # On ne garde que les petites zones pres de l'ouverture
        lip_cut_size = outer_r + 2
        lip_sector_angle = 15  # degres de chaque cote
        lip_keep1 = rotate([0, 0, 90 - half_angle - lip_sector_angle])(
            translate([0, 0, -0.1])(
                cube([lip_cut_size, lip_cut_size, length + 0.4])
            )
        )
        lip_keep2 = rotate([0, 0, 90 - half_angle])(
            mirror([1, 0, 0])(
                translate([0, 0, -0.1])(
                    cube([lip_cut_size, lip_cut_size, length + 0.4])
                )
            )
        )
        lip_left = lip & lip_keep1 & lip_keep2

        lip_keep3 = rotate([0, 0, 90 + half_angle])(
            translate([0, 0, -0.1])(
                cube([lip_cut_size, lip_cut_size, length + 0.4])
            )
        )
        lip_keep4 = rotate([0, 0, 90 + half_angle + lip_sector_angle])(
            mirror([1, 0, 0])(
                translate([0, 0, -0.1])(
                    cube([lip_cut_size, lip_cut_size, length + 0.4])
                )
            )
        )
        lip_right = lip & lip_keep3 & lip_keep4

        clip = clip_ring + lip_left + lip_right

        # -- Base plate --
        # La base est au bas du clip (y negatif), plate
        base = translate([-bw / 2, -outer_r - bt, 0])(
            cube([bw, bt, length])
        )

        # Transition arrondie entre clip et base
        fillet = translate([0, -outer_r, 0])(
            cube([bw * 0.3, bt, length], center=True)
        )

        model = clip + base

        # -- Trou de montage (vis) ou surface plate (adhesif) --
        if p['mount_type'] == 'screw':
            hole_d = p['screw_hole_diameter']
            # Trou au centre de la base
            screw_hole = translate([0, -outer_r - bt / 2, length / 2])(
                rotate([0, 0, 0])(
                    cylinder(d=hole_d, h=bt + 0.4, _fn=32, center=True)
                )
            )
            # Orienter le trou vers le bas (a travers l'epaisseur de la base)
            screw_hole = translate([0, -outer_r - bt - 0.1, length / 2])(
                rotate([-90, 0, 0])(
                    cylinder(d=hole_d, h=bt + 0.4, _fn=32)
                )
            )
            model = model - screw_hole

        return model


if __name__ == "__main__":
    import sys
    clip = CableClip()
    print(f"Generation du clip cable...")
    print(f"Parametres: {clip.params}")

    scad_path = clip.save_scad()
    print(f"SCAD: {scad_path}")

    try:
        stl_path = clip.render_stl()
        print(f"STL: {stl_path}")
        print("OK - Modele genere avec succes!")
    except Exception as e:
        print(f"Erreur STL (OpenSCAD requis): {e}", file=sys.stderr)
        print("Le fichier SCAD a ete genere, OpenSCAD est necessaire pour le STL.")
