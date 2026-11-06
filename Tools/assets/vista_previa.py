"""Renders de revisión de un FBX exportado (Cycles, sin interfaz).

Uso:  python Tools/assets/vista_previa.py Assets/_Ominous/Art/Models/MuebleRecibidor.fbx carpeta_salida
Saca cuatro vistas: frente, tres cuartos, lado y desde arriba (a la altura de los ojos, 1,6 m).
"""
import math
import os
import sys

import bpy
from mathutils import Vector

fbx, salida = sys.argv[1], sys.argv[2]
os.makedirs(salida, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=os.path.abspath(fbx))
textura_dir = os.path.join(os.path.dirname(os.path.abspath(fbx)), "Texturas")
for img in bpy.data.images:
    ruta = os.path.join(textura_dir, os.path.basename(img.filepath))
    if os.path.exists(ruta):
        img.filepath = ruta

s = bpy.context.scene
s.render.engine = "CYCLES"
s.cycles.samples = 48
s.cycles.use_denoising = True
s.render.resolution_x, s.render.resolution_y = 960, 720
s.view_settings.view_transform = "Standard"
mundo = bpy.data.worlds.new("Mundo"); s.world = mundo
mundo.use_nodes = True
mundo.node_tree.nodes["Background"].inputs[1].default_value = 0.35
# Tercer argumento "salon": luz cálida y tenue, pared y suelo oscuros, como en las referencias
SALON = len(sys.argv) > 3 and sys.argv[3] == "salon"
if SALON:
    mundo.node_tree.nodes["Background"].inputs[1].default_value = 0.04

mallas = [o for o in s.objects if o.type == "MESH"]
esquinas = [o.matrix_world @ Vector(e) for o in mallas for e in o.bound_box]
lo_ = Vector((min(p.x for p in esquinas), min(p.y for p in esquinas), min(p.z for p in esquinas)))
hi_ = Vector((max(p.x for p in esquinas), max(p.y for p in esquinas), max(p.z for p in esquinas)))
tam = hi_ - lo_
diag = tam.length
lado_suelo = max(6.0, diag * 4)

bpy.ops.mesh.primitive_plane_add(size=lado_suelo)
suelo = bpy.context.object
m = bpy.data.materials.new("Suelo"); m.use_nodes = True
m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.08, 0.07, 0.05, 1) if SALON else (0.35, 0.33, 0.3, 1)
suelo.data.materials.append(m)
bpy.ops.mesh.primitive_plane_add(size=lado_suelo, location=(0, hi_.y + 0.4, lado_suelo / 2), rotation=(math.radians(90), 0, 0))
pared = bpy.context.object
mp = bpy.data.materials.new("Pared"); mp.use_nodes = True
mp.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.10, 0.09, 0.07, 1) if SALON else (0.7, 0.68, 0.62, 1)
pared.data.materials.append(mp)

# Plafón por encima y algo por delante, proporcional al tamaño del objeto
luz = bpy.data.lights.new("Plafon", "AREA"); luz.energy = 120 * max(1.0, diag / 1.2) ** 2; luz.size = 0.6 * max(1.0, diag / 1.2)
if SALON:
    luz.energy *= 0.6; luz.color = (1.0, 0.82, 0.55)
lo = bpy.data.objects.new("Plafon", luz); lo.location = (0.4 * diag / 1.2, lo_.y - 0.8 * diag / 1.2, max(2.5, hi_.z + 1.2)); s.collection.objects.link(lo)
cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam")); s.collection.objects.link(cam); s.camera = cam
cam.data.lens = 28
centro = (lo_ + hi_) / 2
objetivo = Vector((centro.x, centro.y, tam.z * 0.55))
d = max(1.6, diag * 1.15)
# Direcciones horizontales desde el objeto hacia la cámara; ojos a 1,6 m
vistas = {"frente": ((0, -1), 1.6), "tres_cuartos": ((0.62, -0.8), 1.6), "lado": ((-0.95, -0.25), 1.3), "arriba": ((0.2, -0.45), max(1.6, hi_.z + 0.8))}
for nombre, ((dx, dy), z) in vistas.items():
    cam.location = (centro.x + dx * d, centro.y + dy * d, z)
    o = Vector((centro.x, centro.y, hi_.z * 0.9)) if nombre == "arriba" else objetivo
    cam.rotation_euler = (o - cam.location).to_track_quat("-Z", "Y").to_euler()
    s.render.filepath = os.path.join(salida, nombre + ".png")
    bpy.ops.render.render(write_still=True)
print("ok")
