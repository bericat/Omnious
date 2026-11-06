# Colocación de los assets PSX (fase 10)

Guía para HouseBuilder. Coordenadas del mundo de la casa (x al este, z al norte, calle al sur), en metros.
Las llamadas siguen la firma de `Model(nombre, padre, x, z, yaw, renombrar, y, collider)`.
Todas las texturas de `Art/Models/Texturas` y `Art/Superficies` van con filtro **Point** (aspecto PSX).

## Lo que cambia en assets que ya están colocados

- Mismos nombres, pivotes y huellas: Sofa, Tele, MesaBaja, Estanteria, Vitrina, Alfombra, Manta, Lampara,
  Cortina, Plafon, Encimera, Nevera, MesaCocina, SillaCocina, CajaLatas, Cama, Mesilla, MesillaLampara,
  Comoda, Armario, varios, Vater, Lavabo, Banera, LamparaTecho. Solo cambian la malla (menos polígonos)
  y la textura (128 px).
- **Cama** rehecha: misma huella (1,64 x 2,06 m con postes), cabecero en +Z local como antes.
- **MuebleRecibidor** trae ahora dos objetos: `MuebleRecibidor` y `Cuenco` (encimera a 0,835 m, cuenco a
  x local +0,2).
- **Llaves**: el origen va 3 mm por encima del fondo interior del cuenco. En la casa, **y = 0,854**
  (antes 0,845, que quedaba por debajo del fondo y no se veían). Mismo x, z y yaw: (6,8, 1,7), 30°.
- **Superficies** (Gotele, PapelPasillo, PapelDormitorio, PapelDamasco, Moqueta, SueloCocina,
  AzulejoCocina, Hormigon): ahora cada imagen cubre 4 x 4 m, así que el **tiling es 0,25** (antes 1).
  Nuevas para el exterior, también a 0,25: FachadaEnfoscado (paredes de nuestra casa), ZocaloPiedra
  (franja de 0 a 0,5 m), FachadaMadera (casa de Chechu) y Teja (tejados).

## Objetos nuevos (vida.py y laminas.py)

Medidas en ejes de Unity (ancho X, alto Y, fondo Z). Origen en el centro de la base salvo que se diga.
Los de pared tienen el origen en el centro de la cara de atrás (Z local = 0 contra la pared) y miran a +Z.
Grosor de pared 0,12: la cara interior de una pared en x = 8,2 está en x = 8,26.

### Cocina (encimera 8,3–12,7 en x, z 0,07–0,69, a 0,92 m; fregadero en x 10,2–10,6; fuego en 11,47–12,03)

| Objeto | Medida | Dónde | Llamada |
|---|---|---|---|
| Microondas | 0,48 x 0,29 x 0,38 | encimera, a la derecha del fuego | `Model("Microondas", f, 12.38f, 0.36f, 0f, null, 0.92f)` |
| Escurreplatos | 0,46 x 0,24 x 0,32 | sobre el escurridor del fregadero | `Model("Escurreplatos", f, 10.78f, 0.38f, 0f, null, 0.926f, collider: false)` |
| BotellasCocina | 0,18 x 0,31 x 0,17 | entre fregadero y fuego, contra los azulejos | `Model("BotellasCocina", f, 11.2f, 0.22f, 0f, null, 0.92f, collider: false)` |
| Cafetera | 0,13 x 0,22 x 0,12 | en el quemador de atrás a la izquierda | `Model("Cafetera", f, 11.62f, 0.29f, 20f, null, 0.95f, collider: false)` |
| Sarten | 0,40 x 0,05 x 0,22 | quemador delantero derecho, mango hacia el jugador | `Model("Sarten", f, 11.88f, 0.51f, 90f, null, 0.95f, collider: false)` |
| CuboBasura | 0,32 x 0,45 x 0,34 | hueco entre encimera y nevera | `Model("CuboBasura", f, 12.9f, 0.4f, 0f)` |
| Frutero | 0,30 x 0,16 x 0,28 | mesa de la cocina, junto al plato | `Model("Frutero", f, 8.9f, 2.75f, 0f, null, 0.76f, collider: false)` |
| Calendario | 0,30 x 0,48 (origen en el clavo, arriba) | pared oeste, encima de la mesa | `Model("Calendario", f, 8.26f, 2.35f, 90f, null, 1.75f, collider: false)` |

