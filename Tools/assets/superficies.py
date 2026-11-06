"""Texturas de superficie que se repiten sin costuras, todas viejas y sucias:
  PapelDamasco     papel pintado de damasco (salón)
  Moqueta          moqueta gastada (salón)
  Gotele           techo de gotelé amarilleado por el humo (toda la casa)
  PapelPasillo     papel de rayas ocre con florecillas (pasillo y recibidor)
  PapelDormitorio  papel de ramitos sobre rosa polvo (dormitorio)
  SueloCocina      baldosa de barro de 25 x 25 cm con juntas sucias (cocina)
  AzulejoCocina    azulejo crema de 20 x 20 cm con alguno decorado y grasa (paredes de la cocina)
  Hormigon         hormigón del garaje con manchas de aceite y grietas

Cada textura cubre 1 m x 1 m (las mallas de HouseBuilder llevan UV en metros: tiling 1).
Salida: Assets/_Ominous/Art/Superficies/<Nombre>.jpg

Uso:  python Tools/assets/superficies.py [Nombre ...]
CC0: Moqueta_Carpet016 (pelo de la moqueta), Garaje_Concrete034 (poro del hormigón).
"""
import math
import os
import sys

import bpy
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import comun as c  # noqa: E402

SALIDA = os.path.join(c.RAIZ, "Assets", "_Ominous", "Art", "Superficies")
T = 1024


def guardar_jpg(nombre, rgb):
    """rgb en sRGB 0..1 (alto x ancho x 3)."""
    os.makedirs(SALIDA, exist_ok=True)
    h, w, _ = rgb.shape
    img = bpy.data.images.new(nombre, w, h, alpha=False)
    img.colorspace_settings.name = "Non-Color"  # los valores ya son sRGB: que no los convierta
    rgba = np.ones((h, w, 4), dtype=np.float32)
    rgba[..., :3] = np.clip(rgb, 0, 1)
    img.pixels.foreach_set(rgba[::-1].ravel())
    ruta = os.path.join(SALIDA, nombre + ".jpg")
    img.filepath_raw = ruta
    img.file_format = "JPEG"
    bpy.context.scene.render.image_settings.quality = 90
    img.save()
    print("Guardado", ruta)


def ruido(rng, escalas):
    return c.fbm(T, T, rng, escalas)


def motivo_damasco(n):
    """Un motivo de damasco simétrico en un cuadro n x n (1 = dibujo, 0 = fondo)."""
    yy, xx = np.mgrid[0:n, 0:n].astype(float)
    u = np.abs((xx + 0.5) / n * 2 - 1)          # 0..1, simétrico
    v = (yy + 0.5) / n * 2 - 1                  # -1 arriba .. 1 abajo
    m = np.zeros((n, n), bool)
    # Flor central: pétalos alrededor de un centro un poco alto
    cy = -0.15
    r = np.hypot(u, (v - cy) * 0.9)
    a = np.arctan2(v - cy, u)
    m |= r < 0.20 * (0.75 + 0.25 * np.cos(6 * a))
    m &= ~(r < 0.06)
    m |= r < 0.03
    # Hojas en voluta a los lados
    for (ox, oy, s, giro) in ((0.38, 0.05, 0.22, 0.6), (0.30, -0.45, 0.16, -0.8), (0.22, 0.42, 0.14, 1.0)):
        du, dv = u - ox, v - oy
        ca, sa = math.cos(giro), math.sin(giro)
        p, q = du * ca - dv * sa, du * sa + dv * ca
        hoja = (p / s) ** 2 + (q / (s * 0.45)) ** 2 < 1
        vena = np.abs(q - 0.25 * s * np.sin(p / s * 3)) < s * 0.06
        m |= hoja & ~vena
    # Tallo y remate en punta arriba y abajo
    m |= (u < 0.025) & (v > 0.05) & (v < 0.75)
    m |= (u < 0.12 * (1 - np.abs(v + 0.62) / 0.18)) & (np.abs(v + 0.62) < 0.18)
    m |= (u < 0.10 * (1 - np.abs(v - 0.80) / 0.12)) & (np.abs(v - 0.80) < 0.12)
    # Marco en óvalo apuntado alrededor de todo
    borde = (u / 0.92) ** 1.6 + np.abs(v / 0.98) ** 1.6
    m |= (borde > 0.93) & (borde < 1.0)
    return m.astype(float)


