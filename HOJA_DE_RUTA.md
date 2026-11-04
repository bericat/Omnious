# OMINOUS · Hoja de ruta de desarrollo en Unity

Versión 6 · 3 de noviembre de 2026 · Autor del juego: Toni

> **Para Claude:** este documento es tu guía de trabajo. Toni no ha usado Unity nunca y tú haces todo el desarrollo. Trabaja **una fase cada vez**, en orden. Antes de empezar cualquier sesión lee la sección 0 y el archivo `ESTADO.md` del repositorio. No pases a la fase siguiente hasta que Toni haya probado la actual y diga que está bien. Responde siempre en español.

---

## 0. Reglas de trabajo (leer en cada sesión)

### 0.1 Cómo trabajamos

- **Equipo de Toni:** Steam Deck en modo escritorio (SteamOS, Linux). **Unity Hub y el editor ya están instalados.** Toni juega y prueba con **teclado y ratón**.
- **Claude hace todo:** scripts, escenas, modelos, texturas, materiales, configuración y builds. Toni prueba, juzga y decide.
- **Dos etapas:** primero se hace la **primera versión** completa y jugable (fases 0 a 9) con geometría provisional hecha dentro de Unity. Después, en la **fase de pulido (fase 10)**, Claude crea los **assets propios definitivos con Python en la nube** (en una sesión de Claude Code en la nube con el mismo repositorio) y sustituye la geometría provisional. En la Steam Deck no hace falta instalar Blender. No se usan los packs del prototipo. Si hace falta un asset que Claude no puede hacer con calidad, se lo pide a Toni diciendo exactamente qué necesita.
- **Packs de referencia:** Toni tiene packs PSX en la carpeta `OMINOUS` de la microSD (en SteamOS suele estar en `/run/media/deck/<nombre de la tarjeta>/OMINOUS`). No se importan al proyecto salvo que Toni lo pida; sirven para pulir más adelante.
- **Conexión con Unity:** Claude Code corre en la Steam Deck y controla el editor con un servidor MCP para Unity (por ejemplo *MCP for Unity*, `CoplayDev/unity-mcp`), que permite crear objetos, ejecutar menús, leer la consola y pulsar Play. Si el MCP falla, el plan B es que Claude escriba los archivos y *scripts de editor* (`Tools/Ominous/...`) que montan las escenas, y Toni solo pulsa el menú y Play.
- **Las escenas se construyen por código** siempre que se pueda (scripts de editor que colocan props desde datos). Así una escena se puede regenerar, revisar en git y arreglar sin arrastrar objetos a mano.
- **Repositorio git** (GitHub, con Git LFS para modelos, texturas y audio). Al terminar cada tarea: commit con mensaje en español. El historial es la memoria entre sesiones.
- **`ESTADO.md`** en la raíz del repo: fase actual, qué está hecho, qué falta, problemas conocidos y la última decisión de Toni. Claude lo actualiza al final de cada sesión.
- **Toni es exigente con la colocación de objetos.** En la primera versión se acepta geometría provisional (ver 2.4), pero siempre a escala real, bien colocada y reconocible (un sofá tiene que parecer un sofá). Antes de dar una estancia por buena, hacer capturas desde varios ángulos y revisarlas de cerca.

### 0.2 Cómo probar cada fase

1. Claude explica en dos o tres frases qué probar y cómo (qué escena abrir, qué pulsar).
2. Toni juega con teclado y ratón.
3. Toni dice qué falla o qué no le gusta; Claude corrige.
4. Solo con el visto bueno de Toni: commit con la etiqueta `fase-N-ok` y `ESTADO.md` actualizado.

### 0.3 Rendimiento: la Steam Deck es la plataforma objetivo

