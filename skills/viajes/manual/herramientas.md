# Manual — Herramientas y fuentes de datos

> Léelo cuando necesites **datos vivos o acciones**.
> **Regla: datos vivos → herramienta, nunca la memoria del modelo.**

## 🧰 1. `travel.py` — la caja de herramientas (skill `viajes`)
Catálogo completo, credenciales y cuotas: `~/.claude/skills/viajes/SKILL.md`.
```bash
T=~/.claude/skills/viajes/scripts/travel.py
python3 $T status                                              # qué está habilitado
python3 $T weather "Oporto" 2026-12-10 2026-12-14              # pronóstico o histórico (automático)
python3 $T fx --to <MONEDA_BASE>,EUR --amount 250               # tasas y conversión
python3 $T maps-link "Hotel, Ciudad" "Parada 1" "Parada 2" --mode walking
python3 $T route "Hotel, Ciudad" "Parada 1" "Hotel, Ciudad" --mode walk       # 🔑 Geoapify
python3 $T isochrone "Hotel, Ciudad" --minutes 15 --cat catering.restaurant  # 🔑 Geoapify
python3 $T nearby "Hotel, Ciudad" --cat tourism.sights --radius 1000         # 🔑 Geoapify
python3 $T place "Nombre, Ciudad" --date 2026-12-11                          # 🔑 Google Places
python3 $T flights <IATA_BASE> LIS 2027-02-10 --return 2027-02-24 --stops 2   # 🔑 SerpApi
python3 $T hotels "Alfama Lisboa" 2027-02-10 2027-02-14 --adults 2           # 🔑 SerpApi
python3 $T activities "Lisboa food tour"                                     # 🔑 Viator
```

### Qué herramienta para qué decisión
| Necesitas… | Herramienta | Sin clave (fallback, confianza 🟡) |
|---|---|---|
| Saber si un lugar existe, abre ese día y sigue operando | `place --date` | WebSearch: web oficial + Google Maps + reseñas recientes |
| Tiempos reales entre paradas | `route` | Estimación (≈ 12 min por km a pie) + `maps-link` para que el usuario vea la ruta |
| Qué hay cerca o qué alcanza en N minutos | `isochrone` / `nearby` | WebSearch "cerca de <lugar>" |
| Clima | `weather` | — (siempre disponible) |
| Pasar a la moneda base | `fx` | — (siempre disponible) |
| Precio real de vuelos | `flights` | Link de Google Flights (§3) + rango orientativo **marcado como tal** |
| Precio real de hoteles | `hotels` | Link de Booking o Airbnb (§3) |
| Tours | `activities` | Link de GetYourGuide o Civitatis (§3) + reseñas |

- Cuando la herramienta no tenga clave, **avísale al usuario una sola vez por sesión** cuál credencial desbloquea esa respuesta y ofrécele guardarla (`travel.py set-key`; prioridad en `SKILL.md`).
- **SerpApi tiene 250 búsquedas al mes:** solo búsquedas que deciden algo y nunca barridos automáticos. Mira `cuota_mes` en la respuesta.
- Copia la **fuente y la hora de consulta** que trae el JSON cuando des un precio o un horario.

## ✉️ 2. Correo de reservas (solo si `config.md` lo declara)
Si el usuario tiene una integración de correo (en `config.md` → Integraciones), úsala **solo para leer**:
- Busca confirmaciones: `(vuelo OR flight OR reserva OR booking OR itinerario OR "e-ticket" OR "check-in") newer_than:90d`, o por remitente (aerolíneas, Booking, Airbnb, Expedia…).
- Pasa lo esencial a `## Reservas` de la ficha del viaje: tipo, proveedor, **código**, fechas y **hora local con zona horaria**, dirección, check-in y check-out, equipaje y política de cancelación.
- 🚫 **Nunca** envíes ni respondas correos. No copies tarjetas, contraseñas ni enlaces de "gestionar reserva" con tokens.
- Si no hay integración, o la reserva solo viene en un adjunto que no puedes leer, pídele al usuario que te pegue los datos o te comparta el archivo.
- Respeta las cuentas que `config.md` marque como fuera de alcance.

## 🔗 3. Links de reserva (búsqueda prellenada; el usuario reserva)
- **Vuelos (Google Flights):** `https://www.google.com/travel/flights?q=Flights%20from%20<IATA_BASE>%20to%20<IATA>%20on%20AAAA-MM-DD%20through%20AAAA-MM-DD` (la herramienta `flights` ya lo devuelve).
- **Hoteles (Booking):** `https://www.booking.com/searchresults.html?ss=<ciudad>&checkin=AAAA-MM-DD&checkout=AAAA-MM-DD&group_adults=<n>`
- **Airbnb:** `https://www.airbnb.com/s/<ciudad>/homes?checkin=AAAA-MM-DD&checkout=AAAA-MM-DD&adults=<n>`
- **Actividades:** `https://www.getyourguide.com/s/?q=<ciudad+actividad>` · `https://www.civitatis.com/es/<ciudad>/`. Para entradas, primero la **web oficial** del lugar (suele ser más barata).
- **Trenes de Europa:** la web del operador (Renfe, CP, Trenitalia, SBB, DB) o Trainline.
- Un lugar suelto en Maps: `https://www.google.com/maps/search/?api=1&query=<nombre+ciudad>`

## 🛂 4. Requisitos de entrada (según la nacionalidad de `config.md`)
- **Fuentes, en orden:** 1) la web oficial de migración o la embajada del país de destino; 2) la fuente oficial del país del usuario declarada en `config.md` (cancillería o ministerio de exteriores); 3) IATA Travel Centre / Timatic, como apoyo.
- Revisa: visa / ETA / eVisa (costo y plazo) · **vigencia del pasaporte** (muchos piden 6 meses) · tiquete de salida · solvencia · seguro obligatorio · **vacunas** (p. ej. fiebre amarilla si el usuario viene de un país de riesgo) · **escalas:** algunos países exigen visa incluso en tránsito (EE.UU. es el caso clásico); revísalo para cada escala de la ruta.
- Guarda lo verificado en `requisitos/<pais>.md` (plantilla en `plantillas.md`) con **fuente + fecha**. **Caduca a los 90 días.**
- Confianza 🟢 solo con fuente oficial. Nunca des por hecho un requisito migratorio de memoria.

## 📥 5. Ideas y enlaces que manda el usuario (bandeja de inspiración)
- **URLs de blogs, artículos o Maps:** `WebFetch` y extrae la ficha de idea (`plantillas.md` §3). Si es un lugar, verifícalo con `place`.
- **Instagram y TikTok** suelen bloquear la lectura automática: intenta `WebFetch`; si falla, pide el texto del post o una captura.
- **YouTube:** título y descripción con `WebFetch`. Si hace falta el contenido completo, pide el texto o usa la herramienta de subtítulos que tenga el usuario.
- **Capturas y fotos:** léelas con `Read` (imagen).

## 💸 6. Gastos
No lleves gastos: viven en la herramienta de gastos que declare `config.md` (y, si no hay, el usuario decide dónde). En la ficha solo va el presupuesto **planeado y reservado**.
