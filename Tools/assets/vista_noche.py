"""Render de noche con niebla, para comparar un asset con el ambiente del juego.

Uso:  python Tools/assets/vista_noche.py modelo.fbx salida.png
Calle oscura, una farola cálida y niebla verdosa. Después aplica una gradación parecida a la
de VideoPost (negros levantados, tinte oliva, poca saturación y grano fino).
"""
import math
import os
import sys

import bpy
import numpy as np
from mathutils import Vector

fbx, salida = sys.argv[1], sys.argv[2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=os.path.abspath(fbx))
tex = os.path.join(os.path.dirname(os.path.abspath(fbx)), "Texturas")
for img in bpy.data.images:
    ruta = os.path.join(tex, os.path.basename(img.filepath))
    if os.path.exists(ruta):
        img.filepath = ruta

s = bpy.context.scene
s.render.engine = "CYCLES"
s.cycles.samples = 64
s.cycles.use_denoising = True
s.render.resolution_x, s.render.resolution_y = 1280, 868
s.view_settings.view_transform = "Standard"
mundo = bpy.data.worlds.new("Noche"); s.world = mundo
mundo.use_nodes = True
mundo.node_tree.nodes["Background"].inputs[0].default_value = (0.004, 0.006, 0.002, 1)
mundo.node_tree.nodes["Background"].inputs[1].default_value = 1.0


def plano(nombre, tam, loc, color, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_plane_add(size=tam, location=loc, rotation=rot)
    o = bpy.context.object
    m = bpy.data.materials.new(nombre); m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*color, 1)
    m.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.9
    o.data.materials.append(m)
    return o


plano("Asfalto", 60, (0, 0, 0), (0.035, 0.032, 0.028))
plano("Acera", 1, (-4.5, 0, 0.12), (0.18, 0.17, 0.15)).scale = (2.5, 60, 1)
plano("Valla", 1, (-6, 0, 1.0), (0.06, 0.045, 0.03), (0, math.radians(90), 0)).scale = (2, 60, 1)

# Niebla: volumen en toda la escena
bpy.ops.mesh.primitive_cube_add(size=60, location=(0, 0, 10))
caja = bpy.context.object
v = bpy.data.materials.new("Niebla"); v.use_nodes = True
n = v.node_tree.nodes
n.remove(n["Principled BSDF"])
vol = n.new("ShaderNodeVolumePrincipled")
vol.inputs["Color"].default_value = (0.45, 0.5, 0.28, 1)
vol.inputs["Density"].default_value = 0.012
v.node_tree.links.new(vol.outputs[0], n["Material Output"].inputs["Volume"])
caja.data.materials.append(v)

# Farola cálida a un lado y por detrás de la cámara
luz = bpy.data.lights.new("Farola", "SPOT"); luz.energy = 4000; luz.color = (1.0, 0.72, 0.38)
luz.spot_size = math.radians(80); luz.spot_blend = 0.6; luz.shadow_soft_size = 0.3
lo = bpy.data.objects.new("Farola", luz); lo.location = (-5.0, -6.5, 5.5); s.collection.objects.link(lo)
lo.rotation_euler = (Vector((0, -1.5, 0)) - lo.location).to_track_quat("-Z", "Y").to_euler()

cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam")); s.collection.objects.link(cam); s.camera = cam
cam.data.lens = 30
cam.location = (-2.2, -4.8, 1.55)
cam.rotation_euler = (Vector((0.3, -0.6, 0.7)) - cam.location).to_track_quat("-Z", "Y").to_euler()

tmp = salida + ".crudo.png"
s.render.filepath = tmp
bpy.ops.render.render(write_still=True)

# Gradación parecida a VideoPost
img = bpy.data.images.load(tmp)
w, h = img.size
a = np.array(img.pixels[:]).reshape(h, w, 4)[..., :3]
a = np.clip((a - 0.35) * 1.05 + 0.35, 0, 1)
luma = (a * np.array((0.299, 0.587, 0.114))).sum(-1, keepdims=True)
a = luma + (a - luma) * 0.75
t = np.clip((luma - 0.08) / 0.64, 0, 1); t = t * t * (3 - 2 * t)
a *= np.array((1.0, 1.04, 0.72)) * (1 - t) + np.array((1.06, 0.98, 0.70)) * t
a = 0.035 + a * (0.93 - 0.035)
rng = np.random.default_rng(3)
a += (rng.random((h, w, 1)) - 0.5) * 0.06 * (1.5 - 0.75 * luma)
out = bpy.data.images.new("Noche", w, h, alpha=False)
rgba = np.ones((h, w, 4), dtype=np.float32); rgba[..., :3] = np.clip(a, 0, 1)
out.pixels.foreach_set(rgba.ravel())
out.filepath_raw = salida; out.file_format = "PNG"; out.save()
os.remove(tmp)
print("ok")