- Objetivo: **60 fps estables en Steam Deck** (mínimo aceptable: 40 fps fijos). Medir con el Profiler en cada fase a partir de la 1.
- La estética PSX ayuda: resolución interna baja, pocas luces en tiempo real, sombras horneadas.
- Las builds son **Linux x86_64** (Steam Deck nativa). Windows más adelante.
- **Teclado y ratón primero:** WASD, ratón para mirar, E para interactuar, clic para elegir en diálogos, Esc para pausa. El mando se puede añadir al final. Textos legibles a 1280×800.

### 0.4 Lo que no se negocia

- Juego original: Buckshot Roulette y Fears to Fathom son solo referencia de ambiente, sin copiar escenas, interfaz ni personajes.
- Nada sobrenatural confirmado. Todo podría tener explicación, o no.
- Cada línea de diálogo tiene un ID único para el doblaje futuro.

---

## 1. El juego

### 1.1 En una frase

Una noche en casa: Chevas vuelve tarde del trabajo, su mujer Roberta se va a dormir y un vecino nuevo, Chechu, empieza a llamar a la puerta sabiendo cosas que no debería saber, mientras la casa deja de ser la que Chevas conocía.

### 1.2 Ficha

| Campo | Valor |
| --- | --- |
| Título | Ominous |
| Género | Terror psicológico que se vuelve surrealista |
| Jugadores | 1, primera persona |
| Duración | 60–90 minutos, una sola noche, historia lineal |
| Plataforma | Steam Deck / Linux primero; Windows después |
| Estilo | PSX de baja resolución, pixelado moderado (que no canse la vista) |
| Idioma | Español, subtítulos; doblaje en el futuro |

### 1.3 Personajes

| Personaje | Papel | Notas |
| --- | --- | --- |
| **Chevas** | Protagonista, el jugador | Vuelve de trabajar de madrugada, cansado pero sin sueño. Sus pensamientos aparecen como subtítulos en cursiva. |
| **Roberta** | Su mujer | Peso narrativo propio. Al principio es el ancla de normalidad; luego desaparece de la cama y vuelve a aparecer hablando como si nada. |
| **Chechu** | El vecino nuevo | Educado, correcto, demasiado tranquilo. Cada visita sabe más. Las habitaciones ocultas de la casa están ligadas a él. |

En la primera versión los personajes son figuras provisionales de pocos polígonos; los modelos definitivos llegan en la fase de pulido (fase 10) (ver 2.4). Chevas no se ve (primera persona; solo manos si hacen falta).

### 1.4 Historia por actos

**Prólogo: llegar a casa (≈10 min)**
- Chevas aparca y entra por la puerta principal. Por las ventanas se ve la calle: farolas, casas vecinas, una casa de enfrente que acaba de venderse (cartel de «Vendida»).
- Roberta está en el sofá viendo la tele, a punto de dormirse. Conversación con elecciones: hay que convencerla de que apague la tele y se acueste.
- **Siembra del detalle (decidido):** es algo que Chevas **solo piensa**, nunca lo dice en voz alta. Aparece como subtítulo de pensamiento mientras mira a Roberta dormirse. Frase (aprobada): *«Tengo que arreglar el grifo del baño antes de que se entere de que lo rompí yo.»* Nadie más puede saberlo.
- Tareas cotidianas que enseñan los controles: dejar las llaves, cerrar la puerta, apagar luces, beber agua en la cocina.

**Acto 1: el vecino nuevo (≈15 min)**
- Roberta duerme. Chevas, solo y sin sueño, deambula (tele bajita, nevera, mirar por la ventana).
- Hacia las 2:40 llaman a la puerta. Chevas abre y dice una **frase fija** (no es una elección, porque se repetirá en el final). Propuesta: *«¿Sí…? Son casi las tres. ¿Pasa algo?»* Es Chechu, que se presenta como el nuevo vecino de enfrente. Conversación educada y normal (se ha quedado sin luz, pregunta por la basura, cualquier excusa creíble).
- En medio de la charla suelta, sin darle importancia, **lo que Chevas pensó en el prólogo**: *«Por cierto, ese grifo del baño… yo lo arreglaría antes de que ella se entere.»* El juego no lo resalta; el jugador puede pasarlo por alto.
- Chechu se va. Al mirar por la ventana, su casa sigue a oscuras.

