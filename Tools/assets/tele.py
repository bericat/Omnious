"""Tele de los 70-80 con caja de chapa de madera, frontal gris y mandos de rueda, sobre un banco
bajo de madera con balda (vídeo VHS, cintas y libros abajo). Vieja y con polvo.

Sustituye a la malla provisional Tele de SalonBuilder/HouseBuilder y mantiene su huella:
mueble de 1,2 x 0,46 x 0,5 m y tele encima. En este FBX el frente mira a +Z en Unity, como
todos los modelos: en el salón se coloca girada 180° (la provisional tenía el frente a -Z).

Dos objetos: "TeleMueble" (todo, con la textura horneada Texturas/Tele.jpg) y "Pantalla"
(el cristal de la pantalla, material Tele_Pantalla aparte, para encenderla y hacer parpadear
la luz desde Unity). Centro de la pantalla en local (0, 0,815, 0,24) de Unity; mide 0,44 x 0,32 m.

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

MADERA, CHAPA, FRONTAL, NEGRO, METAL, PAPEL = range(6)
LIBROS = (6, 7, 8)
# Blender: frente a -Y
Z_TV = 0.525           # base de la caja de la tele (encima del zócalo)
PANT = (0.815, 0.44, 0.32)  # centro (altura) y tamaño de la pantalla


def caja(bm, centro, tam, mat, biselado=0.004, segmentos=1):
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
    """Banco bajo: tablero, faldones, cuatro patas y balda abajo con el vídeo, cintas y libros."""
    W, D, H = 1.2, 0.46, 0.50
    caja(bm, (0, 0, H - 0.0175), (W, D, 0.035), MADERA, 0.005)
    for y in (-D / 2 + 0.03, D / 2 - 0.03):
        caja(bm, (0, y, H - 0.065), (W - 0.10, 0.022, 0.06), MADERA, 0.002)
    for x in (-W / 2 + 0.04, W / 2 - 0.04):
        caja(bm, (x, 0, H - 0.065), (0.022, D - 0.10, 0.06), MADERA, 0.002)
        for y in (-D / 2 + 0.04, D / 2 - 0.04):
            caja(bm, (x, y, (H - 0.035) / 2), (0.05, 0.05, H - 0.035), MADERA, 0.004)
    caja(bm, (0, 0, 0.10), (W - 0.06, D - 0.06, 0.02), MADERA, 0.003)       # balda
    # Vídeo VHS en la balda (x de Blender positiva = izquierda en Unity)
    caja(bm, (-0.22, -0.01, 0.11 + 0.045), (0.43, 0.30, 0.085), NEGRO, 0.005)
    caja(bm, (-0.22, -0.161, 0.165), (0.20, 0.004, 0.022), NEGRO, 0)
    caja(bm, (-0.34, -0.161, 0.14), (0.06, 0.004, 0.012), METAL, 0)
    for i in range(3):
        caja(bm, (0.12 + i * 0.01, 0.0, 0.123 + i * 0.026), (0.19, 0.105, 0.025), NEGRO, 0.003)
    # Libros tumbados a la derecha
    alto = 0.11
    for i, (g, l) in enumerate(((0.035, 0.24), (0.03, 0.22), (0.045, 0.25))):
        caja(bm, (0.40 + i * 0.006, 0.0, alto + g / 2), (l, 0.17, g), LIBROS[i], 0.003)
        alto += g


def boton(bm, x, z, r, largo, mat):
    """Mando de rueda que sale del frente."""
    c.marcar(bm)
    bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=r, radius2=r * 0.85, depth=largo)
    nuevos = c.nuevos(bm)
    bmesh.ops.rotate(bm, verts=nuevos, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, "X"))
    bmesh.ops.translate(bm, verts=nuevos, vec=(x, -0.232 - largo / 2, z))
    c.asignar(bm, {f for v in nuevos for f in v.link_faces}, mat)


def televisor(bm):
    """Caja de chapa de madera, frontal de plástico gris, panel de mandos y antena de cuernos."""
    z0 = Z_TV
    W, H, y0, y1 = 0.62, 0.48, -0.21, 0.17
    caja(bm, (0, -0.02, z0 - 0.0125), (0.54, 0.30, 0.025), NEGRO, 0.004)          # zócalo
    caja(bm, (0, (y0 + y1) / 2, z0 + H / 2), (W, y1 - y0, H), CHAPA, 0.008)       # caja de madera
    caja(bm, (0, y1 + 0.03, z0 + 0.24), (0.42, 0.06, 0.34), NEGRO, 0.01)          # tapa trasera
    caja(bm, (0, y0 - 0.006, z0 + H / 2), (W - 0.03, 0.014, H - 0.03), FRONTAL, 0.006)  # marco gris
    zc, pw, ph = PANT
    caja(bm, (0, y0 - 0.014, zc), (pw + 0.04, 0.006, ph + 0.04), NEGRO, 0.004)   # hueco de la pantalla
    # Panel de mandos bajo la pantalla
    zp = z0 + 0.065
    caja(bm, (0, y0 - 0.016, zp), (W - 0.09, 0.006, 0.075), NEGRO, 0.002)
    for x in (0.20, 0.145):
        boton(bm, x, zp, 0.019, 0.018, METAL)
    for x in (-0.06, -0.20):
        boton(bm, x, zp, 0.022, 0.02, METAL)
    for i in range(3):
        caja(bm, (0.03 - i * 0.025, -0.234, zp), (0.012, 0.006, 0.02), METAL, 0.001)
    caja(bm, (0.08, -0.232, zp + 0.012), (0.04, 0.004, 0.012), PAPEL, 0)          # rótulo del canal
    # Antena de cuernos sobre su peana
    c.marcar(bm)
    c.torno(bm, [(0.065, 0), (0.06, 0.012), (0.02, 0.022), (0.012, 0.03), (0.002, 0.03)], lados=16,
            desde=(0.0, -0.02, z0 + H))
    c.asignar(bm, {f for v in c.nuevos(bm) for f in v.link_faces}, METAL)
    for s, ang in ((-1, 28), (1, 40)):
        c.marcar(bm)
        bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=0.004, radius2=0.002, depth=0.45)
        nuevos = c.nuevos(bm)
        bmesh.ops.translate(bm, verts=nuevos, vec=(0, 0, 0.225))
        bmesh.ops.rotate(bm, verts=nuevos, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(s * ang), 3, "Y"))
        bmesh.ops.translate(bm, verts=nuevos, vec=(0, -0.02, z0 + H + 0.03))
        c.asignar(bm, {f for v in nuevos for f in v.link_faces}, METAL)


def pantalla(mat):
    """Cristal abombado del tubo."""
    bm = bmesh.new()
    r = bmesh.ops.create_grid(bm, x_segments=12, y_segments=10, size=0.5)
    zc, pw, ph = PANT
    for v in r["verts"]:
        x, y = v.co.x, v.co.y  # -0.5..0.5
        bulto = (1 - (2 * x) ** 2) * (1 - (2 * y) ** 2)
        v.co = Vector((x * pw, -0.226 - 0.014 * bulto, zc + y * ph))
    for f in bm.faces:
        f.material_index = 0
    ob = c.objeto("Pantalla", bm, [mat], suave=True)
    # UV 0..1 para poder poner una imagen en la pantalla
    me = ob.data
    for p in me.polygons:
        for li in p.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            me.uv_layers.active.data[li].uv = (0.5 - co.x / pw, (co.z - zc) / ph + 0.5)
    return ob


def main():
    c.escena_vacia()
    hs = hornear.material_sucio
    mats = [
        hornear.madera_vieja("Madera", (0.25, 0.19, 0.13), desgaste=0.6, manchas=0.4),
        hornear.madera_vieja("Chapa", "marron", escala=0.5, veta=1.1, rugosidad=0.45, desgaste=0.3, polvo=0.2,
                             semilla=2.0),
        hornear.plastico_viejo("Frontal", (0.45, 0.44, 0.40)),
        hs("Negro", (0.03, 0.03, 0.03), rugosidad=0.5, suciedad=0.5, manchas=0.2, color_sucio=(0.14, 0.12, 0.10)),
        hs("Metal", (0.42, 0.41, 0.38), rugosidad=0.35, metal=1.0, suciedad=0.7, manchas=0.3),
        hs("Papel", (0.55, 0.50, 0.40), rugosidad=0.8, suciedad=0.5),
    ]
    for i, col in enumerate(((0.30, 0.10, 0.07), (0.12, 0.17, 0.22), (0.35, 0.30, 0.20))):
        mats.append(hs(f"Libro{i}", col, rugosidad=0.7, suciedad=0.9, manchas=0.4, escala_manchas=15, semilla=i))
    vidrio = hornear.material_liso("Tele_Pantalla", (0.035, 0.04, 0.04), rugosidad=0.08)
    bm = bmesh.new()
    mueble(bm)
    televisor(bm)
    ob = c.objeto("TeleMueble", bm, mats)  # "Tele" es la raíz en Unity (GameObject.Find)
    hornear.atlas(ob, "Tele", tam=2048)
    pan = pantalla(vidrio)
    ruta = c.exportar_fbx("Tele", [ob, pan])
    tris = sum(len(p.vertices) - 2 for o in (ob, pan) for p in o.data.polygons)
    print(f"Exportado {ruta} ({tris} triángulos)")


if __name__ == "__main__":
    main()
