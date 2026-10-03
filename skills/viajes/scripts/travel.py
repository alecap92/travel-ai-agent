#!/usr/bin/env python3
"""travel.py — herramientas de datos del agente asesor-viajes.

Solo stdlib. Paquete genérico: los datos y las claves del usuario viven en su KB
(por defecto ~/.claude/agents/_kb/viajes/, o la ruta en la variable VIAJES_KB), en el
archivo <KB>/.env. El paquete solo trae .env.example.
Cada comando imprime JSON compacto pensado para que lo lea el agente.

  python3 travel.py setup                     # crea la KB del usuario y su .env si no existen (no sobrescribe)
  python3 travel.py set-key GEOAPIFY_API_KEY  # guarda una clave (valor por stdin; nunca se imprime)
  python3 travel.py status
  python3 travel.py weather "Oporto" 2026-12-10 2026-12-14          # pronóstico o histórico automático
  python3 travel.py fx --to COP,EUR [--base USD] [--amount 100]
  python3 travel.py holidays CO 2027 [--from 2027-01-01 --to 2027-03-31]            # festivos + puentes (Nager.Date)
  python3 travel.py geocode "Torre de Belém, Lisboa"
  python3 travel.py maps-link "Hotel X, Lisboa" "Castelo de São Jorge" "Alfama" [--mode walking]
  python3 travel.py route "A" "B" ["C" ...] [--mode walk|drive|transit|bicycle] [--optimize]  # Google Routes o Geoapify
  python3 travel.py isochrone "Hotel X, Lisboa" --minutes 15 [--mode walk]          # Geoapify
  python3 travel.py nearby "Hotel X, Lisboa" --cat catering.restaurant [--radius 800] [--limit 15]
  python3 travel.py place "Cervejaria Ramiro, Lisboa" [--date 2026-12-11]            # Google Places (GOOGLE_MAPS_API_KEY)
  python3 travel.py flights BOG MAD 2027-02-10 [--return 2027-02-24] [--adults 1] [--stops 2] [--currency USD]
  python3 travel.py hotels "Lisboa Alfama" 2027-02-10 2027-02-14 [--adults 2] [--currency COP]
  python3 travel.py activities "Lisboa food tour" [--currency USD] [--limit 10]      # Viator
  python3 travel.py ta-search "Cervejaria Ramiro Lisboa" [--category restaurants]   # Tripadvisor
  python3 travel.py ta-details <location_id>
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import shutil
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

PKG_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KB_DIR = os.path.expanduser(os.environ.get("VIAJES_KB", "~/.claude/agents/_kb/viajes"))
ENV_PATH = os.path.join(KB_DIR, ".env")
CACHE_DIR = os.path.expanduser("~/.cache/viajes-tools")
UA = "asesor-viajes/1.0 (uso personal)"

# Variable de entorno → (proveedor, para qué sirve, dónde se saca)
KEYS = {
    "GEOAPIFY_API_KEY": ("Geoapify", "route, isochrone, nearby, geocode preciso", "https://myprojects.geoapify.com"),
    "SERPAPI_API_KEY": ("SerpApi", "flights, hotels (Google Flights/Hotels)", "https://serpapi.com/manage-api-key"),
    "GOOGLE_MAPS_API_KEY": ("Google Maps Platform (Places New + Routes + Geocoding)",
                            "place (verificar), route con transporte público y orden óptimo, geocode exacto",
                            "https://console.cloud.google.com/apis/credentials"),
    "VIATOR_API_KEY": ("Viator Partner API", "activities: tours y experiencias", "https://partnerresources.viator.com"),
    "TRIPADVISOR_API_KEY": ("Tripadvisor Content API", "ta-search, ta-details: ratings y reviews", "https://www.tripadvisor.com/developers"),
}
# Cuota mensual gratis aproximada, para avisar antes de quemarla
MONTHLY_QUOTA = {"SERPAPI_API_KEY": 250}


# ---------- utilidades ----------
def load_env():
    env = {}
    try:
        with open(ENV_PATH) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    env.update({k: v for k, v in os.environ.items() if k in KEYS})
    return env


ENV = load_env()


def out(obj):
    print(json.dumps(obj, ensure_ascii=False, indent=1))


def fail(msg, **extra):
    out({"ok": False, "error": msg, **extra})
    sys.exit(1)


def need(key):
    val = ENV.get(key)
    if not val:
        prov, use, where = KEYS[key]
        fail(f"Falta {key} en {ENV_PATH}",
             proveedor=prov, sirve_para=use, como_sacarla=where,
             que_hacer=("Usa el fallback (WebSearch/WebFetch). Avisa al usuario una vez por sesión: si quiere activarla, "
                        f"que te pase la clave y la guardas con `travel.py set-key {key}` (ver skills/viajes/SKILL.md)."))
    return val


def usage_count(key):
    """Cuenta llamadas por mes a APIs con cuota. Devuelve el total del mes."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    path = os.path.join(CACHE_DIR, "usage.json")
    month = dt.date.today().strftime("%Y-%m")
    try:
        data = json.load(open(path))
    except Exception:
        data = {}
    data.setdefault(month, {}).setdefault(key, 0)
    data[month][key] += 1
    json.dump(data, open(path, "w"))
    return data[month][key]