**Acto 2: vuelve (≈20 min)**
- Dos o tres visitas más, cada una más explícita: primero detalles de la casa (dónde está el diferencial, qué baldosa del baño cojea), luego de la pareja (su aniversario, una discusión reciente, cosas de la cama).
- Entre visitas, **la casa se modifica** (objetos movidos, cuadros que no estaban) y **Chevas descubre la primera habitación oculta**: una puerta detrás de la estantería del pasillo.
- **Roberta desaparece:** en una de las vueltas al dormitorio la cama está vacía y caliente. Chevas la busca por toda la casa sin encontrarla. Más tarde aparece en la cocina, en pijama, hablando normal («¿qué haces despierto?»), como si no hubiera pasado nada. Si Chevas pregunta, ella no entiende de qué habla.

**Acto 3: la casa deja de tener sentido (≈20 min)**
- Más habitaciones ocultas, cada una más inquietante y más ligada a Chechu (ver 1.5).
- La geometría falla: el pasillo se alarga, una habitación se repite, el reloj marca siempre las 3:33, la vista de la ventana ya no coincide con la calle.
- Roberta vuelve a desaparecer y reaparece en sitios imposibles, siempre tranquila. Una vez repite palabra por palabra algo que dijo Chechu.
- Chechu ya no llama: aparece dentro de la casa.

**Desenlace: el bucle (≈10 min)**
- Al final del pasillo alargado, Chevas abre una puerta que **no da a nada**: al otro lado solo hay vacío, como una puerta abierta en una pared exterior a mucha altura (referencia: `referencias/puerta-al-vacio.png`). Al cruzarla cae al vacío, o se desmaya en el umbral. Fundido a negro.
- **Vuelta al principio:** el juego arranca otra vez como el prólogo. Chevas vuelve de trabajar de noche, la misma calle, la misma casa. Todo parece normal.
- Pero esta vez **la puerta no se abre con sus llaves** y tiene que llamar. Abre **Chechu** y le dice, palabra por palabra, la frase que Chevas le dijo en el acto 1: *«¿Sí…? Son casi las tres. ¿Pasa algo?»* Al fondo se oye la tele y la voz de Roberta.
- Ahora Chevas es el «vecino» y Chechu es Chevas. Corte a negro y créditos. El juego acaba ahí, sin explicación, dejando al jugador confundido.
- **Solo hay un final.** Las habitaciones ocultas y lo que sabía Chechu se pueden releer después como parte del mismo bucle.

### 1.5 Las habitaciones ocultas (todas ligadas a Chechu)

Cada habitación se descubre en un acto concreto y es más turbia que la anterior. **Tabla aprobada por Toni.** Al final del juego, cada habitación se puede releer como parte del bucle.

| # | Acceso | Qué hay | Relación con Chechu |
| --- | --- | --- | --- |
| 1 | Detrás de la estantería del pasillo (acto 2) | Un cuartito estrecho con una silla, una manta y latas vacías | Alguien ha vivido aquí. Una chaqueta como la que llevaba Chechu. |
| 2 | Trampilla en el armario del dormitorio (acto 2–3) | Un hueco entre paredes con agujeros que dan al dormitorio y al baño | Desde aquí se oye y se ve todo. Así sabía lo que Chevas y Roberta hablaban. |
| 3 | Sótano que «no existía» (acto 3) | Una copia exacta del dormitorio de la pareja, pero con fotos de ellos durmiendo | Chechu ha reconstruido su vida. En la mesilla, una libreta con lo que Chevas pensó en el prólogo. |
| 4 | Puerta al final del pasillo alargado (desenlace) | Nada: la puerta da al vacío (ver `referencias/puerta-al-vacio.png`) | Es el paso por el que Chevas acaba convertido en el «vecino» y Chechu ocupa su lugar. |

