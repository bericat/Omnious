"""Puertas de interior como la de la referencia del salón: hoja tapizada en skai marrón con capitoné de
botones, tachuelas de latón por el borde y manilla con placa; marco de madera oscura con tapajuntas.

Mantienen las medidas y los pivotes de las provisionales de HouseBuilder (coordenadas de Unity, yaw 0):
  PuertaHoja   origen en el eje de la bisagra, en el suelo. Hoja de 0,86 x 2,0 x 0,04 a lo largo de +Z
               (de z = 0 a z = 0,86), centrada en x = 0. Manillas a los dos lados en z = 0,77, y = 0,95.
  PuertaMarco  origen en el centro del hueco, en el suelo. Hueco de 0,90 x 2,0, muro de 0,19 en X.
               Jambas en z = ±0,46 y dintel a 2,02 como las provisionales, más tapajuntas a las dos caras.

Uso:  python Tools/assets/puertas.py [PuertaHoja|PuertaMarco]
"""
import math
import os
import sys

import bpy  # noqa: F401  (carga bmesh)
import bmesh
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(__file__))
import comun as c  # noqa: E402
import hornear  # noqa: E402

MADERA, SKAI, LATON = range(3)
# En Blender: X = -X de Unity, Y = -Z de Unity, Z = Y de Unity. La hoja va de y = 0 a y = -0.86.
ANCHO, ALTO, GROSOR = 0.86, 2.0, 0.04
MARGEN = 0.045                       # madera vista alrededor del tapizado
COLS, FILAS = 3, 6                   # botones del capitoné


def materiales():
    hs = hornear.material_sucio
    return [
        hornear.madera_vieja("Madera", "oscura", desgaste=0.5, escala=0.8),
        hs("Skai", (0.10, 0.05, 0.025), rugosidad=0.45, suciedad=1.0, polvo=0.3, manchas=0.6, escala_manchas=6,
           mugre=0.9, color_sucio=(0.04, 0.025, 0.012), desgaste=0.35, color_desgaste=(0.22, 0.15, 0.09),
           chorretones=0.3),
        hs("Laton", (0.30, 0.22, 0.08), rugosidad=0.35, metal=1.0, suciedad=1.0, manchas=0.6, polvo=0.2,
           color_sucio=(0.07, 0.05, 0.02)),
    ]


def tachuela(bm, centro, r, normal_x):
    """Cabeza de clavo semiesférica que sale hacia normal_x (+1 o -1)."""
    c.marcar(bm)
    c.torno(bm, [(r, 0.0), (r * 0.7, r * 0.55), (0.0005, r * 0.85)], lados=6)
    nv = c.nuevos(bm)
    bmesh.ops.rotate(bm, verts=nv, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90 * normal_x), 3, "Y"))
    bmesh.ops.translate(bm, verts=nv, vec=centro)
    c.asignar(bm, {f for v in nv for f in v.link_faces}, LATON)


def tapizado(bm, lado):
    """Almohadillado de una cara: rejilla abombada hundida en cada botón, con botones y tachuelas."""
    y0, y1 = -ANCHO + MARGEN, -MARGEN
    z0, z1 = MARGEN, ALTO - MARGEN
    x0 = lado * GROSOR / 2
    nu, nv_ = 18, 42
    botones = [(y0 + (y1 - y0) * (i + 0.5) / COLS, z0 + (z1 - z0) * (j + 0.5) / FILAS)
               for i in range(COLS) for j in range(FILAS)]
    # Botones intercalados (tresbolillo) entre filas para el capitoné
    botones += [(y0 + (y1 - y0) * i / COLS, z0 + (z1 - z0) * j / FILAS)
                for i in range(1, COLS) for j in range(1, FILAS)]
    rejilla = []
    for j in range(nv_ + 1):
        fila = []
        for i in range(nu + 1):
            y = y0 + (y1 - y0) * i / nu
            z = z0 + (z1 - z0) * j / nv_
            borde = min(i, nu - i, j, nv_ - j)
            hinchado = 0.014 * min(1.0, borde / 1.5)
            d = min(math.hypot(y - by, z - bz) for by, bz in botones)
            hinchado -= 0.010 * math.exp(-(d / 0.045) ** 2) * min(1.0, borde / 1.5)
            fila.append(bm.verts.new((x0 + lado * max(hinchado, 0.0005), y, z)))
        rejilla.append(fila)
    caras = []
    for j in range(nv_):
        for i in range(nu):
            q = (rejilla[j][i], rejilla[j][i + 1], rejilla[j + 1][i + 1], rejilla[j + 1][i])
            caras.append(bm.faces.new(q if lado > 0 else q[::-1]))
    c.asignar(bm, caras, SKAI)
    for by, bz in botones:
        d_x = x0 + lado * (0.014 - 0.010 + 0.0005)
        tachuela(bm, (d_x, by, bz), 0.009, lado)
    # Tachuelas de latón todo alrededor del tapizado
    paso = 0.07
    n_y, n_z = round((y1 - y0) / paso), round((z1 - z0) / paso)
    puntos = [(y0 + (y1 - y0) * k / n_y, z) for k in range(n_y + 1) for z in (z0 + 0.012, z1 - 0.012)]
    puntos += [(y, z0 + (z1 - z0) * k / n_z) for k in range(1, n_z) for y in (y0 + 0.012, y1 - 0.012)]
    for py, pz in puntos:
        tachuela(bm, (x0 + lado * 0.002, py, pz), 0.006, lado)


