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

# Fichier spécifique
poetry run pytest tests/unit/test_security.py

# Test spécifique
poetry run pytest tests/unit/test_security.py::TestBcryptPasswordService::test_hash_password

# Mode verbeux
poetry run pytest -v

# Arrêter au premier échec
poetry run pytest -x
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
