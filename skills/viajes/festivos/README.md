# Festivos y temporadas por país

Conocimiento **general** del paquete: festivos, puentes, vacaciones escolares, temporadas altas y bajas, y eventos que mueven la demanda. Aquí **no** van datos del usuario, así que el agente sí puede crear y actualizar estos archivos.

## Archivos
Un archivo por país, en minúsculas y sin tildes: `colombia.md`, `peru.md`, `espana.md`, …

## Cómo se crea uno nuevo
1. `python3 ~/.claude/skills/viajes/scripts/travel.py holidays <ISO2> <año>`: festivos nacionales y los puentes que forman (fuente: Nager.Date).
2. Investiga las **temporadas** con WebSearch: vacaciones escolares, temporada alta y baja de turismo, eventos grandes (ferias, carnavales, Ramadán, Golden Week, agosto europeo…). Prefiere fuentes oficiales (ministerio de educación o de turismo).
3. Estructura, igual que `colombia.md`: **Festivos <año>** (fecha, día, festivo, puente) → **Temporadas** (fechas aproximadas, quién viaja, efecto 🔴🟠🟢) → **Cómo usarlo al planear** (como origen y como destino) → **Eventos**.
4. Marca 🟡 lo aproximado y pon fuente y fecha de consulta. Lo que no puedas confirmar va en "⚠️ Por verificar".

## Mantenimiento
- Los festivos cambian cada año (Pascua, traslados de lunes). Si el archivo no tiene el año que se está planeando, agrégalo con `holidays`.
- Si el usuario corrige una fecha, la corrección manda: anótala con la fecha.
