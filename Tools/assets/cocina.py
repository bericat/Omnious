"""Cocina vieja de los 80: encimera con armarios de madera, azulejos, fregadero y fuego de gas; nevera
de esmalte amarillento; mesa de formica, silla de madera y una caja de fruta con latas y botellas.

Sustituyen a las mallas provisionales de HouseBuilder con la misma huella y orientación: frente a +Z
en Unity (aquí, en Blender, a -Y), origen en el suelo en el centro. x de Unity = -x de Blender.
- Encimera: 4,4 x 0,62 m, a 0,92 m. Armarios altos a x Unity -1,65 (1,05 m) y 1,45 (1,45 m).
- Nevera: 0,72 x 0,68 x 1,84 m, tiradores a la izquierda (x Unity -0,29).
- MesaCocina: 1,4 x 0,8 m, a 0,76 m.   SillaCocina: asiento 0,42 m a 0,45 m, respaldo detrás.
- CajaLatas (nueva): caja de 0,50 x 0,32 x 0,18 m con latas y botellas.

Uso:  python Tools/assets/cocina.py [Encimera|Nevera|MesaCocina|SillaCocina|CajaLatas]
Texturas CC0: Mueble_Wood092, Oxido_Rust004, Suciedad_SurfaceImperfections015.
"""
import math
import os
import random
import sys

import bpy
import bmesh
import numpy as np
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(__file__))
import comun as c  # noqa: E402
import hornear  # noqa: E402

(MADERA, PUERTA, FORMICA, AZULEJO, ACERO, NEGRO, ESMALTE, METAL, OXIDO,
 LATA_R, LATA_V, LATA_A, BOTELLA, ETIQUETA, CAJA) = range(15)