def http(url, method="GET", headers=None, body=None, ttl=0, timeout=30):
    """GET/POST con caché en disco (ttl en segundos; 0 = sin caché)."""
    h = {"User-Agent": UA, "Accept": "application/json"}
    h.update(headers or {})
    data = json.dumps(body).encode() if body is not None else None
    if data is not None:
        h.setdefault("Content-Type", "application/json")
    ck = hashlib.sha1((method + url + (data or b"").decode() + json.dumps(h, sort_keys=True)).encode()).hexdigest()
    cpath = os.path.join(CACHE_DIR, ck + ".json")
    if ttl and os.path.exists(cpath) and time.time() - os.path.getmtime(cpath) < ttl:
        res = json.load(open(cpath))
        res["_cache"] = True if isinstance(res, dict) else None
        return res
    req = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            res = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:500]
        fail(f"HTTP {e.code} en {urllib.parse.urlsplit(url).netloc}", detalle=detail)
    except urllib.error.URLError as e:
        fail(f"Sin conexión: {e.reason}")
    if ttl:
        os.makedirs(CACHE_DIR, exist_ok=True)
        json.dump(res, open(cpath, "w"))
    return res


def geocode_point(text):
    """Devuelve (lat, lon, etiqueta). Google o Geoapify si hay clave; si no, Open-Meteo (solo ciudades)."""
    gkey = ENV.get("GOOGLE_MAPS_API_KEY")
    if gkey:
        q = urllib.parse.urlencode({"address": text, "language": "es", "key": gkey})
        r = http(f"https://maps.googleapis.com/maps/api/geocode/json?{q}", ttl=30 * 86400)
        if r.get("status") == "OK" and r.get("results"):
            g = r["results"][0]
            loc = g["geometry"]["location"]
            return loc["lat"], loc["lng"], g.get("formatted_address", text)
    key = ENV.get("GEOAPIFY_API_KEY")
    if key:
        q = urllib.parse.urlencode({"text": text, "limit": 1, "lang": "es", "apiKey": key})
        r = http(f"https://api.geoapify.com/v1/geocode/search?{q}", ttl=30 * 86400)
        feats = r.get("features") or []
        if feats:
            p = feats[0]["properties"]
            return p["lat"], p["lon"], p.get("formatted", text)
    city = text.split(",")[-1].strip() if "," in text and not key and not gkey else text
    q = urllib.parse.urlencode({"name": city, "count": 1, "language": "es"})
    r = http(f"https://geocoding-api.open-meteo.com/v1/search?{q}", ttl=30 * 86400)
    res = r.get("results") or []
    if not res:
        fail(f"No encontré coordenadas para '{text}'")
    g = res[0]
    return g["latitude"], g["longitude"], f'{g["name"]}, {g.get("country", "")}'


def maps_link(stops, mode=None):
    enc = [urllib.parse.quote_plus(s) for s in stops]
    if mode:
        params = {"api": 1, "origin": stops[0], "destination": stops[-1], "travelmode": mode}
        if len(stops) > 2:
            params["waypoints"] = "|".join(stops[1:-1])
        return "https://www.google.com/maps/dir/?" + urllib.parse.urlencode(params)
    return "https://www.google.com/maps/dir/" + "/".join(enc)


# ---------- instalación del usuario ----------
def cmd_setup(a):
    """Crea la KB del usuario desde templates/kb y su .env desde .env.example. Nunca sobrescribe."""
    created, kept = [], []
    src_root = os.path.join(PKG_DIR, "templates", "kb")
    for root, _, files in os.walk(src_root):
        rel = os.path.relpath(root, src_root)
        dst_dir = os.path.normpath(os.path.join(KB_DIR, rel))
        os.makedirs(dst_dir, exist_ok=True)
        for f in files:
            dst = os.path.join(dst_dir, f)
            if os.path.exists(dst):
                kept.append(os.path.relpath(dst, KB_DIR))
            else:
                shutil.copy2(os.path.join(root, f), dst)
                created.append(os.path.relpath(dst, KB_DIR))
    for d in ("viajes", "destinos", "requisitos"):
        os.makedirs(os.path.join(KB_DIR, d), exist_ok=True)
    if not os.path.exists(ENV_PATH):
        shutil.copy2(os.path.join(PKG_DIR, ".env.example"), ENV_PATH)
        created.append(".env")
    else:
        kept.append(".env")
    os.chmod(ENV_PATH, 0o600)
    env = load_env()
    out({"ok": True, "kb": KB_DIR, "creados": created, "ya_existian": kept,
         "claves_faltantes": [k for k in KEYS if not env.get(k)],
         "siguiente_paso": "Si se creó travel-dna.md o config.md, haz el onboarding (ver SKILL.md §Onboarding)."})


