"""
Base de Trophee/Recompense Parametrique
Socle multi-niveaux pour trophees et prix corporate.
Specifications par defaut:
  - Largeur: 100mm, Profondeur: 80mm
  - 1 a 3 niveaux empiles
  - Texte grave sur la face avant du niveau superieur
  - Chanfreins elegants
"""
from solid2 import *
from ..base import ParametricModel
from ..brand import (
    BRAND_NAME, DEFAULT_TEXT_DEPTH, DEFAULT_TEXT_FONT
)
from ..utils import chamfered_box
from ..logo import logo_engrave


class TrophyBase(ParametricModel):

    def __init__(self, **params):
        super().__init__("trophy_base", **params)

    def default_params(self):
        return {
            'width': 100.0,
            'depth': 80.0,
            'height': 30.0,
            'tiers': 1,
            'text_line1': BRAND_NAME,
            'text_line2': '',
            'text_size': 6.0,
            'chamfer': 2.0,
            'tier_inset': 8.0,
            'mounting_hole': False,
            'mounting_hole_diameter': 5.0,
            'mounting_hole_depth': 15.0,
            'use_logo': True,
            'logo_width': 0.0,
        }

    def param_schema(self):
        return {
            'width': {
                'type': 'float', 'min': 50, 'max': 200, 'unit': 'mm',
                'description': 'Largeur de la base (niveau le plus grand)'
            },
            'depth': {
                'type': 'float', 'min': 40, 'max': 150, 'unit': 'mm',
                'description': 'Profondeur de la base'
            },
            'height': {
                'type': 'float', 'min': 15, 'max': 60, 'unit': 'mm',
                'description': 'Hauteur totale de la base'
            },
            'tiers': {
                'type': 'int', 'min': 1, 'max': 3, 'unit': '',
                'description': 'Nombre de niveaux empiles'
            },
            'text_line1': {
                'type': 'string',
                'description': 'Premiere ligne de texte (face avant)'
            },
            'text_line2': {
                'type': 'string',
                'description': 'Deuxieme ligne de texte (optionnelle)'
            },
            'text_size': {
                'type': 'float', 'min': 3, 'max': 12, 'unit': 'mm',
                'description': 'Taille du texte'
            },
            'chamfer': {
                'type': 'float', 'min': 0, 'max': 5, 'unit': 'mm',
                'description': 'Taille du chanfrein sur les aretes'
            },
            'tier_inset': {
                'type': 'float', 'min': 3, 'max': 15, 'unit': 'mm',
                'description': 'Retrait de chaque niveau superieur'
            },
            'mounting_hole': {
                'type': 'bool',
                'description': 'Trou de montage au centre du dessus'
            },
            'mounting_hole_diameter': {
                'type': 'float', 'min': 3, 'max': 10, 'unit': 'mm',
                'description': 'Diametre du trou de montage'
            },
            'mounting_hole_depth': {
                'type': 'float', 'min': 5, 'max': 30, 'unit': 'mm',
                'description': 'Profondeur du trou de montage'
            },
            'use_logo': {
                'type': 'boolean',
                'description': 'Utiliser le vrai logo SVG sur la face avant'
            },
            'logo_width': {
                'type': 'float', 'min': 0, 'max': 100, 'unit': 'mm',
                'description': 'Largeur du logo (0=auto 60% largeur)'
            },
        }

    def build(self):
        p = self.params
        w = p['width']
        d = p['depth']
        h = p['height']
        tiers = p['tiers']
        chamf = p['chamfer']
        inset = p['tier_inset']
        ts = p['text_size']

        tier_h = h / tiers
        model = None

        z_offset = 0
        for i in range(tiers):
            # Chaque niveau est plus petit (en retrait)
            tier_inset = inset * i
            tw = w - 2 * tier_inset
            td = d - 2 * tier_inset

            # Creation du niveau avec chanfrein
            tier = chamfered_box(tw, td, tier_h, chamf)

            # Positionner: centrer le retrait et empiler en Z
            tier = translate([tier_inset, tier_inset, z_offset])(tier)

            if model is None:
                model = tier
            else:
                model = model + tier

            z_offset += tier_h

        # -- Texte grave sur la face avant du niveau superieur --
        top_inset = inset * (tiers - 1)
        top_w = w - 2 * top_inset
        top_z = h - tier_h  # Base Z du dernier niveau

        if p.get('use_logo', False) and not p['text_line2']:
            # Logo SVG grave sur la face avant
            logo_w = p['logo_width'] if p['logo_width'] > 0 else top_w * 0.6
            logo_obj = logo_engrave(width=logo_w, depth=DEFAULT_TEXT_DEPTH)
            logo_obj = rotate([90, 0, 0])(logo_obj)
            logo_obj = translate([
                top_inset + top_w / 2,
                top_inset - 0.05,
                top_z + tier_h / 2
            ])(logo_obj)
            model = model - logo_obj
        else:
            if p['text_line1']:
                txt1 = linear_extrude(height=DEFAULT_TEXT_DEPTH + 0.1)(
                    text(p['text_line1'],
                         size=ts,
                         font=DEFAULT_TEXT_FONT,
                         halign="center",
                         valign="center",
                         _fn=64)
                )
                txt1 = rotate([90, 0, 0])(txt1)

                if p['text_line2']:
                    txt1 = translate([
                        top_inset + top_w / 2,
                        top_inset - 0.05,
                        top_z + tier_h * 0.6
                    ])(txt1)
                else:
                    txt1 = translate([
                        top_inset + top_w / 2,
                        top_inset - 0.05,
                        top_z + tier_h / 2
                    ])(txt1)
                model = model - txt1

            if p['text_line2']:
                txt2 = linear_extrude(height=DEFAULT_TEXT_DEPTH + 0.1)(
                    text(p['text_line2'],
                         size=ts * 0.8,
                         font=DEFAULT_TEXT_FONT,
                         halign="center",
                         valign="center",
                         _fn=64)
                )
                txt2 = rotate([90, 0, 0])(txt2)
                txt2 = translate([
                    top_inset + top_w / 2,
                    top_inset - 0.05,
                    top_z + tier_h * 0.3
                ])(txt2)
                model = model - txt2

        # -- Trou de montage (pour fixer un trophee/figurine) --
        if p['mounting_hole']:
            hole_d = p['mounting_hole_diameter']
            hole_depth = p['mounting_hole_depth']
            hole = translate([w / 2, d / 2, h - hole_depth])(
                cylinder(d=hole_d, h=hole_depth + 0.1, _fn=32)
            )
            model = model - hole

        return model


if __name__ == "__main__":
    import sys
    tb = TrophyBase(tiers=2, text_line2="Award 2026")
    print(f"Generation de la base de trophee...")
    print(f"Parametres: {tb.params}")

    scad_path = tb.save_scad()
    print(f"SCAD: {scad_path}")

    try:
        stl_path = tb.render_stl()
        print(f"STL: {stl_path}")
        print("OK - Modele genere avec succes!")
    except Exception as e:
        print(f"Erreur STL (OpenSCAD requis): {e}", file=sys.stderr)
        print("Le fichier SCAD a ete genere, OpenSCAD est necessaire pour le STL.")
