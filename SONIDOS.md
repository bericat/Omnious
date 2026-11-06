# Sonidos que faltan por poner

Lista de trabajo para la fase de pulido de sonido (decisión de Toni: el sonido va al final). Ahora el juego usa
sonidos provisionales hechos por script (`Editor/AudioGen.cs`) o no tiene ninguno. Cada fila dice dónde suena y
cómo se llama en el código, para poder sustituirlo sin tocar nada más.

## Efectos que ya suenan con un provisional (`Sfx.Play("…")` o `<<sonido …>>` en Yarn)

| Nombre | Dónde suena | Qué debería ser |
|---|---|---|
| `paso` | Cada paso de Chevas | Pasos sobre madera, moqueta, baldosa y hormigón (uno por suelo) |
| `puerta_abre` / `puerta_cierra` | Todas las puertas | Bisagra vieja y golpe de madera |
| `puerta_cerrada` | Probar una puerta con llave | Picaporte que no cede |
| `interruptor` | Interruptores de luz | Clic de interruptor antiguo |
| `llaves` | Dejar las llaves en el cuenco; abrir la puerta | Llavero sobre cerámica |
| `llamada_puerta` | Chechu llama (visitas y bucle) | Tres golpes con los nudillos, siempre el mismo ritmo |
| `llave_no_gira` | Bucle final: la llave no entra | Llave que no gira en la cerradura |
| `llave_se_parte` | Acto 2: la llave inglesa con el grifo | Metal que cede |
| `tuberia_golpe` | Acto 2: el grifo | Golpe dentro de la pared |
| `objeto_cae` | La foto, la lata y otros sustos | Caídas (marco, lata, cosas pequeñas) |
| `golpe_armario` | Acto 2: el golpe en el armario | Golpe sordo dentro del armario |
| `risa` | Chechu desaparece riéndose | Risa ahogada, lejos |

## Bucles de ambiente que ya existen (provisionales)

| Nombre | Dónde | Qué debería ser |
|---|---|---|
| `Grifo` | Baño | Gota del grifo, irregular |
| `Nevera` | Cocina | Zumbido de nevera vieja, con arranques y paradas |
| `Reloj` | Pasillo | Tic-tac (se para en el acto 3) |
| `Viento` | Exterior | Viento suave entre las casas |

## Pendientes de la historia (aún sin sonido)

- **Tele de Roberta:** programa de teletienda (voces, música de anuncio), según la distancia. Lo quitó Toni hasta el doblaje.
- **Voces:** todo el guion de Chevas, Roberta y Chechu (doblaje de Toni). Los IDs de línea de Yarn sirven para cruzar archivos.
- **Coche:** motor que se apaga en el prólogo; coche que pasa lejos (`CocheLejano` ya existe como provisional).
- **Casa:** crujidos de madera, tuberías, puertas que se cierran solas al fondo de la casa.
- **Sótano:** escalera estrecha (pasos huecos), aire frío.
- **Desenlace:** silencio total de 2-3 s al abrir la puerta al vacío; caída; golpe al cortar a negro.
- **Menú y créditos:** música o ambiente de menú (si se quiere) y créditos.

## Oscuridad (OSCURIDAD.md)

| Nombre propuesto | Cuándo | Qué debería ser |
|---|---|---|
| `diferencial_baja` / `diferencial_sube` | Al saltar o subir el diferencial | Clac metálico del cuadro eléctrico |
| `apagon` | Cuando la casa se queda sin luz | La nevera y la tele se cortan de golpe; se nota el silencio |
| `linterna` | Encender y apagar la linterna | Clic de linterna de pilas |
| `linterna_tapar` | Tapar la linterna con la mano | Roce de la mano (muy suave) |
| `crujido_*` (15-20 variantes) | A oscuras, al azar | Madera, tuberías, cristales, la casa asentándose |
| `puerta_lejos` | Primer apagón | Una puerta que se cierra suave al otro lado de la casa |
| `aire_frio` | Rejilla del sótano | Corriente de aire con un tono bajo |
| `pasos_chechu` | Acto 3, Chechu dentro de casa | Pasos lentos, que se paran |
| `encontrado` | Chechu encuentra a Chevas | Golpe de sonido corto y seco |
| `despertar` | Chevas despierta en la cama | Respiración agitada, sábanas |
| Mezcla `Luz` / `Oscuridad` | Al cambiar el estado de la luz de la casa | En oscuridad: ambiente más bajo, pasos y crujidos más presentes, algo de filtro de graves (cambio suave de 1-2 s) |