def cmd_set_key(a):
    if a.name not in KEYS:
        fail(f"Variable desconocida: {a.name}", validas=list(KEYS))
    value = (a.value if a.value is not None else sys.stdin.read()).strip()
    if not value or " " in value:
        fail("Valor vacío o con espacios: revisa la clave que pasó el usuario.")
    if not os.path.exists(ENV_PATH):
        fail(f"No existe {ENV_PATH}: corre primero `travel.py setup`.")
    lines = open(ENV_PATH).read().splitlines()
    found = False
    for i, line in enumerate(lines):
        if line.split("=", 1)[0].strip().lstrip("# ").strip() == a.name:
            lines[i] = f"{a.name}={value}"
            found = True
            break
    if not found:
        lines.append(f"{a.name}={value}")
    with open(ENV_PATH, "w") as f:
        f.write("\n".join(lines) + "\n")
    os.chmod(ENV_PATH, 0o600)
    out({"ok": True, "guardada": a.name, "termina_en": "…" + value[-4:], "archivo": ENV_PATH,
         "siguiente_paso": "Prueba un comando que la use y actualiza el estado en el README de la KB."})


# ---------- comandos sin clave ----------
def cmd_status(a):
    rows = []
    for k, (prov, use, where) in KEYS.items():
        rows.append({"variable": k, "proveedor": prov, "configurada": bool(ENV.get(k)), "sirve_para": use})
    month = dt.date.today().strftime("%Y-%m")
    try:
        used = json.load(open(os.path.join(CACHE_DIR, "usage.json"))).get(month, {})
    except Exception:
        used = {}
    out({"ok": True, "kb": KB_DIR, "env": ENV_PATH, "env_existe": os.path.exists(ENV_PATH),
         "sin_clave_siempre_disponibles": ["weather (Open-Meteo)", "fx (open.er-api)", "maps-link", "geocode (ciudades)"],
         "credenciales": rows, "uso_mes": used, "cuotas_mensuales": MONTHLY_QUOTA})


def cmd_weather(a):
    lat, lon, label = geocode_point(a.place)
    start = dt.date.fromisoformat(a.start)
    end = dt.date.fromisoformat(a.end)
    today = dt.date.today()
    daily = "temperature_2m_max,temperature_2m_min,precipitation_sum"
    if (end - today).days <= 15 and start >= today:
        q = urllib.parse.urlencode({"latitude": lat, "longitude": lon, "timezone": "auto",
                                    "daily": daily + ",precipitation_probability_max",
                                    "start_date": a.start, "end_date": a.end})
        r = http(f"https://api.open-meteo.com/v1/forecast?{q}", ttl=3 * 3600)
        d = r["daily"]
        days = [{"fecha": d["time"][i], "max": d["temperature_2m_max"][i], "min": d["temperature_2m_min"][i],
                 "lluvia_mm": d["precipitation_sum"][i], "prob_lluvia": d["precipitation_probability_max"][i]}
                for i in range(len(d["time"]))]
        out({"ok": True, "tipo": "pronostico", "lugar": label, "dias": days, "fuente": "Open-Meteo forecast"})
        return
    # Histórico: mismas fechas en los últimos 3 años
    years = []
    for back in range(0, 6):
        if len(years) == 3:
            break
        try:
            s = start.replace(year=start.year - back)
        except ValueError:  # 29 de febrero
            continue
        e = s + (end - start)
        if e >= today:
            continue
        q = urllib.parse.urlencode({"latitude": lat, "longitude": lon, "timezone": "auto", "daily": daily,
                                    "start_date": s.isoformat(), "end_date": e.isoformat()})
        r = http(f"https://archive-api.open-meteo.com/v1/archive?{q}", ttl=30 * 86400)
        d = r["daily"]
        mx = [x for x in d["temperature_2m_max"] if x is not None]
        mn = [x for x in d["temperature_2m_min"] if x is not None]
        pr = [x for x in d["precipitation_sum"] if x is not None]
        years.append({"anio": s.year, "max_prom": round(sum(mx) / len(mx), 1) if mx else None,
                      "min_prom": round(sum(mn) / len(mn), 1) if mn else None,
                      "dias_con_lluvia": sum(1 for x in pr if x >= 1), "dias": len(d["time"])})
    out({"ok": True, "tipo": "historico (tendencia, NO pronóstico)", "lugar": label, "fechas": [a.start, a.end],
         "anios": years, "fuente": "Open-Meteo archive"})


def cmd_fx(a):
    r = http(f"https://open.er-api.com/v6/latest/{a.base.upper()}", ttl=6 * 3600)
    if r.get("result") != "success":
        fail("open.er-api no respondió bien", detalle=r)
    to = [c.strip().upper() for c in a.to.split(",")]
    rates = {c: r["rates"].get(c) for c in to}
    res = {"ok": True, "base": a.base.upper(), "tasas": rates, "actualizado": r.get("time_last_update_utc"),
           "fuente": "open.er-api.com", "nota": "Tasa de mercado; con tarjeta colombiana suma ~3-5 % de spread/comisión."}
    if a.amount:
        res["conversion"] = {c: round(a.amount * v, 2) for c, v in rates.items() if v}
    out(res)


WD = ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"]


