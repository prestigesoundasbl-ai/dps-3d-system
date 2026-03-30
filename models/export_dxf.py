#!/usr/bin/env python3
"""
DPS 3D System - Export DXF pour decoupe laser CityFab1.

CityFab1 utilise LaserCut 6 qui requiert le format DXF (R14 ou R12).
Ce module convertit notre logo SVG et les contours 2D en fichiers DXF
compatibles avec les decoupeuses laser ML.

Usage CLI:
    python -m models.export_dxf logo --width=100
    python -m models.export_dxf logo --width=100 --output=output/dxf/logo_100mm.dxf
    python -m models.export_dxf coaster --diameter=90
    python -m models.export_dxf nameplate --width=120 --height=60

Specification CityFab1:
    - Format: DXF R14 (ou R12)
    - Logiciel: LaserCut 6
    - Couleurs definissent le type d'operation:
      - Noir (0): decoupe
      - Rouge (1): gravure
      - Bleu (5): marquage
    - Surface max: 1200x900mm (grande) ou 900x600mm (petite)
"""
import argparse
import json
import math
import os
import sys

# Repertoire de sortie
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'output')
DXF_DIR = os.path.join(OUTPUT_DIR, 'dxf')


def _ensure_dxf_dir():
    """Cree le repertoire dxf s'il n'existe pas."""
    os.makedirs(DXF_DIR, exist_ok=True)


class DXFWriter:
    """
    Generateur DXF minimal compatible R14 / LaserCut 6.
    Ecrit des entites de base: LINE, CIRCLE, ARC, LWPOLYLINE, TEXT.
    Les couleurs ACI (AutoCAD Color Index) definissent le type d'operation:
      - 0 (noir/blanc): decoupe
      - 1 (rouge): gravure rapide
      - 5 (bleu): marquage/gravure lente
    """

    def __init__(self):
        self.entities = []

    def add_line(self, x1, y1, x2, y2, color=0, layer='0'):
        """Ajoute un segment de ligne."""
        self.entities.append(
            f"  0\nLINE\n  8\n{layer}\n 62\n{color}\n"
            f" 10\n{x1:.4f}\n 20\n{y1:.4f}\n 30\n0.0\n"
            f" 11\n{x2:.4f}\n 21\n{y2:.4f}\n 31\n0.0\n"
        )

    def add_circle(self, cx, cy, radius, color=0, layer='0'):
        """Ajoute un cercle."""
        self.entities.append(
            f"  0\nCIRCLE\n  8\n{layer}\n 62\n{color}\n"
            f" 10\n{cx:.4f}\n 20\n{cy:.4f}\n 30\n0.0\n"
            f" 40\n{radius:.4f}\n"
        )

    def add_rectangle(self, x, y, width, height, color=0, layer='0'):
        """Ajoute un rectangle (4 lignes)."""
        pts = [
            (x, y), (x + width, y),
            (x + width, y + height), (x, y + height)
        ]
        for i in range(4):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % 4]
            self.add_line(x1, y1, x2, y2, color, layer)

    def add_rounded_rectangle(self, x, y, width, height, radius, color=0, layer='0'):
        """Ajoute un rectangle avec coins arrondis (lignes + arcs)."""
        r = min(radius, width / 2, height / 2)
        if r <= 0:
            self.add_rectangle(x, y, width, height, color, layer)
            return

        # Lignes droites
        self.add_line(x + r, y, x + width - r, y, color, layer)  # bas
        self.add_line(x + width, y + r, x + width, y + height - r, color, layer)  # droite
        self.add_line(x + width - r, y + height, x + r, y + height, color, layer)  # haut
        self.add_line(x, y + height - r, x, y + r, color, layer)  # gauche

        # Arcs (coins)
        self.add_arc(x + r, y + r, r, 180, 270, color, layer)  # bas-gauche
        self.add_arc(x + width - r, y + r, r, 270, 360, color, layer)  # bas-droite
        self.add_arc(x + width - r, y + height - r, r, 0, 90, color, layer)  # haut-droite
        self.add_arc(x + r, y + height - r, r, 90, 180, color, layer)  # haut-gauche

    def add_arc(self, cx, cy, radius, start_angle, end_angle, color=0, layer='0'):
        """Ajoute un arc de cercle (angles en degres)."""
        self.entities.append(
            f"  0\nARC\n  8\n{layer}\n 62\n{color}\n"
            f" 10\n{cx:.4f}\n 20\n{cy:.4f}\n 30\n0.0\n"
            f" 40\n{radius:.4f}\n"
            f" 50\n{start_angle:.4f}\n 51\n{end_angle:.4f}\n"
        )

    def add_text(self, x, y, height, text, color=1, layer='GRAVURE'):
        """Ajoute du texte (pour gravure laser)."""
        self.entities.append(
            f"  0\nTEXT\n  8\n{layer}\n 62\n{color}\n"
            f" 10\n{x:.4f}\n 20\n{y:.4f}\n 30\n0.0\n"
            f" 40\n{height:.4f}\n"
            f"  1\n{text}\n"
            f" 72\n1\n"  # Centre horizontal
            f" 11\n{x:.4f}\n 21\n{y:.4f}\n 31\n0.0\n"
        )

    def save(self, filepath):
        """Ecrit le fichier DXF complet."""
        with open(filepath, 'w') as f:
            # Header minimal
            f.write("  0\nSECTION\n  2\nHEADER\n")
            f.write("  9\n$ACADVER\n  1\nAC1014\n")  # R14
            f.write("  0\nENDSEC\n")

            # Tables (layers)
            f.write("  0\nSECTION\n  2\nTABLES\n")
            f.write("  0\nTABLE\n  2\nLAYER\n")
            # Layer DECOUPE (noir)
            f.write("  0\nLAYER\n  2\nDECOUPE\n 70\n0\n 62\n0\n  6\nContinuous\n")
            # Layer GRAVURE (rouge)
            f.write("  0\nLAYER\n  2\nGRAVURE\n 70\n0\n 62\n1\n  6\nContinuous\n")
            # Layer MARQUAGE (bleu)
            f.write("  0\nLAYER\n  2\nMARQUAGE\n 70\n0\n 62\n5\n  6\nContinuous\n")
            f.write("  0\nENDTAB\n")
            f.write("  0\nENDSEC\n")

            # Entities
            f.write("  0\nSECTION\n  2\nENTITIES\n")
            for entity in self.entities:
                f.write(entity)
            f.write("  0\nENDSEC\n")

            # EOF
            f.write("  0\nEOF\n")

        return filepath


