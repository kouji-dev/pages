# App1 DDD Structure

This document explains the Domain-Driven Design (DDD) structure for the `app1` Angular application.

---

## Directory Structure

```
app1/src/app/
├── domain/           # Domain layer - Business logic and entities
├── application/      # Application layer - Use cases and services
├── infrastructure/   # Infrastructure layer - External integrations, HTTP clients
├── presentation/     # Presentation layer - Components, pages, layouts
└── app.ts           # Root component
```

---

## Layer Responsibilities

### Domain Layer (`domain/`)

**Purpose**: Core business logic, domain models, entities, and value objects

**Contains**:

- Domain entities (User, Project, Issue, Page, etc.)
- Value objects (Email, DateRange, etc.)
- Domain services (business logic that doesn't belong to a single entity)
- Domain events
- Domain interfaces/contracts

**Rules**:

- No dependencies on other layers (pure TypeScript)
- No Angular-specific code
- Represents the core business domain

**Example Structure**:

```
domain/
├── entities/
│   ├── user.entity.ts
│   ├── project.entity.ts
│   └── issue.entity.ts
├── value-objects/
│   ├── email.vo.ts
│   └── date-range.vo.ts
├── services/
│   └── issue-assignment.service.ts
└── events/
    └── issue-created.event.ts
```

---

### Application Layer (`application/`)

**Purpose**: Application use cases and orchestration

**Contains**:

- Use case services (business workflows)
- Application services
- DTOs (Data Transfer Objects) for API communication
- Application-level state management (signals, services)
- Command/Query handlers (if using CQRS pattern)

**Rules**:

- Depends only on `domain/`
- Orchestrates domain logic
- Handles application-specific workflows
- Uses infrastructure layer via interfaces

**Example Structure**:

```
application/
├── use-cases/
│   ├── create-project.use-case.ts
│   ├── assign-issue.use-case.ts
│   └── create-page.use-case.ts
├── services/
│   ├── auth.service.ts
│   ├── project.service.ts
│   └── issue.service.ts
├── dtos/
│   ├── create-project.dto.ts
│   └── update-issue.dto.ts
└── state/
    └── auth.state.ts
```

---

### Infrastructure Layer (`infrastructure/`)

**Purpose**: External integrations and technical implementations

**Contains**:

- HTTP clients/services (API communication)
- Repository implementations
- Local storage services
- WebSocket services
- External service integrations (GitHub, Slack, etc.)
- HTTP interceptors
- Error handling services

**Rules**:

- Implements interfaces defined in `application/` or `domain/`
- Handles all external communication
- Framework-specific implementations (Angular HttpClient, etc.)

**Example Structure**:

```
infrastructure/
├── http/
│   ├── api-client.service.ts
│   ├── project-api.service.ts
│   └── issue-api.service.ts
├── repositories/
│   ├── project.repository.ts
│   └── issue.repository.ts
├── storage/
│   ├── local-storage.service.ts
│   └── session-storage.service.ts
├── interceptors/
│   ├── auth.interceptor.ts
│   └── error.interceptor.ts
└── websocket/
    └── websocket.service.ts
```

---

### Presentation Layer (`presentation/`)

**Purpose**: UI components, pages, layouts, and user interaction

**Contains**:

- Pages/views (routes)
- Components (UI building blocks)
- Layouts (base layout, page layouts)
- Feature modules/components
- Route guards
- View models (data prepared for display)

**Rules**:

- Depends on `application/` for business logic
- Uses `infrastructure/` services via `application/` layer
- Handles user interaction and display logic
- No direct business logic (delegates to application layer)

**Example Structure**:

```
presentation/
├── layout/
│   ├── base-layout.component.ts
│   └── auth-layout.component.ts
├── pages/
│   ├── landing/
│   ├── login/
│   ├── dashboard/
│   ├── projects/
│   └── issues/
├── components/
│   ├── issue-card/
│   └── project-list/
├── guards/
│   └── auth.guard.ts
└── view-models/
    └── issue-list.view-model.ts
```

---

## Dependency Flow

```
Presentation → Application → Domain
     ↓              ↓
Infrastructure → Domain
```

**Rules**:

1. **Presentation** depends on **Application** and **Infrastructure**
2. **Application** depends only on **Domain**
3. **Infrastructure** implements interfaces from **Application** or **Domain**
4. **Domain** has no dependencies (pure business logic)

---

## Component Organization Example

### Feature: Issue Management

```
presentation/pages/issues/
├── issue-list.page.ts          # Page component
├── issue-detail.page.ts        # Page component
└── components/
    ├── issue-card.component.ts
    └── issue-form.component.ts

application/
├── use-cases/
│   └── create-issue.use-case.ts
└── services/
    └── issue.service.ts

infrastructure/
└── http/
    └── issue-api.service.ts

domain/
├── entities/
│   └── issue.entity.ts
└── value-objects/
    └── issue-status.vo.ts
```

---

## Best Practices

1. **Keep domain pure**: No framework dependencies in domain layer
2. **Use interfaces**: Define contracts in application/domain, implement in infrastructure
3. **Single responsibility**: Each layer has a clear purpose
4. **Dependency injection**: Use Angular's DI to wire layers together
5. **State management**: Use Angular Signals in application layer
6. **Reusable components**: UI components go in `presentation/components/`
7. **Page components**: Route components go in `presentation/pages/`
8. **Layout components**: Layout components go in `presentation/layout/`

---

## Shared UI Library

The `libraries/shared-ui/` library contains **only reusable design components**:

- Button
- Input
- Card
- Modal
- Table
- List
- Icon
- Spinner
- Toast
- etc.

**Layout components belong in `app1/src/app/presentation/layout/`, NOT in shared-ui.**

---

_Last Updated: December 2024_
