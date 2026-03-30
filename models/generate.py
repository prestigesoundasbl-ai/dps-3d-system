#!/usr/bin/env python3
"""
DPS 3D System - CLI pour generer un modele parametrique individuel.

Usage:
    python -m models.generate tablet_stand
    python -m models.generate tablet_stand --scad-only
    python -m models.generate table_number --params-json '{"number": 5}'
    python -m models.generate cable_clip --width=40 --height=25
    python -m models.generate --list

Sortie JSON sur stdout pour integration avec le serveur Express.
"""
import argparse
import importlib
import json
import os
import sys

# ---------------------------------------------------------------------------
# Registre de tous les modeles disponibles
# Format : "nom_cli" -> "sous_package.module.Classe"
# L'import dynamique resoudra models.<sous_package>.<module>.<Classe>
# ---------------------------------------------------------------------------
MODEL_REGISTRY: dict[str, str] = {
    # --- DJ Equipment (5) ---
    "tablet_stand":        "dj_equipment.tablet_stand.TabletStand",
    "cable_clip":          "dj_equipment.cable_clip.CableClip",
    "headphone_holder":    "dj_equipment.headphone_holder.HeadphoneHolder",
    "speaker_shelf":       "dj_equipment.speaker_shelf.SpeakerShelf",
    "cable_cover":         "dj_equipment.cable_cover.CableCover",
    "flycase_booth":       "dj_equipment.flycase_booth.FlycaseBooth",
    # --- Event (6) ---
    "table_number":        "event.table_number.TableNumber",
    "place_card":          "event.place_card.PlaceCard",
    "menu_holder":         "event.menu_holder.MenuHolder",
    "cake_topper_base":    "event.cake_topper_base.CakeTopperBase",
    "business_card_holder": "event.business_card_holder.BusinessCardHolder",
    "trophy_base":         "event.trophy_base.TrophyBase",
    # --- Branded (4) ---
    "logo_nameplate":      "branded.logo_nameplate.LogoNameplate",
    "coaster":             "branded.coaster.Coaster",
    "keychain":            "branded.keychain.Keychain",
    "phone_amplifier":     "branded.phone_amplifier.PhoneAmplifier",
    # --- DJ Booth (8) ---
    "booth_corner_bracket": "dj_booth.corner_bracket.BoothCornerBracket",
    "booth_t_joint":       "dj_booth.t_joint.BoothTJoint",
    "booth_facade_tile":   "dj_booth.facade_tile.BoothFacadeTile",
    "booth_logo_panel":    "dj_booth.logo_panel.BoothLogoPanel",
    "booth_cable_clip":    "dj_booth.cable_clip.BoothCableClip",
    "booth_led_holder":    "dj_booth.led_holder.BoothLedHolder",
    "booth_shelf_bracket": "dj_booth.shelf_bracket.BoothShelfBracket",
    "booth_foot":          "dj_booth.foot.BoothFoot",
    "booth_hinge":         "dj_booth.hinge.BoothHinge",
    "booth_quick_pin":     "dj_booth.quick_pin.BoothQuickPin",
    "booth_assembly":      "dj_booth.assembly.BoothAssembly",
    "apex_booth":          "dj_booth.apex_booth.ApexBooth",
    # --- Accordion DJ Booth (11) ---
    "accordion_booth":         "dj_booth.accordion_booth.AccordionBooth",
    "accordion_hinge":         "dj_booth.accordion_hinge.AccordionHinge",
    "accordion_corner":        "dj_booth.accordion_corner.AccordionCorner",
    "accordion_foot":          "dj_booth.accordion_foot.AccordionFoot",
    "accordion_lock":          "dj_booth.accordion_lock.AccordionLock",
    "accordion_leg_bracket":   "dj_booth.accordion_leg.AccordionLegBracket",
    "accordion_cable_port":    "dj_booth.accordion_cable.AccordionCablePort",
    "accordion_facade_clip":   "dj_booth.accordion_facade.AccordionFacadeClip",
    "accordion_logo_plate":    "dj_booth.accordion_logo.AccordionLogoPlate",
    "accordion_shelf_bracket": "dj_booth.accordion_shelf.AccordionShelfBracket",
    "accordion_handle":        "dj_booth.accordion_handle.AccordionHandle",
    "double_pivot_hinge":      "dj_booth.double_pivot_hinge.DoublePivotHinge",
    "folding_corner":          "dj_booth.folding_corner.FoldingCorner",
    "modular_tile_clip":       "dj_booth.modular_tile_clip.ModularTileClip",
    "apex_folding_hub":        "dj_booth.apex_folding_hub.ApexFoldingHub",
    "table_support_bracket":   "dj_booth.table_support_bracket.TableSupportBracket",
    "leveling_foot":           "dj_booth.leveling_foot.LevelingFoot",
    "apex_booth_v2":           "dj_booth.apex_booth_v2.ApexBoothV2",
    "folding_leg_pivot":       "dj_booth.folding_leg_pivot.FoldingLegPivot",
    "tray_lock_butterfly":     "dj_booth.tray_lock_butterfly.TrayLockButterfly",
    "flight_case_corner":      "dj_booth.flight_case_corner.FlightCaseCorner",
    "table_lock_gravity":      "dj_booth.table_lock_gravity.TableLockGravity",
    "flyht_master":            "dj_booth.dps_flyht_master.FlyhtMasterBooth",
    "flyht_pro_replica":       "dj_booth.flyht_pro_replica.FlyhtProReplica",
    "thon_z_style":            "dj_booth.thon_z_style.ThonZStyle",
    # --- Accessories (2) ---
    "trumpet_bodypack_mount":  "accessories.trumpet_bodypack_mount.TrumpetBodypackMount",
    "toothbrush_holder":       "accessories.toothbrush_holder.ToothbrushHolder",
}


