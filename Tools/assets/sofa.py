"""Sofá del salón: tapizado entero, brazos enrollados y tela de espiga marrón oliva, viejo y hundido.

Sustituye a la malla provisional Sofa de SalonBuilder/HouseBuilder y mantiene su huella:
2,0 x 0,86 m, respaldo hasta 0,94 m, frente hacia +Z en Unity, origen en el suelo en el centro.

Uso:  python Tools/assets/sofa.py
Salida: Assets/_Ominous/Art/Models/Sofa.fbx y Texturas/Sofa.jpg (atlas horneado).
Tela de espiga generada aquí; CC0: Tapiceria_Fabric083, Mueble_Wood092 y Suciedad_SurfaceImperfections015.
"""
import math
import os
import sys

import bpy
import numpy as np
import bmesh
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(__file__))
import comun as c  # noqa: E402
import hornear  # noqa: E402

ANCHO, FONDO = 2.0, 0.86
TELA, PATA, COJIN = range(3)


def caja(bm, centro, tam, mat, biselado=0.006, segmentos=1, rot=None):
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


def cojin(bm, centro, tam, mat, abombado=0.10, rot=None, semilla=0, n=7.0, hundido=0.0):
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
        norma = (abs(p.x) ** n + abs(p.y) ** n + abs(p.z) ** n) ** (1 / n)
        q = p / max(norma, 1e-6) * max(abs(p.x), abs(p.y), abs(p.z))
        otros = [i for i in range(3) if i != fino]
        hinchado = (1 - q[otros[0]] ** 2) * (1 - q[otros[1]] ** 2)
        q[fino] *= 1 + abombado * hinchado / max(1e-3, tam[fino]) * 0.5
        # hundido en el centro de la cara de arriba por el uso
        if hundido and q.z > 0:
            q.z -= hundido / max(hz, 1e-3) * (1 - q.x ** 2) * (1 - q.y ** 2) * q.z
        v.co = Vector((q.x * hx, q.y * hy, q.z * hz))
    if rot is not None:
        bmesh.ops.transform(bm, matrix=rot.to_4x4(), verts=nuevos)
    bmesh.ops.translate(bm, vec=centro, verts=nuevos)
    c.asignar(bm, {f for v in nuevos for f in v.link_faces}, mat)
    return nuevos


def tela_espiga():
    """Tela de espiga (zigzag) en gris: el tono lo pone el material. Cubre 0,4 m."""
    t = 512
    yy, xx = np.mgrid[0:t, 0:t].astype(float)
    p = t / 16
    zig = (yy + np.abs((xx % (2 * p)) - p)) % p / p
    rayas = np.where(zig < 0.5, 1.0, 0.72)
    trama = ((xx.astype(int) // 2 + yy.astype(int) // 2) % 2) * 0.06
    rng = np.random.default_rng(3)
    v = rayas * (0.9 + trama) * (0.92 + c.fbm(t, t, rng, (64, 16, 4)) * 0.16)
    img = c.guardar_png("_Espiga", np.repeat(v[..., None], 3, axis=2))
    img.pack(); os.remove(img.filepath_raw)
    return img


def sofa(mats):
    bm = bmesh.new()
    hx, hy = ANCHO / 2, FONDO / 2
    BRAZO = 0.20
    # Patas cortas de madera
    for x in (-hx + 0.08, hx - 0.08):
        for y in (-hy + 0.08, hy - 0.08):
            caja(bm, (x, y, 0.03), (0.06, 0.06, 0.06), PATA, biselado=0.006)
    # Bastidor tapizado: base, respaldo y brazos con el rulo de arriba
    cojin(bm, (0, 0.01, 0.23), (ANCHO - 0.06, FONDO - 0.06, 0.34), TELA, abombado=0.01, n=6)
    cojin(bm, (0, hy - 0.11, 0.64), (ANCHO - 0.10, 0.20, 0.58), TELA, abombado=0.02, n=4,
          rot=Matrix.Rotation(math.radians(-6), 3, "X"))
    for s in (-1, 1):
        x = s * (hx - BRAZO / 2 + 0.01)
        cojin(bm, (x, 0.0, 0.33), (BRAZO - 0.02, FONDO - 0.02, 0.52), TELA, abombado=0.02, n=6)
        cojin(bm, (x + s * 0.02, -0.01, 0.585), (BRAZO + 0.04, FONDO, 0.15), TELA, abombado=0.0, n=2.6)
    # Cojines: tres de asiento (hundidos por el uso) y tres de respaldo
    dentro = ANCHO - 2 * BRAZO
    a = dentro / 3 - 0.006
    for i in (-1, 0, 1):
        x = i * (a + 0.006)
        cojin(bm, (x, -0.07, 0.465), (a, FONDO - 0.26, 0.15), TELA, abombado=0.03, n=5,
              hundido=0.012 + 0.008 * (i == 1))
        cojin(bm, (x, 0.20, 0.68), (a, 0.18, 0.44), TELA, abombado=0.05, n=4,
              rot=Matrix.Rotation(math.radians(-14), 3, "X"))
    # Un cojín suelto de otra tela, caído contra el brazo
    cojin(bm, (hx - BRAZO - 0.17, 0.05, 0.66), (0.40, 0.13, 0.38), COJIN, abombado=0.10, n=3,
          rot=Matrix.Rotation(math.radians(-25), 3, "X") @ Matrix.Rotation(math.radians(15), 3, "Y")
          @ Matrix.Rotation(math.radians(20), 3, "Z"))
    ob = c.objeto("Sofa", bm, mats)
    for p in ob.data.polygons:
        p.use_smooth = p.material_index != PATA
    return ob


def main():
    c.escena_vacia()
    hs = hornear.material_sucio
    mats = [
        hs("Tela", (0.16, 0.13, 0.08), rugosidad=0.95, imagen=tela_espiga(), escala=0.4, veta=0.9,
           suciedad=0.6, polvo=0.3, manchas=0.5, color_sucio=(0.06, 0.05, 0.03), mugre=0.8, escala_manchas=4,
           desgaste=0.3, color_desgaste=(0.24, 0.21, 0.15)),
        hornear.madera_vieja("Pata", "oscura", polvo=0.8),
        hs("Cojin", (0.22, 0.16, 0.08), rugosidad=0.95, imagen=c.cc0("Tapiceria_Fabric083"), escala=0.3, veta=1.0,
           suciedad=0.6, manchas=0.5, color_sucio=(0.07, 0.05, 0.03), mugre=0.6),
    ]
    ob = sofa(mats)
    hornear.atlas(ob, "Sofa", tam=2048)
    ruta = c.exportar_fbx("Sofa", [ob])
    tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
    print(f"Exportado {ruta} ({tris} triángulos)")


if __name__ == "__main__":
    main()
