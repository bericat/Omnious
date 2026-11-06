"""Recibidor y salón según la referencia mejorada de Toni (Docs/Referencias/recibidor_salon_mejorado.png),
en estilo PSX. Frente a +Z en Unity (aquí, en Blender, a -Y), origen en el suelo salvo que se diga.

  Alfombra         persa roja y azul del salón, 2,4 x 1,7 m (sustituye a la de textiles_salon.py).
  AlfombraPasillo  persa estrecha del recibidor, 0,75 x 2,4 m (larga en Z de Unity).
  PlantaGrande     ficus de hoja ancha en maceta de cerámica crema, 1,3 m.
  PercheroPared    tabla con cinco ganchos, una chaqueta azul y una bufanda. Origen en el suelo, contra la
                   pared (Z local = 0 en la pared); los ganchos quedan a 1,70 m.
  CuadroPaisaje1   bosque, 0,85 x 0,60.   CuadroPaisaje2   campo al atardecer, vertical, 0,55 x 0,70.
  CuadroPaisaje3   prado, 0,75 x 0,50.    Marco grueso de madera; origen en el centro de la trasera (PARED).
                   Dos objetos: el marco (horneado) y "<Nombre>_Lienzo" con su pintura (Texturas/<Nombre>_Lienzo.jpg).
  EstanteriaLibros la huella de Estanteria (1,0 x 1,9 x 0,3), madera oscura, llena de libros y algunos tumbados.
  Taza             taza oscura de café, 0,08 m de diámetro.   Mando   mando de la tele, 0,05 x 0,18 m.

Uso:  python Tools/assets/recibidor_salon.py [Nombre ...]      (sin nombres, todos)
Necesita Pillow (para los cuadros). Texturas CC0: Mueble_Wood092, Suciedad_SurfaceImperfections015.
"""
import math
import os
import random
import sys

import bpy  # noqa: F401  (carga bmesh)
import bmesh
import numpy as np
from mathutils import Matrix, Vector
from PIL import Image, ImageFilter

sys.path.insert(0, os.path.dirname(__file__))
import comun as c  # noqa: E402
import hornear  # noqa: E402
import laminas  # noqa: E402

R = lambda grados, eje="Z": Matrix.Rotation(math.radians(grados), 3, eje)  # noqa: E731


def _poner(bm, nv, mat, rot=None, centro=(0, 0, 0)):
    if rot is not None:
        bmesh.ops.transform(bm, matrix=rot.to_4x4(), verts=nv)
    bmesh.ops.translate(bm, verts=nv, vec=centro)
    c.asignar(bm, {f for v in nv for f in v.link_faces}, mat)
    return nv


def cil(bm, centro, r, alto, mat, lados=8, r2=None, rot=None):
    c.marcar(bm)
    bmesh.ops.create_cone(bm, cap_ends=True, segments=lados, radius1=r, radius2=r if r2 is None else r2, depth=alto)
    return _poner(bm, c.nuevos(bm), mat, rot, centro)


def barra(bm, a, b, r, mat, lados=5):
    a, b = Vector(a), Vector(b)
    c.marcar(bm)
    bmesh.ops.create_cone(bm, cap_ends=True, segments=lados, radius1=r, radius2=r, depth=(b - a).length)
    nv = c.nuevos(bm)
    bmesh.ops.transform(bm, matrix=(b - a).to_track_quat("Z", "Y").to_matrix().to_4x4(), verts=nv)
    return _poner(bm, nv, mat, None, (a + b) / 2)


def torno(bm, perfil, mat, lados=10, desde=(0, 0, 0)):
    c.marcar(bm)
    c.torno(bm, perfil, lados=lados, desde=desde)
    nv = c.nuevos(bm)
    c.asignar(bm, {f for v in nv for f in v.link_faces}, mat)
    return nv


def exportar(nombre, objs):
    ruta = c.exportar_fbx(nombre, objs)
    print(f"Exportado {ruta} ({sum(len(p.vertices) - 2 for o in objs for p in o.data.polygons)} triángulos)")


def limpiar_materiales(ob):
    """Quita los materiales que no usa ninguna cara (el atlas sale más limpio)."""
    usados = sorted({p.material_index for p in ob.data.polygons})
    viejos, idx = list(ob.data.materials), {o: n for n, o in enumerate(usados)}
    nuevos = [idx[p.material_index] for p in ob.data.polygons]
    ob.data.materials.clear()  # (pone los índices a 0: se reasignan después)
    for i in usados:
        ob.data.materials.append(viejos[i])
    for p, i in zip(ob.data.polygons, nuevos):
        p.material_index = i


# ---------------------------------------------------------------- alfombras persas

ROJO = np.array((0.47, 0.10, 0.07))
ROJO_OSC = np.array((0.30, 0.06, 0.05))
AZUL = np.array((0.10, 0.13, 0.27))
CREMA = np.array((0.74, 0.64, 0.46))
ORO = np.array((0.58, 0.40, 0.15))
NEGRO = np.array((0.09, 0.06, 0.05))