def papel_damasco():
    rng = np.random.default_rng(11)
    n = T // 4  # cuatro motivos por metro en horizontal (25 cm)
    mot = motivo_damasco(n)
    # Repetición con medio salto: columnas alternas desplazadas medio motivo
    tile = np.zeros((T, T))
    for i in range(T // n):
        for j in range(T // n):
            tile[j * n:(j + 1) * n, i * n:(i + 1) * n] = mot
    salto = np.roll(tile, n // 2, axis=0)
    cols = (np.arange(T) // n) % 2 == 1
    tile[:, cols] = salto[:, cols]
    # Suavizado leve del borde del dibujo (impresión)
    blando = (tile + np.roll(tile, 1, 0) + np.roll(tile, -1, 0) + np.roll(tile, 1, 1) + np.roll(tile, -1, 1)) / 5
    fondo = np.array((0.29, 0.26, 0.21))
    dibujo = np.array((0.37, 0.34, 0.27))
    img = fondo + (dibujo - fondo) * blando[..., None]
    # Grano del papel y variación de tono
    img *= (0.94 + ruido(rng, (4, 2, 1))[..., None] * 0.12)
    img *= (0.88 + ruido(rng, (256, 128, 64))[..., None] * 0.24)
    # Juntas entre tiras de papel (cada 0,5 m) algo levantadas y más oscuras
    x = np.arange(T)
    tira = T // 2
    junta = np.exp(-((x % tira) - 0.0) ** 2 / 6.0) + np.exp(-((x % tira) - tira) ** 2 / 6.0)
    img *= 1 - 0.25 * junta[None, :, None]
    # Manchas de humedad y amarilleo
    hum = ruido(rng, (512, 256, 128, 64, 32))
    mancha = np.clip((hum - 0.58) / 0.12, 0, 1)
    img = img * (1 - 0.22 * mancha[..., None]) + mancha[..., None] * np.array((0.10, 0.07, 0.02)) * 0.22
    amar = ruido(rng, (512, 256))
    img *= np.stack([1 + 0.03 * amar, 1 + 0.01 * amar, 1 - 0.04 * amar], axis=-1)
    guardar_jpg("PapelDamasco", img)


def moqueta():
    rng = np.random.default_rng(23)
    img = c.cc0("Moqueta_Carpet016")
    w, h = img.size
    px = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(px)
    px = px.reshape(h, w, 4)[::-1, :, :3]
    lum = px @ np.array((0.2126, 0.7152, 0.0722), dtype=np.float32)
    # Escalar a T x T (1 m): el CC0 se repite 2 x 2 para que el pelo salga fino
    iy = (np.arange(T) * 2 * h // T) % h
    ix = (np.arange(T) * 2 * w // T) % w
    lum = lum[np.ix_(iy, ix)]
    pelo = lum / max(lum.mean(), 1e-3)
    pelo = 1 + (pelo - 1) * 2.2
    base = np.array((0.24, 0.22, 0.17))
    img = base * np.clip(pelo, 0.2, 2.0)[..., None]
    # Dibujo muy discreto de rombos pequeños (moqueta de los 80)
    yy, xx = np.mgrid[0:T, 0:T]
    p = T // 16
    rombo = (np.abs((xx % p) - p / 2) + np.abs((yy % p) - p / 2)) < p * 0.18
    img *= np.where(rombo, 0.88, 1.0)[..., None]
    # Pisado (más claro y aplastado), manchas oscuras y suciedad general
    pis = ruido(rng, (512, 256, 128))
    img *= (0.85 + 0.3 * pis)[..., None]
    man = ruido(rng, (256, 128, 64, 32, 16))
    m = np.clip((man - 0.66) / 0.08, 0, 1)
    img = img * (1 - 0.2 * m[..., None])
    img *= (0.95 + ruido(rng, (8, 4, 2))[..., None] * 0.1)
    guardar_jpg("Moqueta", img)


def manchas_periodicas(rng, n, sigma, peso=None):
    """Suma de manchas gaussianas en sitios al azar, repetida sin costuras (convolución por FFT)."""
    imp = np.zeros((T, T))
    ys, xs = rng.integers(0, T, n), rng.integers(0, T, n)
    np.add.at(imp, (ys, xs), 1.0 if peso is None else peso)
    f = np.fft.fftfreq(T)
    g = np.exp(-2 * (np.pi * sigma) ** 2 * (f[:, None] ** 2 + f[None, :] ** 2))
    return np.real(np.fft.ifft2(np.fft.fft2(imp) * g))


def relieve(h, fuerza):
    """Sombreado de un mapa de alturas con luz de arriba a la izquierda (sin costuras)."""
    d = (np.roll(h, 1, 1) - np.roll(h, -1, 1)) + (np.roll(h, 1, 0) - np.roll(h, -1, 0))
    return 1 + fuerza * d


def envejecer_papel(img, rng, humedad=0.22):
    """Grano, juntas de tira cada 0,5 m, manchas de humedad y amarilleo (como el damasco)."""
    img = img * (0.94 + ruido(rng, (4, 2, 1))[..., None] * 0.12)
    img *= (0.88 + ruido(rng, (256, 128, 64))[..., None] * 0.24)
    x = np.arange(T)
    tira = T // 2
    junta = np.exp(-((x % tira) - 0.0) ** 2 / 6.0) + np.exp(-((x % tira) - tira) ** 2 / 6.0)
    img *= 1 - 0.25 * junta[None, :, None]
    hum = ruido(rng, (512, 256, 128, 64, 32))
    mancha = np.clip((hum - 0.58) / 0.12, 0, 1)
    img = img * (1 - humedad * mancha[..., None]) + mancha[..., None] * np.array((0.10, 0.07, 0.02)) * humedad
    amar = ruido(rng, (512, 256))
    # Suciedad que baja desde arriba (la tira se ve más oscura hacia el techo) y roce abajo
    y = np.linspace(0, 1, T)[:, None, None]
    img *= 1 - 0.06 * np.exp(-y / 0.08)
    return img * np.stack([1 + 0.03 * amar, 1 + 0.01 * amar, 1 - 0.04 * amar], axis=-1)


def gotele():
    rng = np.random.default_rng(31)
    # Gotas de pintura de 2 a 8 mm (1 px = 1 mm), aplastadas por arriba
    h = manchas_periodicas(rng, 9000, 2.2) * 2.6 + manchas_periodicas(rng, 2500, 4.0) * 6.0
    h += ruido(rng, (16, 8, 4)) * 0.4
    h = np.tanh(h * 1.4)
    luz = relieve(h, 1.6)
    base = np.array((0.42, 0.39, 0.33))
    img = base * np.clip(luz, 0.55, 1.35)[..., None]
    img *= (0.90 + 0.10 * h)[..., None]  # las crestas cogen menos polvo
    # Humo de tabaco y de cocina: amarilleo y nubes más oscuras
    humo = ruido(rng, (512, 256, 128, 64))
    img *= (0.80 + 0.28 * humo)[..., None]
    img *= np.stack([1 + 0.02 * humo, 1 - 0.01 * humo, 1 - 0.07 * humo], axis=-1)
    # Cerco de una gotera antigua
    hum = ruido(rng, (512, 256, 128, 32))
    anillo = np.exp(-((hum - 0.62) / 0.02) ** 2)
    dentro = np.clip((hum - 0.62) / 0.05, 0, 1)
    img *= (1 - 0.12 * anillo - 0.05 * dentro)[..., None]
    img += (anillo * 0.015)[..., None] * np.array((0.6, 0.4, 0.1))
    guardar_jpg("Gotele", img)


def papel_pasillo():
    rng = np.random.default_rng(41)
    yy, xx = np.mgrid[0:T, 0:T].astype(float)
    # Rayas verticales: banda ancha de 8 cm y dos filetes, repetición de 12,5 cm (8 por metro)
    p = T / 8
    u = xx % p
    fondo = np.array((0.36, 0.29, 0.18))
    banda = np.array((0.30, 0.23, 0.13))
    filete = np.array((0.22, 0.15, 0.08))
    img = np.broadcast_to(fondo, (T, T, 3)).copy()
    en_banda = (u > p * 0.18) & (u < p * 0.82)
    img[en_banda] = banda
    for c0 in (p * 0.10, p * 0.90):
        img[np.abs(u - c0) < 1.6] = filete
    # Florecilla de cuatro pétalos en el centro de la banda cada 6,25 cm, alternando altura
    q = T / 16
    cy = (yy + (np.floor(xx / p) % 2) * q / 2) % q - q / 2
    cx = u - p / 2
    r = np.hypot(cx, cy)
    a = np.arctan2(cy, cx)
    flor = r < 9 * (0.55 + 0.45 * np.abs(np.cos(2 * a)))
    img[flor & ~(r < 2.5)] = np.array((0.42, 0.35, 0.22))
    img[r < 2.5] = filete
    blando = (img + np.roll(img, 1, 0) + np.roll(img, -1, 0) + np.roll(img, 1, 1) + np.roll(img, -1, 1)) / 5
    guardar_jpg("PapelPasillo", envejecer_papel(blando, rng, 0.26))


def papel_dormitorio():
    rng = np.random.default_rng(43)
    yy, xx = np.mgrid[0:T, 0:T].astype(float)
    fondo = np.array((0.38, 0.31, 0.28))
    flor_c = np.array((0.31, 0.20, 0.19))
    hoja_c = np.array((0.26, 0.27, 0.20))
    img = np.broadcast_to(fondo, (T, T, 3)).copy()
    # Ramito: tres florecillas y dos hojas, en red de 12,5 cm con medio salto
    p = T / 8
    col = np.floor(xx / p)
    v = (yy + (col % 2) * p / 2) % p - p / 2
    u = xx % p - p / 2
    hojas = np.zeros((T, T), bool)
    for ox, oy, giro in ((-10, 14, 0.7), (11, 15, -0.7)):
        du, dv = u - ox, v - oy
        ca, sa = math.cos(giro), math.sin(giro)
        pp, qq = du * ca - dv * sa, du * sa + dv * ca
        hojas |= (pp / 11) ** 2 + (qq / 4.5) ** 2 < 1
    tallo = (np.abs(u - 0.15 * v) < 1.2) & (v > 0) & (v < 26)
    img[hojas | tallo] = hoja_c
    for ox, oy, rr in ((0, -8, 8.0), (-11, 0, 6.0), (10, -1, 6.5)):
        du, dv = u - ox, v - oy
        r = np.hypot(du, dv)
        a = np.arctan2(dv, du)
        petalo = r < rr * (0.6 + 0.4 * np.abs(np.cos(2.5 * a)))
        img[petalo] = flor_c
        img[r < rr * 0.25] = np.array((0.40, 0.33, 0.20))
    # Lunares diminutos entre ramitos
    lun = (np.hypot((xx + p / 2) % p - p / 2, (yy + p / 4) % (p / 2) - p / 4) < 1.8)
    img[lun & ~(hojas | tallo)] = flor_c * 1.05
    blando = (img + np.roll(img, 1, 0) + np.roll(img, -1, 0) + np.roll(img, 1, 1) + np.roll(img, -1, 1)) / 5
    guardar_jpg("PapelDormitorio", envejecer_papel(blando, rng, 0.2))


def juntas(n, ancho):
    """Máscara de juntas de una cuadrícula de n x n piezas por metro (1 en la junta)."""
    p = T / n
    yy, xx = np.mgrid[0:T, 0:T].astype(float)
    dx = np.minimum(xx % p, p - xx % p)
    dy = np.minimum(yy % p, p - yy % p)
    d = np.minimum(dx, dy)
    return np.clip(1 - (d - ancho / 2) / 1.5, 0, 1), np.floor(xx / p).astype(int), np.floor(yy / p).astype(int), d


def suelo_cocina():
    rng = np.random.default_rng(51)
    n = 4
    junta, ix, iy, d = juntas(n, 4.0)
    # Barro cocido: cada baldosa con su tono, moteada
    tonos = np.array((0.40, 0.27, 0.17)) * (1 + rng.normal(0, 0.07, (n, n, 1))) * (1 + rng.normal(0, 0.03, (n, n, 3)))
    img = tonos[iy % n, ix % n]
    mot = ruido(rng, (24, 12, 6, 3))
    img = img * (0.88 + 0.24 * mot)[..., None]
    img *= (0.94 + 0.12 * ruido(rng, (2, 1)))[..., None]
    # Cantos de la baldosa algo más oscuros y la junta llena de mugre
    borde = np.exp(-d / 10)
    img *= (1 - 0.15 * borde)[..., None]
    img = img * (1 - junta[..., None]) + junta[..., None] * np.array((0.13, 0.11, 0.08))
    # Paso gastado (más claro y mate en el centro), manchas de grasa y alguna grieta
    pis = ruido(rng, (512, 256, 128))
    img *= (0.88 + 0.22 * pis)[..., None]
    gr = ruido(rng, (128, 64, 32, 16, 8))
    man = np.clip((gr - 0.70) / 0.1, 0, 1)
    img *= (1 - 0.25 * man)[..., None]
    grieta = ruido(rng, (64, 32, 16))
    linea = np.exp(-((grieta - 0.5) / 0.004) ** 2) * (ruido(rng, (256, 128)) > 0.74)
    img *= (1 - 0.35 * linea)[..., None]
    guardar_jpg("SueloCocina", img)


def azulejo_cocina():
    rng = np.random.default_rng(53)
    n = 5
    junta, ix, iy, d = juntas(n, 3.0)
    p = T / n
    crema = np.array((0.52, 0.48, 0.38))
    tonos = crema * (1 + rng.normal(0, 0.025, (n, n, 1)))
    img = tonos[iy % n, ix % n]
    # Algunos azulejos decorados con una flor marrón (en diagonal)
    yy, xx = np.mgrid[0:T, 0:T].astype(float)
    u = xx % p - p / 2
    v = yy % p - p / 2
    r = np.hypot(u, v)
    a = np.arctan2(v, u)
    deco = ((ix + 2 * iy) % 5 == 0)
    petalos = r < p * 0.32 * (0.55 + 0.45 * np.abs(np.cos(4 * a)))
    corazon = r < p * 0.08
    esquinas = (np.minimum(np.abs(np.abs(u) - p / 2), np.abs(np.abs(v) - p / 2)) < p * 0.04) & (r > p * 0.45)
    marron = np.array((0.38, 0.27, 0.15))
    img[deco & petalos & ~corazon] = marron
    img[deco & corazon] = np.array((0.46, 0.38, 0.20))
    img[deco & esquinas] = marron
    img = (img + np.roll(img, 1, 0) + np.roll(img, -1, 0) + np.roll(img, 1, 1) + np.roll(img, -1, 1)) / 5
    # Vidriado: brillo que cambia en cada pieza, bisel junto a la junta
    brillo = ruido(rng, (64, 32))
    img *= (0.95 + 0.1 * brillo)[..., None]
    img *= (1 - 0.18 * np.exp(-d / 4))[..., None]
    img = img * (1 - junta[..., None]) + junta[..., None] * np.array((0.20, 0.18, 0.14))
    # Grasa y salpicaduras más fuertes abajo (zona de la encimera y los fogones)
    y = np.linspace(0, 1, T)[:, None]
    grasa = ruido(rng, (256, 128, 64, 32)) * (0.4 + 0.6 * y)
    img *= (1 - 0.35 * np.clip((grasa - 0.3) / 0.4, 0, 1))[..., None]
    img *= np.stack([np.ones_like(grasa), 1 - 0.04 * grasa, 1 - 0.12 * grasa], axis=-1)
    gotas = manchas_periodicas(rng, 400, 1.5)
    img *= (1 - 0.6 * np.clip(gotas * 4, 0, 1) * y)[..., None]
    guardar_jpg("AzulejoCocina", img)


def hormigon():
    rng = np.random.default_rng(61)
    img = c.cc0("Garaje_Concrete034")
    w, h = img.size
    px = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(px)
    px = px.reshape(h, w, 4)[::-1, :, :3]
    lum = px @ np.array((0.2126, 0.7152, 0.0722), dtype=np.float32)
    # Sin deformar: el CC0 (1024 x 512) se repite las veces que haga falta para llenar 1 m x 1 m
    rep = max(1, round(w / h))
    iy = (np.arange(T) * rep * h // T) % h
    ix = (np.arange(T) * w // T) % w
    lum = lum[np.ix_(iy, ix)]
    poro = lum / max(lum.mean(), 1e-3)
    poro = 1 + (poro - 1) * 1.5
    base = np.array((0.36, 0.34, 0.30))
    img = base * np.clip(poro, 0.3, 1.8)[..., None]
    img *= (0.80 + 0.35 * ruido(rng, (512, 256, 128, 64)))[..., None]
    # Manchas de aceite (oscuras, con cerco) y polvo claro
    ac = ruido(rng, (256, 128, 64, 32))
    aceite = np.clip((ac - 0.66) / 0.08, 0, 1)
    img = img * (1 - 0.55 * aceite[..., None]) + aceite[..., None] * np.array((0.02, 0.02, 0.015))
    polvo = np.clip((ruido(rng, (512, 128, 32)) - 0.5) / 0.3, 0, 1)
    img = img * (1 - 0.15 * polvo[..., None]) + polvo[..., None] * np.array((0.45, 0.42, 0.36)) * 0.15
    # Grietas finas
    g = ruido(rng, (256, 128, 64, 32))
    linea = np.exp(-((g - 0.5) / 0.0025) ** 2) * (ruido(rng, (512, 256)) > 0.68)
    img *= (1 - 0.35 * linea)[..., None]
    guardar_jpg("Hormigon", img)


TEXTURAS = {"PapelDamasco": papel_damasco, "Moqueta": moqueta, "Gotele": gotele, "PapelPasillo": papel_pasillo,
            "PapelDormitorio": papel_dormitorio, "SueloCocina": suelo_cocina, "AzulejoCocina": azulejo_cocina,
            "Hormigon": hormigon}


if __name__ == "__main__":
    for n in (sys.argv[1:] or list(TEXTURAS)):
        TEXTURAS[n]()
