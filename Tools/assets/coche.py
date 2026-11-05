"""Coche: berlina genérica de los 80, cuadrada, con faros rectangulares y parrilla cromada (no imita ningún modelo real).

Sustituye a la malla provisional Coche de HouseBuilder (coche de Chevas en el garaje y
los dos coches de la calle). Misma colocación: origen en el suelo, en el centro del coche,
morro hacia +Z en Unity. Medidas: 4,36 x 1,72 x 1,38 m (con paragolpes), batalla 2,55 m (cabe en el garaje
de 4,4 m de fondo).

Tiene interior (asientos, salpicadero, volante) porque en los actos 2 y 3 Roberta aparece
sentada al volante. El conductor va a la izquierda (x = -0,37 en Unity).
Asiento del conductor, en coordenadas locales de Unity: superficie del cojín a 0,38 m,
centro del cojín en (x -0,37, z -0,05). Para la figura sentada de HouseBuilder (muslos a 0,48)
el punto de colocación es local (-0,37, -0,10, -0,2).

Sale en tres colores (mismo modelo, distinto material de pintura):
CocheRojo.fbx (Chevas), CocheAzul.fbx y CocheGris.fbx (calle).
El material Coche_Cristal viene con alfa 0,6: en Unity ponerlo transparente.

Uso:  python Tools/assets/coche.py
"""
import math
import os
import sys

import bpy
import bmesh
import numpy as np
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(__file__))
import comun as c  # noqa: E402

# Blender: X ancho (x de Unity = -X), Y largo con el morro hacia -Y, Z arriba.
YF, YR = -1.33, 1.22      # ejes delantero y trasero
R_RUEDA = 0.29
VIA = 0.71                # mitad de la vía
COND = 0.37               # X del conductor en Blender (= -0,37 en Unity)
ASIENTO = 0.38            # altura del cojín
SUELO_INT = 0.22          # suelo del habitáculo
CINTURA_D, CINTURA_T = 0.80, 0.87  # línea de cintura delante y detrás de las ventanillas
TECHO = 1.37
TECHO_X = 0.69            # media anchura del techo (poca caída: carrocería cuadrada)
YA, YT0, YT1, YC = -0.98, -0.20, 0.64, 1.18  # base del parabrisas, techo delante y detrás, base de la luneta

# Índices de material (todas las piezas comparten la misma lista)
PINTURA, CRISTAL, NEGRO, CROMO, FARO, PILOTO, NEUMATICO, TAPACUBOS, INTERIOR, MATRICULA, INTERMITENTE = range(11)

# Secciones de la carrocería baja: (y, z abajo, z arriba, media anchura)
SECCIONES = [
    (-2.135, 0.30, 0.50, 0.78),
    (-2.125, 0.24, 0.69, 0.82),
    (-2.105, 0.22, 0.715, 0.835),
    (-2.00, 0.20, 0.725, 0.84),
    (-1.40, 0.19, 0.765, 0.84),
    (-0.98, 0.18, 0.80, 0.84),
    (-0.30, 0.17, 0.83, 0.84),
    (0.50, 0.17, 0.85, 0.84),
    (1.15, 0.18, 0.87, 0.84),
    (1.60, 0.20, 0.885, 0.84),
    (2.03, 0.22, 0.885, 0.835),
    (2.105, 0.24, 0.87, 0.82),
    (2.13, 0.30, 0.60, 0.80),
]


def seccion(z0, z1, hw):
    """Contorno cerrado de una sección (x, z), redondeado en las esquinas."""
    h = z1 - z0
    der = [(hw * 0.94, z0), (hw * 0.99, z0 + min(0.03, h * 0.1)), (hw, z0 + h * 0.3),
           (hw, z1 - min(0.05, h * 0.15)), (hw * 0.988, z1 - 0.01), (hw * 0.95, z1 - 0.001),
           (hw * 0.5, z1 + 0.006)]
    izq = [(-x, z) for x, z in reversed(der)]
    return [(0.0, z0)] + der + [(0.0, z1 + 0.008)] + izq