def cmd_holidays(a):
    """Festivos nacionales de un país (código ISO-2) y los puentes que forman. Fuente: Nager.Date (sin clave)."""
    r = http(f"https://date.nager.at/api/v3/PublicHolidays/{a.year}/{a.country.upper()}", ttl=30 * 86400)
    if not isinstance(r, list):
        fail("Nager.Date no devolvió festivos (¿código de país ISO-2 válido?)", detalle=r)
    items = []
    for h in r:
        if not h.get("global", True) and not a.regional:
            continue
        d = dt.date.fromisoformat(h["date"])
        if (a.desde and h["date"] < a.desde) or (a.hasta and h["date"] > a.hasta):
            continue
        wd = d.weekday()
        puente = None
        if wd == 0:
            puente = f"{(d - dt.timedelta(days=2)).isoformat()} → {h['date']} (sáb-lun)"
        elif wd == 4:
            puente = f"{h['date']} → {(d + dt.timedelta(days=2)).isoformat()} (vie-dom)"
        elif wd == 1:
            puente = "martes: se puede armar puente de 4 días tomando el lunes"
        elif wd == 3:
            puente = "jueves: se puede armar puente de 4 días tomando el viernes"
        items.append({"fecha": h["date"], "dia": WD[wd], "nombre": h.get("localName"), "nombre_en": h.get("name"),
                      "nacional": h.get("global", True), "regiones": h.get("counties"), "puente": puente})
    out({"ok": True, "pais": a.country.upper(), "anio": a.year, "festivos": items, "fuente": "Nager.Date (date.nager.at)",
         "nota": ("Confírmalo con la fuente oficial del país si una fecha es decisiva; las temporadas altas y vacaciones "
                  "escolares no salen aquí: están en skills/viajes/festivos/<pais>.md.")})


def cmd_geocode(a):
    lat, lon, label = geocode_point(a.text)
    out({"ok": True, "lugar": label, "lat": lat, "lon": lon,
         "precision": "direccion" if (ENV.get("GOOGLE_MAPS_API_KEY") or ENV.get("GEOAPIFY_API_KEY")) else "ciudad (sin clave de Google ni Geoapify)"})


def cmd_maps_link(a):
    out({"ok": True, "link": maps_link(a.stops, a.mode), "paradas": len(a.stops),
         "aviso": "Más de ~9 paradas: divide el día" if len(a.stops) > 10 else None})


# ---------- Geoapify ----------
GEO_MODE = {"walk": "walk", "walking": "walk", "drive": "drive", "driving": "drive",
            "transit": "approximated_transit", "bicycle": "bicycle"}


G_MODE = {"walk": "WALK", "walking": "WALK", "drive": "DRIVE", "driving": "DRIVE",
          "transit": "TRANSIT", "bicycle": "BICYCLE", "bicycling": "BICYCLE"}


def _dur(sv):
    return round(int(str(sv).rstrip("s") or 0) / 60)


def cmd_route_google(a, key):
    """Google Routes API: tramo por tramo (transit no admite paradas intermedias)."""
    mode = G_MODE.get(a.mode, "WALK")
    stops = list(a.stops)
    order = list(range(len(stops)))
    fm = "routes.duration,routes.distanceMeters,routes.legs.duration,routes.legs.distanceMeters,routes.optimizedIntermediateWaypointIndex"
    if mode == "TRANSIT":
        fm += ",routes.legs.steps.transitDetails,routes.legs.steps.travelMode"
    legs = []
    if mode != "TRANSIT" and len(stops) > 2:
        body = {"origin": {"address": stops[0]}, "destination": {"address": stops[-1]},
                "intermediates": [{"address": x} for x in stops[1:-1]], "travelMode": mode,
                "languageCode": "es", "optimizeWaypointOrder": bool(a.optimize)}
        r = http("https://routes.googleapis.com/directions/v2:computeRoutes", method="POST",
                 headers={"X-Goog-Api-Key": key, "X-Goog-FieldMask": fm}, body=body, ttl=7 * 86400)
        if not r.get("routes"):
            fail("Google Routes no devolvió ruta", detalle=r)
        rt = r["routes"][0]
        opt = rt.get("optimizedIntermediateWaypointIndex")
        if a.optimize and opt:
            order = [0] + [i + 1 for i in opt] + [len(stops) - 1]
        seq = [stops[i] for i in order]
        for i, l in enumerate(rt.get("legs", [])):
            legs.append({"de": seq[i], "a": seq[i + 1], "km": round(l.get("distanceMeters", 0) / 1000, 2),
                         "min": _dur(l.get("duration", "0s"))})
    else:
        seq = stops
        for i in range(len(stops) - 1):
            body = {"origin": {"address": stops[i]}, "destination": {"address": stops[i + 1]},
                    "travelMode": mode, "languageCode": "es"}
            if mode == "TRANSIT" and a.depart:
                body["departureTime"] = a.depart
            r = http("https://routes.googleapis.com/directions/v2:computeRoutes", method="POST",
                     headers={"X-Goog-Api-Key": key, "X-Goog-FieldMask": fm}, body=body, ttl=86400)
            if not r.get("routes"):
                legs.append({"de": stops[i], "a": stops[i + 1], "error": "sin ruta para ese modo"})
                continue
            rt = r["routes"][0]
            leg = {"de": stops[i], "a": stops[i + 1], "km": round(rt.get("distanceMeters", 0) / 1000, 2),
                   "min": _dur(rt.get("duration", "0s"))}
            if mode == "TRANSIT":
                lines = []
                for lg in rt.get("legs", []):
                    for st in lg.get("steps", []):
                        td = st.get("transitDetails")
                        if td:
                            ln = td.get("transitLine", {})
                            lines.append(f'{(ln.get("vehicle") or {}).get("name", {}).get("text", "")} '
                                         f'{ln.get("nameShort") or ln.get("name", "")}: '
                                         f'{td.get("stopDetails", {}).get("departureStop", {}).get("name", "")} → '
                                         f'{td.get("stopDetails", {}).get("arrivalStop", {}).get("name", "")}'.strip())
                leg["transporte"] = lines
            legs.append(leg)
    ok_legs = [l for l in legs if "min" in l]
    out({"ok": True, "proveedor": "Google Routes", "modo": mode.lower(), "orden": seq,
         "optimizado": bool(a.optimize and mode != "TRANSIT"),
         "total_km": round(sum(l["km"] for l in ok_legs), 2), "total_min": sum(l["min"] for l in ok_legs),
         "tramos": legs, "maps": maps_link(seq, {"WALK": "walking", "DRIVE": "driving", "TRANSIT": "transit",
                                                 "BICYCLE": "bicycling"}[mode]),
         "nota": "Tiempos sin fricción humana: suma colchón (ver manual/itinerarios.md)."})


