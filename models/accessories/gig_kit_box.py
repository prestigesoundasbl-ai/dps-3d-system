"""
Gig Kit Box — DJ Prestige Sound K2 Pro
========================================
Boîte de survie DJ avec compartiments visibles, logo gravé,
et couvercle emboîtable.

Compartiments :
  - Grand : adaptateurs secteur, gaffer mini
  - 2 moyens : fusibles, câble XLR spare
  - 3 petits : clés USB, pile CR2032, AirTag spare
"""
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from build123d import *
from models.build_base import BuildParametricModel
from models.brand import LOGO_TEXT_PRIMARY


class GigKitBox(BuildParametricModel):
    """Boîte de survie DJ avec compartiments et logo."""

    def __init__(self, **params):
        super().__init__("gig_kit_box", **params)

    def default_params(self) -> dict:
        return {
            'width': 200.0,
            'depth': 140.0,
            'height': 40.0,
            'wall_t': 2.5,
            'base_t': 2.0,
            'corner_r': 5.0,
            'divider_t': 1.6,
            'branding': True,
        }

    def build(self) -> Part:
        p = self.params
        w, d, h = p['width'], p['depth'], p['height']
        wt, bt = p['wall_t'], p['base_t']

        iw = w - 2 * wt
        id_ = d - 2 * wt

        with BuildPart() as box:
            # 1. Coque extérieure
            Box(w, d, h + bt)

            # 2. Évidement intérieur
            with BuildPart(mode=Mode.SUBTRACT):
                with Locations((0, 0, bt)):
                    Box(iw, id_, h + 1)

            # 3. Séparateur vertical principal (40% depuis la gauche)
            div_x = -iw / 2 + iw * 0.38
            with BuildPart(mode=Mode.ADD):
                with Locations((div_x, 0, bt + h / 2)):
                    Box(p['divider_t'], id_, h)

            # 4. Séparateur horizontal dans la partie gauche (2 zones)
            left_center = (-iw / 2 + div_x) / 2
            with BuildPart(mode=Mode.ADD):
                with Locations((left_center, 0, bt + h / 2)):
                    left_w = (div_x + iw / 2) - p['divider_t']
                    Box(left_w, p['divider_t'], h)

            # 5. Deux séparateurs horizontaux dans la partie droite (3 rangées)
            right_start = div_x + p['divider_t'] / 2
            right_center = (right_start + iw / 2) / 2
            right_w = iw / 2 - right_start
            for fy in [-id_ / 3, id_ / 3]:
                with BuildPart(mode=Mode.ADD):
                    with Locations((right_center, fy, bt + h * 0.35)):
                        Box(right_w, p['divider_t'], h * 0.7)

            # 6. Mini-séparateurs dans les petits compartiments droite
            for fy in [-id_ / 3, 0, id_ / 3]:
                with BuildPart(mode=Mode.ADD):
                    with Locations((right_center + right_w * 0.3, fy - id_ / 6, bt + h * 0.25)):
                        Box(p['divider_t'], id_ / 3 - p['divider_t'], h * 0.5)

            # 7. Gravure logo sur la face avant
            if p['branding']:
                front_face = box.faces().sort_by(Axis.Y)[-1]
                with BuildSketch(Plane(front_face)) as logo:
                    Text(LOGO_TEXT_PRIMARY, font_size=6,
                         font="Arial", font_style=FontStyle.BOLD)
                extrude(logo.sketch, amount=-1.5, mode=Mode.SUBTRACT)

            # 8. Gravure "GIG KIT" sur le fond intérieur
            if p['branding']:
                try:
                    inner_bottom = box.faces().filter_by(Axis.Z).sort_by(Axis.Z)[1]
                    with BuildSketch(Plane(inner_bottom)) as gk:
                        with Locations((-iw / 4, id_ / 4)):
                            Text("GIG KIT", font_size=8,
                                 font="Arial", font_style=FontStyle.BOLD)
                    extrude(gk.sketch, amount=-0.5, mode=Mode.SUBTRACT)
                except Exception:
                    pass

            # 9. Rebord pour couvercle (lèvre intérieure)
            lip_h = 2.0
            lip_t = 1.2
            with BuildPart(mode=Mode.ADD):
                with Locations((0, 0, bt + h)):
                    Box(iw, id_, lip_h)
                with Locations((0, 0, bt + h)):
                    Box(iw - 2 * lip_t, id_ - 2 * lip_t, lip_h + 1,
                        mode=Mode.SUBTRACT)

        return box.part

    def build_lid(self) -> Part:
        """Couvercle avec logo gravé."""
        p = self.params
        w, d = p['width'], p['depth']
        wt = p['wall_t']
        lt = 2.0

        iw = w - 2 * wt - 0.6  # Jeu
        id_ = d - 2 * wt - 0.6

        with BuildPart() as lid:
            # 1. Plaque principale
            Box(w, d, lt)

            # 2. Rebord d'emboîtement (rentre dans la lèvre de la boîte)
            with BuildPart(mode=Mode.ADD):
                with Locations((0, 0, -lt / 2 - 1.5)):
                    Box(iw, id_, 3)
                with Locations((0, 0, -lt / 2 - 1.5)):
                    Box(iw - 2.4, id_ - 2.4, 4, mode=Mode.SUBTRACT)

            # 3. Logo PRESTIGE SOUND gravé sur le dessus
            if p['branding']:
                top = lid.faces().sort_by(Axis.Z)[-1]
                with BuildSketch(Plane(top)) as logo:
                    Text(LOGO_TEXT_PRIMARY, font_size=10,
                         font="Arial", font_style=FontStyle.BOLD)
                extrude(logo.sketch, amount=-1.5, mode=Mode.SUBTRACT)

                # Ligne décorative
                with BuildSketch(Plane(top)) as deco:
                    with Locations((0, -10)):
                        Rectangle(80, 0.6)
                extrude(deco.sketch, amount=-0.5, mode=Mode.SUBTRACT)

                # "GIG KIT" en petit
                with BuildSketch(Plane(top)) as sub:
                    with Locations((0, -14)):
                        Text("GIG KIT", font_size=5,
                             font="Arial", font_style=FontStyle.BOLD)
                extrude(sub.sketch, amount=-0.8, mode=Mode.SUBTRACT)

        return lid.part


if __name__ == '__main__':
    model = GigKitBox()
    model.generate()

    # Couvercle
    from build123d import export_stl, export_step
    lid = model.build_lid()
    os.makedirs("output/stl", exist_ok=True)
    os.makedirs("output/step", exist_ok=True)
    export_stl(lid, "output/stl/gig_kit_box_lid.stl")
    export_step(lid, "output/step/gig_kit_box_lid.step")
    print("✅ Couvercle exporté : gig_kit_box_lid.stl")
