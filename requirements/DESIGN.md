# Design System Documentation

This document outlines the design philosophy, layout structure, and design token usage for the Pages application.

---

## Design Philosophy

### Hybrid Approach: Notion Layout + Jira/Confluence Header Toolbar

Our design combines the best of both worlds:

- **Notion's Layout Structure**: Clean, minimal sidebar navigation with generous spacing and text-first approach
- **Jira/Confluence Header Toolbar**: Functional header with navigation, breadcrumbs, search, and quick actions

### Core Principles

1. **Text-First Design**: Prioritize text content with generous spacing (Notion-inspired)
2. **Functional Toolbar**: Header provides quick access to navigation, search, and actions (Jira/Confluence-inspired)
3. **Minimal Visual Chrome**: Clean interface with subtle colors and minimal distractions (Notion-inspired)
4. **Clear Hierarchy**: Structured information presentation with clear visual hierarchy (Jira/Confluence-inspired)
5. **Accessibility First**: Ensure all designs meet WCAG standards

---

## Layout Structure

### Overall Layout

```
┌─────────────────────────────────────────────────────────┐
│ HEADER TOOLBAR (Jira/Confluence Style)                  │
│ [Logo] [Breadcrumbs] [Search] [Actions] [User Menu]    │
├──────────┬──────────────────────────────────────────────┤
│          │                                              │
│ SIDEBAR  │  MAIN CONTENT AREA                          │
│ (Notion) │  (Notion-style: Clean, Spacious, Text-First)│
│          │                                              │
│ - Nav    │  - Generous padding                          │
│ - Pages  │  - Wide reading width                        │
│ - Spaces │  - Minimal visual distractions               │
│          │  - Focus on content                          │
│          │                                              │
└──────────┴──────────────────────────────────────────────┘
```

### Key Components

#### 1. Header Toolbar (Jira/Confluence Style)

- **Position**: Fixed at top
- **Height**: ~48-56px
- **Background**: White/light with subtle border
- **Components**:
  - Logo/Brand (left)
  - Breadcrumb navigation (left-center)
  - Global search (center)
  - Quick actions (right)
  - Notifications (right)
  - User menu (right)
- **Style**: Functional, slightly more prominent than Notion's minimal bar

#### 2. Sidebar (Notion Style)

