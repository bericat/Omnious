"""Estilo de los assets (referencia: Fears to Fathom): objetos realistas, usados y sucios.

En vez de colores planos, cada material se describe con nodos de Blender (color base,
suciedad en rincones por oclusión, polvo abajo, manchas, desgaste en cantos) y después
se hornea todo a UNA textura de color por objeto (atlas). Así en Unity basta un material
con una textura, sin nodos ni shaders especiales.

Uso típico en un generador:
    m = hornear.material_sucio("Pintura", (0.5, 0.1, 0.08), rugosidad=0.4, suciedad=0.8)
    ... modelar y asignar materiales ...
    hornear.atlas(objeto, "CocheRojo", tam=2048, sin_hornear={"Coche_Cristal"})
"""
import os

import bpy

import comun as c


def _n(nt, tipo, x, y, **props):
    nodo = nt.nodes.new(tipo)
    nodo.location = (x, y)
    for k, v in props.items():
        setattr(nodo, k, v)
    return nodo


def material_sucio(nombre, color, rugosidad=0.6, metal=0.0, suciedad=0.6, polvo=0.5,
                   manchas=0.3, desgaste=0.0, color_desgaste=(0.5, 0.48, 0.45), color_sucio=(0.16, 0.13, 0.09),
                   imagen=None, escala=1.0, desplazar=(0, 0, 0), escala_manchas=3.0, semilla=0.0, mugre=0.0,
                   mugre_cc0="Suciedad_SurfaceImperfections015", mugre_escala=1.0,
                   veta=0.0, chorretones=0.25, saturacion=0.75, brillo=0.8):
    """Material con el color ya envejecido. Todo es procedural salvo 'imagen' (opcional, se multiplica).

    suciedad: mugre en rincones y huecos (oclusión).  polvo: polvo de abajo hacia arriba (primer medio metro).
    manchas: manchas sueltas.  desgaste: cantos gastados que dejan ver color_desgaste.
    veta: si > 0, la imagen solo aporta su dibujo (en gris, con ese contraste) y el tono lo da 'color':
          así una madera anaranjada sirve para madera gris y gastada.
    chorretones: rayas verticales de mugre.  saturacion, brillo: tono final apagado (estilo del juego).
    """
    m = bpy.data.materials.new(nombre)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = rugosidad
    bsdf.inputs["Metallic"].default_value = metal
    L = nt.links.new

    base = _n(nt, "ShaderNodeRGB", -1400, 300)
    base.outputs[0].default_value = (*color, 1)
    col = base.outputs[0]
    if imagen is not None:
        # Proyección por caja en coordenadas del objeto: 'escala' = metros que cubre la imagen
        tci = _n(nt, "ShaderNodeTexCoord", -1800, 100)
        mpi = _n(nt, "ShaderNodeMapping", -1600, 100)
        esc = escala if isinstance(escala, (tuple, list)) else (escala,) * 3
        mpi.inputs["Scale"].default_value = tuple(1 / e for e in esc)
        mpi.inputs["Location"].default_value = desplazar
        L(tci.outputs["Object"], mpi.inputs["Vector"])
        tex = _n(nt, "ShaderNodeTexImage", -1400, 100, image=imagen, projection="BOX", projection_blend=0.15)
        L(mpi.outputs["Vector"], tex.inputs["Vector"])
        mul = _n(nt, "ShaderNodeMix", -1150, 250, data_type="RGBA", blend_type="MULTIPLY")
        mul.inputs["Factor"].default_value = 1.0
        L(col, mul.inputs[6])
        if veta > 0:
            # Solo el dibujo: gris normalizado a media 1 y con contraste 'veta'
            import numpy as np
            px = np.empty(len(imagen.pixels), dtype=np.float32)
            imagen.pixels.foreach_get(px)
            px = px.reshape(-1, 4)[:, :3]
            media = float((px @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)).mean()) or 0.5
            bw = _n(nt, "ShaderNodeRGBToBW", -1250, 0)
            L(tex.outputs["Color"], bw.inputs[0])
            con = _n(nt, "ShaderNodeMapRange", -1150, 0, clamp=False)
            con.inputs["From Min"].default_value = 0.0
            con.inputs["From Max"].default_value = media
            con.inputs["To Min"].default_value = 1.0 - veta
            con.inputs["To Max"].default_value = 1.0
            L(bw.outputs[0], con.inputs["Value"])
            mx = _n(nt, "ShaderNodeMath", -1050, 0, operation="MAXIMUM")
            mx.inputs[1].default_value = 0.05
            L(con.outputs["Result"], mx.inputs[0])
            L(mx.outputs[0], mul.inputs[7])
        else:
            L(tex.outputs["Color"], mul.inputs[7])
        col = mul.outputs[2]

    # Variación de tono a gran escala (nada es de un color perfecto)
    var = _n(nt, "ShaderNodeTexNoise", -1400, -100)
    var.inputs["Scale"].default_value = 1.5
    var.inputs["Detail"].default_value = 4
    if "W" in var.inputs:
        var.noise_dimensions = "4D"; var.inputs["W"].default_value = semilla
    vmix = _n(nt, "ShaderNodeMix", -900, 250, data_type="RGBA", blend_type="OVERLAY")
    vmix.inputs["Factor"].default_value = 0.18
    L(col, vmix.inputs[6]); L(var.outputs["Fac"], vmix.inputs[7])
    col = vmix.outputs[2]

    # Suciedad en rincones: oclusión ambiental
    ao = _n(nt, "ShaderNodeAmbientOcclusion", -1400, -350)
    ao.samples = 8
    ao.inputs["Distance"].default_value = 0.25
    inv = _n(nt, "ShaderNodeMath", -1150, -350, operation="SUBTRACT")
    inv.inputs[0].default_value = 1.0
    L(ao.outputs["AO"], inv.inputs[1])
    f_ao = _n(nt, "ShaderNodeMath", -950, -350, operation="MULTIPLY", use_clamp=True)
    f_ao.inputs[1].default_value = suciedad * 1.6
    L(inv.outputs[0], f_ao.inputs[0])

    # Polvo de abajo: altura en el mundo, roto con ruido
    geo = _n(nt, "ShaderNodeNewGeometry", -1400, -650)
    sep = _n(nt, "ShaderNodeSeparateXYZ", -1200, -650)
    L(geo.outputs["Position"], sep.inputs[0])
    alt = _n(nt, "ShaderNodeMapRange", -1000, -650)
    alt.inputs["From Min"].default_value = 0.65
    alt.inputs["From Max"].default_value = 0.05
    L(sep.outputs["Z"], alt.inputs["Value"])
    rpol = _n(nt, "ShaderNodeTexNoise", -1200, -850)
    rpol.inputs["Scale"].default_value = 9.0
    rpol.inputs["Detail"].default_value = 8
    pol = _n(nt, "ShaderNodeMath", -800, -650, operation="MULTIPLY", use_clamp=True)
    L(alt.outputs["Result"], pol.inputs[0]); L(rpol.outputs["Fac"], pol.inputs[1])
    f_pol = _n(nt, "ShaderNodeMath", -650, -650, operation="MULTIPLY", use_clamp=True)
    f_pol.inputs[1].default_value = polvo * 1.8
    L(pol.outputs[0], f_pol.inputs[0])

    # Manchas sueltas
    man = _n(nt, "ShaderNodeTexNoise", -1400, -1050)
    man.inputs["Scale"].default_value = escala_manchas
    man.inputs["Detail"].default_value = 10
    man.inputs["Roughness"].default_value = 0.7
    rmp = _n(nt, "ShaderNodeMapRange", -1150, -1050)
    rmp.inputs["From Min"].default_value = 0.55
    rmp.inputs["From Max"].default_value = 0.75
    L(man.outputs["Fac"], rmp.inputs["Value"])
    f_man = _n(nt, "ShaderNodeMath", -950, -1050, operation="MULTIPLY", use_clamp=True)
    f_man.inputs[1].default_value = manchas
    L(rmp.outputs["Result"], f_man.inputs[0])

    if mugre > 0:
        # Mugre fotográfica (CC0) proyectada por caja en coordenadas del objeto
        tc = _n(nt, "ShaderNodeTexCoord", -1700, -1350)
        mp = _n(nt, "ShaderNodeMapping", -1550, -1350)
        mp.inputs["Scale"].default_value = (1 / mugre_escala,) * 3
        L(tc.outputs["Object"], mp.inputs["Vector"])
        tm = _n(nt, "ShaderNodeTexImage", -1350, -1350, image=c.cc0(mugre_cc0, "Opacity", no_color=True),
                projection="BOX", projection_blend=0.3)
        L(mp.outputs["Vector"], tm.inputs["Vector"])
        fm = _n(nt, "ShaderNodeMath", -1100, -1350, operation="MULTIPLY", use_clamp=True)
        fm.inputs[1].default_value = mugre
        L(tm.outputs["Color"], fm.inputs[0])
        mm = _n(nt, "ShaderNodeMath", -800, -1200, operation="MAXIMUM")
        L(f_man.outputs[0], mm.inputs[0]); L(fm.outputs[0], mm.inputs[1])
        f_man = mm

    if chorretones > 0:
        # Chorretones: ruido estirado en vertical
        tcc = _n(nt, "ShaderNodeTexCoord", -1700, -1650)
        mpc = _n(nt, "ShaderNodeMapping", -1550, -1650)
        mpc.inputs["Scale"].default_value = (14.0, 14.0, 0.9)
        L(tcc.outputs["Object"], mpc.inputs["Vector"])
        nc = _n(nt, "ShaderNodeTexNoise", -1350, -1650)
        nc.inputs["Scale"].default_value = 3.0
        nc.inputs["Detail"].default_value = 6
        if "W" in nc.inputs:
            nc.noise_dimensions = "4D"; nc.inputs["W"].default_value = semilla + 7.3
        L(mpc.outputs["Vector"], nc.inputs["Vector"])
        rc = _n(nt, "ShaderNodeMapRange", -1150, -1650)
        rc.inputs["From Min"].default_value = 0.52
        rc.inputs["From Max"].default_value = 0.72
        L(nc.outputs["Fac"], rc.inputs["Value"])
        fc = _n(nt, "ShaderNodeMath", -950, -1650, operation="MULTIPLY", use_clamp=True)
        fc.inputs[1].default_value = chorretones
        L(rc.outputs["Result"], fc.inputs[0])
        mc = _n(nt, "ShaderNodeMath", -700, -1400, operation="MAXIMUM")
        L(f_man.outputs[0], mc.inputs[0]); L(fc.outputs[0], mc.inputs[1])
        f_man = mc

    suma = _n(nt, "ShaderNodeMath", -500, -500, operation="MAXIMUM")
    L(f_ao.outputs[0], suma.inputs[0]); L(f_pol.outputs[0], suma.inputs[1])
    suma2 = _n(nt, "ShaderNodeMath", -350, -500, operation="MAXIMUM", use_clamp=True)
    L(suma.outputs[0], suma2.inputs[0]); L(f_man.outputs[0], suma2.inputs[1])

    if desgaste > 0:
        # Cantos gastados: 'Pointiness' no hornea bien; se usa oclusión invertida en el interior (convexidad)
        ao2 = _n(nt, "ShaderNodeAmbientOcclusion", -1400, 700, inside=True)
        ao2.samples = 8
        ao2.inputs["Distance"].default_value = 0.02
        canto = _n(nt, "ShaderNodeMapRange", -1150, 700)
        canto.inputs["From Min"].default_value = 0.75
        canto.inputs["From Max"].default_value = 0.35
        L(ao2.outputs["AO"], canto.inputs["Value"])
        rd = _n(nt, "ShaderNodeTexNoise", -1150, 900)
        rd.inputs["Scale"].default_value = 30
        rd.inputs["Detail"].default_value = 6
        fd = _n(nt, "ShaderNodeMath", -950, 700, operation="MULTIPLY", use_clamp=True)
        L(canto.outputs["Result"], fd.inputs[0]); L(rd.outputs["Fac"], fd.inputs[1])
        fd2 = _n(nt, "ShaderNodeMath", -800, 700, operation="MULTIPLY", use_clamp=True)
        fd2.inputs[1].default_value = desgaste * 2.5
        L(fd.outputs[0], fd2.inputs[0])
        dmix = _n(nt, "ShaderNodeMix", -600, 400, data_type="RGBA")
        dmix.inputs[7].default_value = (*color_desgaste, 1)
        L(fd2.outputs[0], dmix.inputs["Factor"]); L(col, dmix.inputs[6])
        col = dmix.outputs[2]

    smix = _n(nt, "ShaderNodeMix", -200, 250, data_type="RGBA")
    smix.inputs[7].default_value = (*color_sucio, 1)
    L(suma2.outputs[0], smix.inputs["Factor"]); L(col, smix.inputs[6])
    # Tono final apagado: menos saturación y algo más oscuro
    hsv = _n(nt, "ShaderNodeHueSaturation", 0, 250)
    hsv.inputs["Saturation"].default_value = saturacion
    hsv.inputs["Value"].default_value = brillo
    L(smix.outputs[2], hsv.inputs["Color"])
    L(hsv.outputs["Color"], bsdf.inputs["Base Color"])
    return m


