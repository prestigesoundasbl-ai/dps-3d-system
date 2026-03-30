"""
Equerre d'Angle Accordion DJ Booth
====================================
Connecteur L pour jonction montant vertical / traverse horizontale.
2 bras en U-channel a 90 degres avec gusset diagonal de renfort.

Imprimable CityFab1 : ~93x93x33mm
8 necessaires par section (4 coins x haut/bas).
24 au total pour le booth complet.
"""
from solid2 import *
from ..base import ParametricModel
from ._constants import (
    M5_HOLE, M5_HEAD, M5_HEAD_DEPTH,
    FIT_CLEARANCE,
    ACCORDION_TUBE, ACCORDION_INSERT_CLEARANCE,
)


class AccordionCorner(ParametricModel):

    def __init__(self, **params):
        super().__init__("accordion_corner", **params)

    def default_params(self):
        return {
            'tube_size': ACCORDION_TUBE,
            'plate_thickness': 4.0,
            'arm_length': 60.0,
            'gusset': True,
            'fit_clearance': FIT_CLEARANCE,
        }

    def param_schema(self):
        return {
            'tube_size': {
                'type': 'float', 'min': 20, 'max': 30, 'unit': 'mm',
                'description': 'Section tube alu carre',
            },
            'plate_thickness': {
                'type': 'float', 'min': 3, 'max': 6, 'unit': 'mm',
                'description': 'Epaisseur des plaques',
            },
            'arm_length': {
                'type': 'float', 'min': 40, 'max': 100, 'unit': 'mm',
                'description': 'Longueur de chaque bras',
            },
            'gusset': {
                'type': 'bool',
                'description': 'Ajouter un renfort diagonal',
            },
            'fit_clearance': {
                'type': 'float', 'min': 0.1, 'max': 0.6, 'unit': 'mm',
                'description': 'Jeu d\'ajustement',
            },
        }

    def _u_arm(self, tube, pt, clr, length):
        """Bras en U-channel le long de l'axe X.
        Optimise : chanfreins + cutouts.
        """
        inner = tube + 2 * clr
        outer_h = inner + pt  # fond + hauteur interne
        outer_w = inner + 2 * pt  # parois laterales

        arm = cube([length, outer_w, outer_h])
        
        # Chanfreins (Biseaux a 45 degres)
        chamfer_size = 2.0
        # Outil de coupe pour chanfrein (le long de X)
        cutter = rotate([45, 0, 0])(cube([length + 2, chamfer_size * 3, chamfer_size * 3], center=True))
        
        # Chanfreins longitudinaux (aretes superieures)
        arm -= translate([length/2, 0, outer_h])(cutter)
        arm -= translate([length/2, outer_w, outer_h])(cutter)
        
        # Evidement interieur
        cavity = translate([-0.1, pt, pt])(
            cube([length + 0.2, inner, inner + 0.1])
        )
        arm -= cavity

        # OPTIMISATION : Decoupes laterales (flancs)
        cutout_l = length - pt - 15  # Garder matiere au bout et au coin
        cutout_h = outer_h - pt - 8
        if cutout_l > 5 and cutout_h > 5:
            # Flanc Avant
            arm -= translate([pt + 10, -1, pt + 4])(cube([cutout_l, pt + 2, cutout_h]))
            # Flanc Arriere
            arm -= translate([pt + 10, outer_w - pt - 1, pt + 4])(cube([cutout_l, pt + 2, cutout_h]))

        # 2 trous M5
        spacing = length / 3
        for i in range(2):
            x = spacing * (i + 1)
            hole = translate([x, outer_w / 2, -0.1])(
                cylinder(d=M5_HOLE, h=pt + 0.2, _fn=24)
            )
            # Tete noyee
            cs = translate([x, outer_w / 2, -0.1])(
                cylinder(d=M5_HEAD, h=M5_HEAD_DEPTH, _fn=24)
            )
            arm -= hole
            arm -= cs

        return arm

    def build(self):
        p = self.params
        tube = p['tube_size']
        pt = p['plate_thickness']
        arm_len = p['arm_length']
        clr = p['fit_clearance']

        inner = tube + 2 * clr
        outer_w = inner + 2 * pt
        outer_h = inner + pt

        model = union()

        # Bras horizontal (axe X, vers la droite)
        arm_h = self._u_arm(tube, pt, clr, arm_len)
        model += arm_h

        # Bras vertical (axe Z, vers le haut)
        arm_v = self._u_arm(tube, pt, clr, arm_len)
        # Rotation de 90 degres pour le rendre vertical
        arm_v = rotate([0, -90, 0])(arm_v)
        # Positionner au coin (le _u_arm cree un bloc de 0 a length en X, donc apres rot -90 Y, il va de 0 a -length en Z. Il faut le remonter et le decaler)
        # Correction : arm_v cree le long de X. Rotate -90 Y -> pointe vers +Z.
        # Dimensions apres rot : X=outer_h, Y=outer_w, Z=length
        
        # On doit recréer arm_v correctement orienté ou le translater
        # Le bras horizontal fait [length, outer_w, outer_h]
        # Le bras vertical doit partir de Z=outer_h vers le haut
        
        # Recalcul manuel plus simple pour arm_v pour eviter les soucis de rotation
        arm_v_geom = self._u_arm(tube, pt, clr, arm_len) # Long X
        # On veut qu'il soit long Z.
        # X devient Z, Y reste Y, Z devient X.
        # Mais attention aux dimensions. Le U doit s'ouvrir vers l'interieur du cadre.
        
        # Approche par rotation :
        # arm_h s'ouvre vers +Z (cavite a Z=pt).
        # arm_v doit s'ouvrir vers +X (cavite a X=pt).
        
        # Rotation : 
        # arm_v initial : L x W x H. Cavite vers +Z.
        # Rotate [0, -90, 0] : H x W x L. Cavite vers +X. C'est bon.
        arm_v_placed = translate([0, 0, outer_h])(rotate([0, -90, 0])(arm_v_geom))
        # Ajustement position X : Apres rotation -90 Y, l'axe X initial pointe vers +Z. L'axe Z initial pointe vers -X.
        # Il faut translater en X de 'outer_h' pour ramener la face du fond a X=0
        arm_v_placed = translate([outer_h, 0, 0])(arm_v_placed)
        
        model += arm_v_placed

        # Gusset diagonal (renfort triangulaire) - Version "Tech" EVIDEE
        if p['gusset']:
            gusset_size = arm_len * 0.5
            gusset_t = pt
            
            # Points du triangle
            p1 = [outer_h, 0, outer_h] # Coin interieur bas
            p2 = [outer_h + gusset_size, 0, outer_h] # Pointe horizontale
            p3 = [outer_h, 0, outer_h + gusset_size] # Pointe verticale
            
            # Extrusion du triangle plein
            # On le fait plus fin (gusset_t) et centre ou sur les bords ?
            # Sur les bords (flancs) pour la rigidite max
            
            # Flanc 1
            g1 = translate([0, 0, 0])(
                polyhedron(
                    points=[
                        [outer_h, 0, outer_h], # 0
                        [outer_h + gusset_size, 0, outer_h], # 1
                        [outer_h, 0, outer_h + gusset_size], # 2
                        [outer_h, pt, outer_h], # 3
                        [outer_h + gusset_size, pt, outer_h], # 4
                        [outer_h, pt, outer_h + gusset_size]  # 5
                    ],
                    faces=[[0,1,2], [3,5,4], [0,3,4,1], [1,4,5,2], [2,5,3,0]]
                )
            )
            # Flanc 2
            g2 = translate([0, outer_w - pt, 0])(
                 polyhedron(
                    points=[
                        [outer_h, 0, outer_h], 
                        [outer_h + gusset_size, 0, outer_h], 
                        [outer_h, 0, outer_h + gusset_size],
                        [outer_h, pt, outer_h], 
                        [outer_h + gusset_size, pt, outer_h], 
                        [outer_h, pt, outer_h + gusset_size]
                    ],
                    faces=[[0,1,2], [3,5,4], [0,3,4,1], [1,4,5,2], [2,5,3,0]]
                )
            )
            
            model += g1 + g2

        return model
