# Angular Style Guide

This document outlines the Angular style guide conventions used in this project, based on the [official Angular Style Guide](https://angular.dev/style-guide).

**Last Updated**: December 2024

---

## File Naming Conventions

### Rule: Match File Names to the TypeScript Identifier

File names must match the TypeScript identifier (class name) within the file, using kebab-case (hyphenated lowercase).

**Examples**:

- Class: `BaseLayout` → File: `base-layout.ts`
- Class: `Card` → File: `card.ts`
- Class: `UserProfile` → File: `user-profile.ts`
- Class: `UserProfileService` → File: `user-profile.service.ts`
- Class: `AuthGuard` → File: `auth.guard.ts`
- Class: `IssueEntity` → File: `issue.entity.ts`
- Class: `CreateIssueUseCase` → File: `create-issue.use-case.ts`

**Note**: Component classes do NOT use the "Component" suffix (e.g., `Card`, not `CardComponent`). Component files do NOT use `.component.ts` extension, just `.ts` (e.g., `card.ts`, not `card.component.ts`).

### File Extensions

| Type         | Extension         | Example                      |
| ------------ | ----------------- | ---------------------------- |
| Component    | `.ts`             | `base-layout.ts`             |
| Service      | `.service.ts`     | `auth.service.ts`            |
| Guard        | `.guard.ts`       | `auth.guard.ts`              |
| Interceptor  | `.interceptor.ts` | `auth.interceptor.ts`        |
| Entity       | `.entity.ts`      | `issue.entity.ts`            |
| Value Object | `.vo.ts`          | `email.vo.ts`                |
| Use Case     | `.use-case.ts`    | `create-issue.use-case.ts`   |
| DTO          | `.dto.ts`         | `create-issue.dto.ts`        |
| Interface    | `.interface.ts`   | `repository.interface.ts`    |
| Type         | `.type.ts`        | `api-response.type.ts`       |
| Enum         | `.enum.ts`        | `issue-status.enum.ts`       |
| Pipe         | `.pipe.ts`        | `currency.pipe.ts`           |
| Directive    | `.directive.ts`   | `click-outside.directive.ts` |
| Module       | `.module.ts`      | `shared.module.ts`           |
| Test         | `.spec.ts`        | `base-layout.spec.ts`        |
| Route        | `.routes.ts`      | `app.routes.ts`              |

### Special Cases

- **Root Component**: The root `App` class can use `app.ts` (single word, no extension needed for the root)
- **Routes**: Route files use `.routes.ts` (e.g., `app.routes.ts`, `issue.routes.ts`)
- **Configuration**: Config files use `.config.ts` (e.g., `app.config.ts`)

---

## Component Structure

### Single File Components (Inline Template & Styles)

**All components use inline templates and styles** (no separate `.html` or `.css` files).

```typescript
@Component({
  selector: 'app-base-layout',
  imports: [RouterOutlet],
  template: `
    <div class="layout">
      <!-- Component template -->
    </div>
  `,
  styles: [
    `
      @reference "#theme";

      .layout {
        @apply ...;
      }
    `,
  ],
  standalone: true,
})
export class BaseLayoutComponent {
  // Component logic
}
```

### File Structure Example

```
feature/
├── feature.ts                    # Component (inline template & styles)
├── feature.spec.ts               # Component tests
├── feature.service.ts            # Service
├── feature.service.spec.ts       # Service tests
└── feature.routes.ts             # Routes (if feature routing)
```

---

## Naming Conventions

### Classes

- **UpperCamelCase** (PascalCase)
- **Components**: NO suffix (e.g., `Card`, `BaseLayout`, `UserProfile`)
- **Services**: Suffix with `Service` (e.g., `AuthService`, `UserService`)
- **Guards**: Suffix with `Guard` (e.g., `AuthGuard`, `RoleGuard`)
- **Entities**: Suffix with `Entity` (e.g., `IssueEntity`, `UserEntity`)
- **Use Cases**: Suffix with `UseCase` (e.g., `CreateIssueUseCase`)

**Examples**:

- `BaseLayout` (component - no suffix)
- `Card` (component - no suffix)
- `AuthService` (service)
- `AuthGuard` (guard)
- `IssueEntity` (entity)
- `CreateIssueUseCase` (use case)

### Interfaces

- **UpperCamelCase** (PascalCase)
- No prefix (avoid `I` prefix)

**Examples**:

- `UserRepository`
- `IssueRepository`
- `ApiResponse`

### Enums

- **UpperCamelCase** (PascalCase)
- Singular nouns
- Enum members: `UPPER_SNAKE_CASE`

**Examples**:

```typescript
export enum IssueStatus {
  TODO = 'todo',
  IN_PROGRESS = 'in_progress',
  DONE = 'done',
}
```

### Types

- **UpperCamelCase** (PascalCase)

**Examples**:

```typescript
export type IssuePriority = 'low' | 'medium' | 'high' | 'critical';
```

### Variables and Properties

- **camelCase**

**Examples**:

```typescript
const userProfile = {};
const isLoading = signal(false);
const issueList = signal<Issue[]>([]);
```

### Constants

- **UPPER_SNAKE_CASE** for true constants

**Examples**:

```typescript
const API_BASE_URL = 'https://api.example.com';
const MAX_RETRY_ATTEMPTS = 3;
```

### Methods/Functions

- **camelCase**
- Verb-based names (e.g., `getUser`, `createIssue`, `handleSubmit`)

**Examples**:

```typescript
getUser(id: string): Observable<User> {}
createIssue(issue: CreateIssueDto): void {}
handleSubmit(): void {}
```

### Selectors

- **kebab-case** with prefix
- Prefix: `app-` for app components, `lib-` for library components

**Examples**:

- `app-base-layout`
- `app-user-profile`
- `lib-card`
- `lib-button`

### CSS Classes (BOM Methodology)

- **BOM naming**: `block`, `block_object`, `block--modifier`, `block_object--modifier`
- All lowercase with underscores for objects and double dashes for modifiers

**Examples**:

- `.layout`
- `.layout_header`
- `.layout--sidebar-open`
- `.layout_header--collapsed`
- `.card`
- `.card_body`
- `.card--large`

---

## Component Decorator Conventions

### Standalone Components

All components are **standalone** (no NgModules).

```typescript
@Component({
  selector: 'app-feature',
  imports: [CommonModule, RouterOutlet], // Explicit imports
  template: `...`,
  styles: [`...`],
  standalone: true, // Always true
})
export class FeatureComponent {}
```

### Component Metadata Order

1. `selector`
2. `imports` (if standalone)
3. `template`
4. `styles`
5. `standalone: true`
6. Other properties (e.g., `changeDetection`)

---

## Modern Angular APIs

### Use Modern APIs

**Required**: Use Angular's latest APIs:

- ✅ `input()` instead of `@Input()`
- ✅ `output()` instead of `@Output()`
- ✅ `model()` for two-way binding
- ✅ `signal()` for reactive state
- ✅ `computed()` for derived state
- ✅ `effect()` for side effects
- ✅ `inject()` instead of constructor injection
- ✅ `httpResource()` for HTTP requests
- ✅ `resource()` for async resources
- ✅ New template blocks: `@if`, `@for`, `@switch`, `@defer`
- ✅ Standalone components

**Examples**:

```typescript
@Component({
  selector: 'app-card',
  // ...
})
export class Card {
  // Modern inputs
  title = input.required<string>();
  size = input<'small' | 'medium' | 'large'>('medium');

  // Modern outputs
  onClose = output<void>();

  // Signals
  isCollapsed = signal(false);

  // Computed
  displayTitle = computed(() => this.title().toUpperCase());

  // Inject (not constructor)
  private logger = inject(LoggerService);

  // Effects
  constructor() {
    effect(() => {
      console.log('Title changed:', this.title());
    });
  }
}
```

---

## Project Structure

### DDD Structure (app1)

```
app1/src/app/
├── domain/              # Domain layer
│   ├── entities/
│   ├── value-objects/
│   ├── services/
│   └── events/
├── application/         # Application layer
│   ├── use-cases/
│   ├── services/
│   ├── dtos/
│   └── state/
├── infrastructure/      # Infrastructure layer
│   ├── http/
│   ├── repositories/
│   ├── storage/
│   ├── interceptors/
│   └── websocket/
└── presentation/        # Presentation layer
    ├── layout/
    ├── pages/
    ├── components/
    ├── guards/
    └── view-models/
```

### Shared UI Library Structure

```
shared-ui/src/lib/
├── button/
│   └── button.ts
├── card/
│   └── card.ts
├── input/
│   └── input.ts
├── modal/
│   └── modal.ts
├── styles.css          # Design tokens
└── public-api.ts       # Exports
```

---

## Code Organization

### Component Class Order

1. **Imports**
2. **Component decorator**
3. **Class declaration**
4. **Public inputs/outputs** (using `input()`, `output()`, `model()`)
5. **Signals and computed** (reactive state)
6. **Private properties** (using `inject()` or signals)
7. **Constructor** (if needed)
8. **Public methods**
9. **Private methods**
10. **Lifecycle hooks** (if needed)

**Example**:

```typescript
import { Component, signal, input, computed, inject } from '@angular/core';

@Component({
  selector: 'app-feature',
  imports: [],
  template: `...`,
  styles: [`...`],
  standalone: true,
})
export class Feature {
  // Inputs
  title = input.required<string>();

  // Signals
  isVisible = signal(true);

  // Computed
  displayTitle = computed(() => this.title().toUpperCase());

  // Injected services
  private logger = inject(LoggerService);

  // Public methods
  handleClick(): void {
    this.isVisible.set(false);
  }

  // Private methods
  private logAction(action: string): void {
    this.logger.log(action);
  }
}
```

---

## CSS Styling

### BOM Methodology

Use **Block Object Modifier (BOM)** naming for CSS classes:

- **Block**: Main component name (e.g., `card`, `button`)
- **Object**: Child element (e.g., `card_header`, `button_icon`)
- **Modifier**: Variation (e.g., `card--large`, `button--primary`)

### Tailwind CSS

- Use `@reference "#theme";` at the top of component styles
- Use `@apply` directive for Tailwind utilities
- Use design tokens from the theme

**Example**:

```typescript
styles: [
  `
    @reference "#theme";

    .card {
      @apply rounded-lg shadow-md bg-pages-bg-primary p-6;
    }

    .card_header {
      @apply flex items-center justify-between mb-4;
    }

    .card--large {
      @apply p-8;
    }
  `,
];
```

---

## Testing

### Test File Naming

- Test files: `*.spec.ts`
- Match the component/service file name

**Examples**:

- `base-layout.spec.ts`
- `auth.service.spec.ts`

### Test Structure

```typescript
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Feature } from './feature';

describe('Feature', () => {
  let component: Feature;
  let fixture: ComponentFixture<Feature>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Feature],
    }).compileComponents();

    fixture = TestBed.createComponent(Feature);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
```

---

## Best Practices

### DO

✅ Use kebab-case for file names  
✅ Match file names to TypeScript identifiers  
✅ Use inline templates and styles  
✅ Use modern Angular APIs (`input()`, `output()`, `signal()`, etc.)  
✅ Use standalone components  
✅ Use `inject()` for dependency injection  
✅ Use BOM methodology for CSS classes  
✅ Use design tokens from `#theme` reference  
✅ Use descriptive, verb-based method names  
✅ Use UpperCamelCase for classes  
✅ Omit "Component" suffix from component class names  
✅ Omit `.component` from component file names (use `.ts` only)  
✅ Use camelCase for variables and methods

### DON'T

❌ Use separate `.html` or `.css` files (use inline)  
❌ Use `@Input()` or `@Output()` decorators (use `input()`, `output()`)  
❌ Use NgModules (use standalone components)  
❌ Use constructor injection (use `inject()`)  
❌ Use prefixes like `I` for interfaces  
❌ Mix naming conventions  
❌ Use unclear or abbreviated names

---

## References

- [Angular Style Guide](https://angular.dev/style-guide)
- [Angular Signals](https://angular.dev/guide/signals)
- [Standalone Components](https://angular.dev/guide/components/importing)

---

_Last Updated: December 2024_
