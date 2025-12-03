# Technology Stack & Tools
**Last Updated**: 2024  
**Status**: Finalized Technology Decisions

---

## Selected Technology Stack

This document outlines the finalized technology stack for the project based on team decisions.

---

## Frontend Stack
```
Framework:          Angular 21 with TypeScript 5.7+
Architecture:       Domain-Driven Design (DDD) - Domain models, bounded contexts
Workspace Setup:    Empty Angular workspace at root
                     Then create apps/ and libraries/ within workspace
Build Tool:         Angular CLI (Webpack-based)
UI Library:         Tailwind CSS 4+ (with Angular)
Component Library:  Custom Shared UI Library (built from scratch, in libraries/)
CSS Methodology:    BOM (Block Object Modifier) with Tailwind `@apply`
Component Style:    Inline templates and styles (single TS file per component)
State Management:   Angular Signals + RxJS (signals for reactive state, RxJS for async streams)
Modern APIs:        Signals, input()/output(), model(), effect(), computed(), 
                     inject(), httpResource(), resource(), new template blocks (@if, @for, @switch), @defer
Forms:              Angular Reactive Forms + Validators
HTTP Client:        Angular HttpClient with httpResource() (new resource API)
Routing:            Angular Router (feature-based routing)
Rich Text Editor:   Lexical (Facebook)
Charting:           Apache ECharts (via ngx-echarts)
Date Handling:      Luxon
Real-time:          Native WebSockets (via Angular WebSocket service)
```

**Rationale**: Angular provides enterprise-grade features, strong TypeScript support, built-in dependency injection, and excellent tooling. Lexical is a modern, extensible editor framework from Facebook with excellent performance.

**Note on Lexical**: While Lexical has React-specific packages, the core `lexical` package is framework-agnostic. For Angular integration, use the core `lexical` package directly and create Angular service wrappers around Lexical's core APIs.

### Component Architecture with BOM + Tailwind

**Component Structure**:
- Each Angular component uses a **single TypeScript file** (no separate HTML/CSS files)
- **Inline template** and **inline styles** in the `@Component` decorator
- Template uses **only CSS classes** following BOM convention
- Inline CSS uses **Tailwind `@apply` directive** to implement classes

**BOM (Block Object Modifier) Methodology**:
- **Block**: Main component name (e.g., `card`, `button`, `form`)
- **Object**: Child element or sub-component (e.g., `card_header`, `card_body`, `button_icon`)
- **Modifier**: Variations (e.g., `card--large`, `button--primary`, `card_header--collapsed`)

**Component Example**:
```typescript
@Component({
  selector: 'app-card',
  template: `
    <div class="card">
      <div class="card_header">
        <h2 class="card_title">{{ title }}</h2>
        <button class="card_close">×</button>
      </div>
      <div class="card_body">
        <ng-content></ng-content>
      </div>
    </div>
  `,
  styles: [`
    .card {
      @apply rounded-lg shadow-md bg-white p-6;
    }
    
    .card_header {
      @apply flex items-center justify-between mb-4;
    }
    
    .card_title {
      @apply text-xl font-semibold text-gray-900;
    }
    
    .card_close {
      @apply text-gray-400 hover:text-gray-600 transition-colors;
    }
    
    .card_body {
      @apply text-gray-700;
    }
    
    /* Modifiers */
    .card--large {
      @apply p-8;
    }
    
    .card_header--collapsed {
      @apply mb-0;
    }
  `]
})
export class CardComponent {
  // Using modern input() API instead of @Input()
  title = input.required<string>();
  
  // Optional input with default
  size = input<'small' | 'medium' | 'large'>('medium');
  
  // Output with modern output() API
  onClose = output<void>();
  
  // Dependency injection with inject()
  private logger = inject(LoggerService);
}
```

**Benefits**:
- **Single file components**: Easier to maintain and understand
- **BOM naming**: Clear, semantic class names following consistent pattern
- **Tailwind utilities**: Leverage Tailwind's utility classes via `@apply`
- **Composability**: Combine multiple utilities easily
- **Consistency**: BOM ensures predictable class naming across components
- **Type safety**: Single TS file keeps everything together for better IDE support

### Modern Angular APIs & Patterns

