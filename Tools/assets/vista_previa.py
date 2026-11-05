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
s.view_settings.view_transform = "AgX"
mundo = bpy.data.worlds.new("Mundo"); s.world = mundo
mundo.use_nodes = True
mundo.node_tree.nodes["Background"].inputs[1].default_value = 0.35

bpy.ops.mesh.primitive_plane_add(size=6)
suelo = bpy.context.object
m = bpy.data.materials.new("Suelo"); m.use_nodes = True
m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.35, 0.33, 0.3, 1)
suelo.data.materials.append(m)
bpy.ops.mesh.primitive_plane_add(size=6, location=(0, 0.6, 3), rotation=(math.radians(90), 0, 0))
pared = bpy.context.object
mp = bpy.data.materials.new("Pared"); mp.use_nodes = True
mp.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.7, 0.68, 0.62, 1)
pared.data.materials.append(mp)

luz = bpy.data.lights.new("Plafon", "AREA"); luz.energy = 120; luz.size = 0.6
lo = bpy.data.objects.new("Plafon", luz); lo.location = (0.4, -1.0, 2.5); s.collection.objects.link(lo)
cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam")); s.collection.objects.link(cam); s.camera = cam
cam.data.lens = 28
objetivo = Vector((0, 0, 0.55))
vistas = {"frente": (0, -1.6, 1.6), "tres_cuartos": (1.0, -1.3, 1.6), "lado": (-1.5, -0.4, 1.3), "arriba": (0.2, -0.7, 1.6)}
for nombre, pos in vistas.items():
    cam.location = pos
    o = Vector((-0.2, 0, 0.85)) if nombre == "arriba" else objetivo
    cam.rotation_euler = (o - cam.location).to_track_quat("-Z", "Y").to_euler()
    s.render.filepath = os.path.join(salida, nombre + ".png")
    bpy.ops.render.render(write_still=True)
print("ok")