def loft(bm, secciones, mat):
    anillos = []
    for y, z0, z1, hw in secciones:
        anillos.append([bm.verts.new((x, y, z)) for x, z in seccion(z0, z1, hw)])
    caras = []
    n = len(anillos[0])
    for a, b in zip(anillos, anillos[1:]):
        for i in range(n):
            j = (i + 1) % n
            caras.append(bm.faces.new((a[i], a[j], b[j], b[i])))
    caras.append(bm.faces.new(list(reversed(anillos[0]))))
    caras.append(bm.faces.new(anillos[-1]))
    c.asignar(bm, caras, mat)
    return caras


def lado_x(z, y=0.0):
    """X del costado del habitáculo (cristal) a la altura z: entra hacia el techo."""
    return 0.80 - (z - CINTURA_D) * ((0.80 - TECHO_X) / (TECHO - CINTURA_D))


def barra(bm, p0, p1, ancho, grosor, fuera, mat):
    """Listón entre p0 y p1. 'fuera' es la dirección hacia la que mira su cara exterior."""
    p0, p1, fuera = Vector(p0), Vector(p1), Vector(fuera).normalized()
    d = (p1 - p0)
    largo = d.length
    d.normalize()
    w = d.cross(fuera).normalized()
    n = w.cross(d).normalized()
    m = Matrix((w, d, n)).transposed()
    vs = c.caja(bm, (0, 0, 0), (ancho, largo, grosor))
    bmesh.ops.transform(bm, matrix=m.to_4x4(), verts=vs)
    bmesh.ops.translate(bm, vec=(p0 + p1) / 2 + n * (grosor / 2), verts=vs)
    c.asignar(bm, {f for v in vs for f in v.link_faces}, mat)
    return vs


def caja_mat(bm, centro, tam, mat, biselado=0.0, segmentos=1, rot=None):
    antes = set(bm.verts)
    vs = c.caja(bm, (0, 0, 0), tam)
    if rot is not None:
        bmesh.ops.transform(bm, matrix=rot.to_4x4(), verts=vs)
    bmesh.ops.translate(bm, vec=centro, verts=vs)
    if biselado > 0:
        aristas = list({e for v in vs for e in v.link_edges})
        bmesh.ops.bevel(bm, geom=aristas, offset=biselado, segments=segmentos,
                        profile=0.5, affect="EDGES", clamp_overlap=True)
    nuevos = [v for v in bm.verts if v not in antes]
    c.asignar(bm, {f for v in nuevos for f in v.link_faces}, mat)
    return nuevos


def revolucion(bm, perfil, lados, cerrado=False):
    """Revoluciona perfil [(r, z)] alrededor de Z; devuelve los anillos."""
    anillos = []
    for r, z in perfil:
        anillos.append([bm.verts.new((r * math.cos(2 * math.pi * i / lados),
                                      r * math.sin(2 * math.pi * i / lados), z)) for i in range(lados)])
    pares = list(zip(anillos, anillos[1:]))
    if cerrado:
        pares.append((anillos[-1], anillos[0]))
    for a, b in pares:
        for i in range(lados):
            j = (i + 1) % lados
            bm.faces.new((a[i], a[j], b[j], b[i]))
    return anillos


# ---------- piezas ----------

