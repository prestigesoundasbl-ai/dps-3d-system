"""
Plaque Nominative / Enseigne Logo Parametrique
Plaque rectangulaire avec texte en relief ou grave.
Specifications par defaut:
  - Largeur: 150mm, Hauteur: 50mm
  - Texte: "DJ PRESTIGE SOUND"
  - Style relief ou gravure
  - Cadre decoratif optionnel
"""
from solid2 import *
from ..base import ParametricModel
from ..brand import (
    BRAND_NAME, DEFAULT_TEXT_DEPTH, DEFAULT_TEXT_FONT
)
from ..utils import rounded_box
from ..logo import logo_engrave, logo_relief


class LogoNameplate(ParametricModel):

    def __init__(self, **params):
        super().__init__("logo_nameplate", **params)

    def default_params(self):
        return {
            'width': 150.0,
            'height': 50.0,
            'thickness': 5.0,
            'text': BRAND_NAME,
            'style': 'relief',
            'text_size': 10.0,
            'text_depth': 2.0,
            'border_width': 3.0,
            'border_height': 1.5,
            'corner_radius': 3.0,
            'mounting_holes': True,
            'mounting_hole_diameter': 4.0,
            'use_logo': True,
            'logo_width': 0.0,
        }

    def param_schema(self):
        return {
            'width': {
                'type': 'float', 'min': 80, 'max': 400, 'unit': 'mm',
                'description': 'Largeur de la plaque'
            },
            'height': {
                'type': 'float', 'min': 25, 'max': 150, 'unit': 'mm',
                'description': 'Hauteur de la plaque'
            },
            'thickness': {
                'type': 'float', 'min': 3, 'max': 10, 'unit': 'mm',
                'description': 'Epaisseur de la plaque'
            },
            'text': {
                'type': 'string',
                'description': 'Texte a afficher'
            },
            'style': {
                'type': 'string',
                'description': 'Style: relief (texte en saillie) ou engrave (texte creuse)'
            },
            'text_size': {
                'type': 'float', 'min': 5, 'max': 30, 'unit': 'mm',
                'description': 'Taille du texte'
            },
            'text_depth': {
                'type': 'float', 'min': 0.5, 'max': 4, 'unit': 'mm',
                'description': 'Profondeur/hauteur du texte'
            },
            'border_width': {
                'type': 'float', 'min': 0, 'max': 10, 'unit': 'mm',
                'description': 'Largeur du cadre decoratif (0 = pas de cadre)'
            },
            'border_height': {
                'type': 'float', 'min': 0.5, 'max': 3, 'unit': 'mm',
                'description': 'Hauteur du cadre au-dessus de la plaque'
            },
            'corner_radius': {
                'type': 'float', 'min': 0, 'max': 10, 'unit': 'mm',
                'description': 'Rayon des coins arrondis'
            },
            'mounting_holes': {
                'type': 'bool',
                'description': 'Ajouter des trous de montage'
            },
            'mounting_hole_diameter': {
                'type': 'float', 'min': 2, 'max': 6, 'unit': 'mm',
                'description': 'Diametre des trous de montage'
            },
            'use_logo': {
                'type': 'boolean',
                'description': 'Utiliser le vrai logo SVG Prestige Sound'
            },
            'logo_width': {
                'type': 'float', 'min': 0, 'max': 200, 'unit': 'mm',
                'description': 'Largeur du logo (0=auto 70% largeur plaque)'
            },
        }

    def build(self):
        p = self.params
        w = p['width']
        h = p['height']
        t = p['thickness']
        ts = p['text_size']
        td = p['text_depth']
        bw = p['border_width']
        bh = p['border_height']
        cr = p['corner_radius']

        # -- Plaque de base --
        plate = rounded_box(w, h, t, cr)

        # -- Cadre decoratif (rebord sureleve) --
        if bw > 0:
            border_outer = rounded_box(w, h, t + bh, cr)
            border_inner = translate([bw, bw, 0])(
                rounded_box(w - 2 * bw, h - 2 * bw, t + bh + 0.1, max(0, cr - bw))
            )
            border = border_outer - border_inner
            # Ne garder que la partie au-dessus de la plaque
            # En fait le cadre englobe la plaque, on combine
            plate = plate + border

        # -- Logo ou Texte --
        if p.get('use_logo', False):
            logo_w = p['logo_width'] if p['logo_width'] > 0 else w * 0.7
            if p['style'] == 'relief':
                logo_obj = logo_relief(width=logo_w, depth=td)
                logo_obj = translate([w / 2, h / 2, t])(logo_obj)
                plate = plate + logo_obj
            else:
                logo_obj = logo_engrave(width=logo_w, depth=td)
                logo_obj = translate([w / 2, h / 2, t - td])(logo_obj)
                plate = plate - logo_obj
        elif p['text']:
            txt = linear_extrude(height=td + 0.1)(
                text(p['text'],
                     size=ts,
                     font=DEFAULT_TEXT_FONT,
                     halign="center",
                     valign="center",
                     _fn=64)
            )
            txt = translate([w / 2, h / 2, 0])(txt)

            if p['style'] == 'relief':
                txt = translate([0, 0, t])(txt)
                plate = plate + txt
            else:
                txt = translate([0, 0, t - td])(txt)
                plate = plate - txt

        # -- Trous de montage --
        if p['mounting_holes']:
            hole_d = p['mounting_hole_diameter']
            margin = bw + hole_d
            # Quatre coins
            positions = [
                [margin, margin],
                [w - margin, margin],
                [margin, h - margin],
                [w - margin, h - margin],
            ]
            for pos in positions:
                hole = translate([pos[0], pos[1], -0.1])(
                    cylinder(d=hole_d, h=t + 0.4, _fn=32)
                )
                # Fraisage
                countersink = translate([pos[0], pos[1], -0.1])(
                    cylinder(d1=hole_d * 2, d2=hole_d, h=t * 0.4, _fn=32)
                )
                plate = plate - hole - countersink

        return plate


if __name__ == "__main__":
    import sys
    np = LogoNameplate()
    print(f"Generation de la plaque nominative...")
    print(f"Parametres: {np.params}")

    scad_path = np.save_scad()
    print(f"SCAD: {scad_path}")

    try:
        stl_path = np.render_stl()
        print(f"STL: {stl_path}")
        print("OK - Modele genere avec succes!")
    except Exception as e:
        print(f"Erreur STL (OpenSCAD requis): {e}", file=sys.stderr)
        print("Le fichier SCAD a ete genere, OpenSCAD est necessaire pour le STL.")