- **Position**: Fixed left, collapsible
- **Width**: ~240-280px (wider than typical Jira sidebar)
- **Background**: Light beige/gray (Notion's `#f7f6f3`)
- **Style**:
  - Clean, minimal
  - Text-heavy navigation
  - Generous spacing between items
  - Subtle hover states
- **Components**:
  - Workspace selector
  - Navigation items (Projects, Spaces, etc.)
  - Page/space tree (collapsible)
  - Quick actions

#### 3. Main Content Area (Notion Style)

- **Style**:
  - Generous padding (Notion-style: ~96px sides on desktop)
  - Wide but readable max-width (~900-1000px centered)
  - Minimal visual chrome
  - Text-first presentation
- **Background**: White/light
- **Focus**: Content readability

---

## Color System

### Primary Palette (Notion Colors)

**Text Colors:**

- Default: `#37352f` (Notion's primary text)
- Secondary: `#9b9a97` (Notion gray)
- Tertiary: `#787774` (Muted gray)

**Background Colors:**

- Primary: `#ffffff` (White)
- Secondary: `#f7f6f3` (Notion's light beige - used for sidebar)
- Tertiary: `#ebeced` (Notion gray background)

**Semantic Colors (Based on Notion Palette):**

- Primary/Blue: `#0b6e99` (Notion blue - for links, primary actions)
- Success/Green: `#0f7b6c` (Notion green)
- Warning/Orange: `#d9730d` (Notion orange)
- Error/Red: `#e03e3e` (Notion red)
- Purple: `#6940a5` (Notion purple - for secondary actions)

**Full Notion Color Palette:**
See `libraries/shared-ui/src/styles.css` for complete color definitions including all Notion colors (gray, brown, orange, yellow, green, blue, purple, pink, red) with their background variants.

---

## Typography

### Font Family

- **Primary**: System font stack (Notion-style)
  ```css
  ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica,
  "Apple Color Emoji", Arial, sans-serif
  ```
- **Monospace**: For code blocks
  ```css
  ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace
  ```

### Font Sizes (Optimized for Text Reading)

- **Base**: 16px (comfortable reading)
- **Small**: 14px
- **Large**: 18px
- **Headings**: 20px, 24px, 30px, 36px

### Line Heights

- **Body**: 1.5-1.75 (generous for readability)
- **Headings**: 1.25 (tighter)

---

## Spacing System

### Notion-Inspired Generous Spacing

- **Content Padding**:
  - Desktop: 96px horizontal padding
  - Tablet: 48px
  - Mobile: 24px
- **Component Spacing**:
  - Between sections: 48-64px
  - Between elements: 16-24px
  - Within components: 8-16px

---

## Component Design Guidelines

### Buttons

- **Primary**: Notion blue (`#0b6e99`)
- **Style**: Subtle, minimal borders, gentle hover states
- **Sizes**: Small (compact), Medium (default), Large (prominent)

### Inputs

- **Style**: Minimal borders, subtle focus states
- **Focus**: Notion blue outline (2px)
- **Padding**: Generous for comfortable typing

### Cards

- **Background**: White
- **Border**: Subtle gray border or shadow
- **Padding**: Generous (24-32px)
- **Hover**: Subtle elevation change

### Modals/Dialogs

- **Background**: White with subtle shadow
- **Overlay**: Semi-transparent dark overlay
- **Max Width**: Comfortable reading width (~600px)

---

## Layout Patterns

### Page Layout (Notion Style)

```
┌─────────────────────────────────────────┐
│ [Header Toolbar - Jira/Confluence]     │
├──────────┬──────────────────────────────┤
│          │                              │
│ Sidebar  │  Content Area                │
│          │  ┌─────────────────────────┐ │
│          │  │ Title (Large, Bold)     │ │
│          │  ├─────────────────────────┤ │
│          │  │                         │ │
│          │  │ Content blocks with     │ │
│          │  │ generous spacing        │ │
│          │  │                         │ │
│          │  │ Wide but readable       │ │
│          │  │ max-width               │ │
│          │  │                         │ │
│          │  └─────────────────────────┘ │
│          │                              │
└──────────┴──────────────────────────────┘
```

### List/Table View (Jira/Confluence Style)

- More structured, compact spacing
- Clear columns and headers
- Action buttons and filters visible

---

## Design Tokens

All design tokens are centralized in `libraries/shared-ui/src/styles.css` using Tailwind CSS 4's CSS custom properties.

### Usage in Components

When creating components:

1. **Use CSS custom properties** from the theme:

   ```css
   .my-component {
     color: var(--color-text-primary);
     background: var(--color-bg-secondary);
     border-color: var(--color-border-default);
   }
   ```

2. **Use Tailwind utilities with @apply**:

   ```css
   .my-component {
     @apply text-[var(--color-text-primary)];
     @apply bg-[var(--color-bg-secondary)];
   }
   ```

3. **Reference semantic colors**:
   ```css
   .button--primary {
     background-color: var(--color-primary-500); /* Notion blue */
   }
   ```

---

## Responsive Breakpoints

- **Mobile**: < 640px
- **Tablet**: 640px - 1024px
- **Desktop**: > 1024px

### Responsive Behavior

- **Header Toolbar**:
  - Desktop: Full toolbar with all items
  - Tablet: Compact, some items in dropdown
  - Mobile: Minimal, hamburger menu
- **Sidebar**:
  - Desktop: Always visible (can collapse)
  - Tablet: Collapsible overlay
  - Mobile: Hidden by default, overlay when opened
- **Content Area**:
  - Desktop: Generous padding (96px)
  - Tablet: Moderate padding (48px)
  - Mobile: Compact padding (24px)

---

## Accessibility

### Color Contrast

- All text meets WCAG AA standards (4.5:1 for normal text)
- Focus states are clearly visible
- Error states use both color and icons/text

### Keyboard Navigation

- All interactive elements are keyboard accessible
- Focus order is logical
- Skip links available

### Screen Readers

- Semantic HTML structure
- ARIA labels where needed
- Alt text for images

---

## Design References

### Inspiration Sources

1. **Notion** (`design/notion home page.png`):
   - Sidebar layout
   - Typography and spacing
   - Color palette
   - Minimal visual chrome

2. **Jira/Confluence**:
   - Header toolbar functionality
   - Breadcrumb navigation
   - Quick actions and search
   - Information hierarchy

### Design Files

Reference images and design assets are stored in the `design/` folder:

- `notion home page.png`: Notion layout reference

---

## Component Library Structure

Components should follow BOM (Block Object Modifier) methodology:

```css
/* Block */
.card {
  /* Base styles */
}

/* Elements */
.card_header {
}
.card_body {
}
.card_footer {
}

/* Modifiers */
.card--large {
}
.card--compact {
}
.card_header--collapsed {
}
```

---

## Best Practices

1. **Always use design tokens** - Never hardcode colors, spacing, or typography
2. **Follow BOM methodology** - Use Block, Object, Modifier pattern
3. **Mobile-first** - Design for mobile, enhance for desktop
4. **Accessibility first** - Ensure WCAG compliance
5. **Text-first** - Prioritize readability and content
6. **Consistent spacing** - Use spacing scale consistently
7. **Subtle interactions** - Gentle hover states, smooth transitions

---

## Design Token Reference

See `libraries/shared-ui/src/styles.css` for complete design token definitions including:

- Color palette (Notion colors)
- Semantic colors (primary, secondary, success, warning, error, info)
- Typography scale
- Spacing scale
- Border radius
- Shadows
- Transitions

---

_Last Updated: December 2024_