### 1.6 La casa

- Casa unifamiliar de barrio residencial estadounidense: una planta + sótano (oculto) + desván o hueco de tejado. Porche delantero, puerta con mirilla, garaje.
- Estancias: recibidor, salón, cocina-comedor, pasillo, dormitorio principal, baño, cuarto de la colada, garaje.
- **Ventanas con exterior visible:** desde cada ventana se ve la calle, las casas vecinas (con la de Chechu enfrente), farolas, coches aparcados y árboles, todo modelado por Claude. El exterior es un decorado bajo detalle, con niebla, para que funcione en Steam Deck.
- El exterior cambia con los actos: luces que se encienden en casa de Chechu, una silueta en su ventana y, en el acto 3, una calle que ya no es la misma.

---

## 2. Arquitectura técnica

### 2.1 Versiones y paquetes

| Elemento | Elección |
| --- | --- |
| Motor | Unity 6 LTS más reciente, instalado con Unity Hub en modo escritorio de SteamOS |
| Render | URP (Universal Render Pipeline) |
| Entrada | Input System (teclado y ratón; mando opcional al final) |
| Cámara | Cinemachine |
| Diálogo | Yarn Spinner (diálogos con elecciones y variables; ID por línea) |
| Textos | Localization de Unity (subtítulos ahora, clips de voz por ID después) |
| Cinemáticas | Timeline |
| Texto en pantalla | TextMeshPro con una fuente pixel libre (licencia OFL o CC); mantener el crédito si la licencia lo pide |
| Modelado | Primera versión: ProBuilder y mallas generadas por scripts de editor en Unity. Fase 10 (pulido): assets definitivos generados con Python en la nube |
| Control de MCP | MCP for Unity (o el que funcione en Linux en ese momento) |

### 2.2 Estructura de carpetas

```
Assets/
  _Ominous/
    Art/            modelos, texturas y materiales hechos por Claude
    Audio/          ambiente, efectos, (voces en el futuro)
    Dialogue/       archivos .yarn por acto
    Materials/PSX/  shader y materiales PSX
    Prefabs/        interactuables, personajes, props montados
    Scenes/         Boot, MainMenu, House, Test_*
    Scripts/
      Core/         GameDirector, SaveSystem, NightState
      Player/       movimiento, cámara, interacción
      Interaction/  Interactable, Door, LightSwitch, Examinable, HiddenPassage
      Dialogue/     integración Yarn, subtítulos, pensamientos
      House/        HouseVariant, Window exterior, eventos surrealistas
      UI/           menús, pausa, opciones, avisos
    Editor/         scripts que construyen escenas y comprueban colocación
    Data/           ScriptableObjects: actos, visitas, variantes de la casa
ESTADO.md
HOJA_DE_RUTA.md
```

### 2.3 Sistemas clave

- **NightState / GameDirector:** guarda el acto, la visita, la hora del juego, si Roberta está en la cama y qué habitaciones están abiertas. Todo lo demás pregunta aquí.
- **HouseVariant:** cada estancia tiene variantes (normal, acto 2, acto 3). El director activa la que toca al cambiar de acto. Nada de duplicar escenas.
- **Interactable:** un componente base con aviso en pantalla («Abrir», «Examinar», «Llamar a Roberta») y un evento. Puertas, interruptores, objetos y pasadizos heredan de él.
- **Dialogue + Subtítulos:** Yarn ejecuta el diálogo; cada línea lleva `#line:id`; los subtítulos muestran nombre y texto; los pensamientos de Chevas van en cursiva y gris.
- **Efecto PSX:** render a textura interna de ~360 px de alto (ajustable 240–480), snap de vértices, ligera deformación afín de texturas, tramado Bayer suave, niebla de distancia y filtrado de texturas en punto. Todo en un único panel de ajustes.
- **Guardado:** punto de control al empezar cada visita.