def export_logo_dxf(width=100, output=None):
    """
    Exporte le contour du logo DPS en DXF pour gravure laser.
    Note: Le logo SVG complexe (94 paths) ne peut pas etre converti
    directement en DXF simple. On genere un cadre + texte pour gravure.

    Pour le vrai logo vectoriel, utiliser Inkscape:
      1. Ouvrir logo-prestige-sound-3d.svg dans Inkscape
      2. Fichier > Enregistrer sous > DXF R14 (*.dxf)
      3. Utiliser ce DXF dans LaserCut 6

    Cette fonction genere un DXF complementaire avec:
      - Contour de decoupe (couche DECOUPE, noir)
      - Texte de marque pour gravure (couche GRAVURE, rouge)
    """
    _ensure_dxf_dir()
    dxf = DXFWriter()

    height = width * 0.3  # Ratio logo DPS

    # Contour de decoupe - rectangle arrondi
    dxf.add_rounded_rectangle(0, 0, width, height, radius=3, color=0, layer='DECOUPE')

    # Texte grave au centre
    text_size = height * 0.35
    dxf.add_text(width / 2, height / 2, text_size, "DJ PRESTIGE SOUND",
                 color=1, layer='GRAVURE')

    if output is None:
        output = os.path.join(DXF_DIR, f"logo_dps_{int(width)}mm.dxf")

    dxf.save(output)
    return output


