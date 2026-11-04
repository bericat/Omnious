# Estado de Ominous

**Fase actual:** 3, sistemas básicos.

## Hecho
- Unity 6.3 LTS (6000.3.28f1) en Steam Deck (Unity Hub en Flatpak), con módulo de build Linux.
- Proyecto `Ominous` con URP activo (`PC_RPAsset`) e Input System, con los paquetes actualizados a las versiones mínimas de Unity 6.3.
- Git local en la rama `main`, con Git LFS para modelos, texturas y audio.
- Conexión de Claude con el Editor. Prueba superada: crear un objeto, pulsar Play, detenerlo, leer la consola y borrar el objeto.

## Falta
- Fase 3: prueba de Toni en `Test_Sistemas` (build `Builds/Ominous_Test/Ominous`). Con su visto bueno, etiqueta `fase-3-ok`.
- Falta una fuente pixel con licencia libre: de momento se usa LiberationSans de TextMeshPro. Toni debe autorizar la descarga.
- Sin confirmar por Toni: los 60 fps mientras anda y si el suelo ya no se estira.
- Estilo: se sigue Buckshot Roulette; Toni no pidió lo contrario.
- Sin bloquear: crear el repositorio privado en GitHub (lo crea Toni) y subir el proyecto.

## Fase 3: cómo está montada
- Yarn Spinner 3.2.8 por git. Proyecto `Assets/_Ominous/Dialogue/Ominous.yarnproject`; todo el guion compila.
- Regenerar escenas: `Tools/Ominous/Construir escena de sistemas y menú`. Ese comando sobrescribe `Test_Salon`, `Test_Sistemas` y `MainMenu`.
- Yarn no admite `#line` y `#shadow` en la misma línea: las frases repetidas llevan solo `#shadow`.
- Comandos del guion que aún no hacen nada: lista en `DialogueManager` (se implementan en las fases 5 a 8).
- Si el Editor está en Play no se puede construir ni importar paquetes.

## Fase 2: cómo está montada
- Escena `Assets/_Ominous/Scenes/Test_Salon.unity`, regenerable con `Tools/Ominous/Construir salón de pruebas`.
- Ajustes en `Assets/_Ominous/Data/PSXSettings.asset`, o en vivo con F1.
- Estilo guiado por las referencias de Toni (Buckshot Roulette y Fears to Fathom): 360 px de alto, 12 niveles por canal con tramado Bayer, negros profundos, color apagado y texturas con suciedad.
- Suelos, paredes, techo y alfombra llevan `_Stable`: sin temblor ni deformación afín, porque Toni los veía estirarse al caminar.
- Sin sombras en tiempo real. La calle usa la capa `Exterior`, con luces y ambiente propios.
- Build de prueba en `Builds/Ominous_Test/Ominous`. `-fpslog 20` mide y escribe en `~/.config/unity3d/Toni/Ominous/Player.log`.
- Medido en la Deck (1280×800, OpenGL, jugador quieto, 20 s): 60,0 fps, peor fotograma 18,5 ms.

## Conexión con Unity
La hoja de ruta menciona MCP for Unity, pero la vía real es Unity CLI con el paquete `com.unity.pipeline`:
- Usar `~/.local/bin/unity-editor` desde la raíz del proyecto, no `unity`, porque Unity Hub va en Flatpak.
- Unity Hub debe abrir el proyecto: la licencia no permite crearlo ni abrirlo por línea de comandos.
- No hay MCP en este proyecto: `com.unity.ai.assistant` no está instalado y `unity-mcp` se quitó de Claude Code. El script `~/.local/bin/unity-mcp-flatpak` sigue disponible.

## Problemas conocidos
- Durante la prueba de la fase 0 aparecieron dos errores `GUI Window tried to begin rendering`, de causa desconocida. Vigilar si se repiten.
- `unity status` no detecta el Editor. Para comprobar la conexión, usar `unity-editor command`.
- Justo después de una recarga de scripts, un comando puede fallar una vez. Basta con reintentar.

## Última decisión de Toni
Pidió pasar a la fase 3 (fase 2 dada por buena).
