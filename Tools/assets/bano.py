"""Baño viejo: váter con asiento de madera, lavabo de pie y bañera. Loza amarillenta y sucia.

Sustituyen a las mallas provisionales Vater, Lavabo y Banera de HouseBuilder con la misma huella
y orientación: frente a +Z en Unity (aquí, en Blender, a -Y), origen en el suelo en el centro.
- Vater: cisterna detrás (+Y de Blender), tapa levantada. 0,44 x 0,64 m, cisterna hasta 0,83 m.
- Lavabo: 0,60 x 0,46 m, borde a 0,80 m. El caño del grifo (el que gotea) acaba en local de Unity
  (0, 0,945, -0,055), como en la provisional.
- Banera: 0,76 x 1,70 m (larga en Z de Unity), borde a 0,52 m, grifo en el extremo +Z de Unity.

Uso:  python Tools/assets/bano.py [Vater|Lavabo|Banera]
Texturas CC0: Mueble_Wood092, Oxido_Rust004, Suciedad_SurfaceImperfections015.
"""
import math
import os
import sys

import bpy
import bmesh
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(__file__))
import comun as c  # noqa: E402
import hornear  # noqa: E402

LOZA, MADERA, METAL, OXIDO, AGUA = range(5)


def materiales():
    hs = hornear.material_sucio
    return [
        hs("Loza", (0.50, 0.46, 0.36), rugosidad=0.3, suciedad=1.0, polvo=0.4, manchas=0.5, escala_manchas=5,
           mugre=0.9, mugre_escala=0.4, color_sucio=(0.20, 0.15, 0.08), chorretones=0.45, semilla=1.0),
        hornear.madera_vieja("Madera", "marron", escala=0.4, veta=1.0, rugosidad=0.4, desgaste=0.6),
        hs("Metal", (0.40, 0.39, 0.36), rugosidad=0.3, metal=1.0, suciedad=0.9, manchas=0.5, mugre=0.6,
           color_sucio=(0.15, 0.11, 0.06)),
        hs("Oxido", (0.8, 0.8, 0.8), rugosidad=0.8, imagen=c.cc0("Oxido_Rust004"), escala=0.4, suciedad=0.6,
           color_sucio=(0.06, 0.04, 0.02)),
        hs("Agua", (0.10, 0.09, 0.06), rugosidad=0.1, suciedad=0.3, manchas=0.6, color_sucio=(0.05, 0.04, 0.02)),
    ]


def torno_mat(bm, perfil, mat, lados=12, desde=(0, 0, 0), esc=(1, 1, 1)):
    c.marcar(bm)
    c.torno(bm, perfil, lados=lados)
    nv = c.nuevos(bm)
    bmesh.ops.scale(bm, vec=esc, verts=nv)
    bmesh.ops.translate(bm, vec=desde, verts=nv)
    c.asignar(bm, {f for v in nv for f in v.link_faces}, mat)
    return nv


def barra(bm, a, b, r, mat, lados=8):
    a, b = Vector(a), Vector(b)
    c.marcar(bm)
    bmesh.ops.create_cone(bm, cap_ends=True, segments=lados, radius1=r, radius2=r, depth=(b - a).length)
    nv = c.nuevos(bm)
    bmesh.ops.transform(bm, matrix=(b - a).to_track_quat("Z", "Y").to_matrix().to_4x4(), verts=nv)
    bmesh.ops.translate(bm, verts=nv, vec=(a + b) / 2)
    c.asignar(bm, {f for v in nv for f in v.link_faces}, mat)


def disco(bm, centro, r, alto, mat, lados=12, esc=(1, 1, 1), rot=None):
    c.marcar(bm)
    bmesh.ops.create_cone(bm, cap_ends=True, segments=lados, radius1=r, radius2=r, depth=alto)
    nv = c.nuevos(bm)
    bmesh.ops.scale(bm, vec=esc, verts=nv)
    if rot is not None:
        bmesh.ops.transform(bm, matrix=rot.to_4x4(), verts=nv)
    bmesh.ops.translate(bm, verts=nv, vec=centro)
    c.asignar(bm, {f for v in nv for f in v.link_faces}, mat)


