#!/usr/bin/env python3
"""
DPS 3D System - Generation par lots depuis un manifeste JSON.

Usage:
    python -m models.batch manifest.json
    python -m models.batch --all
    python -m models.batch --all --scad-only

Format du manifeste JSON :
[
    {"model": "tablet_stand", "params": {"width": 250}},
    {
        "model": "table_number",
        "variants": [{"number": 1}, {"number": 2}, {"number": 3}],
        "shared_params": {"height": 120, "depth": 80}
    },
    {"model": "coaster"}
]

Chaque entree peut avoir :
  - "model" (requis) : nom du modele tel que dans MODEL_REGISTRY
  - "params" (optionnel) : dict de parametres pour une generation unique
  - "variants" (optionnel) : liste de dicts, genere un STL par variante
  - "shared_params" (optionnel) : parametres communs fusionnes avec chaque variante
"""
import argparse
import json
import os
import sys
import time

# Import du registre et des fonctions utilitaires depuis generate.py
from .generate import MODEL_REGISTRY, load_model_class


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _progress(current: int, total: int, model_name: str, suffix: str = "") -> None:
    """Affiche une ligne de progression sur stderr (ne pollue pas stdout)."""
    pct = int(current / total * 100) if total > 0 else 0
    label = f"[{current}/{total}] ({pct}%) {model_name}"
    if suffix:
        label += f" - {suffix}"
    print(label, file=sys.stderr)


def _generate_single(
    model_name: str,
    params: dict,
    scad_only: bool = False,
    name_override: str | None = None,
) -> dict:
    """
    Genere un seul modele. Retourne un dict de resultat.

    Args:
        model_name: Nom du modele dans le registre.
        params: Dictionnaire de parametres.
        scad_only: Si True, genere uniquement le SCAD.
        name_override: Nom de fichier alternatif (pour les variantes).

    Returns:
        Dict avec status, type, path ou message d'erreur.
    """
    try:
        model_cls = load_model_class(model_name)
    except SystemExit:
        # load_model_class appelle sys.exit en cas d'erreur ;
        # en mode batch on veut continuer, donc on capture
        return {
            "status": "error",
            "model": model_name,
            "message": f"Modele inconnu: '{model_name}'",
        }

    try:
        model = model_cls(**params)
    except (ValueError, TypeError) as exc:
        return {
            "status": "error",
            "model": model_name,
            "message": f"Parametres invalides: {exc}",
        }

    # Si un nom alternatif est demande, on ecrase model.name
    if name_override:
        model.name = name_override

    try:
        if scad_only:
            path = model.save_scad()
            return {
                "status": "ok",
                "type": "scad",
                "model": model_name,
                "path": os.path.abspath(path),
                "params": model.params,
            }
        else:
            path = model.render_stl()
            return {
                "status": "ok",
                "type": "stl",
                "model": model_name,
                "path": os.path.abspath(path),
                "params": model.params,
            }
    except FileNotFoundError:
        return {
            "status": "error",
            "model": model_name,
            "message": "OpenSCAD introuvable. Installe-le ou utilise --scad-only.",
        }
    except RuntimeError as exc:
        return {
            "status": "error",
            "model": model_name,
            "message": f"Erreur OpenSCAD: {exc}",
        }
    except Exception as exc:
        return {
            "status": "error",
            "model": model_name,
            "message": f"Erreur inattendue: {exc}",
        }


# ---------------------------------------------------------------------------
# Traitement du manifeste
# ---------------------------------------------------------------------------

def process_manifest(manifest: list[dict], scad_only: bool = False) -> list[dict]:
    """
    Traite une liste d'entrees de manifeste et genere les fichiers.

    Chaque entree peut etre :
      - Generation simple  : {"model": "...", "params": {...}}
      - Multi-variantes    : {"model": "...", "variants": [...], "shared_params": {...}}

    Retourne la liste des resultats (un dict par fichier genere).
    """
    # Compter le nombre total de fichiers a generer
    total = 0
    for entry in manifest:
        variants = entry.get("variants")
        if variants:
            total += len(variants)
        else:
            total += 1

    results: list[dict] = []
    current = 0

    for entry in manifest:
        model_name = entry.get("model")
        if not model_name:
            results.append({
                "status": "error",
                "model": None,
                "message": "Entree sans champ 'model' dans le manifeste.",
            })
            continue

        variants = entry.get("variants")
        shared_params = entry.get("shared_params", {})
        base_params = entry.get("params", {})

        if variants:
            # Mode multi-variantes : un fichier par variante
            for idx, variant_params in enumerate(variants, start=1):
                current += 1
                # Fusionner : shared_params < variant_params (priorite aux variantes)
                merged = {**shared_params, **variant_params}

                # Construire un suffixe descriptif pour le nom de fichier
                suffix = _variant_suffix(variant_params, idx)
                name_override = f"{model_name}_{suffix}"

                _progress(current, total, model_name, f"variante {suffix}")
                result = _generate_single(model_name, merged, scad_only, name_override)
                result["variant"] = variant_params
                results.append(result)
        else:
            # Mode simple
            current += 1
            merged = {**shared_params, **base_params}
            _progress(current, total, model_name)
            result = _generate_single(model_name, merged, scad_only)
            results.append(result)

    return results


