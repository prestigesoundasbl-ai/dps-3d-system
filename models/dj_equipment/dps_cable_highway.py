"""
Cable Highway DPS Prestige — Goulotte ouverte section U
Canal qui longe la paroi arriere du flycase pour regrouper les cables d'alim.
Sections de 200mm qui se clipsent bout a bout.
Specifications par defaut:
  - Section U: 30mm large × 12mm haut (interieur)
  - Longueur: 200mm par section
  - Connecteurs male/femelle bout a bout
  - Rainures accent or sur les bords superieurs
  - Gravure DPS discrette sur la section centrale
  - Base plate pour fixation Dual Lock
"""
from solid2 import *
from ..base import ParametricModel
from ..brand import (
    BRAND_NAME_SHORT, DEFAULT_TEXT_DEPTH, DEFAULT_TEXT_FONT,
    DEFAULT_CORNER_RADIUS, COLOR_GOLD
)
from ..utils import rounded_box, brand_text


class DPSCableHighway(ParametricModel):

    def __init__(self, **params):
        super().__init__("dps_cable_highway", **params)

    def default_params(self):
        return {
            'channel_width': 30.0,        # Largeur interieure (3 cables alim)
            'channel_height': 12.0,       # Hauteur interieure
            'length': 200.0,              # Longueur par section
            'wall_thickness': 2.0,
            'base_thickness': 2.5,
            'corner_radius': 3.0,
            'connector_length': 8.0,      # Longueur du connecteur M/F
            'connector_clearance': 0.3,   # Jeu pour l'emboitement
            'accent_groove_depth': 0.5,   # Rainure or sur bords superieurs
            'accent_groove_width': 0.8,
            'engrave_dps': True,          # Gravure DPS sur la section
            'engrave_text_size': 6.0,
            'cable_entry_slots': 2,       # Encoches laterales pour entree cables
            'cable_entry_width': 10.0,    # Largeur des encoches
            'export_part': 'all',         # 'all', 'section', 'end_cap'
        }

    def param_schema(self):
        return {
            'channel_width': {
                'type': 'float', 'min': 15, 'max': 60, 'unit': 'mm',
                'description': 'Largeur interieure du canal'
            },
            'channel_height': {
                'type': 'float', 'min': 8, 'max': 30, 'unit': 'mm',
                'description': 'Hauteur interieure du canal'
            },
            'length': {
                'type': 'float', 'min': 50, 'max': 400, 'unit': 'mm',
                'description': 'Longueur de la section'
            },
            'wall_thickness': {
                'type': 'float', 'min': 1.2, 'max': 4, 'unit': 'mm',
                'description': 'Epaisseur des parois laterales'
            },
            'base_thickness': {
                'type': 'float', 'min': 1.5, 'max': 5, 'unit': 'mm',
                'description': 'Epaisseur du fond'
            },
            'corner_radius': {
                'type': 'float', 'min': 0, 'max': 5, 'unit': 'mm',
                'description': 'Rayon des coins arrondis'
            },
            'connector_length': {
                'type': 'float', 'min': 4, 'max': 15, 'unit': 'mm',
                'description': 'Longueur du connecteur bout a bout'
            },
            'connector_clearance': {
                'type': 'float', 'min': 0.1, 'max': 0.5, 'unit': 'mm',
                'description': 'Jeu d\'emboitement entre sections'
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
                'description': 'Graver DPS sur la face exterieure'
            },
            'engrave_text_size': {
                'type': 'float', 'min': 3, 'max': 12, 'unit': 'mm',
                'description': 'Taille de la gravure DPS'
            },
            'cable_entry_slots': {
                'type': 'int', 'min': 0, 'max': 4,
                'description': 'Nombre d\'encoches laterales pour entree cables'
            },
            'cable_entry_width': {
                'type': 'float', 'min': 5, 'max': 20, 'unit': 'mm',
                'description': 'Largeur des encoches d\'entree cable'
            },
            'export_part': {
                'type': 'string',
                'description': 'Piece: all, section, end_cap'
            },
        }

    def _build_section(self):
        """Construit une section de highway."""
        p = self.params
        cw = p['channel_width']
        ch = p['channel_height']
        length = p['length']
        wt = p['wall_thickness']
        bt = p['base_thickness']
        cr = p['corner_radius']
        cl = p['connector_length']
        cc = p['connector_clearance']
        groove_d = p['accent_groove_depth']
        groove_w = p['accent_groove_width']

        total_w = cw + 2 * wt
        total_h = ch + bt

        # -- Section U principale --
        # Exterieur avec coins arrondis en haut
        outer = cube([total_w, length, total_h])

        # Interieur (le canal)
        inner = translate([wt, -0.1, bt])(
            cube([cw, length + 0.2, ch + 0.1])
        )

        section = outer - inner

        # -- Arrondir les aretes superieures des parois --
        # On ajoute un petit conge sur le bord superieur interieur
        fillet_r = 1.0
        # Conge gauche (interieur haut)
        fillet_profile = difference()(
            cube([fillet_r, length, fillet_r]),
            translate([fillet_r, -0.1, fillet_r])(
                rotate([-90, 0, 0])(
                    cylinder(r=fillet_r, h=length + 0.2, _fn=32)
                )
            )
        )
        fillet_left = translate([wt - fillet_r, 0, total_h - fillet_r])(
            fillet_profile
        )
        fillet_right = translate([total_w - wt, 0, total_h - fillet_r])(
            mirror([1, 0, 0])(
                translate([-fillet_r, 0, 0])(fillet_profile)
            )
        )
        section = section - fillet_left - fillet_right

        # -- Connecteur male (cote +Y) --
        # Tenon qui depasse a l'extremite +Y
        tenon_w = cw - 2 * cc
        tenon_h = ch - 2 * cc
        tenon = translate([wt + cc, length, bt + cc])(
            cube([tenon_w, cl, tenon_h])
        )
        section = section + tenon

        # -- Connecteur femelle (cote -Y) --
        # Mortaise (creux) a l'extremite -Y
        mortaise_w = cw
        mortaise_h = ch
        mortaise = translate([wt, -cl, bt])(
            cube([mortaise_w, cl + 0.1, mortaise_h])
        )
        section = section - mortaise

        # -- Encoches laterales pour entree des cables --
        n_slots = p['cable_entry_slots']
        slot_w = p['cable_entry_width']
        if n_slots > 0:
            slot_spacing = length / (n_slots + 1)
            for i in range(n_slots):
                y_pos = slot_spacing * (i + 1) - slot_w / 2
                # Encoche sur la paroi gauche (cote appareils)
                slot = translate([-0.1, y_pos, bt])(
                    cube([wt + 0.2, slot_w, ch + 0.1])
                )
                section = section - slot

        # -- Rainures accent or sur les bords superieurs --
        if groove_d > 0 and groove_w > 0:
            # Rainure sur le dessus de la paroi gauche
            groove_l = translate([-0.1, cr, total_h - groove_d])(
                cube([groove_w + 0.1, length - 2 * cr, groove_d + 0.1])
            )
            # Rainure sur le dessus de la paroi droite
            groove_r = translate([total_w - groove_w, cr, total_h - groove_d])(
                cube([groove_w + 0.1, length - 2 * cr, groove_d + 0.1])
            )
            section = section - groove_l - groove_r

        # -- Gravure DPS sur la face exterieure droite --
        if p['engrave_dps']:
            txt_size = p['engrave_text_size']
            dps_text = linear_extrude(height=0.8 + 0.1)(
                text("DPS", size=txt_size, font=DEFAULT_TEXT_FONT,
                     halign="center", valign="center", _fn=32)
            )
            # Rotation pour placer sur la face exterieure droite
            dps_text = translate([total_w - 0.8, length / 2, total_h / 2])(
                rotate([0, -90, 0])(
                    rotate([0, 0, 90])(dps_text)
                )
            )
            section = section - dps_text

        return section

    def _build_end_cap(self):
        """Construit un bouchon d'extremite."""
        p = self.params
        cw = p['channel_width']
        ch = p['channel_height']
        wt = p['wall_thickness']
        bt = p['base_thickness']
        cc = p['connector_clearance']
        cl = p['connector_length']
        cr = p['corner_radius']

        total_w = cw + 2 * wt
        total_h = ch + bt

        # Paroi de fermeture
        cap = cube([total_w, wt, total_h])

        # Tenon pour s'emboiter dans la mortaise de la section
        tenon_w = cw - 2 * cc
        tenon_h = ch - 2 * cc
        tenon = translate([wt + cc, wt, bt + cc])(
            cube([tenon_w, cl, tenon_h])
        )

        # Petit arrondi sur le bord superieur
        cap_round = translate([cr, 0, total_h])(
            rotate([-90, 0, 0])(
                cylinder(r=cr, h=wt, _fn=32)
            )
        )

        return cap + tenon

    def build(self):
        p = self.params
        export = p['export_part']

        if export == 'end_cap':
            return self._build_end_cap()
        elif export == 'section':
            return self._build_section()
        else:
            # Montrer une section + end cap decale pour visualisation
            section = self._build_section()
            end_cap = translate([0, -self.params['wall_thickness'] - 2, 0])(
                self._build_end_cap()
            )
            return section + end_cap


if __name__ == "__main__":
    import sys

    # Section standard
    highway = DPSCableHighway(export_part='section')
    print("Generation Highway section 200mm...")
    scad_path = highway.save_scad()
    print(f"  SCAD: {scad_path}")

    # End cap
    cap = DPSCableHighway(export_part='end_cap')
    cap.name = "dps_cable_highway_end_cap"
    scad_path = cap.save_scad()
    print(f"  End cap SCAD: {scad_path}")

    try:
        stl_path = highway.render_stl()
        print(f"  STL: {stl_path}")
        print("OK!")
    except Exception as e:
        print(f"  Erreur STL: {e}", file=sys.stderr)
