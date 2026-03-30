"""
Wingman Phone Clip - Version Robuste
Modèle : wingman_phone_clip.py (Version 1.3)
Fix : Branding par soustraction de Box pour éviter les crashs de triangulation.
"""
import os
import sys
import math

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from build123d import *
from models.build_base import BuildParametricModel

class WingmanPhoneClip(BuildParametricModel):
    def __init__(self, **params):
        super().__init__("wingman_phone_clip", **params)

    def default_params(self) -> dict:
        return {
            'wall_t': 7.0,
            'phone_t': 13.0,
            'phone_w': 85.0,
            'angle': 20.0,
            'clip_depth': 35.0,
        }

    def build(self) -> Part:
        p = self.params
        wt, pt, pw, angle, cd = p['wall_t']+0.4, p['phone_t']+0.4, p['phone_w'], p['angle'], p['clip_depth']
        st = 4.0

        with BuildPart() as wingman:
            # 1. Structure par primitives (Box) pour stabilité maximale
            # Clip
            Box(pw, st, cd, align=(Align.CENTER, Align.MIN, Align.MAX))
            with Locations((0, wt + st, 0)):
                Box(pw, st, cd, align=(Align.CENTER, Align.MIN, Align.MAX))
            with Locations((0, 0, 0)):
                Box(pw, wt + 2*st, st, align=(Align.CENTER, Align.MIN, Align.MIN))
            
            # Support incliné
            with Locations((0, wt + 2*st, 0)):
                with Locations(Rotation(-angle, 0, 0)):
                    Box(pw, st, 100, align=(Align.CENTER, Align.MIN, Align.MIN))
                    # Lèvre de rétention
                    with Locations((0, pt, 0)):
                        Box(pw, st, 15, align=(Align.CENTER, Align.MIN, Align.MIN))
                    # Fond support
                    Box(pw, pt + st, st, align=(Align.CENTER, Align.MIN, Align.MIN))

            # 2. Passage de câble
            with BuildPart(mode=Mode.SUBTRACT):
                Box(25, 200, 200)

        return wingman.part

if __name__ == "__main__":
    model = WingmanPhoneClip()
    model.generate()
