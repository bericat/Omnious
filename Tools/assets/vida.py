"""Objetos para que la casa parezca habitada por una pareja (Chevas y Roberta), en estilo PSX:
pocos polígonos y textura horneada de 128 px por objeto (Texturas/<Nombre>.jpg).

Convenciones: escala real, frente a +Z en Unity (aquí -Y), origen en el suelo (o en la superficie donde se
apoya) en el centro de la base. Los objetos de pared (PARED) tienen el origen en el centro de su cara de
atrás, que va contra la pared; la altura la pone quien los coloca.

Uso:  python Tools/assets/vida.py [Nombre ...]      (sin nombres, todos)
"""
import math
import os
import random
import sys

import bpy  # noqa: F401  (carga bmesh)
import bmesh
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(__file__))
import comun as c  # noqa: E402
import hornear  # noqa: E402

(MADERA, MADERA_OSC, BEIGE, NEGRO, METAL, LOZA, VIDRIO, TOALLA, ROSA, MARRON, PAPEL, CARTON, GOMA,
 NARANJA, VERDE, ROJO, AMARILLO, TIERRA, CUBO_VERDE, GRIS, MIMBRE, AZUL) = range(22)


def materiales():
    hs = hornear.material_sucio
    mv = hornear.madera_vieja
    tela = dict(rugosidad=0.95, suciedad=0.7, manchas=0.6, escala_manchas=5, polvo=0.2, mugre=0.6)
    return [
        mv("Madera", "gris"),
        mv("MaderaOscura", "oscura", desgaste=0.5),
        hornear.plastico_viejo("Beige"),
        hs("Negro", (0.04, 0.04, 0.04), rugosidad=0.5, suciedad=0.6, polvo=0.6, desgaste=0.3,
           color_desgaste=(0.15, 0.15, 0.14)),
        hs("Metal", (0.30, 0.30, 0.28), rugosidad=0.35, metal=1.0, suciedad=0.9, manchas=0.5, polvo=0.3),
        hs("Loza", (0.55, 0.53, 0.47), rugosidad=0.25, suciedad=0.9, manchas=0.4, polvo=0.3),
        hs("Vidrio", (0.12, 0.17, 0.10), rugosidad=0.15, suciedad=0.7, polvo=0.5),
        hs("Toalla", (0.20, 0.27, 0.33), **tela),
        hs("Rosa", (0.42, 0.24, 0.24), **tela),
        hs("Marron", (0.20, 0.12, 0.07), **tela),
        hs("Papel", (0.55, 0.52, 0.43), rugosidad=0.9, suciedad=0.6, manchas=0.6, escala_manchas=8, polvo=0.0),
        hs("Carton", (0.36, 0.27, 0.16), rugosidad=0.9, suciedad=0.8, manchas=0.5, escala_manchas=10),
        hs("Goma", (0.03, 0.03, 0.03), rugosidad=0.8, suciedad=0.5, polvo=0.8),
        hs("Naranja", (0.55, 0.20, 0.03), rugosidad=0.4, suciedad=0.4, manchas=0.5),
        hs("Verde", (0.10, 0.16, 0.05), rugosidad=0.6, suciedad=0.6, manchas=0.6),
        hs("Rojo", (0.40, 0.04, 0.03), rugosidad=0.4, suciedad=0.6, manchas=0.4),
        hs("Amarillo", (0.50, 0.40, 0.08), rugosidad=0.5, suciedad=0.6, manchas=0.6),
        hs("Tierra", (0.10, 0.07, 0.04), rugosidad=1.0, suciedad=0.3),
        hs("CuboVerde", (0.06, 0.15, 0.07), rugosidad=0.6, suciedad=1.0, manchas=0.6, polvo=0.6, mugre=0.8,
           chorretones=0.6),
        hs("Gris", (0.22, 0.22, 0.21), rugosidad=0.6, suciedad=1.0, manchas=0.5, polvo=0.6, mugre=0.8),
        hs("Mimbre", (0.38, 0.28, 0.15), rugosidad=0.9, imagen=c.cc0("Tapiceria_Fabric083"), escala=0.08,
           veta=1.2, suciedad=0.8, polvo=0.3),
        hs("Azul", (0.06, 0.10, 0.22), rugosidad=0.5, suciedad=0.8, manchas=0.5),
    ]


# ---------------------------------------------------------------- piezas sueltas

def caja(bm, centro, tam, mat, bisel=0.004, rot=None):
    return c.caja_mat(bm, centro, tam, mat, bisel, rot=rot)


def _poner(bm, nv, mat, rot=None, centro=(0, 0, 0)):
    if rot is not None:
        bmesh.ops.transform(bm, matrix=rot.to_4x4(), verts=nv)
    bmesh.ops.translate(bm, verts=nv, vec=centro)
    c.asignar(bm, {f for v in nv for f in v.link_faces}, mat)
    return nv


