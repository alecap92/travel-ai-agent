---
name: viajes
description: Paquete del agente asesor-viajes — manual de operación (itinerarios, recomendaciones, herramientas, operación del viaje, plantillas) y CLI `travel.py` con datos en vivo — clima (Open-Meteo), tasas de cambio, links de Google Maps, rutas e isócronas (Geoapify), verificación de lugares (Google Places), vuelos y hoteles con precio en vivo (SerpApi), tours (Viator), ratings (Tripadvisor). Incluye la instalación de la KB personal del usuario (`travel.py setup`) y el guardado de claves en su propio .env (`travel.py set-key`). Úsala para planear, verificar o cotizar un viaje con datos reales en vez de inventarlos.
---

# viajes — paquete del asesor de viajes

Paquete **genérico y compartible**. Aquí no hay datos de ningún usuario.

| Va en el paquete (`~/.claude/skills/viajes/`) | Va en la KB del usuario (`~/.claude/agents/_kb/viajes/`) |
|---|---|
| `manual/`: cómo trabaja el agente | `config.md`: nombre, canal, aeropuerto, moneda, pasaporte, integraciones |
| `scripts/travel.py`: herramientas | `travel-dna.md`, `paises-visitados.md`, `wishlist.md` |
| `templates/kb/`: KB vacía para usuarios nuevos | `viajes/`, `destinos/`, `requisitos/` |
| `.env.example` (sin valores) | `.env` con **sus** claves |

La ruta de la KB se puede cambiar con la variable `VIAJES_KB`.

```bash
T=~/.claude/skills/viajes/scripts/travel.py
python3 $T setup     # crea la KB y su .env si faltan (nunca sobrescribe)
python3 $T status    # qué claves hay, dónde está la KB, uso del mes
```

## Onboarding (primera vez o KB recién creada)
Si `setup` reporta que creó `config.md` o `travel-dna.md`, o si `config.md` sigue con "—" en lo esencial:
1. Preséntate en una línea y haz **solo 4 preguntas**, juntas y cortas: **nombre** · **ciudad y aeropuerto desde donde sale** · **moneda en la que piensa el presupuesto** · **nacionalidad/pasaporte** (sin números).
2. Llena `config.md` con eso. El resto de `config.md` (canal, integraciones, otros asesores) y del Travel DNA **se aprende con el uso**: no hagas cuestionarios.
3. Ofrece en una línea activar herramientas: "Si quieres precios reales de vuelos o rutas exactas, consigue estas claves gratis…" (prioridad abajo).
4. Sigue con lo que el usuario había preguntado.

## Catálogo de herramientas

