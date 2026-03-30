"""
DJ Prestige Sound - Constantes de marque pour modeles 3D
Toutes les valeurs de branding centralisees ici.
"""

# Identite de marque
BRAND_NAME = "DJ PRESTIGE SOUND"
BRAND_NAME_SHORT = "DPS"
BRAND_TAGLINE = "Premium Event Entertainment"

# Couleurs (reference pour UI et documentation)
COLOR_GOLD = "#C9A962"
COLOR_GOLD_LIGHT = "#E8D5A3"
COLOR_BLACK = "#1A1A1A"
COLOR_CHAMPAGNE_BG = "#F7F3E9"
COLOR_WHITE = "#FFFFFF"
COLOR_GRAY_TEXT = "#444444"

# Dimensions par defaut (mm)
DEFAULT_WALL_THICKNESS = 2.5
DEFAULT_BASE_THICKNESS = 3.0
DEFAULT_CORNER_RADIUS = 2.0
DEFAULT_TEXT_DEPTH = 1.0
DEFAULT_TEXT_HEIGHT = 8.0
DEFAULT_TEXT_FONT = "Liberation Sans:style=Bold"

# Contraintes imprimante FDM generique
MIN_WALL = 0.8
MAX_OVERHANG_ANGLE = 45
LAYER_HEIGHT = 0.2
NOZZLE_DIAMETER = 0.4

# ==========================================================================
# Profil Creality K2 Pro (imprimante principale depuis mars 2026)
# ==========================================================================
K2_PRO = {
    'name': 'Creality K2 Pro',
    'type': 'CoreXY',
    'volume': (300, 300, 300),
    'nozzle': 0.4,
    'nozzle_type': 'hardened-steel',
    'filament_diameter': 1.75,
    'temp_nozzle_max': 300,
    'temp_bed_max': 110,
    'temp_chamber_max': 60,
    'chamber_heated': True,
    'multi_color': True,
    'multi_color_system': 'CFS',
    'max_slots': 4,
    'speed_max': 600,
    'acceleration': 20000,
    'slicer': 'OrcaSlicer',
    'profiles': {
        'draft':    {'layer_height': 0.28, 'speed': 300, 'infill': 15},
        'standard': {'layer_height': 0.20, 'speed': 200, 'infill': 20},
        'quality':  {'layer_height': 0.12, 'speed': 120, 'infill': 25},
        'ultra':    {'layer_height': 0.08, 'speed': 80,  'infill': 30},
    },
    'slots': {
        1: {'material': 'PLA+', 'color': COLOR_BLACK, 'name': 'Noir mat', 'brand': 'eSun'},
        2: {'material': 'PLA-Silk', 'color': COLOR_GOLD, 'name': 'Or Prestige', 'brand': 'eSun'},
        3: {'material': 'PLA+', 'color': COLOR_WHITE, 'name': 'Blanc', 'brand': 'eSun'},
        4: {'material': 'PLA', 'color': '#90EE90', 'name': 'Vert test', 'brand': 'Nice Essentials'},
    },
}

# Materiaux multi-couleur K2 Pro
MULTICOLOR_BLACK_GOLD = {'body': 1, 'accent': 2}  # Slot 1 = noir, Slot 2 = or
MULTICOLOR_BLACK_WHITE = {'body': 1, 'accent': 3}  # Slot 1 = noir, Slot 3 = blanc

# Textes logo pour gravure 3D
LOGO_TEXT_PRIMARY = "PRESTIGE SOUND"
LOGO_TEXT_SECONDARY = "DJ"

# ==========================================================================
# Profils machines CityFab (Bruxelles)
# Source: modes d'emploi officiels CityFab1, fevrier 2026
# ==========================================================================

