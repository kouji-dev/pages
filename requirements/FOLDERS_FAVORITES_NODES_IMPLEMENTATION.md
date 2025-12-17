# Implémentation des Folders, Favorites et Nodes

## Vue d'ensemble

Cette implémentation ajoute trois fonctionnalités principales au système :
- **Folders** : Système hiérarchique de dossiers pour organiser les projets et espaces
- **Favorites** : Système de favoris hétérogène pour les projets, espaces et pages
- **Nodes** : Représentation unifiée des projets et espaces avec filtrage par folder

## Architecture (DDD & Clean Architecture)

L'implémentation suit strictement les principes de **Domain-Driven Design (DDD)** et de **Clean Architecture** :

### Couches

1. **Domain Layer** : Entités, Value Objects, Interfaces de repositories (ports)
2. **Infrastructure Layer** : Implémentations SQLAlchemy des repositories (adapters), modèles de base de données
3. **Application Layer** : Use cases, DTOs
4. **Presentation Layer** : Endpoints FastAPI

## Fonctionnalités implémentées

### 1. Folders (Dossiers)

#### Entités Domain
- **`Folder`** : Entité avec factory method `create()`, validation dans `__post_init__`
  - Attributs : `id`, `organization_id`, `name`, `parent_id`, `position`, timestamps
  - Méthodes : `update_name()`, `update_parent()`, `update_position()`, `delete()` (soft delete)

#### Repository (Port)
- **`FolderRepository`** : Interface abstraite avec méthodes :
  - `create()`, `get_by_id()`, `update()`, `delete()` (hard delete)
  - `get_all()` avec filtrage par `parent_id` et `include_deleted`
  - `count()`, `get_children()`, `exists_by_name()`

#### Use Cases
- **`CreateFolderUseCase`** : Création avec validation d'organisation et parent
- **`GetFolderUseCase`** : Récupération par ID
- **`ListFoldersUseCase`** : Liste avec filtrage par parent et pagination
- **`UpdateFolderUseCase`** : Mise à jour (nom, parent, position)
- **`DeleteFolderUseCase`** : Soft delete
- **`AssignNodesToFolderUseCase`** : Assignation de projets/espaces à un folder

#### Endpoints API
```
GET    /api/v1/organizations/{id}/folders
POST   /api/v1/organizations/{id}/folders
GET    /api/v1/organizations/{id}/folders/{id}
PUT    /api/v1/organizations/{id}/folders/{id}
DELETE /api/v1/organizations/{id}/folders/{id}
PUT    /api/v1/organizations/{id}/folders/{id}/nodes
```

### 2. Favorites (Favoris)

#### Value Object
- **`EntityType`** : Value object immuable pour valider les types d'entités
  - Types valides : `project`, `space`, `page`
  - Méthodes : `from_string()`, `project()`, `space()`, `page()`
  - Validation stricte avec exceptions

#### Entités Domain
- **`Favorite`** : Entité avec factory method `create()`
  - Attributs : `id`, `user_id`, `entity_type` (EntityType), `entity_id`, timestamps
  - Validation : `entity_type` doit être un `EntityType` valide

#### Repository (Port)
- **`FavoriteRepository`** : Interface abstraite avec méthodes :
  - `create()`, `get_by_id()`, `delete()` (hard delete)
  - `get_all()` avec filtrage par `entity_type` et pagination
  - `count()`, `exists()`, `get_by_entity()`

#### Use Cases
- **`CreateFavoriteUseCase`** : Création avec validation d'unicité
- **`ListFavoritesUseCase`** : Liste avec filtrage par type et pagination
- **`DeleteFavoriteUseCase`** : Suppression

#### Endpoints API
```
GET    /api/v1/users/me/favorites
POST   /api/v1/users/me/favorites
DELETE /api/v1/users/me/favorites/{id}
```

### 3. Nodes (Projets + Espaces unifiés)

#### DTOs
- **`NodeResponse`** : Représentation unifiée avec `type: "project" | "space"`
- **`NodeListResponse`** : Liste paginée de nodes

#### Use Cases
- **`ListNodesUseCase`** : Combine projets et espaces en une liste unifiée
  - Filtrage optionnel par `folder_id`
  - Tri par date de création (plus récent en premier)
  - Pagination

#### Endpoints API
```
GET    /api/v1/organizations/{id}/nodes?folder_id={id}
```

## Modifications de la base de données

