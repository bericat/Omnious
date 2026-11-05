"""EXPERIMENTO (no se usa en el juego): utilitario de cuatro puertas de principios de los 2000, genérico (no imita ningún modelo real).

Estilo de las referencias de Toni (Fears to Fathom): formas redondeadas, coche usado,
polvo en los bajos, suciedad en juntas y rincones y la pintura algo gastada.

Sustituye a la malla provisional Coche de HouseBuilder (coche de Chevas en el garaje y
los dos de la calle). Origen en el suelo, en el centro del coche, morro hacia +Z en Unity.
Medidas: 4,32 x 1,70 x 1,47 m, batalla 2,50 m (cabe en el garaje de 4,4 m).

Tiene interior porque Roberta aparece sentada al volante (conductor a la izquierda,
x = -0,37 en Unity). Cojín del conductor a 0,45 m: para la figura sentada de HouseBuilder
(muslos a 0,48) el punto de colocación es local (-0,37, -0,03, -0,2).

Salen CocheRojo.fbx (Chevas), CocheAzul.fbx y CocheGris.fbx, cada uno con su textura
horneada (Texturas/<nombre>.jpg) y el material Coche_Cristal (alfa 0,55, transparente).

Uso:  python Tools/assets/coche.py [Rojo|Azul|Gris]
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
import hornear  # noqa: E402

# Salida a nombres propios para no pisar los coches del juego
PREFIJO = "Coche2000"

# Blender: X ancho (x de Unity = -X), Y largo con el morro hacia -Y, Z arriba.
YF, YR = -1.30, 1.20
R_RUEDA = 0.30
VIA = 0.72
COND = 0.37
ASIENTO = 0.45
SUELO_INT = 0.26

(PINTURA, CRISTAL, NEGRO, CROMO, FARO, PILOTO, NEUMATICO, LLANTA, INTERIOR, MATRICULA,
 INTERMITENTE, BAJOS) = range(12)

# Estaciones a lo largo del coche: (y, z abajo, z cintura, media anchura, z techo, media anchura del techo)
EST = [
    (-2.16, 0.33, 0.50, 0.55, 0.52, 0.40),
    (-2.12, 0.26, 0.64, 0.76, 0.66, 0.55),
    (-1.98, 0.23, 0.74, 0.83, 0.76, 0.62),
    (-1.55, 0.22, 0.83, 0.85, 0.86, 0.64),
    (-1.00, 0.21, 0.90, 0.85, 0.94, 0.66),   # base del parabrisas
    (-0.50, 0.21, 0.93, 0.85, 1.28, 0.665),
    (-0.12, 0.21, 0.95, 0.85, 1.455, 0.665),  # techo delante
    (0.24, 0.21, 0.965, 0.85, 1.47, 0.665),   # montante B
    (0.34, 0.21, 0.97, 0.85, 1.47, 0.665),
    (0.80, 0.22, 0.99, 0.85, 1.44, 0.645),   # techo detrás
    (1.25, 0.23, 1.01, 0.845, 1.20, 0.63),
    (1.58, 0.24, 1.02, 0.835, 1.06, 0.62),   # base de la luneta
    (1.95, 0.26, 1.02, 0.81, 1.045, 0.58),
    (2.10, 0.29, 0.98, 0.76, 1.00, 0.52),
    (2.16, 0.36, 0.72, 0.58, 0.74, 0.40),
]
# Pares de estaciones con cristal lateral, parabrisas y luneta (índices en EST)
VENT_LAT = {(5, 6), (6, 7), (8, 9)}
PILAR_B = {(7, 8)}
PARABRISAS = {(4, 5), (5, 6)}
LUNETA = {(9, 10), (10, 11)}


def anillo(z0, zb, hw, zr, hr):
    """Contorno (x, z) de la mitad derecha, de abajo arriba (11 puntos)."""
    return [
        (0.0, z0), (hw * 0.80, z0), (hw * 0.97, z0 + 0.07), (hw, z0 + (zb - z0) * 0.5),
        (hw * 0.985, zb - 0.06), (hw * 0.93, zb), (hr + (hw * 0.93 - hr) * 0.45, zb + (zr - zb) * 0.5),
        (hr, zr - 0.035), (hr * 0.75, zr - 0.005), (hr * 0.35, zr + 0.008), (0.0, zr + 0.012),
    ]


def carroceria(mats):
    bm = bmesh.new()
    anillos = []
    for y, *p in EST:
        der = anillo(*p)
        pts = der + [(-x, z) for x, z in reversed(der[1:-1])]
        anillos.append([bm.verts.new((x, y, z)) for x, z in pts])
    n = len(anillos[0])
    for i, (a, b) in enumerate(zip(anillos, anillos[1:])):
        for k in range(n):
            j = (k + 1) % n
            f = bm.faces.new((a[k], a[j], b[j], b[k]))
            seg = min(k, n - 1 - k)  # segmento por la simetría (0 abajo ... 9 arriba)
            par = (i, i + 1)
            if seg in (5, 6) and par in VENT_LAT:
                f.material_index = CRISTAL
            elif seg in (5, 6) and (par in PILAR_B or par == (4, 5)):
                f.material_index = NEGRO
            elif seg in (7, 8, 9) and par in PARABRISAS | LUNETA:
                f.material_index = CRISTAL
            elif seg == 0:
                f.material_index = BAJOS
            else:
                f.material_index = PINTURA
            # Faros: esquinas delanteras arriba; pilotos: esquinas traseras
            if par == (0, 1) and seg in (4, 5, 6):
                f.material_index = FARO
            if par == (0, 1) and seg in (8, 9):
                f.material_index = NEGRO  # rejilla entre los faros
            if par == (12, 13) and seg in (4, 5):
                f.material_index = PILOTO
            if par in ((0, 1), (1, 2)) and seg in (1, 2):
                f.material_index = NEGRO  # paragolpes inferior y rejilla baja
            if par in ((13, 14),) and seg in (1, 2):
                f.material_index = NEGRO
    bm.faces.new(list(reversed(anillos[0])))
    tapa = bm.faces.new(anillos[-1])
    tapa.material_index = PINTURA
    ob = c.objeto("Carroceria", bm, mats)
    sub = ob.modifiers.new("Sub", "SUBSURF")
    sub.levels = sub.render_levels = 2
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.modifier_apply(modifier=sub.name)

    # Pasos de rueda
    for y in (YF, YR):
        rb = bmesh.new()
        r = bmesh.ops.create_cone(rb, cap_ends=True, segments=36, radius1=0.355, radius2=0.355, depth=2.2)
        bmesh.ops.rotate(rb, verts=r["verts"], cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, "Y"))
        bmesh.ops.translate(rb, verts=r["verts"], vec=(0, y, R_RUEDA + 0.02))
        c.asignar(rb, rb.faces, BAJOS)
        corte = c.objeto("CorteRueda", rb, mats)
        # Solo por fuera: se resta la rueda menos una caja central
        cb = bmesh.new()
        c.caja(cb, (0, y, 0.5), (1.20, 1.0, 1.2))
        caja = c.objeto("CentroRueda", cb, mats)
        m = corte.modifiers.new("Centro", "BOOLEAN"); m.operation = "DIFFERENCE"; m.solver = "EXACT"; m.object = caja
        bpy.context.view_layer.objects.active = corte
        bpy.ops.object.modifier_apply(modifier=m.name)
        bpy.data.objects.remove(caja)
        m = ob.modifiers.new("Rueda", "BOOLEAN"); m.operation = "DIFFERENCE"; m.solver = "EXACT"
        m.material_mode = "TRANSFER"; m.object = corte
        bpy.context.view_layer.objects.active = ob
        bpy.ops.object.modifier_apply(modifier=m.name)
        bpy.data.objects.remove(corte)
    for p in ob.data.polygons:
        p.use_smooth = p.material_index in (PINTURA, CRISTAL, FARO, PILOTO)
    return ob


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
    anillos = []
    for r, z in perfil:
        anillos.append([bm.verts.new((r * math.cos(2 * math.pi * i / lados),
                                      r * math.sin(2 * math.pi * i / lados), z)) for i in range(lados)])
    pares = list(zip(anillos, anillos[1:]))
    if cerrado:
        pares.append((anillos[-1], anillos[0]))
    caras = []
    for a, b in pares:
        for i in range(lados):
            j = (i + 1) % lados
            caras.append(bm.faces.new((a[i], a[j], b[j], b[i])))
    return anillos, caras


def rueda(bm, x, y, s):
    """Neumático 185/65 R14 con tapacubos de plástico de radios."""
    antes = set(bm.verts)
    perfil = [(0.19, -0.08), (0.24, -0.0925), (0.285, -0.088), (R_RUEDA, -0.06), (R_RUEDA, 0.06),
              (0.285, 0.088), (0.24, 0.0925), (0.19, 0.08)]
    _, neum = revolucion(bm, perfil, 32)
    c.asignar(bm, neum, NEUMATICO)
    tapa = [(0.19, 0.08), (0.185, 0.086), (0.16, 0.088), (0.12, 0.084), (0.07, 0.088), (0.04, 0.095), (0.0, 0.097)]
    an, tap = revolucion(bm, tapa, 32)
    c.asignar(bm, tap, LLANTA)
    fondo = bm.faces.new(list(reversed([v for v in an[0]])))
    fondo.material_index = NEGRO
    # Huecos oscuros entre los radios
    for k in range(6):
        a = 2 * math.pi * k / 6
        vs = caja_mat(bm, (0, 0, 0), (0.06, 0.035, 0.008), NEGRO)
        bmesh.ops.translate(bm, verts=vs, vec=(0.12, 0, 0.089))
        bmesh.ops.rotate(bm, verts=vs, cent=(0, 0, 0), matrix=Matrix.Rotation(a, 3, "Z"))
    nuevos = [v for v in bm.verts if v not in antes]
    bmesh.ops.rotate(bm, verts=nuevos, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90 * s), 3, "Y"))
    bmesh.ops.translate(bm, verts=nuevos, vec=(x, y, R_RUEDA))


def detalles(mats):
    bm = bmesh.new()
    for y in (YF, YR):
        for s in (-1, 1):
            rueda(bm, s * VIA, y, s)
    # Rejilla delantera trapezoidal y matrículas
    caja_mat(bm, (0, -2.105, 0.585), (0.62, 0.06, 0.10), NEGRO, biselado=0.02, segmentos=2)
    caja_mat(bm, (0, -2.135, 0.585), (0.06, 0.012, 0.035), CROMO, biselado=0.005)
    caja_mat(bm, (0, -2.155, 0.40), (0.52, 0.012, 0.11), MATRICULA)
    caja_mat(bm, (0, 2.145, 0.62), (0.52, 0.012, 0.11), MATRICULA)
    # Retrovisores, manetas, juntas de puertas y antinieblas
    for s in (-1, 1):
        vs = caja_mat(bm, (s * 0.93, -0.88, 1.00), (0.15, 0.07, 0.10), PINTURA, biselado=0.025, segmentos=3)
        caja_mat(bm, (s * 0.86, -0.88, 0.97), (0.06, 0.05, 0.04), NEGRO)
        for y in (0.08, 0.98):
            caja_mat(bm, (s * 0.852, y, 0.86), (0.02, 0.13, 0.03), PINTURA, biselado=0.008, segmentos=2)
        for y in (-0.98, 0.27, 1.12):
            caja_mat(bm, (s * 0.851, y, 0.58), (0.003, 0.004, 0.68), NEGRO)
        caja_mat(bm, (s * 0.60, -2.10, 0.36), (0.12, 0.04, 0.06), FARO, biselado=0.015, segmentos=2)
        caja_mat(bm, (s * 0.835, -1.75, 0.70), (0.01, 0.05, 0.025), INTERMITENTE, biselado=0.004)
    # Tubo de escape
    r = bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=0.028, radius2=0.028, depth=0.20)
    bmesh.ops.rotate(bm, verts=r["verts"], cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, "X"))
    bmesh.ops.translate(bm, verts=r["verts"], vec=(-0.48, 2.10, 0.25))
    c.asignar(bm, {f for v in r["verts"] for f in v.link_faces}, CROMO)
    return c.objeto("Detalles", bm, mats)


def interior(mats):
    bm = bmesh.new()
    # Suelo, paneles de puerta (para no ver la carrocería por dentro) y salpicadero
    caja_mat(bm, (0, 0.2, SUELO_INT), (1.55, 2.9, 0.02), INTERIOR)
    for s in (-1, 1):
        caja_mat(bm, (s * 0.80, -0.07, (SUELO_INT + 0.92) / 2), (0.03, 1.76, 0.92 - SUELO_INT), INTERIOR)
    caja_mat(bm, (0, -0.86, 0.80), (1.56, 0.36, 0.26), NEGRO, biselado=0.06, segmentos=3)
    caja_mat(bm, (0, -0.62, 0.55), (0.24, 0.40, 0.34), NEGRO, biselado=0.02, segmentos=2)
    caja_mat(bm, (0, 1.55, 1.02), (1.5, 0.6, 0.02), INTERIOR)  # bandeja trasera
    inclin = Matrix.Rotation(math.radians(-14), 3, "X")
    for x in (COND, -COND):
        caja_mat(bm, (x, 0.0, ASIENTO - 0.07), (0.50, 0.50, 0.14), INTERIOR, biselado=0.04, segmentos=3)
        caja_mat(bm, (x, 0.02, (SUELO_INT + ASIENTO - 0.14) / 2), (0.40, 0.42, ASIENTO - 0.14 - SUELO_INT), NEGRO)
        caja_mat(bm, (x, 0.33, ASIENTO + 0.31), (0.50, 0.13, 0.62), INTERIOR, biselado=0.04, segmentos=3, rot=inclin)
        caja_mat(bm, (x, 0.42, ASIENTO + 0.73), (0.26, 0.10, 0.18), INTERIOR, biselado=0.04, segmentos=3, rot=inclin)
    caja_mat(bm, (0, 0.85, ASIENTO - 0.04), (1.30, 0.45, 0.15), INTERIOR, biselado=0.04, segmentos=3)
    caja_mat(bm, (0, 1.12, ASIENTO + 0.28), (1.30, 0.13, 0.58), INTERIOR, biselado=0.04, segmentos=3,
             rot=Matrix.Rotation(math.radians(-20), 3, "X"))
    # Volante
    antes = set(bm.verts)
    circulo = [(0.19 + 0.017 * math.cos(a), 0.017 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 8, endpoint=False)]
    revolucion(bm, circulo, 24, cerrado=True)
    caja_mat(bm, (0, 0, 0), (0.36, 0.05, 0.03), NEGRO)
    caja_mat(bm, (0, 0, -0.01), (0.12, 0.12, 0.06), NEGRO, biselado=0.015, segmentos=2)
    nuevos = [v for v in bm.verts if v not in antes]
    for f in {f for v in nuevos for f in v.link_faces}:
        f.material_index = NEGRO
    bmesh.ops.rotate(bm, verts=nuevos, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(-62), 3, "X"))
    bmesh.ops.translate(bm, verts=nuevos, vec=(COND, -0.50, 0.85))
    caja_mat(bm, (0, -0.30, 1.38), (0.22, 0.03, 0.06), NEGRO, biselado=0.01)
    return c.objeto("Interior", bm, mats)


def textura_matricula(nombre):
    """Matrícula genérica y sucia: fondo blanco roto, franja azul y caracteres ilegibles."""
    w, h = 512, 108
    img = np.ones((h, w, 3)) * np.array((0.75, 0.73, 0.66))
    img[:, :44] = (0.10, 0.18, 0.45)
    rng = np.random.default_rng(41)
    x = 70
    for i in range(7):
        if i == 4:
            x += 22
        bloque = np.zeros((h - 30, 46))
        for _ in range(4):
            if rng.random() > 0.3:
                k = rng.integers(0, 3) * 15
                bloque[:, k:k + 9] = 1
            yy = rng.integers(0, 3) * ((h - 39) // 2)
            bloque[yy:yy + 9, :] = 1
        img[15:h - 15, x:x + 46][bloque > 0] = (0.08, 0.08, 0.08)
        x += 58
    return c.guardar_png(nombre, img)


COLORES = {
    "Rojo": (0.42, 0.07, 0.05),
    "Azul": (0.10, 0.16, 0.26),
    "Gris": (0.36, 0.37, 0.37),
}


def materiales(nombre, color, semilla):
    hs = hornear.material_sucio
    plate = textura_matricula("_Matricula")
    plate.pack()
    os.remove(plate.filepath_raw)  # solo hace falta en memoria: acaba dentro del atlas
    return [
        hs("Pintura", color, rugosidad=0.35, suciedad=0.7, polvo=1.0, manchas=0.3, desgaste=0.12,
           color_desgaste=(0.30, 0.29, 0.27), color_sucio=(0.17, 0.12, 0.07), semilla=semilla, mugre=0.7),
        hornear.material_liso("Coche_Cristal", (0.05, 0.06, 0.06), rugosidad=0.05, alfa=0.55),
        hs("Negro", (0.04, 0.04, 0.04), rugosidad=0.7, suciedad=0.4, polvo=0.8, manchas=0.2, color_sucio=(0.14, 0.12, 0.09)),
        hs("Cromo", (0.55, 0.55, 0.55), rugosidad=0.25, metal=1.0, suciedad=0.6, polvo=0.4),
        hs("Faro", (0.12, 0.12, 0.115), rugosidad=0.1, suciedad=0.9, manchas=0.5, color_sucio=(0.30, 0.26, 0.18)),
        hs("Piloto", (0.40, 0.04, 0.03), rugosidad=0.15, suciedad=0.6, manchas=0.3),
        hs("Neumatico", (0.035, 0.035, 0.035), rugosidad=0.9, suciedad=0.3, polvo=1.0, manchas=0.2, color_sucio=(0.17, 0.15, 0.12)),
        hs("Llanta", (0.30, 0.30, 0.31), rugosidad=0.5, suciedad=0.9, polvo=1.0, manchas=0.4, color_sucio=(0.15, 0.12, 0.08)),
        hs("Interior", (0.13, 0.13, 0.14), rugosidad=0.9, suciedad=0.5, polvo=0.2),
        hs("Matricula", (0.8, 0.8, 0.8), rugosidad=0.5, imagen=plate, suciedad=0.6, manchas=0.2, polvo=0.4, mugre=0.25),
        hs("Intermitente", (0.60, 0.30, 0.04), rugosidad=0.15, suciedad=0.6),
        hs("Bajos", (0.03, 0.028, 0.025), rugosidad=0.9, suciedad=0.2, polvo=0.6, manchas=0.0),
    ]


def generar(color_nombre, color, semilla):
    nombre = PREFIJO + color_nombre
    c.escena_vacia()
    mats = materiales(nombre, color, semilla)
    partes = [carroceria(mats), detalles(mats), interior(mats)]
    bpy.ops.object.select_all(action="DESELECT")
    for p in partes:
        p.select_set(True)
    bpy.context.view_layer.objects.active = partes[0]
    bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active
    ob.name = ob.data.name = "Coche"
    hornear.atlas(ob, nombre, tam=2048, sin_hornear={"Coche_Cristal"}, poco_detalle={"Interior", "Bajos"})
    ruta = c.exportar_fbx(nombre, [ob])
    tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
    print(f"Exportado {ruta} ({tris} triángulos)")


def main():
    pedidos = sys.argv[1:] or list(COLORES)
    for i, n in enumerate(COLORES):
        if n in pedidos:
            generar(n, COLORES[n], float(i * 7))


if __name__ == "__main__":
    main()
