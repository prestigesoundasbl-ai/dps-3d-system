"""
Base de Cake Topper Parametrique
Disque avec tiges d'insertion pour decoration de gateau.
Specifications par defaut:
  - Diametre disque: 60mm
  - Hauteur: 8mm
  - 2 tiges de 40mm pour insertion dans le gateau
  - Texte optionnel sur le dessus
"""
from solid2 import *
from ..base import ParametricModel
from ..brand import (
    BRAND_NAME_SHORT, DEFAULT_TEXT_DEPTH, DEFAULT_TEXT_FONT
)


class CakeTopperBase(ParametricModel):

    def __init__(self, **params):
        super().__init__("cake_topper_base", **params)

    def default_params(self):
        return {
            'diameter': 60.0,
            'height': 8.0,
            'spike_length': 40.0,
            'spike_count': 2,
            'spike_diameter': 3.0,
            'top_text': '',
            'top_text_size': 6.0,
            'border_width': 2.0,
            'border_height': 1.5,
            'food_safe_note': True,
        }

    def param_schema(self):
        return {
            'diameter': {
                'type': 'float', 'min': 30, 'max': 120, 'unit': 'mm',
                'description': 'Diametre du disque de base'
            },
            'height': {
                'type': 'float', 'min': 4, 'max': 15, 'unit': 'mm',
                'description': 'Epaisseur du disque'
            },
            'spike_length': {
                'type': 'float', 'min': 20, 'max': 80, 'unit': 'mm',
                'description': 'Longueur des tiges d\'insertion'
            },
            'spike_count': {
                'type': 'int', 'min': 1, 'max': 4, 'unit': '',
                'description': 'Nombre de tiges'
            },
            'spike_diameter': {
                'type': 'float', 'min': 2, 'max': 6, 'unit': 'mm',
                'description': 'Diametre des tiges'
            },
            'top_text': {
                'type': 'string',
                'description': 'Texte optionnel sur le dessus du disque'
            },
            'top_text_size': {
                'type': 'float', 'min': 3, 'max': 12, 'unit': 'mm',
                'description': 'Taille du texte sur le dessus'
            },
            'border_width': {
                'type': 'float', 'min': 1, 'max': 5, 'unit': 'mm',
                'description': 'Largeur du rebord decoratif'
            },
            'border_height': {
                'type': 'float', 'min': 0.5, 'max': 3, 'unit': 'mm',
                'description': 'Hauteur du rebord au-dessus du disque'
            },
            'food_safe_note': {
                'type': 'bool',
                'description': 'Note rappel: utiliser filament food-safe'
            },
        }

    def build(self):
        p = self.params
        d = p['diameter']
        h = p['height']
        sl = p['spike_length']
        sc = p['spike_count']
        sd = p['spike_diameter']
        bw = p['border_width']
        bh = p['border_height']

        r = d / 2

        # -- Disque principal --
        disc = cylinder(d=d, h=h, _fn=64)

        # -- Rebord decoratif autour du disque --
        border_outer = cylinder(d=d, h=h + bh, _fn=64)
        border_inner = cylinder(d=d - 2 * bw, h=h + bh + 0.1, _fn=64)
        border_ring = border_outer - border_inner
        # On ne garde que la partie au-dessus du disque
        border = translate([0, 0, 0])(border_ring)

        model = disc + border

        # -- Tiges d'insertion (pointent vers le bas, sous le disque) --
        # Reparties uniformement sous le disque
        import math
        for i in range(sc):
            if sc == 1:
                # Une seule tige au centre
                sx, sy = 0, 0
            else:
                # Repartition sur un cercle
                spike_r = r * 0.4  # Rayon du cercle des tiges
                angle = (2 * math.pi * i) / sc
                sx = spike_r * math.cos(angle)
                sy = spike_r * math.sin(angle)

            spike = translate([sx, sy, -sl])(
                cylinder(d=sd, h=sl, _fn=32)
            )
            # Pointe conique pour faciliter l'insertion
            tip = translate([sx, sy, -sl - sd])(
                cylinder(d1=0, d2=sd, h=sd, _fn=32)
            )
            model = model + spike + tip

        # -- Texte optionnel sur le dessus --
        if p['top_text']:
            txt = linear_extrude(height=DEFAULT_TEXT_DEPTH + 0.1)(
                text(p['top_text'],
                     size=p['top_text_size'],
                     font=DEFAULT_TEXT_FONT,
                     halign="center",
                     valign="center",
                     _fn=64)
            )
            # En relief sur le dessus du disque
            txt = translate([0, 0, h + bh])(txt)
            model = model + txt

        return model


if __name__ == "__main__":
    import sys
    ct = CakeTopperBase(top_text="Love")
    print(f"Generation de la base cake topper...")
    print(f"Parametres: {ct.params}")

    scad_path = ct.save_scad()
    print(f"SCAD: {scad_path}")

    try:
        stl_path = ct.render_stl()
        print(f"STL: {stl_path}")
        print("OK - Modele genere avec succes!")
    except Exception as e:
        print(f"Erreur STL (OpenSCAD requis): {e}", file=sys.stderr)
        print("Le fichier SCAD a ete genere, OpenSCAD est necessaire pour le STL.")
