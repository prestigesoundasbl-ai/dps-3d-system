"""
Clip de Gestion de Cables pour DJ Booth - T-Slot 2040
Petit clip snap-in pour maintenir les cables le long des profiles aluminium.
Tab T-slot s'insere dans la rainure, anneau C maintient le cable.
25 necessaires pour le booth complet. ~10g chacun.
"""
from solid2 import *
from ..base import ParametricModel
from ._constants import (
    SLOT_WIDTH, SLOT_DEPTH,
    FIT_CLEARANCE, SLOT_CLEARANCE
)


class BoothCableClip(ParametricModel):

    def __init__(self, **params):
        super().__init__("booth_cable_clip", **params)

    def default_params(self):
        return {
            'cable_diameter': 8.0,
            'cable_count': 1,
            'clip_wall': 2.5,
            'clip_gap': 3.0,
            'base_width': 15.0,
            'base_depth': 12.0,
            'base_height': 3.0,
            'label_text': '',
            'fit_clearance': FIT_CLEARANCE,
        }

    def param_schema(self):
        return {
            'cable_diameter': {
                'type': 'float', 'min': 3.0, 'max': 20.0, 'unit': 'mm',
                'description': 'Diametre du cable a maintenir'
            },
            'cable_count': {
                'type': 'int', 'min': 1, 'max': 3,
                'description': 'Nombre d\'anneaux cable (1-3)'
            },
            'clip_wall': {
                'type': 'float', 'min': 1.5, 'max': 5.0, 'unit': 'mm',
                'description': 'Epaisseur paroi de l\'anneau C'
            },
            'clip_gap': {
                'type': 'float', 'min': 1.5, 'max': 8.0, 'unit': 'mm',
                'description': 'Ouverture du snap-fit en haut de l\'anneau'
            },
            'base_width': {
                'type': 'float', 'min': 10.0, 'max': 30.0, 'unit': 'mm',
                'description': 'Largeur de la plaque de base'
            },
            'base_depth': {
                'type': 'float', 'min': 8.0, 'max': 25.0, 'unit': 'mm',
                'description': 'Profondeur de la plaque (le long du profil)'
            },
            'base_height': {
                'type': 'float', 'min': 2.0, 'max': 6.0, 'unit': 'mm',
                'description': 'Epaisseur de la plaque de base'
            },
            'label_text': {
                'type': 'str',
                'description': 'Texte optionnel grave sur la plaque (vide = pas de label)'
            },
            'fit_clearance': {
                'type': 'float', 'min': 0.1, 'max': 0.6, 'unit': 'mm',
                'description': 'Jeu d\'ajustement (0.3mm standard FDM)'
            },
        }

    def build(self):
        p = self.params
        cd = p['cable_diameter']
        n_cables = p['cable_count']
        cw = p['clip_wall']
        gap = p['clip_gap']
        bw = p['base_width']
        bd = p['base_depth']
        bh = p['base_height']

        # -- Tab T-slot (s'insere dans la rainure du profil 2040) --
        tab_w = SLOT_WIDTH - 2 * SLOT_CLEARANCE
        tab_d = SLOT_DEPTH - SLOT_CLEARANCE
        # Tab centre sous la base, s'etend vers le bas (-Z)
        tab = translate([-(tab_w / 2), -(bd / 2), -tab_d])(
            cube([tab_w, bd, tab_d])
        )

        # Levre de retenue : petite bosse sur chaque cote du tab
        # pour maintenir le clip dans la rainure par friction
        lip_h = 0.6   # hauteur de la bosse
        lip_d = bd * 0.6  # longueur de la bosse le long du profil
        lip_w = 0.4   # largeur de la bosse (depassement lateral)

        lip_left = translate([-(tab_w / 2) - lip_w, -(lip_d / 2),
                              -tab_d + 1.0])(
            cube([lip_w, lip_d, lip_h])
        )
        lip_right = translate([tab_w / 2, -(lip_d / 2),
                               -tab_d + 1.0])(
            cube([lip_w, lip_d, lip_h])
        )
        tab = tab + lip_left + lip_right

        # -- Plaque de base --
        base = translate([-(bw / 2), -(bd / 2), 0])(
            cube([bw, bd, bh])
        )

        model = tab + base

        # -- Anneaux C pour cables --
        ring_outer_d = cd + 2 * cw
        ring_outer_r = ring_outer_d / 2
        ring_inner_r = cd / 2
        ring_h = bd  # hauteur de l'anneau = profondeur de la base

        # Espacement des anneaux si multiples
        if n_cables == 1:
            x_positions = [0.0]
        elif n_cables == 2:
            spacing = bw / 3
            x_positions = [-spacing / 2, spacing / 2]
        else:  # 3
            spacing = bw / 4
            x_positions = [-spacing, 0.0, spacing]

        for x_pos in x_positions:
            # Cylindre externe
            outer = cylinder(r=ring_outer_r, h=ring_h, _fn=48)
            # Cylindre interne (a soustraire)
            inner = cylinder(r=ring_inner_r, h=ring_h + 0.2, _fn=48)

            # Cube pour couper le gap en haut (direction +X depuis le centre)
            # Le gap est au sommet de l'anneau (en +Z quand couche)
            # L'anneau est oriente verticalement : axe le long de Y
            # On construit couche (axe Z) puis on tourne
            gap_cut = translate([-(gap / 2), -(ring_outer_r + 0.1), -0.1])(
                cube([gap, ring_outer_r + 0.1, ring_h + 0.4])
            )

            # Anneau C = externe - interne - gap
            c_ring = outer - inner - gap_cut

            # Positionner : rotation pour que l'axe du cylindre soit le long de Y
            # puis placer au dessus de la base
            c_ring = rotate([90, 0, 0])(c_ring)
            # Apres rotation: axe Z -> axe -Y, donc il faut recentrer
            c_ring = translate([x_pos, bd / 2, bh + ring_outer_r])(c_ring)

            model = model + c_ring

        # -- Label optionnel --
        if p['label_text']:
            txt = p['label_text']
            label = linear_extrude(height=0.6)(
                text(txt, size=4, halign="center", valign="center", _fn=24)
            )
            # Placer sur le dessus de la base, cote Y positif (face avant)
            label = translate([0, 0, bh])(label)
            model = model + label

        return model


if __name__ == "__main__":
    import sys
    clip = BoothCableClip()
    print(f"Generation clip cable booth...")
    print(f"Parametres: {clip.params}")
    scad_path = clip.save_scad()
    print(f"SCAD: {scad_path}")
    try:
        stl_path = clip.render_stl()
        print(f"STL: {stl_path}")
        print("OK")
    except Exception as e:
        print(f"Erreur STL: {e}", file=sys.stderr)
