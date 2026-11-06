"""Objetos con imagen, en estilo PSX: la foto de la boda, el calendario de la cocina y las notas del corcho
del sótano (lo que Chechu sabe de Chevas y Roberta).

  FotoBoda      marco de pared de 0,30 x 0,40 (PARED: origen en el centro de la cara de atrás).
                Dos objetos: "FotoBoda" (marco horneado) y "FotoBoda_Imagen" (la foto, textura propia).
  FotoBodaMesa  la misma foto, más pequeña (0,18 x 0,23), en un marco de pie para un mueble.
  Calendario    calendario de pared de 0,30 x 0,46 colgado de un clavo (PARED). Noviembre, con el
                aniversario marcado y los días de Roberta con su hermana.
  NotasCorcho   lo que va clavado en el corcho del sótano: fotos de la casa desde enfrente, Roberta en
                la ventana, la foto de la boda con la cara de Chevas rayada, un plano de la casa y notas.
                Ocupa 0,80 x 0,55; origen en el centro, sobre la cara del corcho (PARED). Tres objetos:
                "NotasCorcho" (papeles y fotos), "Hilos" (hilo rojo) y "Chinchetas".

Uso:  python Tools/assets/laminas.py [Nombre ...]
Salida: Models/<Nombre>.fbx y sus imágenes en Models/Texturas (necesita Pillow).
"""
import math
import os
import random
import sys

import bpy
import bmesh
import numpy as np
from mathutils import Matrix, Vector
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(__file__))
import comun as c  # noqa: E402
import hornear  # noqa: E402

FUENTE = "/usr/share/fonts/truetype/freefont/FreeSans.ttf"
FUENTE_N = "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"


# ---------------------------------------------------------------- dibujo

def fuente(tam, negrita=False):
    try:
        return ImageFont.truetype(FUENTE_N if negrita else FUENTE, tam)
    except OSError:
        return ImageFont.load_default()


def a_mano(img, xy, texto, tam, color=(30, 30, 60), giro=0.0, semilla=0, negrita=False):
    """Texto que parece escrito a mano: ondulado, inclinado y con el trazo irregular."""
    rnd = random.Random(semilla)
    f = fuente(tam, negrita)
    lineas = texto.split("\n")
    w = int(max(f.getlength(l) for l in lineas) + tam)
    h = int(len(lineas) * tam * 1.25 + tam)
    capa = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(capa)
    for i, l in enumerate(lineas):
        x = tam * 0.3
        for ch in l:
            dy = rnd.uniform(-tam * 0.06, tam * 0.06)
            d.text((x, tam * 0.3 + i * tam * 1.25 + dy), ch, font=f, fill=255)
            x += f.getlength(ch) * rnd.uniform(0.92, 1.05)
    a = np.asarray(capa).astype(np.float32)
    # Ondulación vertical y cursiva
    ys, xs = np.mgrid[0:h, 0:w]
    src_x = (xs + (ys - h / 2) * 0.22).astype(int).clip(0, w - 1)
    src_y = (ys + np.sin(xs / (tam * 1.7) + semilla) * tam * 0.08).astype(int).clip(0, h - 1)
    a = a[src_y, src_x]
    capa = Image.fromarray(a.astype(np.uint8)).filter(ImageFilter.GaussianBlur(tam * 0.02))
    capa = capa.rotate(giro, expand=True, resample=Image.BICUBIC)
    img.paste(Image.new("RGB", capa.size, color), xy, capa)


def grano(img, fuerza=10, semilla=0, vineta=0.35):
    rng = np.random.default_rng(semilla)
    a = np.asarray(img).astype(np.float32)
    h, w = a.shape[:2]
    a += rng.normal(0, fuerza, (h, w, 1))
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.hypot((xx - w / 2) / (w / 2), (yy - h / 2) / (h / 2))
    a *= (1 - vineta * np.clip(r - 0.4, 0, 1))[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def revelada(img, borde=0.06, color=(232, 226, 210), tono=(1.05, 0.98, 0.85), semilla=0):
    """Foto de papel de los 90-2000: colores desvaídos y cálidos, grano y borde blanco."""
    a = np.asarray(img).astype(np.float32)
    a = a * np.array(tono) * 0.85 + 25
    img = grano(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2)),
                9, semilla)
    w, h = img.size
    b = int(min(w, h) * borde)
    marco = Image.new("RGB", (w + 2 * b, h + 2 * b), color)
    marco.paste(img, (b, b))
    return marco


