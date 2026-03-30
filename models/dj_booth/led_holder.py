"""
Support LED WS2812B pour DJ Booth - Canal en U avec fixation T-slot
Maintient les bandes LED WS2812B sur les profiles aluminium 2040.
Canal en U avec option diffuseur translucide. 14 necessaires pour le booth complet.
~20g chacun en PLA standard.
"""
from solid2 import *
from ..base import ParametricModel
from ._constants import (
    LED_STRIP_W, LED_STRIP_H, LED_STRIP_MARGIN,
    LED_CHANNEL_W, LED_CONNECTOR_W,
    SLOT_WIDTH, SLOT_DEPTH, SLOT_CLEARANCE, FIT_CLEARANCE
)


class BoothLedHolder(ParametricModel):

    def __init__(self, **params):
        super().__init__("booth_led_holder", **params)

    def default_params(self):
        return {
            'length': 200.0,
            'channel_type': 'open',
            'channel_width': LED_CHANNEL_W,
            'channel_depth': 5.0,
            'wall_thickness': 2.0,
            'mount_type': 'tslot',
            'mount_count': 2,
            'connector_cutout': True,
            'connector_width': LED_CONNECTOR_W,
            'angle': 0.0,
        }

    def param_schema(self):
        return {
            'length': {
                'type': 'float', 'min': 50, 'max': 500, 'unit': 'mm',
                'description': 'Longueur du segment (correspond a la taille tuile)'
            },
            'channel_type': {
                'type': 'string', 'options': ['open', 'diffused', 'indirect'],
                'description': 'Type de canal : open, diffused (couvercle translucide), indirect (eclairage rebond)'
            },
            'channel_width': {
                'type': 'float', 'min': 10, 'max': 25, 'unit': 'mm',
                'description': 'Largeur interne du canal U (LED 12mm + marges)'
            },
            'channel_depth': {
                'type': 'float', 'min': 3, 'max': 15, 'unit': 'mm',
                'description': 'Profondeur du canal U'
            },
            'wall_thickness': {
                'type': 'float', 'min': 1.2, 'max': 5, 'unit': 'mm',
                'description': 'Epaisseur des parois laterales et du fond'
            },
            'mount_type': {
                'type': 'string', 'options': ['tslot', 'clip'],
                'description': 'Mode de fixation sur le profil 2040'
            },
            'mount_count': {
                'type': 'int', 'min': 1, 'max': 6,
                'description': 'Nombre de points de fixation le long du support'
            },
            'connector_cutout': {
                'type': 'bool',
                'description': 'Decoupes aux extremites pour connecteurs LED'
            },
            'connector_width': {
                'type': 'float', 'min': 10, 'max': 25, 'unit': 'mm',
                'description': 'Largeur de la decoupe connecteur'
            },
            'angle': {
                'type': 'float', 'min': -90, 'max': 90, 'unit': 'deg',
                'description': 'Angle d\'inclinaison (0=droit, pour eclairage indirect)'
            },
        }

    def build(self):
        p = self.params
        length = p['length']
        ch_w = p['channel_width']
        ch_d = p['channel_depth']
        wt = p['wall_thickness']
        ch_type = p['channel_type']
        n_mounts = p['mount_count']
        conn_w = p['connector_width']

        total_w = ch_w + 2 * wt  # largeur externe totale

        # -- 1. Plaque de fond du canal U --
        base_plate = cube([length, total_w, wt])

        # -- 2. Parois laterales du canal U --
        wall_h = ch_d + wt  # hauteur totale paroi
        wall_left = translate([0, 0, 0])(
            cube([length, wt, wall_h])
        )
        wall_right = translate([0, total_w - wt, 0])(
            cube([length, wt, wall_h])
        )

        model = base_plate + wall_left + wall_right

        # -- 3. Couvercle diffuseur (0.8mm en PLA translucide) --
        if ch_type == 'diffused':
            diffuser_thickness = 0.8
            diffuser = translate([0, wt, wall_h])(
                cube([length, ch_w, diffuser_thickness])
            )
            model = model + diffuser

        # -- 4. Tabs T-slot (fixation dans la rainure 2040) --
        if p['mount_type'] == 'tslot':
            tab_w = SLOT_WIDTH - 2 * SLOT_CLEARANCE
            tab_d = SLOT_DEPTH - SLOT_CLEARANCE
            tab_len = 15.0  # longueur individuelle de chaque tab

            spacing = length / (n_mounts + 1)
            for i in range(n_mounts):
                x_pos = spacing * (i + 1) - tab_len / 2
                tab = translate([x_pos, (total_w - tab_w) / 2, -tab_d])(
                    cube([tab_len, tab_w, tab_d])
                )
                model = model + tab

        # -- 5. Clips de fixation (alternative au T-slot) --
        if p['mount_type'] == 'clip':
            clip_h = 6.0
            clip_w = 8.0
            clip_lip = 1.5
            spacing = length / (n_mounts + 1)
            for i in range(n_mounts):
                x_pos = spacing * (i + 1) - clip_w / 2
                # Base du clip
                clip_base = translate([x_pos, (total_w - clip_w) / 2, -clip_h])(
                    cube([clip_w, clip_w, clip_h])
                )
                # Levre d'accroche de chaque cote
                lip_left = translate([x_pos, (total_w - clip_w) / 2 - clip_lip, -clip_h])(
                    cube([clip_w, clip_lip, 2.0])
                )
                lip_right = translate([x_pos, (total_w + clip_w) / 2, -clip_h])(
                    cube([clip_w, clip_lip, 2.0])
                )
                model = model + clip_base + lip_left + lip_right

        # -- 6. Decoupes connecteurs aux extremites --
        if p['connector_cutout']:
            cutout_h = ch_d
            cutout_margin = wt  # commence au-dessus de la plaque de fond

            # Decoupe cote X=0
            cutout_start = translate([-0.1, (total_w - conn_w) / 2, wt])(
                cube([wt + 0.2, conn_w, cutout_h + 0.1])
            )
            # Decoupe cote X=length
            cutout_end = translate([length - wt - 0.1, (total_w - conn_w) / 2, wt])(
                cube([wt + 0.2, conn_w, cutout_h + 0.1])
            )
            model = model - cutout_start - cutout_end

        # -- 7. Encoches passage cable dans le fond du canal --
        notch_w = 6.0
        notch_d = wt + 0.2  # traverse toute l'epaisseur du fond
        notch_len = 4.0

        # Encoche cote X=0
        notch_start = translate([-0.1, (total_w - notch_w) / 2, -0.1])(
            cube([notch_len + 0.1, notch_w, notch_d])
        )
        # Encoche cote X=length
        notch_end = translate([length - notch_len, (total_w - notch_w) / 2, -0.1])(
            cube([notch_len + 0.1, notch_w, notch_d])
        )
        model = model - notch_start - notch_end

        # -- 8. Rotation pour eclairage indirect --
        if ch_type == 'indirect' and p['angle'] != 0.0:
            # Pivot autour de l'axe X au centre du support
            model = translate([0, total_w / 2, 0])(
                rotate([0, 0, 0])(
                    rotate([p['angle'], 0, 0])(
                        translate([0, -total_w / 2, 0])(model)
                    )
                )
            )

        return model