### Salón

| Objeto | Medida | Dónde | Llamada |
|---|---|---|---|
| Planta (potos) | 0,90 x 0,38 x 0,76 | rincón noroeste, en el suelo | `Model("Planta", f, 0.5f, 3.85f, 135f, collider: false)` |
| Revistas (periódico, revistas, mando y cenicero) | 0,49 x 0,02 x 0,36 | en el cojín derecho del sofá (la mesa baja ya trae los suyos); ajustar y al asiento | `Model("Revistas", f, 2.75f, 1.55f, 10f, null, 0.47f, collider: false)` |

### Recibidor (mueble a lo largo de z 0,98–2,02, contra la pared este, frente al oeste)

| Objeto | Medida | Dónde | Llamada |
|---|---|---|---|
| Telefono | 0,29 x 0,11 x 0,22 | mueble, en el extremo opuesto al cuenco | `Model("Telefono", f, 6.8f, 1.25f, 270f, null, 0.835f, collider: false)` |
| Paraguero | 0,24 x 0,83 x 0,24 | junto al perchero, pared oeste | `Model("Paraguero", f, 5.22f, 0.98f, 0f)` |
| Zapatos (de él y de ella) | 0,52 x 0,16 x 0,30 | a lo largo de la pared oeste, después del paraguero | `Model("Zapatos", f, 5.25f, 1.55f, 90f, collider: false)` |

### Pasillo y dormitorio

| Objeto | Medida | Dónde | Llamada |
|---|---|---|---|
| FotoBoda (cuadro de pared) | 0,40 x 0,30 x 0,03 | pasillo, pared sur, entre el salón y el recibidor | `Model("FotoBoda", f, 3.6f, 4.46f, 0f, null, 1.55f, collider: false)` |
| FotoBodaMesa (marco de pie) | 0,24 x 0,18 x 0,13 | encima de la cómoda, mirando a la cama | `Model("FotoBodaMesa", f, 2.95f, 9.75f, 180f, null, 0.76f, collider: false)` |
| Despertador | 0,10 x 0,14 x 0,04 | mesilla del sur (la de la lámpara del pack), mirando a la cama | `Model("Despertador", f, 0.45f, 7.15f, 90f, null, 0.40f, collider: false)` |
| Zapatillas | 0,27 x 0,07 x 0,28 | al bajar de la cama por el lado sur | `Model("Zapatillas", f, 1.0f, 6.95f, 180f, collider: false)` |
| SillaRopa | 0,42 x 0,96 x 0,44 | rincón sureste, junto al armario, mirando al cuarto | `Model("SillaRopa", f, 5.4f, 6.5f, 315f)` |

### Baño (lavabo en (9,6, 7,2), váter en (9,4, 9,55), bañera de x 6,9 a 7,66 y z 8,05 a 9,75; azulejo de la pared este en x 9,93)

| Objeto | Medida | Dónde | Llamada |
|---|---|---|---|
| Toallero (PARED, origen arriba en la barra) | 0,58 x 0,47 x 0,09 | pared este, entre lavabo y váter | `Model("Toallero", f, 9.925f, 8.35f, 270f, null, 1.15f, collider: false)` |
| PapelHigienico (PARED) | 0,16 x 0,15 x 0,12 | pared este, a mano desde el váter | `Model("PapelHigienico", f, 9.925f, 9.1f, 270f, null, 0.70f, collider: false)` |
| VasoCepillos | 0,20 x 0,18 x 0,07 | borde de atrás del lavabo, a un lado del grifo | `Model("VasoCepillos", f, 9.77f, 7.42f, 270f, null, 0.80f, collider: false)` |
| BotesBano (champú, gel) | 0,23 x 0,20 x 0,07 | borde de la bañera, junto a la pared, cerca del grifo | `Model("BotesBano", f, 6.97f, 9.45f, 90f, null, 0.52f, collider: false)` |
| Alfombrilla | 0,64 x 0,01 x 0,42 | en el suelo, al lado de la bañera | `Model("Alfombrilla", f, 8.0f, 8.9f, 90f, collider: false)` |