def carroceria(mats):
    bm = bmesh.new()
    loft(bm, SECCIONES, PINTURA)
    ob = c.objeto("Carroceria", bm, mats, uv_metros=2.0)

    # Habitáculo hueco (se ve por los cristales) y pasos de rueda.
    cortes = []
    for centro, tam in (((0, -0.01, (SUELO_INT + 1.3) / 2), (1.42, 1.74, 1.3 - SUELO_INT)),
                        ((0, 0.97, (SUELO_INT + 0.15 + 1.3) / 2), (1.10, 0.24, 1.3 - SUELO_INT - 0.15))):
        hb = bmesh.new()
        caja_mat(hb, centro, tam, INTERIOR)
        cortes.append(c.objeto("CorteHabitaculo", hb, mats))
    for y in (YF, YR):
        for s in (-1, 1):
            rb = bmesh.new()
            r = bmesh.ops.create_cone(rb, cap_ends=True, segments=28, radius1=0.335, radius2=0.335, depth=0.40)
            bmesh.ops.rotate(rb, verts=r["verts"], cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, "Y"))
            bmesh.ops.translate(rb, verts=r["verts"], vec=(s * 0.78, y, R_RUEDA + 0.01))
            c.asignar(rb, rb.faces, NEGRO)
            cortes.append(c.objeto("CorteRueda", rb, mats))
    for corte in cortes:
        mod = ob.modifiers.new("Corte", "BOOLEAN")
        mod.operation = "DIFFERENCE"
        mod.solver = "EXACT"
        mod.material_mode = "TRANSFER"
        mod.object = corte
        bpy.context.view_layer.objects.active = ob
        bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.data.objects.remove(corte)
    return ob


def habitaculo(mats):
    """Cristales y techo: envolvente convexa entre la cintura y el techo."""
    bm = bmesh.new()
    pts = []
    for s in (-1, 1):
        pts += [(s * 0.80, YA, CINTURA_D), (s * 0.80, YC, CINTURA_T),
                (s * TECHO_X, YT0, TECHO - 0.005), (s * TECHO_X, YT1, TECHO)]
    pts += [(0, YT0 + 0.01, TECHO + 0.008), (0, YT1 - 0.01, TECHO + 0.01)]
    vs = [bm.verts.new(p) for p in pts]  # noqa
    r = bmesh.ops.convex_hull(bm, input=vs)
    bmesh.ops.delete(bm, geom=[v for v in r["geom_interior"] + r["geom_unused"] if isinstance(v, bmesh.types.BMVert)], context="VERTS")
    # Montante B y montante C (inclinado), cortando los costados
    planos = [((0, 0.13, CINTURA_D), (0, 1, 0.12)), ((0, 0.21, CINTURA_D), (0, 1, 0.12)),
              ((0, 0.80, CINTURA_D), (0, 1, 0.45))]
    for co, no in planos:
        geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
        bmesh.ops.bisect_plane(bm, geom=geom, plane_co=co, plane_no=no)
    bm.normal_update()
    abajo = []
    for f in bm.faces:
        n, cen = f.normal, f.calc_center_median()
        if n.z < -0.5:
            abajo.append(f)
            continue
        f.material_index = CRISTAL
        if n.z > 0.85 and cen.z > TECHO - 0.02:
            f.material_index = PINTURA  # techo
        elif abs(n.x) > 0.6:
            dy = lambda co, no: (cen - Vector(co)).dot(Vector(no).normalized())
            if dy(*planos[0]) > 0 and dy(*planos[1]) < 0:
                f.material_index = PINTURA
            elif dy(*planos[2]) > 0:
                f.material_index = PINTURA
    bmesh.ops.delete(bm, geom=abajo, context="FACES_ONLY")

    # Montantes A, gomas de las ventanillas y del parabrisas
    for s in (-1, 1):
        a0, a1 = Vector((s * 0.80, YA, CINTURA_D)), Vector((s * TECHO_X, YT0, TECHO - 0.005))
        barra(bm, a0, a1, 0.06, 0.012, Vector((s * 0.9, -0.35, 0.3)), PINTURA)
        lat = Vector((s * 0.97, 0, 0.2))
        # Molduras cromadas: canaleta del techo y cintura
        barra(bm, (s * (TECHO_X + 0.004), YT0, TECHO - 0.012), (s * (TECHO_X + 0.004), YT1, TECHO - 0.012), 0.022, 0.008, lat, CROMO)
        barra(bm, (s * 0.802, YA + 0.04, CINTURA_D + 0.008), (s * 0.802, YC - 0.12, CINTURA_T - 0.005), 0.018, 0.008, lat, CROMO)
    # Marcos cromados del parabrisas y de la luneta
    fr = Vector((0, -0.6, 0.8))
    barra(bm, (-0.79, YA - 0.005, CINTURA_D + 0.01), (0.79, YA - 0.005, CINTURA_D + 0.01), 0.025, 0.008, fr, CROMO)
    barra(bm, (-TECHO_X, YT0 - 0.004, TECHO - 0.012), (TECHO_X, YT0 - 0.004, TECHO - 0.012), 0.022, 0.008, fr, CROMO)
    tr = Vector((0, 0.7, 0.7))
    barra(bm, (-TECHO_X, YT1 + 0.004, TECHO - 0.012), (TECHO_X, YT1 + 0.004, TECHO - 0.012), 0.022, 0.008, tr, CROMO)
    barra(bm, (-0.79, YC + 0.005, CINTURA_T + 0.01), (0.79, YC + 0.005, CINTURA_T + 0.01), 0.025, 0.008, tr, CROMO)
    return c.objeto("Habitaculo", bm, mats, uv_metros=2.0)


