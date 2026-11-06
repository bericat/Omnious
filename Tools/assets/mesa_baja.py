"""Mesa baja del salón: madera vieja agrisada, con balda abajo, revistas, un mando y una taza.

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

MADERA, PATA, NEGRO, PAPEL, TAZA = range(5)


def mesa():
    """Mesa de patas rectas con travesaños y balda abajo, como un mueble de los 70 gastado."""
    bm = bmesh.new()
    cm = c.caja_mat
    cm(bm, (0, 0, 0.40), (1.0, 0.55, 0.035), MADERA, 0.006)            # tablero
    for y in (-0.235, 0.235):
        cm(bm, (0, y, 0.355), (0.86, 0.022, 0.06), PATA, 0.002)          # faldones
    for x in (-0.445, 0.445):
        cm(bm, (x, 0, 0.355), (0.022, 0.42, 0.06), PATA, 0.002)
    cm(bm, (0, 0, 0.11), (0.90, 0.46, 0.02), MADERA, 0.003)             # balda
    for x in (-0.46, 0.46):
        for y in (-0.235, 0.235):
            cm(bm, (x, y, 0.19), (0.045, 0.045, 0.38), PATA, 0.004)
    # Mando, revistas y una taza
    cm(bm, (-0.22, -0.05, 0.43), (0.17, 0.05, 0.025), NEGRO, 0.004)
    for i in range(4):
        cm(bm, (-0.28 + i * 0.03, -0.056, 0.443), (0.012, 0.012, 0.004), PAPEL, 0)
    cm(bm, (0.10, 0.03, 0.126), (0.26, 0.34, 0.012), PAPEL, 0.001)
    cm(bm, (0.13, 0.05, 0.135), (0.24, 0.32, 0.008), PAPEL, 0.001)
    c.marcar(bm)
    c.torno(bm, [(0.035, 0), (0.04, 0.09), (0.036, 0.09), (0.032, 0.006), (0.002, 0.006)], lados=12,
            desde=(0.25, -0.08, 0.4175))
    c.asignar(bm, {f for v in c.nuevos(bm) for f in v.link_faces}, TAZA)
    cm(bm, (0.295, -0.08, 0.465), (0.012, 0.008, 0.05), TAZA, 0.002)    # asa
    return c.objeto("MesaBaja", bm, [])


def main():
    c.escena_vacia()
    hs = hornear.material_sucio
    mats = [
        hornear.madera_vieja("Madera", "gris", desgaste=0.6, manchas=0.45, escala_manchas=6),
        hornear.madera_vieja("Pata", "gris", polvo=0.6, semilla=3.0),
        hs("Negro", (0.04, 0.04, 0.04), rugosidad=0.5, suciedad=0.5, manchas=0.3),
        hs("Papel", (0.50, 0.46, 0.38), rugosidad=0.8, suciedad=0.7, manchas=0.5, escala_manchas=12),
        hs("Taza", (0.45, 0.42, 0.36), rugosidad=0.3, suciedad=0.9, manchas=0.4, color_sucio=(0.22, 0.16, 0.10)),
    ]
    ob = mesa()
    for m in mats:
        ob.data.materials.append(m)
    hornear.atlas(ob, "MesaBaja", tam=1024)
    ruta = c.exportar_fbx("MesaBaja", [ob])
    print(f"Exportado {ruta} ({sum(len(p.vertices) - 2 for p in ob.data.polygons)} triángulos)")


if __name__ == "__main__":
    main()