**Core Reactive APIs**:
- **Signals**: Use `signal()` for reactive state management (preferred over BehaviorSubject for simple state)
- **Computed**: Use `computed()` for derived reactive values based on signals
- **Effect**: Use `effect()` for side effects triggered by signal changes
- **Resource**: Use `resource()` for async resource loading with signals
- **HttpResource**: Use `httpResource()` for HTTP requests with automatic loading/error states

**Component APIs**:
- **input()**: Use `input()` function instead of `@Input()` decorator (type-safe, required/optional)
- **output()**: Use `output()` function instead of `@Output()` decorator (type-safe event emitters)
- **model()**: Use `model()` for two-way binding with signals [(ngModel)] alternative
- **inject()**: Use `inject()` function instead of constructor injection (cleaner DI)

**Template Syntax**:
- **@if**: Use `@if` control flow instead of `*ngIf` (better performance, type narrowing)
- **@for**: Use `@for` instead of `*ngFor` (better performance, trackBy built-in)
- **@switch**: Use `@switch/@case/@default` instead of `[ngSwitch]`
- **@defer**: Use `@defer` for lazy loading blocks (improves initial load time)

**Component Example with Modern APIs**:
```typescript
import { Component, signal, computed, effect, input, output, model, inject } from '@angular/core';
import { httpResource } from '@angular/common/http';
import { HttpClient } from '@angular/common/http';

interface Task {
  id: number;
  title: string;
  description: string;
  status: 'active' | 'completed';
}

@Component({
  selector: 'app-task-list',
  template: `
    @if (tasksResource.value(); as tasks) {
      @for (task of tasks; track task.id) {
        <div class="task">
          <h3 class="task_title">{{ task.title }}</h3>
          <p class="task_description">{{ task.description }}</p>
          <button class="task_button" (click)="onComplete.emit(task.id)">
            Complete
          </button>
        </div>
      } @empty {
        <p>No tasks found</p>
      }
    } @else if (tasksResource.isLoading()) {
      <p>Loading tasks...</p>
    } @else if (tasksResource.hasError()) {
      <p>Error: {{ tasksResource.error() }}</p>
    }

    @defer (on viewport) {
      <app-heavy-component />
    } @placeholder {
      <div>Loading heavy component...</div>
    }
  `,
  styles: [`
    .task {
      @apply p-4 border rounded-lg mb-4;
    }
    .task_title {
      @apply text-lg font-semibold mb-2;
    }
    .task_description {
      @apply text-gray-600 mb-4;
    }
    .task_button {
      @apply px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600;
    }
  `]
})
export class TaskListComponent {
  // Modern input/output API
  userId = input.required<number>();
  status = input<'all' | 'active' | 'completed'>('all');
  
  onComplete = output<number>();
  onTaskSelected = output<Task>();
  
  // Two-way binding with signals
  selectedTaskId = model<number | null>(null);
  
  // Dependency injection with inject()
  private http = inject(HttpClient);
  
  // Signals for reactive state
  private filter = signal(this.status());
  tasks = signal<Task[]>([]);
  
  // Computed derived values
  filteredTasks = computed(() => {
    const allTasks = this.tasks();
    const statusFilter = this.filter();
    return statusFilter === 'all' 
      ? allTasks 
      : allTasks.filter(t => t.status === statusFilter);
  });
  
  // HttpResource for async data loading
  tasksResource = httpResource({
    request: () => this.http.get<Task[]>(`/api/tasks?userId=${this.userId()}`)
  });
  
  // Effect for side effects
  private logger = effect(() => {
    console.log('Selected task changed:', this.selectedTaskId());
  });
  
  // Update filter when status input changes
  constructor() {
    effect(() => {
      this.filter.set(this.status());
    });
  }
}
```

**Service Example with Modern APIs**:
```typescript
import { Injectable, inject, signal, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({ providedIn: 'root' })
export class TaskService {
  private http = inject(HttpClient);
  
  // State with signals
  private tasks = signal<Task[]>([]);
  private loading = signal(false);
  
  // Public readonly signals
  readonly tasks$ = this.tasks.asReadonly();
  readonly loading$ = this.loading.asReadonly();
  
  // Computed derived state
  readonly activeTasks = computed(() => 
    this.tasks().filter(t => t.status === 'active')
  );
  
  async loadTasks(userId: number): Promise<Task[]> {
    this.loading.set(true);
    try {
      const tasks = await this.http.get<Task[]>(`/api/tasks/${userId}`).toPromise();
      this.tasks.set(tasks || []);
      return tasks || [];
    } finally {
      this.loading.set(false);
    }
  }
}
```

