# 🧳 Asesor de Viajes — agente para Claude Code

> **"La IA que aprende cómo viajas."**
> No es un generador de itinerarios: es un copiloto que **recuerda** cómo te gusta viajar, **investiga** con datos reales, **opera** el viaje contigo de la primera idea al regreso y **aprende** de cada viaje para el siguiente.

Versión 3 · oct-2026 · paquete genérico (sin datos personales).

---

## 1. Qué incluye y cómo se instala

```
~/.claude/agents/asesor-viajes.md          ← el agente (genérico)
~/.claude/skills/viajes/                    ← el paquete (genérico)
├── README.md            ← este documento
├── SKILL.md             ← catálogo de herramientas, onboarding y credenciales
├── .env.example         ← claves soportadas (vacías)
├── scripts/travel.py    ← herramientas: clima, cambio, Maps, rutas, isócronas, lugares, vuelos, hoteles, tours
├── festivos/<pais>.md   ← festivos, puentes, vacaciones escolares, temporadas altas y eventos por país (conocimiento general)
├── manual/              ← cómo trabaja el agente (lo lee según la fase)
│   ├── itinerarios.md       restricciones → zonas → línea de tiempo con fricción → densidad y energía → clima → QA → edición y re-plan
│   ├── recomendaciones.md   puntaje, ficha de recomendación, "explícame", foodie, anti-invención, confianza y fuentes
│   ├── herramientas.md      qué herramienta para cada decisión + fallback, correo, links de reserva, requisitos, ideas
│   ├── operacion-viaje.md   checklist pre-viaje, brief de 72 h, "¿qué hago ahora?", modo rescate, post-viaje
│   ├── plantillas.md        ficha del viaje, ciudad, idea, destino, requisitos
│   └── packing-base.md      lista de empaque base
└── templates/kb/        ← KB vacía que se copia a cada usuario nuevo

~/.claude/agents/_kb/viajes/               ← DATOS DEL USUARIO (no se comparte)
├── config.md · travel-dna.md · paises-visitados.md · wishlist.md · README.md
├── viajes/ · destinos/ · requisitos/
└── .env                 ← sus claves
```

**Instalar en otra máquina o para otra persona:**
1. Copia `agents/asesor-viajes.md` y `skills/viajes/` a su `~/.claude/`. **No copies `agents/_kb/viajes/`.**
2. Ya está. La primera vez que hable con el agente, este corre `travel.py setup`, crea su KB vacía y su `.env`, y le hace 4 preguntas de onboarding.
3. Requisitos: Python 3 (solo librería estándar) y conexión a internet.

**Compartir sin filtrar datos:** todo lo personal vive en `_kb/viajes/`. El paquete no tiene nombres, rutas personales ni claves. Antes de compartir, revísalo así:
`grep -rn -i "<tu nombre>" ~/.claude/agents/asesor-viajes.md ~/.claude/skills/viajes/` debe salir vacío.

---

## 2. Cómo usarlo
No hay comandos: se le habla normal.

| Fase | Ejemplos |
|---|---|
| 💡 Inspiración | "¿A dónde me voy en diciembre con 10 días?" · "¿Argentina o Croacia?" |
| 🔎 Descubrimiento | "¿Qué zonas me recomiendas?" · "¿Cuántos días en cada una?" |
| 🗺️ Planeación | "Armemos 5 días en Estambul" · "Hazme el día 2" |
| ✂️ Optimización | "Está muy caro" · "Quítame lo turístico" · "Más relajado" · "Mueve lo del sábado" |
| 🎟️ Reservas | "¿Cuánto cuesta volar a Lima en marzo?" · "Ya compré, revisa mi correo" |
| 🧾 Pre-viaje | "¿Qué necesito para entrar a Bolivia?" · "¿Qué empaco?" |
| 📍 En viaje | "Explícame este lugar" · "Tengo 3 horas" · "Llueve" · "Nos levantamos tarde" · "Cancelaron mi vuelo" |
| 📓 Post-viaje | "Ya volví" · "Califiquemos el viaje" |
| 📥 Ideas | Un link, reel o captura + "guárdalo para Roma" |
| 🔑 Claves | "Aquí está mi clave de Geoapify: …" → la guarda en tu `.env` sin repetirla |

