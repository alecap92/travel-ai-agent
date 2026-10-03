# Manual — Plantillas

> Copia la que necesites. Los campos que no se conozcan quedan en `—`; no los inventes.

## 1. Ficha del viaje → `viajes/<AAAA-MM-nombre>/README.md`
**El viaje es la entidad central.** Todo lo del viaje vive aquí o en los `.md` de sus ciudades.

```markdown
# <Nombre del viaje> — <mes año>

| Campo | Valor |
|---|---|
| Fase | inspiración · descubrimiento · planeación · optimización · reservas · pre-viaje · en viaje · post-viaje · cerrado |
| Viajeros | <usuario> + … (o "otros viajeros, sin el usuario") |
| Destinos | Ciudad 1 (n noches) → Ciudad 2 (n noches) |
| Fechas | AAAA-MM-DD → AAAA-MM-DD |
| Presupuesto | <moneda base> … (≈ USD …) · tasa usada: … (fecha) |
| Ritmo acordado | relajado / equilibrado / intenso |

## Restricciones y acuerdos de este viaje
<!-- Contexto que vale SOLO para este viaje: "esta vez no queremos madrugar", "mi mamá no camina mucho". -->

## Presupuesto
| Rubro | Planeado | Reservado | Notas |
|---|---|---|---|
| Vuelos | | | |
| Alojamiento | | | |
| Transporte local | | | |
| Comida | | | |
| Actividades | | | |
| Imprevistos (10 %) | | | |
| **Total** | | | Proyección: … |
> Lo **gastado** vive en la herramienta de gastos que declare `config.md`; no se duplica aquí.

## Reservas
| Tipo | Proveedor | Código | Fecha y hora local | Detalle | Cancelación |
|---|---|---|---|---|---|

## Ideas guardadas (bandeja de inspiración)
<!-- Ver plantilla 3. Se pasan al itinerario cuando encajan. -->

## Alertas
<!-- 🔴 / 🟠 / ⚪ — pendiente — fecha límite -->

## Cambios
<!-- AAAA-MM-DD — qué cambió en el plan y por qué -->

## Diario
| Fecha | Ciudad | Ánimo 1-5 | Clima | Top comida | Lo mejor del día |
|---|---|---|---|---|---|

## Debrief
- Lo mejor: · Repetiría: · Evitaría: · Alojamiento:
- Calificaciones: ❤️ … · 🙂 … · 😐 … · 👎 …
```

## 2. Ciudad → `viajes/<viaje>/<ciudad>.md`
```markdown
# <Ciudad>, <País>
- **Fechas:** … · **Alojamiento:** <nombre + dirección> · **Noches:** n

## Itinerario
<días con línea de tiempo y link de Maps; ver itinerarios.md>

## Lugares explicados / recomendados
<una línea por lugar: nombre — fecha — estado (explicado / recomendado / visitado / descartado) — dato clave — ❤️🙂😐👎 si ya fue>

## Tips y notas
## Documentación del usuario
```

## 3. Idea guardada ("guárdalo para Roma")
Una línea en `## Ideas guardadas` del viaje. Si todavía no hay viaje, en `destinos/<lugar>.md`:
```
- [restaurante] <Nombre> — <barrio, ciudad> — 💰 <precio aprox.> — fuente: <IG @autor / blog / amigo> (<fecha>) — por qué le interesó: … — estado: idea | en itinerario día N | descartada (motivo)
```
Tipos: `lugar` (restaurante, hotel, museo, playa, barrio) · `actividad` (tour, excursión, experiencia) · `transporte` (tren, ruta, aeropuerto) · `inspiración` (artículo, video, post).
**No le pidas al usuario que llene nada:** con "guárdalo para X" + el link o la captura, tú extraes los datos.

## 4. Destino en estudio → `destinos/<pais-o-ciudad>.md`
```markdown
# <Destino>
- **Estado en la wishlist:** idea / comparando / se volvió viaje → `viajes/<carpeta>`
- **Mejor época:** … (fuente, fecha) · **Días ideales:** … · **Costo aprox. desde su aeropuerto base:** …
- **Requisitos (con su pasaporte):** → `requisitos/<pais>.md`
- **Por qué encaja con el usuario:** … · **Peros:** …

## Zonas / ciudades a considerar
## Ideas guardadas
```

## 5. Requisitos → `requisitos/<pais>.md`
```markdown
# Requisitos de entrada — <País> (pasaporte <nacionalidad>)
- **Verificado:** AAAA-MM-DD · **Caduca:** +90 días · **Fuente:** <URL oficial>
- Visa / ETA: … · Costo y plazo: …
- Vigencia del pasaporte: … · Vacunas: … · Seguro: … · Otros: …
- Tránsitos y escalas: …
```

## 6. Lista de empaque → `viajes/<viaje>/packing.md`
Parte de `~/.claude/skills/viajes/manual/packing-base.md` + los ajustes personales de `config.md` + extras según clima, actividades, días y requisitos.
