"""
download_view.py

Author:  Nathan Filipowitz
Date:    2026-05-12
Purpose: HTML page generation for the download interface. style and script are served as separate static files from /static/.
"""

import os
import datetime
from pathlib import Path

# known file extensions, to append a specific color and icon in download page
# svg icons are taken from feathericons.com github repo: https://github.com/feathericons/feather/blame/main/icons/folder.svg
FILE_TYPES = [
    {
        "extensions": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp"],
        "color": "#4ade80",
        "icon": (
            '<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>'
            '<polyline points="9 22 9 12 15 12 15 22"/>'
        ),
    },
    {
        "extensions": [".mp4", ".mov", ".avi", ".mkv", ".webm"],
        "color": "#f472b6",
        "icon": (
            '<polygon points="23 7 16 12 23 17 23 7"/>'
            '<rect x="1" y="5" width="15" height="14" rx="2" ry="2"/>'
        ),
    },
    {
        "extensions": [".mp3", ".wav", ".flac", ".ogg", ".m4a"],
        "color": "#c084fc",
        "icon": (
            '<path d="M9 18V5l12-2v13"/>'
            '<circle cx="6" cy="18" r="3"/>'
            '<circle cx="18" cy="16" r="3"/>'
        ),
    },
    {
        "extensions": [".pdf"],
        "color": "#f87171",
        "icon": (
            '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>'
            '<polyline points="14 2 14 8 20 8"/>'
            '<line x1="16" y1="13" x2="8" y2="13"/>'
            '<line x1="16" y1="17" x2="8" y2="17"/>'
        ),
    },
    {
        "extensions": [".doc", ".docx", ".odt", ".txt", ".md"],
        "color": "#60a5fa",
        "icon": (
            '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>'
            '<polyline points="14 2 14 8 20 8"/>'
            '<line x1="16" y1="13" x2="8" y2="13"/>'
        ),
    },
    {
        "extensions": [".xls", ".xlsx", ".ods", ".csv"],
        "color": "#34d399",
        "icon": (
            '<rect x="3" y="3" width="18" height="18" rx="2"/>'
            '<path d="M3 9h18M3 15h18M9 3v18"/>'
        ),
    },
    {
        "extensions": [".zip", ".rar", ".tar", ".gz", ".7z"],
        "color": "#fbbf24",
        "icon": (
            '<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0'
            'l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0'
            'l7-4A2 2 0 0 0 21 16z"/>'
        ),
    },
    {
        "extensions": [".py", ".js", ".ts", ".html", ".css", ".json", ".sh", ".c", ".cpp"],
        "color": "#a78bfa",
        "icon": (
            '<polyline points="16 18 22 12 16 6"/>'
            '<polyline points="8 6 2 12 8 18"/>'
        ),
    },
]

# fallback if no extension match
ICON_FOLDER = {
    "color": "#fb923c",
    "icon": '<path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>',
}
ICON_UNKNOWN = {
    "color": "#94a3b8",
    "icon": (
        '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>'
        '<polyline points="14 2 14 8 20 8"/>'
    ),
}

# browse through FILE_TYPES to get corresponding color and icon to build SVG
def _file_icon(filename):
    extension = Path(filename).suffix.lower()

    # no extension = folder
    if extension == "":
        return ICON_FOLDER["color"], ICON_FOLDER["icon"]

    # browse FILE_TYPES
    for file_type in FILE_TYPES:
        if extension in file_type["extensions"]:
            return file_type["color"], file_type["icon"]

    # Fallback generic icon
    return ICON_UNKNOWN["color"], ICON_UNKNOWN["icon"]

# Returns file size in ready to read format
def _format_size(path):
    try:
        if os.path.isdir(path):
            return "dossier"
        size = os.path.getsize(path)
        for unit in ("o", "Ko", "Mo", "Go"):
            if size < 1024:
                return f"{size:.0f} {unit}"
            size /= 1024
        return f"{size:.1f} To"
    except OSError:
        return "—"

# Return file's last modification date
def _format_date(path):
    try:
        ts = os.path.getmtime(path)
        return datetime.datetime.fromtimestamp(ts).strftime("%d %b %Y")
    except OSError:
        return "—"

# append all to create a single line html <svg> tag
def _make_icon_svg(color, paths):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"> {paths}</svg>'
    )


_DL_ICON = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" '
    'viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>'
    '<polyline points="7 10 12 15 17 10"/>'
    '<line x1="12" y1="15" x2="12" y2="3"/>'
    '</svg>'
)

# Main Download Page
# Generate html for download page. Shared_path should be absolute for os.path.getsize and getmtime
def generate_html(files, shared_path=""):
    items_html = ""
    for f in files:
        full = os.path.join(shared_path, f) if shared_path else f
        size = _format_size(full)
        date = _format_date(full)
        color, paths = _file_icon(f)
        icon_svg = _make_icon_svg(color, paths)
        is_folder = os.path.isdir(full)
        is_hidden = f.startswith(".")
        hidden_class = " hidden-file" if is_hidden else ""
        dl_label = "Télécharger (.zip)" if is_folder else "Télécharger"

        items_html += f"""
    <div class="file-card{hidden_class}" data-name="{f}">
      <input class="cb" type="checkbox" value="{f}" aria-label="Sélectionner {f}">
      <div class="file-icon">{icon_svg}</div>
      <div class="file-info">
        <span class="file-name">{f}</span>
        <span class="file-meta">{size}&nbsp;·&nbsp;{date}</span>
      </div>
      <a href="/{f}" class="dl-btn" download>
        {_DL_ICON} {dl_label}
      </a>
    </div>"""

    count = len(files)
    label_count = f"{count} fichier{'s' if count > 1 else ''}"

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Share++</title>
  <link rel="stylesheet" href="/static/download.css">
</head>
<body>
  <header>
    <div class="logo">Share++</div>
    <span class="count-badge">{label_count}</span>
  </header>
 
  <button class="bulk-btn" id="bulk-btn">
    {_DL_ICON} Télécharger la sélection (<span id="bulk-count">0</span>)
  </button>
 
  <div class="file-list">
    {items_html if files else '<p class="empty">Aucun fichier disponible.</p>'}
  </div>
 
  <script src="/static/download.js"></script>
</body>
</html>"""


# Authentification Page
# Generate password login page with no username.
def generate_auth_html(error=False):
    error_block = (
        '<p class="error-msg">Mot de passe incorrect. Veuillez réessayer.</p>'
        if error else ""
    )
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Share++ Authentification</title>
  <link rel="stylesheet" href="/static/download.css">
</head>
<body class="auth-page">
  <div class="auth-card">
    <div class="auth-logo">Share++</div>
    <div class="auth-sub">Ce partage est protégé par un mot de passe.</div>
    <form method="POST">
      <label for="pwd">Mot de passe</label>
      <input id="pwd" type="password" name="password" placeholder="••••••••" autofocus required>
      {error_block}
      <button type="submit" class="submit-btn">Accéder au partage</button>
    </form>
  </div>
</body>
</html>"""