def _json_out(data: dict) -> None:
    """Ecrit un dict JSON sur stdout et quitte."""
    print(json.dumps(data, ensure_ascii=False))


def _json_error(message: str, code: int = 1) -> None:
    """Ecrit une erreur JSON sur stdout et quitte avec le code specifie."""
    _json_out({"status": "error", "message": message})
    sys.exit(code)


def load_model_class(model_name: str):
    """
    Charge dynamiquement la classe d'un modele depuis le registre.

    Exemple : "tablet_stand" -> models.dj_equipment.tablet_stand.TabletStand
    Retourne la classe (non instanciee).
    """
    if model_name not in MODEL_REGISTRY:
        _json_error(f"Modele inconnu: '{model_name}'. Utilise --list pour voir les modeles disponibles.")

    dotted_path = MODEL_REGISTRY[model_name]
    # Separer "dj_equipment.tablet_stand.TabletStand" en module_path + class_name
    parts = dotted_path.rsplit(".", 1)
    module_path = f"models.{parts[0]}"
    class_name = parts[1]

    try:
        module = importlib.import_module(module_path)
    except ModuleNotFoundError as exc:
        _json_error(
            f"Module introuvable pour '{model_name}': {module_path} ({exc}). "
            f"Verifie que le fichier models/{parts[0].replace('.', '/')}.py existe."
        )

    cls = getattr(module, class_name, None)
    if cls is None:
        _json_error(
            f"Classe '{class_name}' introuvable dans {module_path}. "
            f"Verifie que la classe est bien definie dans le module."
        )

    return cls


def list_models() -> None:
    """Affiche la liste des modeles disponibles au format JSON."""
    categories: dict[str, list[str]] = {}
    for name, path in MODEL_REGISTRY.items():
        category = path.split(".")[0]
        categories.setdefault(category, []).append(name)

    _json_out({
        "status": "ok",
        "models": categories,
        "total": len(MODEL_REGISTRY),
    })


def parse_extra_params(extra_args: list[str]) -> dict:
    """
    Parse les arguments supplementaires de type --key=value ou --key value.
    Tente de convertir les valeurs en int, float ou bool quand c'est possible.
    """
    params = {}
    i = 0
    while i < len(extra_args):
        arg = extra_args[i]
        if not arg.startswith("--"):
            i += 1
            continue

        if "=" in arg:
            key, val = arg[2:].split("=", 1)
        elif i + 1 < len(extra_args) and not extra_args[i + 1].startswith("--"):
            key = arg[2:]
            val = extra_args[i + 1]
            i += 1
        else:
            # Flag booleen sans valeur
            key = arg[2:]
            val = "true"

        # Conversion automatique du type
        params[key] = _coerce_value(val)
        i += 1

    return params


def _coerce_value(val: str):
    """Convertit une chaine en int, float, bool ou la laisse en string."""
    # Booleens
    if val.lower() in ("true", "yes", "1"):
        return True
    if val.lower() in ("false", "no", "0"):
        return False
    # Entier
    try:
        return int(val)
    except ValueError:
        pass
    # Flottant
    try:
        return float(val)
    except ValueError:
        pass
    # Chaine
    return val


