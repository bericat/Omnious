"""Utilidades comunes para generar assets de Ominous con Blender sin interfaz (bpy).

Convenciones:
- Escala real: 1 unidad = 1 metro.
- Se modela en Blender con Z arriba y el frente del mueble mirando a -Y.
  Al exportar, el frente queda hacia +Z en Unity (igual que en HouseBuilder).
- El origen de cada objeto está en el suelo, en el centro de su base.
"""
import math
import os

import bpy  # noqa: F401  (antes que bmesh)
import bmesh
import numpy as np

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MODELOS = os.path.join(RAIZ, "Assets", "_Ominous", "Art", "Models")
TEXTURAS = os.path.join(MODELOS, "Texturas")
CC0 = os.path.join(RAIZ, "Assets", "_Ominous", "Art", "CC0")


def cc0(carpeta, mapa="Color", no_color=False):
    """Carga un mapa de una textura CC0 de Assets/_Ominous/Art/CC0/<carpeta>/ (Color, NormalGL, Roughness, AO, Opacity).
    Hace falta `git lfs pull --include="Assets/_Ominous/Art/CC0/<carpeta>/*"` antes."""
    d = os.path.join(CC0, carpeta)
    for f in sorted(os.listdir(d)):
        if f.endswith("_" + mapa + ".jpg") or f.endswith("_" + mapa + ".png"):
            img = bpy.data.images.load(os.path.join(d, f), check_existing=True)
            if no_color:
                img.colorspace_settings.name = "Non-Color"
            return img
    raise FileNotFoundError(f"{carpeta}: no hay mapa {mapa}")


def escena_vacia():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene
    s.unit_settings.system = "METRIC"
    s.unit_settings.scale_length = 1.0


# ---------- texturas ----------

