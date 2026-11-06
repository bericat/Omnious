"""Piezas sueltas del lavadero, el garaje, el recibidor, el pasillo y el baño, con el estilo de la fase 10.

Sustituyen a las mallas provisionales de HouseBuilder con su misma huella, orientación y origen.
Ejes: x de Unity = -x de Blender, z de Unity = -y de Blender, y de Unity = z de Blender.
- Lavadora / Secadora: 0,6 x 0,86 x 0,6 m, frente a +Z. La lavadora lleva "Cristal" aparte (ojo de buey).
- Baldas: dos tablas de 0,30 x 1,50 m (largas en Z de Unity), origen en el centro de la de abajo; la pared
  está en -X de Unity. Se colocan a 1,55 m como ahora.
- Cesto: cesto de mimbre con ropa, 0,48 m de diámetro y 0,6 m de alto.
- EstanteriaGaraje: estantería metálica de 1,4 x 1,9 x 0,42 m, frente a +Z.
- LatasPintura: tres botes de pintura en las posiciones de la provisional.
- Escalera: escalera de mano de madera, 0,45 x 2,2 m, de pie.
- CuadroElectrico: caja de 0,40 x 0,55 x 0,08 m, origen en el centro, la tapa mira a -Z de Unity.
- Perchero: perchero de pie con un abrigo colgado hacia +X de Unity.
- Felpudo: 0,8 x 0,5 m.
- Reloj: reloj de pared redondo de 0,32 m, origen en el centro, la esfera mira a -Z de Unity (10:10).
- RelojParado: el mismo, parado a las 3:33 (acto 3).
- Espejo: espejo del baño de 0,7 x 0,55 m en la pared (grosor en X de Unity, luna hacia -X), con la luna
  como objeto aparte "Luna" (material Espejo_Luna, para ponerle el material de espejo en Unity).

Uso:  python Tools/assets/varios.py [Nombre ...]
Texturas CC0: Mueble_Wood092, Oxido_Rust004, Tapiceria_Fabric080/083, Suciedad_SurfaceImperfections015.
"""
import math
import os
import random
import sys

import bpy
import bmesh
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(__file__))
import comun as c  # noqa: E402
import hornear  # noqa: E402

(MADERA, MADERA_CLARA, ESMALTE, METAL, CHAPA, OXIDO, NEGRO, CRISTAL_OSC, TELA, TELA2, CARTON, MIMBRE,
 PAPEL, COCO, PINTURA_B, PINTURA_V) = range(16)


