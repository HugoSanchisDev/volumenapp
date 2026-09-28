"""
Actualiza productos.json con precios de Mercadona y valores nutricionales de Open Food Facts.

- Precios: API pública (no oficial) de tienda.mercadona.es, documentada en
  https://github.com/datania/mercadona-catalog  (solo se piden los ~35 productos del plan).
- Nutrición: Open Food Facts (datos abiertos, licencia ODbL), buscando por código de barras (EAN).

Se ejecuta solo una vez por semana con GitHub Actions. También puedes lanzarlo a mano:
    python actualizar_productos.py
No necesita instalar nada: solo usa la librería estándar de Python.
"""
import json, time, urllib.request, urllib.error
from datetime import date
from pathlib import Path

ARCHIVO = Path(__file__).with_name("productos.json")
CP = "46001"          # tu código postal cambia el almacén y a veces el precio; ponlo aquí si quieres
UA = {"User-Agent": "Volumen-app-personal/1.0 (uso personal, 1 vez por semana)", "Accept": "application/json"}


def get_json(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


def num(v):
    try:
        return float(str(v).replace(",", "."))
    except (TypeError, ValueError):
        return None


def mercadona(pid):
    p = get_json(f"https://tienda.mercadona.es/api/products/{pid}/?lang=es")
    pi = p.get("price_instructions") or {}
    precio = num(pi.get("unit_price"))
    bulk = num(pi.get("bulk_price"))
    ref = str(pi.get("reference_format") or "").lower()
    datos = {
        "id": str(p.get("id") or pid),
        "nombre": p.get("display_name"),
        "precio": precio,
        "formato": " ".join(str(x) for x in [pi.get("unit_size"), pi.get("size_format")] if x) or None,
        "url": p.get("share_url"),
        "foto": p.get("thumbnail"),
        "ean": p.get("ean"),
    }
    # precio por kilo o litro, que es lo que usa la app para estimar el coste
    if bulk and ref in ("kg", "l"):
        datos["precio_kg"] = bulk
    return datos


def open_food_facts(ean):
    url = f"https://world.openfoodfacts.org/api/v2/product/{ean}.json?fields=product_name,nutriments"
    d = get_json(url)
    n = (d.get("product") or {}).get("nutriments") or {}
    k, p, c, f = (num(n.get(x)) for x in ("energy-kcal_100g", "proteins_100g", "carbohydrates_100g", "fat_100g"))
    if None in (k, p, c, f) or k <= 0:
        return None
    # control de calidad: las calorías deben cuadrar con los macros (±25 %)
    estim = 4 * p + 4 * c + 9 * f
    if estim == 0 or abs(estim - k) / k > 0.25:
        return None
    return {"k": round(k), "p": round(p, 1), "c": round(c, 1), "f": round(f, 1), "fuente": "Open Food Facts"}


def main():
    actual = json.loads(ARCHIVO.read_text(encoding="utf-8"))
    try:  # fijar el código postal (almacén) antes de pedir precios
        req = urllib.request.Request("https://tienda.mercadona.es/api/postal-codes/actions/change-pc/",
                                     data=json.dumps({"new_postal_code": CP}).encode(), method="PUT",
                                     headers={**UA, "Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=20).close()
    except Exception:
        pass

    ok = fallos = 0
    for clave, prod in actual["productos"].items():
        try:
            nuevo = mercadona(prod["id"])
            if nuevo.get("ean"):
                try:
                    nut = open_food_facts(nuevo["ean"])
                    if nut:
                        nuevo["nutricion"] = nut
                except Exception:
                    pass
            if not nuevo.get("nutricion") and prod.get("nutricion"):
                nuevo["nutricion"] = prod["nutricion"]
            actual["productos"][clave] = {k: v for k, v in nuevo.items() if v is not None}
            ok += 1
        except urllib.error.HTTPError as e:
            prod["error"] = f"HTTP {e.code}: revisa el id de este producto"
            fallos += 1
        except Exception as e:
            prod["error"] = str(e)[:120]
            fallos += 1
        time.sleep(1.0)  # sin prisas: 1 petición por segundo

    actual["actualizado"] = date.today().isoformat()
    actual["fuente"] = "Precios: API pública de tienda.mercadona.es. Nutrición: Open Food Facts (ODbL)."
    ARCHIVO.write_text(json.dumps(actual, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Actualizados {ok} productos, {fallos} con error.")


if __name__ == "__main__":
    main()
