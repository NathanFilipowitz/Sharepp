"""
server_controller.py

Author:  Nathan Filipowitz
Date:    2026-05-05
Purpose: Shared aiohttp server logic used by both app_controller.py (GUI) and cli.py (CLI).
         Contains no Flet dependency.
         Authentication uses a custom HTML form instead of WWW-Authenticate Basic,
         so only the password field is shown (no username prompt from the browser).
"""

import base64
import hashlib
import hmac
import os
import shutil
import tempfile
from pathlib import Path
from aiohttp import web
from views.download_view import generate_html, generate_auth_html

# Static files (download.css, download.js) folder path
_STATIC_DIR = Path(__file__).parent.parent / "views" / "static"

# random sequence used to sign the session cookie. A new one is generated on each server startup
_COOKIE_SECRET = os.urandom(32)
_COOKIE_NAME = "sharepp_session"

# return HMAC-signed token proving the user entered the correct password
def _make_session_token(password_hash):
    sig = hmac.new(_COOKIE_SECRET, password_hash.encode(), hashlib.sha256).hexdigest()
    return sig

# Check that session cookie was based on current password hash. Extra validation
def _is_session_valid(cookie_value, password_hash):
    expected = _make_session_token(password_hash)
    return hmac.compare_digest(cookie_value, expected)


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

# return the aiohttp password authentification middleware using the custom HTML password form.
def make_auth_middleware(password_hash):
    @web.middleware
    async def auth_middleware(request, handler):
        if request.path == "/password" or request.path.startswith("/static/"):
            return await handler(request)

        # Check session cookie
        cookie = request.cookies.get(_COOKIE_NAME, "")
        if cookie and _is_session_valid(cookie, password_hash):
            return await handler(request)

        # Redirect to password page if user is not authentificated
        raise web.HTTPFound("/password")

    return auth_middleware

# return GET and POST handlers for the /password route
def make_login_handlers(password_hash):
    async def handle_login_get(request):
        return web.Response(
            text=generate_auth_html(error=False),
            content_type="text/html",
        )

    async def handle_login_post(request):
        data = await request.post()
        submitted = data.get("password", "")
        submitted_hash = hashlib.sha256(submitted.encode()).hexdigest()

        # Write session cookie to user browser. redirects to index
        if hmac.compare_digest(submitted_hash, password_hash):
            token = _make_session_token(password_hash)
            response = web.HTTPFound("/")
            response.set_cookie(
                _COOKIE_NAME,
                token,
                httponly=True,
                samesite="Strict",
            )
            return response

        # Wrong password
        return web.Response(
            text=generate_auth_html(error=True),
            content_type="text/html",
            status=401,
        )

    return handle_login_get, handle_login_post


# Returns index and download handlers. log_function can use both log solutions (GUI or TUI)
def make_handlers(shared_path, log_function):
    async def handle_index(request):
        device = parse_user_agent(request.headers.get("User-Agent", ""))
        log_function(f"Connexion de {request.remote} [{device}]", "success")
        try:
            files = os.listdir(shared_path)
            return web.Response(
                text=generate_html(files, shared_path),
                content_type="text/html",
            )
        except Exception as e:
            log_function(f"Erreur lors de la lecture du répertoire : {e}", "error")
            return web.Response(text=str(e), status=500)

    async def handle_download(request):
        filename = request.match_info.get("filename", "")
        if not filename:
            return web.Response(text="Bad Request", status=400)
 
        device = parse_user_agent(request.headers.get("User-Agent", ""))
        log_function(f"{request.remote} [{device}] télécharge '{filename}'", "warning")
 
        # anti directory traversal protection :
        # make path absolute and compare requested filename to match absolute path
        base_dir = Path(shared_path).resolve()
        requested = (base_dir / filename).resolve()
 
        if not str(requested).startswith(str(base_dir)):
            log_function(f"Traversée de répertoire bloquée : {filename}", "error")
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
                log_function(f"Erreur lors de la compression de '{filename}' : {e}", "error")
                return web.Response(text="Erreur lors de la création du zip", status=500)
 
        return web.Response(text="Fichier introuvable", status=404)

    return handle_index, handle_download

# Return a configured aiohttp web.Application
def build_app(shared_path, password_hash, log_function):
    middlewares = [make_auth_middleware(password_hash)] if password_hash else []
    app = web.Application(middlewares=middlewares)

    handle_index, handle_download = make_handlers(shared_path, log_function)
    app.router.add_get("/", handle_index)

    # add download.css and download.js
    app.router.add_static("/static", _STATIC_DIR)
    app.router.add_get("/{filename}", handle_download)

    # Login routes (only active when protection is active)
    if password_hash:
        login_get, login_post = make_login_handlers(password_hash)
        app.router.add_get("/password", login_get)
        app.router.add_post("/password", login_post)

    return app