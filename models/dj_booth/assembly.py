"""
DJ Booth Pliable - Assemblage Complet (style Roadworx)
Cadre perimetrique en U a 4 montants verticaux relies par charnieres.
Se plie en accordeon (zigzag) a plat pour transport dans une housse.

Architecture (vue du dessus, deploye):

   [Post3]----cote G----[Post4]
      |                    |
    front G              front D
      |                    |
   [Post2]----cote D----[Post1]
            (public)

   Arriere OUVERT (le DJ est ici)

Pliage: les 4 panneaux se replient en zigzag
  - Charnieres entre Post1-Post2, Post2-Post3, Post3-Post4
  - open_pct=100 : deploye en U
  - open_pct=0   : plie a plat (tout empile)

Le plateau se pose par-dessus avec goupilles + equerres laterales.
La facade (panneaux + LED) se fixe sur les traverses avant.
"""
import math
from solid2 import *
from ..base import ParametricModel
from ._constants import *


# Epaisseur du tube carre alu (simplification visuelle)
TUBE_SIZE = 25.0      # tube carre 25x25mm
TUBE_WALL = 2.0       # epaisseur paroi tube


class BoothAssembly(ParametricModel):

    def __init__(self, **params):
        super().__init__("booth_assembly", **params)

    def default_params(self):
        return {
            'width': 1200.0,
            'height': 1100.0,
            'depth': 600.0,
            'open_pct': 100.0,
            'show_facade': True,
            'show_leds': True,
            'show_top': True,
            'show_shelf': True,
            'export_part': 'all',
        }

    def param_schema(self):
        return {
            'width': {'type': 'float', 'min': 1000, 'max': 2000, 'unit': 'mm',
                      'description': 'Largeur totale (facade)'},
            'height': {'type': 'float', 'min': 900, 'max': 1300, 'unit': 'mm',
                       'description': 'Hauteur du cadre'},
            'depth': {'type': 'float', 'min': 400, 'max': 800, 'unit': 'mm',
                      'description': 'Profondeur (cotes) deployee'},
            'open_pct': {'type': 'float', 'min': 0, 'max': 100, 'unit': '%',
                         'description': 'Ouverture (0=plie, 100=deploye)'},
            'show_facade': {'type': 'bool', 'description': 'Afficher panneaux facade'},
            'show_leds': {'type': 'bool', 'description': 'Afficher LED strips'},
            'show_top': {'type': 'bool', 'description': 'Afficher plateau'},
            'show_shelf': {'type': 'bool', 'description': 'Afficher etagere'},
            'export_part': {'type': 'select',
                            'options': ['all', 'frame', 'top', 'shelf', 'facade'],
                            'description': 'Partie a exporter'},
        }

    # ------------------------------------------------------------------
    # Helpers geometriques
    # ------------------------------------------------------------------

    def _tube(self, length):
        """Tube carre alu (simplifie - plein pour le rendu)."""
        return cube([TUBE_SIZE, TUBE_SIZE, length])

    def _tube_h(self, length):
        """Tube horizontal (le long de X)."""
        return cube([length, TUBE_SIZE, TUBE_SIZE])

    def _cross_brace(self, width, height):
        """Renfort diagonal entre 2 traverses (dans le plan XZ vertical)."""
        bar_t = 3
        bar_w = 15
        # Barre diagonale dans le plan XZ
        diag = math.sqrt(width**2 + height**2)
        angle = math.degrees(math.atan2(height, width))
        brace = cube([diag, bar_w, bar_t])
        # Rotation autour de Y pour monter en diagonal (plan XZ)
        brace = translate([0, 0, 0])(
            rotate([0, -angle, 0])(brace)
        )
        return brace

    def _hinge_barrel(self, z_pos):
        """Charniere simplifiee entre 2 panneaux (visible au coin)."""
        barrel_h = 60
        barrel_r = 8
        pin_r = 3
        barrel = cylinder(r=barrel_r, h=barrel_h, _fn=24)
        barrel -= cylinder(r=pin_r, h=barrel_h + 2, _fn=16)
        return translate([0, 0, z_pos])(barrel)

    def _foot(self):
        """Pied reglable avec rotule."""
        base = cylinder(r=20, h=5, _fn=32)
        stem = translate([0, 0, 5])(cylinder(r=8, h=15, _fn=16))
        pad = translate([0, 0, -3])(cylinder(r=15, h=3, _fn=32))
        return base + stem + pad

    # ------------------------------------------------------------------
    # Construction d'un panneau (section du cadre entre 2 montants)
    # ------------------------------------------------------------------

    def _build_panel(self, panel_width, h, is_front=False):
        """
        Un panneau = 2 montants verticaux + 2-3 traverses horizontales
        + renforts diagonaux.

        panel_width: distance exterieure entre les 2 montants
        h: hauteur totale
        is_front: True = panneau avant (recoit facade + LED)
        """
        p = union()

        # 2 montants verticaux
        post = self._tube(h)
        p += post
        p += translate([panel_width - TUBE_SIZE, 0, 0])(post)

        # Traverse basse (a ~100mm du sol pour stabilite)
        rail_len = panel_width - 2 * TUBE_SIZE
        beam = self._tube_h(rail_len)
        p += translate([TUBE_SIZE, 0, 80])(beam)

        # Traverse haute (en haut du cadre)
        p += translate([TUBE_SIZE, 0, h - TUBE_SIZE])(beam)

        # Traverse milieu (pour la facade avant, ou pour l'etagere sur les cotes)
        mid_z = h * 0.45
        p += translate([TUBE_SIZE, 0, mid_z])(beam)

        # Renforts diagonaux (entre traverse basse et milieu, plan XZ)
        brace_w = rail_len * 0.3
        brace_h = mid_z - 80 - TUBE_SIZE
        if brace_h > 100 and brace_w > 50:
            # Renfort gauche : monte de bas-gauche vers haut-droite
            brace = self._cross_brace(brace_w, brace_h)
            p += translate([TUBE_SIZE + 10, TUBE_SIZE / 2 - 7, 80 + TUBE_SIZE])(brace)
            # Renfort droit : miroir en X (monte de bas-droite vers haut-gauche)
            p += translate([panel_width - TUBE_SIZE - 10, TUBE_SIZE / 2 - 7, 80 + TUBE_SIZE])(
                mirror([1, 0, 0])(self._cross_brace(brace_w, brace_h))
            )

        # Pieds (2 par panneau)
        p += translate([TUBE_SIZE / 2, TUBE_SIZE / 2, 0])(self._foot())
        p += translate([panel_width - TUBE_SIZE / 2, TUBE_SIZE / 2, 0])(self._foot())

        return p

    # ------------------------------------------------------------------
    # Cadre complet avec pliage
    # ------------------------------------------------------------------

    def _build_frame(self, w, h, d, open_pct):
        """
        Construit le cadre en U avec 3 panneaux (front gauche, front droit, + 2 cotes)
        relies par 3 charnieres.

        Le Roadworx a 4 montants formant un U:
          - Panneau facade = toute la largeur (front)
          - Panneau cote gauche (depth)
          - Panneau cote droit (depth)

        Pour le pliage, la facade est en 2 moities (gauche+droite)
        avec charniere centrale, et les cotes pivotent aux extremites.

        Pliage en zigzag: cote_G <- front_G -> <- front_D -> cote_D
        """
        frame = union()
        hinges = union()

        # Demi-largeur facade
        half_w = w / 2

        # Angle de pliage
        # A 100%: U deploye (cotes a 90 deg de la facade)
        # A 0%: tout plat (0 deg)
        max_side_angle = 90.0  # angle des cotes par rapport a la facade
        max_front_angle = 0.0   # les 2 moities de facade sont alignees a 100%

        # A 0% plie: les cotes se replient sur la facade,
        # et les 2 moities de facade se replient l'une sur l'autre
        side_angle = max_side_angle * (open_pct / 100.0)
        # Angle d'ouverture entre les 2 moities de facade
        # A 100% = 180 deg (plat/aligne), a 0% = 0 deg (replie)
        front_angle = 180.0 * (open_pct / 100.0)

        # === PANNEAU FACADE DROIT (reference, ne bouge pas) ===
        front_r = self._build_panel(half_w, h, is_front=True)
        frame += front_r

        # === PANNEAU FACADE GAUCHE (pivote autour de la charniere centrale) ===
        front_l = self._build_panel(half_w, h, is_front=True)
        # Miroir pour que le panneau gauche parte vers la gauche
        front_l = mirror([1, 0, 0])(front_l)

        if open_pct >= 99:
            # Deploye: simplement translate a gauche
            front_l = translate([-half_w, 0, 0])(mirror([1, 0, 0])(
                self._build_panel(half_w, h, is_front=True)
            ))
        else:
            # Rotation autour de l'axe vertical a X=0 (charniere centrale)
            # front_angle: 180=plat, 0=replie
            front_l_raw = self._build_panel(half_w, h, is_front=True)
            # Placer le panneau pour qu'il parte de X=0 vers X=+half_w
            # puis rotation autour de Z (axe vertical) a X=0
            front_l = rotate([0, 0, front_angle])(
                front_l_raw
            )

        frame += front_l

        # Charniere centrale facade (axe vertical a X=0, Y=TUBE/2)
        for hz in [120, h / 2, h - 80]:
            hinges += translate([0, TUBE_SIZE / 2, 0])(
                self._hinge_barrel(hz)
            )

        # === PANNEAU COTE DROIT (pivote autour de la charniere droite) ===
        side_r = self._build_panel(d, h)
        # Le cote droit part de X=half_w, pivote autour de l'axe vertical
        # a X=half_w, Y=0 vers Y positif (vers l'arriere)
        if open_pct >= 99:
            # Deploye a 90 deg : le cote part vers Y positif
            side_r = translate([half_w - TUBE_SIZE, 0, 0])(
                rotate([0, 0, -90])(
                    translate([-TUBE_SIZE, 0, 0])(side_r)
                )
            )
        else:
            pivot_x = half_w - TUBE_SIZE
            side_r_placed = translate([-TUBE_SIZE, 0, 0])(side_r)
            side_r = translate([pivot_x, 0, 0])(
                rotate([0, 0, -side_angle])(
                    side_r_placed
                )
            )

        frame += side_r

        # Charniere cote droit (axe vertical a X=half_w, Y=TUBE/2)
        for hz in [120, h / 2, h - 80]:
            hinges += translate([half_w - TUBE_SIZE / 2, TUBE_SIZE / 2, 0])(
                self._hinge_barrel(hz)
            )

        # === PANNEAU COTE GAUCHE (pivote autour de la charniere gauche) ===
        side_l = self._build_panel(d, h)

        if open_pct >= 99:
            # Deploye: cote gauche part vers Y positif depuis X=-half_w
            side_l = translate([-half_w, 0, 0])(
                rotate([0, 0, -90])(
                    translate([-TUBE_SIZE, 0, 0])(side_l)
                )
            )
        elif open_pct < 1:
            # Completement plie: tout empile
            front_l_angle = front_angle  # ~0 deg
            # Le cote gauche doit suivre la position du panneau facade gauche
            # puis pivoter depuis son extremite
            pivot_x = 0  # charniere a X=0 apres pliage facade
            side_l = translate([pivot_x + TUBE_SIZE, 0, 0])(side_l)
        else:
            # Position intermediaire
            # D'abord calculer ou se trouve la charniere gauche
            # Elle est a l'extremite du panneau facade gauche
            hinge_l_x = -half_w * math.cos(math.radians(180 - front_angle))
            hinge_l_y = half_w * math.sin(math.radians(180 - front_angle))

            # Le panneau cote gauche pivote autour de cette charniere
            side_l_placed = translate([-TUBE_SIZE, 0, 0])(side_l)
            # Angle total = angle facade + angle cote
            total_rot = front_angle + side_angle
            side_l = translate([hinge_l_x, hinge_l_y, 0])(
                rotate([0, 0, -(180 - front_angle) - side_angle])(
                    side_l_placed
                )
            )

        frame += side_l

        # Charniere cote gauche
        if open_pct >= 99:
            for hz in [120, h / 2, h - 80]:
                hinges += translate([-half_w + TUBE_SIZE / 2, TUBE_SIZE / 2, 0])(
                    self._hinge_barrel(hz)
                )
        else:
            hinge_l_x = -half_w * math.cos(math.radians(180 - front_angle))
            hinge_l_y = half_w * math.sin(math.radians(180 - front_angle))
            for hz in [120, h / 2, h - 80]:
                hinges += translate([hinge_l_x, hinge_l_y, 0])(
                    self._hinge_barrel(hz)
                )

        return frame + hinges

    # ------------------------------------------------------------------
    # Facade (panneaux decoratifs sur la face avant)
    # ------------------------------------------------------------------

    def _build_facade(self, w, h):
        """Panneaux facade avec perforations + zone logo + LED."""
        facade = union()

        facade_h = h - 250  # hauteur facade visible
        facade_z = 150      # debut facade (au-dessus des pieds)
        half_w = w / 2

        # Panneau facade = plaque fine devant les traverses
        panel_t = TILE_THICKNESS

        # 2 panneaux (gauche + droite)
        for side in [-1, 1]:
            panel = cube([half_w - TUBE_SIZE - 20, panel_t, facade_h])

            # Perforations hexagonales (partie basse)
            perf_h = facade_h * 0.35
            perfs = union()
            spacing = 28
            hole_r = 9
            nx = int((half_w - TUBE_SIZE - 60) / spacing)
            ny = int(perf_h / spacing)
            for ix in range(nx):
                for iy in range(ny):
                    px = 15 + ix * spacing + (spacing / 2 if iy % 2 else 0)
                    pz = 20 + iy * spacing
                    if px < half_w - TUBE_SIZE - 35:
                        perfs += translate([px, -0.5, pz])(
                            rotate([-90, 0, 0])(
                                cylinder(r=hole_r, h=panel_t + 1, _fn=6)
                            )
                        )
            panel -= perfs

            x_offset = TUBE_SIZE + 10 if side > 0 else 0
            if side > 0:
                facade += translate([x_offset, -panel_t, facade_z])(panel)
            else:
                facade += translate([-half_w + TUBE_SIZE + 10, -panel_t, facade_z])(panel)

        # Zone logo central
        logo_w = min(400, w * 0.3)
        logo_h = 50
        logo = cube([logo_w, panel_t + 4, logo_h])
        logo_z = facade_z + facade_h * 0.55
        facade += translate([-logo_w / 2, -panel_t - 4, logo_z])(logo)

        return facade

    # ------------------------------------------------------------------
    # LED strips
    # ------------------------------------------------------------------

    def _build_leds(self, w, h, d):
        """LED strips sur la facade et underglow."""
        leds = union()
        half_w = w / 2
        led_len = w - 4 * TUBE_SIZE
        led = cube([led_len, LED_STRIP_W, LED_STRIP_H])

        # LED haut facade
        leds += translate([-led_len / 2, -LED_STRIP_W - 5, h - 50])(led)
        # LED bas facade
        leds += translate([-led_len / 2, -LED_STRIP_W - 5, 180])(led)

        # LED underglow (sous la traverse basse)
        leds += translate([-led_len / 2, TUBE_SIZE / 2 - LED_STRIP_W / 2, 15])(led)

        # LED sur les cotes (plus courtes)
        side_led_len = d - 2 * TUBE_SIZE
        side_led = cube([LED_STRIP_W, side_led_len, LED_STRIP_H])
        # Cote droit
        leds += translate([half_w - LED_STRIP_W - 5, TUBE_SIZE, h - 50])(side_led)
        # Cote gauche
        leds += translate([-half_w + 5, TUBE_SIZE, h - 50])(side_led)

        return leds

    # ------------------------------------------------------------------
    # Plateau (surface de travail)
    # ------------------------------------------------------------------

    def _build_top(self, w, d, h):
        """Plateau contreplaque avec feutre + goupilles de positionnement."""
        top = union()

        overhang = 15  # debord du plateau
        top_w = w + 2 * overhang
        top_d = d + overhang  # debord seulement devant et cotes, pas derriere

        # Panneau principal
        panel = cube([top_w, top_d, TOP_PANEL_THICKNESS])
        top += translate([-top_w / 2, -overhang, h])(panel)

        # Feutre anti-derapant
        felt = cube([top_w - 40, top_d - 40, 1])
        top += translate([-top_w / 2 + 20, -overhang + 20, h + TOP_PANEL_THICKNESS])(felt)

        # Goupilles de positionnement (sous le plateau, s'inserent dans le cadre)
        pin_r = 4
        pin_h = 15
        pin = cylinder(r=pin_r, h=pin_h, _fn=16)
        half_w = w / 2
        for px in [-half_w + TUBE_SIZE / 2, -TUBE_SIZE / 2, TUBE_SIZE / 2, half_w - TUBE_SIZE / 2]:
            for py in [TUBE_SIZE / 2, d - TUBE_SIZE - TUBE_SIZE / 2]:
                top += translate([px, py, h - pin_h])(pin)

        return top

    # ------------------------------------------------------------------
    # Etagere intermediaire
    # ------------------------------------------------------------------

    def _build_shelf(self, w, d, h):
        """Etagere amovible a mi-hauteur (pour rangement cables/sac)."""
        shelf_h = h * 0.4  # position a 40% de la hauteur
        shelf_t = 12  # epaisseur etagere
        shelf_w = w - 4 * TUBE_SIZE
        shelf_d = d - 2 * TUBE_SIZE

        panel = cube([shelf_w, shelf_d, shelf_t])
        shelf = translate([-shelf_w / 2, TUBE_SIZE, shelf_h])(panel)

        # Tasseaux de support (boulons qui s'inserent dans les trous du cadre)
        bolt_r = 4
        bolt_l = 15
        bolt = rotate([0, 90, 0])(cylinder(r=bolt_r, h=bolt_l, _fn=16))
        half_w = w / 2
        # 2 boulons par cote
        for side_x in [-half_w + TUBE_SIZE, half_w - TUBE_SIZE - bolt_l]:
            for sy in [TUBE_SIZE + 30, d - TUBE_SIZE - 30]:
                shelf += translate([side_x, sy, shelf_h + shelf_t / 2])(bolt)

        return shelf

    # ------------------------------------------------------------------
    # Assemblage principal
    # ------------------------------------------------------------------

    def build(self):
        p = self.params
        w = p['width']
        h = p['height']
        d = p['depth']
        open_pct = p['open_pct']
        mode = p['export_part']

        # === CADRE PLIANT ===
        frame = self._build_frame(w, h, d, open_pct)

        if mode == 'frame':
            return frame

        # Les elements suivants ne sont visibles que deploye
        is_deployed = open_pct >= 95

        # === FACADE ===
        facade = union()
        if p['show_facade'] and is_deployed:
            facade = self._build_facade(w, h)

        if mode == 'facade':
            return facade

        # === PLATEAU ===
        top = union()
        if p['show_top'] and is_deployed:
            top = self._build_top(w, d, h)

        if mode == 'top':
            return top

        # === ETAGERE ===
        shelf = union()
        if p['show_shelf'] and is_deployed:
            shelf = self._build_shelf(w, d, h)

        if mode == 'shelf':
            return shelf

        # === LED ===
        leds = union()
        if p['show_leds'] and is_deployed:
            leds = self._build_leds(w, h, d)

        # === ASSEMBLAGE COMPLET ===
        assembly = frame

        if is_deployed:
            if p['show_facade']:
                assembly += facade
            if p['show_top']:
                assembly += top
            if p['show_shelf']:
                assembly += shelf
            if p['show_leds']:
                assembly += leds

        return assembly


if __name__ == "__main__":
    import sys
    # Vue deployee
    booth = BoothAssembly(open_pct=100)
    print("Generation booth Roadworx-style (deploye)...")
    scad_path = booth.save_scad()
    print(f"SCAD: {scad_path}")
    try:
        stl_path = booth.render_stl()
        print(f"STL: {stl_path}")
        print("OK")
    except Exception as e:
        print(f"Erreur STL: {e}", file=sys.stderr)