### 2.4 Assets: primera versión y definitivos

**Primera versión (fases 0 a 9): geometría provisional.**
- Muebles, casa y exterior con ProBuilder y mallas sencillas generadas por scripts de editor, a escala real y con la silueta correcta del objeto.
- Colores planos o texturas muy simples generadas por script, ya con el efecto PSX encima para juzgar el ambiente.
- Personajes: figuras de pocos polígonos con proporciones humanas y cabeza diferenciada; sin animación compleja (deslizar, girar, inclinarse).
- Cada objeto provisional es un prefab con nombre definitivo (`Sofa`, `Tele`, `Roberta`...), para que en la fase 10 baste con cambiar el modelo.

**Assets definitivos (fase 10, pulido): hechos con Python en la nube.**
- Claude los genera con scripts en Python en una sesión en la nube (Blender en modo línea de comandos dentro del contenedor, o librerías de Python para mallas), los exporta a FBX con sus texturas y los sube al repositorio con Git LFS. En la Deck basta con hacer `git pull` y Unity los importa.
- Antes de subir cada asset, Claude renderiza capturas de prueba en la nube con el estilo PSX para revisarlo.
- Pocos polígonos: props de 50–500 triángulos, personajes de 500–1500, con esqueleto sencillo y animaciones cortas y algo rígidas, como en la época PSX.
- Texturas pequeñas (32, 64 o 128 px) generadas por script, con una paleta común y filtrado en punto.
- Cada asset nuevo se enseña a Toni con una captura antes de usarlo en muchas escenas.
- Si algo no llega a la calidad necesaria (lo más probable: personajes y animaciones), Claude se lo dice a Toni y propone qué asset buscar o qué pack de la microSD usar.

**Audio (desde la primera versión):** ambiente y efectos sintetizados o de bancos libres (CC0), con la licencia de cada archivo anotada en `Audio/CREDITOS.md`.

---

## 3. Fases

Cada fase tiene: **objetivo**, **tareas** (en orden), **cómo lo prueba Toni** y **terminado cuando**. Duraciones orientativas.

### Fase 0 · Montar el entorno en la Steam Deck (1–2 sesiones)

**Objetivo:** que Claude pueda controlar Unity desde la Steam Deck. Unity Hub y el editor ya están instalados.

Tareas:
1. Comprobar la versión del editor instalado y que tenga el módulo de build Linux.
2. Instalar git, Git LFS y Claude Code en la Steam Deck (en el directorio de usuario, porque el sistema de SteamOS es de solo lectura; usar distrobox si hace falta). Guiar a Toni con instrucciones cortas, una cada vez.
3. Crear el repositorio **privado** en GitHub (Toni lo crea, Claude lo configura) y el proyecto Unity con URP.
4. Instalar el MCP para Unity y comprobar que Claude puede crear un objeto, leer la consola y pulsar Play.
5. Crear `ESTADO.md` y hacer el primer commit.

**Cómo lo prueba Toni:** ve a Claude crear un objeto en una escena vacía y darle a Play.
**Terminado cuando:** Unity abre el proyecto, el MCP responde y el repo tiene el primer commit. Si algo no funciona bien en SteamOS, parar y proponer alternativas (por ejemplo, distrobox con Ubuntu).

### Fase 1 · Guion y diseño cerrado (1–2 semanas)

**Objetivo:** tener la historia completa escrita antes de construir.

Tareas:
1. Escribir el guion completo en archivos `.yarn` (prólogo, cada visita de Chechu, cada aparición de Roberta, pensamientos de Chevas) con IDs de línea.
2. Cerrar con Toni el número exacto de visitas. (Ya decidido: el pensamiento del grifo, la tabla 1.5 y el final en bucle.)
3. Dibujar el plano de la casa (imagen o diagrama) con estancias, ventanas, accesos ocultos y la calle.
4. Lista de objetos por estancia y por acto (muebles, props, casas exteriores, coches, personajes): sirve para la geometría provisional y, después, para la fase 10.
5. Tabla de escalada: por cada visita, qué sabe Chechu, qué cambia en la casa y dónde está Roberta.

