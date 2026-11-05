# Generadores de assets (fase 10)

Assets definitivos hechos con Python y Blender sin interfaz (`bpy`), en una sesión de Claude Code en la nube.
Los modelos de personas no se generan aquí: los aporta Toni.

## Preparar
```
python3.13 -m venv venv && venv/bin/pip install -r Tools/assets/requirements.txt
```
Si pip se queda parado bajando `bpy` (unos 400 MB), bájalo con `curl` desde files.pythonhosted.org e instala el `.whl`.
En la nube el entorno trae `git lfs` con el smudge desactivado: tras un `checkout`, `git lfs pull` para tener los FBX de verdad.

## Generar
```
venv/bin/python Tools/assets/mueble_recibidor.py
venv/bin/python Tools/assets/coche.py              # CocheRojo, CocheAzul y CocheGris
venv/bin/python Tools/assets/vista_previa.py Assets/_Ominous/Art/Models/MuebleRecibidor.fbx /tmp/vistas
```
`vista_previa.py` encuadra la cámara según el tamaño del objeto.

## Convenciones
- FBX en `Assets/_Ominous/Art/Models/`, texturas en `Assets/_Ominous/Art/Models/Texturas/` (con LFS).
- Escala real (1 unidad = 1 m), Y arriba, escala 1 y rotación 0 al importar en Unity.
- Origen en el suelo, en el centro de la base. El frente mira a +Z en Unity, igual que en `HouseBuilder`.
- En Blender se modela con Z arriba y el frente a -Y; la x de Unity es la x de Blender cambiada de signo.
- UV a escala real: una textura cubre 1 m x 1 m.
- Estilo: realista y con poco detalle, colores apagados (cámara doméstica de principios de los 2000).
