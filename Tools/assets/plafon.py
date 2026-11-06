"""Plafón de techo con tubos fluorescentes y rejilla de alambre, como el de la referencia del salón.

0,62 x 0,42 m y 0,10 m de alto. El origen está ARRIBA, en el centro (se pega al techo), y cuelga hacia
abajo. Dos objetos: "Plafon" (chapa y rejilla, textura horneada Texturas/Plafon.jpg) y "Tubos"
(material Plafon_Tubo aparte, para hacerlo emisivo en Unity y apagarlo o hacerlo parpadear).

Uso:  python Tools/assets/plafon.py
"""
import math
import os
import sys

import bpy
import bmesh
from mathutils import Matrix

sys.path.insert(0, os.path.dirname(__file__))
import comun as c  # noqa: E402
import hornear  # noqa: E402

CHAPA, ALAMBRE, BLANCO = range(3)
W, D, H = 0.62, 0.42, 0.10


def barra(bm, a, b, r, mat, lados=6):
    """Cilindro fino de a a b (alambre)."""
    import mathutils
    a, b = mathutils.Vector(a), mathutils.Vector(b)
    c.marcar(bm)
    bmesh.ops.create_cone(bm, cap_ends=True, segments=lados, radius1=r, radius2=r, depth=(b - a).length)
    nv = c.nuevos(bm)
    rot = (b - a).to_track_quat("Z", "Y").to_matrix()
    bmesh.ops.transform(bm, matrix=rot.to_4x4(), verts=nv)
    bmesh.ops.translate(bm, verts=nv, vec=(a + b) / 2)
    c.asignar(bm, {f for v in nv for f in v.link_faces}, mat)


def plafon(bm):
    cm = c.caja_mat
    # Bandeja de chapa: fondo y cuatro bordes
    cm(bm, (0, 0, -0.01), (W, D, 0.02), CHAPA, 0.004)
    for s in (-1, 1):
        cm(bm, (s * (W / 2 - 0.006), 0, -0.035), (0.012, D, 0.05), CHAPA, 0.002)
        cm(bm, (0, s * (D / 2 - 0.006), -0.035), (W, 0.012, 0.05), CHAPA, 0.002)
    # Reflector blanco y portalámparas
    cm(bm, (0, 0, -0.022), (W - 0.03, D - 0.03, 0.004), BLANCO, 0)
    for i in range(3):
        y = (i - 1) * 0.12
        for s in (-1, 1):
            cm(bm, (s * (W / 2 - 0.035), y, -0.045), (0.03, 0.035, 0.03), BLANCO, 0.003)
    # Rejilla de alambre: marco y barras en cuadrícula, abombada hacia abajo
    zr = -H + 0.004
    for s in (-1, 1):
        barra(bm, (-W / 2 + 0.01, s * (D / 2 - 0.01), zr), (W / 2 - 0.01, s * (D / 2 - 0.01), zr), 0.003, ALAMBRE)
        barra(bm, (s * (W / 2 - 0.01), -D / 2 + 0.01, zr), (s * (W / 2 - 0.01), D / 2 - 0.01, zr), 0.003, ALAMBRE)
    for i in range(1, 6):
        x = -W / 2 + i * W / 6
        barra(bm, (x, -D / 2 + 0.01, zr), (x, D / 2 - 0.01, zr), 0.0022, ALAMBRE)
    for j in range(1, 4):
        y = -D / 2 + j * D / 4
        barra(bm, (-W / 2 + 0.01, y, zr - 0.003), (W / 2 - 0.01, y, zr - 0.003), 0.0022, ALAMBRE)
    # Patillas de la rejilla al borde
    for sx in (-1, 1):
        for sy in (-1, 1):
            barra(bm, (sx * (W / 2 - 0.01), sy * (D / 2 - 0.01), zr), (sx * (W / 2 - 0.01), sy * (D / 2 - 0.01), -0.06),
                  0.003, ALAMBRE)


def tubos(mat):
    bm = bmesh.new()
    for i in range(3):
        y = (i - 1) * 0.12
        c.marcar(bm)
        bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=0.013, radius2=0.013, depth=W - 0.10)
        nv = c.nuevos(bm)
        bmesh.ops.rotate(bm, verts=nv, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, "Y"))
        bmesh.ops.translate(bm, verts=nv, vec=(0, y, -0.05))
    for f in bm.faces:
        f.material_index = 0
    return c.objeto("Tubos", bm, [mat], suave=True)


def main():
    c.escena_vacia()
    hs = hornear.material_sucio
    mats = [
        hs("Chapa", (0.30, 0.29, 0.26), rugosidad=0.5, suciedad=1.0, polvo=0.0, manchas=0.5, mugre=0.8,
           color_sucio=(0.08, 0.07, 0.05), desgaste=0.3, color_desgaste=(0.35, 0.30, 0.22)),
        hs("Alambre", (0.42, 0.41, 0.38), rugosidad=0.4, metal=1.0, suciedad=0.8, manchas=0.4, polvo=0.0),
        hs("Blanco", (0.55, 0.52, 0.44), rugosidad=0.6, suciedad=0.9, manchas=0.6, polvo=0.0,
           color_sucio=(0.20, 0.16, 0.09), escala_manchas=8),
    ]
    bm = bmesh.new()
    plafon(bm)
    ob = c.objeto("Plafon", bm, mats)
    hornear.atlas(ob, "Plafon", tam=1024, margen=0.002)
    tub = tubos(hornear.material_liso("Plafon_Tubo", (0.85, 0.82, 0.62), rugosidad=0.3))
    ruta = c.exportar_fbx("Plafon", [ob, tub])
    tris = sum(len(p.vertices) - 2 for o in (ob, tub) for p in o.data.polygons)
    print(f"Exportado {ruta} ({tris} triángulos)")


if __name__ == "__main__":
    main()
