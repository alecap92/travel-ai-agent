# Manual — Motor de itinerarios

> Léelo cuando vayas a **crear, editar o re-planear** un itinerario.
> Un itinerario no es una lista de lugares: es una **secuencia logística realista**.

## Paso 1 — Restricciones (antes de armar nada)
Junta lo que ya sabes (ficha del viaje + Travel DNA) y pregunta **solo lo que falte y cambie el plan**:
- Fechas y horas reales de llegada y salida (vuelos de `## Reservas`), check-in y check-out
- Quién viaja (edades, movilidad, intereses de cada uno) y la dirección del alojamiento de cada noche
- Presupuesto, y si hay carro o solo transporte público
- **Lo que tiene hora fija:** reservas, entradas con horario, tours, vuelos o trenes
- Días y horarios de apertura de cada lugar (muchos museos cierran lunes o martes) y clima esperado
- **Festivos y temporadas** del destino en esas fechas (`festivos/<pais>.md` o `travel.py holidays`): cierres, multitudes, eventos

## Paso 2 — Agrupar por zona
- Cada día cubre **una zona** (o dos contiguas). Ponle nombre al día: `DÍA 2 — Alfama + Baixa`.
- **El alojamiento es el punto de partida y de llegada.**
- Lo de hora fija se pone primero y lo flexible se acomoda alrededor.
- Excursiones fuera de la ciudad ocupan su propio día.

## Paso 3 — Línea de tiempo con fricción humana
Tiempo de cada bloque = **duración de la actividad + traslado + colchón + fricción humana**.
- **Traslados reales:** `travel.py route` (hotel → paradas → hotel). Sin clave: ≈ 12 min por km a pie, marcado como estimado.
- **Horarios reales:** `travel.py place "<lugar, ciudad>" --date <día>` para cada lugar con horario.
- **Fricción humana:** filas, encontrar la entrada, caminar dentro de estaciones, baños, fotos, descanso. Como guía: +15 min por traslado en ciudad desconocida y +20–30 min en atracciones grandes con fila.
- Comidas a hora local real (en España se almuerza a las 14:00 y se cena a las 21:00).
- Formato:
```
DÍA 2 — Alfama + Baixa · ritmo: equilibrado · ~9 km a pie
09:30  Salida del hotel
09:45  Desayuno — <lugar> (pastel de nata)
10:30  Castelo de São Jorge (1h30) 🎟️ comprar online
12:15  Bajar a pie por Alfama (40 min, cuestas)
13:30  Almuerzo — <lugar>
...
19:00  Regreso al hotel
🗺️ Ruta: <link de Google Maps>
```

## Paso 4 — Densidad y energía
| Densidad | Actividades principales | Caminata aprox. |
|---|---|---|
| Relajado | 1–2 | < 8 km |
| Equilibrado | 3 | 8–14 km |
| Cargado | 4 | 14–18 km |
| Muy cargado | 5+ | > 18 km → **evítalo** salvo que el usuario lo pida |

- **Nunca llenes un día solo porque cabe.** Más actividades no hacen un mejor viaje.
- **Modelo de energía:** caminata + traslados + intensidad + cómo durmió (vuelo nocturno o jet lag). El día de llegada y el siguiente a un vuelo largo van ligeros. **Avisa si un día es mucho más pesado que el anterior** ("el día 4 está bastante más cargado que el 3; ¿muevo X al 5?").
- Alterna días pesados con días ligeros.

## Paso 5 — Clima
- Cruza el plan con el clima (`travel.py weather <ciudad> <inicio> <fin>`). Pon lo de exterior en el día de mejor pronóstico y deja un **plan B bajo techo** para los días dudosos.

## Paso 6 — QA antes de entregar (obligatorio)
No entregues el itinerario hasta pasar esta lista:
- [ ] ¿Cada lugar **existe y abre ese día y a esa hora**? (verificado: ver `recomendaciones.md`, capa anti-invención)
- [ ] ¿Algún traslado es imposible o muy justo? (llegada de vuelo o tren vs. la primera actividad)
- [ ] ¿Respeta las reservas que ya existen?
- [ ] ¿Algún día queda "muy cargado"? ¿Hay saltos bruscos de energía?
- [ ] ¿Tiene lógica geográfica, sin idas y vueltas?
- [ ] ¿Cabe en el presupuesto?
- [ ] ¿Encaja con el Travel DNA (antipatías incluidas) y con el de los acompañantes?
- [ ] ¿Algo crítico necesita reserva anticipada? → márcalo 🎟️ y súbelo a `## Alertas`
Si algo falla, corrígelo; si no se puede, **dilo** en vez de esconderlo.

## Paso 7 — Explica, incluido lo que dejaste fuera
- Una línea de **por qué** el día quedó así.
- **"Lo que no incluí":** 1–3 cosas famosas que dejaste fuera y por qué ("No puse Versalles: es medio día de traslado y ese día ya tienes dos cosas largas").

## Edición conversacional (después de entregado)
- **Cambia solo lo que depende del cambio.** "Quítame el museo" no rehace el viaje: rehace ese bloque y, si toca, la ruta de ese día.
- Siempre cierra con **"🔄 Qué cambió"**:
```
🔄 Qué cambió
• Museo X eliminado (día 3)
• Almuerzo movido a las 13:00 en Y (más cerca)
• −2,1 km a pie · −€18
```
- Frases como "hazlo más barato", "algo romántico", "quítame lo turístico", "no quiero manejar" o "mueve lo del sábado" se aplican sin pedir más datos, salvo que haya ambigüedad real.
- Si el pedido choca con algo (presupuesto, otra reserva, el ritmo), **avísalo con la consecuencia**: "Se puede, pero tendríamos que sacrificar X o Y".

## Re-plan en vivo (durante el viaje)
"Nos levantamos tarde", "está lloviendo", "estamos cansados" o "cerraron X":
1. Saca lo que ya no es viable.
2. **Protege lo intocable:** reservas pagadas o no cancelables y lo que el usuario marcó como imperdible.
3. Mueve lo flexible a otro día o a otra hora.
4. Recalcula la ruta (`route` / `maps-link`) y manda un link nuevo de Maps. Para "¿qué hago cerca?", usa `isochrone`.
5. Entrega "🔄 Qué cambió". Corto: está en la calle con el celular.

## Dónde se guarda
- El itinerario vigente va en el `.md` de la ciudad, bajo `## Itinerario`.
- Cada versión importante deja una línea en `## Cambios` del `README.md` del viaje (fecha + qué cambió). No guardes copias enteras de versiones viejas.
