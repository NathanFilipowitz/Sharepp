"""
server.py

Author:  Nathan Filipowitz
Date:    2026-05-05
Purpose: Shared aiohttp server logic used by both app_controller.py (GUI) and cli.py (CLI).
         Contains no Flet dependency
"""

import base64
import hashlib
import os
import shutil
import tempfile
from pathlib import Path
from aiohttp import web
from views.download_view import generate_html

# Identify device type and OS from HTTP User-Agent to render something readable for the user
def parse_user_agent(ua):
    if not ua:
        return "Appareil inconnu"
 
    if "Mobile" in ua or "Android" in ua:
        device = "Mobile"
    elif "Tablet" in ua or "iPad" in ua:
        device = "Tablette"
    else:
        device = "PC"
 
    if "Android" in ua:
        os_name = "Android"
    elif "iPhone" in ua or "iPad" in ua:
        os_name = "iOS"
    elif "Windows" in ua:
        os_name = "Windows"
    elif "Linux" in ua:
        os_name = "Linux"
    elif "Mac" in ua:
        os_name = "macOS"
    else:
        os_name = "OS inconnu"
 
    return f"{device} ({os_name})"


# Return an aiohttp middleware for basic auth password verification
def make_auth_middleware(password_hash: str):
    @web.middleware
    async def auth_middleware(request, handler):
        if not password_hash:
            return await handler(request)
 
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Basic "):
            try:
                # Navigator sends: "Basic <base64(user:password)>"
                decoded = base64.b64decode(auth_header[6:]).decode("utf-8")
                _, pwd = decoded.split(":", 1)
                if hashlib.sha256(pwd.encode()).hexdigest() == password_hash:
                    return await handler(request)
            except Exception as e:
                print(f"Middleware error: {e}")
 
        # Send the password Pop-up authentification page
        return web.Response(
            status=401,
            headers={"WWW-Authenticate": 'Basic realm="Share++ (ignorer le champ utilisateur)"'},
            text="Authentification requise",
        )
 
    return auth_middleware


# Returns index and download handlers. log_function can use both log solutions (GUI or TUI)
def make_handlers(shared_path, log_function):
    async def handle_index(request):
        device = parse_user_agent(request.headers.get("User-Agent", ""))
        log_fn(f"Connexion de {request.remote} [{device}]", "success")
        try:
            files = os.listdir(shared_path)
            return web.Response(text=generate_html(files), content_type="text/html")
        except Exception as e:
            log_fn(f"Erreur lors de la lecture du répertoire : {e}", "error")
            return web.Response(text=str(e), status=500)

    async def handle_download(request):
        filename = request.match_info.get("filename", "")
        if not filename:
            return web.Response(text="Bad Request", status=400)
 
        device = parse_user_agent(request.headers.get("User-Agent", ""))
        log_fn(f"{request.remote} [{device}] télécharge '{filename}'", "warning")
 
        # anti directory traversal protection :
        # make path absolute and compare requested filename to match absolute path
        base_dir = Path(shared_path).resolve()
        requested = (base_dir / filename).resolve()
 
        if not str(requested).startswith(str(base_dir)):
            log_fn(f"Traversée de répertoire bloquée : {filename}", "error")
            return web.Response(text="Accès refusé", status=403)
 
        if requested.is_file():
            return web.FileResponse(requested, headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": "application/octet-stream",
            })
 
        if requested.is_dir():
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
                    zip_path = shutil.make_archive(
                        tmp.name.replace(".zip", ""), "zip", requested
                    )
                return web.FileResponse(zip_path, headers={
                    "Content-Disposition": f'attachment; filename="{filename}.zip"',
                })
            except Exception as e:
                log_fn(f"Erreur lors de la compression de '{filename}' : {e}", "error")
                return web.Response(text="Erreur lors de la création du zip", status=500)
 
        return web.Response(text="Fichier introuvable", status=404)


    return handle_index, handle_download

# Return a configured aiohttp web.Application
def build_app(shared_path, password_hash, log_function):
    middlewares = [make_auth_middleware(password_hash)] if password_hash else []
    app = web.Application(middlewares=middlewares)

    handle_index, handle_download = make_handlers(shared_path, log_function)
    app.router.add_get("/", handle_index)
    app.router.add_get("/{filename}", handle_download)

    return app