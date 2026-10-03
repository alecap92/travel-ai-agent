# Datos de viaje de <nombre>

> Carpeta **personal** del asesor de viajes: perfil, viajes y claves de este usuario.
> El agente y su manual son genéricos y están en `~/.claude/agents/asesor-viajes.md` y `~/.claude/skills/viajes/`.
> **No compartas esta carpeta**: tiene datos personales y `.env` con claves.

| Archivo | Qué es |
|---|---|
| `config.md` | Datos operativos: nombre, canal, aeropuerto, moneda, pasaporte, integraciones |
| `travel-dna.md` | Cómo viaja: gustos −2…+2 con confianza, antipatías, compañeros |
| `paises-visitados.md` | Atlas de países visitados |
| `wishlist.md` | A dónde quiere ir |
| `viajes/<AAAA-MM-nombre>/` | Un viaje real: `README.md` (ficha), `packing.md`, `<ciudad>.md` |
| `destinos/<lugar>.md` | Destinos en estudio |
| `requisitos/<pais>.md` | Requisitos de entrada verificados (caducan a los 90 días) |
| `.env` | Claves de las APIs (`travel.py set-key`). **Privado** |

## Viajes
| Carpeta | Quién | Fechas | Fase |
|---|---|---|---|

## Estado de las herramientas
<!-- Lo actualiza el agente después de `travel.py status` o al agregar una clave. -->
| Clave | Estado |
|---|---|
| GEOAPIFY_API_KEY | ⏳ |
| SERPAPI_API_KEY | ⏳ |
| GOOGLE_MAPS_API_KEY | ⏳ |
| VIATOR_API_KEY | ⏳ |
| TRIPADVISOR_API_KEY | ⏳ |