def cmd_route(a):
    gkey = ENV.get("GOOGLE_MAPS_API_KEY")
    if gkey:
        return cmd_route_google(a, gkey)
    key = need("GEOAPIFY_API_KEY")
    pts = [geocode_point(s) for s in a.stops]
    wp = "|".join(f"{lat},{lon}" for lat, lon, _ in pts)
    q = urllib.parse.urlencode({"waypoints": wp, "mode": GEO_MODE.get(a.mode, a.mode), "apiKey": key})
    r = http(f"https://api.geoapify.com/v1/routing?{q}", ttl=7 * 86400)
    feats = r.get("features") or []
    if not feats:
        fail("Geoapify no devolvió ruta", detalle=r)
    p = feats[0]["properties"]
    legs = [{"de": pts[i][2], "a": pts[i + 1][2], "km": round(l["distance"] / 1000, 2), "min": round(l["time"] / 60)}
            for i, l in enumerate(p.get("legs", []))]
    out({"ok": True, "modo": a.mode, "total_km": round(p["distance"] / 1000, 2), "total_min": round(p["time"] / 60),
         "tramos": legs, "maps": maps_link(a.stops, {"walk": "walking", "drive": "driving"}.get(a.mode, a.mode)),
         "nota": "Tiempos sin fricción humana: suma colchón (ver manual/itinerarios.md)."})


def cmd_isochrone(a):
    if not ENV.get("GEOAPIFY_API_KEY") and ENV.get("GOOGLE_MAPS_API_KEY") and a.cat:
        # Aproximación sin Geoapify: círculo de radio = minutos a pie (~80 m/min) con Google Places
        a.radius, a.by_distance, a.place = int(a.minutes * 80 * 0.8), False, a.place
        return cmd_nearby_google(a, ENV["GOOGLE_MAPS_API_KEY"])
    key = need("GEOAPIFY_API_KEY")
    lat, lon, label = geocode_point(a.place)
    q = urllib.parse.urlencode({"lat": lat, "lon": lon, "type": "time", "mode": GEO_MODE.get(a.mode, a.mode),
                                "range": a.minutes * 60, "apiKey": key})
    r = http(f"https://api.geoapify.com/v1/isoline?{q}", ttl=30 * 86400)
    feats = r.get("features") or []
    if not feats:
        fail("Geoapify no devolvió isócrona (puede tardar; reintenta en unos segundos)", detalle=r)
    iso_id = feats[0]["properties"].get("id")
    res = {"ok": True, "origen": label, "minutos": a.minutes, "modo": a.mode, "isoline_id": iso_id}
    if a.cat:
        q2 = urllib.parse.urlencode({"categories": a.cat, "filter": f"geometry:{iso_id}", "limit": a.limit,
                                     "lang": "es", "apiKey": key})
        res["lugares"] = _places_list(http(f"https://api.geoapify.com/v2/places?{q2}", ttl=7 * 86400))
    out(res)


def _places_list(r):
    items = []
    for f in r.get("features", []):
        p = f["properties"]
        items.append({"nombre": p.get("name"), "direccion": p.get("address_line2") or p.get("formatted"),
                      "categorias": (p.get("categories") or [])[:3], "distancia_m": p.get("distance"),
                      "web": (p.get("datasource", {}).get("raw", {}) or {}).get("website"),
                      "horario_osm": (p.get("datasource", {}).get("raw", {}) or {}).get("opening_hours")})
    return [i for i in items if i["nombre"]]


G_TYPES = {"catering.restaurant": "restaurant", "catering.cafe": "cafe", "catering.bar": "bar",
           "entertainment.museum": "museum", "tourism.sights": "tourist_attraction",
           "tourism.attraction": "tourist_attraction", "leisure.park": "park",
           "accommodation.hotel": "lodging", "commercial.marketplace": "market"}