### Garaje (sin coche)

| Objeto | Medida | Dónde | Llamada |
|---|---|---|---|
| Bicicleta (de pie en su pata) | 1,70 x 0,89 x 0,50 | donde estaba el coche | `Model("Bicicleta", f, 16.3f, 2.4f, 15f)` |
| Neumaticos (dos apilados) | 0,66 x 0,50 x 0,66 | rincón sureste, junto al portón | `Model("Neumaticos", f, 18.5f, 0.5f, 0f)` |
| Bidon | 0,32 x 0,39 x 0,18 | contra la pared este, antes de la estantería | `Model("Bidon", f, 18.7f, 1.2f, 90f)` |
| Herramientas (PARED, tablero 1,0 x 0,6) | 1,00 x 0,60 x 0,06 | pared oeste, entre la puerta de la cocina y el rincón; las latas de pintura quedan debajo | `Model("Herramientas", f, 14.06f, 3.7f, 90f, null, 1.45f, collider: false)` |

### Exterior (fachada sur en z = 0, cara exterior en z = -0,06)

| Objeto | Medida | Dónde | Llamada |
|---|---|---|---|
| Farola (sustituye a la provisional) | 0,44 x 3,48 x 0,96; brazo hacia +Z local | mismos sitios; el farol debe quedar sobre la carretera | `(2, -2,6)` yaw 180, `(13, -6,1)` yaw 0, `(26, -2,6)` yaw 180 |
| Valla (tramo de 2 m, de x 0 a +2 local) | 2,10 x 1,10 x 0,14 | valla delantera en z -2,3, dejando libres el camino (5,4–6,6) y la entrada de coches (14,9–18,1) | x = -3, -1, 1, 3 y 7, 9, 11, 12,9, todos yaw 0 |
| Buzon | 0,23 x 1,34 x 0,46 | al final de la valla, junto al camino, boca a la calle | `(5.1, -2.45)` yaw 180 |
| CubosBasura (verde y gris) | 1,34 x 1,02 x 0,84 | contra la fachada, entre la ventana de la cocina y el garaje | `(13.4, -0.55)` yaw 0 |
| MacetaSeca | 0,44 x 0,90 x 0,44 | porche, a la derecha de la puerta | `(7.15, -0.4)` yaw 0, y 0,03 |
| Bajante (PARED, origen abajo en el tubo; canalón de 1 m hacia +X local) | 1,05 x 3,04 x 0,16 | junto al garaje y en la esquina suroeste. Bajarla hasta que el canalón quede bajo el alero | `(14.85, -0.06)` yaw 180 y `(-0.06, 0.12)` yaw 270 |
| Contraventanas (PARED, origen en el centro de la ventana, para 1,0 x 1,2 m) | 2,02 x 1,20 x 0,06 | ventana de la cocina, ventana oeste del salón y ventana de la colada (las del dormitorio y la pareja del salón están muy juntas y se pisarían) | cocina `(10.2, -0.06)` yaw 180, y 1,55, escala (1,4, 0,83, 1); salón oeste `(-0.06, 2.5)` yaw 270, y 1,5, escala (1,4, 1, 1); colada `(12.0, 10.06)` yaw 0, y 1,6, escala (1, 0,83, 1) |

La farola trae la bombilla como objeto aparte, **Luz** (material Farola_Luz, para hacerlo emisivo), en
(0, 3,2, 0,62) local. La luz de cada farola baja a esa altura y se desplaza con el brazo: con yaw 180,
en (x, 3,15, z - 0,62); con yaw 0, en (x, 3,15, z + 0,62). La de x = 13 se sigue llamando "Farola"
para que la escena de "falta una farola" la encuentre.

### Corcho

`NotasCorcho` (0,73 x 0,45, notas, recortes y fotos de Chevas, Roberta y Chechu con hilos rojos y
chinchetas, origen en el centro de atrás) se hizo para ir encima del corcho del sótano. Como el corcho ya
lleva las texturas personalizadas de la Deck, es opcional: usarlo solo si se quieren más capas encima.
