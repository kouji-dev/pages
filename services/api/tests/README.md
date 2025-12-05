# Tests d'intégration

## Configuration

Les tests d'intégration nécessitent une base de données PostgreSQL de test. Un Docker Compose est fourni pour démarrer automatiquement cette base de données.

### Démarrage de la base de données de test

```bash
# Démarrer la base de données de test
docker-compose -f docker-compose.test.yml up -d

# Vérifier que la base de données est prête
docker-compose -f docker-compose.test.yml ps
```

### Exécution des tests

```bash
# Tous les tests
poetry run pytest

# Tests d'intégration uniquement
poetry run pytest tests/integration/

# Tests unitaires uniquement
poetry run pytest tests/unit/
```

### Arrêt de la base de données de test

```bash
docker-compose -f docker-compose.test.yml down
```

## Configuration des tests

Les tests utilisent une base de données PostgreSQL séparée configurée via `TEST_DATABASE_URL` (par défaut : `postgresql+asyncpg://postgres:postgres@localhost:5434/pages_test`).

Les fixtures gèrent automatiquement :
- La création/suppression des tables
- L'isolation des tests via des transactions avec rollback
- Le remplacement des dépendances FastAPI pour utiliser la session de test

