#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gestor de anuncios del banner publicitario de la Tienda en Linea (PG del Campo).

Controla el TEXTO, el ENLACE y el FONDO (color) de cada anuncio, ademas de la
imagen o el video. Guarda todo en 'anuncios.json' con la MISMA estructura que
usa el nodo Firebase 'anuncios' que lee tienda.html.

Notas importantes
-----------------
* La rotacion aleatoria "en cada recarga de la pagina" del banner de la tienda
  ocurre en el navegador (JavaScript en tienda.html baraja los anuncios en cada
  carga). Es la unica forma de hacerlo en un sitio estatico (GitHub Pages): un
  script de Python no se ejecuta al recargar la pagina del visitante.
* Este script se usa para AUTORAR/administrar los anuncios y, si se desea,
  publicarlos. El comando 'shuffle' baraja el orden guardado (util si prefiere
  dejar un orden aleatorio "congelado" al momento de publicar). El comando
  'push' sube los anuncios al Firebase Realtime Database via su API REST.

Uso rapido
----------
  python anuncios.py add --titulo "Cafe 2x1" --texto "Solo esta semana" \
      --enlace https://wa.me/50557973097 --fondo "#1b382b" \
      --imagen https://.../promo.jpg
  python anuncios.py add --titulo "Video receta" --tipo video \
      --url https://www.youtube.com/embed/XXXXXXXX
  python anuncios.py list
  python anuncios.py disable AN12345678
  python anuncios.py shuffle
  python anuncios.py push --db https://productos-globales-campo-default-rtdb.firebaseio.com
