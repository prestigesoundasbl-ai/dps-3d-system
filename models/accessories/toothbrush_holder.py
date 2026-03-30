"""
Toothbrush Holder — Porte Brosse a Dent Oral-B Familial
========================================================
Coque ajouree avec maillage croise (barres diagonales continues).
4 tubes pour brosses electriques, prenoms graves, tiroir drainant.

Design inspire d'un vase ceramique a texture treillis :
  - Murs = grille de barres croisees a ±45° (on voit a travers)
  - 4 tubes cylindriques pour les brosses
  - Plateau drainant qui connecte les tubes aux murs
  - Tiroir amovible en dessous

Impression K2 Pro : corps blanc + tiroir noir, sans supports.
"""
import os
import sys
import math

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from build123d import *
from models.build_base import BuildParametricModel


class ToothbrushHolder(BuildParametricModel):
    """Porte brosse a dent Oral-B familial avec maillage croise."""

    def __init__(self, **params):
        super().__init__("toothbrush_holder", **params)

    def default_params(self) -> dict:
        return {
            # Dimensions (basees sur STL reference 170x70x85)
            'width': 170.0,
            'depth': 70.0,
            'height': 85.0,
            # Trous brosses (Oral-B Pro ~31.5mm, +0.7mm tolerance FDM)
            'hole_d': 32.2,
            'hole_count': 4,
            'hole_spacing': 35.0,
            # Structure
            'wall_t': 2.5,
            'base_t': 2.5,
            'corner_r': 8.0,
            'tube_wall': 2.5,       # Paroi des tubes autour des puits
            # Plateau drainant
            'shelf_z': 15.0,
            'shelf_t': 2.5,
            'drain_d': 14.0,
            # Maillage croise
            'mesh_spacing': 9.0,    # Entraxe des barres
            'mesh_bar': 1.8,        # Largeur des barres
            # Tiroir
            'tray_h': 12.0,
            'tray_gap': 0.3,
            'tray_wall': 1.6,
            # Prenoms
            'names': ['Papa', 'Maman', 'Leo', 'Jade'],
            'name_font_size': 7.0,
            'name_depth': 1.2,
        }

    def build(self) -> Part:
        p = self.params
        w, d, h = p['width'], p['depth'], p['height']
        wt, bt = p['wall_t'], p['base_t']
        cr = p['corner_r']
        sz, st = p['shelf_z'], p['shelf_t']
        hd = p['hole_d']
        tw_ = p['tube_wall']
        icr = max(cr - wt, 1.0)
        iw = w - 2 * wt
        id_ = d - 2 * wt
        well_z = sz + st
        well_h = h - well_z + 0.1
        n = p['hole_count']
        sp = p['hole_spacing']
        hole_xs = [-(n - 1) * sp / 2 + i * sp for i in range(n)]

        with BuildPart() as part:

            # --- 1. COQUE EXTERIEURE (z=0 → z=h) ---
            with BuildSketch() as sk:
                RectangleRounded(w, d, cr)
            extrude(sk.sketch, amount=h)

            # --- 2. EVIDEMENT TIROIR (z=bt → z=sz) ---
            with BuildSketch(Plane.XY.offset(bt)) as sk:
                RectangleRounded(iw, id_, icr)
            extrude(sk.sketch, amount=sz - bt, mode=Mode.SUBTRACT)

            # --- 3. PUITS (z=well_z → z=h) ---
            with BuildSketch(Plane.XY.offset(well_z)) as sk:
                for hx in hole_xs:
                    with Locations((hx, 0)):
                        Circle(hd / 2)
            extrude(sk.sketch, amount=well_h, mode=Mode.SUBTRACT)

            # --- 5. DRAINAGE (trous dans le plateau) ---
            with BuildSketch(Plane.XY.offset(sz - 0.05)) as sk:
                for hx in hole_xs:
                    with Locations((hx, 0)):
                        Circle(p['drain_d'] / 2)
            extrude(sk.sketch, amount=st + 0.1, mode=Mode.SUBTRACT)

            # --- 6. CHANFREIN D'INSERTION (cones en haut) ---
            ch = 2.0
            for hx in hole_xs:
                with Locations((hx, 0, h - ch)):
                    Cone(hd / 2, hd / 2 + ch, ch + 0.05,
                         align=(Align.CENTER, Align.CENTER, Align.MIN),
                         mode=Mode.SUBTRACT)

            # --- 7. OUVERTURE TIROIR (face avant) ---
            tray_h = sz - bt
            with Locations((0, -d / 2, bt + tray_h / 2)):
                Box(iw, wt + 1, tray_h, mode=Mode.SUBTRACT)

            # --- 8. MAILLAGE CROISE (gravure 1.5mm sur les 4 murs) ---
            cut = 1.5
            lx = (-w/2 + cr + 1, w/2 - cr - 1)
            sxr = (-d/2 + cr + 1, d/2 - cr - 1)

            sk = self._crosshatch_sketch(Plane.XZ.offset(d / 2), *lx)
            extrude(sk, amount=-cut, mode=Mode.SUBTRACT)
            sk = self._crosshatch_sketch(Plane.XZ.offset(-d / 2), *lx)
            extrude(sk, amount=cut, mode=Mode.SUBTRACT)
            sk = self._crosshatch_sketch(Plane.YZ.offset(w / 2), *sxr)
            extrude(sk, amount=-cut, mode=Mode.SUBTRACT)
            sk = self._crosshatch_sketch(Plane.YZ.offset(-w / 2), *sxr)
            extrude(sk, amount=cut, mode=Mode.SUBTRACT)

            # --- 9. PRENOMS (graves sur la face avant) ---
            names = p.get('names', [])
            if names:
                try:
                    front = Plane.XZ.offset(d / 2)
                    for i, hx in enumerate(hole_xs):
                        if i < len(names) and names[i]:
                            with BuildSketch(front) as sk:
                                with Locations((hx, h * 0.7)):
                                    Text(names[i],
                                         font_size=p['name_font_size'],
                                         font="Arial Rounded MT Bold",
                                         font_style=FontStyle.BOLD)
                            extrude(sk.sketch, amount=-p['name_depth'],
                                    mode=Mode.SUBTRACT)
                except Exception:
                    pass

        return part.part

    def _crosshatch_sketch(self, plane, sx_min, sx_max):
        """Cree le sketch des losanges ouverts (reutilise pour body + inlay)."""
        p = self.params
        S, B = p['mesh_spacing'], p['mesh_bar']
        well_z = p['shelf_z'] + p['shelf_t']
        z_lo = well_z + 1
        z_hi = p['height'] - 1.5
        zone_w = sx_max - sx_min
        zone_h = z_hi - z_lo
        cx = (sx_min + sx_max) / 2
        cz = (z_lo + z_hi) / 2
        diag = math.sqrt(zone_w**2 + zone_h**2) * 1.5
        nb = int(diag / S) + 4

        with BuildSketch(plane) as sk:
            with Locations((cx, cz)):
                Rectangle(zone_w, zone_h)
            for i in range(-nb, nb + 1):
                off = i * S
                bx = cx + off * math.cos(math.radians(45))
                bz = cz + off * math.sin(math.radians(45))
                with Locations((bx, bz)):
                    Rectangle(B, diag, rotation=45, mode=Mode.SUBTRACT)
            for i in range(-nb, nb + 1):
                off = i * S
                bx = cx + off * math.cos(math.radians(45))
                bz = cz - off * math.sin(math.radians(45))
                with Locations((bx, bz)):
                    Rectangle(B, diag, rotation=-45, mode=Mode.SUBTRACT)
        return sk.sketch

    def build_mesh_inlay(self) -> Part:
        """Inlay noir : remplit les losanges graves dans les murs."""
        p = self.params
        w, d, cr = p['width'], p['depth'], p['corner_r']
        cut = 1.5  # Meme profondeur que la gravure

        lx = (-w/2 + cr + 1, w/2 - cr - 1)
        sx = (-d/2 + cr + 1, d/2 - cr - 1)

        with BuildPart() as inlay:
            # Avant
            sk = self._crosshatch_sketch(Plane.XZ.offset(d / 2), *lx)
            extrude(sk, amount=-cut)
            # Arriere
            sk = self._crosshatch_sketch(Plane.XZ.offset(-d / 2), *lx)
            extrude(sk, amount=cut)
            # Droit
            sk = self._crosshatch_sketch(Plane.YZ.offset(w / 2), *sx)
            extrude(sk, amount=-cut)
            # Gauche
            sk = self._crosshatch_sketch(Plane.YZ.offset(-w / 2), *sx)
            extrude(sk, amount=cut)

        return inlay.part

    def build_name_inlay(self) -> Part:
        """Inlay or : remplit les prenoms graves."""
        p = self.params
        d, h = p['depth'], p['height']
        n = p['hole_count']
        sp = p['hole_spacing']
        hole_xs = [-(n - 1) * sp / 2 + i * sp for i in range(n)]
        names = p.get('names', [])

        with BuildPart() as inlay:
            front = Plane.XZ.offset(d / 2)
            for i, hx in enumerate(hole_xs):
                if i < len(names) and names[i]:
                    with BuildSketch(front) as sk:
                        with Locations((hx, h * 0.7)):
                            Text(names[i],
                                 font_size=p['name_font_size'],
                                 font="Arial Rounded MT Bold",
                                 font_style=FontStyle.BOLD)
                    extrude(sk.sketch, amount=-p['name_depth'])

        return inlay.part

    def build_tray(self) -> Part:
        """Tiroir collecteur amovible."""
        p = self.params
        w, d = p['width'], p['depth']
        wt = p['wall_t']
        gap = p['tray_gap']
        cr = p['corner_r']
        th = p['tray_h']
        twt = p['tray_wall']
        tw = w - 2 * wt - 2 * gap
        td = d - 2 * wt - 2 * gap
        tcr = max(cr - wt - gap, 1.0)

        with BuildPart() as tray:
            with BuildSketch() as sk:
                RectangleRounded(tw, td, tcr)
            extrude(sk.sketch, amount=th)
            with BuildSketch(Plane.XY.offset(twt)) as sk:
                RectangleRounded(tw - 2 * twt, td - 2 * twt,
                                 max(tcr - twt, 0.5))
            extrude(sk.sketch, amount=th, mode=Mode.SUBTRACT)
            with Locations((0, -td / 2 - 1.5, th / 2)):
                Box(25, 3, 5)

        return tray.part


