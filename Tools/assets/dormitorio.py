"""Dormitorio viejo: cama de madera con colcha, mesillas (una con lamparita), cómoda y el armario
del fondo falso. Madera oscura gastada, telas apagadas y sucias.

Sustituyen a las mallas provisionales de HouseBuilder con la misma huella y orientación (frente a +Z
en Unity; aquí, en Blender, a -Y), origen en el suelo en el centro. x de Unity = -x de Blender.
- Cama: 1,5 x 2,0 m; el cabecero está en +Z de Unity (como la provisional), colchón a 0,49 m.
- Mesilla / MesillaLampara: 0,45 x 0,54 x 0,40 m, cajón delante. La lamparita tiene "Bombilla" aparte.
- Comoda: 0,95 x 0,76 x 0,42 m, tres cajones.
- Armario: 1,4 x 2,1 x 0,58 m, hueco por dentro (se entra). Cuatro objetos, como las piezas de ahora:
  "ArmarioCuerpo"; "ArmarioHojaIzq" con su origen en la bisagra (-0,68, 0,02, 0,295) de Unity;
  "ArmarioHojaDer" en (0,68, 0,02, 0,295); "ArmarioFondo" en (-0,68, 0, -0,28). Las hojas y el fondo
  tienen la misma forma que las provisionales para que SimpleHinge siga igual.

Uso:  python Tools/assets/dormitorio.py [Cama|Mesilla|MesillaLampara|Comoda|Armario]
Texturas CC0: Mueble_Wood092, Tapiceria_Fabric080, Tapiceria_Fabric083, Suciedad_SurfaceImperfections015.
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

MADERA, PUERTA, METAL, SABANA, COLCHA, ALMOHADA, PANTALLA, LATON = range(8)


def materiales():
    hs = hornear.material_sucio
    mv = hornear.madera_vieja
    return [
        mv("Madera", "oscura", desgaste=0.6),
        mv("Puerta", (0.24, 0.16, 0.10), escala=0.6, desgaste=0.15, semilla=3.0),
        hs("Metal", (0.42, 0.40, 0.36), rugosidad=0.35, metal=1.0, suciedad=0.8, manchas=0.4),
        hs("Sabana", (0.45, 0.42, 0.35), rugosidad=0.9, suciedad=0.7, manchas=0.6, escala_manchas=4, mugre=0.6,
           color_sucio=(0.20, 0.16, 0.10), polvo=0.0),
        hs("Colcha", (0.22, 0.14, 0.10), rugosidad=0.95, imagen=c.cc0("Tapiceria_Fabric080"), escala=0.5, veta=1.1,
           suciedad=0.6, manchas=0.5, mugre=0.7, color_sucio=(0.08, 0.06, 0.04), polvo=0.0),
        hs("Almohada", (0.42, 0.40, 0.33), rugosidad=0.9, imagen=c.cc0("Tapiceria_Fabric083"), escala=0.3,
           veta=0.6, suciedad=0.6, manchas=0.7, color_sucio=(0.22, 0.17, 0.10), polvo=0.0),
        hs("Pantalla", (0.40, 0.30, 0.18), rugosidad=0.9, imagen=c.cc0("Tapiceria_Fabric083"), escala=0.2,
           veta=0.8, suciedad=0.7, manchas=0.5, polvo=0.3),
        hs("Laton", (0.36, 0.27, 0.12), rugosidad=0.35, metal=1.0, suciedad=0.7, manchas=0.4, desgaste=0.3,
           color_desgaste=(0.55, 0.45, 0.25)),
    ]


def cojin(bm, centro, tam, mat, n=4.0, abombado=0.02, rot=None):
    """Caja de esquinas redondeadas (superelipsoide), algo abombada."""
    c.marcar(bm)
    r = bmesh.ops.create_cube(bm, size=2.0)
    bmesh.ops.subdivide_edges(bm, edges=list({e for v in r["verts"] for e in v.link_edges}), cuts=5,
                              use_grid_fill=True)
    nv = c.nuevos(bm)
    fino = min(range(3), key=lambda i: tam[i])
    for v in nv:
        p = Vector(v.co)
        norma = (abs(p.x) ** n + abs(p.y) ** n + abs(p.z) ** n) ** (1 / n)
        q = p / max(norma, 1e-6) * max(abs(p.x), abs(p.y), abs(p.z))
        otros = [i for i in range(3) if i != fino]
        q[fino] *= 1 + abombado / max(1e-3, tam[fino]) * (1 - q[otros[0]] ** 2) * (1 - q[otros[1]] ** 2)
        v.co = Vector((q.x * tam[0] / 2, q.y * tam[1] / 2, q.z * tam[2] / 2))
    if rot is not None:
        bmesh.ops.transform(bm, matrix=rot.to_4x4(), verts=nv)
    bmesh.ops.translate(bm, vec=centro, verts=nv)
    c.asignar(bm, {f for v in nv for f in v.link_faces}, mat)


def cil(bm, centro, r, alto, mat, lados=12, r2=None):
    c.marcar(bm)
    bmesh.ops.create_cone(bm, cap_ends=True, segments=lados, radius1=r, radius2=r if r2 is None else r2, depth=alto)
    nv = c.nuevos(bm)
    bmesh.ops.translate(bm, verts=nv, vec=centro)
    c.asignar(bm, {f for v in nv for f in v.link_faces}, mat)


def cama():
    bm = bmesh.new()
    cm = c.caja_mat
    W, L = 1.5, 2.0
    # Bastidor, patas, cabecero (en -Y de Blender = +Z de Unity) y piecero bajo
    cm(bm, (0, 0, 0.17), (W, L, 0.22), MADERA, 0.006)
    for x in (-0.7, 0.7):
        for y in (-0.95, 0.95):
            cm(bm, (x, y, 0.03), (0.07, 0.07, 0.06), MADERA, 0.004)
    cm(bm, (0, -1.0, 0.55), (W, 0.05, 1.10), MADERA, 0.008)
    cm(bm, (0, -1.0, 1.11), (W + 0.06, 0.08, 0.04), MADERA, 0.008)
    for k in range(4):
        cm(bm, (-0.54 + k * 0.36, -0.966, 0.72), (0.26, 0.02, 0.50), PUERTA, 0.004)   # cuarterones (hacia el colchón)
    cm(bm, (0, 1.0, 0.36), (W, 0.05, 0.36), MADERA, 0.006)
    # Colchón con la sábana, colcha que cae por los lados y almohadas
    cojin(bm, (0, 0, 0.38), (1.44, 1.94, 0.20), SABANA, n=6, abombado=0.01)
    cm(bm, (0, 0.2, 0.495), (1.52, 1.56, 0.04), COLCHA, 0.01)
    for s in (-1, 1):
        cm(bm, (s * 0.765, 0.2, 0.34), (0.025, 1.56, 0.30), COLCHA, 0.005)
    cm(bm, (0, 0.985, 0.34), (1.55, 0.025, 0.30), COLCHA, 0.005)
    cm(bm, (0, -0.52, 0.52), (1.50, 0.18, 0.06), COLCHA, 0.02)        # embozo doblado
    for x, rz in ((0.36, 4), (-0.36, -6)):
        cojin(bm, (x, -0.76, 0.56), (0.62, 0.42, 0.13), ALMOHADA, n=3, abombado=0.06,
              rot=Matrix.Rotation(math.radians(rz), 3, "Z") @ Matrix.Rotation(math.radians(-8), 3, "X"))
    return bm


def mesilla(lampara):
    bm = bmesh.new()
    cm = c.caja_mat
    cm(bm, (0, 0, 0.30), (0.45, 0.40, 0.50), MADERA, 0.004)
    cm(bm, (0, -0.01, 0.555), (0.48, 0.43, 0.025), MADERA, 0.006)
    cm(bm, (0, -0.208, 0.43), (0.40, 0.016, 0.14), PUERTA, 0.004)
    cm(bm, (0, -0.208, 0.21), (0.40, 0.016, 0.26), PUERTA, 0.004)
    cil(bm, (0, -0.222, 0.43), 0.014, 0.02, LATON, lados=8)
    cm(bm, (0.15, -0.222, 0.21), (0.014, 0.012, 0.08), LATON, 0.002)
    for x in (-0.2, 0.2):
        for y in (-0.17, 0.17):
            cm(bm, (x, y, 0.025), (0.04, 0.04, 0.05), MADERA, 0.004)
    if lampara:
        c.marcar(bm)
        c.torno(bm, [(0.07, 0.0), (0.07, 0.015), (0.03, 0.03), (0.012, 0.05), (0.012, 0.20), (0.02, 0.21),
                     (0.002, 0.21)], lados=12, desde=(0.05, 0.02, 0.5675))
        c.asignar(bm, {f for v in c.nuevos(bm) for f in v.link_faces}, LATON)
        c.marcar(bm)
        c.torno(bm, [(0.13, 0.0), (0.075, 0.15), (0.072, 0.15), (0.127, 0.0)], lados=16, desde=(0.05, 0.02, 0.73))
        c.asignar(bm, {f for v in c.nuevos(bm) for f in v.link_faces}, PANTALLA)
        cm(bm, (-0.10, -0.05, 0.585), (0.16, 0.22, 0.03), SABANA, 0.003)   # libro
    else:
        cil(bm, (-0.08, 0.0, 0.62), 0.035, 0.11, SABANA, lados=10)       # vaso
    return bm


def comoda():
    bm = bmesh.new()
    cm = c.caja_mat
    cm(bm, (0, 0, 0.40), (0.95, 0.42, 0.70), MADERA, 0.004)
    cm(bm, (0, -0.01, 0.765), (0.99, 0.45, 0.03), MADERA, 0.008)
    cm(bm, (0, -0.005, 0.025), (0.97, 0.43, 0.05), MADERA, 0.006)
    for i in range(3):
        z = 0.17 + i * 0.205
        cm(bm, (0, -0.215, z), (0.87, 0.016, 0.19), PUERTA, 0.004)
        for s in (-1, 1):
            cil(bm, (s * 0.25, -0.228, z), 0.016, 0.02, LATON, lados=8)
    # Encima: un pañito y un marco caído
    cm(bm, (0.0, -0.02, 0.783), (0.40, 0.25, 0.004), SABANA, 0)
    cm(bm, (-0.28, 0.05, 0.79), (0.18, 0.13, 0.012), LATON, 0.002)
    return bm


def armario():
    """Devuelve un bmesh por pieza: cuerpo, hoja izquierda, hoja derecha y fondo (en sus pivotes)."""
    cm = c.caja_mat
    cuerpo = bmesh.new()
    cm(cuerpo, (0, 0, 2.08), (1.4, 0.58, 0.04), MADERA, 0.004)
    cm(cuerpo, (0, -0.012, 2.12), (1.46, 0.62, 0.04), MADERA, 0.008)    # cornisa
    for s in (-1, 1):
        cm(cuerpo, (s * 0.69, 0, 1.04), (0.02, 0.58, 2.08), MADERA, 0.003)
        cm(cuerpo, (s * 0.69, -0.265, 1.05), (0.06, 0.02, 2.10), MADERA, 0.003)   # montantes de delante
    cm(cuerpo, (0, 0.05, 1.75), (1.36, 0.46, 0.02), MADERA, 0.002)              # balda
    c.marcar(cuerpo)
    bmesh.ops.create_cone(cuerpo, cap_ends=True, segments=8, radius1=0.01, radius2=0.01, depth=1.36)
    nv = c.nuevos(cuerpo)
    bmesh.ops.rotate(cuerpo, verts=nv, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, "Y"))
    bmesh.ops.translate(cuerpo, verts=nv, vec=(0, 0, 1.62))
    c.asignar(cuerpo, {f for v in nv for f in v.link_faces}, METAL)
    # Perchas vacías en la barra
    for k in range(4):
        x = 0.35 + k * 0.06
        cm(cuerpo, (x, 0, 1.55), (0.006, 0.40, 0.006), METAL, 0, rot=Matrix.Rotation(math.radians(8 * (k - 1.5)), 3, "X"))
        cm(cuerpo, (x, 0, 1.585), (0.004, 0.004, 0.05), METAL, 0)

    # Hojas: pivote en la bisagra (Blender x = -x de Unity, y = -z de Unity, z = y de Unity)
    def hoja(lado):
        bm = bmesh.new()
        s = -1 if lado == "Izq" else 1        # hacia dónde crece la hoja en x de Blender desde la bisagra
        cm(bm, (s * 0.34, 0, 1.03), (0.68, 0.018, 2.04), PUERTA, 0.004)
        for z, alto in ((0.52, 0.80), (1.50, 0.86)):
            cm(bm, (s * 0.34, -0.018, z), (0.54, 0.02, alto), PUERTA, 0.003)    # cuarterones
        cm(bm, (s * 0.62, -0.03, 1.03), (0.02, 0.02, 0.14), LATON, 0.003)
        return bm
    fondo = bmesh.new()
    cm(fondo, (-0.68, 0, 1.04), (1.36, 0.02, 2.08), MADERA, 0.002)
    return [("ArmarioCuerpo", cuerpo, (0, 0, 0)),
            ("ArmarioHojaIzq", hoja("Izq"), (0.68, -0.295, 0.02)),
            ("ArmarioHojaDer", hoja("Der"), (-0.68, -0.295, 0.02)),
            ("ArmarioFondo", fondo, (0.68, 0.28, 0.0))]


def armario_fbx(mats):
    """Hornea todo junto (un atlas) y lo separa en sus cuatro objetos con el origen en su pivote."""
    piezas = armario()
    junto = bmesh.new()
    capa = junto.faces.layers.int.new("pieza")
    for i, (_, bm, piv) in enumerate(piezas):
        bmesh.ops.translate(bm, verts=bm.verts, vec=piv)
        me = bpy.data.meshes.new("tmp")
        bm.to_mesh(me); bm.free()
        antes = set(junto.faces)
        junto.from_mesh(me)
        for f in junto.faces:
            if f not in antes:
                f[capa] = i
    pieza_de = [f[capa] for f in junto.faces]
    ob = c.objeto("Armario", junto, mats)
    hornear.atlas(ob, "Armario", tam=2048, margen=0.003)
    objetos = []
    for i, (nombre, _, piv) in enumerate(piezas):
        bm = bmesh.new(); bm.from_mesh(ob.data)
        bmesh.ops.delete(bm, geom=[f for f, p in zip(bm.faces, pieza_de) if p != i], context="FACES")
        bmesh.ops.translate(bm, verts=bm.verts, vec=Vector(piv) * -1)
        me = bpy.data.meshes.new(nombre)
        bm.to_mesh(me); bm.free()
        for m in ob.data.materials:
            me.materials.append(m)
        o = bpy.data.objects.new(nombre, me)
        o.location = piv
        bpy.context.scene.collection.objects.link(o)
        objetos.append(o)
    bpy.data.objects.remove(ob)
    return objetos


PIEZAS = {"Cama": (cama, 2048), "Mesilla": (lambda: mesilla(False), 1024),
          "MesillaLampara": (lambda: mesilla(True), 1024), "Comoda": (comoda, 1024), "Armario": (None, 2048)}


def main(nombre):
    c.escena_vacia()
    mats = materiales()
    if nombre == "Armario":
        objetos = armario_fbx(mats)
    else:
        f, tam = PIEZAS[nombre]
        ob = c.objeto(nombre, f(), mats)
        for p in ob.data.polygons:
            p.use_smooth = p.material_index in (SABANA, ALMOHADA, LATON) and len(p.vertices) == 4
        usados = sorted({p.material_index for p in ob.data.polygons})
        viejos, idx = list(ob.data.materials), {o: n for n, o in enumerate(usados)}
        nuevos = [idx[p.material_index] for p in ob.data.polygons]
        ob.data.materials.clear()  # (pone los índices a 0: se reasignan después)
        for i in usados:
            ob.data.materials.append(viejos[i])
        for p, i in zip(ob.data.polygons, nuevos):
            p.material_index = i
        hornear.atlas(ob, nombre, tam=tam, margen=0.003)
        objetos = [ob]
        if nombre == "MesillaLampara":
            bb = bmesh.new()
            bmesh.ops.create_uvsphere(bb, u_segments=10, v_segments=6, radius=0.035)
            bmesh.ops.translate(bb, verts=bb.verts, vec=(0.05, 0.02, 0.80))
            objetos.append(c.objeto("Bombilla", bb, [hornear.material_liso("Mesilla_Bombilla", (1.0, 0.85, 0.6))],
                                    suave=True))
    ruta = c.exportar_fbx(nombre, objetos)
    tris = sum(len(p.vertices) - 2 for o in objetos for p in o.data.polygons)
    print(f"Exportado {ruta} ({tris} triángulos)")


if __name__ == "__main__":
    for n in (sys.argv[1:] or list(PIEZAS)):
        main(n)