def _ruido(h, w, escala, rng):
    """Ruido de valor suave y periódico (se repite sin costuras)."""
    gy, gx = max(1, h // escala), max(1, w // escala)
    g = rng.random((gy, gx))
    ys = np.arange(h) * gy / h
    xs = np.arange(w) * gx / w
    y0 = np.floor(ys).astype(int); x0 = np.floor(xs).astype(int)
    fy = ys - y0; fx = xs - x0
    fy = fy * fy * (3 - 2 * fy); fx = fx * fx * (3 - 2 * fx)
    y1 = (y0 + 1) % gy; x1 = (x0 + 1) % gx
    a = g[y0][:, x0]; b = g[y0][:, x1]; c = g[y1][:, x0]; d = g[y1][:, x1]
    fx = fx[None, :]; fy = fy[:, None]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


def fbm(h, w, rng, escalas=(64, 32, 16, 8, 4)):
    t = np.zeros((h, w)); peso = 0
    for i, e in enumerate(escalas):
        p = 0.5 ** i
        t += _ruido(h, w, e, rng) * p; peso += p
    return t / peso


def guardar_png(nombre, rgb):
    """Guarda una imagen RGB (0..1, alto x ancho x 3) como PNG y la devuelve cargada en Blender."""
    os.makedirs(TEXTURAS, exist_ok=True)
    h, w, _ = rgb.shape
    img = bpy.data.images.new(nombre, w, h, alpha=False)
    rgba = np.ones((h, w, 4), dtype=np.float32)
    rgba[..., :3] = np.clip(rgb, 0, 1)
    img.pixels.foreach_set(rgba[::-1].ravel())  # Blender guarda las filas de abajo arriba
    ruta = os.path.join(TEXTURAS, nombre + ".png")
    img.filepath_raw = ruta
    img.file_format = "PNG"
    img.save()
    return img


def textura_madera(nombre, color, tam=512, semilla=1, vetas=24.0):
    """Madera barnizada: vetas finas y alargadas a lo largo de U, poco contraste.

    La textura cubre 1 m x 1 m (UV a escala real); vetas = líneas por metro.
    """
    rng = np.random.default_rng(semilla)
    h = w = tam
    # ruido estirado a lo largo de U para que las vetas sean largas y rectas
    largo = np.repeat(fbm(h, w // 8, rng, (32, 16, 8, 4)), 8, axis=1)
    fino = np.repeat(fbm(h, w // 4, rng, (4, 2, 1)), 4, axis=1)
    mancha = fbm(h, w, rng, (128, 64))
    y = np.linspace(0, 1, h, endpoint=False)[:, None]
    anillos = np.sin((y * vetas + largo * 2.2) * 2 * math.pi) * 0.5 + 0.5
    anillos = anillos ** 4
    v = 0.92 - 0.16 * anillos + (fino - 0.5) * 0.10 + (mancha - 0.5) * 0.08
    c = np.array(color)[None, None, :]
    return guardar_png(nombre, c * v[..., None])


def textura_ceramica(nombre, color, tam=256, semilla=2):
    """Vidriado de cerámica: casi liso, con motas y un poco de suciedad."""
    rng = np.random.default_rng(semilla)
    n = fbm(tam, tam, rng, (64, 32, 16))
    motas = (rng.random((tam, tam)) > 0.996) * 0.25
    v = 0.95 + (n - 0.5) * 0.08 - motas
    c = np.array(color)[None, None, :]
    return guardar_png(nombre, c * v[..., None])


def material(nombre, imagen=None, color=(0.8, 0.8, 0.8), rugosidad=0.6, metal=0.0):
    m = bpy.data.materials.new(nombre)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = rugosidad
    bsdf.inputs["Metallic"].default_value = metal
    if imagen is not None:
        tex = m.node_tree.nodes.new("ShaderNodeTexImage")
        tex.image = imagen
        m.node_tree.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    return m


# ---------- geometría ----------

def caja(bm, centro, tam, biselado=0.0, segmentos=1):
    """Añade una caja (centro y tamaño en metros) a un bmesh, con bisel opcional."""
    r = bmesh.ops.create_cube(bm, size=1.0)
    vs = r["verts"]
    bmesh.ops.scale(bm, vec=tam, verts=vs)
    bmesh.ops.translate(bm, vec=centro, verts=vs)
    if biselado > 0:
        aristas = list({e for v in vs for e in v.link_edges})
        bmesh.ops.bevel(bm, geom=aristas, offset=biselado, segments=segmentos,
                        profile=0.5, affect="EDGES", clamp_overlap=True)
    return vs


def torno(bm, perfil, lados=24, desde=(0, 0, 0)):
    """Sólido de revolución alrededor de Z. perfil = [(radio, altura), ...] de abajo arriba."""
    anillos = []
    for r, z in perfil:
        anillo = []
        for i in range(lados):
            a = 2 * math.pi * i / lados
            anillo.append(bm.verts.new((desde[0] + r * math.cos(a), desde[1] + r * math.sin(a), desde[2] + z)))
        anillos.append(anillo)
    for a, b in zip(anillos, anillos[1:]):
        for i in range(lados):
            j = (i + 1) % lados
            bm.faces.new((a[i], a[j], b[j], b[i]))
    # tapa del fondo
    bm.faces.new(list(reversed(anillos[0])))
    return anillos


def objeto(nombre, bm, materiales, suave=False, uv_metros=1.0):
    """Crea el objeto a partir del bmesh. UV por proyección de caja a escala real (1 UV = uv_metros)."""
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    uv = bm.loops.layers.uv.verify()
    for f in bm.faces:
        n = f.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        for l in f.loops:
            p = l.vert.co
            if ax == 0:
                u, v = p.y, p.z
            elif ax == 1:
                u, v = p.x, p.z
            else:
                u, v = p.x, p.y
            l[uv].uv = (u / uv_metros, v / uv_metros)
    me = bpy.data.meshes.new(nombre)
    bm.to_mesh(me)
    bm.free()
    for m in materiales:
        me.materials.append(m)
    if suave:
        for p in me.polygons:
            p.use_smooth = True
    ob = bpy.data.objects.new(nombre, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def asignar(bm, caras, indice):
    for f in caras:
        f.material_index = indice


def exportar_fbx(nombre, objetos):
    """Exporta a Assets/_Ominous/Art/Models/<nombre>.fbx con ejes de Unity (Y arriba, escala 1)."""
    os.makedirs(MODELOS, exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    for o in objetos:
        o.select_set(True)
    ruta = os.path.join(MODELOS, nombre + ".fbx")
    bpy.ops.export_scene.fbx(
        filepath=ruta,
        use_selection=True,
        object_types={"MESH", "EMPTY"},
        apply_unit_scale=True,
        apply_scale_options="FBX_SCALE_ALL",
        axis_forward="-Z",
        axis_up="Y",
        bake_space_transform=True,
        mesh_smooth_type="FACE",
        use_mesh_modifiers=True,
        add_leaf_bones=False,
        path_mode="STRIP",
        embed_textures=False,
    )
    return ruta