**Lo que hace solo:** avisa lo 🔴 crítico de un viaje cercano, detecta traslados muy justos, recomienda comida local, lleva el diario mientras le cuentas y aprende tus gustos de lo que aceptas y rechazas.
**Lo que NO hace:** comprar, reservar, enviar correos o mensajes, llevar los gastos ni inventar precios u horarios.

---

## 3. Cómo piensa: Memoria + Inteligencia + Acciones

```
      MEMORIA (KB usuario)        INTELIGENCIA (agente + manual)         ACCIONES (travel.py + integraciones)
 ┌──────────────────────┐   ┌───────────────────────────────┐   ┌───────────────────────────────┐
 │ config · Travel DNA   │   │ Detecta la fase (8)            │   │ Clima, cambio, Maps            │
 │ Países · Wishlist     │──▶│ Restricciones y conflictos     │──▶│ Rutas, isócronas, lugares      │
 │ Ficha de cada viaje   │   │ Recomendación explicada        │   │ Vuelos, hoteles, tours         │
 │ Diario · Requisitos   │   │ Itinerario + QA · re-plan      │   │ Correo (lectura) · links       │
 └──────────────────────┘   └───────────────────────────────┘   └───────────────────────────────┘
            ▲                                                                      │
            └──────────────── aprende de cada interacción y cada viaje ◀───────────┘
```

**Fases:** Inspiración → Descubrimiento → Planeación → Optimización → Reservas → Pre-viaje → En viaje → Post-viaje → (memoria) → siguiente viaje.

**Principios:**
1. Nunca inventa datos vivos: usa una herramienta o una fuente oficial, y si no puede verificar, lo dice.
2. Confianza visible: 🟢 oficial o en vivo · 🟡 varias fuentes recientes · 🔴 secundaria o vieja.
3. Explica por qué (y por qué podría no gustarte, y qué dejó fuera).
4. Cambios quirúrgicos con "🔄 Qué cambió".
5. Menos es más: 2–3 opciones, itinerarios con densidad y energía realistas.
6. No pregunta lo que ya sabe; las preguntas sobre gustos llegan de a una.
7. Proactivo solo con lo que cambia una decisión.

**Memoria en 3 niveles:** lo momentáneo no se guarda · lo del viaje va a la ficha del viaje · lo permanente va al Travel DNA.

---

## 4. Herramientas y claves
Detalle y paso a paso en `SKILL.md`. Sin ninguna clave el agente funciona (clima, cambio, Maps y búsqueda web), pero con confianza 🟡 y sin precios en vivo.

| Prioridad | Clave | Desbloquea |
|---|---|---|
| 1 | SerpApi | Vuelos y hoteles con precio en vivo |
| 2 | Google Maps (Places + Routes + Geocoding) | Verificar lugares, rutas (también transporte público), orden óptimo de paradas, lugares cerca |
| 3 | Viator | Tours |
| 4 | Geoapify | Opcional con Google: isócrona real. Sin Google: rutas y lugares cerca |
| 5 | Tripadvisor | Ratings extra |

Las claves se guardan **solo** en el `.env` de la KB del usuario (`travel.py set-key`), nunca en el paquete.

---

## 5. Roadmap
| Idea | Requiere |
|---|---|
| Brief automático 72 h antes por el canal del usuario | Un cron que invoque al agente |
| Trip Board: mapa, línea de tiempo y atlas en una web | Un dashboard que lea `_kb/viajes/viajes/` |
| Presupuesto vs. gastado en vivo | Lectura de la herramienta de gastos del usuario |
| CO₂ por vuelo | Google Travel Impact Model (API key gratis) |
