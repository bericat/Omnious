"""Mueble del recibidor con su cuenco para las llaves.

Sustituye a la malla provisional MuebleRecibidor de HouseBuilder.BuildHall y mantiene
su huella: cuerpo 1,00 x 0,34 m, encimera 1,04 x 0,38 m a 0,835 m del suelo.
El cuenco es un objeto aparte (Cuenco), apoyado en la encimera a 0,2 m a la derecha
del centro en coordenadas locales de Unity (x = +0,2), como el cuenco provisional.

Uso:  python Tools/assets/mueble_recibidor.py
Salida: Assets/_Ominous/Art/Models/MuebleRecibidor.fbx y sus texturas en Models/Texturas.
"""
import math
import os
import sys

import bpy  # noqa: F401  (carga bmesh y mathutils)
import bmesh

sys.path.insert(0, os.path.dirname(__file__))
import comun as c  # noqa: E402

ANCHO, FONDO = 1.0, 0.34
Z_ZOCALO, Z_CUERPO = 0.06, 0.80
ENCIMERA = (1.04, 0.38, 0.035)
FRENTE = -FONDO / 2  # cara delantera del cuerpo (Blender -Y = frente)
GROSOR_FRENTE = 0.018


def pomo(bm, x, z):
    """Pomo redondo pequeño que sale hacia el frente."""
    perfil = [(0.009, 0.0), (0.006, 0.006), (0.006, 0.014), (0.014, 0.018),
              (0.016, 0.023), (0.012, 0.027), (0.001, 0.028)]
    antes = set(bm.verts)
    anillos = c.torno(bm, perfil, lados=12)
    bm.faces.new(anillos[-1])
    nuevos = [v for v in bm.verts if v not in antes]
    bmesh.ops.rotate(bm, verts=nuevos, cent=(0, 0, 0),
                     matrix=__import__("mathutils").Matrix.Rotation(math.radians(90), 3, "X"))
    bmesh.ops.translate(bm, verts=nuevos, vec=(x, FRENTE - GROSOR_FRENTE, z))
    return {f for v in nuevos for f in v.link_faces}


def frente(bm, x, z0, z1, ancho, moldura):
    """Puerta o cajón: tablero biselado y, si moldura, un marco en relieve."""
    h = z1 - z0
    yc = FRENTE - GROSOR_FRENTE / 2
    c.caja(bm, (x, yc, z0 + h / 2), (ancho, GROSOR_FRENTE, h), biselado=0.003)
    if moldura:
        m, w, p = 0.05, 0.016, 0.006  # margen, ancho del listón, relieve
        y = FRENTE - GROSOR_FRENTE - p / 2
        ix0, ix1 = x - ancho / 2 + m, x + ancho / 2 - m
        iz0, iz1 = z0 + m, z1 - m
        c.caja(bm, (x, y, iz1 - w / 2), (ix1 - ix0, p, w), biselado=0.002)
        c.caja(bm, (x, y, iz0 + w / 2), (ix1 - ix0, p, w), biselado=0.002)
        c.caja(bm, (ix0 + w / 2, y, (iz0 + iz1) / 2), (w, p, iz1 - iz0 - 2 * w), biselado=0.002)
        c.caja(bm, (ix1 - w / 2, y, (iz0 + iz1) / 2), (w, p, iz1 - iz0 - 2 * w), biselado=0.002)


def mueble(mats):
    bm = bmesh.new()
    # Cuerpo y zócalo (madera oscura)
    c.caja(bm, (0, 0, (Z_ZOCALO + Z_CUERPO) / 2), (ANCHO, FONDO, Z_CUERPO - Z_ZOCALO), biselado=0.002)
    c.caja(bm, (0, 0.01, Z_ZOCALO / 2), (ANCHO - 0.04, FONDO - 0.04, Z_ZOCALO), biselado=0.002)
    oscuras = set(bm.faces)
    # Encimera (madera clara), con canto redondeado
    c.caja(bm, (0, 0, Z_CUERPO + ENCIMERA[2] / 2), ENCIMERA, biselado=0.008, segmentos=3)
    # Dos cajones arriba y dos puertas abajo
    hueco = 0.004
    a = (ANCHO - 0.03 - hueco) / 2
    for s in (-1, 1):
        x = s * (a / 2 + hueco / 2)
        frente(bm, x, 0.665, 0.785, a, moldura=False)
        frente(bm, x, 0.08, 0.655, a, moldura=True)
    claras = set(bm.faces) - oscuras
    metal = set()
    for s in (-1, 1):
        x = s * (a / 2 + hueco / 2)
        metal |= pomo(bm, x, 0.725)
        metal |= pomo(bm, s * 0.06, 0.585)
    c.asignar(bm, oscuras, 0)
    c.asignar(bm, claras - metal, 1)
    c.asignar(bm, metal, 2)
    return c.objeto("MuebleRecibidor", bm, mats)


def cuenco(mat):
    bm = bmesh.new()
    perfil = [
        (0.040, 0.000), (0.046, 0.003), (0.050, 0.008),            # pie
        (0.072, 0.018), (0.095, 0.038), (0.110, 0.058),            # pared exterior
        (0.118, 0.070), (0.119, 0.074), (0.116, 0.076),            # labio
        (0.112, 0.072), (0.100, 0.055), (0.080, 0.036),            # pared interior
        (0.050, 0.022), (0.020, 0.017), (0.001, 0.016),            # fondo interior
    ]
    anillos = c.torno(bm, perfil, lados=32)
    bm.faces.new(anillos[-1])
    return c.objeto("Cuenco", bm, [mat], suave=True)


def main():
    c.escena_vacia()
    tex_osc = c.textura_madera("MuebleRecibidor_MaderaOscura", (0.24, 0.15, 0.09), semilla=11)
    tex_cla = c.textura_madera("MuebleRecibidor_MaderaClara", (0.40, 0.29, 0.19), semilla=12, vetas=18)
    tex_cer = c.textura_ceramica("Cuenco_Ceramica", (0.70, 0.66, 0.56), semilla=13)
    mats = [
        c.material("MuebleRecibidor_MaderaOscura", tex_osc, rugosidad=0.55),
        c.material("MuebleRecibidor_MaderaClara", tex_cla, rugosidad=0.45),
        c.material("MuebleRecibidor_Pomo", color=(0.42, 0.33, 0.18), rugosidad=0.4, metal=1.0),
    ]
    m = mueble(mats)
    b = cuenco(c.material("Cuenco_Ceramica", tex_cer, rugosidad=0.25))
    # En Unity x = -x de Blender: el cuenco va a x = +0,2 en Unity.
    b.location = (-0.2, 0.0, Z_CUERPO + ENCIMERA[2])
    ruta = c.exportar_fbx("MuebleRecibidor", [m, b])
    tris = sum(len(p.vertices) - 2 for o in (m, b) for p in o.data.polygons)
    print(f"Exportado {ruta} ({tris} triángulos)")


if __name__ == "__main__":
    main()