def rueda(bm, x, y, s):
    """Neumático 175/70 R13 con tapacubos. s = 1 lado derecho (+X), -1 izquierdo."""
    antes = set(bm.verts)
    perfil = [(0.205, -0.075), (0.25, -0.0875), (0.278, -0.082), (R_RUEDA, -0.055), (R_RUEDA, 0.055),
              (0.278, 0.082), (0.25, 0.0875), (0.205, 0.075)]
    anillos = revolucion(bm, perfil, 28, cerrado=False)
    neum = {f for a in anillos for v in a for f in v.link_faces}
    tapa = [(0.205, 0.075), (0.19, 0.082), (0.15, 0.084), (0.09, 0.090), (0.05, 0.096), (0.03, 0.097), (0.0, 0.097)]
    anillos_t = revolucion(bm, tapa, 28)
    # fondo de la llanta (cara interior)
    bm.faces.new(list(reversed(anillos[0])))
    tapas = {f for a in anillos_t for v in a for f in v.link_faces} - neum
    for f in neum:
        f.material_index = NEUMATICO
    for f in tapas:
        f.material_index = TAPACUBOS
    nuevos = [v for v in bm.verts if v not in antes]
    bmesh.ops.rotate(bm, verts=nuevos, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90 * s), 3, "Y"))
    bmesh.ops.translate(bm, verts=nuevos, vec=(x, y, R_RUEDA))