def _km(lat1, lon1, lat2, lon2):
    from math import radians, sin, cos, asin, sqrt
    dlat, dlon = radians(lat2 - lat1), radians(lon2 - lon1)
    h = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 6371 * 2 * asin(sqrt(h))


def cmd_nearby_google(a, key):
    lat, lon, label = geocode_point(a.place)
    types = sorted({G_TYPES.get(c.strip(), c.strip()) for c in a.cat.split(",") if c.strip()})
    fields = ("places.displayName,places.formattedAddress,places.businessStatus,places.rating,places.userRatingCount,"
              "places.priceLevel,places.primaryTypeDisplayName,places.location,places.googleMapsUri,places.currentOpeningHours.openNow")
    body = {"includedTypes": types, "maxResultCount": min(a.limit, 20), "languageCode": "es",
            "rankPreference": "DISTANCE" if a.by_distance else "POPULARITY",
            "locationRestriction": {"circle": {"center": {"latitude": lat, "longitude": lon}, "radius": float(a.radius)}}}
    r = http("https://places.googleapis.com/v1/places:searchNearby", method="POST",
             headers={"X-Goog-Api-Key": key, "X-Goog-FieldMask": fields}, body=body, ttl=3 * 86400)
    items = []
    for p in r.get("places", []):
        loc = p.get("location") or {}
        d = _km(lat, lon, loc.get("latitude", lat), loc.get("longitude", lon)) * 1000
        items.append({"nombre": (p.get("displayName") or {}).get("text"), "direccion": p.get("formattedAddress"),
                      "tipo": (p.get("primaryTypeDisplayName") or {}).get("text"), "rating": p.get("rating"),
                      "resenas": p.get("userRatingCount"), "precio": p.get("priceLevel"),
                      "estado": p.get("businessStatus"), "abierto_ahora": (p.get("currentOpeningHours") or {}).get("openNow"),
                      "distancia_m": round(d), "a_pie_min": round(d / 80), "maps": p.get("googleMapsUri")})
    out({"ok": True, "proveedor": "Google Places (searchNearby)", "origen": label, "radio_m": a.radius, "tipos": types,
         "orden": "distancia" if a.by_distance else "popularidad", "lugares": items,
         "nota": "Distancia en línea recta (a_pie_min ≈ 80 m/min). Para el tiempo real usa `route`."})


def cmd_nearby(a):
    gkey = ENV.get("GOOGLE_MAPS_API_KEY")
    if gkey:
        return cmd_nearby_google(a, gkey)
    key = need("GEOAPIFY_API_KEY")
    lat, lon, label = geocode_point(a.place)
    q = urllib.parse.urlencode({"categories": a.cat, "filter": f"circle:{lon},{lat},{a.radius}",
                                "bias": f"proximity:{lon},{lat}", "limit": a.limit, "lang": "es", "apiKey": key})
    r = http(f"https://api.geoapify.com/v2/places?{q}", ttl=7 * 86400)
    out({"ok": True, "origen": label, "radio_m": a.radius, "lugares": _places_list(r),
         "nota": "Datos OSM: sirven para descubrir; horario y estado se verifican con `place` (Google)."})


# ---------- Google Places (New) ----------
def cmd_place(a):
    key = need("GOOGLE_MAPS_API_KEY")
    fields = ("places.id,places.displayName,places.formattedAddress,places.businessStatus,places.rating,"
              "places.userRatingCount,places.priceLevel,places.regularOpeningHours,places.googleMapsUri,"
              "places.websiteUri,places.primaryTypeDisplayName,places.location")
    r = http("https://places.googleapis.com/v1/places:searchText", method="POST",
             headers={"X-Goog-Api-Key": key, "X-Goog-FieldMask": fields},
             body={"textQuery": a.query, "languageCode": "es", "maxResultCount": a.limit}, ttl=3 * 86400)
    res = []
    for p in r.get("places", []):
        hours = (p.get("regularOpeningHours") or {}).get("weekdayDescriptions")
        item = {"nombre": (p.get("displayName") or {}).get("text"), "direccion": p.get("formattedAddress"),
                "estado": p.get("businessStatus"), "rating": p.get("rating"), "resenas": p.get("userRatingCount"),
                "precio": p.get("priceLevel"), "tipo": (p.get("primaryTypeDisplayName") or {}).get("text"),
                "horario": hours, "maps": p.get("googleMapsUri"), "web": p.get("websiteUri")}
        if a.date and hours:
            wd = dt.date.fromisoformat(a.date).weekday()  # 0=lunes; Google empieza en lunes
            item["horario_ese_dia"] = hours[wd] if wd < len(hours) else None
        item["veredicto"] = ("CERRADO DEFINITIVAMENTE" if p.get("businessStatus") == "CLOSED_PERMANENTLY" else
                             "CERRADO TEMPORALMENTE" if p.get("businessStatus") == "CLOSED_TEMPORARILY" else
                             "operando" if p.get("businessStatus") == "OPERATIONAL" else "sin dato")
        res.append(item)
    out({"ok": True, "consulta": a.query, "resultados": res, "fuente": "Google Places API (New)",
         "verificado": dt.date.today().isoformat(), "nota": "Horario regular; festivos y cierres puntuales pueden variar."})


