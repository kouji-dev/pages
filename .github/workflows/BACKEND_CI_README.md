# Backend CI/CD - Documentation

Ce document décrit les jobs GitHub Actions configurés pour le backend API.

## Jobs Configurés

### 1. **Lint & Format Check** ✅
- **Objectif** : Vérifier la qualité et la cohérence du code
- **Outils utilisés** :
  - **Black** : Vérification du formatage du code
  - **Ruff** : Linting rapide (remplace flake8, isort, etc.)
  - **MyPy** : Vérification des types statiques
- **Déclenchement** : À chaque push/PR
- **Durée estimée** : ~2-3 minutes

### 2. **Unit Tests** ✅
- **Objectif** : Exécuter les tests unitaires
- **Outils** :
  - pytest avec pytest-asyncio
  - pytest-cov pour la couverture de code
- **Rapports** :
  - Coverage XML (upload vers Codecov)
  - Coverage HTML (artefact téléchargeable)
- **Déclenchement** : À chaque push/PR
- **Durée estimée** : ~3-5 minutes

### 3. **Integration Tests** ✅
- **Objectif** : Exécuter les tests d'intégration avec une vraie base de données
- **Infrastructure** :
  - PostgreSQL 17 via service container GitHub Actions
  - Base de données de test isolée
- **Rapports** :
  - Coverage XML (upload vers Codecov)
  - Coverage HTML (artefact téléchargeable)
- **Déclenchement** : À chaque push/PR
- **Durée estimée** : ~5-8 minutes

### 4. **Security Scanning** ✅
- **Objectif** : Détecter les vulnérabilités de sécurité
- **Outils** :
  - **Safety** : Vérification des dépendances Python contre une base de données de vulnérabilités connues
  - **Bandit** : Analyse statique du code pour détecter les problèmes de sécurité courants
- **Rapports** : JSON téléchargeable
- **Déclenchement** : À chaque push/PR
- **Durée estimée** : ~3-4 minutes

### 5. **Migrations Check** ✅
- **Objectif** : Vérifier que les migrations Alembic sont valides
- **Actions** :
  - Vérifie l'état actuel des migrations
  - Teste les migrations (up et down)
  - S'assure qu'il n'y a pas de conflits
- **Déclenchement** : À chaque push/PR
- **Durée estimée** : ~2-3 minutes

### 6. **Build Docker Image** ✅
- **Objectif** : Construire l'image Docker de l'API
- **Déclenchement** : Uniquement sur push vers `main` ou `develop` (après succès des tests)
- **Fonctionnalités** :
  - Utilise Docker Buildx avec cache GitHub Actions
  - Ne push pas l'image (peut être ajouté si nécessaire)
- **Durée estimée** : ~5-10 minutes

### 7. **All Tests Summary** ✅
- **Objectif** : Afficher un résumé de tous les jobs
- **Déclenchement** : Après tous les autres jobs (même en cas d'échec)
- **Utilité** : Vue d'ensemble rapide de l'état de la CI

## Autres Jobs Recommandés (Non Implémentés)

### A. **Performance Tests**
```yaml
performance-tests:
  name: Performance & Load Tests
  runs-on: ubuntu-latest
  steps:
    - name: Run load tests
      run: |
        # Utiliser locust, k6, ou pytest-benchmark
        poetry run locust -f tests/performance/locustfile.py --headless
```
**Utilité** : Détecter les régressions de performance

### B. **API Contract Testing**
```yaml
contract-tests:
  name: API Contract Tests
  steps:
    - name: Validate OpenAPI schema
      run: poetry run pytest tests/contract/
```
**Utilité** : S'assurer que l'API respecte le contrat OpenAPI

### C. **Dependency Updates Check**
```yaml
dependencies-check:
  name: Check for Dependency Updates
  steps:
    - name: Check updates
      run: poetry show --outdated
```
**Utilité** : Identifier les dépendances obsolètes

### D. **Code Quality Metrics**
```yaml
code-quality:
  name: Code Quality Metrics
  steps:
    - name: Run SonarQube / CodeClimate
      # Intégration avec des outils d'analyse de qualité
```
**Utilité** : Métriques de qualité (complexité, duplication, etc.)

### E. **Database Schema Validation**
```yaml
schema-validation:
  name: Database Schema Validation
  steps:
    - name: Validate schema consistency
      run: poetry run alembic check
```
**Utilité** : Vérifier la cohérence du schéma (déjà partiellement couvert par migrations-check)

### F. **Docker Image Security Scan**
```yaml
docker-security:
  name: Docker Image Security Scan
  steps:
    - name: Scan with Trivy
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: pages-api:latest
```
**Utilité** : Scanner l'image Docker pour les vulnérabilités

### G. **Deploy to Staging**
```yaml
deploy-staging:
  name: Deploy to Staging
  if: github.ref == 'refs/heads/develop'
  needs: [build]
  steps:
    - name: Deploy
      # Déploiement vers environnement de staging
```
**Utilité** : Déploiement automatique après validation

### H. **Backup & Restore Tests**
```yaml
backup-tests:
  name: Backup & Restore Tests
  steps:
    - name: Test backup/restore procedures
      # Vérifier que les procédures de sauvegarde fonctionnent
```
**Utilité** : S'assurer que les sauvegardes sont fonctionnelles

### I. **Documentation Generation**
```yaml
docs-generation:
  name: Generate API Documentation
  steps:
    - name: Generate docs
      run: poetry run python scripts/generate_docs.py
    - name: Deploy to GitHub Pages
      # Publier la documentation
```
**Utilité** : Documentation toujours à jour

### J. **Multi-version Python Testing**
```yaml
test-python-versions:
  name: Test Python Versions
  strategy:
    matrix:
      python-version: ['3.11', '3.12', '3.13']
```
**Utilité** : Compatibilité avec plusieurs versions de Python

## Configuration Requise

### Variables d'Environnement GitHub (Optionnel)

Pour activer certaines fonctionnalités avancées, vous pouvez ajouter :

- `CODECOV_TOKEN` : Pour uploader les rapports de couverture vers Codecov
- `DOCKER_HUB_USERNAME` / `DOCKER_HUB_TOKEN` : Pour push les images Docker
- `SONAR_TOKEN` : Pour l'analyse de qualité de code

### Secrets GitHub (Optionnel)

- Secrets pour les déploiements
- Tokens d'accès aux services externes
- Clés de chiffrement

## Optimisations

### Cache
- Les dépendances Poetry sont mises en cache
- Les images Docker utilisent le cache GitHub Actions

### Parallélisation
- Les jobs `lint`, `test-unit`, `test-integration`, `security`, et `migrations-check` s'exécutent en parallèle
- Réduction du temps total de CI de ~20 minutes à ~8-10 minutes

### Conditions de Déclenchement
- Les jobs ne s'exécutent que si des fichiers dans `services/api/` sont modifiés
- Le build Docker ne s'exécute que sur `main` et `develop`

## Prochaines Étapes

1. ✅ Jobs de base configurés
2. 🔄 Ajouter les outils de sécurité (safety, bandit) aux dépendances dev si nécessaire
3. 📊 Configurer Codecov pour les rapports de couverture
4. 🐳 Configurer le push d'images Docker vers un registry si nécessaire
5. 🚀 Ajouter les jobs de déploiement selon vos besoins

## Notes

- Les jobs de sécurité (`safety` et `bandit`) sont configurés avec `continue-on-error: true` pour ne pas bloquer la CI en cas d'avertissements
- Les rapports de couverture sont disponibles en tant qu'artefacts pendant 7 jours
- Les rapports de sécurité sont conservés pendant 30 jours

