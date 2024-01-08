[![Licence-MIT](https://img.shields.io/badge/Licence-MIT-blue)](https://github.com/Dylanolivro/Twitter_scrapping/blob/main/LICENSE)

---

[![Python](https://img.shields.io/badge/Python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/)
[![Selenium](https://img.shields.io/badge/Selenium-43B02A?style=for-the-badge&logo=selenium&logoColor=white)](https://www.selenium.dev/)

# Twitter/X Crawler
Ce projet est un crawler pour Twitter/X qui offre la possibilité de récupérer les tweets d'une liste de compte.

Il propose plusieurs modes :

- **Classique** : Récupère les 10 derniers tweets postés dans les 24 dernières heures.
- **Complet** : Récupère les 10 derniers tweets sans tenir compte de la date de publication.

**Note importante** : Twitter/X impose une limite de scrapping pour un compte par jour, qui est d’environ 2500 tweets.

En plus du script pour le scrapping, le dossier contient deux autres scripts qui permettent de **convertir les usernames en id** et inversement.

## Prérequis

- python 3.11.5
- pip 23.2.1
- selenium 4.16.0

## Installation

Ce projet utilise Selenium. Vous pouvez l'installer avec le gestionnaire de paquets [pip](https://pip.pypa.io/en/stable/).

Pour installer Selenium, exécutez la commande suivante dans votre terminal :

```bash
pip install selenium==4.16
pip install pymysql
```

Pour plus d'informations sur l'installation et l'utilisation de Selenium, consultez la [documentation officielle](https://selenium-python.readthedocs.io/installation.html).

Créez un fichier **JSON** dans le répertoire `./Ressources/Json/` et nommez-le `twitter_accounts.json`. Ce fichier doit être structuré comme suit :
```
[
    {
        "email": "exemple@gmail.com",
        "pseudo": "Exemple01",
        "password": "azerty",
        "lastCrawl": ""
    },
    {
        "email": "secondExemple@gmail.com",
        "pseudo": "secondExemple02",
        "password": "azerty",
        "lastCrawl": "",
    }
]
```

## Structure du projet

```
.
├── Classes/
│   ├── __init__.py
│   ├── Config.py
│   ├── Mysql.py
│   └── Selenium.py
├── Ressources/
│   ├── Json/
│   │   ├── profiles.json
│   │   └── selenium_xpaths.json
│   └── crawl_twitter.sql
└── Scripts/
    ├── add_profiles_in_db.py
    ├── crawl.py
    ├── id_to_username.py
    └── username_to_id.py
```

## 🔗 Links

[![portfolio](https://img.shields.io/badge/my_portfolio-000?style=for-the-badge&logo=ko-fi&logoColor=white)](https://dylan-olivro.students-laplateforme.io/)