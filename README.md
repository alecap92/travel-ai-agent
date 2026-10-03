# 🧳 Travel AI Agent: asesor de viajes para Claude Code

> **"La IA que aprende cómo viajas."**
> Un agente de viajes para [Claude Code](https://claude.com/claude-code) que no se queda en generar itinerarios. **Recuerda** cómo te gusta viajar, **investiga con datos reales**, **opera el viaje contigo** desde la primera idea hasta el regreso, y **aprende** de cada viaje para el siguiente.

*English summary: a travel-advisor subagent + skill for Claude Code. It keeps a persistent "Travel DNA" of the traveler, treats each trip as a structured file, plans realistic itineraries (routing, opening hours, weather, holidays, crowd seasons), fetches live data (flights, hotels, places, routes, weather, FX, public holidays) and never invents live facts. Prompts and docs are in Spanish. MIT licensed.*

---

## ¿Por qué?

Los chatbots generales sirven para tener ideas, pero en un viaje real fallan:

- No recuerdan cómo viajas. Las recomendaciones salen genéricas, de "lo más famoso".
- Inventan horarios, precios o lugares que ya cerraron.
- Arman itinerarios imposibles: cruzan la ciudad tres veces y meten 12 cosas en un día.
- Les cambias un restaurante y te rehacen todo el viaje.
- Se olvidan del viaje entre una conversación y otra, y durante el viaje ya no ayudan.

Este agente parte de una idea distinta: **el objeto principal no es la conversación, es EL VIAJE.** Cada viaje es una ficha persistente en disco, y el chat es solo la forma de trabajar sobre ella.

## Qué hace

| Fase | Ejemplos |
|---|---|
| 💡 Inspiración | "¿A dónde me voy en diciembre con 10 días?" → 2–3 opciones con el porqué personal, la mejor época, el costo, la visa según tu pasaporte y un "pero" honesto |
| 🔎 Descubrimiento | "¿Qué zonas de Argentina me recomiendas?" |
| 🗺️ Planeación | "Armemos 5 días en Estambul" → días agrupados por zona, línea de tiempo con traslados reales y colchón, densidad y energía de cada día, clima, festivos, revisión de calidad antes de entregar |
| ✂️ Optimización | "Está muy caro" · "quítame lo turístico" → solo cambia lo que depende de ese cambio y te dice **"🔄 Qué cambió"** |
| 🎟️ Reservas | Precios en vivo de vuelos y hoteles + links de búsqueda prellenados (el agente **no compra**) |
| 🧾 Pre-viaje | Visas y requisitos según tu pasaporte (fuente oficial), checklist 🔴🟠⚪, lista de empaque, **brief 72 h antes** |
| 📍 En viaje | "Explícame este lugar" · "tengo 3 horas" · "está lloviendo" · "nos levantamos tarde" · **modo rescate** si cancelan tu vuelo |
| 📓 Post-viaje | Diario, calificaciones ❤️🙂😐👎, debrief → actualiza tu Travel DNA |
| 📥 Ideas | Mándale un link, un reel o una captura + "guárdalo para Roma" |

### Principios
1. **Nunca inventa datos vivos:** precios, horarios, disponibilidad y requisitos migratorios salen de una herramienta o de una fuente oficial, o el agente dice que no pudo verificarlos.
2. **Confianza visible:** 🟢 oficial o en vivo · 🟡 varias fuentes recientes · 🔴 secundaria o vieja.
3. **Explica por qué** te recomienda algo, por qué podría no gustarte y qué dejó fuera.
4. **Cambios quirúrgicos:** nunca rehace todo por un detalle.
5. **Menos es más:** 2–3 opciones y una recomendación. Más actividades no hacen un mejor viaje.
6. **Calendario siempre:** cruza las fechas con los festivos y temporadas del país de origen (puentes, demanda) y del destino (cierres, multitudes, eventos).
7. **Consultivo, no ejecutor:** no compra, no reserva y no envía nada.

### Travel DNA
El agente arma, poco a poco, un perfil de cómo viajas: gustos en una escala de −2 a +2 con nivel de confianza, **antipatías** (evitar una mala recomendación vale tanto como acertar una buena), ritmo, compañeros de viaje. Aprende más de lo que **haces** (lo que aceptas, quitas o calificas) que de lo que dices, y nunca te hace un cuestionario.

---

## Instalación

Requisitos: [Claude Code](https://claude.com/claude-code), Python 3 (solo librería estándar) e internet.

```bash
git clone https://github.com/alecap92/travel-ai-agent.git
cd travel-ai-agent
./install.sh            # copia el agente y la skill a ~/.claude (no sobrescribe sin --force)
```

O a mano:
```bash
cp agents/asesor-viajes.md ~/.claude/agents/
cp -R skills/viajes ~/.claude/skills/
```

Después, en Claude Code, háblale de viajes ("ayúdame a planear un viaje a Lisboa"). La primera vez el agente crea tu carpeta personal en `~/.claude/agents/_kb/viajes/` y te hace 4 preguntas: nombre, aeropuerto desde donde sales, moneda y pasaporte. El resto lo aprende con el uso.

## Claves de API (opcionales)

Funciona sin ninguna clave: clima, tasas de cambio, festivos, links de Maps y búsqueda web. Cada clave desbloquea datos en vivo:

| Prioridad | Clave | Qué desbloquea | Costo |
|---|---|---|---|
| 1 | `SERPAPI_API_KEY` | Vuelos y hoteles con precio en vivo (Google Flights/Hotels) | Gratis: 250 búsquedas/mes |
| 2 | `GOOGLE_MAPS_API_KEY` | Places (New) + Routes + Geocoding: verificar si un lugar sigue abierto y su horario del día, rutas a pie, en carro y en **transporte público**, orden óptimo de paradas, lugares cerca | Cuota gratis mensual; exige billing en Google Cloud |
| 3 | `VIATOR_API_KEY` | Tours y experiencias | Gratis para afiliados |
| 4 | `GEOAPIFY_API_KEY` | Isócronas reales ("qué alcanzo a pie en 15 min"); rutas y lugares cerca si no tienes Google | Gratis: 3.000 créditos/día |
| 5 | `TRIPADVISOR_API_KEY` | Ratings extra | Con aprobación |

Para agregar una, pásasela al agente en el chat, o mejor desde tu terminal, para que no quede en ningún historial:
```bash
python3 ~/.claude/skills/viajes/scripts/travel.py set-key SERPAPI_API_KEY   # pega la clave, Enter, Ctrl+D
python3 ~/.claude/skills/viajes/scripts/travel.py status
```
Las claves se guardan **solo** en tu `.env` personal (`~/.claude/agents/_kb/viajes/.env`, permisos 600), nunca en este repo. Paso a paso por proveedor: [`skills/viajes/SKILL.md`](skills/viajes/SKILL.md).

---

## Arquitectura

```
      MEMORIA (tu KB)             INTELIGENCIA (agente + manual)        ACCIONES (travel.py)
 ┌──────────────────────┐   ┌───────────────────────────────┐   ┌───────────────────────────────┐
 │ config · Travel DNA   │   │ Detecta la fase (8)            │   │ Clima · cambio · festivos      │
 │ Países · Wishlist     │──▶│ Calendario origen/destino      │──▶│ Lugares · rutas · geocoding    │
 │ Ficha de cada viaje   │   │ Recomendación explicada        │   │ Vuelos · hoteles · tours       │
 │ Diario · Requisitos   │   │ Itinerario + QA · re-plan      │   │ Links de Maps y de reserva     │
 └──────────────────────┘   └───────────────────────────────┘   └───────────────────────────────┘
            ▲                                                                      │
            └──────────────── aprende de cada interacción y cada viaje ◀───────────┘
```

**Dos carpetas que nunca se mezclan:**

| Este repo (genérico, compartible) | Tu KB personal (no se comparte) |
|---|---|
| `agents/asesor-viajes.md`: el agente | `~/.claude/agents/_kb/viajes/` |
| `skills/viajes/manual/`: cómo trabaja (itinerarios, recomendaciones, herramientas, operación del viaje, plantillas, empaque) | `config.md`: tu nombre, aeropuerto, moneda, pasaporte, integraciones |
| `skills/viajes/scripts/travel.py`: herramientas con datos en vivo | `travel-dna.md`, `paises-visitados.md`, `wishlist.md` |
| `skills/viajes/festivos/`: festivos y temporadas por país | `viajes/`, `destinos/`, `requisitos/` |
| `skills/viajes/templates/kb/`: KB vacía para usuarios nuevos | `.env` con tus claves |

### Herramientas (`travel.py`)
Un CLI en Python sin dependencias que devuelve JSON con **fuente y hora de consulta**, con caché en disco y control de cuotas:

`setup` · `set-key` · `status` · `weather` (Open-Meteo: pronóstico o histórico de las mismas fechas) · `fx` (tasas de cambio) · `holidays` (festivos y puentes de cualquier país, vía Nager.Date) · `maps-link` · `geocode` · `route` (walk, drive, transit, `--optimize`) · `nearby` · `isochrone` · `place` (verificar existencia, estado y horario de un día) · `flights` · `hotels` · `activities` · `ta-search` / `ta-details`

Catálogo completo: [`skills/viajes/SKILL.md`](skills/viajes/SKILL.md) · Detalle del paquete: [`skills/viajes/README.md`](skills/viajes/README.md)

---

## Contribuir

- **Festivos y temporadas de tu país:** agrega `skills/viajes/festivos/<pais>.md` siguiendo [`festivos/README.md`](skills/viajes/festivos/README.md). Es la contribución más fácil y útil.
- **Nuevas herramientas:** un subcomando en `travel.py`, solo con librería estándar, que devuelva JSON con `fuente` y fecha.
- **Mejoras al manual:** reglas generales de cómo planear mejor (nunca datos de una persona).
- Antes de abrir un PR, verifica que no se cuele nada personal: `grep -rn -i "<tu nombre>" .` debe salir vacío.

## Limitaciones
- Prompts y documentación en español. El agente responde en el idioma que configures.
- `activities` (Viator) y `ta-*` (Tripadvisor) están implementados según la documentación oficial, pero sin probar en vivo.
- Open-Meteo es gratis solo para **uso no comercial**. Si usas este agente dentro de un producto comercial, necesitas su plan pago. Revisa también los términos de cada proveedor de API.
- El agente no reserva, no compra ni envía mensajes. Es así por diseño.

## Licencia

[MIT](LICENSE): úsalo, modifícalo y compártelo libremente, manteniendo el aviso de copyright.