def cil(bm, centro, r, alto, mat, lados=8, r2=None, rot=None):
    """Cilindro (o cono) centrado en 'centro', eje Z antes de girar."""
    c.marcar(bm)
    bmesh.ops.create_cone(bm, cap_ends=True, segments=lados, radius1=r, radius2=r if r2 is None else r2, depth=alto)
    return _poner(bm, c.nuevos(bm), mat, rot, centro)


def torno(bm, perfil, mat, lados=8, desde=(0, 0, 0), rot=None):
    c.marcar(bm)
    anillos = c.torno(bm, perfil, lados=lados)
    if perfil[-1][0] > 0.003:
        bm.faces.new(anillos[-1])
    return _poner(bm, c.nuevos(bm), mat, rot, desde)


def barra(bm, a, b, r, mat, lados=5):
    a, b = Vector(a), Vector(b)
    c.marcar(bm)
    bmesh.ops.create_cone(bm, cap_ends=True, segments=lados, radius1=r, radius2=r, depth=(b - a).length)
    nv = c.nuevos(bm)
    bmesh.ops.transform(bm, matrix=(b - a).to_track_quat("Z", "Y").to_matrix().to_4x4(), verts=nv)
    return _poner(bm, nv, mat, None, (a + b) / 2)


def esfera(bm, centro, esc, mat, seg=8, rot=None):
    c.marcar(bm)
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=max(4, seg // 2), radius=1.0)
    nv = c.nuevos(bm)
    bmesh.ops.scale(bm, vec=esc, verts=nv)
    return _poner(bm, nv, mat, rot, centro)


def toro(bm, centro, R, r, mat, n=12, m=5, rot=None):
    c.marcar(bm)
    an = [[bm.verts.new(((R + r * math.cos(b)) * math.cos(a), (R + r * math.cos(b)) * math.sin(a), r * math.sin(b)))
           for b in (2 * math.pi * k / m for k in range(m))] for a in (2 * math.pi * i / n for i in range(n))]
    for i in range(n):
        for k in range(m):
            bm.faces.new((an[i][k], an[i][(k + 1) % m], an[(i + 1) % n][(k + 1) % m], an[(i + 1) % n][k]))
    return _poner(bm, c.nuevos(bm), mat, rot, centro)


def tela(bm, ancho, alto, mat, filas=4, cols=4, ondas=0.015, desde=(0, 0, 0), rot=None, caida=None):
    """Lámina con algo de grosor y arrugas: toallas, trapos, ropa. Plano XZ (cuelga hacia -Z)."""
    c.marcar(bm)
    vs = []
    for j in range(filas + 1):
        fila = []
        for i in range(cols + 1):
            x = -ancho / 2 + ancho * i / cols
            z = -alto * j / filas
            y = ondas * math.sin(i * 2.1 + j * 1.3) + (caida(i / cols, j / filas) if caida else 0)
            fila.append(bm.verts.new((x, y, z)))
        vs.append(fila)
    caras = [bm.faces.new((vs[j][i], vs[j][i + 1], vs[j + 1][i + 1], vs[j + 1][i]))
             for j in range(filas) for i in range(cols)]
    for f in caras:
        f.normal_update()
    bmesh.ops.solidify(bm, geom=caras, thickness=0.008)
    return _poner(bm, c.nuevos(bm), mat, rot, desde)


R = lambda grados, eje="Z": Matrix.Rotation(math.radians(grados), 3, eje)  # noqa: E731


# ---------------------------------------------------------------- cocina

def microondas():
    bm = bmesh.new()
    caja(bm, (0, 0, 0.15), (0.48, 0.36, 0.28), BEIGE, 0.012)
    caja(bm, (-0.05, -0.181, 0.15), (0.30, 0.004, 0.19), NEGRO, 0)                 # ventana de la puerta
    caja(bm, (0.17, -0.181, 0.15), (0.10, 0.004, 0.22), GRIS, 0)                   # panel
    for z in (0.20, 0.15):
        cil(bm, (0.17, -0.186, z), 0.014, 0.012, NEGRO, rot=R(90, "X"))
    caja(bm, (0.105, -0.19, 0.15), (0.012, 0.02, 0.15), GRIS, 0.003)               # tirador
    for x in (-0.2, 0.2):
        for y in (-0.14, 0.14):
            cil(bm, (x, y, 0.005), 0.012, 0.01, NEGRO)
    return bm


def cafetera():
    """Cafetera italiana de aluminio, origen en la base."""
    bm = bmesh.new()
    torno(bm, [(0.045, 0), (0.05, 0.02), (0.042, 0.09), (0.035, 0.095), (0.002, 0.095)], METAL, 8)
    torno(bm, [(0.035, 0.095), (0.042, 0.10), (0.05, 0.19), (0.045, 0.20), (0.02, 0.215), (0.002, 0.215)], METAL, 8)
    caja(bm, (-0.03, -0.055, 0.17), (0.02, 0.03, 0.02), METAL, 0.004)              # pico
    caja(bm, (0.075, 0, 0.15), (0.015, 0.02, 0.09), NEGRO, 0.004)                  # asa
    barra(bm, (0.045, 0, 0.19), (0.075, 0, 0.19), 0.006, NEGRO)
    return bm


def escurreplatos():
    bm = bmesh.new()
    caja(bm, (0, 0, 0.01), (0.46, 0.32, 0.02), GRIS, 0.004)                        # bandeja
    for x in (-0.21, 0.21):
        for y in (-0.14, 0.14):
            barra(bm, (x, y, 0.02), (x, y, 0.16), 0.004, METAL)
    for y in (-0.14, 0.14):
        barra(bm, (-0.21, y, 0.16), (0.21, y, 0.16), 0.004, METAL)
    for x in (-0.21, 0.21):
        barra(bm, (x, -0.14, 0.16), (x, 0.14, 0.16), 0.004, METAL)
    for k in range(6):                                                              # platos de canto
        cil(bm, (-0.16 + k * 0.035, 0.03, 0.14), 0.11, 0.012, LOZA, lados=10, rot=R(90, "Y") @ R(-8 + k * 2, "X"))
    for k in range(2):                                                              # vasos boca abajo
        torno(bm, [(0.035, 0), (0.03, 0.10), (0.002, 0.10)], VIDRIO, 8, desde=(0.12 + k * 0.08, -0.08, 0.02))
    cil(bm, (0.17, 0.07, 0.10), 0.03, 0.14, ROJO, lados=6)                          # cubilete de cubiertos
    for k in range(4):
        barra(bm, (0.16 + k * 0.006, 0.07, 0.12), (0.15 + k * 0.01, 0.07 - k * 0.004, 0.24), 0.004, METAL, 4)
    return bm


def frutero():
    bm = bmesh.new()
    torno(bm, [(0.06, 0), (0.07, 0.01), (0.15, 0.07), (0.14, 0.075), (0.065, 0.02), (0.002, 0.02)], LOZA, 10)
    rnd = random.Random(3)
    for k in range(5):
        a = k * 1.25
        esfera(bm, (0.065 * math.cos(a), 0.065 * math.sin(a), 0.07 + (k % 2) * 0.02), (0.038,) * 3, NARANJA, 8)
    esfera(bm, (0.0, 0.0, 0.12), (0.04, 0.04, 0.037), ROJO, 8)                    # manzana
    for k in range(3):                                                              # plátanos
        barra(bm, (-0.10, -0.05 + k * 0.02, 0.10), (0.06, -0.09 + k * 0.02, 0.14), 0.016, AMARILLO, 5)
    rnd.random()
    return bm


def cubo_basura():
    bm = bmesh.new()
    torno(bm, [(0.13, 0), (0.15, 0.40), (0.155, 0.40), (0.155, 0.44), (0.02, 0.45), (0.002, 0.45)], BEIGE, 10)
    caja(bm, (0, -0.15, 0.02), (0.12, 0.08, 0.02), GRIS, 0.004)                    # pedal
    tela(bm, 0.18, 0.06, NEGRO, 1, 3, 0.01, desde=(0, -0.14, 0.44))                # bolsa que asoma
    return bm


def botellas_cocina():
    bm = bmesh.new()
    torno(bm, [(0.04, 0), (0.04, 0.20), (0.015, 0.26), (0.013, 0.29), (0.002, 0.29)], VIDRIO, 8, desde=(-0.06, 0, 0))
    caja(bm, (-0.06, -0.041, 0.10), (0.06, 0.004, 0.07), PAPEL, 0)                 # etiqueta
    torno(bm, [(0.04, 0), (0.04, 0.22), (0.02, 0.27), (0.015, 0.30), (0.002, 0.30)], AMARILLO, 8, desde=(0.04, 0.02, 0))
    cil(bm, (0.04, 0.02, 0.305), 0.016, 0.012, ROJO)
    torno(bm, [(0.03, 0), (0.03, 0.12), (0.012, 0.16), (0.002, 0.16)], LOZA, 8, desde=(0.0, -0.08, 0))  # salero
    return bm


def sarten():
    bm = bmesh.new()
    torno(bm, [(0.10, 0), (0.12, 0.04), (0.115, 0.042), (0.095, 0.006), (0.002, 0.006)], NEGRO, 10)
    caja(bm, (0.20, 0, 0.035), (0.17, 0.025, 0.02), NEGRO, 0.006)
    return bm


# ---------------------------------------------------------------- baño

def toallero():
    """Barra de toallero con una toalla doblada colgando (PARED)."""
    bm = bmesh.new()
    for x in (-0.28, 0.28):
        caja(bm, (x, -0.03, 0), (0.03, 0.06, 0.03), METAL, 0.004)
    barra(bm, (-0.29, -0.06, 0), (0.29, -0.06, 0), 0.01, METAL, 6)
    tela(bm, 0.42, 0.45, TOALLA, 5, 4, 0.01, desde=(0.02, -0.075, 0.0))
    tela(bm, 0.42, 0.40, TOALLA, 4, 4, 0.01, desde=(0.02, -0.048, 0.0))
    return bm


def vaso_cepillos():
    bm = bmesh.new()
    torno(bm, [(0.03, 0), (0.035, 0.10), (0.031, 0.10), (0.027, 0.006), (0.002, 0.006)], VIDRIO, 8)
    barra(bm, (0.005, 0, 0.01), (0.02, 0.01, 0.18), 0.004, AZUL, 4)
    barra(bm, (-0.005, 0, 0.01), (-0.02, -0.005, 0.18), 0.004, ROSA, 4)
    caja(bm, (0.08, 0.0, 0.015), (0.16, 0.035, 0.03), ROJO, 0.01, rot=R(10))        # pasta de dientes
    return bm


def botes_bano():
    bm = bmesh.new()
    caja(bm, (-0.07, 0, 0.09), (0.07, 0.045, 0.18), AZUL, 0.012)
    cil(bm, (-0.07, 0, 0.19), 0.015, 0.02, BEIGE)
    caja(bm, (0.0, 0.01, 0.075), (0.06, 0.04, 0.15), ROSA, 0.014)
    cil(bm, (0.0, 0.01, 0.16), 0.014, 0.02, BEIGE)
    caja(bm, (0.08, -0.01, 0.02), (0.09, 0.06, 0.035), BEIGE, 0.014)                # jabón
    return bm


def alfombrilla():
    bm = bmesh.new()
    caja(bm, (0, 0, 0.006), (0.65, 0.42, 0.012), ROSA, 0.01)
    return bm


def papel_higienico():
    """Portarrollos de pared con su rollo (PARED)."""
    bm = bmesh.new()
    caja(bm, (0, -0.01, 0), (0.16, 0.02, 0.05), METAL, 0.005)
    barra(bm, (-0.07, -0.06, 0), (0.07, -0.06, 0), 0.008, METAL)
    for x in (-0.07, 0.07):
        barra(bm, (x, -0.02, 0), (x, -0.06, 0), 0.006, METAL)
    cil(bm, (0, -0.06, 0), 0.055, 0.10, PAPEL, lados=10, rot=R(90, "Y"))
    tela(bm, 0.09, 0.10, PAPEL, 2, 1, 0.0, desde=(0, -0.115, -0.0))
    return bm


# ---------------------------------------------------------------- salón

def revistas():
    """Periódico doblado, dos revistas, el mando de la tele y un cenicero con colillas (sobre la mesa baja)."""
    bm = bmesh.new()
    caja(bm, (-0.12, 0.02, 0.006), (0.30, 0.22, 0.012), PAPEL, 0.002, rot=R(8))
    caja(bm, (-0.10, 0.03, 0.016), (0.21, 0.28, 0.006), ROJO, 0.002, rot=R(-12))
    caja(bm, (-0.11, 0.0, 0.022), (0.21, 0.28, 0.005), AZUL, 0.002, rot=R(20))
    caja(bm, (0.14, -0.07, 0.009), (0.05, 0.18, 0.018), NEGRO, 0.006, rot=R(-25))   # mando
    torno(bm, [(0.05, 0), (0.06, 0.02), (0.055, 0.025), (0.04, 0.008), (0.002, 0.008)], VIDRIO, 8,
          desde=(0.15, 0.10, 0))                                                    # cenicero
    for k in range(3):
        barra(bm, (0.15 + 0.01 * k, 0.10, 0.012), (0.15 + 0.04 * math.cos(k * 2), 0.10 + 0.04 * math.sin(k * 2), 0.016),
              0.004, PAPEL, 4)
    return bm


def planta():
    """Potos en maceta de barro: hojas en abanico, bajas y caídas (PSX: triángulos)."""
    bm = bmesh.new()
    torno(bm, [(0.10, 0), (0.14, 0.24), (0.15, 0.25), (0.15, 0.27), (0.13, 0.27), (0.12, 0.24), (0.002, 0.24)],
          TIERRA, 8)
    rnd = random.Random(7)
    c.marcar(bm)
    for k in range(26):
        a = rnd.uniform(0, 2 * math.pi)
        r0 = rnd.uniform(0.0, 0.08)
        largo = rnd.uniform(0.18, 0.45)
        sube = rnd.uniform(-0.25, 0.35)
        base = Vector((r0 * math.cos(a), r0 * math.sin(a), 0.25))
        d = Vector((math.cos(a), math.sin(a), sube)).normalized()
        punta = base + d * largo
        lado = d.cross(Vector((0, 0, 1))).normalized() * rnd.uniform(0.04, 0.07)
        m = base + d * largo * 0.55 + Vector((0, 0, 0.03))
        vs = [bm.verts.new(base), bm.verts.new(m + lado), bm.verts.new(punta), bm.verts.new(m - lado)]
        bm.faces.new(vs)
    c.asignar(bm, {f for v in c.nuevos(bm) for f in v.link_faces}, VERDE)
    return bm


def telefono():
    """Teléfono fijo de góndola, beige (mueble del recibidor o mesilla)."""
    bm = bmesh.new()
    caja(bm, (0, 0, 0.035), (0.20, 0.22, 0.07), BEIGE, 0.012)
    caja(bm, (0, -0.03, 0.074), (0.09, 0.10, 0.008), GRIS, 0.002)                 # teclado
    for i in range(3):
        for j in range(4):
            caja(bm, (-0.025 + i * 0.025, -0.065 + j * 0.022, 0.08), (0.016, 0.014, 0.006), BEIGE, 0.002)
    caja(bm, (0, 0.06, 0.09), (0.22, 0.05, 0.035), BEIGE, 0.012)                    # auricular
    for x in (-0.09, 0.09):
        caja(bm, (x, 0.06, 0.08), (0.05, 0.06, 0.045), BEIGE, 0.012)
    for k in range(6):                                                              # cable rizado
        toro(bm, (0.11 + k * 0.012, 0.02, 0.01), 0.008, 0.002, NEGRO, 6, 3, rot=R(90, "Y"))
    return bm


# ---------------------------------------------------------------- dormitorio

def zapatillas():
    bm = bmesh.new()
    for x, rz, mat in ((-0.07, 8, MARRON), (0.07, -5, MARRON)):
        caja(bm, (x, 0, 0.012), (0.10, 0.27, 0.024), NEGRO, 0.01, rot=R(rz))
        esfera(bm, (x - math.sin(math.radians(rz)) * 0.06, -0.06, 0.035), (0.05, 0.07, 0.03), mat, 8, rot=R(rz))
    return bm


def despertador():
    bm = bmesh.new()
    cil(bm, (0, 0, 0.06), 0.055, 0.04, ROJO, lados=10, rot=R(90, "X"))
    cil(bm, (0, -0.021, 0.06), 0.045, 0.002, PAPEL, lados=10, rot=R(90, "X"))
    for x in (-0.03, 0.03):
        esfera(bm, (x, 0, 0.12), (0.022, 0.012, 0.016), METAL, 6)
        barra(bm, (x, 0, 0.01), (x * 1.4, -0.01, 0.03), 0.004, METAL, 4)
    caja(bm, (0.0, -0.024, 0.07), (0.003, 0.002, 0.03), NEGRO, 0)
    caja(bm, (0.012, -0.024, 0.06), (0.025, 0.002, 0.003), NEGRO, 0)
    return bm


def silla_ropa():
    """Silla de madera con una chaqueta de punto y unos vaqueros encima (dormitorio)."""
    bm = bmesh.new()
    caja(bm, (0, 0, 0.45), (0.42, 0.40, 0.03), MADERA_OSC, 0.006)
    for x in (-0.18, 0.18):
        for y in (-0.17, 0.17):
            caja(bm, (x, y, 0.22), (0.03, 0.03, 0.44), MADERA_OSC, 0.004)
        caja(bm, (x, 0.18, 0.70), (0.03, 0.03, 0.50), MADERA_OSC, 0.004)
    for z in (0.72, 0.90):
        caja(bm, (0, 0.18, z), (0.36, 0.02, 0.06), MADERA_OSC, 0.004)
    # Chaqueta colgada del respaldo y vaqueros doblados en el asiento
    tela(bm, 0.40, 0.45, ROSA, 4, 4, 0.02, desde=(0, 0.20, 0.96),
         caida=lambda u, v: -0.04 * v + 0.02 * math.sin(u * 6))
    tela(bm, 0.36, 0.20, ROSA, 2, 4, 0.01, desde=(0, 0.17, 0.96), rot=R(180),
         caida=lambda u, v: 0.0)
    caja(bm, (0.02, -0.02, 0.48), (0.34, 0.28, 0.04), AZUL, 0.012, rot=R(6))
    tela(bm, 0.18, 0.30, AZUL, 3, 2, 0.01, desde=(0.08, -0.17, 0.48))             # pernera que cae
    return bm


# ---------------------------------------------------------------- recibidor

def paraguero():
    bm = bmesh.new()
    torno(bm, [(0.11, 0), (0.12, 0.50), (0.11, 0.50), (0.10, 0.02), (0.002, 0.02)], METAL, 8)
    for k, (x, y, mat) in enumerate(((0.03, 0.02, NEGRO), (-0.04, -0.01, AZUL))):
        barra(bm, (x, y, 0.03), (x * 2, y * 2, 0.80 - k * 0.06), 0.008, METAL, 4)
        torno(bm, [(0.002, 0.30), (0.04, 0.42), (0.035, 0.60), (0.008, 0.66), (0.002, 0.66)], mat, 6,
              desde=(x * 1.5, y * 1.5, 0))
        toro(bm, (x * 2 + 0.025, y * 2, 0.80 - k * 0.06), 0.025, 0.006, MARRON, 8, 4, rot=R(90, "X"))
    return bm


def zapatos():
    """Zapatos de él (negros) y botines de ella junto a la puerta."""
    bm = bmesh.new()
    for x, rz in ((-0.20, 4), (-0.09, -3)):
        caja(bm, (x, 0, 0.012), (0.10, 0.29, 0.024), GOMA, 0.008, rot=R(rz))
        esfera(bm, (x, -0.06, 0.04), (0.048, 0.09, 0.04), NEGRO, 8, rot=R(rz))
        caja(bm, (x, 0.07, 0.05), (0.09, 0.12, 0.07), NEGRO, 0.02, rot=R(rz))
    for x, rz in ((0.08, -10), (0.19, 15)):
        caja(bm, (x, 0.02, 0.01), (0.08, 0.24, 0.02), GOMA, 0.008, rot=R(rz))
        esfera(bm, (x, -0.04, 0.035), (0.04, 0.07, 0.035), MARRON, 8, rot=R(rz))
        caja(bm, (x + math.sin(math.radians(-rz)) * 0.06, 0.07, 0.08), (0.075, 0.10, 0.15), MARRON, 0.02, rot=R(rz))
    return bm


# ---------------------------------------------------------------- garaje

def bicicleta():
    """Bici vieja de paseo apoyada en la pata (de lado, a lo largo de X)."""
    bm = bmesh.new()
    for x in (-0.52, 0.52):
        toro(bm, (x, 0, 0.34), 0.31, 0.018, GOMA, 16, 4, rot=R(90, "X"))
        cil(bm, (x, 0, 0.34), 0.02, 0.06, METAL, rot=R(90, "X"))
        for k in range(6):
            a = k * math.pi / 6
            barra(bm, (x - 0.30 * math.cos(a), 0, 0.34 - 0.30 * math.sin(a)),
                  (x + 0.30 * math.cos(a), 0, 0.34 + 0.30 * math.sin(a)), 0.002, METAL, 3)
    pedal = Vector((-0.05, 0, 0.30))
    sillin = Vector((-0.17, 0, 0.82))
    manillar = Vector((0.40, 0, 0.88))
    for a, b in ((Vector((-0.52, 0, 0.34)), pedal), (pedal, sillin), (sillin, Vector((0.36, 0, 0.72))),
                 (pedal, Vector((0.38, 0, 0.66))), (Vector((-0.52, 0, 0.34)), Vector((-0.20, 0, 0.74))),
                 (Vector((0.52, 0, 0.34)), manillar)):
        barra(bm, a, b, 0.016, ROJO, 6)
    caja(bm, (sillin.x - 0.02, 0, sillin.z + 0.04), (0.24, 0.12, 0.05), NEGRO, 0.02)
    barra(bm, manillar + Vector((0, -0.25, 0)), manillar + Vector((0, 0.25, 0)), 0.012, METAL, 6)
    cil(bm, (pedal.x, 0, pedal.z), 0.09, 0.01, METAL, lados=10, rot=R(90, "X"))
    barra(bm, (-0.52, 0, 0.66), (0.0, 0, 0.66), 0.01, METAL)                       # guardabarros-portabultos
    barra(bm, (-0.05, -0.03, 0.30), (-0.13, -0.12, 0.0), 0.008, METAL)              # pata de cabra
    return bm


def neumaticos():
    bm = bmesh.new()
    for k in range(3):
        toro(bm, (0.01 * k, 0.012 * k, 0.09 + k * 0.17), 0.24, 0.085, GOMA, 14, 6)
    return bm


def bidon():
    bm = bmesh.new()
    caja(bm, (0, 0, 0.17), (0.32, 0.17, 0.34), ROJO, 0.02)
    caja(bm, (0.04, 0, 0.36), (0.16, 0.03, 0.05), ROJO, 0.01)                      # asa
    cil(bm, (-0.12, 0, 0.36), 0.025, 0.05, NEGRO)
    return bm


def herramientas():
    """Tablero perforado con herramientas colgadas (PARED), 1,0 x 0,6 m."""
    bm = bmesh.new()
    caja(bm, (0, -0.01, 0), (1.0, 0.02, 0.6), CARTON, 0.003)
    caja(bm, (-0.38, -0.03, 0.10), (0.03, 0.02, 0.24), MADERA, 0.006)               # martillo
    caja(bm, (-0.38, -0.035, 0.22), (0.12, 0.03, 0.035), METAL, 0.006)
    caja(bm, (-0.20, -0.03, 0.05), (0.03, 0.02, 0.30), METAL, 0.004)                # llave inglesa
    caja(bm, (-0.20, -0.03, 0.21), (0.07, 0.02, 0.04), METAL, 0.006)
    for k in range(4):                                                              # destornilladores
        caja(bm, (-0.02 + k * 0.06, -0.03, 0.12), (0.025, 0.025, 0.10), (ROJO, AMARILLO, AZUL, NEGRO)[k], 0.006)
        barra(bm, (-0.02 + k * 0.06, -0.03, 0.07), (-0.02 + k * 0.06, -0.03, -0.07), 0.004, METAL, 4)
    caja(bm, (0.33, -0.04, 0.0), (0.22, 0.04, 0.14), ROJO, 0.01)                    # caja de herramientas pequeña
    toro(bm, (0.30, -0.03, 0.20), 0.08, 0.012, AMARILLO, 12, 4, rot=R(90, "X"))    # rollo de cable
    caja(bm, (0.1, -0.03, -0.17), (0.22, 0.02, 0.10), METAL, 0.004)                 # sierra
    caja(bm, (-0.03, -0.03, -0.17), (0.07, 0.03, 0.06), MADERA, 0.008)
    return bm


# ---------------------------------------------------------------- exterior

def buzon():
    """Buzón metálico en su poste de madera, junto a la acera; boca hacia +Z de Unity."""
    bm = bmesh.new()
    caja(bm, (0, 0, 0.55), (0.08, 0.08, 1.1), MADERA, 0.006)
    caja(bm, (0, 0, 1.17), (0.22, 0.45, 0.12), GRIS, 0.004)                         # cuerpo
    cil(bm, (0, 0, 1.23), 0.11, 0.45, GRIS, lados=10, rot=R(90, "X"))              # techo redondo
    caja(bm, (0, -0.226, 1.2), (0.20, 0.006, 0.17), GRIS, 0.004)                   # puerta
    caja(bm, (0.12, 0.05, 1.27), (0.01, 0.03, 0.14), ROJO, 0.003)                   # banderita
    return bm


def cubos_basura():
    """Dos contenedores de ruedas (verde y gris) con la tapa cerrada, a lo largo de X."""
    bm = bmesh.new()
    for x, mat in ((-0.36, CUBO_VERDE), (0.36, GRIS)):
        c.marcar(bm)
        caja(bm, (x, 0, 0.50), (0.58, 0.72, 0.96), mat, 0.03)
        for v in c.nuevos(bm):
            if v.co.z < 0.3:
                v.co.x = x + (v.co.x - x) * 0.9
                v.co.y *= 0.9
        caja(bm, (x, -0.02, 1.0), (0.62, 0.78, 0.05), mat, 0.02)
        caja(bm, (x, 0.40, 0.95), (0.56, 0.06, 0.06), mat, 0.02)                    # asa
        for s in (-1, 1):
            cil(bm, (x + s * 0.24, 0.30, 0.10), 0.10, 0.05, GOMA, lados=10, rot=R(90, "Y"))
    return bm


def valla():
    """Tramo de valla de madera de 2 m (de x = 0 a x = -2 en Blender: en Unity de 0 a +2 m), 1 m de alto."""
    bm = bmesh.new()
    rnd = random.Random(5)
    for x in (0.0, -2.0):
        caja(bm, (x - 0.0, 0, 0.55), (0.09, 0.09, 1.1), MADERA, 0.006)
    for z in (0.25, 0.80):
        caja(bm, (-1.0, 0.05, z), (2.0, 0.025, 0.08), MADERA, 0.004)
    n = 18
    for k in range(n):
        x = -0.06 - k * (1.88 / (n - 1))
        alto = 1.0 + rnd.uniform(-0.03, 0.02)
        caja(bm, (x, 0.075, alto / 2 + 0.02), (0.09, 0.02, alto), MADERA, 0.004,
             rot=R(rnd.uniform(-2.5, 2.5), "Y"))
    return bm


def maceta_seca():
    """Maceta grande de barro con una planta seca (porche)."""
    bm = bmesh.new()
    torno(bm, [(0.14, 0), (0.20, 0.36), (0.22, 0.38), (0.22, 0.42), (0.19, 0.42), (0.18, 0.38), (0.002, 0.38)],
          TIERRA, 8)
    rnd = random.Random(9)
    for k in range(14):
        a = rnd.uniform(0, 2 * math.pi)
        b = Vector((0.02 * math.cos(a), 0.02 * math.sin(a), 0.38))
        p = b + Vector((math.cos(a) * rnd.uniform(0.05, 0.25), math.sin(a) * rnd.uniform(0.05, 0.25),
                        rnd.uniform(0.15, 0.55)))
        barra(bm, b, p, 0.006, MARRON, 3)
    return bm


def farola():
    """Farola de calle de 3,6 m con brazo y farol (la bombilla es el objeto "Luz" aparte, para la emisión)."""
    bm = bmesh.new()
    torno(bm, [(0.12, 0), (0.12, 0.25), (0.08, 0.30), (0.06, 0.32), (0.06, 3.3), (0.045, 3.35), (0.002, 3.35)],
          NEGRO, 8)
    barra(bm, (0, 0, 3.25), (0, -0.55, 3.45), 0.03, NEGRO, 6)
    barra(bm, (0, -0.55, 3.45), (0, -0.62, 3.40), 0.03, NEGRO, 6)
    torno(bm, [(0.002, 3.13), (0.10, 3.20), (0.22, 3.30), (0.20, 3.36), (0.06, 3.42), (0.002, 3.42)], GRIS, 8,
          desde=(0, -0.62, 0))
    return bm


def contraventanas():
    """Par de contraventanas de lamas abiertas a los lados de una ventana de 1,0 m (PARED, origen en el centro
    de la ventana): cada hoja 0,5 x 1,2, desconchadas."""
    bm = bmesh.new()
    for s in (-1, 1):
        x = s * (0.5 + 0.27)
        caja(bm, (x, -0.02, 0), (0.48, 0.03, 1.2), CUBO_VERDE, 0.004)
        for k in range(14):
            caja(bm, (x, -0.04, -0.52 + k * 0.08), (0.40, 0.012, 0.05), CUBO_VERDE, 0.002, rot=R(-25, "X"))
        for z in (-0.4, 0.4):
            caja(bm, (s * 0.52, -0.03, z), (0.08, 0.01, 0.025), NEGRO, 0)
    return bm


def bajante():
    """Canalón de 1 m de largo (a lo largo de X) y bajante de 3 m hasta el suelo (PARED; origen abajo)."""
    bm = bmesh.new()
    cil(bm, (0, -0.06, 1.5), 0.04, 3.0, GRIS, lados=6)
    for z in (0.5, 1.5, 2.5):
        caja(bm, (0, -0.03, z), (0.10, 0.06, 0.02), NEGRO, 0)
    caja(bm, (0, -0.10, 0.06), (0.10, 0.12, 0.05), GRIS, 0.004, rot=R(-30, "X"))   # codo de salida
    caja(bm, (-0.5, -0.07, 3.0), (1.0, 0.12, 0.08), GRIS, 0.004)
    return bm


PIEZAS = {
    # cocina
    "Microondas": microondas, "Cafetera": cafetera, "Escurreplatos": escurreplatos, "Frutero": frutero,
    "CuboBasura": cubo_basura, "BotellasCocina": botellas_cocina, "Sarten": sarten,
    # baño
    "Toallero": toallero, "VasoCepillos": vaso_cepillos, "BotesBano": botes_bano, "Alfombrilla": alfombrilla,
    "PapelHigienico": papel_higienico,
    # salón y recibidor
    "Revistas": revistas, "Planta": planta, "Telefono": telefono, "Paraguero": paraguero, "Zapatos": zapatos,
    # dormitorio
    "Zapatillas": zapatillas, "Despertador": despertador, "SillaRopa": silla_ropa,
    # garaje
    "Bicicleta": bicicleta, "Neumaticos": neumaticos, "Bidon": bidon, "Herramientas": herramientas,
    # exterior
    "Buzon": buzon, "CubosBasura": cubos_basura, "Valla": valla, "MacetaSeca": maceta_seca, "Farola": farola,
    "Contraventanas": contraventanas, "Bajante": bajante,
}


def main(nombre):
    c.escena_vacia()
    mats = materiales()
    bm = PIEZAS[nombre]()
    ob = c.objeto(nombre, bm, mats)
    for p in ob.data.polygons:
        p.use_smooth = p.material_index in (LOZA, TOALLA, ROSA, MARRON, NARANJA, ROJO, AMARILLO, VIDRIO) \
            and len(p.vertices) == 4
    usados = sorted({p.material_index for p in ob.data.polygons})
    viejos, idx = list(ob.data.materials), {o: n for n, o in enumerate(usados)}
    nuevos = [idx[p.material_index] for p in ob.data.polygons]
    ob.data.materials.clear()  # (pone los índices a 0: se reasignan después)
    for i in usados:
        ob.data.materials.append(viejos[i])
    for p, i in zip(ob.data.polygons, nuevos):
        p.material_index = i
    hornear.atlas(ob, nombre, tam=1024, margen=0.006)
    objs = [ob]
    if nombre == "Farola":
        bb = bmesh.new()
        c.torno(bb, [(0.002, 3.16), (0.09, 3.22), (0.12, 3.28), (0.002, 3.30)], lados=8)
        bmesh.ops.translate(bb, verts=bb.verts, vec=(0, -0.62, 0))
        objs.append(c.objeto("Luz", bb, [hornear.material_liso("Farola_Luz", (1.0, 0.75, 0.45))], suave=True))
    ruta = c.exportar_fbx(nombre, objs)
    print(f"Exportado {ruta} ({sum(len(p.vertices) - 2 for o in objs for p in o.data.polygons)} triángulos)")


if __name__ == "__main__":
    for n in (sys.argv[1:] or list(PIEZAS)):
        main(n)
