"""Baño viejo: váter con asiento de madera, lavabo de pie y bañera. Loza amarillenta y sucia.

Sustituyen a las mallas provisionales Vater, Lavabo y Banera de HouseBuilder con la misma huella
y orientación: frente a +Z en Unity (aquí, en Blender, a -Y), origen en el suelo en el centro.
- Vater: cisterna detrás (+Y de Blender), tapa levantada. 0,44 x 0,64 m, cisterna hasta 0,83 m.
- Lavabo: 0,60 x 0,46 m, borde a 0,80 m. El caño del grifo (el que gotea) acaba en local de Unity
  (0, 0,945, -0,055), como en la provisional.
- Banera: 0,76 x 1,70 m (larga en Z de Unity), borde a 0,52 m, grifo en el extremo +Z de Unity.

Uso:  python Tools/assets/bano.py [Vater|Lavabo|Banera]
Texturas CC0: Mueble_Wood092, Oxido_Rust004, Suciedad_SurfaceImperfections015.
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

LOZA, MADERA, METAL, OXIDO, AGUA, PINTURA = range(6)


def materiales():
    hs = hornear.material_sucio
    return [
        hs("Loza", (0.50, 0.46, 0.36), rugosidad=0.3, suciedad=1.0, polvo=0.4, manchas=0.5, escala_manchas=5,
           mugre=0.9, mugre_escala=0.4, color_sucio=(0.20, 0.15, 0.08), chorretones=0.45, semilla=1.0),
        hornear.madera_vieja("Madera", "marron", escala=0.4, veta=1.0, rugosidad=0.4, desgaste=0.6),
        hs("Metal", (0.27, 0.25, 0.21), rugosidad=0.3, metal=1.0, suciedad=0.9, manchas=0.5, mugre=0.6,
           color_sucio=(0.15, 0.11, 0.06)),
        hs("Oxido", (0.8, 0.8, 0.8), rugosidad=0.8, imagen=c.cc0("Oxido_Rust004"), escala=0.4, suciedad=0.6,
           color_sucio=(0.06, 0.04, 0.02)),
        hs("Agua", (0.10, 0.09, 0.06), rugosidad=0.1, suciedad=0.3, manchas=0.6, color_sucio=(0.05, 0.04, 0.02)),
        hs("Pintura", (0.10, 0.13, 0.11), rugosidad=0.5, suciedad=0.9, manchas=0.5, mugre=0.8, desgaste=0.5,
           color_desgaste=(0.25, 0.22, 0.17), color_sucio=(0.04, 0.035, 0.025), chorretones=0.5),
    ]


def torno_mat(bm, perfil, mat, lados=12, desde=(0, 0, 0), esc=(1, 1, 1)):
    c.marcar(bm)
    c.torno(bm, perfil, lados=lados)
    nv = c.nuevos(bm)
    bmesh.ops.scale(bm, vec=esc, verts=nv)
    bmesh.ops.translate(bm, vec=desde, verts=nv)
    c.asignar(bm, {f for v in nv for f in v.link_faces}, mat)
    return nv


def barra(bm, a, b, r, mat, lados=8):
    a, b = Vector(a), Vector(b)
    c.marcar(bm)
    bmesh.ops.create_cone(bm, cap_ends=True, segments=lados, radius1=r, radius2=r, depth=(b - a).length)
    nv = c.nuevos(bm)
    bmesh.ops.transform(bm, matrix=(b - a).to_track_quat("Z", "Y").to_matrix().to_4x4(), verts=nv)
    bmesh.ops.translate(bm, verts=nv, vec=(a + b) / 2)
    c.asignar(bm, {f for v in nv for f in v.link_faces}, mat)


def disco(bm, centro, r, alto, mat, lados=12, esc=(1, 1, 1), rot=None):
    c.marcar(bm)
    bmesh.ops.create_cone(bm, cap_ends=True, segments=lados, radius1=r, radius2=r, depth=alto)
    nv = c.nuevos(bm)
    bmesh.ops.scale(bm, vec=esc, verts=nv)
    if rot is not None:
        bmesh.ops.transform(bm, matrix=rot.to_4x4(), verts=nv)
    bmesh.ops.translate(bm, verts=nv, vec=centro)
    c.asignar(bm, {f for v in nv for f in v.link_faces}, mat)


def vater():
    bm = bmesh.new()
    oval = (1.0, 1.22, 1.0)
    # Pie y taza en una pieza: por fuera se estrecha y se abre; por dentro baja hasta el agua
    perfil = [(0.125, 0.0), (0.11, 0.06), (0.10, 0.18), (0.12, 0.27), (0.165, 0.35), (0.18, 0.395),
              (0.15, 0.40), (0.12, 0.34), (0.07, 0.27), (0.04, 0.23), (0.002, 0.23)]
    torno_mat(bm, perfil, LOZA, lados=12, desde=(0, -0.07, 0), esc=oval)
    disco(bm, (0, -0.05, 0.27), 0.085, 0.004, AGUA, esc=(1, 1.15, 1))
    # Repisa de loza detrás de la taza, donde apoya la cisterna (sin tocar el asiento)
    c.caja_mat(bm, (0, 0.25, 0.375), (0.30, 0.18, 0.05), LOZA, 0.012)
    c.caja_mat(bm, (0, 0.165, 0.185), (0.19, 0.27, 0.37), LOZA, 0.03, segmentos=2)
    # Asiento de madera (anillo) y tapa levantada; la bisagra queda delante de la cisterna
    torno_mat(bm, [(0.185, 0.0), (0.185, 0.022), (0.115, 0.022), (0.115, 0.0)], MADERA, lados=12,
              desde=(0, -0.07, 0.40), esc=oval)
    disco(bm, (0, 0.0, 0.0), 0.19, 0.02, MADERA, esc=oval)
    tapa = c.nuevos(bm)
    bmesh.ops.translate(bm, verts=tapa, vec=(0, 0.23, 0))           # la bisagra queda en el origen
    bmesh.ops.rotate(bm, verts=tapa, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(89.5), 3, "X"))
    bmesh.ops.translate(bm, verts=tapa, vec=(0, 0.152, 0.43))
    for s in (-1, 1):
        barra(bm, (s * 0.09, 0.152, 0.418), (s * 0.04, 0.152, 0.418), 0.008, METAL)
    # Cisterna (frente en y = 0.175, detrás de la tapa) con su tapa y pulsador
    c.caja_mat(bm, (0, 0.265, 0.605), (0.42, 0.18, 0.39), LOZA, 0.02)
    c.caja_mat(bm, (0, 0.265, 0.815), (0.44, 0.20, 0.03), LOZA, 0.012)
    disco(bm, (0, 0.265, 0.835), 0.022, 0.012, METAL, lados=8)
    # Tubo de desagüe oxidado hacia la pared y llave de paso
    barra(bm, (0, 0.20, 0.14), (0, 0.44, 0.14), 0.045, OXIDO, lados=10)
    disco(bm, (0, 0.44, 0.14), 0.06, 0.02, OXIDO, lados=10, rot=Matrix.Rotation(math.radians(90), 3, "X"))
    barra(bm, (0.17, 0.30, 0.48), (0.17, 0.44, 0.30), 0.008, METAL)
    return bm


def lavabo():
    bm = bmesh.new()
    # Pila: bloque de loza redondeado con la cubeta vaciada (booleana) y la repisa de los grifos detrás
    pila = bmesh.new()
    r = bmesh.ops.create_cube(pila, size=2.0)
    bmesh.ops.subdivide_edges(pila, edges=list({e for v in r["verts"] for e in v.link_edges}), cuts=4,
                              use_grid_fill=True)
    n = 3.2
    for v in pila.verts:
        p = Vector(v.co)
        norma = (abs(p.x) ** n + abs(p.y) ** n + abs(p.z) ** n) ** (1 / n)
        q = p / max(norma, 1e-6) * max(abs(p.x), abs(p.y), abs(p.z))
        if q.y > 0:
            q.y = min(1.0, q.y * 1.4)       # la parte de atrás, recta contra la pared
        v.co = Vector((q.x * 0.30, q.y * 0.23, q.z * 0.085))
    bmesh.ops.translate(pila, verts=pila.verts, vec=(0, 0, 0.73))
    me = bpy.data.meshes.new("pila"); pila.to_mesh(me); pila.free()
    ob = bpy.data.objects.new("pila", me); bpy.context.scene.collection.objects.link(ob)
    cubeta = bmesh.new()
    bmesh.ops.create_uvsphere(cubeta, u_segments=20, v_segments=12, radius=1.0)
    for v in cubeta.verts:
        v.co = Vector((v.co.x * 0.235, v.co.y * 0.165 - 0.04, v.co.z * 0.13 + 0.825))
    mc = bpy.data.meshes.new("cubeta"); cubeta.to_mesh(mc); cubeta.free()
    oc = bpy.data.objects.new("cubeta", mc); bpy.context.scene.collection.objects.link(oc)
    mod = ob.modifiers.new("hueco", "BOOLEAN"); mod.operation = "DIFFERENCE"; mod.object = oc; mod.solver = "EXACT"
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.modifier_apply(modifier="hueco")
    bpy.data.objects.remove(oc)
    for poly in ob.data.polygons:
        poly.material_index = LOZA
    bm.from_mesh(ob.data)
    bpy.data.objects.remove(ob)
    # Pie: ancho abajo, se estrecha y se abre arriba hasta tocar la pila
    torno_mat(bm, [(0.13, 0.0), (0.12, 0.03), (0.095, 0.10), (0.08, 0.35), (0.085, 0.55), (0.12, 0.64),
                   (0.14, 0.66), (0.002, 0.66)], LOZA, lados=14, desde=(0, 0.05, 0), esc=(1.0, 0.8, 1.0))
    disco(bm, (0, -0.04, 0.697), 0.02, 0.004, METAL, lados=8)                    # desagüe
    # Grifo: caño (el que gotea, acaba en (0, 0.055, 0.945)) y dos llaves de cruceta en la repisa
    barra(bm, (0, 0.17, 0.80), (0, 0.17, 0.95), 0.014, METAL)
    barra(bm, (0, 0.175, 0.945), (0, 0.055, 0.945), 0.011, METAL)
    disco(bm, (0, 0.06, 0.935), 0.013, 0.02, METAL, lados=8)
    for s in (-1, 1):
        x = s * 0.15
        barra(bm, (x, 0.17, 0.80), (x, 0.17, 0.86), 0.012, METAL)
        barra(bm, (x - 0.03, 0.17, 0.87), (x + 0.03, 0.17, 0.87), 0.006, METAL, lados=6)
        barra(bm, (x, 0.14, 0.87), (x, 0.20, 0.87), 0.006, METAL, lados=6)
        disco(bm, (x, 0.17, 0.88), 0.008, 0.012, LOZA if s > 0 else OXIDO, lados=6)
    # Sifón oxidado que sale por detrás del pie hacia la pared
    barra(bm, (0, 0.10, 0.62), (0, 0.10, 0.50), 0.018, OXIDO)
    barra(bm, (0, 0.10, 0.50), (0, 0.24, 0.50), 0.018, OXIDO)
    return bm


def anillo_tina(a, b, z, lados=36, n=3.0):
    """Puntos de un superóvalo de semiejes a (x) y b (y) a la altura z."""
    pts = []
    for i in range(lados):
        t = 2 * math.pi * i / lados
        ct, st = math.cos(t), math.sin(t)
        x = a * math.copysign(abs(ct) ** (2 / n), ct)
        y = b * math.copysign(abs(st) ** (2 / n), st)
        pts.append((x, y, z))
    return pts


def banera():
    """Bañera exenta de hierro esmaltado con patas de garra, borde enrollado y grifo de teléfono."""
    bm = bmesh.new()
    A, B = 0.38, 0.85
    # (escala, altura, material): por fuera pintada, el borde y el interior esmaltados
    perfil = [(0.86, 0.14, PINTURA), (0.93, 0.22, PINTURA), (0.98, 0.42, PINTURA), (1.0, 0.56, PINTURA),
              (1.02, 0.585, LOZA), (1.0, 0.60, LOZA), (0.95, 0.598, LOZA), (0.92, 0.56, LOZA),
              (0.88, 0.35, LOZA), (0.82, 0.22, LOZA), (0.74, 0.19, LOZA)]
    anillos = []
    for k, z, _ in perfil:
        anillos.append([bm.verts.new(p) for p in anillo_tina(A * k, B * k, z)])
    for idx, (a, b) in enumerate(zip(anillos, anillos[1:])):
        mat = perfil[idx][2] if perfil[idx + 1][2] == perfil[idx][2] else LOZA
        for i in range(len(a)):
            j = (i + 1) % len(a)
            f = bm.faces.new((a[i], a[j], b[j], b[i]))
            f.material_index = mat
    f = bm.faces.new(list(reversed(anillos[0]))); f.material_index = PINTURA
    f = bm.faces.new(anillos[-1]); f.material_index = LOZA
    # Patas de garra
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * 0.25, sy * 0.62
            c.marcar(bm)
            c.torno(bm, [(0.035, 0.0), (0.045, 0.02), (0.03, 0.05), (0.022, 0.10), (0.04, 0.15), (0.002, 0.16)],
                    lados=8, desde=(x, y, 0))
            nv = c.nuevos(bm)
            bmesh.ops.scale(bm, vec=(1.0, 1.3, 1.0), verts=nv)
            bmesh.ops.translate(bm, vec=(0, y * -0.3, 0), verts=nv)       # vuelve a su sitio tras escalar
            c.asignar(bm, {f for v in nv for f in v.link_faces}, PINTURA)
    # Desagüe, rebosadero y cadena del tapón
    yd = -B + 0.20
    disco(bm, (0, yd, 0.195), 0.025, 0.004, METAL, lados=8)
    disco(bm, (0, -B * 0.92 + 0.02, 0.50), 0.025, 0.008, METAL, lados=8,
          rot=Matrix.Rotation(math.radians(70), 3, "X"))
    for i in range(8):
        disco(bm, (0.03, yd + i * 0.012, 0.21 + i * 0.035), 0.004, 0.008, METAL, lados=6)
    # Grifo de teléfono en el extremo -Y (+Z de Unity): dos patas, cuerpo, caño y la ducha en su horquilla
    yg = -B * 1.0 + 0.04
    for s in (-1, 1):
        barra(bm, (s * 0.09, yg, 0.60), (s * 0.09, yg, 0.72), 0.012, METAL)
        barra(bm, (s * 0.09 - 0.03, yg, 0.76), (s * 0.09 + 0.03, yg, 0.76), 0.006, METAL, lados=6)
        barra(bm, (s * 0.09, yg - 0.03, 0.76), (s * 0.09, yg + 0.03, 0.76), 0.006, METAL, lados=6)
    barra(bm, (-0.11, yg, 0.72), (0.11, yg, 0.72), 0.016, METAL)
    barra(bm, (0, yg, 0.72), (0, yg + 0.10, 0.70), 0.012, METAL)
    barra(bm, (0, yg + 0.10, 0.70), (0, yg + 0.12, 0.64), 0.01, METAL)
    barra(bm, (-0.06, yg, 0.72), (-0.06, yg, 0.80), 0.01, METAL)
    barra(bm, (-0.10, yg, 0.84), (-0.02, yg, 0.84), 0.016, METAL)                 # ducha de teléfono
    disco(bm, (-0.10, yg, 0.84), 0.025, 0.02, METAL, lados=10, rot=Matrix.Rotation(math.radians(90), 3, "Y"))
    # Mancha de óxido bajo el caño
    disco(bm, (0, yg + 0.14, 0.27), 0.05, 0.002, OXIDO, lados=10, esc=(0.7, 1.4, 1),
          rot=Matrix.Rotation(math.radians(-40), 3, "X"))
    return bm


PIEZAS = {"Vater": vater, "Lavabo": lavabo, "Banera": banera}


def main(nombre):
    c.escena_vacia()
    mats = materiales()
    bm = PIEZAS[nombre]()
    ob = c.objeto(nombre, bm, mats)
    for p in ob.data.polygons:
        p.use_smooth = p.material_index in (LOZA, METAL, OXIDO, PINTURA) and len(p.vertices) == 4
    hornear.atlas(ob, nombre, tam=1024, margen=0.003)
    ruta = c.exportar_fbx(nombre, [ob])
    print(f"Exportado {ruta} ({sum(len(p.vertices) - 2 for p in ob.data.polygons)} triángulos)")


if __name__ == "__main__":
    for n in (sys.argv[1:] or list(PIEZAS)):
        main(n)