CITYFAB_PROFILES = {
    # ----- Impression 3D FDM : Big Builder Large (CityFab1) -----
    'bigbuilder': {
        'name': 'Big Builder Large (CityFab1)',
        'type': 'FDM',
        'slicer': 'Cura',  # PAS PrusaSlicer!
        'volume': (215, 205, 600),  # mm (largeur, profondeur, hauteur)
        'nozzle': 0.4,  # mm
        'filament_diameter': 1.75,  # mm
        'material': 'PLA',
        'temp_nozzle': (200, 210),  # degres C (min, max recommande)
        'temp_bed': (50, 60),  # degres C
        'profiles': {
            'coarse': {'layer_height': 0.3, 'description': 'Rapide, prototypage'},
            'normal': {'layer_height': 0.2, 'description': 'Standard, bon compromis'},
            'fine':   {'layer_height': 0.1, 'description': 'Haute qualite, lent'},
        },
        'defaults': {
            'layer_height': 0.2,
            'wall_thickness': 0.8,  # 2x buse
            'top_bottom_thickness': 0.8,  # 4x layer_height
            'infill_density': 20,  # % pour decoratif
            'infill_pattern': 'tri_hexagon',
            'support_angle': 45,  # degres - supports au-dela
            'adhesion_type': 'brim',
            'brim_width': 8,  # mm
            'print_speed': 50,  # mm/s
        },
        'tarif': '0.10 EUR/g + 1 EUR/h apres 8h',
        'export': 'G-code sur cle USB',
    },

    # ----- Impression 3D SLA : Formlabs Form 2 (CityFab1) -----
    'form2': {
        'name': 'Formlabs Form 2 (CityFab1)',
        'type': 'SLA',
        'slicer': 'PreForm',
        'volume': (145, 145, 175),  # mm
        'material': 'Resine Clear',
        'profiles': {
            'standard': {'layer_height': 0.1,  'description': 'Standard'},
            'fine':     {'layer_height': 0.05, 'description': 'Details fins'},
            'ultra':    {'layer_height': 0.025, 'description': 'Ultra-fin (25 microns)'},
        },
        'post_processing': 'Lavage alcool isopropylique + cure UV obligatoire',
        'tarif': '0.50 EUR/ml',
    },

    # ----- Decoupe laser : ML Laser (CityFab1) -----
    'laser': {
        'name': 'ML Laser CO2 80W (CityFab1)',
        'type': 'Laser',
        'software': 'LaserCut 6',
        'surfaces': {
            'grande': (1200, 900),  # mm
            'petite': (900, 600),   # mm (x2 unites)
        },
        'file_format': 'DXF',  # R14 ou R12 - PAS SVG!
        'file_format_engrave': 'BMP',
        'operations': {
            'decoupe': {'speed': (4, 100), 'power': (6, 80), 'unit': 'mm/s, %'},
            'gravure': {'speed': (100, 600), 'power': (0, 50), 'unit': 'mm/s, %'},
        },
        'scangap': (0.06, 0.1),  # mm - espacement gravure
        'max_thickness': 6,  # mm decoupe max
        'materials_ok': [
            'bois', 'contreplaque', 'acrylique/PMMA/Plexiglas',
            'cuir', 'feutre', 'tissu', 'papier', 'carton', 'caoutchouc',
            'Nylon/PA', 'ABS', 'PP', 'PET', 'PS',
        ],
        'materials_interdit': [
            'PVC (chlore toxique!)',
            'MDF (encrasse les machines!)',
            'miroirs',
            'metal (puissance insuffisante)',
        ],
        'tarif': '0.50 EUR/minute',
    },

    # ----- CNC (reference) -----
    'cnc_grande': {
        'name': 'CNC ML6090 (CityFab1)',
        'type': 'CNC',
        'surface': (2400, 1500),
        'profondeur_z': 150,  # max utile 70mm
        'precision': 0.05,
        'tarif': '25 EUR/demi-journee, 45 EUR/journee',
    },
}


def validate_for_cityfab(model_name, params, profile='bigbuilder'):
    """
    Valide que les dimensions d'un modele sont compatibles avec CityFab.
    Retourne une liste d'avertissements (vide si tout est OK).
    """
    warnings = []
    machine = CITYFAB_PROFILES.get(profile, {})
    vol = machine.get('volume')

    if not vol:
        return warnings

    # Verification du volume d'impression
    dims = []
    for key in ('width', 'base_width', 'total_width'):
        if key in params:
            dims.append(('largeur', params[key], vol[0]))
    for key in ('depth', 'base_depth', 'total_depth', 'length'):
        if key in params:
            dims.append(('profondeur', params[key], vol[1]))
    for key in ('height', 'base_height', 'total_height'):
        if key in params:
            dims.append(('hauteur', params[key], vol[2]))

    for dim_name, val, limit in dims:
        if val > limit:
            warnings.append(
                f"La {dim_name} ({val}mm) depasse le volume {machine['name']} ({limit}mm)"
            )

    # Verification epaisseur paroi (multiples de 0.4mm)
    nozzle = machine.get('nozzle', 0.4)
    for key in ('wall_thickness', 'base_thickness', 'rim_thickness'):
        if key in params:
            val = params[key]
            if val < nozzle * 2:
                warnings.append(
                    f"{key} ({val}mm) trop fin. Minimum recommande: {nozzle * 2}mm (2x buse)"
                )

    return warnings