**Benefits of Modern Angular APIs**:
- **Better Performance**: Signals are more efficient than observables for simple state
- **Type Safety**: `input()`/`output()` provide better type inference and required/optional handling
- **Cleaner Syntax**: `inject()` is cleaner than constructor injection
- **Better DX**: New template syntax is more readable and performs better
- **Lazy Loading**: `@defer` improves initial bundle size and load time
- **Automatic Loading States**: `httpResource()` handles loading/error states automatically
- **Fine-grained Reactivity**: Signals enable more efficient change detection

---

### Backend Stack
```
Runtime:            Python 3.12+
Framework:          FastAPI
Architecture:       Domain-Driven Design (DDD) - Monolith with clear domain boundaries
                     REST API first
Package Management: Poetry (pyproject.toml)
ORM:                SQLAlchemy 2.0+ (async)
API Style:          REST
API Docs:           Built-in OpenAPI/Swagger (FastAPI)
Validation:         Pydantic v2 (built into FastAPI)
Authentication:     python-jose (JWT) + python-multipart
File Upload:        FastAPI file uploads (built-in, async)
Real-time:          Native WebSockets (FastAPI WebSocket support, async)
Job Queue:          Celery (Redis broker, async workers)
Background Tasks:   Celery (async tasks)
Async Pattern:      Use async/await throughout (async functions where appropriate)
```

**Rationale**: Python + FastAPI with async/await provides excellent performance. Domain-Driven Design ensures clean architecture and maintainability in a monolith structure. Poetry provides better dependency management than requirements.txt. REST API first approach for simplicity. All I/O operations use async patterns for optimal performance.

---

### Database & Storage
```
Primary DB:         PostgreSQL 17+ (hosted on Supabase)
                     Connection: Standard PostgreSQL connection string (direct connection, not Supabase SDK)
                     Driver: asyncpg
Caching:            Redis 8+
Search:             PostgreSQL Full-Text Search
Vector DB:          pgvector (PostgreSQL extension - supported by Supabase)
File Storage:       PostgreSQL Large Objects (pg_largeobject - built-in, open source)
                     File metadata stored in PostgreSQL tables
                     File content stored in PostgreSQL large objects
                     Separate Docker container if needed for optimization
```

**Rationale**: All storage solutions use PostgreSQL and open-source extensions. pg_largeobject is built into PostgreSQL and provides file storage capabilities. File metadata in regular tables and file content in large objects. pgvector runs in a separate container for vector operations. Redis provides fast caching layer.

---

### Infrastructure & DevOps
```
Containerization:   Docker (all services, apps, libraries)
Orchestration:      Docker Compose (development, staging, production)
Repository Style:   Monorepo (all projects in single repository)
Version Management: Python and pnpm versions pinned in Docker images
Cloud Provider:     Google Cloud Platform (GCP) - Recommended for AI/ML focus
CI/CD:              GitHub Actions
CDN:                CloudFlare
Domain/DNS:         CloudFlare
SSL:                Let's Encrypt
```

**Rationale**: Docker Compose manages all services, applications, and libraries in a monorepo structure. All Python and pnpm versions are encapsulated and pinned within Docker containers, ensuring consistent environments across development, staging, and production. This approach provides reproducibility, isolation, and simplified dependency management.

---

### Monitoring & Logging
```
Error Tracking:     Sentry (free tier available)
APM:                Not needed for MVP (add in Phase 2)
Metrics:            Prometheus + Grafana (self-hosted)
Logging:            Python logging + structlog
Log Aggregation:    Loki (self-hosted)
Uptime Monitoring:  UptimeRobot (free tier)
```

**Rationale**: Sentry provides excellent error tracking and monitoring. Prometheus + Grafana offers free, powerful metrics visualization.

---

### AI/ML Stack
```
Multi-Agent Framework: CrewAI (multi-agent orchestration)
LLM Provider:       OpenAI API (GPT-4)
Vector DB:          pgvector (PostgreSQL extension)
ML Framework:       Python - scikit-learn (if needed)
AI SDK:             OpenAI Python SDK (openai package)
Embeddings:         sentence-transformers (self-hosted, free)
Agent Communication: Asynchronous messaging protocol
```

