"""
download_view.py

Author:  Nathan Filipowitz
Date:    2026-03-02
Purpose: HTML page generation from files to display all downloadeable files to the download interface, and adding hypertext to each files.
"""

def generate_login_page(error=False):
    error_msg = '<p style="color: red;">Mot de passe incorrect</p>' if error else ""
    return f"""
    <!DOCTYPE html>
    <html>
    <head><title>Share++ - Login</title></head>
    <body style="font-family: sans-serif; display: flex; justify-content: center; padding-top: 100px; background: #f0f2f5;">
        <form method="post" action="/login" style="background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h2>Accès Protégé</h2>
            {error_msg}
            <input type="password" name="password" placeholder="Mot de passe" required style="padding: 10px; width: 200px; margin-bottom: 10px;"><br>
            <button type="submit" style="padding: 10px 20px; background: #0078d4; color: white; border: none; border-radius: 4px; cursor: pointer;">Entrer</button>
        </form>
    </body>
    </html>
    """

def generate_html(files):
    # Create a list of files, and make them redirect to the download page by adding the href parameter.
    items = ""
    for f in files:
        items += f"""
        <div class="file-card">
            <span class="file-name">{f}</span>
            <a href="/{f}" class="download-btn">⬇️</a>
        </div>
        """
    return f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <title>Share++ - Partage</title>
        <meta charset="utf-8">
        <style>
            body {{ 
                font-family: 'Segoe UI', sans-serif; 
                background-color: #f5f5f5; 
                margin: 0; padding: 20px; 
            }}
            h1 {{ color: #333; text-align: center; }}
            .file-list {{ max-width: 500px; margin: 0 auto; }}
            .file-card {{
                background: white;
                padding: 15px;
                margin-bottom: 10px;
                border-radius: 8px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .file-name {{ font-weight: 500; color: #444; }}
            .download-btn {{
                text-decoration: none;
                background: #0078d4;
                color: white;
                padding: 8px 12px;
                border-radius: 5px;
            }}
        </style>
    </head>
    <body>
        <h1>Share++</h1>
        <div class="file-list">
            {items}
        </div>
    </body>
    </html>
    """
