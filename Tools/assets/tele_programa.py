"""Programa que ve Roberta: teletienda de cuchillos ("¡corta hasta un zapato!") con el rótulo 2x1.

Atlas de 4 x 4 fotogramas de 256 x 192 (1024 x 768 JPG), con colores de tele vieja (algo saturados,
blandos, con sangrado de color y líneas). Orden: de izquierda a derecha y de arriba abajo.
  0-7   un cuchillo corta un tomate (baja, corta, se abren las mitades)
  8-11  el mismo cuchillo corta un zapato viejo
  12-15 plano del producto con los cuchillos en abanico y "¡2x1! LLAME YA" parpadeando
En todos, el logotipo de la teletienda y el rótulo "2x1" en las esquinas.

En Unity el UV va de abajo arriba: el fotograma i tiene offset (col/4, 1 - (fila+1)/4) y tiling (0.25, 0.25),
con col = i % 4 y fila = i // 4.

Uso:  python Tools/assets/tele_programa.py
Salida: Assets/_Ominous/Art/Models/Texturas/Tele_Programa.jpg   (necesita Pillow)
"""
import math
import os
import sys
import tempfile

import bpy
import bmesh
import numpy as np
from mathutils import Matrix, Vector
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(__file__))
import comun as c  # noqa: E402

SALIDA = os.path.join(c.RAIZ, "Assets", "_Ominous", "Art", "Models", "Texturas", "Tele_Programa.jpg")
FW, FH = 256, 192
FUENTES = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
           "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"]


# ---------------------------------------------------------------- escena

def mat(nombre, color, rug=0.5, metal=0.0, brillo=0.5):
    m = bpy.data.materials.new(nombre)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rug
    b.inputs["Metallic"].default_value = metal
    return m


def obj(nombre, bm, mats, suave=True):
    me = bpy.data.meshes.new(nombre)
    bm.to_mesh(me)
    bm.free()
    for m in mats:
        me.materials.append(m)
    for p in me.polygons:
        p.use_smooth = suave
    ob = bpy.data.objects.new(nombre, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def esfera(bm, centro, esc, seg=16):
    c.marcar(bm)
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=seg // 2, radius=1.0)
    nv = c.nuevos(bm)
    bmesh.ops.scale(bm, vec=esc, verts=nv)
    bmesh.ops.translate(bm, vec=centro, verts=nv)
    return nv


def mitades(nombre, construir, m_fuera, m_dentro):
    """Dos mitades (delante y = -, detrás y = +) de un objeto cortado por el plano y = 0, con la cara del corte."""
    res = []
    for signo in (-1, 1):
        bm = bmesh.new()
        construir(bm)
        geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
        bmesh.ops.bisect_plane(bm, geom=geom, plane_co=(0, 0.0007, 0), plane_no=(0, signo, 0), clear_inner=True)
        corte = [e for e in bm.edges if e.is_boundary]
        tapa = bmesh.ops.holes_fill(bm, edges=corte, sides=1000)["faces"]
        for f in bm.faces:
            f.material_index = 1 if f in tapa else 0
        res.append(obj(f"{nombre}_{signo}", bm, [m_fuera, m_dentro]))
    return res


def tomate(bm):
    esfera(bm, (0, 0, 0.058), (0.05, 0.048, 0.04), seg=20)


def zapato(bm):
    """Zapato de cordones viejo, puntera hacia -X: suela, tacón, empeine que sube hacia el talón y boca."""
    c.caja(bm, (-0.005, 0, 0.027), (0.27, 0.095, 0.014), biselado=0.006, segmentos=2)      # suela
    c.caja(bm, (0.095, 0, 0.022), (0.065, 0.08, 0.03), biselado=0.005)                     # tacón
    c.marcar(bm)
    c.caja(bm, (0.02, 0, 0.068), (0.2, 0.088, 0.075), biselado=0.028, segmentos=3)         # empeine
    for v in c.nuevos(bm):                                                                  # baja hacia la puntera
        if v.co.z > 0.05:
            v.co.z -= max(0.0, -v.co.x + 0.02) * 0.35
    esfera(bm, (-0.085, 0, 0.05), (0.06, 0.045, 0.026))                                    # puntera


def cuchillo(m_hoja, m_mango, m_remache):
    """Hoja en el plano YZ (filo abajo, punta hacia +Y), mango hacia -Y. Origen en el talón del filo."""
    bm = bmesh.new()
    perfil = [(0.0, 0.0), (0.20, 0.0), (0.215, 0.012), (0.17, 0.035), (0.0, 0.045)]
    vs = [bm.verts.new((-0.0012, y, z)) for y, z in perfil]
    f = bm.faces.new(vs)
    r = bmesh.ops.extrude_face_region(bm, geom=[f])
    bmesh.ops.translate(bm, vec=(0.0024, 0, 0), verts=[v for v in r["geom"] if isinstance(v, bmesh.types.BMVert)])
    for f in bm.faces:
        f.material_index = 0
    c.marcar(bm)
    c.caja(bm, (0, -0.06, 0.024), (0.016, 0.12, 0.024), biselado=0.006, segmentos=2)
    for f in {f for v in c.nuevos(bm) for f in v.link_faces}:
        f.material_index = 1
    for y in (-0.03, -0.065, -0.10):
        c.marcar(bm)
        c.caja(bm, (0, y, 0.024), (0.0175, 0.008, 0.008), biselado=0.003)
        for f in {f for v in c.nuevos(bm) for f in v.link_faces}:
            f.material_index = 2
    return obj("Cuchillo", bm, [m_hoja, m_mango, m_remache], suave=False)


def mano_derecha(m_piel, m_manga):
    """Puño cerrado alrededor del mango (en el origen del cuchillo) y antebrazo con puño de camisa."""
    bm = bmesh.new()
    esfera(bm, (0.014, -0.065, 0.034), (0.024, 0.048, 0.03))                   # palma y dorso
    for i in range(4):
        esfera(bm, (-0.008, -0.03 - i * 0.022, 0.018), (0.012, 0.011, 0.02), seg=10)  # dedos por delante
    esfera(bm, (-0.006, -0.03, 0.045), (0.011, 0.024, 0.01), seg=10)            # pulgar encima
    for f in bm.faces:
        f.material_index = 0
    c.marcar(bm)
    bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=0.028, radius2=0.034, depth=0.30)
    nv = c.nuevos(bm)
    d = Vector((0.55, -0.75, 0.35)).normalized()
    bmesh.ops.transform(bm, matrix=d.to_track_quat("Z", "Y").to_matrix().to_4x4(), verts=nv)
    bmesh.ops.translate(bm, vec=Vector((0.02, -0.10, 0.04)) + d * 0.15, verts=nv)
    for f in {f for v in nv for f in v.link_faces}:
        f.material_index = 1
    return obj("ManoD", bm, [m_piel, m_manga])