def azulejos():
    """Azulejo de 15 x 15 cm color hueso con juntas sucias. La imagen cubre 0,6 m."""
    t = 512
    yy, xx = np.mgrid[0:t, 0:t]
    p = t // 4
    junta = ((xx % p) < 4) | ((yy % p) < 4)
    rng = np.random.default_rng(4)
    tono = rng.random((4, 4)) * 0.08 - 0.04
    base = np.array((0.78, 0.74, 0.62))[None, None, :] + tono[(yy // p) % 4, (xx // p) % 4][..., None]
    img = np.where(junta[..., None], np.array((0.30, 0.26, 0.19)), base)
    img = img * (0.93 + c.fbm(t, t, rng, (64, 16, 4))[..., None] * 0.14)
    im = c.guardar_png("_Azulejo", img)
    im.pack(); os.remove(im.filepath_raw)
    return im


def materiales():
    hs = hornear.material_sucio
    mv = hornear.madera_vieja
    return [
        mv("Madera", (0.30, 0.20, 0.11)),
        mv("Puerta", (0.34, 0.22, 0.12), escala=0.6, desgaste=0.7, semilla=2.0),
        hs("Formica", (0.40, 0.36, 0.27), rugosidad=0.35, suciedad=0.9, manchas=0.6, escala_manchas=9, mugre=0.8,
           mugre_escala=0.4, color_sucio=(0.14, 0.10, 0.06), polvo=0.0),
        hs("Azulejo", (0.75, 0.75, 0.75), rugosidad=0.25, imagen=azulejos(), escala=0.6, suciedad=0.8, manchas=0.5,
           mugre=0.7, color_sucio=(0.16, 0.12, 0.07), chorretones=0.5, polvo=0.0),
        hs("Acero", (0.50, 0.50, 0.48), rugosidad=0.35, metal=1.0, suciedad=0.8, manchas=0.6, mugre=0.7,
           color_sucio=(0.16, 0.13, 0.09), polvo=0.0),
        hs("Negro", (0.035, 0.033, 0.03), rugosidad=0.5, suciedad=0.4, manchas=0.4, color_sucio=(0.12, 0.10, 0.08)),
        hornear.plastico_viejo("Esmalte", (0.55, 0.52, 0.42), chorretones=0.4),
        hs("Metal", (0.45, 0.44, 0.40), rugosidad=0.3, metal=1.0, suciedad=0.8, manchas=0.4),
        hs("Oxido", (0.8, 0.8, 0.8), rugosidad=0.8, imagen=c.cc0("Oxido_Rust004"), escala=0.3, suciedad=0.5,
           color_sucio=(0.06, 0.04, 0.02)),
        hs("LataR", (0.40, 0.06, 0.04), rugosidad=0.4, suciedad=0.8, manchas=0.6, mugre=0.9, mugre_escala=0.2),
        hs("LataV", (0.08, 0.22, 0.20), rugosidad=0.4, suciedad=0.8, manchas=0.6, mugre=0.9, mugre_escala=0.2),
        hs("LataA", (0.55, 0.42, 0.12), rugosidad=0.4, suciedad=0.8, manchas=0.6, mugre=0.9, mugre_escala=0.2),
        hs("Botella", (0.12, 0.05, 0.015), rugosidad=0.1, suciedad=0.6, manchas=0.3),
        hs("Etiqueta", (0.55, 0.48, 0.34), rugosidad=0.8, suciedad=0.6, manchas=0.6, escala_manchas=20),
        mv("Caja", (0.28, 0.24, 0.16), escala=0.5, desgaste=0.7, semilla=6.0),
    ]


def cil(bm, centro, r, alto, mat, lados=12, rot=None, r2=None):
    c.marcar(bm)
    bmesh.ops.create_cone(bm, cap_ends=True, segments=lados, radius1=r, radius2=r if r2 is None else r2, depth=alto)
    nv = c.nuevos(bm)
    if rot is not None:
        bmesh.ops.transform(bm, matrix=rot.to_4x4(), verts=nv)
    bmesh.ops.translate(bm, verts=nv, vec=centro)
    c.asignar(bm, {f for v in nv for f in v.link_faces}, mat)


def barra(bm, a, b, r, mat, lados=8):
    a, b = Vector(a), Vector(b)
    c.marcar(bm)
    bmesh.ops.create_cone(bm, cap_ends=True, segments=lados, radius1=r, radius2=r, depth=(b - a).length)
    nv = c.nuevos(bm)
    bmesh.ops.transform(bm, matrix=(b - a).to_track_quat("Z", "Y").to_matrix().to_4x4(), verts=nv)
    bmesh.ops.translate(bm, verts=nv, vec=(a + b) / 2)
    c.asignar(bm, {f for v in nv for f in v.link_faces}, mat)


def encimera():
    bm = bmesh.new()
    cm = c.caja_mat
    W = 4.4
    cm(bm, (0, 0.0, 0.47), (W, 0.56, 0.74), MADERA, 0.004)                 # cuerpo
    cm(bm, (0, -0.24, 0.05), (W, 0.06, 0.10), NEGRO, 0.003)                # zócalo
    cm(bm, (0, -0.01, 0.90), (W + 0.02, 0.62, 0.04), FORMICA, 0.006)       # encimera
    cm(bm, (0, 0.30, 1.22), (W, 0.012, 0.60), AZULEJO, 0)                  # azulejos hasta los armarios
    # Puertas y cajones (frente a -Y); el hueco del fregadero (x = 0) solo lleva puertas
    n = 6
    for i in range(n):
        x = -W / 2 + (i + 0.5) * W / n
        ancho = W / n - 0.012
        cm(bm, (x, -0.287, 0.43), (ancho, 0.02, 0.62), PUERTA, 0.004)
        cm(bm, (x, -0.287, 0.80), (ancho, 0.02, 0.10), PUERTA, 0.004)
        hx = x + (ancho / 2 - 0.05) * (1 if i % 2 else -1)
        cm(bm, (hx, -0.302, 0.65), (0.014, 0.012, 0.09), METAL, 0.002)
        cm(bm, (x, -0.302, 0.80), (0.10, 0.012, 0.014), METAL, 0.002)
    # Fregadero de acero con escurridor, grifo y desagüe
    cm(bm, (0, -0.01, 0.922), (0.90, 0.48, 0.006), ACERO, 0.002)
    cm(bm, (0.10, -0.01, 0.85), (0.40, 0.36, 0.14), ACERO, 0.01)           # cubeta (la ve el jugador por arriba)
    cm(bm, (0.10, -0.01, 0.924), (0.36, 0.32, 0.004), NEGRO, 0)            # fondo oscuro de la cubeta
    for k in range(7):
        cm(bm, (-0.24, -0.17 + k * 0.05, 0.926), (0.30, 0.012, 0.003), ACERO, 0)
    barra(bm, (0.10, 0.20, 0.92), (0.10, 0.20, 1.15), 0.014, METAL)
    barra(bm, (0.10, 0.205, 1.14), (0.10, 0.03, 1.10), 0.011, METAL)
    for s in (-1, 1):
        cil(bm, (0.10 + s * 0.09, 0.20, 0.95), 0.016, 0.05, METAL, lados=8)
    # Fuego de gas de cuatro quemadores
    xf = -1.25
    cm(bm, (xf, -0.02, 0.925), (0.56, 0.48, 0.012), ESMALTE, 0.004)
    for dx in (-0.13, 0.13):
        for dy in (-0.11, 0.11):
            cil(bm, (xf + dx, -0.02 + dy, 0.937), 0.045, 0.012, NEGRO, lados=10)
            cil(bm, (xf + dx, -0.02 + dy, 0.945), 0.022, 0.01, OXIDO, lados=8)
    for k in range(4):
        cil(bm, (xf - 0.18 + k * 0.12, -0.31, 0.80), 0.016, 0.02, NEGRO, lados=8,
            rot=Matrix.Rotation(math.radians(90), 3, "X"))
    # Armarios altos a los lados de la ventana
    for x, ancho in ((1.65, 1.05), (-1.45, 1.45)):
        cm(bm, (x, 0.11, 1.82), (ancho, 0.33, 0.72), MADERA, 0.004)
        hojas = 2 if ancho < 1.2 else 3
        for h in range(hojas):
            hx = x - ancho / 2 + (h + 0.5) * ancho / hojas
            cm(bm, (hx, -0.062, 1.82), (ancho / hojas - 0.012, 0.02, 0.68), PUERTA, 0.004)
            cm(bm, (hx + (ancho / hojas / 2 - 0.05) * (1 if h % 2 else -1), -0.078, 1.53), (0.014, 0.012, 0.09),
               METAL, 0.002)
    # Cosas encima: bote de lavavajillas, tarro y trapo
    cil(bm, (0.48, 0.18, 1.0), 0.03, 0.16, LATA_V, lados=8)
    cil(bm, (0.65, 0.2, 0.99), 0.05, 0.14, ETIQUETA, lados=10)
    cm(bm, (-0.62, -0.18, 0.925), (0.30, 0.22, 0.012), ETIQUETA, 0.003)
    return bm


def nevera():
    bm = bmesh.new()
    cm = c.caja_mat
    cm(bm, (0, 0.0, 0.94), (0.72, 0.66, 1.80), ESMALTE, 0.035)
    cm(bm, (0, -0.335, 0.63), (0.69, 0.03, 1.10), ESMALTE, 0.02)           # puerta de abajo
    cm(bm, (0, -0.335, 1.49), (0.69, 0.03, 0.56), ESMALTE, 0.02)           # congelador
    for z, alto in ((1.08, 0.30), (1.36, 0.20)):
        cm(bm, (0.29, -0.365, z), (0.03, 0.03, alto), METAL, 0.008)
    cm(bm, (0, -0.30, 0.035), (0.66, 0.06, 0.07), OXIDO, 0.004)            # rejilla de abajo, oxidada
    for k in range(5):
        cm(bm, (0, -0.333, 0.015 + k * 0.012), (0.60, 0.004, 0.004), NEGRO, 0)
    cm(bm, (0, -0.352, 1.73), (0.12, 0.004, 0.03), METAL, 0)               # placa de la marca
    # Un imán y un papel sujeto en la puerta
    cm(bm, (-0.12, -0.352, 1.25), (0.15, 0.002, 0.20), ETIQUETA, 0)
    cil(bm, (-0.12, -0.355, 1.33), 0.012, 0.008, LATA_R, lados=8, rot=Matrix.Rotation(math.radians(90), 3, "X"))
    return bm


def mesa():
    bm = bmesh.new()
    cm = c.caja_mat
    cm(bm, (0, 0, 0.745), (1.4, 0.8, 0.03), FORMICA, 0.004)
    cm(bm, (0, 0, 0.722), (1.4, 0.8, 0.016), METAL, 0.003)                # canto de aluminio
    for s in (-1, 1):
        cm(bm, (0, s * 0.33, 0.68), (1.2, 0.02, 0.07), MADERA, 0.002)
        cm(bm, (s * 0.61, 0, 0.68), (0.02, 0.6, 0.07), MADERA, 0.002)
    for x in (-0.64, 0.64):
        for y in (-0.34, 0.34):
            cm(bm, (x, y, 0.355), (0.05, 0.05, 0.71), MADERA, 0.004)
    return bm


def silla():
    bm = bmesh.new()
    cm = c.caja_mat
    cm(bm, (0, -0.01, 0.45), (0.42, 0.40, 0.035), MADERA, 0.005)
    for x in (-0.19, 0.19):
        cm(bm, (x, -0.19, 0.22), (0.03, 0.03, 0.44), MADERA, 0.003)
        cm(bm, (x, 0.195, 0.47), (0.03, 0.03, 0.94), MADERA, 0.003)
        cm(bm, (x, 0.0, 0.16), (0.02, 0.36, 0.02), MADERA, 0.002)
    for z in (0.70, 0.86):
        cm(bm, (0, 0.195, z), (0.36, 0.022, 0.07 if z > 0.8 else 0.04), MADERA, 0.003)
    cm(bm, (0, -0.19, 0.16), (0.36, 0.02, 0.02), MADERA, 0.002)
    return bm


def caja_latas():
    bm = bmesh.new()
    cm = c.caja_mat
    W, D, H = 0.50, 0.32, 0.18
    cm(bm, (0, 0, 0.006), (W - 0.02, D - 0.02, 0.012), CAJA, 0.002)
    for s in (-1, 1):
        for z in (0.03, 0.09, 0.15):
            cm(bm, (0, s * (D / 2 - 0.006), z), (W, 0.012, 0.045), CAJA, 0.003)
        for z in (0.04, 0.14):
            cm(bm, (s * (W / 2 - 0.009), 0, z), (0.018, D - 0.024, 0.07), CAJA, 0.003)
        for y in (-1, 1):
            cm(bm, (s * (W / 2 - 0.015), y * (D / 2 - 0.015), H / 2), (0.03, 0.03, H), CAJA, 0.003)
    rng = random.Random(3)
    huecos = [(-0.17, -0.08), (-0.08, -0.09), (0.02, -0.07), (0.11, -0.09), (-0.16, 0.05), (-0.06, 0.06),
              (0.06, 0.07), (0.17, 0.0)]
    for i, (x, y) in enumerate(huecos):
        if i in (2, 6):
            # Botella de cerveza con su etiqueta
            c.marcar(bm)
            c.torno(bm, [(0.03, 0), (0.031, 0.15), (0.026, 0.18), (0.012, 0.22), (0.012, 0.25), (0.002, 0.25)],
                    lados=10, desde=(x, y, 0.012))
            c.asignar(bm, {f for v in c.nuevos(bm) for f in v.link_faces}, BOTELLA)
            cil(bm, (x, y, 0.08), 0.0315, 0.07, ETIQUETA, lados=10)
            cil(bm, (x, y, 0.265), 0.013, 0.012, METAL, lados=8)
            continue
        # Lata de hojalata (u oxidada) con la etiqueta de papel de color
        alto = rng.choice((0.11, 0.12, 0.10))
        cuerpo = OXIDO if rng.random() < 0.3 else METAL
        etiqueta = rng.choice((LATA_R, LATA_V, LATA_A, LATA_R))
        if i == 4:
            rot = Matrix.Rotation(math.radians(90), 3, "Y")
            cil(bm, (x + 0.02, y, 0.012 + 0.04 + 0.11), 0.04, alto, cuerpo, rot=rot)
            cil(bm, (x + 0.02, y, 0.012 + 0.04 + 0.11), 0.0405, alto * 0.75, etiqueta, rot=rot)
            continue
        cil(bm, (x, y, 0.012 + alto / 2), 0.04, alto, cuerpo)
        if cuerpo != OXIDO or rng.random() < 0.5:
            cil(bm, (x, y, 0.012 + alto * 0.5), 0.0405, alto * 0.75, etiqueta)
    return bm


PIEZAS = {"Encimera": (encimera, 2048), "Nevera": (nevera, 1024), "MesaCocina": (mesa, 1024),
          "SillaCocina": (silla, 512), "CajaLatas": (caja_latas, 1024)}


def main(nombre):
    c.escena_vacia()
    f, tam = PIEZAS[nombre]
    mats = materiales()
    ob = c.objeto(nombre, f(), mats)
    for p in ob.data.polygons:
        # Solo los laterales (quads): las tapas de los cilindros, planas
        p.use_smooth = p.material_index in (LATA_R, LATA_V, LATA_A, BOTELLA, ETIQUETA, METAL, OXIDO) and len(p.vertices) == 4
    # Quita los materiales que la pieza no usa (si no, el atlas reserva sitio para nada)
    usados = sorted({p.material_index for p in ob.data.polygons})
    viejos = list(ob.data.materials)
    idx = {old: new for new, old in enumerate(usados)}
    nuevos = [idx[p.material_index] for p in ob.data.polygons]
    ob.data.materials.clear()  # (pone todos los índices a 0: se reasignan después)
    for i in usados:
        ob.data.materials.append(viejos[i])
    for p, i in zip(ob.data.polygons, nuevos):
        p.material_index = i
    hornear.atlas(ob, nombre, tam=tam, margen=0.003)
    ruta = c.exportar_fbx(nombre, [ob])
    print(f"Exportado {ruta} ({sum(len(p.vertices) - 2 for p in ob.data.polygons)} triángulos)")


if __name__ == "__main__":
    for n in (sys.argv[1:] or list(PIEZAS)):
        main(n)
