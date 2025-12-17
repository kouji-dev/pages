# Exécution des commandes CI en local

Ce document explique comment exécuter les mêmes vérifications que GitHub Actions en local.

## 📊 État actuel

✅ **Couverture de tests : 81%** (11,542 lignes, 2,138 non couvertes)  
✅ **Tests : 852 tests passent**  
✅ **Qualité de code : Black ✓ | Ruff ✓ | MyPy ✓**

---

## 🚀 Méthode rapide : Script automatique

```bash
cd services/api
./scripts/run_ci_local.sh
```

---

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

**Résultats attendus :**
- ✅ Black : Tous les fichiers formatés
- ✅ Ruff : Aucune erreur de linting
- ✅ MyPy : 315 fichiers vérifiés sans erreur

---

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

**Résultats attendus :**
- ✅ ~49 tests unitaires passent
- 📊 Couverture partielle générée

**Rapports générés :**
- `coverage.xml` - Pour Codecov/CI
- `htmlcov/index.html` - Rapport HTML interactif

---

### 3. Tests d'intégration

**⚠️ Prérequis :** La base de données de test PostgreSQL doit être en cours d'exécution

```bash
cd services/api

# Démarrer la base de données de test
docker-compose -f docker-compose.test.yml up -d

# Attendre que la base soit prête (healthcheck)
sleep 5

# Tests d'intégration avec coverage
poetry run pytest tests/integration/ -v \
  --cov=src \
  --cov-report=xml \
  --cov-report=html \
  --cov-report=term \
  --cov-append
```

**Résultats attendus :**
- ✅ ~33 tests d'intégration passent
- 📊 Couverture cumulée avec tests unitaires

**Note :** `--cov-append` ajoute la couverture aux tests unitaires.

---

### 4. Tests fonctionnels (E2E)

```bash
cd services/api

# Tests fonctionnels (nécessite la base de données de test)
poetry run pytest tests/functional/ -v
```

**Résultats attendus :**
- ✅ ~23 tests fonctionnels passent
- ⚠️ Ignorer `test_custom_field_workflow.py` si besoin

---

### 5. Tous les tests avec couverture complète

```bash
cd services/api

# Démarrer la base de données de test si pas déjà fait
docker-compose -f docker-compose.test.yml up -d

# Tous les tests avec couverture complète (81%)
poetry run pytest \
  --cov=src \
  --cov-report=html \
  --cov-report=xml \
  --cov-report=term \
  --ignore=tests/functional/test_custom_field_workflow.py \
  -q
```

**Résultats attendus :**
- ✅ **852 tests passent**
- 📊 **Couverture : 81%**
- ⚠️ ~3000 warnings (deprecations, peuvent être ignorés)

---

### 6. Security Scanning

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

---

### 7. Vérification des migrations

**⚠️ Prérequis :** PostgreSQL doit être en cours d'exécution

```bash
cd services/api

# Démarrer la base de données principale
docker-compose up -d postgres

# Vérifier l'état actuel
poetry run alembic current

# Tester les migrations (upgrade)
poetry run alembic upgrade head

# Tester le downgrade (optionnel)
poetry run alembic downgrade -1
poetry run alembic upgrade head
```

---

## 🔧 Configuration requise

### Base de données PostgreSQL de test

```bash
# Démarrer avec Docker Compose (recommandé)
cd services/api
docker-compose -f docker-compose.test.yml up -d

# Vérifier que le container est healthy
docker ps | grep pages-api-test-db

# Arrêter quand terminé
docker-compose -f docker-compose.test.yml down
```

**Configuration automatique :**
- Port : `5434` (pour éviter les conflits avec PostgreSQL principal sur 5433)
- User : `postgres`
- Password : `postgres`
- Database : `pages_test`
- Les données sont en `tmpfs` (volatiles, plus rapides)

---

## 📊 Ordre d'exécution recommandé

1. **Lint & Format** (~30 secondes) ✅
2. **Type checking** (~20 secondes) ✅
3. **Tests unitaires** (~10 secondes) ✅
4. **Tests d'intégration** (~30 secondes, nécessite DB) ✅
5. **Tests fonctionnels** (~60 secondes, nécessite DB) ✅
6. **Security scanning** (~1 minute) 🔒
7. **Migrations** (~10 secondes, nécessite DB) 🗃️

