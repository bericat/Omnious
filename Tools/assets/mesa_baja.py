"""Mesa baja del salón: madera barnizada gastada, con revistero abajo, un mando y cercos de vasos.

Sustituye a la malla provisional MesaBaja (1,0 x 0,55 m, tablero a 0,42 m). Frente a +Z en Unity.
Uso:  python Tools/assets/mesa_baja.py   ->  Models/MesaBaja.fbx y Texturas/MesaBaja.jpg
Texturas CC0: Mueble_Wood092, Suciedad_SurfaceImperfections015.
"""
import os
import sys

import bpy
import bmesh

sys.path.insert(0, os.path.dirname(__file__))
import comun as c  # noqa: E402
import hornear  # noqa: E402

MADERA, PATA, NEGRO, PAPEL = range(4)


def mesa():
    bm = bmesh.new()
    cm = c.caja_mat
    cm(bm, (0, 0, 0.40), (1.0, 0.55, 0.04), MADERA, 0.008, 3)           # tablero
    cm(bm, (0, 0, 0.365), (0.92, 0.47, 0.03), PATA, 0.003)              # faldón
    cm(bm, (0, 0, 0.13), (0.88, 0.45, 0.022), MADERA, 0.004)            # revistero
    for x in (-0.44, 0.44):
        for y in (-0.215, 0.215):
            cm(bm, (x, y, 0.19), (0.05, 0.05, 0.38), PATA, 0.006)
    # Mando a distancia y un par de revistas
    cm(bm, (-0.22, -0.05, 0.4325), (0.16, 0.05, 0.025), NEGRO, 0.006)
    for i in range(4):
        cm(bm, (-0.27 + i * 0.03, -0.055, 0.446), (0.012, 0.012, 0.004), PAPEL, 0)
    cm(bm, (0.10, 0.03, 0.149), (0.26, 0.34, 0.012), PAPEL, 0.001)
    cm(bm, (0.13, 0.05, 0.158), (0.24, 0.32, 0.008), PAPEL, 0.001)
    ob = c.objeto("MesaBaja", bm, [])
    return ob


def main():
    c.escena_vacia()
    hs = hornear.material_sucio
    mats = [
        hs("Madera", (0.42, 0.30, 0.20), rugosidad=0.4, imagen=c.cc0("Mueble_Wood092"), escala=1.0,
           suciedad=0.8, polvo=0.2, manchas=0.35, desgaste=0.6, color_desgaste=(0.50, 0.38, 0.25),
           color_sucio=(0.10, 0.07, 0.04), mugre=0.6, escala_manchas=6),
        hs("Pata", (0.28, 0.19, 0.12), rugosidad=0.5, imagen=c.cc0("Mueble_Wood092"), escala=1.0,
           suciedad=0.8, polvo=0.6, desgaste=0.4, color_sucio=(0.08, 0.06, 0.04)),
        hs("Negro", (0.03, 0.03, 0.03), rugosidad=0.5, suciedad=0.4, manchas=0.3),
        hs("Papel", (0.55, 0.50, 0.42), rugosidad=0.8, suciedad=0.6, manchas=0.5, escala_manchas=12),
    ]
    ob = mesa()
    for m in mats:
        ob.data.materials.append(m)
    hornear.atlas(ob, "MesaBaja", tam=1024)
    ruta = c.exportar_fbx("MesaBaja", [ob])
    print(f"Exportado {ruta} ({sum(len(p.vertices) - 2 for p in ob.data.polygons)} triángulos)")


if __name__ == "__main__":
    main()