| Comando | Para qué | Proveedor | Clave |
|---|---|---|---|
| `setup` | Crea la KB del usuario y su `.env` | — | No |
| `set-key <VAR> [valor]` | Guarda una clave en el `.env` del usuario (por stdin si no se pasa valor; **nunca la imprime**) | — | No |
| `status` | Claves configuradas, ruta de la KB y del `.env`, uso del mes | — | No |
| `weather <lugar> <inicio> <fin>` | Pronóstico (≤16 días) o histórico de las mismas fechas en los últimos 3 años (automático) | Open-Meteo | No |
| `fx --to <MON1,MON2> [--base USD] [--amount N]` | Tasas y conversión para el presupuesto | open.er-api | No |
| `holidays <ISO2> <año> [--from f --to f] [--regional]` | Festivos nacionales y los puentes que forman (las temporadas están en `festivos/<pais>.md`) | Nager.Date | No |
| `maps-link <A> <B> … [--mode walking]` | Link de Google Maps con las paradas en orden | — | No |
| `geocode <texto>` | Coordenadas (ciudad sin clave; dirección exacta con Google o Geoapify) | Google / Geoapify / Open-Meteo | Opcional |
| `route <A> <B> … [--mode walk\|drive\|transit] [--optimize] [--depart RFC3339]` | Distancia y minutos reales por tramo + link de Maps. Con Google: transporte público (líneas y paradas) y `--optimize` reordena las paradas | Google Routes → si no, Geoapify | `GOOGLE_MAPS_API_KEY` o `GEOAPIFY_API_KEY` |
| `isochrone <lugar> --minutes 15 [--cat …]` | Qué se alcanza en N minutos y qué lugares hay dentro. Con Geoapify es una isócrona real; si solo hay clave de Google, se **aproxima** con un círculo de radio ≈ minutos × 64 m | Geoapify → si no, Google | `GEOAPIFY_API_KEY` o `GOOGLE_MAPS_API_KEY` |
| `nearby <lugar> --cat <categoría> [--radius m] [--by-distance]` | Lugares cerca con rating, reseñas, precio y si está abierto ahora | Google Places → si no, Geoapify (OSM) | `GOOGLE_MAPS_API_KEY` o `GEOAPIFY_API_KEY` |
| `place "<nombre, ciudad>" [--date AAAA-MM-DD]` | **Anti-invención:** existe, estado (operando o cerrado), horario de ese día, rating, link | Google Places (New) | `GOOGLE_MAPS_API_KEY` |
| `flights <ORIG> <DEST> <fecha> [--return f] [--stops 2] [--currency X]` | Vuelos con precio en vivo, escalas, duración e insights de precio | SerpApi → Google Flights | `SERPAPI_API_KEY` |
| `hotels "<zona ciudad>" <in> <out> [--adults 2] [--currency X]` | Hoteles: precio por noche y total, rating, ubicación | SerpApi → Google Hotels | `SERPAPI_API_KEY` |
| `activities "<ciudad + tipo>"` | Tours y experiencias | Viator Partner API | `VIATOR_API_KEY` |
| `ta-search` / `ta-details <id>` | Rating, reseñas y ranking | Tripadvisor Content API | `TRIPADVISOR_API_KEY` |

> `flights` y `hotels` usan USD por defecto. **Pasa siempre `--currency` con la moneda base de `config.md`.**

Categorías de `--cat`: se aceptan las de Geoapify (y con Google se traducen solas) o tipos de Google directamente (`restaurant`, `cafe`, `bar`, `museum`, `tourist_attraction`, `park`, `lodging`, `bakery`…). Geoapify: `catering.restaurant`, `catering.cafe`, `catering.bar`,
`entertainment.museum`, `tourism.sights`, `tourism.attraction`, `leisure.park`, `commercial.marketplace`,
`accommodation.hotel`. Se pueden combinar con comas.

**Probadas en vivo (oct-2026):** `weather`, `fx`, `holidays`, `maps-link`, `geocode`, `setup`, `set-key`, `status`, `flights`, `hotels`, `place`, `route` (Google: walk, transit, `--optimize`), `geocode` (Google).

**Festivos y temporadas por país:** `festivos/<pais>.md` (conocimiento general del paquete; cómo crear uno nuevo en `festivos/README.md`).
Las demás están implementadas según la documentación de cada API, pero **se validan al configurar la primera clave**: si una falla, revisa el `detalle` del error y corrige el script.

**`nearby` ordena por popularidad:** lo primero suele ser lo más turístico (en el centro de Lisboa salió un Hard Rock Cafe). **Siempre filtra contra el Travel DNA** (antipatías) y prefiere lo local con buen rating y muchas reseñas. Usa `--by-distance` cuando importe la cercanía.

**Ojo con nombres ambiguos:** `route` y `place` mandan el texto tal cual a Google. "Rossio, Lisboa" lo resolvió a otro Rossio a 44 km. Usa **direcciones completas o con código postal** ("Praça Dom Pedro IV, 1100-200 Lisboa") y **desconfía de distancias absurdas** (>15 km dentro de una ciudad): repite con una dirección más precisa.

## Cómo las combina el agente
- **Verificar un lugar antes de recomendarlo** → `place --date`. Sin clave: WebSearch a la web oficial + reseñas recientes, con confianza 🟡.
- **Itinerario de un día** → `route` hotel → paradas → hotel (+ fricción humana del manual) → `maps-link`.
- **"¿Qué hago cerca?" / "tengo 2 horas"** → `isochrone` (15–20 min a pie) con `--cat` → `place` a los finalistas.
- **Clima en el plan** → `weather` por ciudad y fechas.
- **Presupuesto** → `fx` a la moneda base; `flights` y `hotels` para el costo real.

