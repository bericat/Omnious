"""Aparador bajo de salón: madera oscura como la vitrina, dos cajones y dos puertas de cuarterón.
Encima, un tapete de ganchillo, un jarrón con flores secas, una foto enmarcada y cintas de vídeo.

Mueble nuevo para el hueco a la derecha de la tele: 0,90 x 0,80 x 0,45 m (encimera incluida), frente a +Z
en Unity, origen en el suelo en el centro. Un objeto, textura horneada Texturas/Aparador.jpg.

Uso:  python Tools/assets/aparador.py
"""
import math
import os
import sys

import bpy  # noqa: F401  (carga bmesh)
import bmesh
from mathutils import Matrix

sys.path.insert(0, os.path.dirname(__file__))
import comun as c  # noqa: E402
import hornear  # noqa: E402

MADERA, INTERIOR, METAL, TAPETE, LOZA, SECO, FOTO, VHS = range(8)
W, H, D = 0.90, 0.80, 0.45
G = 0.022
Z_TAPA = H - 0.03          # la encimera va de Z_TAPA a H
Y_FRENTE = -D / 2 + 0.02   # frente del cuerpo (la encimera vuela 2 cm)


def puerta(bm, cx, z0, z1, ancho):
    """Puerta de cuarterón: marco y tablero central en relieve."""
    cm = c.caja_mat
    h = z1 - z0
    zc = (z0 + z1) / 2
    y = Y_FRENTE - 0.011
    cm(bm, (cx, y + 0.004, zc), (ancho, 0.014, h), MADERA, 0.003)
    for dx in (-1, 1):
        cm(bm, (cx + dx * (ancho / 2 - 0.03), y - 0.004, zc), (0.06, 0.012, h), MADERA, 0.003)
    for dz in (-1, 1):
        cm(bm, (cx, y - 0.004, zc + dz * (h / 2 - 0.03)), (ancho - 0.12, 0.012, 0.06), MADERA, 0.003)
    cm(bm, (cx, y - 0.006, zc), (ancho - 0.18, 0.012, h - 0.18), MADERA, 0.012, segmentos=2)


def mueble(bm):
    cm = c.caja_mat
    zb = 0.08
    for s in (-1, 1):
        cm(bm, (s * (W / 2 - 0.02 - G / 2), 0.01, (zb + Z_TAPA) / 2), (G, D - 0.04, Z_TAPA - zb), MADERA, 0.003)
    cm(bm, (0, D / 2 - 0.02, (zb + Z_TAPA) / 2), (W - 0.04, 0.012, Z_TAPA - zb), INTERIOR, 0)
    # Zócalo moldurado y encimera con canto redondeado y moldura debajo
    cm(bm, (0, 0.0, zb / 2), (W - 0.02, D - 0.03, zb), MADERA, 0.006)
    cm(bm, (0, -0.002, zb + 0.008), (W - 0.03, D - 0.034, 0.016), MADERA, 0.006)
    cm(bm, (0, 0, Z_TAPA + 0.015), (W, D, 0.03), MADERA, 0.008, segmentos=2)
    cm(bm, (0, 0.004, Z_TAPA - 0.01), (W - 0.03, D - 0.03, 0.02), MADERA, 0.006)
    cm(bm, (0, Y_FRENTE + 0.01, 0.65), (W - 0.04 - 2 * G, 0.02, 0.2), INTERIOR, 0)   # tapa el hueco tras los cajones
    # Dos cajones arriba con tirador de concha y dos puertas abajo
    ancho = (W - 0.04 - 2 * G - 0.006) / 2
    for s in (-1, 1):
        cx = s * (ancho / 2 + 0.003)
        cm(bm, (cx, Y_FRENTE - 0.009, 0.672), (ancho, 0.018, 0.14), MADERA, 0.004)
        cm(bm, (cx, Y_FRENTE - 0.021, 0.675), (0.10, 0.008, 0.016), METAL, 0.003)
        for dx in (-0.045, 0.045):
            cm(bm, (cx + dx, Y_FRENTE - 0.02, 0.675), (0.016, 0.012, 0.03), METAL, 0.004)
        puerta(bm, cx, 0.095, 0.596, ancho)
        c.marcar(bm)
        c.torno(bm, [(0.008, 0), (0.005, 0.008), (0.005, 0.016), (0.012, 0.02), (0.013, 0.027), (0.002, 0.03)],
                lados=10)
        nv = c.nuevos(bm)
        bmesh.ops.rotate(bm, verts=nv, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, "X"))
        bmesh.ops.translate(bm, verts=nv, vec=(-s * 0.04, Y_FRENTE - 0.022, 0.42))
        c.asignar(bm, {f for v in nv for f in v.link_faces}, METAL)


