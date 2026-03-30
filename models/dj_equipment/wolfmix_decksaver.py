"""
Decksaver Custom WolfMix W1 — Edition Prestige Sound K2 Pro
=============================================================
Capot de protection rigide pour WolfMix W1.
Multi-couleur : corps noir + logo or gravé sur le dessus.

Dimensions WolfMix W1 : 195 x 220 x 62 mm.
Le capot couvre la face supérieure et descend de 15mm sur les côtés
avec 4 clips de retenue et des fentes de ventilation.
"""
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from build123d import *
from models.build_base import BuildParametricModel
from models.brand import LOGO_TEXT_PRIMARY


class WolfmixDecksaver(BuildParametricModel):
    """Capot de protection WolfMix W1 avec logo gravé."""

    def __init__(self, **params):
        super().__init__("wolfmix_decksaver", **params)

    def default_params(self) -> dict:
        return {
            'device_w': 195.0,
            'device_d': 220.0,
            'clearance': 0.5,
            'wall_t': 2.0,
            'top_t': 2.5,
            'skirt_h': 15.0,
            'corner_r': 8.0,
            'logo_depth': 2.5,
            'vent_slots': True,
            'branding': True,
        }

    def build(self) -> Part:
        p = self.params
        iw = p['device_w'] + 2 * p['clearance']
        id_ = p['device_d'] + 2 * p['clearance']
        wt = p['wall_t']
        tt = p['top_t']
        sk = p['skirt_h']

        ew = iw + 2 * wt
        ed = id_ + 2 * wt
        total_h = sk + tt

        with BuildPart() as decksaver:
            # 1. Coque principale — boîte retournée
            Box(ew, ed, total_h)

            # 2. Évidement intérieur (la poche où le WolfMix rentre)
            with BuildPart(mode=Mode.SUBTRACT):
                with Locations((0, 0, -tt / 2)):
                    Box(iw, id_, sk + 1)

            # 3. Clips de retenue (4 ergots qui accrochent le WolfMix)
            clip_w = 10.0
            clip_d = 1.5
            clip_h = 4.0
            clip_positions = [
                (0, ed / 2 - wt / 2, -total_h / 2 + clip_h / 2),      # avant
                (0, -ed / 2 + wt / 2, -total_h / 2 + clip_h / 2),     # arrière
                (ew / 2 - wt / 2, 0, -total_h / 2 + clip_h / 2),      # droite
                (-ew / 2 + wt / 2, 0, -total_h / 2 + clip_h / 2),     # gauche
            ]
            for cx, cy, cz in clip_positions:
                with BuildPart(mode=Mode.ADD):
                    with Locations((cx, cy, cz)):
                        Box(clip_w, clip_d, clip_h)

            # 4. Fentes de ventilation (5 slots sur le dessus)
            if p['vent_slots']:
                slot_w = 50.0
                slot_gap = 1.8
                n_slots = 5
                for i in range(n_slots):
                    y_offset = (i - n_slots / 2 + 0.5) * 8
                    with BuildPart(mode=Mode.SUBTRACT):
                        with Locations((0, y_offset + 30, total_h / 2 - tt / 2)):
                            Box(slot_w, slot_gap, tt + 1)

            # 5. Poignée de retrait (encoche arrondie à l'avant)
            with BuildPart(mode=Mode.SUBTRACT):
                with Locations((0, ed / 2, total_h / 2 - tt / 2)):
                    Cylinder(radius=15, height=tt + 1)

            # 6. Gravure logo PRESTIGE SOUND sur le dessus
            if p['branding']:
                top_face = decksaver.faces().sort_by(Axis.Z)[-1]
                with BuildSketch(Plane(top_face)) as logo_sk:
                    Text(LOGO_TEXT_PRIMARY, font_size=12,
                         font="Arial", font_style=FontStyle.BOLD)
                extrude(logo_sk.sketch, amount=-p['logo_depth'],
                        mode=Mode.SUBTRACT)

                # Ligne décorative sous le texte
                with BuildSketch(Plane(top_face)) as line_sk:
                    with Locations((0, -12)):
                        Rectangle(100, 0.8)
                extrude(line_sk.sketch, amount=-1.0, mode=Mode.SUBTRACT)

            # 7. Chanfreins sur les arêtes du dessus
            try:
                top_edges = decksaver.edges().filter_by(Axis.Z).sort_by(Axis.Z)[-4:]
                chamfer(top_edges, length=1.0)
            except Exception:
                pass

        return decksaver.part


if __name__ == '__main__':
    model = WolfmixDecksaver()
    model.generate()
