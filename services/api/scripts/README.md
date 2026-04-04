# Scripts d'Audit des Migrations

Ce dossier contient un script unifié pour auditer et synchroniser les migrations de base de données.

## Script Principal

### `migration_audit.py`

Script Python qui compare la structure de la base de données avec les modèles SQLAlchemy pour détecter les différences.

#### Fonctionnalités

- ✅ Compare toutes les tables entre la DB et les modèles
- ✅ Détecte les colonnes manquantes
- ✅ Détecte les index manquants
- ✅ Détecte les tables manquantes
- ✅ Génère un script SQL pour corriger les différences (optionnel)

#### Utilisation

> Exécutez les commandes `docker-compose -f docker-compose.dev.yml …` depuis la **racine du dépôt pages**.

##### Audit simple

```bash
# Depuis le conteneur Docker (recommandé)
docker-compose -f docker-compose.dev.yml run --rm api poetry run python scripts/migration_audit.py

# Depuis l'hôte local (nécessite DATABASE_URL configurée)
cd services/api
poetry run python scripts/migration_audit.py
```

##### Audit avec détails supplémentaires

```bash
docker-compose -f docker-compose.dev.yml run --rm api poetry run python scripts/migration_audit.py --verbose
```

##### Audit et génération du script SQL de correction

```bash
docker-compose -f docker-compose.dev.yml run --rm api poetry run python scripts/migration_audit.py --generate-sql
```

Cela génère un fichier `scripts/fix_migrations.sql` que vous pouvez appliquer :

```bash
# Depuis la racine du dépôt pages
docker-compose -f docker-compose.dev.yml exec -T db psql -U postgres -d pages -f /tmp/fix_migrations.sql

# Ou en copiant le fichier dans le conteneur
docker cp services/api/scripts/fix_migrations.sql $(docker-compose -f docker-compose.dev.yml ps -q db):/tmp/
docker-compose -f docker-compose.dev.yml exec db psql -U postgres -d pages -f /tmp/fix_migrations.sql
```

#### Options

- `-v, --verbose` : Affiche les détails supplémentaires (colonnes/index supplémentaires dans la DB)
- `-g, --generate-sql` : Génère un script SQL pour corriger automatiquement les différences

#### Exemple de sortie

```
================================================================================
AUDIT DES MIGRATIONS DE BASE DE DONNÉES
================================================================================

📊 Récupération de la structure de la base de données...
   ✅ 34 tables trouvées dans la base de données
📊 Récupération de la structure des modèles...
   ✅ 34 tables trouvées dans les modèles

🔍 Comparaison des structures...

================================================================================
RÉSULTATS DE LA COMPARAISON
================================================================================

⚠️  COLONNES MANQUANTES DANS LA BASE DE DONNÉES:
   Table 'users':
      - language
   Table 'issues':
      - backlog_order
      - parent_issue_id

⚠️  3 problème(s) détecté(s) nécessitant des migrations.
```

## Workflow Recommandé

### 1. Audit régulier

Exécutez l'audit régulièrement pour détecter les différences :

```bash
docker-compose -f docker-compose.dev.yml run --rm api poetry run python scripts/migration_audit.py
```

### 2. Si des différences sont détectées

#### Option A : Créer une migration Alembic propre (recommandé)

C'est la meilleure pratique : créer une migration Alembic qui ajoute les colonnes manquantes.

```bash
# Créer une nouvelle migration
docker-compose -f docker-compose.dev.yml run --rm api poetry run alembic revision -m "add_missing_columns_from_models"

# Éditer le fichier de migration généré pour ajouter les colonnes manquantes
# Puis l'appliquer
docker-compose -f docker-compose.dev.yml run --rm api poetry run alembic upgrade head
```

**Exemple de migration** : Voir `alembic/versions/2025_12_30_2102_1581b495f287_add_missing_columns_from_models.py` pour un exemple complet.

#### Option B : Utiliser Alembic autogenerate

```bash
# Générer une migration automatique
docker-compose -f docker-compose.dev.yml run --rm api poetry run alembic revision --autogenerate -m "fix_missing_columns"

# ⚠️ ATTENTION : Vérifier soigneusement la migration générée avant de l'appliquer
# Alembic peut parfois générer des suppressions incorrectes

# Puis l'appliquer
docker-compose -f docker-compose.dev.yml run --rm api poetry run alembic upgrade head
```

#### Option C : Générer et appliquer le script SQL

```bash
# Générer le script SQL
docker-compose -f docker-compose.dev.yml run --rm api poetry run python scripts/migration_audit.py --generate-sql

# Appliquer le script (conteneur Postgres kouji-factory)
docker cp services/api/scripts/fix_migrations.sql local-dev-db:/tmp/
docker exec -i local-dev-db psql -U postgres -d pages -f /tmp/fix_migrations.sql
```

### 3. Vérification

Relancez l'audit pour confirmer que tout est synchronisé :

```bash
docker-compose -f docker-compose.dev.yml run --rm api poetry run python scripts/migration_audit.py
```

Vous devriez voir : `✅ Aucune différence détectée !`

## Dépannage

### Erreur de connexion à la base de données

Assurez-vous que :

1. Docker est démarré
2. La base de données est démarrée : `docker-compose -f docker-compose.dev.yml up -d db` (et la base `pages` créée si besoin)
3. La variable d'environnement `DATABASE_URL` est correcte (dans Docker, elle est configurée automatiquement dans `docker-compose.dev.yml`)

### Le script ne détecte pas certaines différences

Le script compare uniquement :

- Les noms de colonnes
- Les noms d'index
- Les noms de tables

Il ne compare pas :

- Les types de données exacts
- Les contraintes de clés étrangères (seulement leur existence)
- Les valeurs par défaut exactes

Pour une vérification plus approfondie, utilisez `alembic revision --autogenerate`.

## Notes

- Le script ignore la table `alembic_version` dans la comparaison
- Les colonnes/index supplémentaires dans la DB ne sont pas considérés comme des erreurs (sauf avec `--verbose`)
- Le script SQL généré utilise `IF NOT EXISTS` pour éviter les erreurs si les éléments existent déjà