**Cómo lo prueba Toni:** lee el guion y el plano.
**Terminado cuando:** Toni aprueba el guion y el plano.

### Fase 2 · Estilo PSX y primera estancia (2 semanas)

**Objetivo:** fijar el aspecto del juego en una habitación.

Tareas:
1. Shader y post-proceso PSX con panel de ajustes (resolución interna, snap, tramado, niebla, paleta).
2. Preparar la geometría provisional (2.4): paleta de colores, texturas simples por script y escala en metros reales.
3. Hacer los muebles provisionales del salón (sofá, tele, mesa, estantería, alfombra, lámpara, ventanas) y construir el salón con un script de editor.
4. Ventana con exterior de prueba: un trozo de calle con farola, árbol y casa de enfrente.
5. Iluminación de noche: tele como fuente principal, luz de farola por la ventana.
6. Medir rendimiento en la Steam Deck.

**Cómo lo prueba Toni:** pasea por el salón con teclado y ratón y mira por la ventana.
**Terminado cuando:** a Toni le gusta el aspecto, el pixelado no cansa y va a 60 fps en la Deck.

### Fase 3 · Sistemas básicos (3–4 semanas)

**Objetivo:** todas las piezas que usa el juego, probadas en una escena de pruebas.

Tareas:
1. Movimiento en primera persona (andar, agacharse, mirar) con teclado y ratón.
2. Interacción: puertas, interruptores, cajones, examinar objetos, aviso en pantalla.
3. Diálogos con Yarn: subtítulos, elecciones con el ratón, pensamientos en cursiva.
4. GameDirector, NightState y HouseVariant con una variante de prueba.
5. Guardado por puntos de control.
6. Menú principal (logo OMINOUS), pausa y opciones (subtítulos, tamaño de texto, brillo, sensibilidad, intensidad del efecto PSX).

**Cómo lo prueba Toni:** en la escena de pruebas abre puertas, habla con un personaje de prueba, elige respuestas, guarda y carga.
**Terminado cuando:** todo funciona con teclado y ratón sin errores en consola.

### Fase 4 · La casa completa y el exterior (3–4 semanas)

**Objetivo:** la casa entera en su versión «normal».

Tareas:
1. Hacer los muebles y props provisionales que faltan y construir todas las estancias del plano con scripts de editor.
2. Exterior visible desde todas las ventanas: calle, casas vecinas, casa de Chechu enfrente, farolas, coches, árboles, niebla.
3. Iluminación horneada y luces de cada estancia con interruptor.
4. Sonido ambiente: zumbido de nevera, reloj, coches lejanos, viento.
5. Revisión de colocación: capturas de cada estancia desde varios ángulos, revisadas una a una.

**Cómo lo prueba Toni:** recorre la casa entera y mira por todas las ventanas.
**Terminado cuando:** Toni da por buena cada estancia y el rendimiento se mantiene.

### Fase 5 · Vertical slice: prólogo y acto 1 (3–4 semanas)

**Objetivo:** los primeros ~25 minutos terminados, con calidad final. **Es la fase más importante:** si esto no da miedo, se corrige aquí antes de seguir.

Tareas:
1. Roberta: figura provisional con sus posturas (sentada en el sofá, andando, tumbada en la cama) y su diálogo del prólogo.
2. Prólogo jugable: llegada, tareas cotidianas, conversación para que se acueste, pensamiento de Chevas sobre el grifo.
3. Chechu: figura provisional en la puerta, mirilla, conversación del acto 1 en la que menciona lo que Chevas pensó.
4. Timeline para la llamada a la puerta y la despedida.
5. Mezcla de audio y ritmo de los silencios.
6. Prueba con alguien que no conozca el juego.

