# Twitter/X Crawler
Ce projet est un crawler pour Twitter/X qui offre la possibilité de récupérer les tweets d'un compte spécifique, d'un hashtag ou simplement d'une requête dans la barre de recherche.

Il propose plusieurs modes :

- **Classique** : Récupère les 10 derniers tweets postés dans les 24 dernières heures.
- **Complet** : Récupère les 10 derniers tweets sans tenir compte de la date de publication.

**Note importante** : Le scrapping est possible jusqu’à 2500 tweets par jour et par compte.

En plus du script pour le scrapping, le dossier contient deux autres scripts qui permettent de **convertir les usernames en id** et inversement.

## Prérequis

- Python 3.11.5
- pip 23.2.1

## Installation

Ce projet utilise Selenium. Vous pouvez l'installer avec le gestionnaire de paquets [pip](https://pip.pypa.io/en/stable/).

Pour installer Selenium, exécutez la commande suivante dans votre terminal :

```bash
pip install selenium
```

Pour plus d'informations sur l'installation et l'utilisation de Selenium, consultez la [documentation officielle](https://selenium-python.readthedocs.io/installation.html).