def materiales():
    hs = hornear.material_sucio
    mv = hornear.madera_vieja
    return [
        mv("Madera", "oscura", desgaste=0.5),
        mv("MaderaClara", "gris", desgaste=0.6, semilla=2.0),
        hornear.plastico_viejo("Esmalte", (0.55, 0.52, 0.43), chorretones=0.4),
        hs("Metal", (0.42, 0.41, 0.38), rugosidad=0.35, metal=1.0, suciedad=0.8, manchas=0.5, mugre=0.6),
        hs("Chapa", (0.22, 0.24, 0.21), rugosidad=0.5, metal=0.6, suciedad=1.0, manchas=0.5, mugre=0.9,
           desgaste=0.4, color_desgaste=(0.40, 0.38, 0.33), color_sucio=(0.07, 0.06, 0.04)),
        hs("Oxido", (0.8, 0.8, 0.8), rugosidad=0.8, imagen=c.cc0("Oxido_Rust004"), escala=0.3, suciedad=0.5,
           color_sucio=(0.06, 0.04, 0.02)),
        hs("Negro", (0.035, 0.033, 0.03), rugosidad=0.5, suciedad=0.4, manchas=0.4, color_sucio=(0.12, 0.10, 0.08)),
        hs("CristalOscuro", (0.05, 0.06, 0.055), rugosidad=0.1, suciedad=0.5, manchas=0.6,
           color_sucio=(0.15, 0.13, 0.10)),
        hs("Tela", (0.16, 0.13, 0.09), rugosidad=0.95, imagen=c.cc0("Tapiceria_Fabric080"), escala=0.4, veta=1.0,
           suciedad=0.6, manchas=0.4, mugre=0.5, color_sucio=(0.06, 0.05, 0.03)),
        hs("Tela2", (0.30, 0.27, 0.20), rugosidad=0.95, imagen=c.cc0("Tapiceria_Fabric083"), escala=0.3, veta=0.8,
           suciedad=0.6, manchas=0.5, color_sucio=(0.12, 0.10, 0.06)),
        hs("Carton", (0.36, 0.27, 0.16), rugosidad=0.9, suciedad=0.8, manchas=0.5, escala_manchas=10, mugre=0.6),
        hs("Mimbre", (0.36, 0.28, 0.16), rugosidad=0.8, imagen=c.cc0("Tapiceria_Fabric083"), escala=0.08, veta=1.4,
           suciedad=0.9, manchas=0.4, color_sucio=(0.10, 0.07, 0.04)),
        hs("Papel", (0.50, 0.46, 0.38), rugosidad=0.8, suciedad=0.6, manchas=0.6, escala_manchas=15),
        hs("Coco", (0.30, 0.22, 0.12), rugosidad=0.95, imagen=c.cc0("Tapiceria_Fabric083"), escala=0.15, veta=1.6,
           suciedad=0.6, manchas=0.7, mugre=1.0, color_sucio=(0.08, 0.06, 0.03), polvo=0.0),
        hs("PinturaB", (0.55, 0.53, 0.46), rugosidad=0.5, suciedad=0.8, manchas=0.6, mugre=0.8, chorretones=0.8),
        hs("PinturaV", (0.12, 0.20, 0.13), rugosidad=0.5, suciedad=0.8, manchas=0.6, mugre=0.8, chorretones=0.8),
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


FRENTE = Matrix.Rotation(math.radians(90), 3, "X")   # cilindro con el eje hacia -Y/+Y (frente)


def lavadora(tambor):
    bm = bmesh.new()
    cm = c.caja_mat
    cm(bm, (0, 0, 0.44), (0.60, 0.60, 0.84), ESMALTE, 0.02)
    cm(bm, (0, 0.0, 0.865), (0.60, 0.60, 0.02), ESMALTE, 0.008)
    cm(bm, (0, -0.30, 0.03), (0.58, 0.02, 0.06), NEGRO, 0.004)
    cm(bm, (0, -0.302, 0.76), (0.56, 0.008, 0.12), ESMALTE, 0.004)          # panel de mandos
    cil(bm, (0.18, -0.31, 0.76), 0.03, 0.02, METAL, rot=FRENTE)
    for k in range(3):
        cm(bm, (-0.05 - k * 0.05, -0.308, 0.76), (0.03, 0.008, 0.018), NEGRO, 0.002)
    cm(bm, (-0.20, -0.307, 0.78), (0.10, 0.004, 0.04), PAPEL, 0)            # cajetín del jabón
    if tambor:
        cil(bm, (0, -0.31, 0.40), 0.19, 0.02, METAL, lados=20, rot=FRENTE)  # aro de la puerta
        cil(bm, (0.17, -0.325, 0.40), 0.015, 0.02, NEGRO, lados=8, rot=FRENTE)
    else:
        cil(bm, (0, -0.31, 0.40), 0.20, 0.016, ESMALTE, lados=20, rot=FRENTE)
        cm(bm, (0, -0.322, 0.53), (0.14, 0.012, 0.025), NEGRO, 0.004)
        for k in range(6):
            cm(bm, (0, -0.32, 0.30 + k * 0.025), (0.22, 0.004, 0.006), NEGRO, 0)
    # Una toalla vieja encima
    cm(bm, (0.08, 0.05, 0.89), (0.36, 0.26, 0.03), TELA2, 0.01)
    return bm


def lavadora_cristal():
    bm = bmesh.new()
    cil(bm, (0, -0.321, 0.40), 0.15, 0.006, 0, lados=20, rot=FRENTE)
    return bm


def baldas():
    bm = bmesh.new()
    cm = c.caja_mat
    for z in (0.0, 0.35):
        cm(bm, (0, 0, z), (0.30, 1.50, 0.025), MADERA_CLARA, 0.003)
        for y in (-0.6, 0.6):
            cm(bm, (0.13, y, z - 0.07), (0.025, 0.025, 0.12), METAL, 0.002)   # escuadras contra la pared (+X)
    cm(bm, (-0.01, 0.45, 0.10), (0.14, 0.20, 0.18), CARTON, 0.004)            # caja de detergente
    cil(bm, (-0.01, 0.0, 0.135), 0.045, 0.24, ESMALTE, lados=10)              # botella de lejía
    cil(bm, (-0.01, 0.0, 0.265), 0.015, 0.03, PINTURA_V, lados=8)
    for k in range(3):                                                         # toallas dobladas
        cm(bm, (-0.01, -0.35, 0.39 + k * 0.05), (0.26, 0.30, 0.05), TELA2 if k % 2 else TELA, 0.015)
    cm(bm, (-0.01, 0.45, 0.405), (0.16, 0.22, 0.08), CARTON, 0.004)
    return bm


def cesto():
    bm = bmesh.new()
    c.marcar(bm)
    c.torno(bm, [(0.19, 0.0), (0.24, 0.55), (0.25, 0.57), (0.23, 0.57), (0.18, 0.03), (0.002, 0.03)], lados=16)
    c.asignar(bm, {f for v in c.nuevos(bm) for f in v.link_faces}, MIMBRE)
    rng = random.Random(5)
    for k in range(5):
        a = k * 1.3
        r = 0.08 + rng.random() * 0.06
        cm = c.caja_mat
        cm(bm, (math.cos(a) * r, math.sin(a) * r, 0.55 + rng.random() * 0.05), (0.26, 0.18, 0.08),
           TELA if k % 2 else TELA2, 0.03, rot=Matrix.Rotation(rng.random() * 3, 3, "Z") @ Matrix.Rotation(0.4, 3, "X"))
    return bm


def estanteria_garaje():
    bm = bmesh.new()
    cm = c.caja_mat
    for x in (-0.68, 0.68):
        for y in (-0.19, 0.19):
            cm(bm, (x, y, 0.95), (0.035, 0.035, 1.9), CHAPA, 0.002)
    for z in (0.3, 0.95, 1.6):
        cm(bm, (0, 0, z), (1.40, 0.42, 0.02), CHAPA, 0.002)
        for y in (-0.205, 0.205):
            cm(bm, (0, y, z - 0.02), (1.40, 0.012, 0.04), CHAPA, 0.002)
    cm(bm, (0.3, 0, 0.47), (0.42, 0.30, 0.31), CARTON, 0.005)
    cm(bm, (0.32, 0.01, 0.635), (0.30, 0.22, 0.02), CARTON, 0.003)
    cil(bm, (-0.35, 0, 1.065), 0.09, 0.21, OXIDO, lados=12)
    cil(bm, (-0.12, 0.02, 1.04), 0.07, 0.16, PINTURA_V, lados=12)
    cm(bm, (0.35, 0, 1.75), (0.35, 0.32, 0.28), TELA, 0.03)                   # manta vieja doblada
    cm(bm, (-0.3, -0.02, 1.68), (0.40, 0.25, 0.14), CARTON, 0.004)
    cm(bm, (-0.2, 0.0, 0.33), (0.50, 0.30, 0.04), MADERA_CLARA, 0.003)         # tablas sueltas
    return bm


def latas_pintura():
    bm = bmesh.new()
    for (ux, uz, h, mat) in ((0.0, 0.0, 0.22, PINTURA_B), (0.26, 0.04, 0.22, OXIDO), (0.12, 0.22, 0.18, PINTURA_V)):
        x, y = -ux, -uz
        cil(bm, (x, y, h / 2), 0.1, h, mat, lados=14)
        cil(bm, (x, y, h + 0.004), 0.102, 0.008, METAL, lados=14)
        barra(bm, (x - 0.1, y, h - 0.02), (x + 0.1, y, h - 0.02), 0.003, METAL, lados=6)   # asa
    return bm


def escalera():
    bm = bmesh.new()
    cm = c.caja_mat
    for x in (-0.2, 0.2):
        cm(bm, (x, 0, 1.1), (0.05, 0.05, 2.2), MADERA_CLARA, 0.006)
    for i in range(7):
        cm(bm, (0, 0, 0.25 + i * 0.3), (0.40, 0.04, 0.03), MADERA_CLARA, 0.004)
    cil(bm, (0.2, -0.03, 1.3), 0.006, 0.02, OXIDO, lados=6, rot=FRENTE)        # clavos
    return bm


def cuadro_electrico():
    bm = bmesh.new()
    cm = c.caja_mat
    cm(bm, (0, 0, 0), (0.40, 0.08, 0.55), CHAPA, 0.006)
    cm(bm, (0, 0.042, 0), (0.37, 0.006, 0.52), CHAPA, 0.004)                   # tapa (hacia +Y = -Z de Unity)
    cm(bm, (-0.14, 0.05, 0), (0.02, 0.012, 0.08), METAL, 0.002)
    cm(bm, (0.05, 0.047, 0.17), (0.18, 0.002, 0.08), PAPEL, 0)                 # etiqueta
    barra(bm, (0.12, 0, -0.27), (0.12, 0, -0.60), 0.012, NEGRO)                # tubo de cables hacia abajo
    return bm


def perchero():
    bm = bmesh.new()
    c.marcar(bm)
    c.torno(bm, [(0.17, 0.0), (0.16, 0.025), (0.05, 0.04), (0.025, 0.06), (0.002, 0.06)], lados=10)
    c.asignar(bm, {f for v in c.nuevos(bm) for f in v.link_faces}, MADERA)
    cil(bm, (0, 0, 0.88), 0.02, 1.66, MADERA, lados=8)
    cil(bm, (0, 0, 1.73), 0.035, 0.06, MADERA, lados=8)
    for a in (0, 90, 180, 270):
        r = math.radians(a)
        barra(bm, (0, 0, 1.6), (math.cos(r) * 0.13, math.sin(r) * 0.13, 1.68), 0.009, MADERA, lados=6)
    # Abrigo colgado (x de Blender negativa = +X de Unity)
    c.marcar(bm)
    c.torno(bm, [(0.13, 0.0), (0.15, 0.25), (0.14, 0.5), (0.10, 0.62), (0.05, 0.66), (0.002, 0.66)], lados=10)
    nv = c.nuevos(bm)
    bmesh.ops.scale(bm, vec=(0.55, 1.1, 1.0), verts=nv)
    bmesh.ops.translate(bm, verts=nv, vec=(-0.13, 0, 1.0))
    c.asignar(bm, {f for v in nv for f in v.link_faces}, TELA)
    return bm


def felpudo():
    bm = bmesh.new()
    c.caja_mat(bm, (0, 0, 0.008), (0.8, 0.5, 0.016), COCO, 0.006)
    c.caja_mat(bm, (0, 0, 0.0165), (0.66, 0.36, 0.002), NEGRO, 0)
    c.caja_mat(bm, (0, 0, 0.018), (0.60, 0.30, 0.002), COCO, 0)
    return bm


def reloj(hora=3.0, minuto=0.0):
    """Esfera vista desde +Y de Blender (-Z de Unity): las 3 quedan a la derecha del que mira (-x de Blender)."""
    bm = bmesh.new()
    cil(bm, (0, 0, 0), 0.16, 0.04, MADERA, lados=24, rot=FRENTE)
    cil(bm, (0, 0.021, 0), 0.135, 0.004, PAPEL, lados=24, rot=FRENTE)

    def radial(ang, r, ancho, largo, y, mat):
        a = math.radians(ang)
        c.caja_mat(bm, (-math.sin(a) * r, y, math.cos(a) * r), (ancho, 0.002, largo), mat, 0,
                   rot=Matrix.Rotation(-a, 3, "Y"))
    for k in range(12):
        radial(k * 30, 0.115, 0.004, 0.02 if k % 3 == 0 else 0.01, 0.024, NEGRO)
    radial(minuto * 6, 0.045, 0.008, 0.09, 0.026, NEGRO)                                   # minutero
    radial((hora % 12 + minuto / 60) * 30, 0.03, 0.01, 0.06, 0.027, NEGRO)                 # horaria
    cil(bm, (0, 0.028, 0), 0.008, 0.004, METAL, lados=8, rot=FRENTE)
    return bm


def espejo():
    bm = bmesh.new()
    cm = c.caja_mat
    # Grosor en X de Unity (aquí x de Blender); la luna mira a -X de Unity = +x de Blender
    for s in (-1, 1):
        cm(bm, (0, s * 0.26, 0), (0.015, 0.03, 0.70), METAL, 0.003)
        cm(bm, (0, 0, s * 0.335), (0.015, 0.55, 0.03), METAL, 0.003)
    cm(bm, (-0.004, 0, 0), (0.006, 0.52, 0.67), NEGRO, 0)
    cm(bm, (0.02, 0, -0.38), (0.05, 0.40, 0.012), CRISTAL_OSC, 0.003)           # repisa de cristal
    return bm


def espejo_luna():
    bm = bmesh.new()
    c.caja(bm, (0.0035, 0, 0), (0.002, 0.50, 0.65))
    for f in bm.faces:
        f.material_index = 0
    return bm


PIEZAS = {
    "Lavadora": (lambda: lavadora(True), 1024), "Secadora": (lambda: lavadora(False), 1024),
    "Baldas": (baldas, 1024), "Cesto": (cesto, 1024), "EstanteriaGaraje": (estanteria_garaje, 1024),
    "LatasPintura": (latas_pintura, 512), "Escalera": (escalera, 512), "CuadroElectrico": (cuadro_electrico, 512),
    "Perchero": (perchero, 1024), "Felpudo": (felpudo, 512), "Reloj": (lambda: reloj(10, 10), 512),
    "RelojParado": (lambda: reloj(3, 33), 512), "Espejo": (espejo, 512),
}


def main(nombre):
    c.escena_vacia()
    f, tam = PIEZAS[nombre]
    mats = materiales()
    ob = c.objeto(nombre, f(), mats)
    for p in ob.data.polygons:
        p.use_smooth = p.material_index in (METAL, OXIDO, PINTURA_B, PINTURA_V, MIMBRE, TELA) and len(p.vertices) == 4
    usados = sorted({p.material_index for p in ob.data.polygons})
    viejos, idx = list(ob.data.materials), {o: n for n, o in enumerate(usados)}
    nuevos = [idx[p.material_index] for p in ob.data.polygons]
    ob.data.materials.clear()  # (pone los índices a 0: se reasignan después)
    for i in usados:
        ob.data.materials.append(viejos[i])
    for p, i in zip(ob.data.polygons, nuevos):
        p.material_index = i
    hornear.atlas(ob, nombre, tam=tam, margen=0.004)
    objetos = [ob]
    if nombre == "Lavadora":
        objetos.append(c.objeto("Cristal", lavadora_cristal(),
                                [hornear.material_liso("Lavadora_Cristal", (0.08, 0.09, 0.08), rugosidad=0.1, alfa=0.4)]))
    if nombre == "Espejo":
        objetos.append(c.objeto("Luna", espejo_luna(), [hornear.material_liso("Espejo_Luna", (0.6, 0.6, 0.58),
                                                                               rugosidad=0.05, metal=1.0)]))
    ruta = c.exportar_fbx(nombre, objetos)
    tris = sum(len(p.vertices) - 2 for o in objetos for p in o.data.polygons)
    print(f"Exportado {ruta} ({tris} triángulos)")


if __name__ == "__main__":
    for n in (sys.argv[1:] or list(PIEZAS)):
        main(n)
