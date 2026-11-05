"""Sofá del salón: estructura de madera con cojines de tela de cuadros, viejo y usado.

Sustituye a la malla provisional Sofa de SalonBuilder/HouseBuilder y mantiene su huella:
2,0 x 0,86 m, respaldo hasta 0,94 m, frente hacia +Z en Unity, origen en el suelo en el centro.

Uso:  python Tools/assets/sofa.py
Salida: Assets/_Ominous/Art/Models/Sofa.fbx y Texturas/Sofa.jpg (atlas horneado).
Texturas CC0 que usa: Tapiceria_Fabric080, Mueble_Wood092 y Suciedad_SurfaceImperfections015.
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

ANCHO, FONDO = 2.0, 0.86
MADERA, TELA, PATA = range(3)


def caja(bm, centro, tam, mat, biselado=0.006, segmentos=2, rot=None):
    c.marcar(bm)
    vs = c.caja(bm, (0, 0, 0), tam)
    if biselado:
        aristas = list({e for v in vs for e in v.link_edges})
        bmesh.ops.bevel(bm, geom=aristas, offset=biselado, segments=segmentos, profile=0.5,
                        affect="EDGES", clamp_overlap=True)
    nuevos = c.nuevos(bm)
    if rot is not None:
        bmesh.ops.transform(bm, matrix=rot.to_4x4(), verts=nuevos)
    bmesh.ops.translate(bm, vec=centro, verts=nuevos)
    c.asignar(bm, {f for v in nuevos for f in v.link_faces}, mat)
    return nuevos


def cojin(bm, centro, tam, mat, abombado=0.10, rot=None, semilla=0):
    """Cojín: caja con las esquinas redondeadas, las caras grandes abombadas y algo hundido por el uso."""
    c.marcar(bm)
    r = bmesh.ops.create_cube(bm, size=2.0)
    bmesh.ops.subdivide_edges(bm, edges=list({e for v in r["verts"] for e in v.link_edges}), cuts=7, use_grid_fill=True)
    nuevos = c.nuevos(bm)
    hx, hy, hz = tam[0] / 2, tam[1] / 2, tam[2] / 2
    # eje más fino = dirección del abombado
    fino = min(range(3), key=lambda i: tam[i])
    for v in nuevos:
        p = Vector(v.co)
        # caja redondeada: superelipsoide
        n = 7.0
        norma = (abs(p.x) ** n + abs(p.y) ** n + abs(p.z) ** n) ** (1 / n)
        q = p / max(norma, 1e-6) * max(abs(p.x), abs(p.y), abs(p.z))
        otros = [i for i in range(3) if i != fino]
        hinchado = (1 - q[otros[0]] ** 2) * (1 - q[otros[1]] ** 2)
        q[fino] *= 1 + abombado * hinchado / max(1e-3, tam[fino]) * 0.5
        # hundido en el centro de la cara de arriba / delantera por el uso
        v.co = Vector((q.x * hx, q.y * hy, q.z * hz))
    if rot is not None:
        bmesh.ops.transform(bm, matrix=rot.to_4x4(), verts=nuevos)
    bmesh.ops.translate(bm, vec=centro, verts=nuevos)
    c.asignar(bm, {f for v in nuevos for f in v.link_faces}, mat)
    return nuevos


def sofa(mats):
    bm = bmesh.new()
    hx, hy = ANCHO / 2, FONDO / 2
    # Patas y bastidor
    for x in (-hx + 0.05, hx - 0.05):
        for y in (-hy + 0.05, hy - 0.05):
            caja(bm, (x, y, 0.07), (0.06, 0.06, 0.14), PATA, biselado=0.008)
    caja(bm, (0, -hy + 0.04, 0.22), (ANCHO - 0.12, 0.05, 0.16), MADERA)
    caja(bm, (0, hy - 0.04, 0.22), (ANCHO - 0.12, 0.05, 0.16), MADERA)
    caja(bm, (0, 0, 0.27), (ANCHO - 0.14, FONDO - 0.08, 0.03), MADERA)  # tablero del asiento
    # Brazos: tabla lateral, postes y reposabrazos con el frente redondeado
    for s in (-1, 1):
        x = s * (hx - 0.035)
        caja(bm, (x, 0.02, 0.38), (0.05, FONDO - 0.10, 0.36), MADERA)
        for y in (-hy + 0.04, hy - 0.04):
            caja(bm, (x, y, 0.37), (0.07, 0.07, 0.52), MADERA, biselado=0.01)
        caja(bm, (x, 0.0, 0.645), (0.11, FONDO + 0.02, 0.035), MADERA, biselado=0.012, segmentos=3)
    # Respaldo de madera
    inclin = Matrix.Rotation(math.radians(-9), 3, "X")
    caja(bm, (0, hy - 0.03, 0.58), (ANCHO - 0.10, 0.04, 0.66), MADERA, rot=inclin)
    caja(bm, (0, hy - 0.02, 0.925), (ANCHO - 0.06, 0.06, 0.035), MADERA, biselado=0.01, segmentos=3, rot=inclin)
    # Cojines: tres de asiento y tres de respaldo
    a = (ANCHO - 0.14) / 3 - 0.01
    for i in (-1, 0, 1):
        cojin(bm, (i * (a + 0.01), -0.04, 0.37), (a, FONDO - 0.14, 0.17), TELA, abombado=0.03)
        cojin(bm, (i * (a + 0.01), 0.27, 0.66), (a, 0.17, 0.48), TELA, abombado=0.03,
              rot=Matrix.Rotation(math.radians(-12), 3, "X"))
    ob = c.objeto("Sofa", bm, mats)
    for p in ob.data.polygons:
        p.use_smooth = p.material_index == TELA
    return ob


def main():
    c.escena_vacia()
    hs = hornear.material_sucio
    mats = [
        hs("Madera", (0.36, 0.25, 0.16), rugosidad=0.55, imagen=c.cc0("Mueble_Wood092"), escala=1.2,
           suciedad=0.8, polvo=0.3, manchas=0.15, desgaste=0.5, color_desgaste=(0.45, 0.33, 0.20),
           color_sucio=(0.10, 0.07, 0.04), mugre=0.4),
        hs("Tela", (0.62, 0.42, 0.36), rugosidad=0.95, imagen=c.cc0("Tapiceria_Fabric080"), escala=0.6,
           suciedad=1.2, polvo=0.3, manchas=0.5, color_sucio=(0.18, 0.12, 0.08), mugre=0.6, escala_manchas=4),
        hs("Pata", (0.22, 0.15, 0.10), rugosidad=0.6, imagen=c.cc0("Mueble_Wood092"), escala=1.2,
           suciedad=0.6, polvo=0.4, manchas=0.2, color_sucio=(0.08, 0.06, 0.04)),
    ]
    ob = sofa(mats)
    hornear.atlas(ob, "Sofa", tam=2048)
    ruta = c.exportar_fbx("Sofa", [ob])
    tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
    print(f"Exportado {ruta} ({tris} triángulos)")


if __name__ == "__main__":
    main()