## Reglas
1. **Si falta una clave**, el comando lo dice: usa el fallback de `manual/herramientas.md` (confianza 🟡) y **avísale al usuario una vez por sesión** cuál clave desbloquearía esa respuesta y cómo sacarla.
2. **Guardar una clave:** cuando el usuario te la pase, corre `python3 $T set-key <VAR>` con el valor por stdin (`printf '%s' '<valor>' | python3 $T set-key <VAR>`). **Nunca la repitas en el chat** ni la escribas en otro archivo. Después prueba un comando que la use y actualiza "Estado de las herramientas" en el `README.md` de la KB. Recuérdale que, si pegó la clave en un chat compartido, conviene rotarla.
3. **Cuota de SerpApi (250 al mes gratis):** solo búsquedas que el usuario pidió o que deciden algo concreto. Nada de crons ni barridos. La caché dura 6 h (vuelos) y 12 h (hoteles). Si `cuota_mes` pasa de 200, avisa.
4. **Los precios en vivo llevan hora de consulta.** "A las 15:40 de hoy estaba en X; puede cambiar."
5. **Ninguna herramienta reserva ni compra.** Dan datos y links; el usuario reserva.
6. Caché y contador de uso: `~/.cache/viajes-tools/` (se puede borrar).

## Credenciales: prioridad para pedírselas al usuario
| # | Variable | Por qué | Cómo sacarla | Costo |
|---|---|---|---|---|
| 4 | `GEOAPIFY_API_KEY` | Opcional si ya hay Google: solo agrega la isócrona real ("qué alcanzo en 15 min" siguiendo calles). Sin Google, es la base de rutas y lugares cercanos. 5 min, sin tarjeta | geoapify.com → registrarse → *My Projects* → crear proyecto → copiar la API key | Gratis: 3.000 créditos/día, uso comercial permitido |
| **1** | `SERPAPI_API_KEY` | Vuelos y hoteles con precio real ("¿cuánto me cuesta ir?") | serpapi.com → registrarse → *Dashboard → API Key* | Gratis: 250 búsquedas/mes |
| **2** | `GOOGLE_MAPS_API_KEY` | Verificación dura (horario del día, si cerró, rating), rutas con **transporte público** y **orden óptimo de paradas**, geocodificación exacta | console.cloud.google.com → proyecto con **facturación activa** → habilitar **Places API (New)**, **Routes API** y **Geocoding API** → *Credentials → Create API key* → restringirla a esas 3 | Cuota gratis mensual por SKU, pero **exige billing activo** |
| 3 | `VIATOR_API_KEY` | Tours y experiencias | partnerresources.viator.com → afiliado → *Basic Access* | Gratis para afiliados |
| 5 | `TRIPADVISOR_API_KEY` | Ratings extra. Poco valor si ya está Google Places | tripadvisor.com/developers (con aprobación) | Cuota gratis |

**De Google Maps Platform no se usan (y por qué):** Route Optimization (es para flotas; `route --optimize` ya ordena paradas), Weather (Open-Meteo lo cubre gratis), Maps Static y Embed (sirven para mostrar mapas en una web: quedan para un dashboard).

**Descartadas (y por qué):** la API de Google Flights no existe para particulares (por eso se usa SerpApi); Booking.com Demand API, Travelpayouts/Aviasales y Kiwi/Tequila requieren ser partner aprobado (para uso personal bastan los links de búsqueda); de Amadeus Self-Service hay reportes de que se descontinuó en jul-2026 (no depender de él sin verificarlo); Google Travel Impact Model (CO₂ por vuelo) es un "nice to have" para después.

## Licencias
Open-Meteo es gratis para **uso no comercial**. Si el agente se usa dentro de un producto comercial, se necesita su plan pago.