### Migration Alembic
- **Fichier** : `alembic/versions/2025_12_17_1638_add_folders_and_favorites.py`

#### Tables créées

1. **`folders`**
   - `id` (UUID, PK)
   - `organization_id` (UUID, FK → organizations)
   - `name` (String 100)
   - `parent_id` (UUID, FK → folders, nullable)
   - `position` (Integer)
   - `created_at`, `updated_at`, `deleted_at` (soft delete)
   - Contrainte unique : `(organization_id, name, parent_id)`

2. **`favorites`**
   - `id` (UUID, PK)
   - `user_id` (UUID, FK → users)
   - `entity_type` (String 50) : "project", "space", "page"
   - `entity_id` (UUID)
   - `created_at`, `updated_at`
   - Contrainte unique : `(user_id, entity_type, entity_id)`

#### Colonnes ajoutées

1. **`projects.folder_id`**
   - UUID, FK → folders, nullable
   - ON DELETE SET NULL
   - Index

2. **`spaces.folder_id`**
   - UUID, FK → folders, nullable
   - ON DELETE SET NULL
   - Index

## Modifications des entités existantes

### Project & Space
- Ajout de `folder_id` dans les repositories
- Modification de `get_all()` pour filtrer par `folder_id`
- Support du filtrage : `folder_id=None` pour les nodes sans folder, `folder_id=UUID` pour les nodes dans un folder spécifique

## Tests

### Tests unitaires (35 tests)
- **Couverture** : 96% pour les use cases
- **Fichiers** :
  - `tests/unit/test_folder_use_cases.py` (18 tests)
  - `tests/unit/test_favorite_use_cases.py` (10 tests)
  - `tests/unit/test_node_use_cases.py` (4 tests)

**Scénarios testés** :
- Succès de toutes les opérations
- Gestion des erreurs (EntityNotFoundException, ConflictException, ValidationException)
- Validation des entrées
- Cas limites (pagination, filtres)

### Tests d'intégration (23 tests)
- **Fichiers** :
  - `tests/integration/test_folder_endpoints.py` (9 tests)
  - `tests/integration/test_node_endpoints.py` (5 tests)
  - `tests/integration/test_favorite_endpoints.py` (9 tests)

**Scénarios testés** :
- Authentification et autorisations
- Opérations CRUD complètes
- Gestion des erreurs HTTP
- Validation des permissions (admin vs member)

### Tests fonctionnels (7 tests)
- **Fichiers** :
  - `tests/functional/test_folder_workflows.py` (3 tests)
  - `tests/functional/test_favorite_workflows.py` (2 tests)
  - `tests/functional/test_node_workflows.py` (2 tests)

**Workflows testés** :
- Workflow complet folder : create → list → update → delete
- Assignation de nodes à folders
- Hiérarchie de folders (3 niveaux)
- Workflow complet favorite : create → list → delete
- Liste hétérogène de favorites (projects + spaces + pages)
- Filtrage de nodes par folder
- Isolation par organization

## Principes respectés

### DDD (Domain-Driven Design)
- ✅ Entités avec identité et comportement
- ✅ Value Objects immuables (`EntityType`)
- ✅ Factory methods pour création
- ✅ Validation dans le domaine (`__post_init__`)
- ✅ Repositories comme ports (interfaces abstraites)

### Clean Architecture
- ✅ Séparation stricte des couches
- ✅ Dépendances pointent vers le domaine
- ✅ Infrastructure implémente les ports
- ✅ Use cases orchestrent le domaine
- ✅ DTOs pour la communication API

### Bonnes pratiques
- ✅ Aucun hardcoding (utilisation de `EntityType` value object)
- ✅ Gestion d'erreurs avec exceptions métier
- ✅ Logging structuré avec structlog
- ✅ Validation à tous les niveaux (domain, DTOs, API)
- ✅ Soft delete pour folders (hard delete pour favorites)
- ✅ Contraintes d'unicité en base de données

## Fichiers créés/modifiés

### Nouveaux fichiers

**Domain Layer** :
- `src/domain/value_objects/entity_type.py`
- `src/domain/entities/folder.py`
- `src/domain/entities/favorite.py`
- `src/domain/repositories/folder_repository.py`
- `src/domain/repositories/favorite_repository.py`

**Infrastructure Layer** :
- `src/infrastructure/database/models/folder.py`
- `src/infrastructure/database/models/favorite.py`
- `src/infrastructure/database/repositories/folder_repository.py`
- `src/infrastructure/database/repositories/favorite_repository.py`
- `alembic/versions/2025_12_17_1638_add_folders_and_favorites.py`

