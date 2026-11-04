# Estado de Ominous

**Fase actual:** 4, la casa completa y el exterior.

## Hecho
- Unity 6.3 LTS (6000.3.28f1) en Steam Deck (Unity Hub en Flatpak), con módulo de build Linux.
- Proyecto `Ominous` con URP activo (`PC_RPAsset`) e Input System, con los paquetes actualizados a las versiones mínimas de Unity 6.3.
- Git local en la rama `main`, con Git LFS para modelos, texturas y audio.
- Conexión de Claude con el Editor. Prueba superada: crear un objeto, pulsar Play, detenerlo, leer la consola y borrar el objeto.

## Dirección visual (decisión de Toni, sustituye a lo que dice la hoja de ruta sobre PSX)
Imagen de cámara doméstica de principios de los 2000, en la línea de Fears to Fathom: realismo cotidiano, imagen imperfecta, colores apagados y luz natural. Nada de pixel art, temblor de vértices, tramado ni líneas VHS.

- `Materials/Video/VideoPost.shader`: lente, separación RGB, suavizado, ruido, viñeta, exposición variable y color. Ajustes en `Data/VideoLook.asset`, o en vivo con F1.
- `Materials/Video/VideoLit.shader`: luz por píxel, sombras suaves y brillo discreto. `VideoGlass.shader`: cristales.
- Resolución interna de 600 px de alto con filtrado lineal. Bloom de URP en `Data/VideoVolume.asset`.
- Sombras en tiempo real en la tele y en la luz de la farola que entra por la ventana. Lámparas sin sombra.
- Cámara: seguimiento suave, balanceo, ligera inclinación y pulso de mano en `FirstPersonController`.
- Pendiente para más adelante: profundidad de campo y desenfoque de movimiento (coste y comodidad, decidir al jugar); fluorescentes, faros y luz de día (fases con esas escenas); luz horneada (fase 4); texturas realistas (fase 10, o CC0 si Toni lo autoriza).

## Falta
- Fase 4: casa completa, exterior, luz horneada y sonido ambiente.
- Sin confirmar por Toni: los 60 fps mientras anda.
- Sin bloquear: crear el repositorio privado en GitHub (lo crea Toni) y subir el proyecto.

## Fase 3: cómo está montada
- Yarn Spinner 3.2.8 por git. Proyecto `Assets/_Ominous/Dialogue/Ominous.yarnproject`; todo el guion compila.
- Regenerar escenas: `Tools/Ominous/Construir escena de sistemas y menú`. Ese comando sobrescribe `Test_Salon`, `Test_Sistemas` y `MainMenu`.
- Yarn no admite `#line` y `#shadow` en la misma línea: las frases repetidas llevan solo `#shadow`.
- Comandos del guion que aún no hacen nada: lista en `DialogueManager` (se implementan en las fases 5 a 8).
- Si el Editor está en Play no se puede construir ni importar paquetes.

## Escenas de prueba
- `Assets/_Ominous/Scenes/Test_Salon.unity` y `Test_Sistemas.unity`: se regeneran con el comando de arriba.
- `-fpslog 20` mide y escribe en `~/.config/unity3d/Toni/Ominous/Player.log`; solo funciona en escenas con el panel F1, no en el menú.
- Medido en la Deck (1280×800, OpenGL, jugador quieto, 20 s): 60,0 fps, peor fotograma 18,1 ms.

## Conexión con Unity
La hoja de ruta menciona MCP for Unity, pero la vía real es Unity CLI con el paquete `com.unity.pipeline`:
- Usar `~/.local/bin/unity-editor` desde la raíz del proyecto, no `unity`, porque Unity Hub va en Flatpak.
- Unity Hub debe abrir el proyecto: la licencia no permite crearlo ni abrirlo por línea de comandos.
- No hay MCP en este proyecto: `com.unity.ai.assistant` no está instalado y `unity-mcp` se quitó de Claude Code. El script `~/.local/bin/unity-mcp-flatpak` sigue disponible.

## Problemas conocidos
- `unity status` no detecta el Editor. Para comprobar la conexión, usar `unity-editor command`.
- Justo después de una recarga de scripts, un comando puede fallar una vez. Basta con reintentar.

## Última decisión de Toni
Pidió pasar a la fase 4 (fase 3 dada por buena).
