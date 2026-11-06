"""Texturas de superficie que se repiten sin costuras: papel pintado de damasco viejo y moqueta gastada.

Cada textura cubre 1 m x 1 m (las mallas de HouseBuilder llevan UV en metros: tiling 1).
Salida: Assets/_Ominous/Art/Superficies/<Nombre>.jpg

Uso:  python Tools/assets/superficies.py [PapelDamasco|Moqueta]
CC0: Moqueta_Carpet016 (solo su dibujo, para el pelo de la moqueta).
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


if __name__ == "__main__":
    que = sys.argv[1:] or ["PapelDamasco", "Moqueta"]
    if "PapelDamasco" in que:
        papel_damasco()
    if "Moqueta" in que:
        moqueta()
