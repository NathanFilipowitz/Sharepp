"""
download_view.py

Author:  Nathan Filipowitz
Date:    2026-03-02
Purpose: HTML page generation from files to display all downloadeable files to the download interface, and adding hypertext to each files.
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