**Cómo lo prueba Toni:** juega de principio a fin del acto 1.
**Terminado cuando:** se juega sin errores y Toni (y un tercero) acaban incómodos.

### Fase 6 · La escalada: acto 2 (4–5 semanas)

**Objetivo:** las visitas que suben de tono, la primera habitación oculta y la desaparición de Roberta.

Tareas:
1. Visitas 2 a 4 de Chechu con sus diálogos.
2. Variantes de la casa del acto 2 (objetos movidos, detalles nuevos).
3. Habitaciones ocultas 1 y 2 con su acceso.
4. Secuencia de Roberta: cama vacía, búsqueda por la casa, reaparición en la cocina hablando normal.
5. Cambios en el exterior (luces y silueta en casa de Chechu).

**Terminado cuando:** se juega del prólogo al final del acto 2 sin saltos y la desaparición de Roberta funciona.

### Fase 7 · Lo surrealista: acto 3 (4–5 semanas)

**Objetivo:** que todo deje de tener sentido sin perder el control técnico.

Tareas:
1. Efectos de geometría imposible: pasillo que se alarga, habitación repetida, puertas que llevan a otro sitio (con escenas aditivas o portales, sin cortes de carga).
2. Habitación oculta 3 (el sótano copia del dormitorio).
3. Roberta en sitios imposibles; la frase de Chechu en su boca.
4. Chechu dentro de la casa.
5. Exterior distorsionado por las ventanas; reloj parado a las 3:33.

**Terminado cuando:** se juega hasta el final del acto 3 y nada se rompe ni marea (probar con la opción de reducir efectos).

### Fase 8 · Desenlace (2–3 semanas)

Tareas:
1. La puerta al vacío: geometría exterior de la casa a una altura imposible, caída del jugador (o desmayo) y fundido a negro.
2. Repetición del prólogo reutilizando la escena del principio, con los cambios: las llaves no abren y hay que llamar.
3. Chechu abre la puerta y repite la frase fija de Chevas del acto 1 (mismo ID de diálogo reutilizado con otro personaje). Tele y voz de Roberta al fondo.
4. Corte a negro, créditos con todas las licencias y revisión completa de subtítulos.
**Terminado cuando:** el juego se completa entero de principio a fin.

### Fase 9 · Cierre de la primera versión (3–4 semanas)

Tareas:
1. Pruebas de juego completas, arreglo de errores, ajuste de sustos y ritmo.
2. Rendimiento: 60 fps estables (o 40 fijos) en toda la partida.
3. Build Linux para Steam Deck y, después, Windows.
4. Opciones de accesibilidad: tamaño de subtítulos, fondo detrás del texto, reducir efectos, reasignar teclas. Soporte opcional de mando.

**Terminado cuando:** la **primera versión** se juega entera en la Deck sin errores graves, con geometría provisional. Etiqueta `v1.0`.

### Fase 10 · Pulido: assets propios con Python en la nube (después de la primera versión)

**Objetivo:** sustituir toda la geometría provisional por assets definitivos que Claude genera con Python en la nube, y pulir el juego con ellos.

Tareas:
1. Abrir una sesión de Claude Code en la nube con el repositorio del juego y preparar ahí Python (y Blender en modo línea de comandos si hace falta). Comprobar el ciclo completo con un asset de prueba: generar, exportar a FBX, subir con Git LFS, `git pull` en la Deck e importar en Unity.
2. Crear una librería de scripts (`Tools/assets/`) con piezas reutilizables: mueble con cajones, marco de puerta, ventana, figura humana con esqueleto.
3. Por orden de importancia: personajes (Roberta y Chechu), salón, dormitorio, cocina, resto de estancias, habitaciones ocultas y exterior.
4. Animaciones de los personajes (andar, sentarse, tumbarse, hablar en la puerta).
5. Sustituir cada prefab provisional por su modelo definitivo, con captura para Toni antes y después.
6. Pulido final con los assets nuevos: iluminación, sonido, ritmo y rendimiento en la Deck.

