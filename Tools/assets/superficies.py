"""Texturas de superficie en estilo PSX, que se repiten sin costuras, todas viejas y sucias.

Cada textura cubre 4 m x 4 m con 256 px por metro (1024 x 1024): así las manchas grandes no se repiten
a la vista. En Unity, con las UV en metros de HouseBuilder: tiling 0,25 y filtro Point.
Interior:
  PapelDamasco     papel pintado de damasco (salón)
  Moqueta          moqueta gastada (salón)
  Gotele           techo de gotelé amarilleado por el humo (toda la casa)
  PapelPasillo     papel de rayas ocre con florecillas (pasillo y recibidor)
  PapelDormitorio  papel de ramitos sobre rosa polvo (dormitorio)
  SueloCocina      baldosa de barro de 25 x 25 cm con juntas sucias (cocina)
  AzulejoCocina    azulejo crema de 20 x 20 cm con alguno decorado y grasa (paredes de la cocina)
  Hormigon         hormigón del garaje con manchas de aceite y grietas
Exterior:
  FachadaMadera    tablas de madera pintada de la fachada, desconchadas y con chorretones
  FachadaEnfoscado enfoscado pintado de crema con chorretones de agua (alternativa a la madera)
  ZocaloPiedra     zócalo de piedra con mortero
  Teja             teja árabe vieja con musgo (4 m de tejado)

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
METROS = 4
PM = 256                 # píxeles por metro
T = METROS * PM          # 1024


def guardar_jpg(nombre, rgb):
    """rgb en sRGB 0..1 (alto x ancho x 3). La fila 0 es la de arriba de la imagen."""
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


def ruido(rng, metros):
    """Ruido fractal periódico; 'metros' son los tamaños de celda, en metros."""
    return c.fbm(T, T, rng, tuple(max(1, int(round(m * PM))) for m in metros))


def malla():
    yy, xx = np.mgrid[0:T, 0:T].astype(float)
    return yy, xx


def suavizar(img, veces=1):
    for _ in range(veces):
        img = (img + np.roll(img, 1, 0) + np.roll(img, -1, 0) + np.roll(img, 1, 1) + np.roll(img, -1, 1)) / 5
    return img


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


def chorretones(rng, n, largo_m, ancho_px=3.0):
    """Regueros verticales de suciedad (como en las texturas PSX): empiezan fuertes y se apagan hacia abajo."""
    out = np.zeros((T, T))
    yy = np.arange(T)
    for _ in range(n):
        x0 = rng.integers(0, T)
        y0 = rng.integers(0, T)
        largo = rng.uniform(0.3, 1.0) * largo_m * PM
        fuerza = rng.uniform(0.3, 1.0)
        ancho = rng.uniform(0.6, 1.4) * ancho_px
        dy = (yy - y0) % T
        perfil = np.where(dy < largo, (1 - dy / largo) ** 1.5, 0.0) * fuerza
        xs = (x0 + np.arange(-int(ancho * 3), int(ancho * 3) + 1)) % T
        g = np.exp(-((np.arange(-int(ancho * 3), int(ancho * 3) + 1)) / ancho) ** 2)
        out[:, xs] += perfil[:, None] * g[None, :]
    return np.clip(out, 0, 1)


def envejecer(img, rng, mancha=0.18, chorro=0.25, amarilleo=1.0):
    """Suciedad de pared: variación grande y suave (de 0,5 a 4 m), algo de grano, chorretones y amarilleo.
    Sin manchas sueltas con borde: lo que se repite a la vista son las manchas con forma."""
    img = img * (0.95 + ruido(rng, (0.016, 0.008, 0.004))[..., None] * 0.10)
    grande = ruido(rng, (4, 2, 1, 0.5))
    img *= (1 - mancha + 2 * mancha * grande)[..., None]
    if chorro:
        img *= (1 - chorro * chorretones(rng, 60, 1.6))[..., None]
    amar = ruido(rng, (4, 2, 1))
    return img * np.stack([1 + 0.03 * amar * amarilleo, 1 + 0.01 * amar * amarilleo, 1 - 0.05 * amar * amarilleo],
                          axis=-1)


def juntas_tiras(img, ancho_tira_m=0.5):
    x = np.arange(T)
    tira = ancho_tira_m * PM
    d = np.minimum(x % tira, tira - x % tira)
    return img * (1 - 0.22 * np.exp(-d ** 2 / 2.0))[None, :, None]


def repetir_motivo(mot, salto_medio=True):
    """Llena T x T con el motivo n x n; columnas alternas desplazadas medio motivo."""
    n = mot.shape[0]
    tile = np.tile(mot, (T // n, T // n))
    if salto_medio:
        salto = np.roll(tile, n // 2, axis=0)
        cols = (np.arange(T) // n) % 2 == 1
        tile[:, cols] = salto[:, cols]
    return tile


# ---------------------------------------------------------------- interior

def motivo_damasco(n):
    """Un motivo de damasco simétrico en un cuadro n x n (1 = dibujo, 0 = fondo)."""
    yy, xx = np.mgrid[0:n, 0:n].astype(float)
    u = np.abs((xx + 0.5) / n * 2 - 1)
    v = (yy + 0.5) / n * 2 - 1
    m = np.zeros((n, n), bool)
    cy = -0.15
    r = np.hypot(u, (v - cy) * 0.9)
    a = np.arctan2(v - cy, u)
    m |= r < 0.20 * (0.75 + 0.25 * np.cos(6 * a))
    m &= ~(r < 0.06)
    m |= r < 0.03
    for (ox, oy, s, giro) in ((0.38, 0.05, 0.22, 0.6), (0.30, -0.45, 0.16, -0.8), (0.22, 0.42, 0.14, 1.0)):
        du, dv = u - ox, v - oy
        ca, sa = math.cos(giro), math.sin(giro)
        p, q = du * ca - dv * sa, du * sa + dv * ca
        hoja = (p / s) ** 2 + (q / (s * 0.45)) ** 2 < 1
        vena = np.abs(q - 0.25 * s * np.sin(p / s * 3)) < s * 0.06
        m |= hoja & ~vena
    m |= (u < 0.025) & (v > 0.05) & (v < 0.75)
    m |= (u < 0.12 * (1 - np.abs(v + 0.62) / 0.18)) & (np.abs(v + 0.62) < 0.18)
    m |= (u < 0.10 * (1 - np.abs(v - 0.80) / 0.12)) & (np.abs(v - 0.80) < 0.12)
    borde = (u / 0.92) ** 1.6 + np.abs(v / 0.98) ** 1.6
    m |= (borde > 0.93) & (borde < 1.0)
    return m.astype(float)


def papel_damasco():
    rng = np.random.default_rng(11)
    tile = suavizar(repetir_motivo(motivo_damasco(PM // 4)))   # motivo de 25 cm
    fondo = np.array((0.29, 0.26, 0.21))
    dibujo = np.array((0.37, 0.34, 0.27))
    img = fondo + (dibujo - fondo) * tile[..., None]
    img = juntas_tiras(img)
    guardar_jpg("PapelDamasco", envejecer(img, rng, 0.2, 0.22))


def moqueta():
    rng = np.random.default_rng(23)
    img = c.cc0("Moqueta_Carpet016")
    w, h = img.size
    px = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(px)
    px = px.reshape(h, w, 4)[::-1, :, :3]
    lum = px @ np.array((0.2126, 0.7152, 0.0722), dtype=np.float32)
    # El CC0 se repite 2 veces por metro para que el pelo salga fino
    iy = (np.arange(T) * 2 * h // PM) % h
    ix = (np.arange(T) * 2 * w // PM) % w
    pelo = lum[np.ix_(iy, ix)]
    pelo = 1 + (pelo / max(pelo.mean(), 1e-3) - 1) * 2.2
    img = np.array((0.24, 0.22, 0.17)) * np.clip(pelo, 0.2, 2.0)[..., None]
    yy, xx = malla()
    p = PM // 16
    rombo = (np.abs((xx % p) - p / 2) + np.abs((yy % p) - p / 2)) < p * 0.18
    img *= np.where(rombo, 0.88, 1.0)[..., None]
    # Caminos de paso más gastados y suciedad grande y suave
    pis = ruido(rng, (4, 2, 1, 0.5))
    img *= (0.80 + 0.4 * pis)[..., None]
    guardar_jpg("Moqueta", envejecer(img, rng, 0.12, 0.0, 0.5))


def gotele():
    rng = np.random.default_rng(31)
    # Gotas de pintura de 4 a 12 mm (1 px = 4 mm), aplastadas por arriba
    h = manchas_periodicas(rng, 9000, 0.8) * 1.6 + manchas_periodicas(rng, 2500, 1.4) * 3.0
    h = np.tanh(h * 1.2)
    luz = relieve(h, 0.9)
    img = np.array((0.42, 0.39, 0.33)) * np.clip(luz, 0.6, 1.3)[..., None]
    img *= (0.92 + 0.08 * h)[..., None]
    # Humo de tabaco y de cocina: amarilleo y nubes grandes más oscuras
    humo = ruido(rng, (4, 2, 1, 0.5))
    img *= (0.78 + 0.3 * humo)[..., None]
    img *= np.stack([1 + 0.02 * humo, 1 - 0.01 * humo, 1 - 0.08 * humo], axis=-1)
    guardar_jpg("Gotele", envejecer(img, rng, 0.08, 0.0, 0.5))


def papel_pasillo():
    rng = np.random.default_rng(41)
    yy, xx = malla()
    p = PM / 8                                   # repetición de 12,5 cm
    u = xx % p
    fondo = np.array((0.36, 0.29, 0.18))
    banda = np.array((0.30, 0.23, 0.13))
    filete = np.array((0.22, 0.15, 0.08))
    img = np.broadcast_to(fondo, (T, T, 3)).copy()
    img[(u > p * 0.18) & (u < p * 0.82)] = banda
    for c0 in (p * 0.10, p * 0.90):
        img[np.abs(u - c0) < 0.8] = filete
    q = PM / 16
    cy = (yy + (np.floor(xx / p) % 2) * q / 2) % q - q / 2
    cx = u - p / 2
    r = np.hypot(cx, cy)
    a = np.arctan2(cy, cx)
    flor = r < 4.5 * (0.55 + 0.45 * np.abs(np.cos(2 * a)))
    img[flor & ~(r < 1.3)] = np.array((0.42, 0.35, 0.22))
    img[r < 1.3] = filete
    img = juntas_tiras(suavizar(img))
    guardar_jpg("PapelPasillo", envejecer(img, rng, 0.22, 0.3))


def papel_dormitorio():
    rng = np.random.default_rng(43)
    yy, xx = malla()
    fondo = np.array((0.38, 0.31, 0.28))
    flor_c = np.array((0.31, 0.20, 0.19))
    hoja_c = np.array((0.26, 0.27, 0.20))
    img = np.broadcast_to(fondo, (T, T, 3)).copy()
    p = PM / 8
    e = PM / 1024                                # escala del dibujo (se diseñó a 1024 px por metro)
    col = np.floor(xx / p)
    v = ((yy + (col % 2) * p / 2) % p - p / 2) / e
    u = (xx % p - p / 2) / e
    hojas = np.zeros((T, T), bool)
    for ox, oy, giro in ((-10, 14, 0.7), (11, 15, -0.7)):
        du, dv = u - ox, v - oy
        ca, sa = math.cos(giro), math.sin(giro)
        pp, qq = du * ca - dv * sa, du * sa + dv * ca
        hojas |= (pp / 11) ** 2 + (qq / 4.5) ** 2 < 1
    tallo = (np.abs(u - 0.15 * v) < 2.0) & (v > 0) & (v < 26)
    img[hojas | tallo] = hoja_c
    for ox, oy, rr in ((0, -8, 8.0), (-11, 0, 6.0), (10, -1, 6.5)):
        du, dv = u - ox, v - oy
        r = np.hypot(du, dv)
        a = np.arctan2(dv, du)
        img[r < rr * (0.6 + 0.4 * np.abs(np.cos(2.5 * a)))] = flor_c
        img[r < rr * 0.3] = np.array((0.40, 0.33, 0.20))
    img = juntas_tiras(suavizar(img))
    guardar_jpg("PapelDormitorio", envejecer(img, rng, 0.18, 0.2))


def juntas(n_por_metro, ancho_px):
    """Máscara de juntas de una cuadrícula con n piezas por metro (1 en la junta) y el índice de cada pieza."""
    p = PM / n_por_metro
    yy, xx = malla()
    d = np.minimum(np.minimum(xx % p, p - xx % p), np.minimum(yy % p, p - yy % p))
    return (np.clip(1 - (d - ancho_px / 2) / 1.0, 0, 1), np.floor(xx / p).astype(int),
            np.floor(yy / p).astype(int), d)


def suelo_cocina():
    rng = np.random.default_rng(51)
    n = 4                                        # 25 cm
    junta, ix, iy, d = juntas(n, 1.5)
    piezas = n * METROS
    tonos = np.array((0.40, 0.27, 0.17)) * (1 + rng.normal(0, 0.07, (piezas, piezas, 1))) \
        * (1 + rng.normal(0, 0.03, (piezas, piezas, 3)))
    img = tonos[iy, ix]
    img = img * (0.88 + 0.24 * ruido(rng, (0.1, 0.05, 0.02, 0.01)))[..., None]
    img *= (1 - 0.15 * np.exp(-d / 3))[..., None]
    img = img * (1 - junta[..., None]) + junta[..., None] * np.array((0.13, 0.11, 0.08))
    # Paso gastado y grasa, en manchas grandes y suaves
    img *= (0.80 + 0.35 * ruido(rng, (4, 2, 1)))[..., None]
    guardar_jpg("SueloCocina", envejecer(img, rng, 0.12, 0.0, 0.5))


def azulejo_cocina():
    rng = np.random.default_rng(53)
    n = 5                                        # 20 cm
    junta, ix, iy, d = juntas(n, 1.2)
    p = PM / n
    piezas = n * METROS
    tonos = np.array((0.52, 0.48, 0.38)) * (1 + rng.normal(0, 0.025, (piezas, piezas, 1)))
    img = tonos[iy, ix]
    yy, xx = malla()
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
    img = suavizar(img)
    img *= (0.95 + 0.1 * ruido(rng, (0.25, 0.12)))[..., None]
    img *= (1 - 0.18 * np.exp(-d / 1.5))[..., None]
    img = img * (1 - junta[..., None]) + junta[..., None] * np.array((0.20, 0.18, 0.14))
    # Grasa amarillenta en nubes grandes y regueros
    grasa = ruido(rng, (4, 2, 1, 0.5))
    img *= (1 - 0.3 * np.clip((grasa - 0.3) / 0.5, 0, 1))[..., None]
    img *= np.stack([np.ones_like(grasa), 1 - 0.04 * grasa, 1 - 0.12 * grasa], axis=-1)
    guardar_jpg("AzulejoCocina", envejecer(img, rng, 0.08, 0.25, 0.6))


def cc0_lum(carpeta, repeticiones_por_metro=1.0):
    """Luminancia de un CC0, repetida sin deformar para llenar T x T."""
    img = c.cc0(carpeta)
    w, h = img.size
    px = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(px)
    px = px.reshape(h, w, 4)[::-1, :, :3]
    lum = px @ np.array((0.2126, 0.7152, 0.0722), dtype=np.float32)
    ix = (np.arange(T) * repeticiones_por_metro * w // PM).astype(int) % w
    iy = (np.arange(T) * repeticiones_por_metro * w // PM).astype(int) % h
    lum = lum[np.ix_(iy, ix)]
    return lum / max(lum.mean(), 1e-3)


def hormigon():
    rng = np.random.default_rng(61)
    poro = 1 + (cc0_lum("Garaje_Concrete034", 0.5) - 1) * 1.5
    img = np.array((0.36, 0.34, 0.30)) * np.clip(poro, 0.3, 1.8)[..., None]
    img *= (0.75 + 0.4 * ruido(rng, (4, 2, 1, 0.5)))[..., None]
    # Aceite: dos o tres manchas grandes y difusas, no muchas pequeñas
    ac = ruido(rng, (2, 1, 0.5))
    aceite = np.clip((ac - 0.62) / 0.15, 0, 1)
    img = img * (1 - 0.45 * aceite[..., None])
    guardar_jpg("Hormigon", envejecer(img, rng, 0.08, 0.15, 0.3))


# ---------------------------------------------------------------- exterior

def fachada_madera():
    rng = np.random.default_rng(71)
    yy, xx = malla()
    tabla = PM * 0.15                            # tablas horizontales de 15 cm (solapadas)
    k = np.floor(yy / tabla).astype(int)
    f = (yy % tabla) / tabla
    tonos = 1 + rng.normal(0, 0.05, k.max() + 1)
    pintura = np.array((0.42, 0.40, 0.34)) * tonos[k][..., None]
    # Sombra bajo el solape y luz en el canto
    img = pintura * (0.65 + 0.35 * np.clip(f / 0.25, 0, 1))[..., None]
    img *= (1 + 0.08 * (f > 0.9))[..., None]
    # Juntas verticales de las tablas cada 2 m, alternando
    jx = (xx + (k % 2) * PM) % (2 * PM)
    img *= (1 - 0.4 * (jx < 1.5))[..., None]
    # Pintura desconchada: deja ver la madera gris
    veta = ruido(rng, (0.5, 0.02, 0.01))
    madera = np.array((0.24, 0.21, 0.17)) * (0.8 + 0.4 * veta)[..., None]
    pelado = ruido(rng, (1, 0.5, 0.12, 0.05, 0.02)) * (0.6 + 0.4 * (1 - f))
    m = np.clip((pelado - 0.62) / 0.05, 0, 1)
    img = img * (1 - m[..., None]) + madera * m[..., None]
    img *= (1 - 0.35 * chorretones(rng, 80, 1.5, 2.0))[..., None]
    guardar_jpg("FachadaMadera", envejecer(img, rng, 0.2, 0.0, 0.6))


def fachada_enfoscado():
    rng = np.random.default_rng(73)
    h = ruido(rng, (0.03, 0.015, 0.008))
    img = np.array((0.50, 0.45, 0.35)) * np.clip(relieve(h, 2.5), 0.8, 1.2)[..., None]
    img *= (0.9 + 0.2 * ruido(rng, (0.3, 0.1)))[..., None]
    # Parches de enfoscado nuevo más claros y desconchones grises
    parche = np.clip((ruido(rng, (1.5, 0.75, 0.3)) - 0.66) / 0.04, 0, 1)
    img = img * (1 - 0.3 * parche[..., None]) + parche[..., None] * np.array((0.40, 0.39, 0.36)) * 0.3
    img *= (1 - 0.45 * chorretones(rng, 70, 2.0, 4.0))[..., None]
    guardar_jpg("FachadaEnfoscado", envejecer(img, rng, 0.22, 0.0, 0.8))


def zocalo_piedra():
    rng = np.random.default_rng(75)
    yy, xx = malla()
    fila = PM * 0.20
    k = np.floor(yy / fila).astype(int)
    largo = PM * 0.35
    desfase = (k * 0.47 % 1.0) * largo
    j = np.floor((xx + desfase) / largo).astype(int)
    semilla = (k * 131 + j * 17) % 997
    tonos = 0.85 + 0.3 * ((semilla * 0.618) % 1.0)
    du = np.minimum((xx + desfase) % largo, largo - (xx + desfase) % largo)
    dv = np.minimum(yy % fila, fila - yy % fila)
    d = np.minimum(du, dv)
    piedra = np.array((0.36, 0.33, 0.28)) * tonos[..., None]
    piedra *= (0.8 + 0.4 * ruido(rng, (0.1, 0.05, 0.02, 0.01)))[..., None]
    piedra *= (0.75 + 0.25 * np.clip(d / 6, 0, 1))[..., None]
    mortero = np.clip(1 - (d - 1.5) / 1.5, 0, 1)
    img = piedra * (1 - mortero[..., None]) + mortero[..., None] * np.array((0.30, 0.29, 0.26))
    musgo = np.clip((ruido(rng, (1, 0.5, 0.1)) - 0.6) / 0.2, 0, 1)
    img = img * (1 - 0.4 * musgo[..., None]) + musgo[..., None] * np.array((0.16, 0.18, 0.08)) * 0.4
    guardar_jpg("ZocaloPiedra", envejecer(img, rng, 0.2, 0.25, 0.3))


def teja():
    rng = np.random.default_rng(77)
    yy, xx = malla()
    ancho = PM * 0.20
    alto = PM * 0.32
    k = np.floor(yy / alto).astype(int)
    u = ((xx + (k % 2) * ancho / 2) % ancho) / ancho
    v = (yy % alto) / alto
    curva = np.sin(np.pi * u)
    tonos = 1 + rng.normal(0, 0.08, (k.max() + 1, int(T / ancho) + 2))
    jj = np.floor((xx + (k % 2) * ancho / 2) / ancho).astype(int) % (int(T / ancho) + 2)
    base = np.array((0.38, 0.25, 0.17)) * tonos[k, jj][..., None]
    img = base * (0.45 + 0.65 * curva)[..., None]
    img *= (0.55 + 0.45 * np.clip(v / 0.15, 0, 1))[..., None]          # sombra de la teja de arriba
    musgo = np.clip((ruido(rng, (1, 0.5, 0.1)) - 0.55) / 0.2, 0, 1) * (1 - curva * 0.5)
    img = img * (1 - 0.5 * musgo[..., None]) + musgo[..., None] * np.array((0.18, 0.19, 0.09)) * 0.5
    img *= (0.85 + 0.3 * ruido(rng, (0.05, 0.02)))[..., None]
    guardar_jpg("Teja", envejecer(img, rng, 0.2, 0.15, 0.3))


TEXTURAS = {"PapelDamasco": papel_damasco, "Moqueta": moqueta, "Gotele": gotele, "PapelPasillo": papel_pasillo,
            "PapelDormitorio": papel_dormitorio, "SueloCocina": suelo_cocina, "AzulejoCocina": azulejo_cocina,
            "Hormigon": hormigon, "FachadaMadera": fachada_madera, "FachadaEnfoscado": fachada_enfoscado,
            "ZocaloPiedra": zocalo_piedra, "Teja": teja}


if __name__ == "__main__":
    for n in (sys.argv[1:] or list(TEXTURAS)):
        TEXTURAS[n]()
