# Exécution des commandes CI en local

Ce document explique comment exécuter les mêmes vérifications que GitHub Actions en local.

## 🚀 Méthode rapide : Script automatique

```bash
cd services/api
./scripts/run_ci_local.sh
```

## 📋 Commandes manuelles

### 1. Lint & Format Check

```bash
cd services/api

# Vérification du formatage (Black)
poetry run black --check .

# Si des fichiers doivent être formatés, exécutez :
poetry run black .

# Linting (Ruff)
poetry run ruff check .

# Correction automatique des erreurs Ruff
poetry run ruff check --fix .

# Vérification des types (MyPy)
poetry run mypy src
```

### 2. Tests unitaires

```bash
cd services/api

# Tests unitaires avec coverage
poetry run pytest tests/unit/ -v \
  --cov=src \
  --cov-report=xml \
  --cov-report=html \
  --cov-report=term
```

**Rapports générés :**
- `coverage.xml` - Pour Codecov
- `htmlcov/index.html` - Rapport HTML (ouvrir dans le navigateur)

### 3. Tests d'intégration

**⚠️ Prérequis :** PostgreSQL doit être en cours d'exécution

```bash
cd services/api

# Configurer la variable d'environnement
export TEST_DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/pages_test"

# Tests d'intégration avec coverage
poetry run pytest tests/integration/ -v \
  --cov=src \
  --cov-report=xml \
  --cov-report=html \
  --cov-report=term \
  --cov-append
```

**Note :** `--cov-append` ajoute la couverture aux tests unitaires.

### 4. Security Scanning

```bash
cd services/api

# Export des dépendances
poetry export --without-hashes -f requirements.txt -o requirements.txt

# Vérification des vulnérabilités (Safety)
poetry run safety check --file requirements.txt

# Analyse de sécurité (Bandit)
poetry run bandit -r src -f json -o bandit-report.json
poetry run bandit -r src
```

### 5. Vérification des migrations

**⚠️ Prérequis :** PostgreSQL doit être en cours d'exécution

```bash
cd services/api

# Configurer la variable d'environnement
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/pages_test"

# Vérifier l'état actuel
poetry run alembic current

# Tester les migrations (downgrade puis upgrade)
poetry run alembic downgrade -1
poetry run alembic upgrade head
```

## 🔧 Configuration requise

### Variables d'environnement

Pour les tests d'intégration et les migrations, configurez :

```bash
export TEST_DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/pages_test"
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/pages_test"
```

### Base de données PostgreSQL

Assurez-vous que PostgreSQL est en cours d'exécution :

```bash
# Avec Docker Compose
docker-compose up -d postgres

# Ou avec PostgreSQL local
# Créer la base de données de test
createdb pages_test
```

## 📊 Ordre d'exécution recommandé

1. **Lint & Format** (rapide, ~30 secondes)
2. **Tests unitaires** (rapide, ~1-2 minutes)
3. **Tests d'intégration** (nécessite PostgreSQL, ~3-5 minutes)
4. **Security** (rapide, ~1 minute)
5. **Migrations** (nécessite PostgreSQL, ~30 secondes)

## 🎯 Commandes rapides

### Toutes les vérifications (sans tests d'intégration)
```bash
cd services/api && \
poetry run black --check . && \
poetry run ruff check . && \
poetry run mypy src && \
poetry run pytest tests/unit/ -v --cov=src --cov-report=term
```

### Tests uniquement
```bash
cd services/api && \
poetry run pytest tests/ -v
```

### Lint uniquement
```bash
cd services/api && \
poetry run black --check . && \
poetry run ruff check . && \
poetry run mypy src
```

## 📝 Notes

- Les erreurs MyPy dans `image_service.py` et `list_users.py` sont connues et non bloquantes
- Les tests d'intégration nécessitent une base de données PostgreSQL
- Le script `run_ci_local.sh` exécute toutes les vérifications dans l'ordre
- Les rapports de couverture sont générés dans `htmlcov/` et `coverage.xml`

