"""
Utilitaires 3D — DPS 3D System
Fonctions réutilisables pour build123d + viewer + export
"""
from build123d import *
from ocp_vscode import show, Camera
import subprocess
import os


def show_part(*parts, names=None, colors=None, reset=True):
    """Affiche dans le viewer avec Camera.RESET automatique"""
    kwargs = {}
    if names:
        kwargs["names"] = names
    if colors:
        kwargs["colors"] = colors
    if reset:
        kwargs["reset_camera"] = Camera.RESET
    show(*parts, **kwargs)


def export_stl_smart(part, path, quality="print"):
    """Export STL avec tolérance adaptée
    draft=0.1mm | print=0.02mm | hq=0.005mm
    """
    tols = {"draft": (0.1, 1.0), "print": (0.02, 0.3), "hq": (0.005, 0.1)}
    tol, ang = tols.get(quality, tols["print"])
    export_stl(part, path, tolerance=tol, angular_tolerance=ang)
    size = os.path.getsize(path) / 1024 / 1024
    print(f"  Export [{quality}]: {path} ({size:.1f} MB)")


def optimize_svg(input_path, output_path=None):
    """Optimise un SVG avec svgo (-50 à -80% complexité)"""
    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_opt{ext}"
    result = subprocess.run(
        ["svgo", input_path, "-o", output_path,
         "--config", '{"plugins":["removeDimensions","collapseGroups","mergePaths",{"name":"convertPathData","params":{"floatPrecision":1}}]}'],
        capture_output=True, text=True)
    if result.returncode == 0:
        orig, opt = os.path.getsize(input_path), os.path.getsize(output_path)
        print(f"  SVG: {orig/1024:.0f}KB → {opt/1024:.0f}KB (-{(1-opt/orig)*100:.0f}%)")
        return output_path
    print(f"  ⚠️ svgo: {result.stderr.strip()}")
    return input_path


def png_to_svg(png_path, svg_path=None, threshold=80, turdsize=10):
    """PNG (fond transparent) → SVG silhouette via potrace + svgo"""
    from PIL import Image
    if svg_path is None:
        svg_path = png_path.rsplit(".", 1)[0] + ".svg"
    img = Image.open(png_path).convert("RGBA")
    sil = Image.new("L", img.size, 255)
    px, sp = img.load(), sil.load()
    for y in range(img.height):
        for x in range(img.width):
            if px[x, y][3] > threshold:
                sp[x, y] = 0
    bmp = "/tmp/_potrace_input.bmp"
    sil.save(bmp)
    subprocess.run(["potrace", bmp, "-s", "-o", svg_path, "--turdsize", str(turdsize), "--opttolerance", "0.5"], capture_output=True)
    opt = optimize_svg(svg_path)
    if opt != svg_path:
        os.rename(opt, svg_path)
    print(f"  PNG→SVG: {png_path} → {svg_path}")
    return svg_path


def transform_svg_face(face, target_w, target_cx, target_cy, target_z=0, flip_y=False):
    """Scale + position une face SVG importée"""
    from OCP.gp import gp_Trsf, gp_Vec, gp_Pnt, gp_Ax1, gp_Dir
    from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
    bb = face.bounding_box()
    cx, cy = (bb.min.X+bb.max.X)/2, (bb.min.Y+bb.max.Y)/2
    scale = target_w / (bb.max.X - bb.min.X)
    t1 = gp_Trsf(); t1.SetTranslation(gp_Vec(-cx, -cy, 0))
    shape = BRepBuilderAPI_Transform(face.wrapped, t1, True).Shape()
    t2 = gp_Trsf(); t2.SetScale(gp_Pnt(0,0,0), scale)
    shape = BRepBuilderAPI_Transform(shape, t2, True).Shape()
    if flip_y:
        t3 = gp_Trsf(); t3.SetMirror(gp_Ax1(gp_Pnt(0,0,0), gp_Dir(1,0,0)))
        shape = BRepBuilderAPI_Transform(shape, t3, True).Shape()
    t4 = gp_Trsf(); t4.SetTranslation(gp_Vec(target_cx, target_cy, target_z))
    shape = BRepBuilderAPI_Transform(shape, t4, True).Shape()
    return Face(shape)


def check_mesh(stl_path):
    """Vérifie watertight + dimensions avant impression"""
    import trimesh
    m = trimesh.load(stl_path)
    d = m.bounds[1] - m.bounds[0]
    ok = "✅" if m.is_watertight else "❌"
    print(f"  {ok} {os.path.basename(stl_path)}: {d[0]:.1f}x{d[1]:.1f}x{d[2]:.1f}mm, {len(m.faces):,} tri")
    return m.is_watertight