def mano_izquierda(m_piel, m_manga):
    """Mano plana que sujeta desde la izquierda, con los dedos por encima."""
    bm = bmesh.new()
    esfera(bm, (-0.11, 0.0, 0.06), (0.05, 0.04, 0.02))
    for i in range(4):
        esfera(bm, (-0.06, -0.03 + i * 0.02, 0.085), (0.03, 0.009, 0.009), seg=10)
    esfera(bm, (-0.075, -0.05, 0.05), (0.025, 0.01, 0.01), seg=10)
    for f in bm.faces:
        f.material_index = 0
    c.marcar(bm)
    bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=0.03, radius2=0.035, depth=0.3)
    nv = c.nuevos(bm)
    d = Vector((-1, 0.2, 0.25)).normalized()
    bmesh.ops.transform(bm, matrix=d.to_track_quat("Z", "Y").to_matrix().to_4x4(), verts=nv)
    bmesh.ops.translate(bm, vec=Vector((-0.15, 0.0, 0.06)) + d * 0.15, verts=nv)
    for f in {f for v in nv for f in v.link_faces}:
        f.material_index = 1
    return obj("ManoI", bm, [m_piel, m_manga])


def escena():
    c.escena_vacia()
    s = bpy.context.scene
    s.render.engine = "CYCLES"
    s.cycles.samples = 24
    s.cycles.use_denoising = True
    s.render.resolution_x, s.render.resolution_y = FW * 2, FH * 2
    s.view_settings.view_transform = "Standard"
    w = bpy.data.worlds.new("W"); s.world = w; w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.25, 0.35, 0.6, 1)
    w.node_tree.nodes["Background"].inputs[1].default_value = 0.25
    # Plató: encimera blanca y fondo azul de teletienda
    bm = bmesh.new(); c.caja(bm, (0, 0.1, -0.01), (2.0, 1.2, 0.02)); obj("Encimera", bm, [mat("Formica", (0.75, 0.72, 0.66), 0.4)], False)
    bm = bmesh.new(); c.caja(bm, (0, 0.6, 0.4), (2.0, 0.02, 1.0)); obj("Fondo", bm, [mat("Azul", (0.03, 0.08, 0.45), 0.8)], False)
    bm = bmesh.new(); c.caja(bm, (0, 0, 0.01), (0.42, 0.26, 0.02), biselado=0.004); obj("Tabla", bm, [mat("Tabla", (0.45, 0.25, 0.10), 0.6)], False)
    for nombre, loc, en in (("Clave", (0.6, -0.6, 0.9), 30), ("Relleno", (-0.7, -0.4, 0.5), 10), ("Contra", (0, 0.4, 0.8), 15)):
        ld = bpy.data.lights.new(nombre, "AREA"); ld.energy = en; ld.size = 0.8; ld.color = (1, 0.95, 0.85)
        lo = bpy.data.objects.new(nombre, ld); s.collection.objects.link(lo); lo.location = loc
        lo.rotation_euler = (Vector((0, 0, 0.05)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam")); s.collection.objects.link(cam); s.camera = cam
    piel = mat("Piel", (0.55, 0.30, 0.20), 0.5)
    manga = mat("Manga", (0.80, 0.80, 0.82), 0.7)
    roja = mat("Tomate", (0.55, 0.02, 0.01), 0.15)
    pulpa = mat("Pulpa", (0.75, 0.12, 0.06), 0.4)
    cuero = mat("Cuero", (0.12, 0.06, 0.03), 0.5)
    corte = mat("CorteCuero", (0.35, 0.22, 0.12), 0.8)
    acero = mat("Acero", (0.55, 0.56, 0.58), 0.32, 0.8)
    negro = mat("Mango", (0.02, 0.02, 0.02), 0.4)
    laton = mat("Remache", (0.8, 0.7, 0.4), 0.3, 1.0)
    return dict(cam=cam, piel=piel, manga=manga, tomate=mitades("Tomate", tomate, roja, pulpa),
                zapato=mitades("Zapato", zapato, cuero, corte), cuchillo=cuchillo(acero, negro, laton),
                mano_d=mano_derecha(piel, manga), mano_i=mano_izquierda(piel, manga), metal=(acero, negro, laton))


def apuntar(cam, pos, objetivo, lente=50):
    cam.location = pos
    cam.rotation_euler = (Vector(objetivo) - Vector(pos)).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = lente


def ver(objs, visibles):
    for o in objs:
        o.hide_render = o not in visibles


def poner_corte(e, cosa, altura_filo, apertura, alto):
    """Cuchillo cortando 'cosa' (lista de dos mitades): el filo a 'altura_filo', mitades separadas 'apertura'."""
    # El cuchillo corta en el plano y = 0 con el mango a la derecha; la mitad de delante cae hacia la cámara
    delante, detras = cosa
    giro = math.radians(28) * min(apertura / 0.03, 1)
    delante.location = (0, -apertura, 0); delante.rotation_euler = (giro, 0, 0)
    detras.location = (0, apertura * 0.5, 0); detras.rotation_euler = (-giro * 0.4, 0, 0)
    k = e["cuchillo"]
    k.location = (0.10, 0, altura_filo)
    k.rotation_euler = (0, math.radians(-5), math.radians(90))
    e["mano_d"].location = k.location
    e["mano_d"].rotation_euler = k.rotation_euler
    # La otra mano sujeta desde detrás, con los dedos encima de la mitad de atrás
    e["mano_i"].location = (0.02, apertura * 0.5 + 0.005, alto - 0.097)
    e["mano_i"].rotation_euler = (0, 0, math.radians(-90))


def renderizar(ruta):
    s = bpy.context.scene
    s.render.filepath = ruta
    bpy.ops.render.render(write_still=True)


def fotogramas(tmp):
    e = escena()
    todo = [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name not in ("Encimera", "Fondo", "Tabla")]
    rutas = []
    cam = e["cam"]
    # 0-7 tomate
    filo = [0.13, 0.10, 0.075, 0.05, 0.022, 0.022, 0.06, 0.12]
    abre = [0, 0, 0, 0, 0.004, 0.015, 0.03, 0.045]
    for i in range(8):
        ver(todo, e["tomate"] + [e["cuchillo"], e["mano_d"], e["mano_i"]])
        poner_corte(e, e["tomate"], filo[i], abre[i], 0.1)
        apuntar(cam, (0.14 - i * 0.01, -0.52, 0.30), (0, 0, 0.06), 48 + i * 2)
        rutas.append(os.path.join(tmp, f"f{i:02d}.png")); renderizar(rutas[-1])
    # 8-11 zapato
    filo = [0.15, 0.09, 0.03, 0.022]
    abre = [0, 0, 0.002, 0.03]
    for j in range(4):
        ver(todo, e["zapato"] + [e["cuchillo"], e["mano_d"]])
        poner_corte(e, e["zapato"], filo[j], abre[j], 0.11)
        apuntar(cam, (0.16, -0.62, 0.36), (0, 0, 0.06), 44)
        rutas.append(os.path.join(tmp, f"f{8 + j:02d}.png")); renderizar(rutas[-1])
    # 12-15 producto: cuatro cuchillos en abanico sobre la tabla y el tomate abierto
    abanico = [e["cuchillo"]]
    for n in range(3):
        k = e["cuchillo"].copy(); k.data = e["cuchillo"].data.copy(); bpy.context.scene.collection.objects.link(k)
        abanico.append(k)
    for n, k in enumerate(abanico):
        k.location = (0.02 * n - 0.01, -0.08 + 0.02 * n, 0.029 + n * 0.017)
        k.rotation_euler = (0, math.radians(90), math.radians(-60 + n * 22))
        k.scale = (1, 1 - n * 0.12, 1)
    # Las dos mitades del tomate con el corte hacia arriba, detrás a la izquierda
    e["tomate"][0].rotation_euler = (math.radians(90), 0, 0); e["tomate"][0].location = (-0.15, 0.108, 0.068)
    e["tomate"][1].rotation_euler = (math.radians(-90), 0, 0); e["tomate"][1].location = (-0.07, 0.042, 0.068)
    for j in range(4):
        ver(todo, abanico + e["tomate"])
        apuntar(cam, (0.0, -0.42 + j * 0.02, 0.32 - j * 0.01), (-0.01, 0.0, 0.02), 42 + j * 3)
        rutas.append(os.path.join(tmp, f"f{12 + j:02d}.png")); renderizar(rutas[-1])
    return rutas


# ---------------------------------------------------------------- rótulos y tele vieja

def fuente(tam):
    for f in FUENTES:
        if os.path.exists(f):
            return ImageFont.truetype(f, tam)
    return ImageFont.load_default()


def texto_borde(d, xy, txt, f, relleno, borde, ancho=2, anchor="la"):
    for dx in range(-ancho, ancho + 1):
        for dy in range(-ancho, ancho + 1):
            if dx or dy:
                d.text((xy[0] + dx, xy[1] + dy), txt, font=f, fill=borde, anchor=anchor)
    d.text(xy, txt, font=f, fill=relleno, anchor=anchor)


def rotular(img, i):
    d = ImageDraw.Draw(img)
    w, h = img.size
    # Logotipo de la teletienda arriba a la izquierda
    d.rectangle((10, 10, 120, 32), fill=(190, 20, 30))
    d.text((16, 13), "TELE-COMPRA", font=fuente(15), fill=(255, 240, 200))
    # Rótulo 2x1 arriba a la derecha (parpadea en el plano del producto)
    if i < 12:
        d.ellipse((w - 92, 6, w - 8, 62), fill=(250, 210, 20), outline=(180, 20, 20), width=3)
        texto_borde(d, (w - 50, 34), "2x1", fuente(30), (200, 20, 20), (255, 255, 255), 1, "mm")
    else:
        color = (255, 230, 30) if i % 2 == 0 else (255, 255, 255)
        texto_borde(d, (w // 2, 70), "¡2x1!", fuente(96), color, (170, 10, 10), 4, "mm")
        d.rectangle((0, h - 74, w, h - 24), fill=(20, 30, 140))
        texto_borde(d, (w // 2, h - 49), "LLAME YA", fuente(36), (255, 255, 255), (0, 0, 0), 2, "mm")
    # Faldón con el reclamo en los cortes
    if i < 12:
        d.rectangle((0, h - 52, w, h - 16), fill=(20, 30, 140))
        txt = "¡CORTA HASTA UN ZAPATO!" if 8 <= i < 12 else "CUCHILLOS PROFESIONALES"
        texto_borde(d, (w // 2, h - 34), txt, fuente(24), (255, 255, 255), (0, 0, 0), 1, "mm")
    return img


def tele_vieja(img, rng):
    img = img.resize((FW, FH), Image.LANCZOS)
    img = ImageEnhance.Color(img).enhance(1.35)
    img = ImageEnhance.Contrast(img).enhance(1.1)
    a = np.asarray(img).astype(np.float32) / 255
    # Sangrado del color: el croma se corre y se emborrona en horizontal
    y = a @ np.array((0.299, 0.587, 0.114), np.float32)
    croma = a - y[..., None]
    k = np.ones(5, np.float32) / 5
    croma = np.apply_along_axis(lambda f: np.convolve(f, k, "same"), 1, croma)
    croma = np.roll(croma, 2, axis=1)
    a = y[..., None] + croma
    a = np.asarray(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6)),
                   np.float32) / 255
    # Líneas de barrido, negros levantados y ruido
    a[1::2] *= 0.88
    a = 0.05 + a * 0.92
    a += rng.normal(0, 0.018, a.shape[:2])[..., None]
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def main():
    rng = np.random.default_rng(7)
    with tempfile.TemporaryDirectory() as tmp:
        rutas = fotogramas(tmp)
        atlas = Image.new("RGB", (FW * 4, FH * 4))
        for i, r in enumerate(rutas):
            img = rotular(Image.open(r).convert("RGB"), i)
            atlas.paste(tele_vieja(img, rng), ((i % 4) * FW, (i // 4) * FH))
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    atlas.save(SALIDA, quality=90)
    print("Guardado", SALIDA)


if __name__ == "__main__":
    main()