if __name__ == "__main__":
    import sys

    # Version standard (open)
    holder = BoothLedHolder()
    print(f"Generation support LED booth (open)...")
    print(f"Parametres: {holder.params}")
    scad_path = holder.save_scad()
    print(f"SCAD: {scad_path}")
    try:
        stl_path = holder.render_stl()
        print(f"STL: {stl_path}")
        print("OK")
    except Exception as e:
        print(f"Erreur STL: {e}", file=sys.stderr)

    # Version diffuseur
    holder_diff = BoothLedHolder(channel_type='diffused')
    holder_diff.name = "booth_led_holder_diffused"
    print(f"\nGeneration support LED booth (diffused)...")
    scad_path = holder_diff.save_scad()
    print(f"SCAD: {scad_path}")
    try:
        stl_path = holder_diff.render_stl()
        print(f"STL: {stl_path}")
        print("OK")
    except Exception as e:
        print(f"Erreur STL: {e}", file=sys.stderr)

    # Version indirect (45 degres)
    holder_ind = BoothLedHolder(channel_type='indirect', angle=45.0)
    holder_ind.name = "booth_led_holder_indirect_45"
    print(f"\nGeneration support LED booth (indirect 45deg)...")
    scad_path = holder_ind.save_scad()
    print(f"SCAD: {scad_path}")
    try:
        stl_path = holder_ind.render_stl()
        print(f"STL: {stl_path}")
        print("OK")
    except Exception as e:
        print(f"Erreur STL: {e}", file=sys.stderr)
