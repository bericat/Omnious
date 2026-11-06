"""Lámpara de techo de salón de los 80: latón con cinco brazos curvos y tulipas de cristal ámbar.

Unos 0,62 m de diámetro y 0,52 m de alto. El origen está ARRIBA, en el centro (se pega al techo), y
cuelga hacia abajo. Dos objetos: "LamparaTecho" (latón, textura horneada Texturas/LamparaTecho.jpg) y
"Pantalla" (las cinco tulipas con su bombilla, material LamparaTecho_Cristal aparte, para hacerlo
emisivo en Unity y apagarlo o hacerlo parpadear).

Uso:  python Tools/assets/lampara_techo.py
"""
import math
import os
import sys

import bpy  # noqa: F401  (carga bmesh)
import bmesh
from mathutils import Vector

sys.path.insert(0, os.path.dirname(__file__))
import comun as c  # noqa: E402
import hornear  # noqa: E402

LATON, OSCURO = range(2)
BRAZOS = 5
R_BRAZO = 0.27          # radio al que quedan las tulipas
Z_CUERPO = -0.40        # altura del cuerpo central (desde el techo)


def torno_mat(bm, perfil, mat, lados=12, desde=(0, 0, 0)):
    c.marcar(bm)
    c.torno(bm, perfil, lados=lados, desde=desde)
    nv = c.nuevos(bm)
    c.asignar(bm, {f for v in nv for f in v.link_faces}, mat)
    return nv


def tubo(bm, puntos, r, mat, lados=6):
    """Tubo que sigue una lista de puntos (brazo curvo)."""
    puntos = [Vector(p) for p in puntos]
    anillos = []
    for i, p in enumerate(puntos):
        t = (puntos[min(i + 1, len(puntos) - 1)] - puntos[max(i - 1, 0)]).normalized()
        ref = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))
        u = t.cross(ref).normalized()
        w = t.cross(u).normalized()
        anillos.append([bm.verts.new(p + r * (math.cos(a) * u + math.sin(a) * w))
                        for a in (2 * math.pi * k / lados for k in range(lados))])
    caras = []
    for a, b in zip(anillos, anillos[1:]):
        for k in range(lados):
            j = (k + 1) % lados
            caras.append(bm.faces.new((a[k], a[j], b[j], b[k])))
    caras.append(bm.faces.new(list(reversed(anillos[0]))))
    caras.append(bm.faces.new(anillos[-1]))
    c.asignar(bm, caras, mat)


def lampara(bm):
    # Florón del techo y vástago con bolas
    torno_mat(bm, [(0.075, -0.035), (0.08, -0.025), (0.07, -0.012), (0.075, 0.0), (0.002, 0.0)], LATON, 16)
    torno_mat(bm, [(0.01, Z_CUERPO + 0.06), (0.01, -0.03)], LATON, 8)
    for z in (-0.12, -0.24):
        torno_mat(bm, [(0.002, z - 0.025), (0.018, z - 0.018), (0.024, z), (0.018, z + 0.018), (0.002, z + 0.025)],
                  LATON, 10)
    # Cuerpo central torneado y remate de abajo
    z0 = Z_CUERPO
    torno_mat(bm, [(0.004, z0 - 0.12), (0.012, z0 - 0.10), (0.02, z0 - 0.075), (0.03, z0 - 0.06),
                   (0.055, z0 - 0.035), (0.06, z0 - 0.01), (0.05, z0 + 0.01), (0.03, z0 + 0.03),
                   (0.035, z0 + 0.05), (0.012, z0 + 0.065), (0.002, z0 + 0.065)], LATON, 14)
    torno_mat(bm, [(0.002, z0 - 0.145), (0.012, z0 - 0.135), (0.014, z0 - 0.12), (0.002, z0 - 0.115)], OSCURO, 8)
    # Brazos en S: salen del cuerpo, bajan un poco y suben hasta el portalámparas
    for i in range(BRAZOS):
        a = 2 * math.pi * i / BRAZOS
        d = Vector((math.cos(a), math.sin(a), 0))
        pts = []
        for k in range(13):
            t = k / 12
            rr = 0.05 + (R_BRAZO - 0.05) * t
            z = z0 - 0.02 - 0.07 * math.sin(math.pi * t * 0.9) + 0.09 * t ** 2
            pts.append(d * rr + Vector((0, 0, z)))
        # Volutilla bajo el brazo
        tubo(bm, pts, 0.008, LATON)
        voluta = [d * (0.08 + 0.05 * math.sin(math.pi * t)) + Vector((0, 0, z0 - 0.04 - 0.05 * t)) for t in
                  (k / 6 for k in range(7))]
        tubo(bm, voluta, 0.004, LATON, lados=5)
        # Arandela (bobeche) y portalámparas oscuro sobre el extremo
        cx, cy = d.x * R_BRAZO, d.y * R_BRAZO
        zt = z0 - 0.02 + 0.09 - 0.07 * math.sin(math.pi * 0.9)
        torno_mat(bm, [(0.01, zt - 0.01), (0.04, zt + 0.005), (0.045, zt + 0.012), (0.012, zt + 0.012),
                       (0.002, zt + 0.012)], LATON, 12, desde=(cx, cy, 0))
        torno_mat(bm, [(0.016, zt + 0.012), (0.016, zt + 0.045), (0.002, zt + 0.045)], OSCURO, 10, desde=(cx, cy, 0))