def manilla(bm, lado):
    """Placa con bocallave y manilla de palanca que apunta hacia la bisagra."""
    x = lado * GROSOR / 2
    yc, zc = -0.77, 0.95
    c.caja_mat(bm, (x + lado * 0.014, yc, zc - 0.04), (0.006, 0.05, 0.24), LATON, 0.002)
    c.caja_mat(bm, (x + lado * 0.0175, yc, zc - 0.11), (0.002, 0.008, 0.022), MADERA, 0)    # bocallave
    # Cuello y palanca
    c.marcar(bm)
    bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=0.011, radius2=0.009, depth=0.05)
    nv = c.nuevos(bm)
    bmesh.ops.rotate(bm, verts=nv, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, "Y"))
    bmesh.ops.translate(bm, verts=nv, vec=(x + lado * 0.03, yc, zc))
    c.asignar(bm, {f for v in nv for f in v.link_faces}, LATON)
    c.caja_mat(bm, (x + lado * 0.055, yc + 0.055, zc), (0.016, 0.125, 0.014), LATON, 0.006, segmentos=2)


def hoja():
    bm = bmesh.new()
    c.caja_mat(bm, (0, -ANCHO / 2, ALTO / 2), (GROSOR, ANCHO, ALTO), MADERA, 0.004)
    for lado in (-1, 1):
        tapizado(bm, lado)
        manilla(bm, lado)
    # Pernios de la bisagra en el canto
    for z in (0.22, 1.0, 1.78):
        c.marcar(bm)
        bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=0.009, radius2=0.009, depth=0.11)
        nv = c.nuevos(bm)
        bmesh.ops.translate(bm, verts=nv, vec=(0, 0.004, z))
        c.asignar(bm, {f for v in nv for f in v.link_faces}, LATON)
    return bm


def marco():
    """Jambas, dintel y tapajuntas moldurados a las dos caras del muro (muro de 0,19 en X)."""
    bm = bmesh.new()
    cm = c.caja_mat
    for s in (-1, 1):
        cm(bm, (0, s * 0.46, 0.99), (0.19, 0.07, 1.98), MADERA, 0.004)
    cm(bm, (0, 0, 2.02), (0.19, 1.02, 0.07), MADERA, 0.004)
    # Tapajuntas: 7 cm de ancho, montados sobre la pared, con un junquillo en el canto interior
    for lado in (-1, 1):
        x = lado * (0.095 + 0.008)
        for s in (-1, 1):
            cm(bm, (x, s * (0.45 + 0.035), 1.035), (0.016, 0.07, 2.07), MADERA, 0.005, segmentos=2)
            cm(bm, (x + lado * 0.009, s * (0.45 + 0.012), 1.03), (0.008, 0.016, 2.06), MADERA, 0.003)
        cm(bm, (x, 0, 2.07 - 0.035 + 0.035), (0.016, 0.9 + 0.14, 0.07), MADERA, 0.005, segmentos=2)
        cm(bm, (x + lado * 0.009, 0, 2.012), (0.008, 0.9, 0.016), MADERA, 0.003)
    return bm


def main(nombre):
    c.escena_vacia()
    mats = materiales()
    bm = hoja() if nombre == "PuertaHoja" else marco()
    ob = c.objeto(nombre, bm, mats)
    for p in ob.data.polygons:
        p.use_smooth = p.material_index in (SKAI, LATON) and len(p.vertices) == 4
    hornear.atlas(ob, nombre, tam=2048 if nombre == "PuertaHoja" else 1024, margen=0.002)
    ruta = c.exportar_fbx(nombre, [ob])
    print(f"Exportado {ruta} ({sum(len(p.vertices) - 2 for p in ob.data.polygons)} triángulos)")


if __name__ == "__main__":
    for n in (sys.argv[1:] or ["PuertaHoja", "PuertaMarco"]):
        main(n)