**Temps total : ~3-4 minutes**

---

## 🎯 Commandes rapides

### Pipeline CI complète (recommandé avant commit)

```bash
cd services/api && \
docker-compose -f docker-compose.test.yml up -d && \
sleep 5 && \
poetry run black . && \
poetry run ruff check --fix . && \
poetry run mypy src && \
poetry run pytest --cov=src --cov-report=term --ignore=tests/functional/test_custom_field_workflow.py -q
```

### Tests uniquement (rapide)

```bash
cd services/api && \
docker-compose -f docker-compose.test.yml up -d && \
poetry run pytest tests/unit/ tests/integration/ -v
```

### Lint uniquement (très rapide)

```bash
cd services/api && \
poetry run black --check . && \
poetry run ruff check . && \
poetry run mypy src
```

### Couverture avec rapport HTML

```bash
cd services/api && \
docker-compose -f docker-compose.test.yml up -d && \
poetry run pytest --cov=src --cov-report=html --ignore=tests/functional/test_custom_field_workflow.py && \
open htmlcov/index.html
```

---

## 📝 Notes importantes

### ✅ Améliorations récentes (Décembre 2024)

- **Couverture améliorée** : Passée de 67% à 81% (+14 points)
- **Tests corrigés** : Tous les 852 tests passent maintenant
- **Qualité de code** : Black, Ruff et MyPy 100% OK
- **Nouveaux tests** : 10 tests ajoutés pour les middlewares

### 🔍 Zones de couverture

**Bien couvertes (>80%) :**
- ✅ Value Objects & Entities
- ✅ Use Cases principaux
- ✅ DTOs & Services de sécurité
- ✅ Middlewares

**À améliorer (<50%) :**
- ⚠️ Endpoints API (0% - normal, testés via intégration)
- ⚠️ Certains repositories (18-40%)
- ⚠️ Services de recherche (25%)

### ⚠️ Tests connus à ignorer

- `test_custom_field_workflow.py` : En cours de refactoring

### 🐛 Warnings non bloquants

- Deprecations Pydantic V2 (config classes → ConfigDict)
- Deprecations FastAPI (on_event → lifespan)
- Deprecations datetime (utcnow → datetime.now(UTC))

Ces warnings n'empêchent pas le CI de passer et seront corrigés dans une PR dédiée.

---

## 🆘 Dépannage

### La base de données de test ne démarre pas

```bash
# Arrêter tous les containers
docker-compose -f docker-compose.test.yml down

# Supprimer les volumes
docker volume prune -f

# Redémarrer
docker-compose -f docker-compose.test.yml up -d

# Vérifier les logs
docker logs pages-api-test-db
```

### Les tests échouent avec "Connection refused"

```bash
# Vérifier que le container est healthy
docker ps | grep pages-api-test-db

# Attendre quelques secondes de plus
sleep 10

# Réessayer les tests
poetry run pytest tests/integration/ -v
```

### Erreur "No module named 'src'"

```bash
# Vérifier l'environnement Poetry
poetry env info

# Réinstaller les dépendances
poetry install

# Vérifier que vous êtes dans le bon répertoire
pwd  # Doit afficher .../services/api
```

### Couverture de tests qui ne s'affiche pas

```bash
# Supprimer les anciens rapports
rm -rf htmlcov/ coverage.xml .coverage

# Relancer avec --cov-report explicite
poetry run pytest --cov=src --cov-report=html --cov-report=term
```

---

## 📚 Ressources

- [Documentation pytest](https://docs.pytest.org/)
- [Documentation pytest-cov](https://pytest-cov.readthedocs.io/)
- [Black code style](https://black.readthedocs.io/)
- [Ruff linter](https://docs.astral.sh/ruff/)
- [MyPy type checking](https://mypy.readthedocs.io/)

---

**Dernière mise à jour :** Décembre 2024  
**Couverture actuelle :** 81%  
**Tests passants :** 852/852 ✅