def fecha_camara(img, texto):
    """Fecha naranja impresa por la cámara, abajo a la derecha."""
    d = ImageDraw.Draw(img)
    w, h = img.size
    f = fuente(int(h * 0.07), True)
    d.text((w * 0.62, h * 0.86), texto, font=f, fill=(255, 140, 40))


def persona(d, x, base, alto, ropa, piel=(205, 160, 130), pelo=(50, 35, 25), vestido=False, velo=False):
    cab = alto * 0.13
    if velo:
        d.polygon([(x - cab * 0.5, base - alto + cab * 0.1), (x + cab * 0.5, base - alto + cab * 0.1),
                   (x + alto * 0.30, base - alto * 0.35), (x - alto * 0.12, base - alto * 0.4)], fill=(215, 215, 205))
    d.ellipse((x - cab * 0.55, base - alto - cab * 0.1, x + cab * 0.55, base - alto + cab * 0.7), fill=pelo)
    d.ellipse((x - cab * 0.42, base - alto + cab * 0.15, x + cab * 0.42, base - alto + cab * 1.05), fill=piel)
    if vestido:
        d.polygon([(x - alto * 0.07, base - alto + cab), (x + alto * 0.07, base - alto + cab),
                   (x + alto * 0.26, base), (x - alto * 0.26, base)], fill=ropa)
    else:
        d.rectangle((x - alto * 0.11, base - alto + cab, x + alto * 0.11, base - alto * 0.45), fill=ropa)
        d.rectangle((x - alto * 0.10, base - alto * 0.45, x + alto * 0.10, base), fill=ropa)
        d.polygon([(x - alto * 0.03, base - alto + cab), (x + alto * 0.03, base - alto + cab),
                   (x, base - alto * 0.6)], fill=(230, 230, 225))


