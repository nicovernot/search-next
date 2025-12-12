# Playwright CI image et commandes

Ce fichier décrit l'image Playwright et les cibles Make disponibles pour exécuter les tests E2E du frontend de façon reproductible (local et CI).

But
- L'image fournie permet d'éviter d'installer Node/Playwright à chaque run.
- Contient les navigateurs Playwright et Xvfb pour permettre les runs UI headful dans un conteneur.

Commandes Make utiles

- Construire l'image Playwright (une fois) :

```bash
make build-playwright-image
```

- Exécuter les tests headless dans l'image pré-construite (CI friendly) :

```bash
make test-front-ci-image
```

- Exécuter la UI (interface Playwright Test Runner) depuis l'image (expose le port 9323) :

```bash
make test-front-ci-ui-image
# puis ouvrez http://localhost:9323 dans votre navigateur
```

- Alternatives plus légères (sans construire d'image) :

```bash
# Installe les dépendances et lance les tests headless sur l'image officielle Playwright
make test-front-ci

# Lancer les tests headless localement (installe les dépendances dans front/)
make test-front
```

CI (exemple GitHub Actions)

Voici un exemple minimal pour GitHub Actions utilisant l'image Playwright que nous construisons :

```yaml
name: frontend-e2e
on: [push, pull_request]

jobs:
  e2e:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4
      - name: Build Playwright image
        run: make build-playwright-image
      - name: Run frontend E2E
        run: make test-front-ci-image
```

Remarques
- Mettre en cache les couches Docker ou le cache npm accélèrera les runs CI.
- Le mode UI (`test-front-ci-ui-image`) nécessite un navigateur et Xvfb — il fonctionne dans le conteneur mais a moins d'intérêt en CI. Préférer le mode headless pour les pipelines automatiques.
- Les rapports Playwright (HTML) peuvent être archivés comme artifacts CI ; adaptez la cible `make` pour copier le dossier `playwright-report` vers `/workdir` puis archivez-le.

