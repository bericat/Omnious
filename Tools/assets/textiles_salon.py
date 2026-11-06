"""Alfombra, manta, lámpara de pie y cortina del salón, con el mismo envejecido que el resto.

- Alfombra.fbx: alfombra de dibujo oriental, gastada y con flecos (2,4 x 1,7 m, como la provisional).
- Manta.fbx: manta de lana doblada sobre el cojín izquierdo del sofá (misma posición que la provisional,
  origen en el suelo; asiento del sofá nuevo a 0,46 m).
- Lampara.fbx: lámpara de pie de latón con pantalla de tela (1,66 m). La bombilla es un objeto
  aparte (Bombilla, material Lampara_Bombilla) para la luz de Unity, a 1,47 m.
- Cortina.fbx: un paño con pliegues de 0,30 x 1,50 m y origen ARRIBA en el centro (en la barra):
  se escala en Unity al tamaño de cada ventana.
Frente a +Z en Unity. Uso:  python Tools/assets/textiles_salon.py [Alfombra|Manta|Lampara|Cortina]
Texturas CC0: Tapiceria_Fabric083, Suciedad_SurfaceImperfections015.
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


def dibujo_alfombra():
    """Alfombra oriental genérica: campo granate, medallón central, cenefas azul y crema."""
    w, h = 1024, 726
    yy, xx = np.mgrid[0:h, 0:w]
    u, v = (xx + 0.5) / w * 2 - 1, (yy + 0.5) / h * 2 - 1     # -1..1
    img = np.zeros((h, w, 3)) + (0.36, 0.07, 0.06)            # granate
    borde = np.minimum(np.minimum(xx, w - 1 - xx), np.minimum(yy, h - 1 - yy))
    azul, crema, oro = np.array((0.08, 0.10, 0.20)), np.array((0.70, 0.60, 0.44)), np.array((0.55, 0.38, 0.14))
    img[borde < 90] = azul
    img[(borde >= 28) & (borde < 34)] = crema
    img[(borde >= 84) & (borde < 90)] = crema
    img[(borde >= 96) & (borde < 100)] = oro
    # motivos de la cenefa: rombos repetidos
    t = np.where(np.minimum(xx, w - 1 - xx) < np.minimum(yy, h - 1 - yy), yy, xx)
    rombo = (np.abs(((t % 56) - 28)) + np.abs(borde - 59)) < 18
    img[(borde >= 36) & (borde < 82) & rombo] = (0.45, 0.10, 0.07)
    img[(borde >= 36) & (borde < 82) & rombo & ((np.abs(((t % 56) - 28)) + np.abs(borde - 59)) < 8)] = crema
    # medallón central y esquinas
    med = np.abs(u) * 1.0 + np.abs(v) * 1.4
    img[(med < 0.45) & (borde >= 100)] = azul
    img[(med < 0.38) & (borde >= 100)] = (0.48, 0.12, 0.08)
    img[(med < 0.22) & (borde >= 100)] = crema
    img[(med < 0.12) & (borde >= 100)] = azul
    esq = (np.abs(np.abs(u) - 1) * 1.0 + np.abs(np.abs(v) - 1) * 1.4)
    img[(esq < 0.55) & (borde >= 100)] = (0.10, 0.12, 0.20)
    img[(esq < 0.48) & (borde >= 100)] = (0.40, 0.09, 0.06)
    # flores pequeñas sueltas en el campo
    rng = np.random.default_rng(5)
    for _ in range(140):
        cx, cy = rng.integers(110, w - 110), rng.integers(110, h - 110)
        if abs((cx / w * 2 - 1)) + abs((cy / h * 2 - 1)) * 1.4 < 0.5:
            continue
        r = rng.integers(4, 8)
        col = [crema, oro, azul][rng.integers(0, 3)]
        m = (np.abs(xx - cx) + np.abs(yy - cy)) < r
        img[m] = col
    # trama de lana y desgaste en el centro (zona de paso)
    trama = ((xx // 2 + yy // 3) % 2) * 0.05 + rng.random((h, w)) * 0.08
    gastado = np.clip(1 - (u ** 2 * 0.8 + v ** 2 * 1.5), 0, 1) * 0.25
    img = img * (0.95 + trama[..., None]) * (1 - gastado[..., None]) + gastado[..., None] * np.array((0.45, 0.38, 0.30))
    return c.guardar_png("_Alfombra", img)


def alfombra():
    c.escena_vacia()
    W, D = 2.4, 1.7
    img = dibujo_alfombra()
    img.pack(); os.remove(img.filepath_raw)
    hs = hornear.material_sucio
    mats = [
        hs("Lana", (0.75, 0.75, 0.75), rugosidad=0.95, imagen=img, escala=(-W, D, 1), desplazar=(0.5, 0.5, 0),
           suciedad=0.6, polvo=0.0, manchas=0.6, escala_manchas=5, color_sucio=(0.12, 0.08, 0.05), mugre=0.8),
        hs("Fleco", (0.38, 0.33, 0.24), rugosidad=0.9, suciedad=0.6, manchas=0.5, color_sucio=(0.25, 0.20, 0.14)),
    ]
    bm = bmesh.new()
    # Alfombra con algo de relieve: rejilla con ondulaciones suaves y los bordes un poco levantados
    r = bmesh.ops.create_grid(bm, x_segments=24, y_segments=18, size=0.5)
    rng = np.random.default_rng(3)
    for vv in r["verts"]:
        x, y = vv.co.x * W, vv.co.y * D * 1.0 / 1.0 * (D / D)
        y = vv.co.y * D
        borde = min(W / 2 - abs(x), D / 2 - abs(y))
        z = 0.008 + 0.004 * math.sin(x * 3.1 + 1) * math.sin(y * 2.3) + (0.006 if borde < 0.05 else 0)
        vv.co = Vector((x, y, z))
    # canto
    bordes = [e for e in bm.edges if e.is_boundary]
    ext = bmesh.ops.extrude_edge_only(bm, edges=bordes)
    for vv in [g for g in ext["geom"] if isinstance(g, bmesh.types.BMVert)]:
        vv.co.z = 0.0
    c.asignar(bm, bm.faces, 0)
    # flecos en los lados cortos
    for s in (-1, 1):
        for i in range(34):
            yv = -D / 2 + 0.04 + i * (D - 0.08) / 33
            c.caja_mat(bm, (s * (W / 2 + 0.035), yv, 0.003), (0.07, 0.012, 0.004), 1, 0,
                       rot=Matrix.Rotation(rng.normal() * 0.25, 3, "Z"))
    ob = c.objeto("Alfombra", bm, mats)
    for p in ob.data.polygons:
        p.use_smooth = True
    hornear.atlas(ob, "Alfombra", tam=2048, margen=0.002)
    return c.exportar_fbx("Alfombra", [ob]), ob


def manta():
    c.escena_vacia()
    hs = hornear.material_sucio
    mats = [hs("Lana", (0.30, 0.20, 0.14), rugosidad=0.95, imagen=c.cc0("Tapiceria_Fabric083"), escala=0.5,
               suciedad=0.8, manchas=0.3, color_sucio=(0.14, 0.11, 0.08), mugre=0.4)]
    # Tira de tela doblada: sobre el asiento y cayendo por delante, con arrugas
    bm = bmesh.new()
    nx, ny = 14, 30
    ancho = 0.52
    pts = []
    for j in range(ny + 1):
        t = j / ny
        # recorrido: respaldo (y 0.10 -> asiento -> borde delantero -> cae)
        if t < 0.6:
            y, z = 0.12 - t / 0.6 * 0.50, 0.475
        else:
            a = (t - 0.6) / 0.4
            ang = a * math.pi / 2
            y, z = -0.38 - math.sin(ang) * 0.06, 0.475 - (1 - math.cos(ang)) * 0.06 - a * 0.30
        fila = []
        for i in range(nx + 1):
            x = (i / nx - 0.5) * ancho
            arruga = 0.008 * math.sin(i * 1.7 + j * 0.9) + 0.006 * math.sin(j * 2.3)
            fila.append(bm.verts.new((x, y + (arruga if t >= 0.6 else 0), z + (arruga if t < 0.6 else 0))))
        pts.append(fila)
    for j in range(ny):
        for i in range(nx):
            bm.faces.new((pts[j][i], pts[j][i + 1], pts[j + 1][i + 1], pts[j + 1][i]))
    bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.012)
    c.asignar(bm, bm.faces, 0)
    ob = c.objeto("Manta", bm, mats, suave=True)
    hornear.atlas(ob, "Manta", tam=1024)
    return c.exportar_fbx("Manta", [ob]), ob


def lampara():
    c.escena_vacia()
    hs = hornear.material_sucio
    mats = [
        hs("Laton", (0.36, 0.27, 0.12), rugosidad=0.35, metal=1.0, suciedad=0.5, manchas=0.3, desgaste=0.3,
           color_desgaste=(0.6, 0.48, 0.25), color_sucio=(0.12, 0.10, 0.06), mugre=0.5),
        hs("Pantalla", (0.40, 0.32, 0.20), rugosidad=0.9, imagen=c.cc0("Tapiceria_Fabric083"), escala=0.3,
           suciedad=0.6, manchas=0.5, escala_manchas=8, color_sucio=(0.30, 0.22, 0.12), mugre=0.5),
    ]
    bm = bmesh.new()
    c.marcar(bm)
    c.torno(bm, [(0.14, 0.0), (0.15, 0.01), (0.15, 0.02), (0.12, 0.035), (0.04, 0.05), (0.02, 0.06), (0.001, 0.061)], lados=24)
    vs = c.nuevos(bm)
    c.asignar(bm, {f for v in vs for f in v.link_faces}, 0)
    c.marcar(bm)
    r = bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=0.011, radius2=0.011, depth=1.38)
    bmesh.ops.translate(bm, verts=c.nuevos(bm), vec=(0, 0, 0.06 + 0.69))
    c.asignar(bm, {f for v in c.nuevos(bm) for f in v.link_faces}, 0)
    for z in (0.45, 0.95):
        c.marcar(bm)
        c.torno(bm, [(0.018, z), (0.022, z + 0.01), (0.018, z + 0.02)], lados=12)
        c.asignar(bm, {f for v in c.nuevos(bm) for f in v.link_faces}, 0)
    # Pantalla troncocónica abierta, con grosor
    c.marcar(bm)
    an = []
    for rr, z in [(0.23, 1.34), (0.225, 1.36), (0.13, 1.60), (0.125, 1.61)]:
        an.append([bm.verts.new((rr * math.cos(2 * math.pi * i / 32), rr * math.sin(2 * math.pi * i / 32), z)) for i in range(32)])
    for a, b in zip(an, an[1:]):
        for i in range(32):
            j = (i + 1) % 32
            bm.faces.new((a[i], a[j], b[j], b[i]))
    caras = {f for v in c.nuevos(bm) for f in v.link_faces}
    bmesh.ops.solidify(bm, geom=list(caras), thickness=0.004)
    c.asignar(bm, {f for v in c.nuevos(bm) for f in v.link_faces}, 1)
    ob = c.objeto("Lampara", bm, mats)
    for p in ob.data.polygons:
        p.use_smooth = True
    hornear.atlas(ob, "Lampara", tam=1024)
    # Bombilla aparte
    bb = bmesh.new()
    bmesh.ops.create_uvsphere(bb, u_segments=12, v_segments=8, radius=0.04)
    bmesh.ops.translate(bb, verts=bb.verts[:], vec=(0, 0, 1.47))
    bomb = c.objeto("Bombilla", bb, [hornear.material_liso("Lampara_Bombilla", (0.9, 0.85, 0.7))], suave=True)
    return c.exportar_fbx("Lampara", [ob, bomb]), ob


def cortina():
    c.escena_vacia()
    hs = hornear.material_sucio
    mats = [hs("Tela", (0.24, 0.20, 0.12), rugosidad=0.9, imagen=c.cc0("Tapiceria_Fabric083"), escala=0.4,
               suciedad=0.7, polvo=0.0, manchas=0.4, escala_manchas=6, color_sucio=(0.22, 0.17, 0.10), mugre=0.6)]
    bm = bmesh.new()
    nx, nz = 24, 12
    W, H = 0.30, 1.50
    filas = []
    for j in range(nz + 1):
        z = -H * j / nz
        apertura = 1.0 + 0.15 * (j / nz)  # se abre un poco hacia abajo
        fila = []
        for i in range(nx + 1):
            x = (i / nx - 0.5) * W * apertura
            pliegue = 0.022 * math.sin(i / nx * math.pi * 6) * (0.8 + 0.2 * j / nz)
            fila.append(bm.verts.new((x, pliegue, z)))
        filas.append(fila)
    for j in range(nz):
        for i in range(nx):
            bm.faces.new((filas[j][i], filas[j][i + 1], filas[j + 1][i + 1], filas[j + 1][i]))
    bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.004)
    c.asignar(bm, bm.faces, 0)
    ob = c.objeto("Cortina", bm, mats, suave=True)
    hornear.atlas(ob, "Cortina", tam=1024)
    return c.exportar_fbx("Cortina", [ob]), ob


PIEZAS = {"Alfombra": alfombra, "Manta": manta, "Lampara": lampara, "Cortina": cortina}


def main():
    pedidos = sys.argv[1:] or list(PIEZAS)
    for n in pedidos:
        ruta, ob = PIEZAS[n]()
        print(f"Exportado {ruta} ({sum(len(p.vertices) - 2 for p in ob.data.polygons)} triángulos)")


if __name__ == "__main__":
    main()