# ---------- SerpApi: Google Flights / Hotels ----------
def _serp(params, ttl):
    key = need("SERPAPI_API_KEY")
    n = usage_count("SERPAPI_API_KEY")
    params = {**params, "api_key": key, "hl": "es", "gl": "co"}
    r = http("https://serpapi.com/search.json?" + urllib.parse.urlencode(params), ttl=ttl, timeout=60)
    if "error" in r:
        fail("SerpApi: " + str(r["error"]))
    return r, n


def _flight(o):
    legs = o.get("flights", [])
    return {"precio": o.get("price"), "duracion_total_min": o.get("total_duration"), "escalas": max(len(legs) - 1, 0),
            "tramos": [{"aerolinea": l.get("airline"), "vuelo": l.get("flight_number"),
                        "sale": f'{l["departure_airport"].get("id")} {l["departure_airport"].get("time")}',
                        "llega": f'{l["arrival_airport"].get("id")} {l["arrival_airport"].get("time")}',
                        "min": l.get("duration")} for l in legs],
            "esperas": [{"aeropuerto": x.get("id"), "min": x.get("duration"), "overnight": x.get("overnight", False)}
                        for x in o.get("layovers", [])],
            "token_reserva": o.get("booking_token") or o.get("departure_token")}


def cmd_flights(a):
    p = {"engine": "google_flights", "departure_id": a.origin.upper(), "arrival_id": a.dest.upper(),
         "outbound_date": a.date, "currency": a.currency, "adults": a.adults,
         "type": 1 if a.ret else 2, "stops": a.stops}
    if a.ret:
        p["return_date"] = a.ret
    r, n = _serp(p, ttl=6 * 3600)
    best = [_flight(o) for o in r.get("best_flights", [])][: a.limit]
    other = [_flight(o) for o in r.get("other_flights", [])][: a.limit]
    q = urllib.parse.quote(f"Flights from {a.origin} to {a.dest} on {a.date}" + (f" through {a.ret}" if a.ret else ""))
    out({"ok": True, "ruta": f"{a.origin}→{a.dest}", "ida": a.date, "vuelta": a.ret, "moneda": a.currency,
         "mejores": best, "otros": other, "insights_precio": r.get("price_insights"),
         "google_flights": f"https://www.google.com/travel/flights?q={q}",
         "fuente": "SerpApi (Google Flights)", "consultado": dt.datetime.now().isoformat(timespec="minutes"),
         "cuota_mes": f"{n}/{MONTHLY_QUOTA['SERPAPI_API_KEY']}",
         "nota": "Precio en vivo al momento de consultar; puede cambiar. En ida y vuelta, el precio es del viaje completo."})


def cmd_hotels(a):
    p = {"engine": "google_hotels", "q": a.query, "check_in_date": a.checkin, "check_out_date": a.checkout,
         "adults": a.adults, "currency": a.currency}
    if a.min_rating:
        p["rating"] = {3.5: 7, 4.0: 8, 4.5: 9}.get(a.min_rating, 8)
    r, n = _serp(p, ttl=12 * 3600)
    props = []
    for h in r.get("properties", [])[: a.limit]:
        props.append({"nombre": h.get("name"), "tipo": h.get("type"), "clase": h.get("hotel_class"),
                      "noche": (h.get("rate_per_night") or {}).get("lowest"),
                      "total": (h.get("total_rate") or {}).get("lowest"),
                      "rating": h.get("overall_rating"), "resenas": h.get("reviews"),
                      "rating_ubicacion": h.get("location_rating"), "link": h.get("link"),
                      "gps": h.get("gps_coordinates")})
    out({"ok": True, "consulta": a.query, "fechas": [a.checkin, a.checkout], "moneda": a.currency, "hoteles": props,
         "fuente": "SerpApi (Google Hotels)", "consultado": dt.datetime.now().isoformat(timespec="minutes"),
         "cuota_mes": f"{n}/{MONTHLY_QUOTA['SERPAPI_API_KEY']}"})


# ---------- Viator ----------
def cmd_activities(a):
    key = need("VIATOR_API_KEY")
    body = {"searchTerm": a.query, "currency": a.currency,
            "searchTypes": [{"searchType": "PRODUCTS", "pagination": {"start": 1, "count": a.limit}}]}
    r = http("https://api.viator.com/partner/search/freetext", method="POST",
             headers={"exp-api-key": key, "Accept": "application/json;version=2.0", "Accept-Language": "es-ES"},
             body=body, ttl=24 * 3600)
    items = []
    for p in ((r.get("products") or {}).get("results") or []):
        items.append({"titulo": p.get("title"), "codigo": p.get("productCode"),
                      "rating": (p.get("reviews") or {}).get("combinedAverageRating"),
                      "resenas": (p.get("reviews") or {}).get("totalReviews"),
                      "desde": (p.get("pricing") or {}).get("summary", {}).get("fromPrice"),
                      "duracion": p.get("duration"), "url": p.get("productUrl")})
    out({"ok": True, "consulta": a.query, "moneda": a.currency, "actividades": items, "fuente": "Viator Partner API"})