if __name__ == '__main__':
    model = ToothbrushHolder()
    os.makedirs("output/stl", exist_ok=True)

    # 1. Corps principal (BLANC - slot 3)
    model.generate()

    # 2. Inlay maillage (NOIR - slot 1)
    print("Building mesh inlay...")
    mesh_inlay = model.build_mesh_inlay()
    export_stl(mesh_inlay, "output/stl/toothbrush_holder_mesh_noir.stl")
    print("  -> toothbrush_holder_mesh_noir.stl")

    # 3. Inlay prenoms (OR - slot 2)
    print("Building name inlay...")
    try:
        name_inlay = model.build_name_inlay()
        export_stl(name_inlay, "output/stl/toothbrush_holder_names_or.stl")
        print("  -> toothbrush_holder_names_or.stl")
    except Exception as e:
        print(f"  Names inlay skipped: {e}")

    # 4. Tiroir (NOIR - slot 1)
    print("Building tray...")
    tray = model.build_tray()
    export_stl(tray, "output/stl/toothbrush_holder_tray.stl")
    print("  -> toothbrush_holder_tray.stl")

    print()
    print("=== WORKFLOW ORCASLICER CFS ===")
    print("1. Charger toothbrush_holder.stl        -> Slot 3 (Blanc)")
    print("2. Add Part: ..._mesh_noir.stl           -> Slot 1 (Noir)")
    print("3. Add Part: ..._names_or.stl            -> Slot 2 (Or)")
    print("4. Imprimer tray separement              -> Slot 1 (Noir)")
    print("================================")
