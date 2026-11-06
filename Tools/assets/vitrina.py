"""Vitrina de salón: mueble alto de madera oscura con dos puertas de cristal cuadriculado, cajón abajo,
cornisa y zócalo moldurados. Dentro, platos de pie, vasos y una caja. Vieja y sucia.

Mueble nuevo (no hay malla provisional): 0,9 x 1,85 x 0,40 m, frente a +Z en Unity, origen en el
suelo en el centro. Dos objetos: "Vitrina" (todo, textura horneada Texturas/Vitrina.jpg) y "Cristal"
(los cristales de las puertas, material Vitrina_Cristal aparte para hacerlo semitransparente en Unity).

Uso:  python Tools/assets/vitrina.py
Texturas CC0: Mueble_Wood092, Suciedad_SurfaceImperfections015.
"""
import os
import sys

import bpy
import bmesh
from mathutils import Matrix

sys.path.insert(0, os.path.dirname(__file__))
import comun as c  # noqa: E402
import hornear  # noqa: E402

MADERA, INTERIOR, METAL, LOZA, VASO, CARTON = range(6)
W, H, D = 0.9, 1.85, 0.40
Z_PUERTA, H_PUERTA = 0.26, 1.42
G = 0.022  # grosor de tablero


def mueble(bm):
    cm = c.caja_mat
    for s in (-1, 1):
        cm(bm, (s * (W / 2 - G / 2), 0, H / 2), (G, D, H), MADERA, 0.003)
    cm(bm, (0, D / 2 - 0.006, H / 2), (W - 2 * G, 0.012, H - 0.1), INTERIOR, 0)       # trasera
    # Cornisa y zócalo
    cm(bm, (0, -0.012, H - 0.012), (W + 0.06, D + 0.035, 0.024), MADERA, 0.004)
    cm(bm, (0, -0.007, H - 0.034), (W + 0.035, D + 0.02, 0.02), MADERA, 0.006)
    cm(bm, (0, -0.003, H - 0.056), (W + 0.012, D + 0.008, 0.024), MADERA, 0.004)
    cm(bm, (0, -0.008, 0.04), (W + 0.04, D + 0.025, 0.08), MADERA, 0.006)
    cm(bm, (0, -0.004, 0.09), (W + 0.018, D + 0.012, 0.02), MADERA, 0.006)
    # Cajón con su tirador
    cm(bm, (0, -D / 2 + 0.01, 0.175), (W - 2 * G - 0.006, 0.02, 0.15), MADERA, 0.004)
    cm(bm, (0, -D / 2 - 0.004, 0.178), (0.16, 0.012, 0.012), METAL, 0.003)
    cm(bm, (0, 0.02, Z_PUERTA - 0.01), (W - 2 * G, D - 0.04, G), INTERIOR, 0.002)  # suelo interior
    zt = (Z_PUERTA + H_PUERTA + H - 0.066) / 2
    cm(bm, (0, -D / 2 + 0.012, zt), (W - 2 * G, 0.024, H - 0.066 - Z_PUERTA - H_PUERTA), MADERA, 0.003)  # travesaño de arriba
    # Baldas por dentro
    for z in (0.62, 1.0, 1.36):
        cm(bm, (0, 0.02, z), (W - 2 * G, D - 0.08, 0.018), INTERIOR, 0.002)
    # Puertas: marco, cuarterones de 2 x 4 y tirador
    ap = (W - 2 * G) / 2
    y = -D / 2 + 0.012
    for s in (-1, 1):
        cx = s * ap / 2
        zc = Z_PUERTA + H_PUERTA / 2
        for dx in (-1, 1):
            cm(bm, (cx + dx * (ap / 2 - 0.028), y, zc), (0.055, 0.024, H_PUERTA), MADERA, 0.004)
        for dz in (-1, 1):
            cm(bm, (cx, y, zc + dz * (H_PUERTA / 2 - 0.035)), (ap - 0.11, 0.024, 0.07), MADERA, 0.004)
        cm(bm, (cx, y - 0.002, zc), (0.016, 0.016, H_PUERTA - 0.14), MADERA, 0.002)
        for k in (1, 2, 3):
            cm(bm, (cx, y - 0.002, Z_PUERTA + 0.07 + k * (H_PUERTA - 0.14) / 4), (ap - 0.11, 0.016, 0.016),
               MADERA, 0.002)
        cm(bm, (-s * 0.035, y - 0.022, zc), (0.012, 0.012, 0.12), METAL, 0.003)
        for dz in (-0.055, 0.055):
            cm(bm, (-s * 0.035, y - 0.016, zc + dz), (0.012, 0.016, 0.012), METAL, 0.002)
    # Contenido: platos de pie, vasos y una caja
    for i in range(4):
        c.marcar(bm)
        bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=0.11, radius2=0.11, depth=0.012)
        nv = c.nuevos(bm)
        bmesh.ops.rotate(bm, verts=nv, cent=(0, 0, 0), matrix=Matrix.Rotation(1.45, 3, "X"))
        bmesh.ops.translate(bm, verts=nv, vec=(-0.25 + i * 0.03, 0.12, 0.629 + 0.115))
        c.asignar(bm, {f for v in nv for f in v.link_faces}, LOZA)
    for i in range(5):
        c.marcar(bm)
        c.torno(bm, [(0.028, 0), (0.035, 0.11), (0.032, 0.11), (0.025, 0.006), (0.002, 0.006)], lados=10,
                desde=(0.06 + i * 0.075, -0.02, 1.009))
        c.asignar(bm, {f for v in c.nuevos(bm) for f in v.link_faces}, VASO)
    cm(bm, (0.18, 0.04, 0.629 + 0.09), (0.26, 0.22, 0.18), CARTON, 0.004)
    for i in range(3):
        cm(bm, (-0.20 + i * 0.02, 0.10, 1.369 + 0.012 + i * 0.024), (0.28, 0.20, 0.024), LOZA, 0.004)