def material_liso(nombre, color, rugosidad=0.5, metal=0.0, alfa=1.0):
    """Material sin envejecer (cristales y similares)."""
    m = c.material(nombre, color=color, rugosidad=rugosidad, metal=metal)
    m.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = alfa
    return m


def atlas(ob, nombre, tam=2048, sin_hornear=(), margen=0.004, poco_detalle=(), factor_poco=0.35):
    """Desenvuelve las UV, hornea el color de todos los materiales a Texturas/<nombre>.png
    y deja el objeto con un solo material <nombre> (más los de 'sin_hornear')."""
    s = bpy.context.scene
    s.render.engine = "CYCLES"
    s.cycles.samples = 24
    s.cycles.device = "CPU"
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob

    # UV nuevas solo para el horneado (las de proyección por caja se descartan)
    me = ob.data
    while me.uv_layers:
        me.uv_layers.remove(me.uv_layers[0])
    me.uv_layers.new(name="UV")
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=margen, area_weight=0.0, scale_to_bounds=True)
    bpy.ops.object.mode_set(mode="OBJECT")
    if poco_detalle:
        # Menos resolución para lo que apenas se ve (interior, bajos): más sitio para lo importante
        import bmesh
        bm = bmesh.new(); bm.from_mesh(me)
        uv = bm.loops.layers.uv.active
        for f in bm.faces:
            mat = me.materials[f.material_index]
            if mat is not None and mat.name in poco_detalle:
                for l in f.loops:
                    l[uv].uv *= factor_poco
        bm.to_mesh(me); bm.free()
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.select_all(action="SELECT")
        bpy.ops.uv.pack_islands(rotate=True, margin=margen, scale=True)
        bpy.ops.object.mode_set(mode="OBJECT")

    # El pase de color difuso de un metal sale negro: se hornea como no metálico
    for mat in me.materials:
        if mat is not None and mat.name not in sin_hornear:
            mat.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = 0.0
    img = bpy.data.images.new(nombre, tam, tam, alpha=False)
    img.generated_color = (0.2, 0.2, 0.2, 1)
    for mat in me.materials:
        if mat is None or mat.name in sin_hornear:
            continue
        nt = mat.node_tree
        t = nt.nodes.new("ShaderNodeTexImage")
        t.image = img
        nt.nodes.active = t
    s.render.bake.use_pass_direct = False
    s.render.bake.use_pass_indirect = False
    s.render.bake.use_pass_color = True
    s.render.bake.margin = 6
    # Los materiales sin hornear también necesitan un nodo de imagen activo (se ignora su resultado)
    tmp = bpy.data.images.new("_descartar", 8, 8)
    for mat in me.materials:
        if mat is not None and mat.name in sin_hornear:
            t = mat.node_tree.nodes.new("ShaderNodeTexImage"); t.image = tmp
            mat.node_tree.nodes.active = t
    bpy.ops.object.bake(type="DIFFUSE", pass_filter={"COLOR"}, use_clear=True)

    os.makedirs(c.TEXTURAS, exist_ok=True)
    # JPG para no gastar la cuota de LFS (1 GB en el plan gratuito)
    ruta = os.path.join(c.TEXTURAS, nombre + ".jpg")
    img.filepath_raw = ruta
    img.file_format = "JPEG"
    bpy.context.scene.render.image_settings.quality = 90
    img.save()

    # Un material con la textura horneada para todo lo horneado
    rug = [mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value
           for mat in me.materials if mat is not None and mat.name not in sin_hornear]
    final = c.material(nombre, img, rugosidad=sum(rug) / max(1, len(rug)))
    nuevos, mapa = [], {}
    for i, mat in enumerate(me.materials):
        clave = mat.name if mat is not None and mat.name in sin_hornear else nombre
        if clave not in mapa:
            mapa[clave] = len(nuevos)
            nuevos.append(mat if clave != nombre else final)
    indices = [mapa[me.materials[p.material_index].name if me.materials[p.material_index].name in sin_hornear else nombre]
               for p in me.polygons]
    me.materials.clear()
    for mat in nuevos:
        me.materials.append(mat)
    for p, i in zip(me.polygons, indices):
        p.material_index = i
    return ruta


