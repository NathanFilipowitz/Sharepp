# Sharepp
Share++ est un outil de transfert de fichiers et de répertoires entre appareils de même sous-réseau. Il permet entre autre d'éviter de passer par internet pour se partager des documents entres ses appareils (mobiles, ordinateurs...).
## Arborescence du projet
```plaintext
Sharepp/
├── src/
│   ├── main.py              # Point d'entrée de l'application
│   ├── models/
│   │   └── config_model.py  # Gestion du JSON et de la logique métier
│   ├── views/
│   │   ├── desktop_view.py  # Interface Flet (Windows)
│   │   └── web_view.py      # Template HTML pour aiohttp
│   └── controllers/
│       └── app_controller.py # Orchestrateur entre l'UI et le serveur
├── docs/                    # Dossier de projet et journaux
├── config.json              # Paramètres de l'application
├── requirements.txt         # Dépendances (flet, aiohttp, etc.)
└── README.md                # Instructions d'installation
```
## Installation et Lancement

1. **Cloner le dépôt** :
    ```bash
    git clone https://github.com/NathanFilipowitz/Sharepp.git
    cd Sharepp
    ```
2. **Installer les dépendances** :
    ```bash
    pip install -r requirements.txt
    ```
3. **Lancer l'application** :
    ```bash
    python src/main.py
    ```
    > Note : il est possible d'ajouter en argument le chemin du répertoire à partager afin de simuler une ouverture depuis le menu contextuel :
    python src/main.py "C:\chemin\dossier"