**Rationale**: CrewAI provides production-ready multi-agent orchestration with guardrails, memory, and observability. OpenAI API provides excellent models. pgvector integrates seamlessly with PostgreSQL for vector storage and knowledge base (RAG).

---

### Mobile Strategy
```
Approach:           PWA (Progressive Web App) Only
Service Worker:     Angular Service Worker (@angular/pwa)
Push Notifications: Web Push API
Offline Support:    Service Worker caching
Install Prompt:     PWA install prompts
```

**Rationale**: PWA approach allows mobile-like experience without native app development, reducing complexity and maintenance overhead.

---

### Development Tools
```
Package Manager:    pnpm
Version Control:    Git + GitHub
Code Quality:       oxlint (oxc project) - 50-100x faster than ESLint
                     Supports 600+ rules from ESLint, TypeScript, React, Jest
                     No configuration needed by default
                     Type-aware linting available (preview)
Type Checking:      TypeScript (tsc)
Pre-commit Hooks:   Husky + lint-staged (with oxlint)
Code Formatting:    Prettier (oxfmt when stable)
Git Hooks:          Husky
API Testing:        Postman (free tier)
E2E Testing:        Playwright
Load Testing:       k6 (open source)
Release Management: Semantic Versioning (semver)
                     Conventional Commits
                     Automated changelog generation (standard-version)
Scripts:            Development scripts (pnpm dev, pnpm test, etc.)
                     Deployment scripts (scripts/deploy.sh)
                     Release scripts (scripts/release.sh)
                     Self-hosted deployment workflows
```

