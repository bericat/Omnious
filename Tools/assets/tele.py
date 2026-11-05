"""Tele de tubo de los 90 sobre su mueble, con un vídeo VHS en el hueco. Vieja y con polvo.

Sustituye a la malla provisional Tele de SalonBuilder/HouseBuilder y mantiene su huella:
mueble de 1,2 x 0,46 x 0,5 m y tele encima. En este FBX el frente mira a +Z en Unity, como
todos los modelos: en el salón se coloca girada 180° (la provisional tenía el frente a -Z).

Dos objetos: "Tele" (todo, con la textura horneada Texturas/Tele.jpg) y "Pantalla"
(el cristal de la pantalla, material Tele_Pantalla aparte, para encenderla y hacer parpadear
la luz desde Unity). Centro de la pantalla en local (0, 0,79, 0,245) de Unity.

Uso:  python Tools/assets/tele.py
Texturas CC0: Mueble_Wood092, Suciedad_SurfaceImperfections015.
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

MADERA, PLASTICO, NEGRO, METAL, PANTALLA = range(5)
# Blender: frente a -Y


def caja(bm, centro, tam, mat, biselado=0.004, segmentos=2):
    c.marcar(bm)
    vs = c.caja(bm, (0, 0, 0), tam)
    if biselado:
        bmesh.ops.bevel(bm, geom=list({e for v in vs for e in v.link_edges}), offset=biselado,
                        segments=segmentos, profile=0.5, affect="EDGES", clamp_overlap=True)
    nuevos = c.nuevos(bm)
    bmesh.ops.translate(bm, vec=centro, verts=nuevos)
    c.asignar(bm, {f for v in nuevos for f in v.link_faces}, mat)
    return nuevos


def mueble(bm):
    # Mueble bajo: costados, techo, base, trasera y una balda; hueco abierto delante
    W, D, H = 1.2, 0.46, 0.50
    g = 0.022
    caja(bm, (0, 0, 0.03), (W - 0.04, D - 0.04, 0.06), MADERA, 0.002)          # zócalo
    caja(bm, (0, 0, 0.06 + g / 2), (W, D, g), MADERA)                            # base
    caja(bm, (0, 0, H - g / 2), (W + 0.02, D + 0.02, g), MADERA, 0.006, 3)       # tapa
    for s in (-1, 1):
        caja(bm, (s * (W / 2 - g / 2), 0, (0.06 + H) / 2), (g, D, H - 0.06), MADERA)
    caja(bm, (0, D / 2 - 0.005, (0.06 + H) / 2), (W - 2 * g, 0.01, H - 0.06), MADERA, 0)
    caja(bm, (0, 0.01, 0.27), (W - 2 * g, D - 0.03, 0.018), MADERA)              # balda
    caja(bm, (0.30, 0.0, (0.06 + H) / 2), (0.018, D - 0.03, H - 0.08), MADERA)   # separación
    # Vídeo VHS en el hueco de arriba a la izquierda (x de Blender positiva = izquierda en Unity)
    caja(bm, (-0.15, 0.0, 0.28 + 0.045), (0.43, 0.30, 0.085), NEGRO, 0.006)
    caja(bm, (-0.15, -0.151, 0.335), (0.20, 0.004, 0.022), NEGRO, 0)
    caja(bm, (-0.27, -0.151, 0.31), (0.06, 0.004, 0.012), METAL, 0)
    # Cintas apiladas abajo
    for i in range(3):
        caja(bm, (-0.05 + i * 0.012, 0.03, 0.093 + i * 0.026), (0.19, 0.105, 0.025), NEGRO, 0.003)
    # Revistas a la derecha
    caja(bm, (0.44, 0.0, 0.10), (0.24, 0.30, 0.04), PLASTICO, 0.002)


def televisor(bm):
    """Caja de tubo: marco delantero redondeado, culata en pirámide, botones y rejilla del altavoz."""
    z0 = 0.50
    W, H = 0.70, 0.54
    # Marco delantero
    caja(bm, (0, -0.19, z0 + H / 2), (W, 0.10, H), PLASTICO, 0.025, 3)
    # Culata: tronco de pirámide hacia atrás
    c.marcar(bm)
    a = [bm.verts.new((sx * W * 0.47, -0.14, z0 + 0.02 + (sz + 1) / 2 * (H - 0.04))) for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    b = [bm.verts.new((sx * 0.20, 0.24, z0 + 0.06 + (sz + 1) / 2 * 0.30)) for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new((a[i], a[j], b[j], b[i]))
    bm.faces.new(list(reversed(b)))
    c.asignar(bm, {f for v in c.nuevos(bm) for f in v.link_faces}, PLASTICO)
    # Hueco de la pantalla (marco interior oscuro)
    caja(bm, (0, -0.242, z0 + 0.29), (0.58, 0.01, 0.43), NEGRO, 0.02, 3)
    # Botones, piloto y rejilla bajo la pantalla
    for i in range(4):
        caja(bm, (0.12 + i * 0.045, -0.246, z0 + 0.04), (0.03, 0.012, 0.016), NEGRO, 0.003)
    caja(bm, (-0.25, -0.246, z0 + 0.04), (0.012, 0.01, 0.012), METAL, 0.002)
    for i in range(6):
        caja(bm, (-0.10 + i * 0.008 - 0.02, -0.2405, z0 + 0.04), (0.003, 0.004, 0.03), NEGRO, 0)
    # Patas pequeñas y antena de cuernos
    for s in (-1, 1):
        caja(bm, (s * 0.25, -0.05, z0 - 0.005), (0.05, 0.05, 0.012), NEGRO, 0.004)
    caja(bm, (0, -0.05, z0 + 0.50), (0.10, 0.07, 0.04), NEGRO, 0.01)
    for s in (-1, 1):
        c.marcar(bm)
        r = bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=0.004, radius2=0.002, depth=0.40)
        nuevos = c.nuevos(bm)
        bmesh.ops.rotate(bm, verts=nuevos, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(s * 30), 3, "Y"))
        bmesh.ops.translate(bm, verts=nuevos, vec=(s * 0.10, -0.05, z0 + 0.68))
        c.asignar(bm, {f for v in nuevos for f in v.link_faces}, METAL)


def pantalla(mat):
    """Cristal abombado del tubo."""
    bm = bmesh.new()
    r = bmesh.ops.create_grid(bm, x_segments=12, y_segments=10, size=0.5)
    for v in r["verts"]:
        x, y = v.co.x, v.co.y  # -0.5..0.5
        bulto = (1 - (2 * x) ** 2) * (1 - (2 * y) ** 2)
        v.co = Vector((x * 0.55, -0.248 - 0.018 * bulto, 0.79 + y * 0.40))
    for f in bm.faces:
        f.material_index = 0
    ob = c.objeto("Pantalla", bm, [mat], suave=True)
    # UV 0..1 para poder poner una imagen en la pantalla
    me = ob.data
    for p in me.polygons:
        for li in p.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            me.uv_layers.active.data[li].uv = (0.5 - co.x / 0.55, (co.z - 0.79) / 0.40 + 0.5)
    return ob


def main():
    c.escena_vacia()
    hs = hornear.material_sucio
    mats = [
        hs("Madera", (0.30, 0.20, 0.13), rugosidad=0.5, imagen=c.cc0("Mueble_Wood092"), escala=1.0,
           suciedad=0.9, polvo=0.3, manchas=0.2, desgaste=0.4, color_desgaste=(0.40, 0.30, 0.20),
           color_sucio=(0.08, 0.06, 0.04), mugre=0.4),
        hs("Plastico", (0.10, 0.10, 0.10), rugosidad=0.45, suciedad=0.6, polvo=0.1, manchas=0.3,
           color_sucio=(0.13, 0.12, 0.10), mugre=0.5, mugre_escala=0.5),
        hs("Negro", (0.025, 0.025, 0.025), rugosidad=0.5, suciedad=0.4, manchas=0.2, color_sucio=(0.15, 0.13, 0.11)),
        hs("Metal", (0.5, 0.5, 0.5), rugosidad=0.3, metal=1.0, suciedad=0.5),
    ]
    vidrio = hornear.material_liso("Tele_Pantalla", (0.035, 0.04, 0.04), rugosidad=0.08)
    bm = bmesh.new()
    mueble(bm)
    televisor(bm)
    ob = c.objeto("Tele", bm, mats)
    hornear.atlas(ob, "Tele", tam=2048)
    pan = pantalla(vidrio)
    ruta = c.exportar_fbx("Tele", [ob, pan])
    tris = sum(len(p.vertices) - 2 for o in (ob, pan) for p in o.data.polygons)
    print(f"Exportado {ruta} ({tris} triángulos)")


if __name__ == "__main__":
    main()