def build_parser() -> argparse.ArgumentParser:
    """Construit le parser d'arguments CLI."""
    parser = argparse.ArgumentParser(
        prog="generate",
        description="DPS 3D System - Generation de modeles parametriques individuels",
    )
    parser.add_argument(
        "model",
        nargs="?",
        help="Nom du modele a generer (ex: tablet_stand, cable_clip)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Lister tous les modeles disponibles",
    )
    parser.add_argument(
        "--stl",
        action="store_true",
        default=True,
        help="Rendu STL via OpenSCAD (par defaut)",
    )
    parser.add_argument(
        "--scad-only",
        action="store_true",
        default=False,
        help="Generer uniquement le fichier SCAD (pas de rendu STL)",
    )
    parser.add_argument(
        "--params-json",
        type=str,
        default=None,
        help='Parametres en JSON (ex: \'{"width": 250, "depth": 150}\')',
    )
    parser.add_argument(
        "--multi-part",
        type=str,
        default=None,
        help='Export multi-part: liste de export_part separes par virgule (ex: "facade_body,facade_logo")',
    )
    return parser


def main() -> None:
    """Point d'entree principal."""
    parser = build_parser()
    args, extra = parser.parse_known_args()

    # --list : afficher les modeles et quitter
    if args.list:
        list_models()
        return

    # Verifier qu'un nom de modele a ete fourni
    if not args.model:
        _json_error("Nom de modele requis. Utilise --list pour voir les modeles disponibles.")

    # Collecter les parametres
    params: dict = {}

    # 1. Parametres depuis --params-json
    if args.params_json:
        try:
            json_params = json.loads(args.params_json)
            if not isinstance(json_params, dict):
                _json_error("--params-json doit etre un objet JSON (dict).")
            params.update(json_params)
        except json.JSONDecodeError as exc:
            _json_error(f"JSON invalide dans --params-json: {exc}")

    # 2. Parametres depuis --key=value (ecrasent le JSON si conflit)
    extra_params = parse_extra_params(extra)
    params.update(extra_params)

    # Charger la classe du modele
    model_cls = load_model_class(args.model)

    # Instancier avec les parametres
    try:
        # Eviter le conflit si 'name' est present dans les params
        params.pop('name', None)
        model = model_cls(**params)
    except (ValueError, TypeError) as exc:
        _json_error(f"Erreur d'instanciation du modele '{args.model}': {exc}")

    # Validation CityFab1 (avertissements non-bloquants)
    cityfab_warnings = []
    try:
        from models.brand import validate_for_cityfab
        cityfab_warnings = validate_for_cityfab(args.model, model.params)
    except ImportError:
        pass

    # Generer le fichier
    try:
        # --- Mode multi-part : genere N STLs pour impression multi-couleur ---
        if args.multi_part:
            part_names = [p.strip() for p in args.multi_part.split(',')]
            parts_result = []
            for part_name in part_names:
                part_params = dict(params)
                part_params['export_part'] = part_name
                part_model = model_cls(**{k: v for k, v in part_params.items() if k != 'name'})
                part_path = part_model.render_stl()
                # Renommer le STL avec le suffixe de la part
                part_stl = part_path.replace('.stl', f'_{part_name}.stl')
                import shutil
                shutil.move(part_path, part_stl)
                parts_result.append({
                    "name": part_name,
                    "stl_url": f"/output/stl/{args.model}_{part_name}.stl",
                    "path": os.path.abspath(part_stl),
                })
            result = {
                "status": "ok",
                "type": "multi_part",
                "model": args.model,
                "parts": parts_result,
                "params": model.params,
            }
            if cityfab_warnings:
                result["cityfab_warnings"] = cityfab_warnings
            _json_out(result)
        elif args.scad_only:
            path = model.save_scad()
            result = {
                "status": "ok",
                "type": "scad",
                "model": args.model,
                "path": os.path.abspath(path),
                "params": model.params,
            }
            if cityfab_warnings:
                result["cityfab_warnings"] = cityfab_warnings
            _json_out(result)
        else:
            path = model.render_stl()
            result = {
                "status": "ok",
                "type": "stl",
                "model": args.model,
                "path": os.path.abspath(path),
                "params": model.params,
            }
            if cityfab_warnings:
                result["cityfab_warnings"] = cityfab_warnings
            _json_out(result)
    except FileNotFoundError:
        _json_error(
            "OpenSCAD introuvable. Installe-le ou utilise --scad-only. "
            "Attendu dans ~/bin/openscad ou dans le PATH."
        )
    except RuntimeError as exc:
        _json_error(f"Erreur de rendu OpenSCAD: {exc}")
    except Exception as exc:
        _json_error(f"Erreur inattendue: {exc}")


if __name__ == "__main__":
    main()
