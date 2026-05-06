"""
network_controller.py

Author:  Nathan Filipowitz
Date:    2026-05-04
Purpose: Network detection utilities for local IP and Tailscale IP

References:
- socket.create_connection & socket.getaddrinfo : https://docs.python.org/3/library/socket.html
- subprocess.run           : https://docs.python.org/3/library/subprocess.html
- re.match (regex)         : https://docs.python.org/3/library/re.html
- Tailscale IP range (CGNAT 100.64.0.0/10) : https://tailscale.com/kb/1015/100.x-addresses
"""

import re
import socket
import subprocess

# Try to establish a connection with the address. Adds a 3 seconds delay to the the UI but allows to hide Tailscale when not available
def _is_reachable(ip, port, timeout: float = 3.0):
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except OSError:
        return False


def _detect_tailscale_ip():
    # Is tailscale active: "tailscale status" output
    try:
        status = subprocess.run(
            ["tailscale", "status"],
            capture_output=True, text=True, timeout=3
        )
        if status.returncode != 0:
            return None

        # get tailscale ip for this machine in IPv4
        result = subprocess.run(
            ["tailscale", "ip", "--4"],
            capture_output=True, text=True, timeout=3
        )
        ip = result.stdout.strip()
        if ip and re.match(r"^100\.(6[4-9]|[7-9]\d|1[0-1]\d|12[0-7])\.\d{1,3}\.\d{1,3}$", ip):
            return ip

    except Exception:
        pass

    return None


def get_tailscale_ip(port):
    ip = _detect_tailscale_ip()
    if ip is None:
        return None
    if not _is_reachable(ip, port):
        return None
    return ip


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return None
    finally:
        s.close()

# Get hotspot ip if it exists, else returns None
def get_hotspot_ip():
    if platform.system() != "Windows":
        return None
    try:
        # Retrieve all ip adresses, created ip seems to always start with 192.168.137.xx
        hostname = socket.gethostname()
        all_ips = socket.getaddrinfo(hostname, None, socket.AF_INET)
        for info in all_ips:
            ip = info[4][0]
            if ip.startswith("192.168.137."):
                return ip
    except Exception as e:
        print(f"Erreur lors de la réception de l'adresse IP du hotspot: {e}")
    return None
