"""
cli.py

Author:  Nathan Filipowitz
Date:    2026-05-05
Purpose: Headless CLI mode for Share++.
Usage:
    sharepp-cli.exe C:\folder [--port 3001] [--secure]
"""

import argparse
import asyncio
import datetime
import hashlib
import os
import sys
import getpass
from pathlib import Path
from aiohttp import web
from controllers import network_controller
from controllers.server_controller import build_app

COLORS = {
    "info":    "\033[0m",
    "success": "\033[92m",
    "warning": "\033[93m",
    "error":   "\033[91m",
    "reset":   "\033[0m",
}

def log(message, level: str = "info"):
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    color = COLORS.get(level, COLORS["info"])
    print(f"{color}[{ts}] {message}{COLORS['reset']}", flush=True)

def print_qr(url: str):
    try:
        import qrcode
        qr = qrcode.QRCode(border=1)
        qr.add_data(url)
        qr.make(fit=True)
        qr.print_ascii(invert=True)
    except Exception as e:
        log(f"Impossible d'afficher le QR code : {e}", "warning")

def parse_args():
    parser = argparse.ArgumentParser(
        prog="sharepp-cli",
        description="Share++ CLI, serveur de partage de fichiers en réseau local en lignes de commandes.",
    )
    # Positional argument : mandatory, doesn't use --
    parser.add_argument("path", help="Répertoire à partager")
    # Optional arguments
    parser.add_argument("--port", type=int, default=8080, help="Port HTTP (défaut : 8080)")
    parser.add_argument("--secure", action="store_true", help="Active la protection par mot de passe")

    return parser.parse_args()

# Ask the user for a password until a valid one (>= 8 chars) is given.
# Returns the sha256 hash of the password.
def _prompt_password():
    while True:
        password = getpass.getpass("Mot de passe du partage (min. 8 car.) : ")
        if not password:
            log("Aucun mot de passe saisi.", "warning")
            continue
        if len(password) < 8:
            log("Le mot de passe doit faire au moins 8 caractères.", "warning")
            continue
        return hashlib.sha256(password.encode()).hexdigest()

async def _run(args):
    shared_path = str(Path(args.path).resolve())

    if not os.path.isdir(shared_path):
        log(f"Répertoire introuvable : {shared_path}", "error")
        sys.exit(1)

    password_hash = ""
    if args.secure:
        password_hash = _prompt_password()
        log("Protection activée.", "success")

    # Pass log argument to specify log function to use
    app = build_app(shared_path, password_hash, log)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", args.port)

    try:
        await site.start()
    except Exception as e:
        log(f"Impossible de démarrer le serveur sur le port {args.port} : {e}", "error")
        sys.exit(1)

    local_ip = network_controller.get_local_ip()
    url = f"http://{local_ip}:{args.port}"

    # Terminal User Interface
    print("\n")
    print("═" * 50)
    print(" Share++ CLI")
    print("═" * 50)
    print(f"  Répertoire : {shared_path}")
    print(f"  Adresse    : {url}")
    print(f"  Protection : {'✔️ activée' if password_hash else '❌ désactivée'}")
    print("═" * 50)
    print("\n")

    print_qr(url)
    print()
    log("Serveur démarré. Ctrl+C pour arrêter.", "success")

    # automatically shut down server after 900s (15min), also used to keep server alive
    try:
        while True:
            await asyncio.sleep(900)
    except Exception as e:
        log(f"Erreur du serveur de fichiers : {e}", "error")
    finally:
        await runner.cleanup()
        log("Serveur arrêté.", "info")


def run_cli():
    args = parse_args()
    try:
        asyncio.run(_run(args))
    except KeyboardInterrupt:
        print()
        log("Arrêt demandé par l'utilisateur.", "info")

if __name__ == "__main__":
    run_cli()