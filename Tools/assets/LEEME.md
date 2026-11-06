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

Cada script dice en su cabecera qué genera, sus medidas y dónde está el origen. Algunos:
`bano.py` (Vater, Lavabo, Banera), `lampara_techo.py` (cuelga del techo: origen arriba), `aparador.py`,
`puertas.py` (PuertaHoja con el origen en la bisagra y PuertaMarco en el centro del hueco), `llaves.py`,
`tele_programa.py` (atlas de 16 fotogramas de la tele; necesita Pillow) y `superficies.py`
(texturas de 1 m x 1 m para paredes, suelos y techo en `Assets/_Ominous/Art/Superficies/`).

## Convenciones
- FBX en `Assets/_Ominous/Art/Models/`, texturas en `Assets/_Ominous/Art/Models/Texturas/` (con LFS).
- Escala real (1 unidad = 1 m), Y arriba, escala 1 y rotación 0 al importar en Unity.
- Origen en el suelo, en el centro de la base. El frente mira a +Z en Unity, igual que en `HouseBuilder`.
- En Blender se modela con Z arriba y el frente a -Y; la x de Unity es la x de Blender cambiada de signo.
- UV a escala real: una textura cubre 1 m x 1 m.
- Estilo: realista y con poco detalle, colores apagados (cámara doméstica de principios de los 2000).

## Estilo (referencia: Fears to Fathom)
Objetos realistas, usados y sucios. `hornear.py` lo hace en dos pasos:
1. `material_sucio(...)`: color base (o textura CC0) con suciedad en rincones (oclusión), polvo de abajo,
   manchas, cantos gastados y mugre fotográfica (`Suciedad_*` de `Assets/_Ominous/Art/CC0`).
2. `atlas(objeto, nombre)`: UV automáticas y horneado de todo a una textura JPG por objeto
   (`poco_detalle` da menos resolución a lo que apenas se ve).

Texturas fotográficas CC0 (ambientCG) en `Assets/_Ominous/Art/CC0/<Categoria>_<ID>/`, fuentes en `LICENCIAS.md`.
Antes de usarlas en la nube: `git lfs pull --include="Assets/_Ominous/Art/CC0/<carpeta>/*"` (solo las que hagan falta:
la cuota de LFS del plan gratuito es 1 GB al mes). Atlas en JPG por la misma razón.

`coche_2000.py` es un experimento (coche redondeado por subdivisión); no se usa en el juego.