**Terminado cuando:** no queda geometría provisional a la vista, Toni da por bueno cada asset y el juego mantiene el rendimiento en la Deck.

### Fase 11 · Doblaje y traducción (cuando haya presupuesto)

Tareas: exportar el guion con IDs para los actores, importar los clips y vincularlos por ID, sincronizar subtítulos, añadir idiomas.
**Terminado cuando:** cada línea tiene voz y los subtítulos siguen sincronizados.

---

## 4. Qué se aprovecha del prototipo Three.js

El prototipo (`juego/prototipo/` y `juego/capturas/`) es solo referencia; no se porta su código.

- **Sí (como idea, no como archivo):** parámetros PSX (360 px de alto, tramado Bayer, snap de vértices), la idea del menú y del logo OMINOUS, las capturas como referencia de distribución y luz, y las lecciones de colocación de objetos.
- **No:** ningún asset del prototipo (modelos, packs, fuentes), la historia cooperativa ni el reparto antiguo (Alan, Berni).
- **Packs de la microSD:** solo si Toni lo pide más adelante. Si se usan, revisar antes sus licencias (el pack de cocina, por ejemplo, no permite redistribuir los archivos sueltos).

---

## 5. Riesgos

| Riesgo | Qué hacemos |
| --- | --- |
| Unity no va bien en SteamOS | Se detecta en la fase 0; alternativas: distrobox con Ubuntu o editar en otro equipo y probar builds en la Deck |
| Rendimiento en la Deck | Medir desde la fase 2; exterior de bajo detalle, luces horneadas |
| Lo surrealista llega demasiado pronto y Chechu deja de dar miedo | La escalada se valida en la fase 5 antes de producir el resto |
| El alcance crece (muchas variantes de la casa) | Pocas variantes muy cuidadas; cada nueva idea se apunta en `ESTADO.md` y se decide al cerrar la fase |
| Los assets propios no llegan a la calidad buscada (sobre todo personajes y animaciones) | Enseñar cada asset a Toni pronto; si no convence, pedirle un asset concreto o usar los packs de la microSD |
| Mareo con efectos de cámara | Opción para reducir efectos desde la fase 3 |
| La geometría provisional no deja juzgar el miedo | Cuidar luz, sonido y siluetas desde la primera versión; el ambiente no depende del detalle de los modelos |
| Los assets generados en la nube no encajan al importarlos en Unity (escala, ejes, materiales) | Probar el ciclo completo con un asset antes de hacer el resto; un script de importación fija escala y materiales |

---

## 6. Decisiones pendientes de Toni

- [x] El detalle es algo que Chevas piensa y Chechu menciona.
- [x] Las habitaciones ocultas de la tabla 1.5.
- [x] Final en bucle: Chevas cae por una puerta al vacío, vuelve al principio y le abre Chechu con la frase de Chevas.
- [ ] La frase fija de Chevas al abrir la puerta en el acto 1 (propuesta: «¿Sí…? Son casi las tres. ¿Pasa algo?»).
- [x] La frase del pensamiento: lo del grifo del baño.
- [x] Un único final.
- [x] Primera versión con geometría provisional; assets propios con Python en la nube, en la fase de pulido (fase 10).
- [ ] Número exacto de visitas de Chechu (se cierra en la fase 1).
- [ ] Aspecto de Roberta y Chechu (se propone en la fase 10).

---

## 7. Cómo arrancar cada sesión (para Claude)

1. Leer este documento y `ESTADO.md`.
2. Decir a Toni en una frase en qué fase estamos y qué toca hoy.
3. Hacer las tareas de la fase en orden, con commit al terminar cada una.
4. Al terminar: explicar qué probar, esperar su opinión y actualizar `ESTADO.md`.
