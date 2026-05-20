# Share++

Share++ est un outil de transfert de fichiers et de répertoires entre appareils d'un même réseau local. Il permet d'éviter de passer par Internet pour partager des documents entre ses appareils (mobiles, ordinateurs...) sans recours à des services tiers (OneDrive, WeTransfer, clé USB).

## Fonctionnalités

- **Partage local** : sélectionnez un dossier, démarrez le serveur, scannez le QR code depuis n'importe quel appareil du réseau.
- **Point d'accès Wi-Fi ad hoc** : créez un réseau Wi-Fi temporaire directement depuis l'application pour connecter un smartphone hors réseau.
- **Intégration Tailscale** : partagez à distance sans configuration de port grâce à la détection automatique de Tailscale.
- **Protection par mot de passe** : page d'authentification HTML avec cookie de session signé (HMAC-SHA256).
- **Journalisation persistante** : historique des connexions et téléchargements avec identification du type d'appareil (User-Agent parsing).
- **Interface web responsive** : icônes par type de fichier, taille, date, téléchargement multiple (bulk download).
- **Mode CLI** : serveur headless en ligne de commande avec QR code ASCII et logs en temps réel.
- **Menu contextuel Windows** : lancez un partage directement depuis l'Explorateur via clic droit sur un dossier. (! Non fonctionnel sur la dernière version)
- **CI/CD automatisé** : build et publication des releases via GitHub Actions à chaque tag de version.

## Installation rapide

1. Rendez-vous sur la page [**Releases**](https://github.com/NathanFilipowitz/Sharepp/releases) du dépôt.
2. Téléchargez `SharePlusPlus_Setup_X.X.X.exe`.
3. Exécutez l'installateur et suivez l'assistant.

Pour les instructions détaillées, consultez le [Manuel d'installation](06_Guides/guide_installation.md).

## Utilisation

```
# GUI : lancer Share++ depuis le bureau ou le menu Démarrer

# CLI :
sharepp-cli.exe <chemin> [--port PORT] [--secure]
```

Exemples :

```bash
sharepp-cli.exe C:\Documents
sharepp-cli.exe C:\partage --port 3001 --secure
```

Pour les instructions complètes, consultez le [Manuel d'utilisation](06_Guides/guide_utilisateur.md).

## Arborescence du projet

```plaintext
Sharepp/
├── .github/
│   └── workflows/
│       └── build-release.yml
├── docs/
│   ├── 01_Gestion_de_projet/
│   │   ├── A01_Justification_agile.md
│   │   └── A04_Planning_Initial_Gantt.pdf
│   ├── 02_Journaux/
│   │   ├── journal_de_bord.pdf
│   │   ├── journal_de_travail.pdf
│   │   ├── journal_de_travail_Nathan_Filipowitz.ods
│   │   └── récapitulatif.pdf
│   ├── 03_Analyse_Conception/
│   │   └── Cahier_des_charges.pdf
│   ├── 04_Realisation/
│   │   ├── Dossier_de_projet.odt
│   │   └── Dossier_de_projet.pdf
│   ├── 05_Tests/
│   │   ├── Journal_de_test.pdf
│   │   ├── Plan_de_test.ods
│   │   └── Plan_de_test.pdf
│   ├── 06_Guides/
│   │   ├── images/
│   │   ├── couverture.txt
│   │   ├── guide_installation.md
│   │   ├── guide_installation.pdf
│   │   ├── guide_utilisateur.md
│   │   └── guide_utilisateur.pdf
│   ├── 07_Schémas/
│   │   ├── UML.pdf
│   │   ├── UML.png
│   │   ├── UML.puml
│   │   ├── UseCase.puml
│   │   ├── comparaison_planning.pdf
│   │   ├── maquette_app.pdf
│   │   ├── maquette_download_page.pdf
│   │   └── useCase.png
│   ├── archives/
│   │   ├── Sprint_planning.md
│   │   └── couverture.txt
│   ├── reseau.drawio
│   ├── schema_reseau.drawio
│   └── schema_reseau.png
├── src/
│   ├── assets/
│   │   ├── icons/
│   │   │   ├── app_icon_compressed.ico
│   │   │   └── app_icon_compressed.svg
│   │   └── icon_windows.ico
│   ├── controllers/
│   │   ├── app_controller.py
│   │   ├── hotspot_controller.py
│   │   ├── network_controller.py
│   │   └── server_controller.py
│   ├── models/
│   │   └── model.py
│   ├── tests/
│   │   ├── test_controller.py
│   │   ├── test_model.py
│   │   └── test_v2.py
│   ├── views/
│   │   ├── static/
│   │   │   ├── download.css
│   │   │   └── download.js
│   │   ├── download_view.py
│   │   └── view.py
│   ├── cli.py
│   └── main.py
├── .gitignore
├── LICENSE
├── README.md
├── pyproject.toml
├── requirements.txt
└── setup.iss
```

## Lancer en développement

```bash
git clone https://github.com/NathanFilipowitz/Sharepp.git
cd Sharepp
pip install -r requirements.txt
python src/main.py
```

Argument optionnel pour simuler une ouverture depuis le menu contextuel :

```bash
python src/main.py "C:\chemin\dossier"
```

## Tests

```bash
cd src
pytest tests/
```

## Licence

[MIT](LICENSE) Nathan Filipowitz, 2026