def detalles(mats):
    bm = bmesh.new()
    # Paragolpes negros, finos y envolventes
    loft(bm, [(-2.175, 0.30, 0.44, 0.74), (-2.165, 0.285, 0.46, 0.83), (-2.06, 0.28, 0.465, 0.86),
              (-1.74, 0.29, 0.455, 0.86)], NEGRO)
    loft(bm, [(1.64, 0.30, 0.47, 0.86), (2.08, 0.29, 0.48, 0.86), (2.17, 0.295, 0.47, 0.83),
              (2.18, 0.31, 0.45, 0.74)], NEGRO)
    # Frontal: faros rectangulares a ras y parrilla cromada en cruz entre ellos
    zf0, zf1 = 0.52, 0.675
    zc = (zf0 + zf1) / 2
    hf = zf1 - zf0
    yf = -2.128
    for s in (-1, 1):
        xc = s * 0.585
        caja_mat(bm, (xc, yf + 0.01, zc), (0.42, 0.03, hf - 0.02), FARO)
        caja_mat(bm, (xc, yf - 0.002, zf1 - 0.006), (0.44, 0.012, 0.012), CROMO)
        caja_mat(bm, (xc, yf - 0.002, zf0 + 0.006), (0.44, 0.012, 0.012), CROMO)
        caja_mat(bm, (s * 0.802, yf - 0.002, zc), (0.012, 0.012, hf), CROMO)
        caja_mat(bm, (s * 0.368, yf - 0.002, zc), (0.012, 0.012, hf), CROMO)
        # Intermitentes naranjas en el paragolpes y en el costado
        caja_mat(bm, (s * 0.62, -2.17, 0.40), (0.14, 0.02, 0.05), INTERMITENTE)
        caja_mat(bm, (s * 0.842, -1.88, 0.62), (0.006, 0.08, 0.035), INTERMITENTE)
        # Pilotos traseros: franja ancha roja con el intermitente naranja por fuera
        caja_mat(bm, (s * 0.56, 2.115, 0.725), (0.40, 0.03, 0.13), PILOTO)
        caja_mat(bm, (s * 0.795, 2.112, 0.725), (0.07, 0.03, 0.13), INTERMITENTE)
    caja_mat(bm, (0, yf - 0.004, zc), (0.70, 0.01, hf), NEGRO)
    for z in (zf0 + 0.005, zc, zf1 - 0.005):
        caja_mat(bm, (0, yf - 0.009, z), (0.72, 0.014, 0.014), CROMO)
    for x in (-0.356, 0.0, 0.356):
        caja_mat(bm, (x, yf - 0.009, zc), (0.016, 0.014, hf), CROMO)
    for z in np.linspace(zf0 + 0.025, zf1 - 0.025, 5):
        caja_mat(bm, (0, yf - 0.012, z), (0.70, 0.006, 0.006), CROMO)
    # Matrículas (520 x 110 mm)
    caja_mat(bm, (0, -2.182, 0.37), (0.52, 0.012, 0.11), MATRICULA)
    caja_mat(bm, (0, 2.19, 0.38), (0.52, 0.012, 0.11), MATRICULA)
    # Molduras laterales, juntas de puertas, manetas y retrovisores
    for s in (-1, 1):
        caja_mat(bm, (s * 0.849, 0.05, 0.47), (0.018, 1.96, 0.035), NEGRO)
        caja_mat(bm, (s * 0.85, 0.05, 0.47), (0.016, 1.96, 0.006), CROMO)
        for y in (-0.96, 0.17, 1.02):
            caja_mat(bm, (s * 0.8425, y, 0.50), (0.004, 0.005, 0.60), NEGRO)
        for y in (0.04, 0.88):
            caja_mat(bm, (s * 0.848, y, 0.74), (0.014, 0.12, 0.025), CROMO)
        caja_mat(bm, (s * 0.90, -0.86, 0.87), (0.11, 0.05, 0.08), NEGRO)
        caja_mat(bm, (s * 0.83, -0.86, 0.84), (0.06, 0.04, 0.03), NEGRO)
    # Tubo de escape
    r = bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=0.025, radius2=0.025, depth=0.25)
    bmesh.ops.rotate(bm, verts=r["verts"], cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, "X"))
    bmesh.ops.translate(bm, verts=r["verts"], vec=(-0.45, 2.10, 0.22))
    c.asignar(bm, {f for v in r["verts"] for f in v.link_faces}, CROMO)
    # Bajos oscuros (se ven desde lejos entre las ruedas)
    caja_mat(bm, (0, 0, 0.165), (1.5, 3.9, 0.03), NEGRO)
    for y in (YF, YR):
        for s in (-1, 1):
            rueda(bm, s * VIA, y, s)
    return c.objeto("Detalles", bm, mats, suave=False, uv_metros=1.0)