**Application Layer** :
- `src/application/dtos/folder.py`
- `src/application/dtos/favorite.py`
- `src/application/dtos/node.py`
- `src/application/use_cases/folder/create_folder.py`
- `src/application/use_cases/folder/get_folder.py`
- `src/application/use_cases/folder/list_folders.py`
- `src/application/use_cases/folder/update_folder.py`
- `src/application/use_cases/folder/delete_folder.py`
- `src/application/use_cases/folder/assign_nodes_to_folder.py`
- `src/application/use_cases/favorite/create_favorite.py`
- `src/application/use_cases/favorite/list_favorites.py`
- `src/application/use_cases/favorite/delete_favorite.py`
- `src/application/use_cases/node/list_nodes.py`

**Presentation Layer** :
- `src/presentation/api/v1/folders.py`
- `src/presentation/api/v1/favorites.py`
- `src/presentation/api/v1/nodes.py`

**Tests** :
- `tests/unit/test_folder_use_cases.py`
- `tests/unit/test_favorite_use_cases.py`
- `tests/unit/test_node_use_cases.py`
- `tests/integration/test_folder_endpoints.py`
- `tests/integration/test_node_endpoints.py`
- `tests/integration/test_favorite_endpoints.py`
- `tests/functional/test_folder_workflows.py`
- `tests/functional/test_favorite_workflows.py`
- `tests/functional/test_node_workflows.py`

### Fichiers modifiés

- `src/domain/entities/__init__.py` : Export Folder, Favorite
- `src/domain/value_objects/__init__.py` : Export EntityType
- `src/domain/repositories/__init__.py` : Export FolderRepository, FavoriteRepository
- `src/infrastructure/database/models/__init__.py` : Export FolderModel, FavoriteModel
- `src/infrastructure/database/models/organization.py` : Relation vers FolderModel
- `src/infrastructure/database/models/project.py` : Ajout folder_id et relation
- `src/infrastructure/database/models/page.py` : Ajout folder_id à SpaceModel et relation
- `src/infrastructure/database/models/user.py` : Relation vers FavoriteModel
- `src/infrastructure/database/repositories/__init__.py` : Export repositories
- `src/infrastructure/database/repositories/project_repository.py` : Filtrage par folder_id
- `src/infrastructure/database/repositories/space_repository.py` : Filtrage par folder_id
- `src/domain/repositories/project_repository.py` : Ajout folder_id à get_all()
- `src/domain/repositories/space_repository.py` : Ajout folder_id à get_all()
- `src/presentation/api/v1/__init__.py` : Inclusion des nouveaux routers
- `src/presentation/dependencies/services.py` : Injection de dépendances pour nouveaux repositories
- `tests/conftest.py` : Import des nouveaux modèles

## Utilisation

### Créer un folder
```bash
POST /api/v1/organizations/{org_id}/folders
{
  "organization_id": "uuid",
  "name": "My Folder",
  "parent_id": null,  # optional
  "position": 0
}
```

### Lister les nodes avec filtre folder
```bash
GET /api/v1/organizations/{org_id}/nodes?folder_id={folder_id}
```

### Ajouter un favori
```bash
POST /api/v1/users/me/favorites
{
  "entity_type": "project",  # ou "space" ou "page"
  "entity_id": "uuid"
}
```

### Assigner des nodes à un folder
```bash
PUT /api/v1/organizations/{org_id}/folders/{folder_id}/nodes
{
  "node_ids": ["uuid1", "uuid2"]
}
```

## Notes techniques

- **Soft delete** : Les folders utilisent le soft delete (colonne `deleted_at`)
- **Hard delete** : Les favorites utilisent le hard delete
- **Cascade** : Suppression en cascade configurée pour les relations
- **Index** : Index créés sur `folder_id`, `parent_id`, `user_id`, `entity_id`
- **Contraintes** : Contraintes d'unicité pour éviter les doublons
- **Validation** : Validation à tous les niveaux (domain, DTOs, API)

## Prochaines étapes possibles

- [ ] Endpoint pour déplacer des nodes entre folders
- [ ] Endpoint pour réorganiser l'ordre des folders (drag & drop)
- [ ] Support de la recherche dans les folders
- [ ] Statistiques par folder (nombre de projets/espaces)
- [ ] Permissions granulaires par folder
- [ ] Templates de folders