def vater():
    bm = bmesh.new()
    oval = (1.0, 1.22, 1.0)
    # Pie y taza en una pieza: por fuera se estrecha y se abre; por dentro baja hasta el agua
    perfil = [(0.125, 0.0), (0.11, 0.06), (0.10, 0.18), (0.12, 0.27), (0.165, 0.35), (0.18, 0.395),
              (0.15, 0.40), (0.12, 0.34), (0.07, 0.27), (0.04, 0.23), (0.002, 0.23)]
    torno_mat(bm, perfil, LOZA, lados=12, desde=(0, -0.07, 0), esc=oval)
    disco(bm, (0, -0.05, 0.27), 0.085, 0.004, AGUA, esc=(1, 1.15, 1))
    # Asiento de madera (anillo) y tapa levantada contra la cisterna
    torno_mat(bm, [(0.185, 0.0), (0.185, 0.022), (0.115, 0.022), (0.115, 0.0)], MADERA, lados=12,
              desde=(0, -0.07, 0.40), esc=oval)
    disco(bm, (0, 0.0, 0.0), 0.19, 0.02, MADERA, esc=oval)
    tapa = c.nuevos(bm)
    bmesh.ops.translate(bm, verts=tapa, vec=(0, 0.23, 0))           # la bisagra queda en el origen
    bmesh.ops.rotate(bm, verts=tapa, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(88), 3, "X"))
    bmesh.ops.translate(bm, verts=tapa, vec=(0, 0.13, 0.43))
    for s in (-1, 1):
        barra(bm, (s * 0.09, 0.13, 0.425), (s * 0.04, 0.13, 0.425), 0.008, METAL)
    # Cisterna con tapa y pulsador
    c.caja_mat(bm, (0, 0.24, 0.61), (0.42, 0.18, 0.40), LOZA, 0.02)
    c.caja_mat(bm, (0, 0.24, 0.825), (0.44, 0.20, 0.03), LOZA, 0.012)
    disco(bm, (0, 0.24, 0.845), 0.022, 0.012, METAL, lados=8)
    c.caja_mat(bm, (0, 0.17, 0.40), (0.30, 0.10, 0.06), LOZA, 0.01)   # unión taza-cisterna
    # Tubo de desagüe oxidado hacia la pared
    barra(bm, (0, 0.06, 0.16), (0, 0.33, 0.16), 0.045, OXIDO, lados=10)
    disco(bm, (0, 0.33, 0.16), 0.06, 0.02, OXIDO, lados=10, rot=Matrix.Rotation(math.radians(90), 3, "X"))
    return bm


def lavabo():
    bm = bmesh.new()
    # Pie
    torno_mat(bm, [(0.10, 0.0), (0.085, 0.05), (0.075, 0.40), (0.085, 0.62), (0.11, 0.68)], LOZA, lados=10,
              desde=(0, 0.06, 0))
    # Pila: óvalo con el borde redondeado y la cubeta por dentro
    perfil = [(0.21, 0.66), (0.27, 0.70), (0.30, 0.76), (0.30, 0.80), (0.27, 0.805), (0.22, 0.80),
              (0.17, 0.75), (0.10, 0.715), (0.002, 0.71)]
    torno_mat(bm, perfil, LOZA, lados=14, esc=(1.0, 0.77, 1.0))
    c.caja_mat(bm, (0, 0.17, 0.78), (0.56, 0.12, 0.06), LOZA, 0.012)    # repisa de atrás para los grifos
    disco(bm, (0, -0.01, 0.713), 0.02, 0.004, METAL, lados=8)           # desagüe
    # Grifo: caño (el que gotea) y dos llaves de cruceta
    barra(bm, (0, 0.18, 0.80), (0, 0.18, 0.95), 0.014, METAL)
    barra(bm, (0, 0.185, 0.945), (0, 0.055, 0.945), 0.011, METAL)
    disco(bm, (0, 0.06, 0.935), 0.013, 0.02, METAL, lados=8)
    for s in (-1, 1):
        x = s * 0.13
        barra(bm, (x, 0.18, 0.81), (x, 0.18, 0.86), 0.012, METAL)
        barra(bm, (x - 0.03, 0.18, 0.87), (x + 0.03, 0.18, 0.87), 0.006, METAL, lados=6)
        barra(bm, (x, 0.15, 0.87), (x, 0.21, 0.87), 0.006, METAL, lados=6)
        disco(bm, (x, 0.18, 0.88), 0.008, 0.012, LOZA if s > 0 else OXIDO, lados=6)
    # Sifón oxidado bajo la pila
    barra(bm, (0, -0.01, 0.70), (0, -0.01, 0.55), 0.018, OXIDO)
    barra(bm, (0, -0.01, 0.55), (0, 0.23, 0.55), 0.018, OXIDO)
    return bm