def interior(mats):
    bm = bmesh.new()
    # Salpicadero, consola y suelo
    caja_mat(bm, (0, -0.78, 0.68), (1.42, 0.30, 0.22), NEGRO, biselado=0.03, segmentos=2)
    caja_mat(bm, (0, -0.55, 0.50), (0.22, 0.40, 0.30), NEGRO, biselado=0.01)
    caja_mat(bm, (0, 0.0, SUELO_INT + 0.005), (1.42, 1.7, 0.01), INTERIOR)
    inclin = Matrix.Rotation(math.radians(-14), 3, "X")
    for x in (COND, -COND):
        caja_mat(bm, (x, 0.05, ASIENTO - 0.065), (0.50, 0.50, 0.13), INTERIOR, biselado=0.03, segmentos=2)
        caja_mat(bm, (x, 0.07, (SUELO_INT + ASIENTO - 0.13) / 2), (0.40, 0.42, ASIENTO - 0.13 - SUELO_INT), NEGRO)
        caja_mat(bm, (x, 0.40, ASIENTO + 0.30), (0.50, 0.12, 0.62), INTERIOR, biselado=0.03, segmentos=2, rot=inclin)
        caja_mat(bm, (x, 0.47, ASIENTO + 0.71), (0.26, 0.09, 0.17), INTERIOR, biselado=0.03, segmentos=2, rot=inclin)
    # Asiento trasero
    caja_mat(bm, (0, 0.82, ASIENTO - 0.04), (1.08, 0.40, 0.14), INTERIOR, biselado=0.03, segmentos=2)
    caja_mat(bm, (0, 1.03, ASIENTO + 0.28), (1.08, 0.12, 0.55), INTERIOR, biselado=0.03, segmentos=2,
             rot=Matrix.Rotation(math.radians(-18), 3, "X"))
    # Volante y columna
    antes = set(bm.verts)
    circulo = [(0.185 + 0.016 * math.cos(a), 0.016 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 8, endpoint=False)]
    revolucion(bm, circulo, 24, cerrado=True)
    caja_mat(bm, (0, 0, 0), (0.36, 0.05, 0.03), NEGRO)
    caja_mat(bm, (0, 0, -0.01), (0.10, 0.10, 0.05), NEGRO, biselado=0.01)
    nuevos = [v for v in bm.verts if v not in antes]
    for f in {f for v in nuevos for f in v.link_faces}:
        f.material_index = NEGRO
    bmesh.ops.rotate(bm, verts=nuevos, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(-62), 3, "X"))
    bmesh.ops.translate(bm, verts=nuevos, vec=(COND, -0.45, 0.76))
    barra(bm, (COND, -0.47, 0.745), (COND, -0.65, 0.66), 0.05, 0.05, (0, 0, 1), NEGRO)
    # Espejo interior
    caja_mat(bm, (0, -0.12, 1.30), (0.22, 0.03, 0.06), NEGRO, biselado=0.008)
    return c.objeto("Interior", bm, mats, uv_metros=1.0)


# ---------- texturas ----------

def textura_pintura(nombre, color, semilla):
    """Pintura algo gastada: tono casi liso con manchas suaves de polvo."""
    rng = np.random.default_rng(semilla)
    t = 512
    n = c.fbm(t, t, rng, (128, 64, 32))
    fino = c.fbm(t, t, rng, (4, 2))
    v = 0.96 + (n - 0.5) * 0.10 + (fino - 0.5) * 0.03
    polvo = np.clip((c.fbm(t, t, rng, (64, 32)) - 0.55) * 2.5, 0, 1)[..., None] * 0.18
    col = np.array(color)[None, None, :] * v[..., None]
    gris = np.array((0.42, 0.40, 0.37))[None, None, :]
    return c.guardar_png(nombre, col * (1 - polvo) + gris * polvo)


