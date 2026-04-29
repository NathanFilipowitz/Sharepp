"""
hotspot_controller.py
 
Author:  Nathan Filipowitz
Date:    2026-04-28
Purpose: Controller for creating a Wi-Fi access point with netsh wlan hostednetwork. Works only on Windows. 
         Also usable on Linux for testing UI (becomes a mock).
"""
# AI USE: AI (Gemini) was partially used in this file — mostly for error handling 
# and the Windows-specific admin/privilege constraints (CREATE_NO_WINDOW flag, 
# HKEY_CURRENT_USER registry scope). See execute_command() for details.
import subprocess
import platform

def get_hotspot_status():
    # Check if hotspot is active
    if platform.system() == "Windows":
        ok, output = execute_command("netsh wlan show hostednetwork")
        # check in results for french and english
        is_running = "Status  : Started" in output or "État  : Démarré" in output
        return {"running": is_running}
    return {"running": False}

# AI USE: Gemini taught me about creation_flags in windows and implemented this function to prevent terminal flashes when executing shell commands (normally just using subprocess)
def execute_command(command):
    try:
        # CREATE_NO_WINDOW (0x08000000) prevent terminal flashing
        creation_flag = 0x08000000 if platform.system() == "Windows" else 0
        result = subprocess.run(
            command, shell=True, check=True, text=True, capture_output=True, creationflags=creation_flag
        )
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip() or str(e)

def setup_and_start(ssid, password):
    if len(password) < 8: return False, "Le mot de passe doit faire 8 caractères."
    if platform.system() == "Windows":
        # Configuration
        cmd_config = f'netsh wlan set hostednetwork mode=allow ssid="{ssid}" key="{password}"'
        ok, msg = execute_command(cmd_config)
        if not ok: return False, f"Erreur de configuration: {msg}"
        # Access Point Creation
        return execute_command("netsh wlan start hostednetwork")
    
    return False, "OS non supporté"

def stop_hotspot():
    if platform.system() == "Windows":
        return execute_command("netsh wlan stop hostednetwork")
    return False, "OS non supporté"