def banera():
    bm = bmesh.new()
    W, L, H, e = 0.76, 1.70, 0.52, 0.07
    cm = c.caja_mat
    # Paredes con el borde redondeado y fondo inclinado hacia el desagüe
    for s in (-1, 1):
        cm(bm, (s * (W / 2 - e / 2), 0, H / 2), (e, L, H), LOZA, 0.02)
        cm(bm, (0, s * (L / 2 - e / 2), H / 2), (W - 2 * e + 0.004, e, H), LOZA, 0.02)
    cm(bm, (0, 0, 0.06), (W - 0.02, L - 0.02, 0.12), LOZA, 0.01)
    cm(bm, (0, 0.03, 0.135), (W - 2 * e, L - 2 * e - 0.06, 0.03), LOZA, 0.015)
    cm(bm, (0, L / 2 - e - 0.12, 0.22), (W - 2 * e, 0.06, 0.16), LOZA, 0.03,
       rot=Matrix.Rotation(math.radians(-35), 3, "X"))                   # respaldo inclinado
    disco(bm, (0, -L / 2 + e + 0.10, 0.152), 0.025, 0.004, METAL, lados=8)
    # Grifo de pared en el extremo (-Y de Blender = +Z de Unity) y cadena del tapón
    yg = -L / 2 + 0.03
    barra(bm, (0, yg, H - 0.01), (0, yg, H + 0.15), 0.014, METAL)
    barra(bm, (0, yg - 0.005, H + 0.14), (0, yg + 0.13, H + 0.14), 0.011, METAL)
    for s in (-1, 1):
        barra(bm, (s * 0.12, yg, H - 0.01), (s * 0.12, yg, H + 0.06), 0.012, METAL)
        barra(bm, (s * 0.12 - 0.03, yg, H + 0.065), (s * 0.12 + 0.03, yg, H + 0.065), 0.006, METAL, lados=6)
    for i in range(6):
        disco(bm, (0.03, -L / 2 + e + 0.10 + i * 0.012, 0.16 + i * 0.03), 0.004, 0.008, METAL, lados=6)
    return bm


PIEZAS = {"Vater": vater, "Lavabo": lavabo, "Banera": banera}


def main(nombre):
    c.escena_vacia()
    mats = materiales()
    bm = PIEZAS[nombre]()
    ob = c.objeto(nombre, bm, mats)
    for p in ob.data.polygons:
        p.use_smooth = p.material_index in (LOZA, METAL, OXIDO) and len(p.vertices) == 4
    hornear.atlas(ob, nombre, tam=1024, margen=0.003)
    ruta = c.exportar_fbx(nombre, [ob])
    print(f"Exportado {ruta} ({sum(len(p.vertices) - 2 for p in ob.data.polygons)} triángulos)")


if __name__ == "__main__":
    for n in (sys.argv[1:] or list(PIEZAS)):
        main(n)
