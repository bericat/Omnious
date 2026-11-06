"""Manojo de llaves para el cuenco del recibidor: aro, tres llaves (dos de latón y una plateada) y un
llavero de plástico rojo. Tumbado, unos 0,11 m de punta a punta.

Sustituye a LlavesCuenco (malla provisional): origen abajo en el centro del aro, apoyado en y = 0.
Un objeto, textura horneada Texturas/Llaves.jpg.

Uso:  python Tools/assets/llaves.py
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

PLATA, LATON, PLASTICO = range(3)
E = 0.0022  # grosor de una llave


def placa(bm, contorno, z0, grosor, mat, rot=0.0, desde=(0, 0)):
    """Pieza plana: contorno (x, y) extruido 'grosor' desde z0, girada 'rot' y movida a 'desde'."""
    c.marcar(bm)
    vs = [bm.verts.new((x, y, z0)) for x, y in contorno]
    f = bm.faces.new(vs)
    r = bmesh.ops.extrude_face_region(bm, geom=[f])
    bmesh.ops.translate(bm, vec=(0, 0, grosor), verts=[v for v in r["geom"] if isinstance(v, bmesh.types.BMVert)])
    nv = c.nuevos(bm)
    bmesh.ops.rotate(bm, verts=nv, cent=(0, 0, 0), matrix=Matrix.Rotation(rot, 3, "Z"))
    bmesh.ops.translate(bm, verts=nv, vec=(desde[0], desde[1], 0))
    c.asignar(bm, {f for v in nv for f in v.link_faces}, mat)


def contorno_llave(largo, dientes, cabeza=0.012, semilla=0):
    """Cabeza redonda con agujero hacia el aro (en el origen) y paleta con dientes hacia +X."""
    pts = []
    # Cabeza: círculo de 'cabeza' de radio centrado en x = cabeza (el agujero queda junto al aro)
    a0 = math.radians(25)
    for k in range(14):
        a = a0 + (2 * math.pi - 2 * a0) * k / 13
        pts.append((cabeza + cabeza * math.cos(a), cabeza * math.sin(a)))
    x0 = cabeza * 2 - 0.002
    rng = __import__("random").Random(semilla)
    pts.append((x0, -0.0035))
    paso = (largo - 0.006) / dientes
    for i in range(dientes):
        x = x0 + i * paso
        pts.append((x + paso * 0.3, -0.0035 - rng.uniform(0.0008, 0.0025)))
        pts.append((x + paso * 0.7, -0.0035))
    pts.append((x0 + largo - 0.002, -0.0025))
    pts.append((x0 + largo, 0.0005))
    pts.append((x0, 0.0035))
    return pts


def manojo():
    bm = bmesh.new()
    # Aro de acero (toro tumbado)
    R, r = 0.014, 0.0011
    anillos = []
    for i in range(20):
        a = 2 * math.pi * i / 20
        anillos.append([bm.verts.new(((R + r * math.cos(b)) * math.cos(a), (R + r * math.cos(b)) * math.sin(a),
                                      r + r * math.sin(b))) for b in (2 * math.pi * k / 6 for k in range(6))])
    for i in range(20):
        a0, a1 = anillos[i], anillos[(i + 1) % 20]
        for k in range(6):
            j = (k + 1) % 6
            f = bm.faces.new((a0[k], a0[j], a1[j], a1[k]))
            f.material_index = PLATA
    # Tres llaves colgando del aro hacia fuera, una encima de otra
    llaves = ((0.045, 6, LATON, 0.4, 1), (0.038, 5, PLATA, -0.35, 2), (0.05, 7, LATON, 2.6, 3))
    for n, (largo, dientes, mat, ang, sem) in enumerate(llaves):
        cx, cy = R * math.cos(ang), R * math.sin(ang)
        placa(bm, contorno_llave(largo, dientes, semilla=sem), 0.0005 + n * E * 0.9, E, mat, ang,
              (cx - 0.004 * math.cos(ang), cy - 0.004 * math.sin(ang)))
    # Llavero de plástico rojo con su anilla, hacia el otro lado
    ang = math.pi + 0.9
    cx, cy = R * math.cos(ang), R * math.sin(ang)
    contorno = [(0.0, 0.006), (0.0, -0.006), (0.006, -0.012), (0.038, -0.012), (0.042, -0.008), (0.042, 0.008),
                (0.038, 0.012), (0.006, 0.012)]
    placa(bm, contorno, 0.0005, 0.004, PLASTICO, ang, (cx, cy))
    return bm


def main():
    c.escena_vacia()
    hs = hornear.material_sucio
    mats = [
        hs("Plata", (0.40, 0.40, 0.38), rugosidad=0.3, metal=1.0, suciedad=0.8, manchas=0.4, polvo=0.0),
        hs("Laton", (0.42, 0.31, 0.11), rugosidad=0.3, metal=1.0, suciedad=0.8, manchas=0.4, polvo=0.0),
        hs("Plastico", (0.32, 0.03, 0.02), rugosidad=0.4, suciedad=0.8, manchas=0.5, polvo=0.0),
    ]
    ob = c.objeto("Llaves", manojo(), mats)
    hornear.atlas(ob, "Llaves", tam=512, margen=0.004)
    ruta = c.exportar_fbx("Llaves", [ob])
    print(f"Exportado {ruta} ({sum(len(p.vertices) - 2 for p in ob.data.polygons)} triángulos)")


if __name__ == "__main__":
    main()
