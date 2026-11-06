"""Estantería del salón: madera vieja agrisada con cornisa y zócalo moldurados, libros viejos, cajas, un marco de foto y un jarrón.

Sustituye a la malla provisional Estanteria (1,0 x 1,9 x 0,3 m). En este FBX el frente mira a +Z
en Unity; la provisional lo tenía a -Z (contra la pared norte): se coloca girada 180°.
Uso:  python Tools/assets/estanteria.py   ->  Models/Estanteria.fbx y Texturas/Estanteria.jpg
Texturas CC0: Mueble_Wood092, Suciedad_SurfaceImperfections015.
"""
import math
import os
import random
import sys

import bpy
import bmesh
from mathutils import Matrix

sys.path.insert(0, os.path.dirname(__file__))
import comun as c  # noqa: E402
import hornear  # noqa: E402

MADERA, BALDA, CARTON, CERAMICA, MARCO, FOTO = range(6)
LIBROS = list(range(6, 12))
W, H, D = 1.0, 1.9, 0.30


def estanteria():
    bm = bmesh.new()
    cm = c.caja_mat
    for s in (-1, 1):
        cm(bm, (s * (W / 2 - 0.015), 0, H / 2), (0.03, D, H), MADERA, 0.004)
    cm(bm, (0, D / 2 - 0.006, H / 2), (W - 0.03, 0.012, H - 0.02), MADERA, 0)
    # Cornisa: tapa que vuela y moldura escalonada debajo
    cm(bm, (0, -0.012, H - 0.012), (W + 0.06, D + 0.035, 0.024), MADERA, 0.004)
    cm(bm, (0, -0.007, H - 0.034), (W + 0.035, D + 0.02, 0.02), MADERA, 0.006)
    cm(bm, (0, -0.003, H - 0.054), (W + 0.012, D + 0.008, 0.022), MADERA, 0.004)
    # Zócalo moldurado
    cm(bm, (0, -0.008, 0.035), (W + 0.04, D + 0.025, 0.07), MADERA, 0.006)
    cm(bm, (0, -0.004, 0.08), (W + 0.018, D + 0.012, 0.02), MADERA, 0.006)
    alturas = [0.08 + i * 0.455 for i in range(4)]
    for z in alturas[1:]:
        cm(bm, (0, 0, z), (W - 0.06, D - 0.015, 0.025), BALDA, 0.003)
    rng = random.Random(7)
    for nivel, z in enumerate(alturas):
        base = z + 0.0125 if nivel else 0.09
        x = -W / 2 + 0.045
        fin = W / 2 - 0.045
        hueco = rng.random() < 0.5
        while x < fin - 0.03:
            if hueco and rng.random() < 0.12:
                # objeto en vez de libros
                tipo = rng.choice(["caja", "jarron", "marco"])
                if tipo == "caja" and x + 0.26 < fin:
                    cm(bm, (x + 0.13, 0.0, base + 0.08), (0.24, 0.22, 0.16), CARTON, 0.004)
                    x += 0.27
                elif tipo == "jarron" and x + 0.16 < fin:
                    c.marcar(bm)
                    perfil = [(0.045, 0), (0.06, 0.04), (0.07, 0.10), (0.055, 0.17), (0.03, 0.21), (0.035, 0.24), (0.03, 0.245)]
                    c.torno(bm, perfil, lados=16, desde=(x + 0.08, 0.0, base))
                    c.asignar(bm, {f for v in c.nuevos(bm) for f in v.link_faces}, CERAMICA)
                    x += 0.17
                elif x + 0.18 < fin:
                    rot = Matrix.Rotation(math.radians(-12), 3, "X")
                    cm(bm, (x + 0.09, 0.02, base + 0.11), (0.16, 0.015, 0.21), MARCO, 0.003, rot=rot)
                    cm(bm, (x + 0.09, 0.0105, base + 0.112), (0.12, 0.002, 0.16), FOTO, 0, rot=rot)
                    x += 0.19
                continue
            bw = 0.022 + rng.random() * 0.04
            bh = 0.17 + rng.random() * 0.17
            bd = 0.15 + rng.random() * 0.07
            if x + bw > fin:
                break
            inclinado = rng.random() < 0.06 and x > -0.3
            rot = Matrix.Rotation(math.radians(-14), 3, "Y") if inclinado else None
            cm(bm, (x + bw / 2, -0.01 + (0.2 - bd) / 2, base + bh / 2), (bw, bd, bh), rng.choice(LIBROS), 0.002, rot=rot)
            x += bw + 0.001 + (0.05 if inclinado else 0)
    return c.objeto("Estanteria", bm, [])


def main():
    c.escena_vacia()
    hs = hornear.material_sucio
    mats = [
        hornear.madera_vieja("Madera", "gris", desgaste=0.5),
        hornear.madera_vieja("Balda", (0.26, 0.23, 0.19), suciedad=1.2, polvo=0.0, semilla=4.0),
        hs("Carton", (0.42, 0.32, 0.21), rugosidad=0.9, suciedad=0.8, manchas=0.5, escala_manchas=10),
        hs("Ceramica", (0.42, 0.46, 0.44), rugosidad=0.3, suciedad=0.7, manchas=0.2),
        hs("Marco", (0.40, 0.32, 0.18), rugosidad=0.4, metal=0.6, suciedad=0.9, manchas=0.4),
        hs("Foto", (0.45, 0.38, 0.30), rugosidad=0.3, suciedad=0.5, manchas=0.6, escala_manchas=20),
    ]
    for i, col in enumerate([(0.28, 0.10, 0.07), (0.11, 0.14, 0.18), (0.14, 0.18, 0.11),
                             (0.40, 0.34, 0.24), (0.20, 0.14, 0.09), (0.08, 0.08, 0.07)]):
        mats.append(hs(f"Libro{i}", col, rugosidad=0.7, suciedad=0.9, manchas=0.4, escala_manchas=15, semilla=i))
    ob = estanteria()
    for m in mats:
        ob.data.materials.append(m)
    hornear.atlas(ob, "Estanteria", tam=2048, margen=0.002)
    ruta = c.exportar_fbx("Estanteria", [ob])
    print(f"Exportado {ruta} ({sum(len(p.vertices) - 2 for p in ob.data.polygons)} triángulos)")


if __name__ == "__main__":
    main()
