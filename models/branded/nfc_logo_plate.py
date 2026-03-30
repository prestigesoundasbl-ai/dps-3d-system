"""
NFC Logo Plate — Edition Prestige Sound K2 Pro
================================================
Plaque avec texte PRESTIGE SOUND en relief + cavité NFC arrière.
Multi-couleur : base noire, texte or en relief.
"""
import os
import sys
import math

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from build123d import *
from models.build_base import BuildParametricModel
from models.brand import LOGO_TEXT_PRIMARY, LOGO_TEXT_SECONDARY


class NfcLogoPlate(BuildParametricModel):
    """Plaque logo multi-couleur avec texte en relief et cavité NFC."""

    def __init__(self, **params):
        super().__init__("nfc_logo_plate", **params)

    def default_params(self) -> dict:
        return {
            'width': 120.0,
            'height': 50.0,
            'base_t': 3.0,
            'logo_relief': 1.0,
            'corner_r': 5.0,
            'nfc_diameter': 26.0,
            'nfc_depth': 1.5,
            'border_groove': True,
            'mounting': 'adhesive',
            'screw_hole_d': 3.2,
            'branding': True,
        }

    def build(self) -> Part:
        p = self.params
        w, h = p['width'], p['height']
        bt = p['base_t']
        lr = p['logo_relief']
        cr = p['corner_r']

        with BuildPart() as plate:
            # 1. Base — plaque arrondie
            with BuildSketch() as base:
                RectangleRounded(w, h, cr)
            extrude(amount=bt)

            # 2. Texte principal "PRESTIGE SOUND" en relief (sera imprimé en or)
            if p['branding']:
                top_face = plate.faces().sort_by(Axis.Z)[-1]
                with BuildSketch(Plane(top_face)) as text_sk:
                    Text(LOGO_TEXT_PRIMARY, font_size=10,
                         font="Arial", font_style=FontStyle.BOLD)
                extrude(text_sk.sketch, amount=lr, mode=Mode.ADD)

                # Texte secondaire "DJ" au-dessus
                with BuildSketch(Plane(top_face)) as dj_sk:
                    with Locations((0, 12)):
                        Text(LOGO_TEXT_SECONDARY, font_size=6,
                             font="Arial", font_style=FontStyle.BOLD)
                extrude(dj_sk.sketch, amount=lr * 0.6, mode=Mode.ADD)

                # Ligne décorative
                with BuildSketch(Plane(top_face)) as line1:
                    with Locations((0, 6)):
                        Rectangle(w * 0.6, 0.6)
                extrude(line1.sketch, amount=lr * 0.3, mode=Mode.ADD)

                with BuildSketch(Plane(top_face)) as line2:
                    with Locations((0, -8)):
                        Rectangle(w * 0.6, 0.6)
                extrude(line2.sketch, amount=lr * 0.3, mode=Mode.ADD)

            # 3. Rainure décorative (bordure)
            if p['border_groove']:
                with BuildSketch(Plane(plate.faces().sort_by(Axis.Z)[-1])) as groove_sk:
                    RectangleRounded(w - 4, h - 4, cr - 1)
                    RectangleRounded(w - 5.2, h - 5.2, cr - 1.5, mode=Mode.SUBTRACT)
                extrude(groove_sk.sketch, amount=-0.8, mode=Mode.SUBTRACT)

            # 4. Cavité NFC (face arrière)
            bottom_face = plate.faces().sort_by(Axis.Z)[0]
            nfc_x = w / 4  # Décalé à droite pour laisser le logo centré
            with BuildPart(mode=Mode.SUBTRACT):
                with Locations((nfc_x, 0, -0.1)):
                    Cylinder(p['nfc_diameter'] / 2, p['nfc_depth'] + 0.1)

            # Petit canal pour le fil d'antenne NFC
            with BuildPart(mode=Mode.SUBTRACT):
                with Locations((nfc_x, 0, p['nfc_depth'] / 2)):
                    Box(p['nfc_diameter'] + 4, 2, p['nfc_depth'])

            # 5. Icône NFC gravée à côté de la cavité (face arrière)
            # Petit symbole "((•))" pour indiquer où scanner
            with BuildPart(mode=Mode.SUBTRACT):
                with Locations((nfc_x, 0, 0)):
                    for r in [8, 11, 14]:
                        Cylinder(radius=r, height=0.5)
                    Cylinder(radius=7, height=0.6)  # Efface le centre
                    Cylinder(radius=10, height=0.6)
                    Cylinder(radius=13, height=0.6)

            # 6. Trous de montage (si vis)
            if p['mounting'] == 'screws-m3':
                total_t = bt + lr
                for sx in [-w / 2 + 8, w / 2 - 8]:
                    with BuildPart(mode=Mode.SUBTRACT):
                        with Locations((sx, 0, 0)):
                            Cylinder(p['screw_hole_d'] / 2, total_t + 1)
                    # Fraisage
                    with BuildPart(mode=Mode.SUBTRACT):
                        with Locations((sx, 0, -0.1)):
                            Cylinder(p['screw_hole_d'], 1.5)

        return plate.part


if __name__ == '__main__':
    model = NfcLogoPlate()
    model.generate()