def dibujo_persa(W, D, medallones, semilla, ppm=400):
    """Persa de dibujo geométrico: cenefa azul con rombos escalonados, campo rojo con medallones escalonados
    y motivos pequeños sueltos. W a lo ancho de la imagen, D a lo alto (en metros)."""
    rng = np.random.default_rng(semilla)
    w, h = int(W * ppm), int(D * ppm)
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    x, y = (xx + 0.5) / ppm, (yy + 0.5) / ppm               # metros desde la esquina
    borde = np.minimum(np.minimum(x, W - x), np.minimum(y, D - y))
    img = np.zeros((h, w, 3)) + ROJO
    # Cenefas: guarda crema, cenefa azul con rombos, guarda roja y crema
    ancho = min(0.16, W * 0.18)
    img[borde < 0.025] = NEGRO
    img[(borde >= 0.025) & (borde < 0.045)] = CREMA
    cen = (borde >= 0.045) & (borde < 0.045 + ancho)
    img[cen] = AZUL
    t = np.where(np.minimum(x, W - x) < np.minimum(y, D - y), y, x)   # a lo largo de la cenefa
    paso = ancho * 0.9
    s = 0.02                                                     # escalón de 2 cm
    du = np.floor(np.abs((t % paso) - paso / 2) / s) * s
    dv = np.floor(np.abs(borde - (0.045 + ancho / 2)) / s) * s
    rombo = (du + dv) < ancho * 0.42
    img[cen & rombo] = ROJO
    img[cen & ((du + dv) < ancho * 0.22)] = CREMA
    img[cen & ((du + dv) < ancho * 0.08)] = AZUL
    g = 0.045 + ancho
    img[(borde >= g) & (borde < g + 0.015)] = CREMA
    img[(borde >= g + 0.015) & (borde < g + 0.03)] = ROJO_OSC
    campo = borde >= g + 0.03
    # Medallones escalonados a lo largo del eje largo
    largo_x = W >= D
    cx, cy = W / 2, D / 2
    ocupado = np.zeros((h, w), bool)
    for k in range(medallones):
        f = (k + 1) / (medallones + 1)
        mx, my = (W * f, cy) if largo_x else (cx, D * f)
        a = (min(W, D) - 2 * g) * (0.42 if medallones == 1 else 0.36)
        b = a * (1.35 if medallones == 1 else 1.0)
        u, v = np.abs(x - mx), np.abs(y - my)
        if largo_x:
            u, v = u, v
        d = np.floor(u / s) * s / b + np.floor(v / s) * s / a
        m = campo & (d < 1.0)
        img[m] = AZUL
        img[campo & (d < 0.84)] = ROJO_OSC
        img[campo & (d < 0.70)] = CREMA
        img[campo & (d < 0.58)] = ROJO
        img[campo & (d < 0.36)] = AZUL
        img[campo & (d < 0.18)] = ORO
        cruz = campo & (d < 0.52) & ((np.abs(x - mx) < 0.012) | (np.abs(y - my) < 0.012))
        img[cruz] = AZUL
        ocupado |= d < 1.05
    # Esquinas del campo: cuartos de medallón azules
    for ex in (g + 0.03, W - g - 0.03):
        for ey in (g + 0.03, D - g - 0.03):
            d = np.floor(np.abs(x - ex) / s) * s / 0.30 + np.floor(np.abs(y - ey) / s) * s / 0.30
            img[campo & (d < 1.0)] = AZUL
            img[campo & (d < 0.75)] = ROJO_OSC
            img[campo & (d < 0.45)] = CREMA * 0.9
            ocupado |= d < 1.1
    # Motivos pequeños: estrellas de ocho puntas y cruces escalonadas en una rejilla con algo de desorden
    p = 0.17
    for gx in np.arange(g + 0.03 + p / 2, W - g - 0.03, p):
        for gy in np.arange(g + 0.03 + p / 2, D - g - 0.03, p):
            mx, my = gx + rng.normal(0, 0.012), gy + rng.normal(0, 0.012)
            i0, j0 = int(my * ppm), int(mx * ppm)
            if not (0 <= i0 < h and 0 <= j0 < w) or ocupado[i0, j0]:
                continue
            col = [CREMA, AZUL, ORO, AZUL, NEGRO][rng.integers(0, 5)]
            r = rng.uniform(0.035, 0.05)
            u, v = np.abs(x - mx), np.abs(y - my)
            if rng.random() < 0.5:
                m = (np.floor(u / s) + np.floor(v / s)) * s < r
                m &= ~((np.floor(u / s) + np.floor(v / s)) * s < r * 0.4)
            else:
                m = ((u < r) & (v < r * 0.35)) | ((v < r) & (u < r * 0.35)) | ((u + v) < r * 0.9)
            img[campo & m] = col
    # Lana: trama, nudos irregulares, color corrido y desgaste en la zona de paso
    trama = ((xx // 2 + yy // 2) % 2) * 0.05 + rng.random((h, w)) * 0.10
    img = img * (0.92 + trama[..., None])
    nub = c.fbm(h, w, rng, (max(4, h // 3), max(4, h // 8), max(2, h // 30)))
    img *= (0.85 + 0.3 * nub)[..., None]
    u2 = ((x / W) * 2 - 1) ** 2
    v2 = ((y / D) * 2 - 1) ** 2
    gastado = np.clip(1 - (u2 * (0.6 if largo_x else 1.6) + v2 * (1.6 if largo_x else 0.6)), 0, 1) * 0.28
    gastado *= (0.6 + 0.8 * nub)
    img = img * (1 - gastado[..., None]) + gastado[..., None] * np.array((0.42, 0.34, 0.27))
    return img


def alfombra(nombre, W, D, medallones, semilla):
    """Rejilla con ondulaciones suaves, canto y flecos en los lados cortos. W en X y D en Y de Blender."""
    c.escena_vacia()
    img = c.guardar_png("_" + nombre, dibujo_persa(W, D, medallones, semilla))
    img.pack(); os.remove(img.filepath_raw)
    hs = hornear.material_sucio
    mats = [
        hs("Lana", (0.80, 0.80, 0.80), rugosidad=0.95, imagen=img, escala=(-W, D, 1), desplazar=(0.5, 0.5, 0),
           suciedad=0.6, polvo=0.0, manchas=0.5, escala_manchas=5, color_sucio=(0.12, 0.08, 0.05), mugre=0.7),
        hs("Fleco", (0.40, 0.35, 0.26), rugosidad=0.9, suciedad=0.6, manchas=0.5, color_sucio=(0.25, 0.20, 0.14)),
    ]
    bm = bmesh.new()
    nx, ny = max(4, int(W * 8)), max(4, int(D * 8))
    r = bmesh.ops.create_grid(bm, x_segments=nx, y_segments=ny, size=0.5)
    for vv in r["verts"]:
        x, y = vv.co.x * W, vv.co.y * D
        b = min(W / 2 - abs(x), D / 2 - abs(y))
        z = 0.008 + 0.004 * math.sin(x * 3.1 + 1) * math.sin(y * 2.3) + (0.005 if b < 0.05 else 0)
        vv.co = Vector((x, y, z))
    bordes = [e for e in bm.edges if e.is_boundary]
    ext = bmesh.ops.extrude_edge_only(bm, edges=bordes)
    for vv in [g for g in ext["geom"] if isinstance(g, bmesh.types.BMVert)]:
        vv.co.z = 0.0
    c.asignar(bm, bm.faces, 0)
    rng = np.random.default_rng(semilla)
    corto_x = W < D                    # los flecos van en los lados cortos
    lado = W if corto_x else D
    n = int(lado / 0.05)
    for s in (-1, 1):
        for i in range(n):
            t = -lado / 2 + 0.04 + i * (lado - 0.08) / (n - 1)
            if corto_x:
                c.caja_mat(bm, (t, s * (D / 2 + 0.03), 0.003), (0.012, 0.06, 0.004), 1, 0,
                           rot=Matrix.Rotation(rng.normal() * 0.25, 3, "Z"))
            else:
                c.caja_mat(bm, (s * (W / 2 + 0.03), t, 0.003), (0.06, 0.012, 0.004), 1, 0,
                           rot=Matrix.Rotation(rng.normal() * 0.25, 3, "Z"))
    ob = c.objeto(nombre, bm, mats)
    for p in ob.data.polygons:
        p.use_smooth = True
    hornear.atlas(ob, nombre, tam=2048, margen=0.002)
    return [ob]


def alfombra_salon():
    return alfombra("Alfombra", 2.4, 1.7, 1, 5)


def alfombra_pasillo():
    return alfombra("AlfombraPasillo", 0.75, 2.4, 3, 9)


# ---------------------------------------------------------------- planta

def planta_grande():
    """Ficus de hoja ancha (gomero) en maceta de cerámica crema: tres tallos y hojas grandes, caídas hacia fuera.
    Cada hoja tiene cara por delante y por detrás (en Unity las caras son de una sola cara)."""
    c.escena_vacia()
    hs = hornear.material_sucio
    mats = [
        hs("Maceta", (0.58, 0.54, 0.44), rugosidad=0.3, suciedad=0.9, manchas=0.4, polvo=0.4, chorretones=0.5),
        hs("Tierra", (0.08, 0.06, 0.04), rugosidad=1.0, suciedad=0.3),
        hs("Tallo", (0.18, 0.14, 0.09), rugosidad=0.8, suciedad=0.5),
        hs("Hoja", (0.035, 0.075, 0.03), rugosidad=0.4, suciedad=0.4, manchas=0.3, polvo=0.3, saturacion=0.8),
        hs("HojaClara", (0.055, 0.10, 0.035), rugosidad=0.4, suciedad=0.4, manchas=0.3, polvo=0.3, saturacion=0.8),
    ]
    MAC, TIE, TAL, HOJ, HOJ2 = range(5)
    bm = bmesh.new()
    torno(bm, [(0.13, 0), (0.14, 0.02), (0.18, 0.28), (0.195, 0.29), (0.195, 0.32), (0.17, 0.32), (0.165, 0.29),
               (0.002, 0.29)], MAC, 10)
    cil(bm, (0, 0, 0.292), 0.165, 0.004, TIE, 10)
    rnd = random.Random(11)
    tallos = [((0.03, 0.02), 1.28, 0.3, 0.10), ((-0.05, 0.03), 1.10, 2.0, 0.20), ((0.01, -0.05), 0.95, 3.5, 0.22),
              ((0.04, -0.03), 0.80, 5.0, 0.24), ((-0.03, -0.02), 1.18, 1.2, 0.16)]
    for (bx, by), alto, ang, abre in tallos:
        a = Vector((bx, by, 0.29))
        med = Vector((bx + abre * 0.5 * math.cos(ang), by + abre * 0.5 * math.sin(ang), 0.29 + (alto - 0.29) * 0.5))
        top = Vector((bx + abre * math.cos(ang), by + abre * math.sin(ang), alto))
        barra(bm, a, med, 0.012, TAL, 5)
        barra(bm, med, top, 0.009, TAL, 5)
        n = int((alto - 0.40) / 0.045) + 4
        for k in range(n):
            t = 0.30 + 0.70 * k / max(1, n - 1)
            p = (a.lerp(med, t * 2) if t < 0.5 else med.lerp(top, (t - 0.5) * 2))
            giro = ang + k * 2.4 + rnd.uniform(-0.4, 0.4)
            d = Vector((math.cos(giro), math.sin(giro), 0))
            arriba = -0.35 + 0.85 * t + rnd.uniform(-0.2, 0.2)          # las de arriba suben, las de abajo caen
            larg = rnd.uniform(0.20, 0.31) * (0.8 if t > 0.92 else 1.0)
            anch = larg * rnd.uniform(0.45, 0.55)
            eje = (d + Vector((0, 0, arriba))).normalized()
            lado = d.cross(Vector((0, 0, 1))).normalized()
            base = p + d * 0.02
            punta = base + eje * larg + Vector((0, 0, -0.06 * (1 - t)))
            mid = base + eje * larg * 0.45
            nrm = lado.cross(eje).normalized()
            if nrm.z < 0:
                nrm = -nrm
            pliegue = -nrm * anch * 0.18          # hoja algo doblada por el nervio
            pts = [base, mid + lado * anch / 2 + pliegue, punta, mid - lado * anch / 2 + pliegue]
            mat = HOJ if rnd.random() < 0.6 else HOJ2
            c.marcar(bm)
            # Hoja cerrada y muy fina (cara y envés): así las normales salen bien y se ve por los dos lados
            vs = [bm.verts.new(q) for q in pts]
            off = [bm.verts.new(q - nrm * 0.003) for q in pts]
            caras = {bm.faces.new(vs), bm.faces.new(list(reversed(off)))}
            for i in range(4):
                j = (i + 1) % 4
                caras.add(bm.faces.new((vs[j], vs[i], off[i], off[j])))
            c.asignar(bm, caras, mat)
            # Pecíolo
            barra(bm, p, base + eje * 0.01, 0.004, TAL, 3)
    ob = c.objeto("PlantaGrande", bm, mats)
    for p in ob.data.polygons:
        p.use_smooth = p.material_index == MAC and len(p.vertices) == 4
    limpiar_materiales(ob)
    hornear.atlas(ob, "PlantaGrande", tam=1024, margen=0.004)
    return [ob]


# ---------------------------------------------------------------- perchero de pared

def tela(bm, ancho, alto, mat, filas=4, cols=3, ondas=0.012, desde=(0, 0, 0), rot=None):
    """Tira de tela colgando hacia abajo (plano XZ), con arrugas y algo de grosor."""
    c.marcar(bm)
    vs = []
    for j in range(filas + 1):
        fila = []
        for i in range(cols + 1):
            x = -ancho / 2 + ancho * i / cols
            z = -alto * j / filas
            y = ondas * math.sin(i * 2.1 + j * 1.3)
            fila.append(bm.verts.new((x, y, z)))
        vs.append(fila)
    caras = [bm.faces.new((vs[j][i], vs[j][i + 1], vs[j + 1][i + 1], vs[j + 1][i]))
             for j in range(filas) for i in range(cols)]
    for f in caras:
        f.normal_update()
    bmesh.ops.solidify(bm, geom=caras, thickness=0.01)
    return _poner(bm, c.nuevos(bm), mat, rot, desde)


def anillos(bm, secciones, mat, lados=8, semilla=0):
    """Tubo cerrado por secciones (z, medio ancho, medio fondo, y del centro); arriba acaba en punta."""
    rnd = random.Random(semilla)
    c.marcar(bm)
    rings = []
    for z, hw, hd, yc in secciones:
        rings.append([bm.verts.new((hw * math.cos(2 * math.pi * k / lados) * (1 + rnd.uniform(-0.05, 0.05)),
                                    yc + hd * math.sin(2 * math.pi * k / lados), z + rnd.uniform(-0.01, 0.01)))
                      for k in range(lados)])
    for a, b in zip(rings, rings[1:]):
        for k in range(lados):
            bm.faces.new((a[k], a[(k + 1) % lados], b[(k + 1) % lados], b[k]))
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    nv = c.nuevos(bm)
    bmesh.ops.recalc_face_normals(bm, faces=list({f for v in nv for f in v.link_faces}))
    c.asignar(bm, {f for v in nv for f in v.link_faces}, mat)
    return nv


def perchero_pared():
    c.escena_vacia()
    hs = hornear.material_sucio
    mats = [
        hornear.madera_vieja("Tabla", "oscura", desgaste=0.5),
        hs("Gancho", (0.16, 0.13, 0.08), rugosidad=0.4, metal=1.0, suciedad=0.8, manchas=0.4),
        hs("Chaqueta", (0.06, 0.09, 0.17), rugosidad=0.9, suciedad=0.7, manchas=0.5, escala_manchas=6, mugre=0.5,
           desgaste=0.2, color_desgaste=(0.12, 0.15, 0.22)),
        hs("Bufanda", (0.30, 0.09, 0.06), rugosidad=0.95, imagen=c.cc0("Tapiceria_Fabric083"), escala=0.15, veta=0.6,
           suciedad=0.6, manchas=0.5),
    ]
    TAB, GAN, CHA, BUF = range(4)
    bm = bmesh.new()
    zg = 1.70
    c.caja_mat(bm, (0, -0.011, zg + 0.02), (0.66, 0.022, 0.11), TAB, 0.006)
    xs = [-0.26, -0.13, 0.0, 0.13, 0.26]
    for x in xs:
        cil(bm, (x, -0.024, zg + 0.035), 0.012, 0.006, GAN, 6, rot=R(90, "X"))
        barra(bm, (x, -0.024, zg), (x, -0.075, zg - 0.01), 0.005, GAN)       # gancho de abajo
        barra(bm, (x, -0.075, zg - 0.01), (x, -0.085, zg + 0.025), 0.005, GAN)
        barra(bm, (x, -0.024, zg + 0.045), (x, -0.05, zg + 0.07), 0.004, GAN)  # gancho de arriba
    # Chaqueta azul colgada por la presilla del cuello
    xc = xs[1]
    anillos(bm, [(zg - 0.005, 0.02, 0.01, -0.075), (zg - 0.07, 0.10, 0.04, -0.075), (zg - 0.15, 0.22, 0.075, -0.085),
                 (zg - 0.40, 0.235, 0.085, -0.09), (zg - 0.65, 0.245, 0.08, -0.09), (zg - 0.78, 0.25, 0.075, -0.085)],
            CHA, 8, 3)
    for v in c.nuevos(bm):
        v.co.x += xc
    for s in (-1, 1):
        barra(bm, (xc + s * 0.20, -0.09, zg - 0.17), (xc + s * 0.235, -0.10, zg - 0.70), 0.05, CHA, 6)
    # Bufanda doblada sobre el gancho del otro lado: dos caídas de distinto largo
    xb = xs[3]
    tela(bm, 0.15, 0.48, BUF, desde=(xb - 0.035, -0.085, zg + 0.02), rot=R(4, "Y"))
    tela(bm, 0.15, 0.60, BUF, desde=(xb + 0.04, -0.06, zg + 0.02), rot=R(-3, "Y"))
    ob = c.objeto("PercheroPared", bm, mats)
    for p in ob.data.polygons:
        p.use_smooth = p.material_index in (CHA, BUF) and len(p.vertices) == 4
    hornear.atlas(ob, "PercheroPared", tam=1024, margen=0.004)
    return [ob]


# ---------------------------------------------------------------- cuadros

def _pinceladas(img, rng, fuerza=0.08, largo=9):
    """Textura de óleo: pinceladas cortas en direcciones al azar y grano de lienzo."""
    h, w, _ = img.shape
    out = img.copy()
    for _ in range(int(w * h / 18)):
        y, x = rng.integers(0, h), rng.integers(0, w)
        a = rng.uniform(-0.6, 0.6)
        n = rng.integers(3, largo)
        col = img[y, x] * (1 + rng.normal(0, fuerza))
        for k in range(n):
            yy, xx = int(y + k * math.sin(a)), int(x + k * math.cos(a))
            if 0 <= yy < h and 0 <= xx < w:
                out[yy, xx] = out[yy, xx] * 0.4 + col * 0.6
    tela = ((np.arange(w)[None, :] + np.arange(h)[:, None]) % 2) * 0.03
    return out * (0.98 + tela[..., None])


def _barniz(img, rng):
    h, w, _ = img.shape
    yy, xx = np.mgrid[0:h, 0:w]
    u, v = xx / w * 2 - 1, yy / h * 2 - 1
    vi = 1 - 0.35 * np.clip(u ** 2 + v ** 2 - 0.3, 0, 1)
    img = img * vi[..., None] * np.array((1.02, 0.96, 0.78))       # barniz amarillento y bordes oscuros
    img *= (0.9 + 0.2 * c.fbm(h, w, rng, (h // 2, h // 6, 6)))[..., None]
    return np.clip(img, 0, 1)


def _arbol(img, rng, x0, base, alto, ancho, col, conifera=False):
    h, w, _ = img.shape
    yy, xx = np.mgrid[0:h, 0:w]
    if conifera:
        t = (base - yy) / alto
        m = (t > 0) & (t < 1) & (np.abs(xx - x0) < ancho / 2 * (1 - t) * (1 + 0.25 * np.sin(yy * 0.9)))
        img[m] = col * (0.85 + 0.3 * rng.random(m.sum()))[:, None]
        return
    img[(np.abs(xx - x0) < max(1, ancho * 0.05)) & (yy < base) & (yy > base - alto * 0.45)] = np.array((0.12, 0.09, 0.06))
    for _ in range(26):
        cx = x0 + rng.normal(0, ancho * 0.24)
        cy = base - alto * rng.uniform(0.42, 0.95)
        r = ancho * rng.uniform(0.10, 0.22)
        m = (xx - cx) ** 2 + ((yy - cy) * 1.15) ** 2 < r * r
        tono = col * rng.uniform(0.75, 1.25)
        img[m] = tono * (0.85 + 0.3 * rng.random(m.sum()))[:, None]


def _hierba(img, rng, desde, fuerza=0.35):
    h, w, _ = img.shape
    yy = np.arange(h)[:, None] * np.ones((1, w))
    n = c.fbm(h, w, rng, (40, 12, 4))
    racha = np.sin(np.arange(w)[None, :] * 0.35 + n * 9) * 0.5 + 0.5
    m = yy >= desde
    f = (1 - fuerza / 2 + fuerza * (0.85 * n + 0.15 * racha))
    img[m] *= f[m][:, None]


def pintura_bosque(w=512, h=362):
    rng = np.random.default_rng(21)
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    hz = h * 0.56
    cielo = np.array((0.46, 0.50, 0.52)) + (yy / hz)[..., None] * np.array((0.20, 0.16, 0.10))
    nubes = c.fbm(h, w, rng, (90, 40, 16))
    img = cielo * (0.85 + 0.35 * nubes)[..., None]
    # Prado
    pr = yy >= hz
    t = (yy - hz) / (h - hz)
    img[pr] = (np.array((0.42, 0.40, 0.22)) * (1 - t[pr])[:, None] + np.array((0.24, 0.24, 0.12)) * t[pr][:, None])
    # Fila de árboles en el horizonte (del fondo, azulados, a los de delante, oscuros)
    for capa, (col, n, alto, ancho) in enumerate(((np.array((0.22, 0.27, 0.24)), 16, 60, 50),
                                                  (np.array((0.10, 0.16, 0.09)), 12, 100, 70))):
        for i in range(n):
            x0 = rng.uniform(0, w)
            con = capa == 1 and rng.random() < 0.3
            _arbol(img, rng, x0, hz + 4 + capa * 6, alto * rng.uniform(0.7, 1.3), ancho * rng.uniform(0.7, 1.2),
                   col, conifera=con)
    _arbol(img, rng, w * 0.8, hz + 14, 170, 60, np.array((0.08, 0.12, 0.07)), conifera=True)
    _arbol(img, rng, w * 0.87, hz + 10, 140, 50, np.array((0.09, 0.13, 0.08)), conifera=True)
    # Senda que serpentea hacia el bosque
    cxs = w * 0.40 + (yy - hz) * 0.6 + 18 * np.sin((yy - hz) / 22)
    sen = (yy > hz + 6) & (np.abs(xx - cxs) < (yy - hz) * 0.07 + 1)
    img[sen] = img[sen] * 0.4 + np.array((0.40, 0.35, 0.24)) * 0.6
    _hierba(img, rng, hz + 2)
    return _barniz(_pinceladas(img, rng), rng) * 0.92


def pintura_atardecer(w=400, h=510):
    rng = np.random.default_rng(23)
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    hz = h * 0.64
    t = np.clip(yy / hz, 0, 1)
    arriba, medio, bajo = np.array((0.20, 0.20, 0.30)), np.array((0.55, 0.32, 0.30)), np.array((0.90, 0.58, 0.26))
    img = np.where((t < 0.55)[..., None], arriba + (medio - arriba) * (t / 0.55)[..., None],
                   medio + (bajo - medio) * ((t - 0.55) / 0.45)[..., None])
    # Nubes alargadas teñidas
    nub = c.fbm(h, w, rng, (120, 50, 20))
    franjas = np.clip(np.sin(yy / 18 + nub * 4) * 0.5 + 0.5, 0, 1) * (yy < hz * 0.85)
    img = img * (1 - 0.25 * franjas[..., None]) + franjas[..., None] * 0.25 * np.array((0.85, 0.45, 0.35))
    sol = np.hypot(xx - w * 0.62, (yy - hz + 8) * 1.1)
    img = img + np.clip(1 - sol / 60, 0, 1)[..., None] ** 2 * np.array((0.45, 0.35, 0.15))
    img[sol < 16] = np.array((0.98, 0.86, 0.55))
    # Campo arado oscuro con surcos que se juntan en el horizonte
    cm_ = yy >= hz
    tt = (yy - hz) / (h - hz)
    img[cm_] = np.array((0.22, 0.15, 0.08)) * (1 - tt[cm_])[:, None] + np.array((0.10, 0.07, 0.04)) * tt[cm_][:, None]
    fase = (xx - w * 0.6) / np.maximum(yy - hz + 4, 1) * 9 + c.fbm(h, w, rng, (30, 8)) * 2
    surco = np.sin(fase) * 0.5 + 0.5
    img[cm_] *= (0.75 + 0.35 * surco[cm_])[:, None]
    brillo = cm_ & (surco > 0.97)
    img[brillo] = img[brillo] * 0.5 + np.array((0.40, 0.25, 0.11)) * 0.5
    _hierba(img, rng, hz + 1, 0.25)
    # Árboles en silueta y una casa lejana
    _arbol(img, rng, w * 0.18, hz + 6, 210, 110, np.array((0.07, 0.05, 0.05)))
    _arbol(img, rng, w * 0.86, hz + 2, 60, 34, np.array((0.10, 0.07, 0.06)))
    img[(yy > hz - 14) & (yy < hz + 1) & (np.abs(xx - w * 0.40) < 12)] = np.array((0.12, 0.08, 0.07))
    img[(yy > hz - 22) & (yy <= hz - 14) & (np.abs(xx - w * 0.40) < 12 - (hz - 14 - yy) * 1.4)] = np.array((0.10, 0.06, 0.06))
    return _barniz(_pinceladas(img, rng), rng)


def pintura_prado(w=512, h=342):
    rng = np.random.default_rng(25)
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    hz = h * 0.48
    img = np.array((0.50, 0.58, 0.64)) + (yy / hz)[..., None] * np.array((0.18, 0.14, 0.06))
    nubes = np.clip((c.fbm(h, w, rng, (110, 45, 18)) - 0.5) * 3, 0, 1) * (yy < hz * 0.8)
    img = img * (1 - nubes[..., None]) + nubes[..., None] * np.array((0.86, 0.84, 0.78))
    # Colinas lejanas azuladas
    col = hz - 22 - 18 * np.sin(xx / w * 5 + 1) - 8 * np.sin(xx / w * 13)
    img[(yy > col) & (yy < hz + 4)] = np.array((0.32, 0.40, 0.40))
    col2 = hz - 6 - 10 * np.sin(xx / w * 3 + 2)
    img[(yy > col2) & (yy < hz + 10)] = np.array((0.26, 0.34, 0.20))
    # Prado verde con flores
    pr = yy >= hz + 8
    t = (yy - hz) / (h - hz)
    img[pr] = np.array((0.42, 0.48, 0.20)) * (1 - t[pr])[:, None] + np.array((0.26, 0.32, 0.12)) * t[pr][:, None]
    _hierba(img, rng, hz + 8)
    for _ in range(160):
        y = rng.integers(int(hz + 14), h)
        x = rng.integers(0, w)
        r = 0.8 + (y - hz) / (h - hz) * 1.6
        m = (xx - x) ** 2 + (yy - y) ** 2 < r * r
        col = [np.array((0.75, 0.72, 0.60)), np.array((0.72, 0.62, 0.25)), np.array((0.60, 0.38, 0.40))][rng.integers(0, 3)]
        img[m] = img[m] * 0.4 + col * 0.6
    _arbol(img, rng, w * 0.70, hz + 26, 135, 100, np.array((0.16, 0.24, 0.10)))
    _arbol(img, rng, w * 0.12, hz + 10, 70, 45, np.array((0.20, 0.28, 0.14)))
    return _barniz(_pinceladas(img, rng), rng)


def cuadro(nombre, ancho, alto, pintura):
    c.escena_vacia()
    arr = pintura()
    img = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))
    img = img.filter(ImageFilter.GaussianBlur(0.8)).resize((img.width // 2, img.height // 2), Image.BOX)  # PSX: ~256 px
    lienzo = laminas.guardar(img, nombre + "_Lienzo")
    mats = [hornear.madera_vieja("MarcoCuadro", (0.30, 0.20, 0.10), desgaste=0.6),
            hornear.material_sucio("TraseraCuadro", (0.25, 0.20, 0.14), suciedad=0.6)]
    liston, fondo = 0.06, 0.045
    m = laminas.marco(nombre, ancho, alto, liston, fondo, mats)
    vis_w, vis_h = ancho - 2 * liston + 0.01, alto - 2 * liston + 0.01
    lz = laminas.objeto_imagen(nombre + "_Lienzo", [((0, 0), vis_w, vis_h, (0, 0, 1, 1), 0.0, -0.012)], lienzo, 0.5)
    return [m, lz]


# ---------------------------------------------------------------- estantería de libros

def estanteria_libros():
    c.escena_vacia()
    W, H, D = 1.0, 1.9, 0.30
    hs = hornear.material_sucio
    mats = [hornear.madera_vieja("Madera", "oscura", desgaste=0.5),
            hornear.madera_vieja("Balda", "oscura", suciedad=1.2, polvo=0.0, semilla=4.0)]
    colores = [(0.30, 0.08, 0.06), (0.10, 0.12, 0.18), (0.12, 0.16, 0.09), (0.48, 0.42, 0.30), (0.22, 0.13, 0.07),
               (0.06, 0.06, 0.05), (0.40, 0.28, 0.10), (0.36, 0.30, 0.24), (0.18, 0.08, 0.12), (0.52, 0.48, 0.40)]
    for i, col in enumerate(colores):
        mats.append(hs(f"Lomo{i}", col, rugosidad=0.7, suciedad=0.9, manchas=0.4, escala_manchas=15, semilla=i,
                       polvo=0.2))
    MAD, BAL = 0, 1
    LIB = list(range(2, 2 + len(colores)))
    bm = bmesh.new()
    cm = c.caja_mat
    for s in (-1, 1):
        cm(bm, (s * (W / 2 - 0.015), 0, H / 2), (0.03, D, H), MAD, 0.004)
    cm(bm, (0, D / 2 - 0.006, H / 2), (W - 0.03, 0.012, H - 0.02), MAD, 0)
    cm(bm, (0, -0.01, H - 0.015), (W + 0.04, D + 0.03, 0.03), MAD, 0.004)
    cm(bm, (0, -0.005, 0.04), (W + 0.01, D + 0.012, 0.08), MAD, 0.004)
    niveles = [0.08 + i * 0.355 for i in range(5)]
    for z in niveles[1:]:
        cm(bm, (0, 0, z), (W - 0.06, D - 0.015, 0.022), BAL, 0.003)
    rng = random.Random(13)
    fin = W / 2 - 0.035
    for nivel, z in enumerate(niveles):
        base = z + 0.011 if nivel else 0.08
        hueco = 0.355 - 0.03
        x = -W / 2 + 0.035
        pila_en = rng.choice([None, 0.15, 0.55, 0.8]) if nivel < 4 else 0.6
        while x < fin - 0.02:
            if pila_en is not None and x > -W / 2 + pila_en * W and x + 0.24 < fin:
                # Pila de libros tumbados
                zz = base
                for k in range(rng.randint(3, 6)):
                    bw, bd, bh = rng.uniform(0.17, 0.24), rng.uniform(0.13, 0.20), rng.uniform(0.025, 0.05)
                    cm(bm, (x + 0.12 + rng.uniform(-0.015, 0.015), -0.02 + (0.2 - bd) / 2, zz + bh / 2), (bw, bd, bh),
                       rng.choice(LIB), 0, rot=R(rng.uniform(-8, 8)))
                    zz += bh
                x += 0.255
                pila_en = None
                continue
            bw = rng.uniform(0.02, 0.055)
            bh = min(hueco - 0.01, rng.uniform(0.16, 0.30))
            bd = rng.uniform(0.14, 0.22)
            if x + bw > fin:
                break
            inclinado = rng.random() < 0.05 and x > -0.3
            rot = R(-12, "Y") if inclinado else None
            cm(bm, (x + bw / 2, -0.015 + (0.2 - bd) / 2, base + bh / 2), (bw, bd, bh), rng.choice(LIB), 0, rot=rot)
            x += bw + 0.001 + (0.05 if inclinado else 0)
    ob = c.objeto("EstanteriaLibros", bm, mats)
    limpiar_materiales(ob)
    hornear.atlas(ob, "EstanteriaLibros", tam=2048, margen=0.002)
    return [ob]


# ---------------------------------------------------------------- mesa baja: taza y mando

def taza():
    c.escena_vacia()
    hs = hornear.material_sucio
    mats = [hs("TazaLoza", (0.10, 0.11, 0.10), rugosidad=0.3, suciedad=0.8, manchas=0.4, color_sucio=(0.05, 0.04, 0.03)),
            hs("Cafe", (0.05, 0.03, 0.015), rugosidad=0.2, suciedad=0.0)]
    bm = bmesh.new()
    torno(bm, [(0.002, 0.0), (0.036, 0.0), (0.04, 0.006), (0.041, 0.095), (0.036, 0.095), (0.035, 0.012),
               (0.002, 0.012)], 0, 10)
    cil(bm, (0, 0, 0.055), 0.035, 0.002, 1, 10)                               # resto de café
    # Asa: medio aro de 6 tramos
    pts = [Vector((0.040 + 0.022 * math.sin(math.pi * k / 6), 0, 0.048 + 0.028 * math.cos(math.pi * k / 6)))
           for k in range(7)]
    for a, b in zip(pts, pts[1:]):
        barra(bm, a, b, 0.006, 0, 5)
    ob = c.objeto("Taza", bm, mats)
    for p in ob.data.polygons:
        p.use_smooth = len(p.vertices) == 4
    hornear.atlas(ob, "Taza", tam=512, margen=0.006)
    return [ob]


def mando():
    c.escena_vacia()
    hs = hornear.material_sucio
    mats = [hs("MandoNegro", (0.035, 0.035, 0.035), rugosidad=0.5, suciedad=0.6, manchas=0.3, desgaste=0.3,
               color_desgaste=(0.12, 0.12, 0.11)),
            hs("Tecla", (0.30, 0.30, 0.28), rugosidad=0.6, suciedad=0.6),
            hs("TeclaRoja", (0.45, 0.05, 0.04), rugosidad=0.5, suciedad=0.4)]
    bm = bmesh.new()
    c.caja_mat(bm, (0, 0, 0.011), (0.05, 0.18, 0.022), 0, 0.006)
    c.caja_mat(bm, (0.012, -0.075, 0.0225), (0.012, 0.01, 0.004), 2, 0)
    for i in range(5):
        for j in range(3):
            c.caja_mat(bm, (-0.013 + j * 0.013, -0.045 + i * 0.016, 0.0225), (0.009, 0.008, 0.004), 1, 0)
    for s in (-1, 1):
        c.caja_mat(bm, (0, 0.045 + s * 0.012, 0.0225), (0.03, 0.007, 0.004), 1, 0)
    ob = c.objeto("Mando", bm, mats)
    hornear.atlas(ob, "Mando", tam=512, margen=0.006)
    return [ob]


PIEZAS = {
    "Alfombra": alfombra_salon,
    "AlfombraPasillo": alfombra_pasillo,
    "PlantaGrande": planta_grande,
    "PercheroPared": perchero_pared,
    "CuadroPaisaje1": lambda: cuadro("CuadroPaisaje1", 0.85, 0.60, pintura_bosque),
    "CuadroPaisaje2": lambda: cuadro("CuadroPaisaje2", 0.55, 0.70, pintura_atardecer),
    "CuadroPaisaje3": lambda: cuadro("CuadroPaisaje3", 0.75, 0.50, pintura_prado),
    "EstanteriaLibros": estanteria_libros,
    "Taza": taza,
    "Mando": mando,
}


if __name__ == "__main__":
    for n in (sys.argv[1:] or list(PIEZAS)):
        exportar(n, PIEZAS[n]())