def _variant_suffix(variant_params: dict, index: int) -> str:
    """
    Genere un suffixe lisible pour une variante.

    Si la variante contient une cle 'number', utilise sa valeur formatee
    sur 2 chiffres (ex: "01", "12"). Sinon, utilise l'index.
    """
    number = variant_params.get("number")
    if number is not None:
        return f"{int(number):02d}"
    # Sinon, suffixe generique base sur l'index
    return f"{index:02d}"


def build_all_manifest() -> list[dict]:
    """
    Construit un manifeste pour TOUS les modeles du registre,
    chacun avec ses parametres par defaut (pas de params supplementaires).
    """
    return [{"model": name} for name in MODEL_REGISTRY]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    """Construit le parser d'arguments CLI."""
    parser = argparse.ArgumentParser(
        prog="batch",
        description="DPS 3D System - Generation par lots de modeles parametriques",
    )
    parser.add_argument(
        "manifest",
        nargs="?",
        help="Chemin vers le fichier manifeste JSON",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        default=False,
        help="Generer tous les modeles du registre avec les parametres par defaut",
    )
    parser.add_argument(
        "--scad-only",
        action="store_true",
        default=False,
        help="Generer uniquement les fichiers SCAD (pas de rendu STL)",
    )
    return parser


def main() -> None:
    """Point d'entree principal."""
    parser = build_parser()
    args = parser.parse_args()

    # Validation : il faut soit un manifeste, soit --all
    if not args.manifest and not args.all:
        print(
            json.dumps({
                "status": "error",
                "message": "Specifie un fichier manifeste JSON ou utilise --all.",
            }),
        )
        sys.exit(1)

    # Construire le manifeste
    if args.all:
        manifest = build_all_manifest()
        print(
            f"Mode --all : generation de {len(manifest)} modeles avec parametres par defaut.",
            file=sys.stderr,
        )
    else:
        manifest_path = os.path.abspath(args.manifest)
        if not os.path.isfile(manifest_path):
            print(
                json.dumps({
                    "status": "error",
                    "message": f"Fichier manifeste introuvable: {manifest_path}",
                }),
            )
            sys.exit(1)

        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
        except json.JSONDecodeError as exc:
            print(
                json.dumps({
                    "status": "error",
                    "message": f"JSON invalide dans le manifeste: {exc}",
                }),
            )
            sys.exit(1)

        if not isinstance(manifest, list):
            print(
                json.dumps({
                    "status": "error",
                    "message": "Le manifeste doit etre un tableau JSON (liste d'objets).",
                }),
            )
            sys.exit(1)

        print(
            f"Manifeste charge : {len(manifest)} entrees depuis {manifest_path}",
            file=sys.stderr,
        )

    # Lancer la generation
    start_time = time.time()
    results = process_manifest(manifest, scad_only=args.scad_only)
    elapsed = time.time() - start_time

    # Bilan
    ok_count = sum(1 for r in results if r.get("status") == "ok")
    err_count = sum(1 for r in results if r.get("status") == "error")

    summary = {
        "status": "ok" if err_count == 0 else "partial",
        "total": len(results),
        "success": ok_count,
        "errors": err_count,
        "elapsed_seconds": round(elapsed, 2),
        "results": results,
    }

    # Afficher le bilan sur stderr
    print(f"\n{'=' * 50}", file=sys.stderr)
    print(f"Batch termine en {elapsed:.1f}s", file=sys.stderr)
    print(f"  Succes  : {ok_count}/{len(results)}", file=sys.stderr)
    print(f"  Erreurs : {err_count}/{len(results)}", file=sys.stderr)
    print(f"{'=' * 50}", file=sys.stderr)

    # Sortie JSON structuree sur stdout
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    # Code de sortie
    if err_count == len(results) and len(results) > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
