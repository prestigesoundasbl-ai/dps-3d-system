"""
Constantes partagees pour le DJ Booth modulaire.
Dimensions des profiles aluminium 2040, LED strips, et enveloppe du booth.
"""

# ========================================================================
# Profil Aluminium 2040 (mm)
# ========================================================================
PROFILE_W = 20.0            # Largeur face (20mm)
PROFILE_H = 40.0            # Hauteur face (40mm)
SLOT_WIDTH = 6.0            # Ouverture rainure T
SLOT_DEPTH = 6.2            # Profondeur rainure T
SLOT_CENTER = 10.0          # Centre rainure depuis chaque bord
CORE_HOLE = 4.2             # Trou central dans le profil

# Visserie
M5_HOLE = 5.3               # Trou de passage M5 avec jeu
M5_HEAD = 8.5               # Fraisage tete bouton M5
M5_HEAD_DEPTH = 3.0         # Profondeur fraisage
M4_HOLE = 4.3               # Trou de passage M4
WOOD_SCREW_HOLE = 3.5       # Vis a bois standard
WOOD_SCREW_HEAD = 7.0       # Tete vis a bois

# Tolerances impression 3D (Optimise pour CityFab Big Builder 0.4mm nozzle)
FIT_CLEARANCE = 0.2         # Jeu ajuste (etait 0.3)
PRESS_FIT = 0.1             # Emboitement serre (etait 0.15)
SLOT_CLEARANCE = 0.2        # Jeu dans la rainure T

# ========================================================================
# Bande LED WS2812B
# ========================================================================
LED_STRIP_W = 12.0          # Largeur PCB
LED_STRIP_H = 3.0           # Epaisseur avec adhesif
LED_STRIP_MARGIN = 1.0      # Marge de chaque cote
LED_CHANNEL_W = LED_STRIP_W + 2 * LED_STRIP_MARGIN  # 14mm
LED_CONNECTOR_W = 15.0      # Largeur connecteur 3 broches

# ========================================================================
# Dimensions generales du booth
# ========================================================================
BOOTH_WIDTH = 1200.0         # Largeur totale (mm)
BOOTH_DEPTH = 500.0          # Profondeur (mm)
BOOTH_HEIGHT = 1150.0        # Hauteur surface de travail (pour DJ 200cm)
FACADE_HEIGHT = 900.0        # Hauteur facade visible (sol+250 a plateau)
FACADE_BOTTOM = 250.0        # Espace sous la facade (pieds visibles)

# Plateau
TOP_PANEL_THICKNESS = 18.0   # Contreplaque standard

# Tuiles facade
TILE_SIZE = 200.0            # Dimension nominale tuile (mm)
TILE_THICKNESS = 4.0         # Epaisseur paroi tuile
TILE_CLIP_DEPTH = 8.0        # Profondeur d'engagement clip

# ========================================================================
# Fonctions helper pour la geometrie T-slot
# ========================================================================
def tslot_tab_dims(length=20.0):
    """Retourne (largeur, profondeur, longueur) d'un tab T-slot."""
    w = SLOT_WIDTH - 2 * SLOT_CLEARANCE
    d = SLOT_DEPTH - SLOT_CLEARANCE
    return (w, d, length)


# ========================================================================
# Systeme pliable / Quick-Release
# ========================================================================
HINGE_PIN_D = 6.0               # Diametre axe de charniere (tige acier 6mm)
HINGE_BARREL_OD = 14.0          # Diametre externe du barrel charniere
HINGE_BARREL_LEN = 20.0         # Longueur de chaque barrel
BALL_LOCK_PIN_D = 6.0           # Diametre ball-lock pin standard
BALL_LOCK_BODY_D = 10.0         # Diametre du corps du pin
BALL_LOCK_DEPTH = 15.0          # Profondeur du receptacle

# ========================================================================
# Accordion DJ Booth - Structure tubes alu 25x25mm
# ========================================================================
ACCORDION_TUBE = 25.0               # Section tube alu carre
ACCORDION_TUBE_WALL = 2.0           # Epaisseur paroi tube alu
ACCORDION_PANEL_T = 4.0             # Epaisseur panneau imprime
ACCORDION_INSERT_CLEARANCE = 0.3    # Jeu insert dans tube
ACCORDION_TUBE_INSERT = 24.4        # tube - 2*clearance (insert carre)
M10_THREAD_D = 10.0                 # Vis de nivelage M10
M10_NUT_AF = 17.0                   # Ecrou M10 cotes plats (across flats)