# Tonos de madera de las referencias de Toni: gastada, apagada, entre gris y marrón
TONOS_MADERA = {
    "gris": (0.33, 0.25, 0.16),      # madera vieja agrisada (estanterías, mesas)
    "marron": (0.42, 0.26, 0.12),    # nogal claro descolorido (chapa de la tele)
    "oscura": (0.17, 0.11, 0.07),    # mueble oscuro y ennegrecido
}


def madera_vieja(nombre, tono="gris", escala=0.9, veta=1.3, semilla=0.0, **kw):
    """Madera gastada: el dibujo sale de la foto CC0 Wood092 y el tono lo pone TONOS_MADERA."""
    color = TONOS_MADERA.get(tono, tono)
    oscuro = tuple(v * 0.35 for v in color)
    args = dict(rugosidad=0.7, imagen=c.cc0("Mueble_Wood092"), escala=escala, veta=veta, suciedad=1.0,
                polvo=0.35, manchas=0.45, desgaste=0.5, chorretones=0.35, color_desgaste=tuple(min(1, v * 1.5) for v in color),
                color_sucio=oscuro, mugre=1.0, semilla=semilla)
    args.update(kw)
    return material_sucio(nombre, color, **args)


def plastico_viejo(nombre, color=(0.52, 0.48, 0.38), **kw):
    """Plástico beige amarilleado por los años (ordenadores, teles, interruptores)."""
    args = dict(rugosidad=0.5, suciedad=0.9, polvo=0.3, manchas=0.35, mugre=0.6, mugre_escala=0.5,
                color_sucio=(0.20, 0.17, 0.11), desgaste=0.2, color_desgaste=(0.60, 0.56, 0.45))
    args.update(kw)
    return material_sucio(nombre, color, **args)