"""
import argparse
import json
import os
import random
import re
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
STORE = os.path.join(HERE, "anuncios.json")
HEX_RE = re.compile(r"^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
URL_RE = re.compile(r"^https?://", re.I)


def load():
    if not os.path.exists(STORE):
        return {}
    try:
        with open(STORE, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception as e:  # archivo corrupto -> no destruir, avisar
        print(f"[!] No se pudo leer {STORE}: {e}", file=sys.stderr)
        return {}


def save(data):
    with open(STORE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[ok] Guardado en {STORE} ({len(data)} anuncio(s)).")


def new_id():
    return "AN" + str(int(time.time() * 1000))[-8:]


def validate(tipo, enlace, imagen, url, fondo):
    errs = []
    if enlace and not URL_RE.match(enlace):
        errs.append("El enlace debe iniciar con http:// o https://")
    if fondo and not HEX_RE.match(fondo):
        errs.append("El fondo debe ser un color hex, p.ej. #1b382b")
    if tipo == "video" and not url:
        errs.append("Un anuncio de tipo 'video' requiere --url (enlace embed)")
    if tipo == "imagen" and not imagen:
        errs.append("Un anuncio de tipo 'imagen' requiere --imagen")
    return errs


def cmd_add(a):
    data = load()
    errs = validate(a.tipo, a.enlace, a.imagen, a.url, a.fondo)
    if errs:
        for e in errs:
            print(f"[x] {e}", file=sys.stderr)
        sys.exit(1)
    aid = a.id or new_id()
    data[aid] = {
        "titulo": a.titulo,
        "descripcion": a.texto or "",
        "enlace": a.enlace or "",
        "tipo": a.tipo,
        "imagen": a.imagen if a.tipo == "imagen" else "",
        "url": a.url if a.tipo == "video" else "",
        "fondo": a.fondo or "#1b382b",
        "activo": not a.inactivo,
    }
    save(data)
    print(f"[ok] Anuncio '{aid}' creado.")


def cmd_edit(a):
    data = load()
    if a.id not in data:
        print(f"[x] No existe el anuncio '{a.id}'", file=sys.stderr)
        sys.exit(1)
    ad = data[a.id]
    if a.titulo is not None:
        ad["titulo"] = a.titulo
    if a.texto is not None:
        ad["descripcion"] = a.texto
    if a.enlace is not None:
        ad["enlace"] = a.enlace
    if a.fondo is not None:
        ad["fondo"] = a.fondo
    if a.tipo is not None:
        ad["tipo"] = a.tipo
    if a.imagen is not None:
        ad["imagen"] = a.imagen
    if a.url is not None:
        ad["url"] = a.url
    errs = validate(ad.get("tipo", "imagen"), ad.get("enlace", ""),
                    ad.get("imagen", ""), ad.get("url", ""), ad.get("fondo", ""))
    if errs:
        for e in errs:
            print(f"[x] {e}", file=sys.stderr)
        sys.exit(1)
    save(data)
    print(f"[ok] Anuncio '{a.id}' actualizado.")


def _set_active(aid, value):
    data = load()
    if aid not in data:
        print(f"[x] No existe el anuncio '{aid}'", file=sys.stderr)
        sys.exit(1)
    data[aid]["activo"] = value
    save(data)
    print(f"[ok] Anuncio '{aid}' {'activado' if value else 'ocultado'}.")


def cmd_enable(a):
    _set_active(a.id, True)


def cmd_disable(a):
    _set_active(a.id, False)


def cmd_remove(a):
    data = load()
    if a.id not in data:
        print(f"[x] No existe el anuncio '{a.id}'", file=sys.stderr)
        sys.exit(1)
    del data[a.id]
    save(data)
    print(f"[ok] Anuncio '{a.id}' eliminado.")


def cmd_list(a):
    data = load()
    if not data:
        print("(sin anuncios)")
        return
    for aid, ad in data.items():
        estado = "activo" if ad.get("activo", True) else "oculto"
        tipo = ad.get("tipo", "imagen")
        print(f"- {aid} [{estado}] ({tipo}) {ad.get('titulo','')!r}")
        if ad.get("descripcion"):
            print(f"    texto : {ad['descripcion']}")
        if ad.get("enlace"):
            print(f"    enlace: {ad['enlace']}")
        if ad.get("imagen"):
            print(f"    imagen: {ad['imagen']}")
        if ad.get("url"):
            print(f"    video : {ad['url']}")
        print(f"    fondo : {ad.get('fondo','#1b382b')}")


def cmd_shuffle(a):
    """Baraja el orden de los anuncios en anuncios.json (Fisher-Yates)."""
    data = load()
    items = list(data.items())
    random.shuffle(items)
    save(dict(items))
    print("[ok] Orden barajado aleatoriamente.")


def cmd_push(a):
    """Sube los anuncios al nodo 'anuncios' del Firebase Realtime Database."""
    data = load()
    base = a.db.rstrip("/")
    url = f"{base}/anuncios.json"
    if a.auth:
        url += f"?auth={a.auth}"
    payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=payload, method="PUT",
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            print(f"[ok] Publicado en Firebase (HTTP {resp.status}). "
                  f"La tienda mostrara los anuncios en vivo.")
    except Exception as e:
        print(f"[x] No se pudo publicar: {e}", file=sys.stderr)
        print("    Verifique la URL del Realtime Database y las reglas de escritura.",
              file=sys.stderr)
        sys.exit(1)


def build_parser():
    p = argparse.ArgumentParser(description="Gestor de anuncios del banner de la Tienda en Linea (PG del Campo).")
    sub = p.add_subparsers(dest="cmd", required=True)

    padd = sub.add_parser("add", help="Agregar un anuncio")
    padd.add_argument("--id", default="")
    padd.add_argument("--titulo", required=True)
    padd.add_argument("--texto", default="", help="Texto / descripcion del anuncio")
    padd.add_argument("--enlace", default="", help="Enlace http(s) al hacer clic")
    padd.add_argument("--tipo", choices=["imagen", "video"], default="imagen")
    padd.add_argument("--imagen", default="", help="URL de la imagen (tipo imagen)")
    padd.add_argument("--url", default="", help="URL embed del video (tipo video)")
    padd.add_argument("--fondo", default="#1b382b", help="Color de fondo hex")
    padd.add_argument("--inactivo", action="store_true", help="Crear oculto")
    padd.set_defaults(func=cmd_add)

    ped = sub.add_parser("edit", help="Editar un anuncio existente")
    ped.add_argument("id")
    ped.add_argument("--titulo")
    ped.add_argument("--texto")
    ped.add_argument("--enlace")
    ped.add_argument("--tipo", choices=["imagen", "video"])
    ped.add_argument("--imagen")
    ped.add_argument("--url")
    ped.add_argument("--fondo")
    ped.set_defaults(func=cmd_edit)

    pen = sub.add_parser("enable", help="Activar (mostrar) un anuncio")
    pen.add_argument("id")
    pen.set_defaults(func=cmd_enable)

    pdi = sub.add_parser("disable", help="Ocultar un anuncio")
    pdi.add_argument("id")
    pdi.set_defaults(func=cmd_disable)

    prm = sub.add_parser("remove", help="Eliminar un anuncio")
    prm.add_argument("id")
    prm.set_defaults(func=cmd_remove)

    sub.add_parser("list", help="Listar anuncios").set_defaults(func=cmd_list)
    sub.add_parser("shuffle", help="Barajar el orden aleatoriamente").set_defaults(func=cmd_shuffle)

    ppu = sub.add_parser("push", help="Publicar los anuncios en Firebase (REST)")
    ppu.add_argument("--db", required=True, help="URL del Realtime Database")
    ppu.add_argument("--auth", default="", help="Token/secret opcional si las reglas lo exigen")
    ppu.set_defaults(func=cmd_push)
    return p


def main():
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
