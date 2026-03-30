"""
Plug Holder DPS Prestige — Berceau pour transformateurs/blocs d'alim
Maintient les blocs d'alimentation (briques) en place pendant le transport.
Specifications par defaut:
  - Berceau en U souple avec pattes de retention
  - Base plate pour fixation Dual Lock
  - Coins arrondis R=3mm, profil doux
  - Rainure accent or
  - Taille adaptee aux blocs d'alim Mixon/Shure (~55×35×30mm)
"""
from solid2 import *
from ..base import ParametricModel
from ..brand import (
    BRAND_NAME_SHORT, DEFAULT_TEXT_DEPTH, DEFAULT_TEXT_FONT,
    DEFAULT_CORNER_RADIUS, COLOR_GOLD
)
from ..utils import rounded_box


class DPSPlugHolder(ParametricModel):

    def __init__(self, **params):
        super().__init__("dps_plug_holder", **params)

    def default_params(self):
        return {
            'plug_width': 45.0,          # Largeur du bloc alim
            'plug_depth': 30.0,          # Profondeur du bloc alim
            'plug_height': 25.0,         # Hauteur du bloc alim
            'clearance': 1.0,            # Jeu autour du bloc
            'wall_thickness': 2.5,
            'base_thickness': 3.0,
            'corner_radius': 3.0,
            'retention_height': 8.0,     # Hauteur des pattes de retention
            'retention_lip': 3.0,        # Avancee de la patte (retient le bloc)
            'cable_exit_width': 15.0,    # Ouverture pour sortie cable
            'accent_groove_depth': 0.5,
            'accent_groove_width': 0.8,
            'engrave_dps': True,
            'export_part': 'all',
        }

    def param_schema(self):
        return {
            'plug_width': {
                'type': 'float', 'min': 20, 'max': 80, 'unit': 'mm',
                'description': 'Largeur du bloc d\'alimentation'
            },
            'plug_depth': {
                'type': 'float', 'min': 15, 'max': 60, 'unit': 'mm',
                'description': 'Profondeur du bloc d\'alimentation'
            },
            'plug_height': {
                'type': 'float', 'min': 10, 'max': 50, 'unit': 'mm',
                'description': 'Hauteur du bloc d\'alimentation'
            },
            'clearance': {
                'type': 'float', 'min': 0.3, 'max': 3, 'unit': 'mm',
                'description': 'Jeu autour du bloc'
            },
            'wall_thickness': {
                'type': 'float', 'min': 1.5, 'max': 5, 'unit': 'mm',
                'description': 'Epaisseur des parois'
            },
            'base_thickness': {
                'type': 'float', 'min': 2, 'max': 6, 'unit': 'mm',
                'description': 'Epaisseur de la base'
            },
            'corner_radius': {
                'type': 'float', 'min': 0, 'max': 5, 'unit': 'mm',
                'description': 'Rayon des coins'
            },
            'retention_height': {
                'type': 'float', 'min': 3, 'max': 15, 'unit': 'mm',
                'description': 'Hauteur des pattes de retention'
            },
            'retention_lip': {
                'type': 'float', 'min': 1, 'max': 8, 'unit': 'mm',
                'description': 'Avancee de la levre de retention'
            },
            'cable_exit_width': {
                'type': 'float', 'min': 8, 'max': 30, 'unit': 'mm',
                'description': 'Largeur de l\'ouverture sortie cable'
            },
            'accent_groove_depth': {
                'type': 'float', 'min': 0, 'max': 1, 'unit': 'mm',
                'description': 'Profondeur de la rainure accent or'
            },
            'accent_groove_width': {
                'type': 'float', 'min': 0, 'max': 2, 'unit': 'mm',
                'description': 'Largeur de la rainure accent'
            },
            'engrave_dps': {
                'type': 'bool',
                'description': 'Graver DPS sur la face avant'
            },
            'export_part': {
                'type': 'string',
                'description': 'all (defaut)'
            },
        }

    def build(self):
        p = self.params
        pw = p['plug_width']
        pd = p['plug_depth']
        ph = p['plug_height']
        cl = p['clearance']
        wt = p['wall_thickness']
        bt = p['base_thickness']
        cr = p['corner_radius']
        ret_h = p['retention_height']
        ret_lip = p['retention_lip']
        cable_w = p['cable_exit_width']
        groove_d = p['accent_groove_depth']
        groove_w = p['accent_groove_width']

        # Dimensions interieures (bloc + jeu)
        inner_w = pw + 2 * cl
        inner_d = pd + 2 * cl

        # Dimensions exterieures totales
        total_w = inner_w + 2 * wt
        total_d = inner_d + 2 * wt
        # Hauteur des parois: on ne monte pas jusqu'en haut du bloc,
        # les pattes de retention font le maintien
        wall_h = ph * 0.6  # Parois a 60% de la hauteur du bloc
        total_h = bt + wall_h

        # -- Base avec coins arrondis --
        base = rounded_box(total_w, total_d, bt, cr)

        # -- Parois laterales --
        # Paroi gauche
        wall_l = translate([0, 0, bt])(
            cube([wt, total_d, wall_h])
        )
        # Paroi droite
        wall_r = translate([total_w - wt, 0, bt])(
            cube([wt, total_d, wall_h])
        )
        # Paroi arriere
        wall_back = translate([0, total_d - wt, bt])(
            cube([total_w, wt, wall_h])
        )
        # Paroi avant (avec ouverture pour le cable)
        wall_front_l = translate([0, 0, bt])(
            cube([total_w / 2 - cable_w / 2, wt, wall_h])
        )
        wall_front_r = translate([total_w / 2 + cable_w / 2, 0, bt])(
            cube([total_w / 2 - cable_w / 2, wt, wall_h])
        )

        walls = wall_l + wall_r + wall_back + wall_front_l + wall_front_r

        # -- Pattes de retention (4 coins, orientees vers l'interieur) --
        # Chaque patte est un petit L inverse qui retient le bloc par dessus
        patte_w = 10.0  # Largeur de chaque patte
        patte_thick = wt * 0.8

        def make_retention_patte(x, y, rot_z):
            """Cree une patte de retention en L."""
            # Montant vertical
            montant = cube([patte_thick, patte_w, ret_h])
            # Levre horizontale (retient le bloc)
            levre = translate([0, 0, ret_h - patte_thick])(
                cube([ret_lip, patte_w, patte_thick])
            )
            patte = montant + levre
            # Positionner et orienter
            return translate([x, y, total_h])(
                rotate([0, 0, rot_z])(patte)
            )

        # Pattes aux 4 coins interieurs
        # Avant-gauche
        p1 = make_retention_patte(wt, wt, 0)
        # Avant-droite
        p2 = make_retention_patte(total_w - wt, wt, 90)
        # Arriere-gauche
        p3 = make_retention_patte(wt, total_d - wt - patte_w, 0)
        # Arriere-droite
        p4 = make_retention_patte(total_w - wt, total_d - wt - patte_w, 90)

        pattes = p1 + p2 + p3 + p4

        model = base + walls + pattes

        # -- Conges interieurs fond-paroi --
        fillet_r = 1.5
        # Conge fond-paroi gauche
        fillet_profile = difference()(
            cube([fillet_r, total_d - 2 * cr, fillet_r]),
            translate([fillet_r, -0.1, fillet_r])(
                rotate([-90, 0, 0])(
                    cylinder(r=fillet_r, h=total_d - 2 * cr + 0.2, _fn=32)
                )
            )
        )
        f_left = translate([wt, cr, bt])(fillet_profile)
        f_right = translate([total_w - wt - fillet_r, cr, bt])(fillet_profile)
        # On les ajoute (ce sont des renforts, pas des soustractions)
        model = model + f_left + f_right

        # -- Rainures accent or sur le bord superieur des parois --
        if groove_d > 0 and groove_w > 0:
            # Rainure gauche (dessus de la paroi)
            g_l = translate([-0.1, cr, total_h - groove_d])(
                cube([groove_w + 0.1, total_d - 2 * cr, groove_d + 0.1])
            )
            # Rainure droite
            g_r = translate([total_w - groove_w, cr, total_h - groove_d])(
                cube([groove_w + 0.1, total_d - 2 * cr, groove_d + 0.1])
            )
            model = model - g_l - g_r

        # -- Gravure DPS sur la face avant --
        if p['engrave_dps']:
            dps_text = linear_extrude(height=0.6 + 0.1)(
                text("DPS", size=5, font=DEFAULT_TEXT_FONT,
                     halign="center", valign="center", _fn=32)
            )
            dps_text = translate([total_w / 2, -0.1, total_h / 2])(
                rotate([90, 0, 0])(
                    mirror([0, 0, 1])(dps_text)
                )
            )
            model = model - dps_text

        return model


if __name__ == "__main__":
    import sys

    holder = DPSPlugHolder()
    print("Generation Plug Holder DPS...")
    print(f"Parametres: {holder.params}")

    scad_path = holder.save_scad()
    print(f"SCAD: {scad_path}")

    try:
        stl_path = holder.render_stl()
        print(f"STL: {stl_path}")
        print("OK - Plug Holder genere!")
    except Exception as e:
        print(f"Erreur STL: {e}", file=sys.stderr)
