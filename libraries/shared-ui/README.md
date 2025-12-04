# Shared UI Library

A reusable component library containing design tokens and UI components used across all client applications.

---

## Purpose

This library provides **only reusable design system components**. It does NOT contain:

- ❌ Layout components (layouts belong in `app1/src/app/presentation/layout/`)
- ❌ Application-specific logic
- ❌ Business domain logic
- ❌ Pages or route components

---

## What This Library Contains

### Design Tokens

- Centralized theme and design tokens in `src/styles.css`
- Pages brand colors
- Typography scale
- Spacing system
- Shadows, borders, transitions

### Reusable UI Components

- **Button** - Button component with variants
- **Input** - Form input component
- **Card** - Card container component
- **Modal/Dialog** - Modal dialog component
- **Table** - Data table component
- **List** - List component
- **Icon** - Icon component
- **Spinner** - Loading spinner component
- **Toast** - Notification/toast component

All components:

- Follow BOM (Block Object Modifier) CSS methodology
- Use Tailwind CSS with `@apply` directives
- Use modern Angular APIs (signals, input(), output(), etc.)
- Are standalone components
- Have inline templates and styles

---

## Usage

### Import Design Tokens

Import the theme in your component styles:

```typescript
styles: [
  `
    @reference "#theme";
    
    .my-component {
      @apply ...;
    }
  `,
];
```

### Import Components

```typescript
import { Card, Button } from 'shared-ui';

@Component({
  imports: [Card, Button],
  // ...
})
```

---

## Component Development Guidelines

1. **Single File Components**: Each component is a single TypeScript file with inline template and styles
2. **BOM Methodology**: Use Block, Object, Modifier naming convention
3. **Design Tokens**: Always use design tokens from `#theme` reference
4. **Modern Angular**: Use signals, input(), output(), inject(), etc.
5. **Standalone**: All components are standalone
6. **No Business Logic**: Only presentation logic, no domain/business logic

---

## File Structure

```
shared-ui/src/
├── lib/
│   ├── card/              # Card component
│   ├── button/            # Button component
│   ├── input/             # Input component
│   ├── modal/             # Modal component
│   ├── table/             # Table component
│   ├── list/              # List component
│   ├── icon/              # Icon component
│   ├── spinner/           # Spinner component
│   └── toast/             # Toast component
├── styles.css             # Design tokens and theme
└── public-api.ts          # Library exports
```

---

## Design Tokens Reference

All design tokens are defined in `src/styles.css` using CSS custom properties:

- Colors: `--color-pages-*`, `--color-primary-*`, `--color-gray-*`
- Spacing: `--spacing-*`
- Typography: `--font-size-*`, `--font-weight-*`, `--line-height-*`
- Borders: `--radius-*`, `--border-*`
- Shadows: `--shadow-*`
- Transitions: `--transition-*`

See `src/styles.css` for complete token definitions.

---

_Last Updated: December 2024_