def textura_faro(nombre):
    """Cristal de faro con prismas: celdas de unos 3,5 cm con brillo desigual (1 m de lado)."""
    rng = np.random.default_rng(23)
    t, celda = 512, 16
    yy, xx = np.mgrid[0:t, 0:t]
    n = t // celda
    brillo = rng.random((n, n))[yy // celda, xx // celda]
    fx, fy = (xx % celda) / celda, (yy % celda) / celda
    prisma = 1 - np.abs(fx - 0.5) * 0.5 - fy * 0.25
    borde = ((xx % celda) < 1) | ((yy % celda) < 1)
    v = 0.62 + 0.25 * brillo * prisma + (c.fbm(t, t, rng, (32, 8)) - 0.5) * 0.15
    v = np.where(borde, v * 0.7, v)
    return c.guardar_png(nombre, np.array((0.95, 0.92, 0.82))[None, None, :] * v[..., None])


def textura_tapiceria(nombre):
    rng = np.random.default_rng(31)
    t = 256
    yy, xx = np.mgrid[0:t, 0:t]
    trama = ((xx // 2 + yy // 2) % 2) * 0.04
    n = c.fbm(t, t, rng, (32, 16, 8))
    v = 0.92 + trama + (n - 0.5) * 0.12
    return c.guardar_png(nombre, np.array((0.20, 0.20, 0.22))[None, None, :] * v[..., None])


def textura_matricula(nombre):
    """Matrícula genérica: fondo blanco, franja azul y caracteres ilegibles."""
    w, h = 512, 108
    img = np.ones((h, w, 3)) * np.array((0.62, 0.60, 0.54))  # blanco sucio
    img[:, :44] = (0.10, 0.18, 0.45)
    rng = np.random.default_rng(41)
    img[6:-6, :] *= 1.0
    x = 70
    for i in range(7):
        if i == 4:
            x += 22
        anchura = 46
        bloque = np.zeros((h - 30, anchura))
        for _ in range(4):
            if rng.random() > 0.3:
                bloque[:, rng.integers(0, 3) * 15:rng.integers(0, 3) * 15 + 9] = 1
            yy = rng.integers(0, 3) * ((h - 39) // 2)
            bloque[yy:yy + 9, :] = 1
        img[15:h - 15, x:x + anchura][bloque > 0] = (0.08, 0.08, 0.08)
        x += anchura + 12
    img[:3, :] = img[-3:, :] = img[:, :3] = img[:, -3:] = (0.1, 0.1, 0.1)
    return c.guardar_png(nombre, img)


def materiales(pintura_img):
    tap = textura_tapiceria("Coche_Tapiceria")
    mat = textura_matricula("Coche_Matricula")
    cristal = c.material("Coche_Cristal", color=(0.03, 0.035, 0.04), rugosidad=0.05)
    cristal.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = 0.6
    return [
        c.material(pintura_img.name, pintura_img, rugosidad=0.35),
        cristal,
        c.material("Coche_PlasticoNegro", color=(0.035, 0.035, 0.035), rugosidad=0.7),
        c.material("Coche_Cromo", color=(0.6, 0.6, 0.6), rugosidad=0.25, metal=1.0),
        c.material("Coche_Faro", textura_faro("Coche_Faro"), rugosidad=0.1),
        c.material("Coche_Piloto", color=(0.35, 0.03, 0.02), rugosidad=0.15),
        c.material("Coche_Neumatico", color=(0.03, 0.03, 0.03), rugosidad=0.85),
        c.material("Coche_Tapacubos", color=(0.18, 0.18, 0.18), rugosidad=0.4),
        c.material("Coche_Tapiceria", tap, rugosidad=0.9),
        c.material("Coche_Matricula", mat, rugosidad=0.5),
        c.material("Coche_Intermitente", color=(0.55, 0.28, 0.03), rugosidad=0.15),
    ]


COLORES = {
    "CocheRojo": (0.24, 0.085, 0.065),
    "CocheAzul": (0.12, 0.18, 0.27),
    "CocheGris": (0.38, 0.39, 0.38),
}


def generar(nombre, color, semilla):
    c.escena_vacia()
    img = textura_pintura("Coche_Pintura" + nombre[5:], color, semilla)
    mats = materiales(img)
    partes = [carroceria(mats), habitaculo(mats), detalles(mats), interior(mats)]
    bpy.ops.object.select_all(action="DESELECT")
    for p in partes:
        p.select_set(True)
    bpy.context.view_layer.objects.active = partes[0]
    bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active
    ob.name = ob.data.name = "Coche"
    ruta = c.exportar_fbx(nombre, [ob])
    tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
    print(f"Exportado {ruta} ({tris} triángulos)")


def main():
    for i, (nombre, color) in enumerate(COLORES.items()):
        generar(nombre, color, 50 + i)


if __name__ == "__main__":
    main()
