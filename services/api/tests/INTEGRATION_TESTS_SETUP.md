# Configuration des Tests d'Intégration

## État Actuel

✅ **Base de données de test configurée**
- Docker Compose pour PostgreSQL de test (`docker-compose.test.yml`)
- Base de données sur le port 5434
- Configuration de test dans `src/infrastructure/config/test_settings.py`

✅ **Fixtures de base configurées**
- `test_engine`: Engine de base de données pour les tests
- `session`: Session avec rollback automatique pour isolation
- `client`: Client HTTP pour les tests

✅ **59 tests unitaires passent** - Tous les tests unitaires fonctionnent correctement

⚠️ **Tests d'intégration en cours de configuration**
- Infrastructure de base mise en place
- Problème restant: Rate limiting qui nécessite un Request object de Starlette
- Problème restant: Fixtures async avec event loops

## Problèmes Techniques Identifiés

### 1. Rate Limiting dans les Tests
Le décorateur `@limiter.limit()` nécessite un `Request` object de Starlette, pas celui de httpx. Solutions possibles:
- Utiliser `TestClient` de FastAPI au lieu de `AsyncClient` d'httpx
- Modifier le limiter pour être conditionnel dans les tests
- Créer une version des routes sans rate limiting pour les tests

### 2. Fixtures Async avec Event Loops
Certains tests ont des problèmes avec les event loops asyncio. Cela nécessite une meilleure gestion des fixtures async.

## Prochaines Étapes Recommandées

1. **Utiliser TestClient de FastAPI** au lieu d'AsyncClient pour simplifier
2. **Simplifier les fixtures** pour éviter les problèmes d'event loops
3. **Créer des routes de test** sans rate limiting, ou mieux intégrer le bypass dans le limiter

## Utilisation

```bash
# Démarrer la base de données de test
docker-compose -f docker-compose.test.yml up -d

# Exécuter les tests unitaires (fonctionnent)
poetry run pytest tests/unit/

# Tests d'intégration (en cours de finalisation)
poetry run pytest tests/integration/

# Arrêter la base de données
docker-compose -f docker-compose.test.yml down
```

## Notes

La configuration de base est solide et permet d'ajouter facilement de nouveaux tests. Les problèmes restants sont principalement liés à l'intégration avec slowapi et nécessitent des ajustements mineurs pour être résolus.

