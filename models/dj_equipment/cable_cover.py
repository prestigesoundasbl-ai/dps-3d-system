"""
Cache-Cable pour Booth DJ Parametrique
Canal en U avec couvercle snap-fit optionnel.
Specifications par defaut:
  - Largeur canal: 40mm
  - Hauteur canal: 20mm
  - Longueur: 200mm
  - Couvercle clipsable optionnel
"""
from solid2 import *
from ..base import ParametricModel
from ..brand import (
    BRAND_NAME_SHORT, DEFAULT_TEXT_DEPTH, DEFAULT_TEXT_FONT
)
from ..logo import logo_engrave


class CableCover(ParametricModel):

    def __init__(self, **params):
        super().__init__("cable_cover", **params)

    def default_params(self):
        return {
            'channel_width': 40.0,
            'channel_height': 20.0,
            'length': 200.0,
            'wall_thickness': 2.0,
            'has_lid': True,
            'snap_height': 1.5,
            'snap_width': 2.0,
            'screw_mount': False,
            'screw_spacing': 80.0,
            'screw_hole_diameter': 3.5,
            'engrave_text': BRAND_NAME_SHORT,
            'use_logo': True,
            'logo_width': 0.0,
        }

    def param_schema(self):
        return {
            'channel_width': {
                'type': 'float', 'min': 15, 'max': 100, 'unit': 'mm',
                'description': 'Largeur interieure du canal'
            },
            'channel_height': {
                'type': 'float', 'min': 10, 'max': 60, 'unit': 'mm',
                'description': 'Hauteur interieure du canal'
            },
            'length': {
                'type': 'float', 'min': 50, 'max': 500, 'unit': 'mm',
                'description': 'Longueur du cache-cable'
            },
            'wall_thickness': {
                'type': 'float', 'min': 1.2, 'max': 5, 'unit': 'mm',
                'description': 'Epaisseur des parois'
            },
            'has_lid': {
                'type': 'bool',
                'description': 'Inclure un couvercle snap-fit'
            },
            'snap_height': {
                'type': 'float', 'min': 0.5, 'max': 3, 'unit': 'mm',
                'description': 'Hauteur du clip de fixation du couvercle'
            },
            'snap_width': {
                'type': 'float', 'min': 1, 'max': 5, 'unit': 'mm',
                'description': 'Largeur du clip de fixation'
            },
            'screw_mount': {
                'type': 'bool',
                'description': 'Ajouter des trous de vis pour fixation'
            },
            'screw_spacing': {
                'type': 'float', 'min': 30, 'max': 200, 'unit': 'mm',
                'description': 'Espacement entre les trous de vis'
            },
            'screw_hole_diameter': {
                'type': 'float', 'min': 2, 'max': 6, 'unit': 'mm',
                'description': 'Diametre des trous de vis'
            },
            'engrave_text': {
                'type': 'string',
                'description': 'Texte grave sur le couvercle'
            },
            'use_logo': {
                'type': 'boolean',
                'description': 'Utiliser le vrai logo SVG sur le couvercle'
            },
            'logo_width': {
                'type': 'float', 'min': 0, 'max': 60, 'unit': 'mm',
                'description': 'Largeur du logo (0=auto)'
            },
        }

    def build(self):
        p = self.params
        cw = p['channel_width']
        ch = p['channel_height']
        length = p['length']
        wt = p['wall_thickness']
        has_lid = p['has_lid']
        snap_h = p['snap_height']
        snap_w = p['snap_width']

        total_w = cw + 2 * wt
        total_h = ch + wt  # Fond + parois laterales (sans couvercle)

        # -- Canal en U (base) --
        outer = cube([total_w, length, total_h])
        inner = translate([wt, -0.1, wt])(
            cube([cw, length + 0.2, ch + 0.1])
        )
        channel = outer - inner

        # -- Rainures de clip sur le haut des parois laterales --
        if has_lid:
            # Petits rebords interieurs en haut des parois pour accrocher le couvercle
            # Rainure gauche
            snap_ledge_l = translate([wt - snap_w, 0, total_h - snap_h])(
                cube([snap_w, length, snap_h])
            )
            # Rainure droite
            snap_ledge_r = translate([total_w - wt, 0, total_h - snap_h])(
                cube([snap_w, length, snap_h])
            )
            channel = channel + snap_ledge_l + snap_ledge_r

        # -- Trous de vis optionnels dans le fond --
        if p['screw_mount']:
            hole_d = p['screw_hole_diameter']
            spacing = p['screw_spacing']
            num_holes = max(2, int(length / spacing) + 1)
            actual_spacing = length / (num_holes - 1) if num_holes > 1 else length / 2

            for i in range(num_holes):
                y_pos = actual_spacing * i if num_holes > 1 else length / 2
                hole = translate([total_w / 2, y_pos, -0.1])(
                    cylinder(d=hole_d, h=wt + 0.4, _fn=32)
                )
                # Fraisage pour tete de vis
                countersink = translate([total_w / 2, y_pos, -0.1])(
                    cylinder(d1=hole_d * 2, d2=hole_d, h=wt * 0.6, _fn=32)
                )
                channel = channel - hole - countersink

        # -- Couvercle (piece separee, positionnee au-dessus) --
        if has_lid:
            lid_gap = 0.3  # Jeu d'assemblage
            lid_thickness = wt
            lid_total_h = lid_thickness + snap_h

            # Plaque du couvercle
            lid_plate = translate([0, 0, total_h + 2])(
                cube([total_w, length, lid_thickness])
            )

            # Clips descendants sur les cotes du couvercle
            clip_l = translate([lid_gap, 0, total_h + 2 - snap_h])(
                cube([snap_w - lid_gap, length, snap_h])
            )
            clip_r = translate([total_w - snap_w, 0, total_h + 2 - snap_h])(
                cube([snap_w - lid_gap, length, snap_h])
            )

            lid = lid_plate + clip_l + clip_r

            # -- Gravure logo ou texte sur le dessus du couvercle --
            if p.get('use_logo', False):
                logo_w = p['logo_width'] if p['logo_width'] > 0 else total_w * 0.7
                logo_obj = logo_engrave(width=logo_w, depth=DEFAULT_TEXT_DEPTH)
                logo_obj = translate([total_w / 2, length / 2,
                                    total_h + 2 + lid_thickness - DEFAULT_TEXT_DEPTH])(logo_obj)
                lid = lid - logo_obj
            elif p['engrave_text']:
                txt = linear_extrude(height=DEFAULT_TEXT_DEPTH + 0.1)(
                    text(p['engrave_text'],
                         size=5,
                         font=DEFAULT_TEXT_FONT,
                         halign="center",
                         valign="center")
                )
                txt = translate([total_w / 2, length / 2,
                                total_h + 2 + lid_thickness - DEFAULT_TEXT_DEPTH])(txt)
                lid = lid - txt

            model = channel + lid
        else:
            model = channel

        return model


if __name__ == "__main__":
    import sys
    cover = CableCover()
    print(f"Generation du cache-cable...")
    print(f"Parametres: {cover.params}")

    scad_path = cover.save_scad()
    print(f"SCAD: {scad_path}")

    try:
        stl_path = cover.render_stl()
        print(f"STL: {stl_path}")
        print("OK - Modele genere avec succes!")
    except Exception as e:
        print(f"Erreur STL (OpenSCAD requis): {e}", file=sys.stderr)
        print("Le fichier SCAD a ete genere, OpenSCAD est necessaire pour le STL.")