def cristales(mat):
    bm = bmesh.new()
    ap = (W - 2 * G) / 2
    for s in (-1, 1):
        c.caja(bm, (s * ap / 2, -D / 2 + 0.012, Z_PUERTA + H_PUERTA / 2), (ap - 0.08, 0.004, H_PUERTA - 0.10))
    for f in bm.faces:
        f.material_index = 0
    return c.objeto("Cristal", bm, [mat])


def main():
    c.escena_vacia()
    hs = hornear.material_sucio
    mats = [
        hornear.madera_vieja("Madera", "oscura", desgaste=0.6, escala=0.8),
        hornear.madera_vieja("Interior", (0.15, 0.12, 0.09), polvo=0.0, suciedad=1.3, semilla=5.0),
        hs("Metal", (0.40, 0.38, 0.34), rugosidad=0.35, metal=1.0, suciedad=0.8, manchas=0.4),
        hs("Loza", (0.62, 0.60, 0.54), rugosidad=0.25, suciedad=1.0, manchas=0.3),
        hs("Vaso", (0.35, 0.38, 0.36), rugosidad=0.15, suciedad=0.8),
        hs("Carton", (0.40, 0.31, 0.20), rugosidad=0.9, suciedad=0.8, manchas=0.5, escala_manchas=10),
    ]
    bm = bmesh.new()
    mueble(bm)
    ob = c.objeto("Vitrina", bm, mats)
    hornear.atlas(ob, "Vitrina", tam=2048, margen=0.002)
    vid = cristales(hornear.material_liso("Vitrina_Cristal", (0.10, 0.12, 0.10), rugosidad=0.1, alfa=0.35))
    ruta = c.exportar_fbx("Vitrina", [ob, vid])
    tris = sum(len(p.vertices) - 2 for o in (ob, vid) for p in o.data.polygons)
    print(f"Exportado {ruta} ({tris} triángulos)")


if __name__ == "__main__":
    main()