**Rationale**: pnpm provides fast, efficient package management. oxlint (from [oxc project](https://oxc.rs/docs/guide/usage/linter.html)) is 50-100x faster than ESLint with over 600 rules, supports type-aware linting, and requires no configuration by default. Semantic versioning and conventional commits ensure consistent release management. Scripts provide smooth local development and self-hosted deployment workflows.

---

### Security Tools
```
Authentication:     JWT (python-jose) + passlib (bcrypt/Argon2)
SSO:                python-saml (SAML)
                     authlib (OAuth/OIDC)
Rate Limiting:      slowapi (FastAPI rate limiting)
CORS:               FastAPI CORS middleware
Security Headers:   FastAPI security middleware
Dependency Scanning: Dependabot (free, GitHub native)
Secret Management:  python-dotenv (environment variables)
                     Google Cloud Secret Manager (production)
```

**Rationale**: Standard security practices with Python-specific tools. JWT for stateless auth, passlib for secure password hashing.

---

### Third-Party Services & Integrations
```
Email:              SendGrid (free tier available)
Slack Integration:  slack-sdk (Python)
GitHub Integration: PyGithub
Analytics:          PostHog (open source, self-hostable)
Customer Support:   Crisp (free tier available)
Payment Processing: Stripe
```

**Rationale**: SendGrid has a free tier. Stripe is the standard for payments. PostHog is open-source, self-hostable, and privacy-friendly.

---

## Technology Versions & Compatibility

### Python Ecosystem
```json
{
  "python": ">=3.12.0",
  "pnpm": ">=10.0.0"
}
```

### Python Package Management
**Tool**: Poetry
**Configuration**: `pyproject.toml`

**Example pyproject.toml structure**:
```toml
[tool.poetry]
name = "backend"
version = "0.1.0"
description = "FastAPI backend with DDD architecture"

[tool.poetry.dependencies]
python = "^3.12"
fastapi = "^0.115.0"
uvicorn = {extras = ["standard"], version = "^0.32.0"}
sqlalchemy = {extras = ["asyncio"], version = "^2.0.36"}
alembic = "^1.13.0"
asyncpg = "^0.29.0"
pydantic = "^2.9.0"
pydantic-settings = "^2.5.0"
python-jose = {extras = ["cryptography"], version = "^3.3.0"}
passlib = {extras = ["bcrypt"], version = "^1.7.4"}
python-multipart = "^0.0.12"
celery = {extras = ["redis"], version = "^5.4.0"}
redis = "^5.2.0"
python-dotenv = "^1.0.1"
openai = "^1.54.0"
structlog = "^24.4.0"
sentence-transformers = "^2.3.0"
crewai = "^0.80.0"
crewai-tools = "^0.8.0"

[tool.poetry.group.dev.dependencies]
pytest = "^8.0.0"
pytest-asyncio = "^0.23.0"
black = "^24.0.0"
ruff = "^0.5.0"
mypy = "^1.10.0"
```

**Key Dependencies (Python - Backend)**:
- All dependencies managed via Poetry (pyproject.toml)
- Async versions of libraries (SQLAlchemy with asyncio, asyncpg)
- Development dependencies in separate group

### Key Dependencies (Angular - Frontend)
```json
{
  "@angular/core": "^21.0.0",
  "@angular/cli": "^21.0.0",
  "typescript": "^5.7.0",
  "rxjs": "^7.8.1",
  "lexical": "^0.18.0",
  "tailwindcss": "^4.0.0",
  "luxon": "^3.5.0",
  "echarts": "^5.5.0",
  "ngx-echarts": "^17.0.0",
  "oxlint": "^0.15.0",
  "conventional-changelog-cli": "^4.1.0",
  "standard-version": "^9.5.0",
  "@ngrx/store": "^18.0.0"
}
```

**Note**: Lexical core package is framework-agnostic. Angular integration will use the core `lexical` package directly.

---

## Selected Technology Decisions

| Technology Area | Selected Choice | Rationale |
|----------------|----------------|-----------|
| **Frontend** | Angular 21 + TypeScript 5.7 | Enterprise-focused, full-featured framework with strong TypeScript support |
| **Backend** | Python 3.12+ + FastAPI | Excellent for AI/ML features, automatic API docs, strong performance |
| **Rich Text Editor** | Lexical 0.18+ | Modern, extensible, high-performance editor framework |
| **Database** | PostgreSQL 17+ (Supabase) | Managed PostgreSQL via Supabase, standard connection (no SDK), supports full-text search and pgvector |
| **Search** | PostgreSQL Full-Text Search | Built-in, no additional infrastructure needed for MVP |
| **Caching** | Redis 8+ | Fast, feature-rich caching layer |
| **Mobile** | PWA Only | Reduce complexity, no native app development needed initially |
| **Cloud** | Google Cloud Platform (GCP) | Excellent for AI/ML, Kubernetes support, Python-friendly |
| **Deployment** | Docker Compose (Monorepo) | All services, apps, libraries in containers. Python/pnpm versions pinned in Docker images |
| **CI/CD** | GitHub Actions | Free, integrated with GitHub |
| **Monitoring** | Sentry | Excellent error tracking and monitoring |
| **Real-time** | Native WebSockets | Lightweight, no additional dependencies |
| **AI Provider** | OpenAI API | Easy integration, excellent models, pay-per-use |
| **Package Manager** | pnpm 10+ | Fast, disk-efficient, strict dependency management |

---

## Architecture Considerations

### Repository Structure
**Recommendation**: Monorepo with Docker Compose orchestration

**Structure**:
```
monorepo/
├── clients/
│   └── app1/              # Angular workspace (main frontend app)
│   └── app2/              # Future app
└── libraries/             # Angular libraries (shared across all clients)
│           ├── shared-ui/ # Shared UI component library
├── angular.json (at root) # Angular workspace configuration at root
│   # Future: clients/app2, clients/mobile, etc.
├── services/
│   └── api/               # FastAPI application (monolith)
│       ├── src/
│       │   ├── domain/    # Domain layer (entities, value objects, domain services)
│       │   ├── application/ # Application layer (use cases, DTOs)
│       │   ├── infrastructure/ # Infrastructure layer (repositories, external services)
│       │   └── presentation/ # Presentation layer (REST API, FastAPI routers)
│       └── pyproject.toml # Poetry configuration
│   # Future: services/auth-service, services/notification-service, etc.
├── docker-compose.yml     # Main orchestration file
├── docker-compose.dev.yml # Development overrides
└── docker-compose.prod.yml # Production overrides
```

**Rationale**:
- Single repository for all code
- Clear separation: `clients/` for frontend apps, `services/` for backend APIs
- Shared `libraries/` directory at root for Angular libraries used across all clients
- `angular.json` at root manages entire Angular workspace
- Shared dependencies and tooling
- Consistent version management via Docker
- Easier code sharing between clients and services
- Simplified CI/CD pipeline
- Easy to add new clients (clients/app2) or extract services (services/service2)

---

### Docker Compose Strategy
**Recommendation**: Docker Compose for all services and clients

**Approach**:
- **Every service/client** runs in its own Docker container
- **Python version** pinned in Dockerfile (Python 3.12.x)
- **pnpm version** pinned in Dockerfile (pnpm 10.x)
- **Node.js version** pinned for client builds
- **Development**: Docker Compose with hot-reload volumes
- **Production**: Docker Compose with optimized images
- **Shared volumes** for node_modules and Python packages (optional optimization)

**Benefits**:
- Consistent environments across all developers
- No local Python/pnpm/Node.js version conflicts
- Reproducible builds
- Easy onboarding (just `docker-compose up`)
- All dependencies encapsulated

---

## Development Scripts & Workflows

### Local Development Scripts

**Package.json scripts (Root monorepo)**:
```json
{
  "scripts": {
    "dev": "docker-compose -f docker-compose.yml -f docker-compose.dev.yml up",
    "dev:api": "docker-compose -f docker-compose.yml -f docker-compose.dev.yml up api",
    "dev:app1": "docker-compose -f docker-compose.yml -f docker-compose.dev.yml up app1",
    "build": "docker-compose run --rm app1 pnpm build",
    "build:api": "docker-compose run --rm api poetry build",
    "test": "docker-compose run --rm app1 pnpm test",
    "test:api": "docker-compose run --rm api poetry run pytest",
    "lint": "docker-compose run --rm app1 pnpm oxlint",
    "lint:type-aware": "docker-compose run --rm app1 pnpm oxlint --type-aware",
    "lint:api": "docker-compose run --rm api poetry run ruff check",
    "format": "docker-compose run --rm app1 pnpm format",
    "format:api": "docker-compose run --rm api poetry run black .",
    "typecheck": "docker-compose run --rm app1 pnpm typecheck",
    "typecheck:api": "docker-compose run --rm api poetry run mypy",
    "clean": "docker-compose down -v && docker system prune -f",
    "logs": "docker-compose logs -f",
    "logs:api": "docker-compose logs -f api",
    "logs:app1": "docker-compose logs -f app1"
  }
}
```

**Poetry scripts (Backend)**:
```toml
[tool.poetry.scripts]
dev = "uvicorn src.main:app --reload --host 0.0.0.0 --port 8000"
start = "uvicorn src.main:app --host 0.0.0.0 --port 8000"
migrate = "alembic upgrade head"
migrate:create = "alembic revision --autogenerate -m"
test = "pytest"
lint = "ruff check ."
format = "black ."
typecheck = "mypy src"
```

### oxlint Configuration

**Installation**:
```bash
pnpm add -D oxlint@latest
# For type-aware linting (preview):
pnpm add -D oxlint-tsgolint@latest
```

**Configuration file** (`.oxlintrc.json`):
```json
{
  "deny": [
    "correctness",
    "suspicious",
    "perf"
  ],
  "allow": [],
  "warn": ["style"],
  "plugins": []
}
```

**Features**:
- 50-100x faster than ESLint ([benchmark](https://oxc.rs/docs/guide/usage/linter.html))
- 600+ rules from ESLint, TypeScript, React, Jest, JSX A11y, Unicorn
- No configuration needed by default
- Type-aware linting available (preview mode with `--type-aware` flag)
- Automatic fixes support
- Comment disabling support (`// oxlint-disable`)

**Usage**:
- Basic: `pnpm oxlint`
- Type-aware: `pnpm oxlint --type-aware`
- In Docker: `docker-compose run --rm app1 pnpm oxlint`

**VS Code Extension**: [oxlint extension](https://marketplace.visualstudio.com/items?itemName=oxc-project.oxc-vscode) - Also works in Cursor

**Integration with lint-staged**:
```json
{
  "lint-staged": {
    "**/*.{js,mjs,cjs,jsx,ts,mts,cts,tsx,vue,astro,svelte}": "oxlint"
  }
}
```

### Deployment Scripts

**Self-Hosted Deployment Script** (`scripts/deploy.sh`):
```bash
#!/bin/bash
set -e

# Load environment variables
source .env.production

# Pull latest code
git pull origin main

# Build and deploy with Docker Compose
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Run database migrations
docker-compose -f docker-compose.yml -f docker-compose.prod.yml run --rm api poetry run alembic upgrade head

# Health check
sleep 5
curl -f http://localhost:${API_PORT:-8000}/health || exit 1

echo "Deployment successful!"
```

**Rollback Script** (`scripts/rollback.sh`):
```bash
#!/bin/bash
set -e

# Load environment variables
source .env.production

# Rollback to previous version
docker-compose -f docker-compose.yml -f docker-compose.prod.yml down
docker-compose -f docker-compose.yml -f docker-compose.prod.yml pull
git checkout HEAD~1
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

echo "Rollback completed!"
```

### Release Management

**Version Strategy**: Semantic Versioning (semver) - MAJOR.MINOR.PATCH

**Release Script** (`scripts/release.sh`):
```bash
#!/bin/bash
set -e

# Check if version type is provided
if [ -z "$1" ]; then
  echo "Usage: ./scripts/release.sh [major|minor|patch]"
  exit 1
fi

VERSION_TYPE=$1

# Bump version
npm version $VERSION_TYPE --no-git-tag-version
cd services/api && poetry version $VERSION_TYPE && cd ../..

NEW_VERSION=$(node -p "require('./package.json').version")

# Generate changelog
npx standard-version --release-as $NEW_VERSION

# Create git tag (standard-version already creates this)
git push origin main --follow-tags

echo "Version bumped to $NEW_VERSION and released!"
```

**Conventional Commits Format**:
- `feat:` - New feature (triggers minor version bump)
- `fix:` - Bug fix (triggers patch version bump)
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, no version bump)
- `refactor:` - Code refactoring (no version bump)
- `perf:` - Performance improvements (triggers patch version bump)
- `test:` - Test additions/changes (no version bump)
- `chore:` - Build process or auxiliary tool changes (no version bump)
- `BREAKING CHANGE:` - Major version bump

**Changelog Generation**: Use `standard-version` which automatically:
- Bumps version based on conventional commits
- Generates CHANGELOG.md
- Creates git tags
- Commits all changes

**Release Best Practices**:
1. Use conventional commits in all commits
2. Run `./scripts/release.sh patch|minor|major` for releases
3. Releases automatically generate changelog and tags
4. Self-hosted deployments use tagged versions
5. Docker images tagged with version numbers
6. Rollback uses previous git tags

---

### Microservices vs Monolith
**Recommendation**: Start with Monolith, extract services later if needed

**Rationale**: 
- Faster development
- Easier debugging
- Lower operational complexity
- Can extract services when needed (e.g., AI service, notification service)
- Docker Compose makes service extraction easier when needed

---

### API Design
**Recommendation**: REST API first (monolith with DDD)

**Rationale**:
- REST is simpler to implement and understand
- Better tooling and documentation (OpenAPI/Swagger)
- DDD provides clear domain boundaries within monolith
- Easy to extract domains to microservices later if needed
- GraphQL can be added in Phase 2+ if complex queries are needed

---

### Database Strategy
**Recommendation**: Single PostgreSQL database with proper indexing

**Rationale**:
- Simpler operations
- ACID transactions across related data
- Can add read replicas for scale
- Consider separate DBs only if needed (e.g., analytics, logs)

---

## Self-Hosted Considerations

For self-hosted deployments, Docker Compose orchestrates all services:

```
All Services:       Managed via Docker Compose
Database:           PostgreSQL container (or external Supabase)
                     - Main PostgreSQL database
pgvector:           Separate PostgreSQL container with pgvector extension
                     - For vector operations and AI features
File Storage:       PostgreSQL Large Objects (pg_largeobject)
                     - Built into PostgreSQL, no separate service needed
                     - File metadata in PostgreSQL tables
                     - File content in PostgreSQL large objects
Cache:              Redis container
Search:             PostgreSQL full-text search (Elasticsearch container optional in Phase 2+)
Monitoring:         Prometheus + Grafana containers (self-hosted)
Logging:            Loki container (self-hosted)
Frontend (app1):    Nginx container serving built Angular app
Backend (api):      FastAPI container with Uvicorn (async)
All Clients/Services: Individual containers as needed
Container Runtime:  Docker + Docker Compose
```

**Monorepo Docker Compose Structure**:
- Single `docker-compose.yml` defines all services
- Services can be enabled/disabled per environment
- Shared networks for inter-service communication
- Volume mounts for persistent data
- Environment-specific compose overrides (dev, staging, prod)

---

## Cost Considerations

### Development Costs (Monthly estimates)
- **SendGrid**: Free tier (100 emails/day), then $19.95/month
- **Sentry**: Free tier (5K events/month), then $26/month
- **OpenAI API**: Pay-per-use (~$0.002 per 1K tokens)
- **AWS S3**: ~$0.023 per GB storage + $0.005 per 1K requests
- **CloudFlare**: Free tier available
- **GitHub Actions**: Free tier (2000 minutes/month)

### Production Costs (Monthly estimates for 100 users)
- **Cloud Hosting** (AWS/DigitalOcean): $50-200/month
- **Database** (managed PostgreSQL): $15-50/month
- **Redis** (managed): $10-30/month
- **Storage** (S3): $5-20/month
- **Monitoring** (Sentry): $26/month
- **Email** (SendGrid): $19.95/month
- **Total**: ~$125-345/month

---

## Migration & Upgrade Paths

### Phase 1 (MVP)
- Domain-Driven Design architecture (frontend and backend)
- REST API first approach
- PostgreSQL full-text search
- PostgreSQL Large Objects for file storage
- Simple JWT authentication
- Docker Compose deployment (PostgreSQL, pgvector, Redis, api service, app1 client)
- PWA for mobile access
- Async/await patterns throughout backend
- Poetry for Python dependency management

### Phase 2 (Enhanced)
- Consider Elasticsearch for advanced search (if needed)
- Add SSO (SAML/OAuth)
- Implement Redis caching layer
- Add job queue (Celery)
- Enhanced real-time collaboration

### Phase 3 (Advanced)
- AI features (OpenAI API)
- Vector database (pgvector)
- Scale with Kubernetes (if needed)
- Advanced analytics and reporting
- Consider GraphQL API (if needed)

---

## Technology Adoption Timeline

| Phase | Technologies Added |
|-------|-------------------|
| **Phase 1** | Angular, Python/FastAPI, PostgreSQL, Redis, Docker Compose, GitHub Actions, Lexical |
| **Phase 2** | Celery, Native WebSockets, Advanced features, Elasticsearch (optional) |
| **Phase 3** | OpenAI API, pgvector, AI features |

---

## Technology Stack Summary

**Selected Stack**:
- **Repository**: Monorepo (all clients and services in single repo)
- **Frontend**: Angular 21 + TypeScript 5.7 + Lexical editor 0.18+
- **Backend**: Python 3.12+ + FastAPI 0.115+
- **Architecture**: Domain-Driven Design (DDD) for frontend and backend
- **Backend Package Manager**: Poetry (pyproject.toml) instead of requirements.txt
- **Async Patterns**: async/await throughout backend (all I/O operations)
- **Database**: PostgreSQL 17+ (Supabase-hosted) with full-text search
- **File Storage**: PostgreSQL Large Objects (pg_largeobject - built-in, open source)
- **Vector DB**: pgvector (separate PostgreSQL container)
- **Caching**: Redis 8+
- **Mobile**: PWA (Progressive Web App)
- **Cloud**: Google Cloud Platform (GCP)
- **Containerization**: Docker + Docker Compose (all services and clients)
- **Version Management**: Python 3.12.x and pnpm 10.x pinned in Docker images
- **CI/CD**: GitHub Actions
- **Monitoring**: Sentry + Prometheus + Grafana
- **Real-time**: Native WebSockets
- **AI**: OpenAI API + pgvector
- **Package Manager**: pnpm 10+

---

## Next Steps

1. **Set up monorepo structure** with clients/ and libraries/ directories
   - Create Angular workspace at root with `angular.json`
   - Create `clients/app1` application
   - Create `libraries/shared-ui` library
2. **Create Dockerfiles** for all services/clients with pinned versions:
   - Python 3.12.x in `services/api/Dockerfile`
   - pnpm 10.x and Node.js in `clients/app1/Dockerfile`
   - All other services with version pins
3. **Create Docker Compose configuration**:
   - `docker-compose.yml` - Base configuration
   - `docker-compose.dev.yml` - Development overrides (hot-reload, volumes)
   - `docker-compose.prod.yml` - Production optimizations
4. **Set up development environment** - developers run `docker-compose up`
5. **Create initial project structure** with Angular and FastAPI in monorepo
6. **Set up CI/CD pipeline** with GitHub Actions (builds Docker images)
7. **Initialize database** with Supabase (PostgreSQL) connection
8. **Configure Redis** in Docker Compose
9. **Integrate Lexical editor** into Angular application
10. **Set up monitoring** with Sentry

---

**Document Status**: Finalized  
**Last Updated**: 2024