def export_coaster_dxf(diameter=90, text="DJ PRESTIGE SOUND", output=None):
    """Exporte un sous-verre pour decoupe laser."""
    _ensure_dxf_dir()
    dxf = DXFWriter()
    r = diameter / 2

    # Contour de decoupe - cercle
    dxf.add_circle(r, r, r, color=0, layer='DECOUPE')

    # Texte grave
    text_size = diameter * 0.06
    dxf.add_text(r, r, text_size, text, color=1, layer='GRAVURE')

    if output is None:
        output = os.path.join(DXF_DIR, f"coaster_{int(diameter)}mm.dxf")

    dxf.save(output)
    return output


def export_nameplate_dxf(width=120, height=60, text="DJ PRESTIGE SOUND",
                         corner_radius=3, output=None):
    """Exporte une plaque pour decoupe + gravure laser."""
    _ensure_dxf_dir()
    dxf = DXFWriter()

    # Contour de decoupe
    dxf.add_rounded_rectangle(0, 0, width, height, corner_radius,
                              color=0, layer='DECOUPE')

    # Texte principal grave
    text_size = height * 0.15
    dxf.add_text(width / 2, height / 2, text_size, text,
                 color=1, layer='GRAVURE')

    # Ligne decorative sous le texte
    margin = width * 0.15
    y_line = height * 0.3
    dxf.add_line(margin, y_line, width - margin, y_line,
                 color=5, layer='MARQUAGE')

    if output is None:
        output = os.path.join(DXF_DIR, f"nameplate_{int(width)}x{int(height)}mm.dxf")

    dxf.save(output)
    return output


def export_table_number_dxf(number=1, width=80, height=100, output=None):
    """Exporte un numero de table pour decoupe + gravure laser."""
    _ensure_dxf_dir()
    dxf = DXFWriter()

    # Contour de decoupe
    dxf.add_rounded_rectangle(0, 0, width, height, 5,
                              color=0, layer='DECOUPE')

    # Numero principal
    num_size = height * 0.5
    dxf.add_text(width / 2, height * 0.55, num_size, str(number),
                 color=1, layer='GRAVURE')

    # Marque en bas
    brand_size = height * 0.06
    dxf.add_text(width / 2, height * 0.12, brand_size, "DJ PRESTIGE SOUND",
                 color=5, layer='MARQUAGE')

    if output is None:
        output = os.path.join(DXF_DIR, f"table_number_{number:02d}.dxf")

    dxf.save(output)
    return output


# ========================================================================
# CLI
# ========================================================================

def main():
    parser = argparse.ArgumentParser(
        description='DPS 3D System - Export DXF pour laser CityFab1'
    )
    parser.add_argument('type', choices=['logo', 'coaster', 'nameplate', 'table_number'],
                        help='Type d\'export')
    parser.add_argument('--width', type=float, default=100, help='Largeur en mm')
    parser.add_argument('--height', type=float, default=0, help='Hauteur en mm (0=auto)')
    parser.add_argument('--diameter', type=float, default=90, help='Diametre en mm (coaster)')
    parser.add_argument('--text', type=str, default='DJ PRESTIGE SOUND', help='Texte')
    parser.add_argument('--number', type=int, default=1, help='Numero (table_number)')
    parser.add_argument('--output', type=str, default=None, help='Chemin fichier sortie')

    args = parser.parse_args()

    if args.type == 'logo':
        path = export_logo_dxf(width=args.width, output=args.output)
    elif args.type == 'coaster':
        path = export_coaster_dxf(diameter=args.diameter, text=args.text,
                                   output=args.output)
    elif args.type == 'nameplate':
        h = args.height if args.height > 0 else args.width * 0.5
        path = export_nameplate_dxf(width=args.width, height=h, text=args.text,
                                     output=args.output)
    elif args.type == 'table_number':
        path = export_table_number_dxf(number=args.number, width=args.width,
                                        height=args.height if args.height > 0 else args.width * 1.25,
                                        output=args.output)

    result = {
        'status': 'ok',
        'type': args.type,
        'path': os.path.abspath(path),
        'format': 'DXF R14',
        'compatible': 'LaserCut 6 (CityFab1)',
        'layers': {
            'DECOUPE': 'Contour de decoupe (noir, couleur 0)',
            'GRAVURE': 'Zone de gravure (rouge, couleur 1)',
            'MARQUAGE': 'Marquage fin (bleu, couleur 5)',
        },
    }
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
