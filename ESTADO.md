# Estado de Ominous

**Fase actual:** 0, montar el entorno (sin cerrar).

## Hecho
- Unity 6000.6.8f1 en Steam Deck (Unity Hub en Flatpak), con módulo de build Linux.
- Proyecto `Omnious` con URP activo (`PC_RPAsset`) e Input System.
- Git local en la rama `main`.
- Conexión de Claude con el Editor. Prueba superada: crear un objeto, pulsar Play, detenerlo y borrarlo.

## Falta para cerrar la fase 0
- Decidir si se cambia a Unity 6.3 LTS (la hoja de ruta pide LTS; 6000.6.8f1 no lo es).
- Decidir si el proyecto y la carpeta se renombran de `Omnious` a `Ominous`.
- Instalar Git LFS y configurarlo.
- Crear el repositorio privado en GitHub (lo crea Toni) y subir el proyecto.
- Prueba de Toni: ver a Claude crear un objeto y pulsar Play. Con su visto bueno, etiqueta `fase-0-ok`.

## Conexión con Unity
La hoja de ruta menciona MCP for Unity, pero la vía real es Unity CLI con el paquete `com.unity.pipeline`:
- Usar `~/.local/bin/unity-editor` desde la raíz del proyecto, no `unity`, porque Unity Hub va en Flatpak.
- Respaldo: el MCP oficial de `com.unity.ai.assistant`, con `~/.local/bin/unity-mcp-flatpak`.

## Problemas conocidos
- `unity status` no detecta el Editor. Para comprobar la conexión, usar `unity-editor command`.
- Justo después de una recarga de scripts, un comando puede fallar una vez. Basta con reintentar.

## Última decisión de Toni
Usar la conexión más eficiente con Unity e inicializar git en el proyecto.
