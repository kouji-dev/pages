# 🧪 Commandes de Tests

## Backend (FastAPI/Python)

### Tests unitaires et intégration
```bash
cd services/api

# Tous les tests
poetry run pytest

# Avec couverture de code
poetry run pytest --cov=src --cov-report=html

# Tests unitaires seulement
poetry run pytest tests/unit/

# Tests d'intégration seulement
poetry run pytest tests/integration/

# Tests fonctionnels (E2E)
export TEST_DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5433/pages_test"
poetry run pytest tests/functional/

# Fichier spécifique
poetry run pytest tests/unit/test_security.py

# Test spécifique
poetry run pytest tests/unit/test_security.py::TestBcryptPasswordService::test_hash_password

# Mode verbeux
poetry run pytest -v

# Arrêter au premier échec
poetry run pytest -x
```

### Commandes GitHub CI (qualité de code)

```bash
cd services/api

# 1. Vérification du formatage avec Black
poetry run black --check .

# Formater automatiquement
poetry run black .

# 2. Linting avec Ruff
poetry run ruff check .

# Corriger automatiquement les erreurs simples
poetry run ruff check --fix .

# 3. Vérification de types avec MyPy
poetry run mypy src

# 4. Tests unitaires avec couverture
export TEST_DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5433/pages_test"
poetry run pytest tests/unit/ -v --cov=src --cov-report=xml --cov-report=html --cov-report=term

# 5. Tests d'intégration avec couverture
export TEST_DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5433/pages_test"
poetry run pytest tests/integration/ -v --cov=src --cov-report=xml --cov-report=html --cov-report=term --cov-append

# 6. Tests fonctionnels (E2E)
export TEST_DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5433/pages_test"
poetry run pytest tests/functional/ -v

# 7. Scan de sécurité avec Bandit
poetry run bandit -r src

# Générer un rapport JSON
poetry run bandit -r src -f json -o bandit-report.json

# 8. Vérification des dépendances avec Safety
poetry export --without-hashes -f requirements.txt -o requirements.txt
poetry run safety check --file requirements.txt

# 9. Vérification des migrations Alembic
poetry run alembic current
poetry run alembic upgrade head
poetry run alembic downgrade -1
poetry run alembic upgrade head

# 10. Toutes les vérifications CI en une fois
poetry run black --check . && \
poetry run ruff check . && \
poetry run mypy src && \
export TEST_DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5433/pages_test" && \
poetry run pytest tests/unit/ -v --cov=src --cov-report=term && \
poetry run pytest tests/integration/ -v --cov=src --cov-report=term --cov-append && \
poetry run pytest tests/functional/ -v
```

## Frontend (Angular)

```bash
# Tous les tests
cd clients/app1
pnpm test

# Avec watch mode
pnpm test --watch

# Tests d'une suite spécifique
pnpm test --include='**/demo.spec.ts'
```

## Docker

```bash
# Backend dans Docker
docker-compose -f docker-compose.dev.yml exec api poetry run pytest

# Frontend dans Docker
docker-compose -f docker-compose.dev.yml exec app1 pnpm test
```