def pantallas(mat):
    """Cinco tulipas de cristal (boca hacia arriba) con su bombilla."""
    bm = bmesh.new()
    z0 = Z_CUERPO
    zt = z0 - 0.02 + 0.09 - 0.07 * math.sin(math.pi * 0.9) + 0.012
    perfil = [(0.02, 0.0), (0.03, 0.012), (0.05, 0.04), (0.068, 0.08), (0.078, 0.115), (0.085, 0.135),
              (0.088, 0.14), (0.082, 0.138), (0.074, 0.115), (0.064, 0.08), (0.046, 0.042), (0.026, 0.014),
              (0.002, 0.008)]
    for i in range(BRAZOS):
        a = 2 * math.pi * i / BRAZOS
        cx, cy = math.cos(a) * R_BRAZO, math.sin(a) * R_BRAZO
        c.torno(bm, [(r, zt + z) for r, z in perfil], lados=12, desde=(cx, cy, 0))
        # Bombilla de vela
        c.torno(bm, [(0.002, zt + 0.045), (0.012, zt + 0.05), (0.014, zt + 0.07), (0.01, zt + 0.095),
                     (0.002, zt + 0.105)], lados=8, desde=(cx, cy, 0))
    for f in bm.faces:
        f.material_index = 0
    return c.objeto("Pantalla", bm, [mat], suave=True)


def main():
    c.escena_vacia()
    hs = hornear.material_sucio
    mats = [
        hs("Laton", (0.36, 0.25, 0.09), rugosidad=0.35, metal=1.0, suciedad=1.0, polvo=0.9, manchas=0.6,
           mugre=0.8, color_sucio=(0.09, 0.07, 0.04), desgaste=0.2, color_desgaste=(0.45, 0.34, 0.14)),
        hs("Portalamparas", (0.08, 0.07, 0.06), rugosidad=0.6, suciedad=0.6, polvo=0.6),
    ]
    bm = bmesh.new()
    lampara(bm)
    ob = c.objeto("LamparaTecho", bm, mats)
    for p in ob.data.polygons:
        p.use_smooth = len(p.vertices) == 4
    hornear.atlas(ob, "LamparaTecho", tam=1024, margen=0.003)
    pan = pantallas(hornear.material_liso("LamparaTecho_Cristal", (0.78, 0.55, 0.25), rugosidad=0.25))
    ruta = c.exportar_fbx("LamparaTecho", [ob, pan])
    tris = sum(len(p.vertices) - 2 for o in (ob, pan) for p in o.data.polygons)
    print(f"Exportado {ruta} ({tris} triángulos)")


if __name__ == "__main__":
    main()