def imagen_boda(w=640, h=480, rayada=False):
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(1)
    # Fachada de piedra de la iglesia y la puerta en arco
    piedra = (rng.random((h // 8, w // 8)) * 25 + 140).astype(np.uint8)
    p = Image.fromarray(piedra).resize((w, h), Image.NEAREST).convert("RGB")
    img.paste(p.point(lambda v: int(v * 0.95)), (0, 0))
    d.rectangle((int(w * 0.30), int(h * 0.20), int(w * 0.70), h), fill=(105, 75, 50))
    d.ellipse((int(w * 0.30), int(h * 0.05), int(w * 0.70), int(h * 0.35)), fill=(105, 75, 50))
    d.rectangle((0, int(h * 0.88), w, h), fill=(120, 110, 95))
    for x0 in (0.0, 0.80):                                                          # setos a los lados
        d.ellipse((w * x0 - w * 0.05, h * 0.55, w * x0 + w * 0.25, h * 0.95), fill=(55, 80, 45))
    persona(d, w * 0.40, h * 0.95, h * 0.72, (25, 25, 30))                            # él
    persona(d, w * 0.58, h * 0.95, h * 0.66, (238, 236, 228), pelo=(90, 55, 30), vestido=True, velo=True)
    d.ellipse((w * 0.50, h * 0.52, w * 0.56, h * 0.58), fill=(200, 60, 80))         # ramo
    d.ellipse((w * 0.52, h * 0.50, w * 0.57, h * 0.55), fill=(240, 220, 120))
    img = img.filter(ImageFilter.GaussianBlur(1.5))
    if rayada:
        d = ImageDraw.Draw(img)
        x, y = w * 0.40, h * 0.95 - h * 0.72
        rnd = random.Random(4)
        for _ in range(40):
            d.line((x + rnd.uniform(-35, 35), y + rnd.uniform(-10, 70), x + rnd.uniform(-35, 35),
                    y + rnd.uniform(-10, 70)), fill=(15, 15, 15), width=4)
    return revelada(img, semilla=2)


def imagen_casa_noche():
    w, h = 640, 480
    img = Image.new("RGB", (w, h), (12, 14, 22))
    d = ImageDraw.Draw(img)
    d.rectangle((0, h * 0.82, w, h), fill=(25, 25, 25))
    d.rectangle((w * 0.15, h * 0.40, w * 0.85, h * 0.85), fill=(38, 36, 34))
    d.polygon([(w * 0.10, h * 0.42), (w * 0.5, h * 0.18), (w * 0.90, h * 0.42)], fill=(28, 26, 26))
    d.rectangle((w * 0.25, h * 0.52, w * 0.36, h * 0.66), fill=(30, 30, 30))
    d.rectangle((w * 0.60, h * 0.52, w * 0.72, h * 0.66), fill=(230, 190, 90))      # ventana con luz
    d.rectangle((w * 0.45, h * 0.58, w * 0.54, h * 0.85), fill=(22, 20, 18))
    d.ellipse((w * 0.88, h * 0.05, w * 1.05, h * 0.25), fill=(90, 80, 50))          # farola
    img = img.filter(ImageFilter.GaussianBlur(2.5))
    img = grano(img, 14, 5, 0.6)
    fecha_camara(img, "'02 11 08")
    return revelada(img, semilla=5)


def imagen_ventana():
    w, h = 480, 640
    img = Image.new("RGB", (w, h), (30, 28, 26))
    d = ImageDraw.Draw(img)
    d.rectangle((w * 0.2, h * 0.25, w * 0.8, h * 0.75), fill=(200, 165, 90))
    persona(d, w * 0.52, h * 0.95, h * 0.62, (150, 130, 140), pelo=(40, 25, 20))
    d.rectangle((0, h * 0.75, w, h), fill=(30, 28, 26))
    d.rectangle((w * 0.2, h * 0.25, w * 0.32, h * 0.75), fill=(120, 60, 50))         # cortina
    img = img.filter(ImageFilter.GaussianBlur(3))
    img = grano(img, 14, 6, 0.6)
    fecha_camara(img, "'02 11 12")
    return revelada(img, semilla=6)


def papel(w, h, color=(225, 218, 195), rayas=False, semilla=0):
    img = Image.new("RGB", (w, h), color)
    d = ImageDraw.Draw(img)
    if rayas:
        for y in range(int(h * 0.15), h, max(12, h // 14)):
            d.line((0, y, w, y), fill=(150, 170, 200), width=2)
        d.line((w * 0.12, 0, w * 0.12, h), fill=(210, 120, 120), width=2)
    return grano(img, 6, semilla, 0.25)


def nota(texto, w=360, h=280, color=(232, 214, 120), tam=46, semilla=0, rayas=False, tinta=(25, 25, 70)):
    img = papel(w, h, color, rayas, semilla)
    a_mano(img, (int(w * 0.07), int(h * 0.08)), texto, tam, tinta, giro=random.Random(semilla).uniform(-4, 4),
           semilla=semilla)
    return img


def imagen_plano():
    w, h = 640, 480
    img = papel(w, h, (220, 215, 200), False, 8)
    d = ImageDraw.Draw(img)
    lapiz = (60, 60, 70)
    for r in ((60, 60, 300, 250), (300, 60, 460, 250), (460, 60, 590, 250), (60, 250, 250, 420),
              (250, 250, 400, 420), (400, 250, 590, 420)):
        d.rectangle(r, outline=lapiz, width=4)
    for (x, y), t in (((90, 140), "salón"), ((320, 140), "cocina"), ((470, 140), "colada"), ((80, 320), "dorm."),
                      ((270, 320), "baño"), ((420, 320), "garaje")):
        a_mano(img, (x, y), t, 34, lapiz, semilla=x)
    d.line((300, 360, 340, 400), fill=(170, 20, 20), width=6)
    d.line((340, 360, 300, 400), fill=(170, 20, 20), width=6)
    a_mano(img, (240, 425), "baldosa", 28, (170, 20, 20), semilla=3)
    a_mano(img, (430, 5), "IGUAL QUE LA MÍA", 30, lapiz, semilla=9, negrita=True)
    d.line((520, 420, 520, 470), fill=lapiz, width=4)
    a_mano(img, (535, 430), "¿?", 34, lapiz, semilla=10)
    return img


def imagen_calendario():
    w, h = 480, 736
    img = Image.new("RGB", (w, h), (226, 222, 210))
    d = ImageDraw.Draw(img)
    # Foto de arriba: un lago con montañas
    for y in range(0, 330):
        t = y / 330
        d.line((20, 20 + y, w - 20, 20 + y), fill=(int(120 + 80 * t), int(150 + 60 * t), int(190 + 30 * t)))
    d.polygon([(20, 260), (150, 120), (260, 230), (360, 100), (w - 20, 240), (w - 20, 350), (20, 350)],
              fill=(80, 90, 85))
    d.rectangle((20, 270, w - 20, 350), fill=(70, 100, 130))
    d.polygon([(130, 140), (150, 120), (170, 140)], fill=(240, 240, 240))
    d.polygon([(340, 120), (360, 100), (380, 120)], fill=(240, 240, 240))
    # Mes
    d.rectangle((20, 360, w - 20, 410), fill=(170, 30, 30))
    f = fuente(38, True)
    d.text((w / 2, 385), "NOVIEMBRE", font=f, fill=(250, 245, 235), anchor="mm")
    fd = fuente(24, True)
    dias = "LMXJVSD"
    cw = (w - 40) / 7
    for i, ch in enumerate(dias):
        d.text((20 + cw * (i + 0.5), 428), ch, font=fd, fill=(170, 30, 30) if ch == "D" else (60, 60, 60),
               anchor="mm")
    fn = fuente(26)
    inicio = 4  # empieza en viernes
    cel = {}
    for dia in range(1, 31):
        k = inicio + dia - 1
        x = 20 + cw * (k % 7 + 0.5)
        y = 460 + (k // 7) * 52
        cel[dia] = (x, y)
        d.text((x, y), str(dia), font=fn, fill=(170, 30, 30) if k % 7 == 6 else (50, 50, 50), anchor="mm")
        d.line((20, y + 26, w - 20, y + 26), fill=(200, 195, 185), width=1)
    # Aniversario marcado y los días de Roberta con su hermana
    x, y = cel[14]
    d.ellipse((x - 26, y - 24, x + 26, y + 24), outline=(190, 20, 20), width=4)
    a_mano(img, (int(x - 40), int(y + 4)), "11 años", 20, (190, 20, 20), semilla=14)
    x0, y0 = cel[4]
    x1, _ = cel[7]
    d.line((x0 - 20, y0 + 12, x1 + 20, y0 + 12), fill=(30, 30, 120), width=3)
    a_mano(img, (int(x0 - 22), int(y0 + 8)), "R. con su hermana", 18, (30, 30, 120), semilla=4)
    x, y = cel[21]
    a_mano(img, (int(x - 28), int(y + 4)), "butano", 17, (30, 30, 30), semilla=21)
    return grano(img, 6, 3, 0.2)


def reducir(img, f=2):
    w, h = img.size
    return img.resize((max(1, w // f), max(1, h // f)), Image.BOX)


def guardar(img, nombre):
    os.makedirs(c.TEXTURAS, exist_ok=True)
    ruta = os.path.join(c.TEXTURAS, nombre + ".jpg")
    img.convert("RGB").save(ruta, quality=90)
    return bpy.data.images.load(ruta)


# ---------------------------------------------------------------- geometría

def quad(bm, uv, centro, ancho, alto, uvrect=(0, 0, 1, 1), giro=0.0, y=0.0):
    """Lámina vertical mirando a -Y (frente a +Z en Unity) con su rectángulo de UV."""
    rot = Matrix.Rotation(math.radians(giro), 3, "Y")
    u0, v0, u1, v1 = uvrect
    esquinas = [(-ancho / 2, -alto / 2, u0, v0), (ancho / 2, -alto / 2, u1, v0), (ancho / 2, alto / 2, u1, v1),
                (-ancho / 2, alto / 2, u0, v1)]
    vs = [bm.verts.new(Vector((centro[0], y, centro[1])) + rot @ Vector((x, 0, z))) for x, z, _, _ in esquinas]
    f = bm.faces.new(vs)
    f.normal_update()
    if f.normal.y > 0:
        f.normal_flip()
    for l, (_, _, u, v) in zip(f.loops, esquinas if f.normal.y <= 0 else esquinas):
        l[uv].uv = (u, v)
    return f


def objeto_imagen(nombre, quads, imagen, rugosidad=0.6):
    """Objeto de láminas con su propia textura (no se hornea). quads: [(centro, ancho, alto, uvrect, giro, y)]."""
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new("UV")
    for q in quads:
        quad(bm, uv, *q)
    me = bpy.data.meshes.new(nombre)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(c.material(nombre, imagen, rugosidad=rugosidad))
    ob = bpy.data.objects.new(nombre, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def marco(nombre, ancho, alto, listón, fondo, mats, de_pie=False):
    bm = bmesh.new()
    cm = c.caja_mat
    y = -fondo / 2
    cm(bm, (0, y, alto / 2 - listón / 2), (ancho, fondo, listón), 0, 0.004)
    cm(bm, (0, y, -alto / 2 + listón / 2), (ancho, fondo, listón), 0, 0.004)
    for s in (-1, 1):
        cm(bm, (s * (ancho / 2 - listón / 2), y, 0), (listón, fondo, alto - 2 * listón), 0, 0.004)
    cm(bm, (0, -0.002, 0), (ancho - listón, 0.004, alto - listón), 1, 0)                 # trasera
    if de_pie:
        c.caja_mat(bm, (0, 0.05, -alto * 0.12), (0.04, 0.006, alto * 0.8), 1, 0,
                   rot=Matrix.Rotation(math.radians(-25), 3, "X"))
    ob = c.objeto(nombre, bm, mats)
    hornear.atlas(ob, nombre, tam=512, margen=0.01)
    return ob


def foto_boda_pared():
    # Foto apaisada en un marco vertical girado: el marco es de 0,40 de ancho por 0,30 de alto
    c.escena_vacia()
    mats = [hornear.madera_vieja("Marco", "oscura", desgaste=0.4),
            hornear.material_sucio("Trasera", (0.25, 0.20, 0.14), suciedad=0.6)]
    img = guardar(reducir(imagen_boda(), 4), "FotoBoda_Imagen")
    m = marco("FotoBoda", 0.40, 0.30, 0.035, 0.025, mats)
    foto = objeto_imagen("FotoBoda_Imagen", [((0, 0), 0.34, 0.24, (0, 0, 1, 1), 0.0, -0.006)], img, 0.3)
    return [m, foto]


def foto_boda_mesa():
    c.escena_vacia()
    mats = [hornear.madera_vieja("Marco", "oscura", desgaste=0.4),
            hornear.material_sucio("Trasera", (0.25, 0.20, 0.14), suciedad=0.6)]
    img = guardar(reducir(imagen_boda(), 4), "FotoBoda_Imagen")
    m = marco("FotoBodaMesa", 0.23, 0.18, 0.025, 0.02, mats, de_pie=True)
    foto = objeto_imagen("FotoBodaMesa_Imagen", [((0, 0), 0.19, 0.14, (0, 0, 1, 1), 0.0, -0.006)], img, 0.3)
    for o in (m, foto):
        o.rotation_euler = (math.radians(-12), 0, 0)
        o.location = (0, 0.0, 0.09)
    return [m, foto]


def calendario():
    c.escena_vacia()
    img = guardar(reducir(imagen_calendario(), 2), "Calendario")
    hoja = objeto_imagen("Calendario", [((0, -0.23), 0.30, 0.46, (0, 0, 1, 1), 0.0, -0.004)], img, 0.8)
    bm = bmesh.new()
    c.caja_mat(bm, (0, -0.004, -0.005), (0.30, 0.006, 0.012), 0, 0)                # varilla
    c.marcar(bm)
    bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=0.004, radius2=0.004, depth=0.02)
    nv = c.nuevos(bm)
    bmesh.ops.rotate(bm, verts=nv, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, "X"))
    bmesh.ops.translate(bm, verts=nv, vec=(0, -0.01, 0.02))
    clavo = c.objeto("Calendario_Clavo", bm, [hornear.material_liso("Calendario_Metal", (0.3, 0.3, 0.3), metal=1.0)])
    return [hoja, clavo]


# Corcho: (imagen, centro x, centro z, ancho, alto, giro en grados)
def piezas_corcho():
    rng = random.Random(11)
    return [
        (imagen_casa_noche(), -0.27, 0.15, 0.15, 0.115, -4),
        (imagen_ventana(), -0.08, 0.14, 0.10, 0.13, 3),
        (imagen_boda(rayada=True), 0.13, 0.16, 0.14, 0.105, -6),
        (imagen_plano(), 0.28, -0.07, 0.20, 0.15, 2),
        (nota("11 AÑOS\naniversario 14", semilla=1), 0.04, -0.01, 0.10, 0.078, 4),
        (nota("Roberta:\n4 días con\nsu hermana", 360, 300, (226, 220, 205), 44, 2, True), -0.27, -0.04, 0.11,
         0.09, -5),
        (nota("grifo baño\nGOTEA", semilla=3), -0.10, -0.06, 0.09, 0.07, 6),
        (nota("3:33", 300, 240, (232, 214, 120), 110, 4, tinta=(150, 20, 20)), 0.06, -0.18, 0.08, 0.064, -3),
        (nota("las paredes\nson de papel", 380, 260, (226, 220, 205), 44, 5, True), -0.29, -0.19, 0.11, 0.075, 3),
        (nota("ÉL NO SE DA\nCUENTA", 380, 220, (232, 214, 120), 46, 6, tinta=(150, 20, 20)), -0.10, -0.19, 0.11,
         0.064, -2),
        (nota("cuadro de la\nluz: garaje", 360, 240, (226, 220, 205), 42, 7, True), 0.33, 0.14, 0.09, 0.06,
         rng.uniform(-6, 6)),
    ]


def notas_corcho():
    c.escena_vacia()
    piezas = piezas_corcho()
    # Atlas: cada pieza en su celda de una cuadrícula 4 x 3 de 1024 x 768 (luego a la mitad)
    W, H = 1024, 768
    cw, ch = W // 4, H // 3
    atlas = Image.new("RGB", (W, H), (0, 0, 0))
    quads = []
    for i, (img, x, z, ancho, alto, giro) in enumerate(piezas):
        cx, cy = (i % 4) * cw, (i // 4) * ch
        esc = min(cw / ancho, ch / alto) * 0.96
        tw, th = int(ancho * esc), int(alto * esc)
        atlas.paste(img.resize((tw, th), Image.LANCZOS), (cx, cy))
        uv = (cx / W, 1 - (cy + th) / H, (cx + tw) / W, 1 - cy / H)
        quads.append(((x, z), ancho, alto, uv, giro, -0.002 - 0.0007 * i))
    img = guardar(reducir(atlas, 2), "NotasCorcho")
    notas = objeto_imagen("NotasCorcho", quads, img, 0.8)
    # Chinchetas y el hilo rojo que une lo que Chechu ha ido atando
    bm = bmesh.new()
    puntos = []
    for (_, x, z, ancho, alto, giro) in piezas:
        a = math.radians(giro)
        px, pz = x - math.sin(a) * alto * 0.38, z + math.cos(a) * alto * 0.38
        puntos.append((px, pz))
        c.marcar(bm)
        bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=0.006, radius2=0.004, depth=0.012)
        nv = c.nuevos(bm)
        bmesh.ops.rotate(bm, verts=nv, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, "X"))
        bmesh.ops.translate(bm, verts=nv, vec=(px, -0.014, pz))
    chinchetas = c.objeto("Chinchetas", bm, [hornear.material_liso("Chincheta", (0.55, 0.05, 0.04), rugosidad=0.3)])
    bm = bmesh.new()
    for a, b in ((0, 2), (2, 4), (4, 1), (1, 5), (5, 6), (6, 3), (3, 7), (7, 9), (2, 3), (0, 10)):
        pa, pb = Vector((puntos[a][0], -0.016, puntos[a][1])), Vector((puntos[b][0], -0.016, puntos[b][1]))
        c.marcar(bm)
        bmesh.ops.create_cone(bm, cap_ends=True, segments=3, radius1=0.0012, radius2=0.0012, depth=(pb - pa).length)
        nv = c.nuevos(bm)
        bmesh.ops.transform(bm, matrix=(pb - pa).to_track_quat("Z", "Y").to_matrix().to_4x4(), verts=nv)
        bmesh.ops.translate(bm, verts=nv, vec=(pa + pb) / 2)
    hilos = c.objeto("Hilos", bm, [hornear.material_liso("Hilo", (0.45, 0.02, 0.02), rugosidad=0.9)])
    return [notas, hilos, chinchetas]


PIEZAS = {"FotoBoda": foto_boda_pared, "FotoBodaMesa": foto_boda_mesa, "Calendario": calendario,
          "NotasCorcho": notas_corcho}


def main(nombre):
    objs = PIEZAS[nombre]()
    ruta = c.exportar_fbx(nombre, objs)
    tris = sum(len(p.vertices) - 2 for o in objs for p in o.data.polygons)
    print(f"Exportado {ruta} ({tris} triángulos)")


if __name__ == "__main__":
    for n in (sys.argv[1:] or list(PIEZAS)):
        main(n)
