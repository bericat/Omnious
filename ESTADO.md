# Estado de Ominous

**Fase actual:** 1, guion y diseño cerrado.

## Hecho
- Unity 6.3 LTS (6000.3.28f1) en Steam Deck (Unity Hub en Flatpak), con módulo de build Linux.
- Proyecto `Ominous` con URP activo (`PC_RPAsset`) e Input System, con los paquetes actualizados a las versiones mínimas de Unity 6.3.
- Git local en la rama `main`, con Git LFS para modelos, texturas y audio.
- Conexión de Claude con el Editor. Prueba superada: crear un objeto, pulsar Play, detenerlo, leer la consola y borrar el objeto.

## Falta
- Fase 1: Toni tiene que aprobar el guion (`Assets/_Ominous/Dialogue`), el plano, la lista de objetos y la tabla de escalada (`Docs/Diseno`).
- El guion no se ha podido compilar: Yarn Spinner se instala en la fase 3.
- Pendiente de la fase 0, sin bloquear: crear el repositorio privado en GitHub (lo crea Toni) y subir el proyecto. Hasta entonces no hay copia fuera de la microSD.

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
Aprobó el plano, la frase fija y las ideas nuevas. Pidió un acto 2 más sutil, con todo lo de Chechu explicable hasta el acto 3; el jugador intenta arreglar el grifo y rompe la herramienta; sin pensamientos que razonen lo del grifo; sin desmayo ni fundido hasta que el jugador se tire. En la visita 4, Chevas va a casa de Chechu. Aprobó 4 visitas y el antecedente de la pareja. Falta su visto bueno final al guion revisado para cerrar la fase 1.