def encima(bm):
    cm = c.caja_mat
    z = H
    # Tapete de ganchillo con borde ondulado, a la derecha (vista de frente)
    c.marcar(bm)
    lados = 36
    anillo = [bm.verts.new(((0.21 + 0.012 * math.cos(9 * 2 * math.pi * i / lados)) * math.cos(2 * math.pi * i / lados)
                            + 0.12, (0.15 + 0.010 * math.cos(9 * 2 * math.pi * i / lados))
                            * math.sin(2 * math.pi * i / lados) - 0.02, z + 0.003)) for i in range(lados)]
    bm.faces.new(anillo)
    c.asignar(bm, {f for v in c.nuevos(bm) for f in v.link_faces}, TAPETE)
    # Jarrón de loza sobre el tapete con flores secas
    jx, jy = 0.16, 0.02
    c.marcar(bm)
    c.torno(bm, [(0.04, 0), (0.06, 0.04), (0.068, 0.09), (0.05, 0.16), (0.03, 0.20), (0.032, 0.22), (0.04, 0.235),
                 (0.034, 0.235), (0.024, 0.20), (0.002, 0.195)], lados=14, desde=(jx, jy, z + 0.003))
    c.asignar(bm, {f for v in c.nuevos(bm) for f in v.link_faces}, LOZA)
    rng = __import__("random").Random(4)
    for k in range(9):
        a = 2 * math.pi * k / 9 + rng.uniform(-0.3, 0.3)
        inc = rng.uniform(0.12, 0.35)
        largo = rng.uniform(0.18, 0.30)
        base = (jx, jy, z + 0.19)
        punta = (jx + math.cos(a) * math.sin(inc) * largo, jy + math.sin(a) * math.sin(inc) * largo,
                 z + 0.19 + math.cos(inc) * largo)
        barra(bm, base, punta, 0.0025, SECO)
        cm(bm, punta, (0.025, 0.025, 0.03), SECO, 0.008, rot=Matrix.Rotation(a, 3, "Z"))
    # Foto enmarcada, inclinada hacia atrás, a la izquierda
    rot = Matrix.Rotation(math.radians(-12), 3, "X")
    cm(bm, (-0.26, 0.10, z + 0.105), (0.17, 0.016, 0.22), MADERA, 0.004, rot=rot)
    cm(bm, (-0.26, 0.10 - 0.009, z + 0.105), (0.13, 0.004, 0.18), FOTO, 0, rot=rot)
    barra(bm, (-0.26, 0.11, z + 0.12), (-0.26, 0.17, z), 0.004, MADERA)
    # Tres cintas de vídeo apiladas, delante
    for i in range(3):
        cm(bm, (-0.18 + i * 0.006, -0.10 + i * 0.004, z + 0.0125 + i * 0.025), (0.19, 0.105, 0.025), VHS, 0.002,
           rot=Matrix.Rotation(math.radians(8 - i * 6), 3, "Z"))


def barra(bm, a, b, r, mat, lados=6):
    from mathutils import Vector
    a, b = Vector(a), Vector(b)
    c.marcar(bm)
    bmesh.ops.create_cone(bm, cap_ends=True, segments=lados, radius1=r, radius2=r, depth=(b - a).length)
    nv = c.nuevos(bm)
    bmesh.ops.transform(bm, matrix=(b - a).to_track_quat("Z", "Y").to_matrix().to_4x4(), verts=nv)
    bmesh.ops.translate(bm, verts=nv, vec=(a + b) / 2)
    c.asignar(bm, {f for v in nv for f in v.link_faces}, mat)


def main():
    c.escena_vacia()
    hs = hornear.material_sucio
    mats = [
        hornear.madera_vieja("Madera", "oscura", desgaste=0.6, escala=0.8),
        hornear.madera_vieja("Interior", (0.15, 0.12, 0.09), polvo=0.0, suciedad=1.3, semilla=5.0),
        hs("Metal", (0.20, 0.14, 0.05), rugosidad=0.35, metal=1.0, suciedad=1.0, manchas=0.6, polvo=0.2),
        hs("Tapete", (0.52, 0.47, 0.36), rugosidad=0.9, suciedad=0.8, manchas=0.6, escala_manchas=12, polvo=0.4),
        hs("Loza", (0.08, 0.13, 0.19), rugosidad=0.25, suciedad=0.9, manchas=0.4, polvo=0.25),
        hs("Seco", (0.13, 0.07, 0.03), rugosidad=0.9, suciedad=0.5, polvo=0.15),
        hs("Foto", (0.15, 0.11, 0.08), rugosidad=0.3, suciedad=0.8, manchas=0.8, escala_manchas=6),
        hs("Vhs", (0.035, 0.035, 0.035), rugosidad=0.5, suciedad=0.6, polvo=1.0),
    ]
    bm = bmesh.new()
    mueble(bm)
    encima(bm)
    ob = c.objeto("Aparador", bm, mats)
    for p in ob.data.polygons:
        p.use_smooth = p.material_index in (LOZA, METAL) and len(p.vertices) == 4
    hornear.atlas(ob, "Aparador", tam=2048, margen=0.002)
    ruta = c.exportar_fbx("Aparador", [ob])
    print(f"Exportado {ruta} ({sum(len(p.vertices) - 2 for p in ob.data.polygons)} triángulos)")


if __name__ == "__main__":
    main()