# ---------- Tripadvisor ----------
def cmd_ta_search(a):
    key = need("TRIPADVISOR_API_KEY")
    p = {"key": key, "searchQuery": a.query, "language": "es"}
    if a.category:
        p["category"] = a.category
    r = http("https://api.content.tripadvisor.com/api/v1/location/search?" + urllib.parse.urlencode(p), ttl=7 * 86400)
    out({"ok": True, "resultados": [{"id": x.get("location_id"), "nombre": x.get("name"),
                                     "direccion": (x.get("address_obj") or {}).get("address_string")}
                                    for x in r.get("data", [])], "fuente": "Tripadvisor Content API"})


def cmd_ta_details(a):
    key = need("TRIPADVISOR_API_KEY")
    p = {"key": key, "language": "es", "currency": "USD"}
    r = http(f"https://api.content.tripadvisor.com/api/v1/location/{a.location_id}/details?" + urllib.parse.urlencode(p),
             ttl=7 * 86400)
    out({"ok": True, "nombre": r.get("name"), "rating": r.get("rating"), "resenas": r.get("num_reviews"),
         "ranking": (r.get("ranking_data") or {}).get("ranking_string"), "precio": r.get("price_level"),
         "web": r.get("web_url"), "fuente": "Tripadvisor Content API"})


# ---------- CLI ----------
def main():
    ap = argparse.ArgumentParser(description="Herramientas de datos para asesor-viajes")
    sp = ap.add_subparsers(dest="cmd", required=True)

    sp.add_parser("setup")
    s = sp.add_parser("set-key"); s.add_argument("name"); s.add_argument("value", nargs="?")
    sp.add_parser("status")
    s = sp.add_parser("weather"); s.add_argument("place"); s.add_argument("start"); s.add_argument("end")
    s = sp.add_parser("fx"); s.add_argument("--base", default="USD"); s.add_argument("--to", default="COP,EUR")
    s.add_argument("--amount", type=float)
    s = sp.add_parser("geocode"); s.add_argument("text")
    s = sp.add_parser("holidays"); s.add_argument("country"); s.add_argument("year", type=int)
    s.add_argument("--from", dest="desde"); s.add_argument("--to", dest="hasta")
    s.add_argument("--regional", action="store_true", help="incluir festivos regionales")
    s = sp.add_parser("maps-link"); s.add_argument("stops", nargs="+"); s.add_argument("--mode", choices=["walking", "driving", "transit", "bicycling"])
    s = sp.add_parser("route"); s.add_argument("stops", nargs="+"); s.add_argument("--mode", default="walk")
    s.add_argument("--optimize", action="store_true", help="Google: reordena las paradas intermedias (no en transit)")
    s.add_argument("--depart", help="Google transit: hora de salida RFC3339, p. ej. 2026-12-11T09:00:00Z")
    s = sp.add_parser("isochrone"); s.add_argument("place"); s.add_argument("--minutes", type=int, default=15)
    s.add_argument("--mode", default="walk"); s.add_argument("--cat"); s.add_argument("--limit", type=int, default=20)
    s = sp.add_parser("nearby"); s.add_argument("place"); s.add_argument("--cat", default="catering.restaurant")
    s.add_argument("--radius", type=int, default=800); s.add_argument("--limit", type=int, default=15)
    s.add_argument("--by-distance", action="store_true", help="Google: ordenar por cercanía en vez de popularidad")
    s = sp.add_parser("place"); s.add_argument("query"); s.add_argument("--date"); s.add_argument("--limit", type=int, default=3)
    s = sp.add_parser("flights"); s.add_argument("origin"); s.add_argument("dest"); s.add_argument("date")
    s.add_argument("--return", dest="ret"); s.add_argument("--adults", type=int, default=1)
    s.add_argument("--stops", type=int, default=0, help="0 cualquiera · 1 directo · 2 máx 1 escala · 3 máx 2")
    s.add_argument("--currency", default="USD"); s.add_argument("--limit", type=int, default=5)
    s = sp.add_parser("hotels"); s.add_argument("query"); s.add_argument("checkin"); s.add_argument("checkout")
    s.add_argument("--adults", type=int, default=2); s.add_argument("--currency", default="USD")
    s.add_argument("--min-rating", type=float); s.add_argument("--limit", type=int, default=8)
    s = sp.add_parser("activities"); s.add_argument("query"); s.add_argument("--currency", default="USD")
    s.add_argument("--limit", type=int, default=10)
    s = sp.add_parser("ta-search"); s.add_argument("query"); s.add_argument("--category", choices=["hotels", "restaurants", "attractions", "geos"])
    s = sp.add_parser("ta-details"); s.add_argument("location_id")

    a = ap.parse_args()
    {"setup": cmd_setup, "set-key": cmd_set_key, "status": cmd_status, "weather": cmd_weather, "fx": cmd_fx, "holidays": cmd_holidays, "geocode": cmd_geocode, "maps-link": cmd_maps_link,
     "route": cmd_route, "isochrone": cmd_isochrone, "nearby": cmd_nearby, "place": cmd_place,
     "flights": cmd_flights, "hotels": cmd_hotels, "activities": cmd_activities,
     "ta-search": cmd_ta_search, "ta-details": cmd_ta_details}[a.cmd](a)


if __name__ == "__main__":
    main()
