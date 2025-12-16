# Design V2 Implementation Plan (Adapted)

**Version**: 1.0  
**Date**: December 15, 2025  
**Status**: Ready for Implementation

---

## Executive Summary

This plan outlines the implementation of Design V2 for the Pages application, **adapted to our existing codebase**. We will extend our current Tailwind CSS 4 setup and shared-ui library rather than rebuilding from scratch.

### Current State

- ✅ **Tailwind CSS 4** with `@theme` directive
- ✅ **Shared-UI Library** with Button, Card, Modal, Input, etc.
- ✅ **Notion-inspired design** (light theme)
- ✅ **Angular 21** with modern APIs (signals, standalone components)
- ✅ **Lexical editor** for rich text editing
- ✅ **Monorepo structure** (pnpm workspaces)

### Design Changes

- 🎨 **New color palette**: Purple/blue primary (`#4b2bee`), dark theme support
- 🎯 **Task management UI**: Kanban boards, task cards, activity timelines
- 📝 **Enhanced editor**: Block-based editing with better UX
- 🧩 **New components**: Status badges, priority indicators, avatar stacks, etc.

---

## 1. Design Tokens Extension

### 1.1 Update `libraries/shared-ui/src/styles.css`

Add task management tokens to the existing `@theme` block **without removing existing tokens**:

```css
@theme {
  /* ... existing Notion-style tokens ... */

  /* ========================================
   * Pages - Task Management Primary Colors
   * ======================================== */
  --color-pages-task-primary: #4b2bee;
  --color-pages-task-primary-light: #6d52f1;
  --color-pages-task-primary-hover: #3a1fc7;

  /* ========================================
   * Pages - Dark Theme Backgrounds
   * ======================================== */
  --color-pages-bg-dark: #131022;
  --color-pages-surface-dark: #1d1933;
  --color-pages-surface-hover: #292348;
  --color-pages-card-dark: #1e1933;

  /* ========================================
   * Pages - Dark Theme Borders
   * ======================================== */
  --color-pages-border-dark: #292348;
  --color-pages-border-hover: #3c3563;

  /* ========================================
   * Pages - Dark Theme Text
   * ======================================== */
  --color-pages-text-dark: #ffffff;
  --color-pages-text-secondary-dark: #9b92c9;
  --color-pages-text-tertiary-dark: #787774;

  /* ========================================
   * Pages - Task Status Colors
   * ======================================== */
  --color-pages-status-todo: #9b9a97;
  --color-pages-status-progress: #2ecc71;
  --color-pages-status-review: #a86cd4;
  --color-pages-status-done: #0f7b6c;

  /* ========================================
   * Pages - Task Priority Colors
   * ======================================== */
  --color-pages-priority-low: #89bbd0;
  --color-pages-priority-medium: #dfab01;
  --color-pages-priority-high: #d9730d;
  --color-pages-priority-critical: #e03e3e;
}
```

### 1.2 Add Dark Theme Overrides

In the same file, extend the dark theme section:

```css
[data-theme='dark'],
.dark {
  /* ... existing dark theme overrides ... */

  /* Task Management Dark Theme - Apply task colors when using task components */
  --color-primary: var(--color-pages-task-primary); /* Override primary for task management */
  --color-bg-primary: var(--color-pages-bg-dark);
  --color-bg-secondary: var(--color-pages-surface-dark);
  --color-bg-hover: var(--color-pages-surface-hover);
  --color-border-default: var(--color-pages-border-dark);
  --color-text-primary: var(--color-pages-text-dark);
  --color-text-secondary: var(--color-pages-text-secondary-dark);
}
```

### 1.3 Add Custom Scrollbar for Task Management

```css
/* Task Management Custom Scrollbar */
.pages-scrollbar::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.pages-scrollbar::-webkit-scrollbar-track {
  background: var(--color-pages-bg-dark);
}

.pages-scrollbar::-webkit-scrollbar-thumb {
  background: var(--color-pages-border-dark);
  border-radius: 4px;
}

.pages-scrollbar::-webkit-scrollbar-thumb:hover {
  background: var(--color-pages-task-primary);
}
```

---

## 2. Component Architecture

### Component Organization Strategy

**Shared-UI Library** (`libraries/shared-ui/src/lib/`):
- Generic, reusable base components (Badge, Avatar, Button, Card, etc.)
- No business logic or app-specific styling
- Can be used across multiple applications

**App1 Shared Components** (`clients/app1/src/app/shared/components/`):
- App-specific components built on top of shared-ui base components
- Contains business logic and domain-specific styling
- Task management components (StatusBadge, PriorityIndicator, AvatarStack, TaskCard)

### 2.1 Update Existing Shared-UI Components

#### Button Component (`libraries/shared-ui/src/lib/button/button.ts`)

**Add task-primary variant**:

```typescript
variant = input<'primary' | 'secondary' | 'danger' | 'ghost' | 'task-primary'>('primary');
```

**Add styles**:

```css
.button--task-primary {
  @apply text-white;
  background-color: var(--color-pages-task-primary);
  border-color: var(--color-pages-task-primary);
}

.button--task-primary:not(.button--disabled):hover {
  background-color: var(--color-pages-task-primary-hover);
  border-color: var(--color-pages-task-primary-hover);
}
```

### 2.2 New Base Components (Shared-UI Library)

#### A. Badge Component (`libraries/shared-ui/src/lib/badge/`)

**File**: `badge.ts`

```typescript
import { Component, input } from '@angular/core';

export type BadgeVariant = 'default' | 'primary' | 'success' | 'warning' | 'danger' | 'info';
export type BadgeSize = 'sm' | 'md' | 'lg';

@Component({
  selector: 'lib-badge',
  template: `
    <span
      class="badge"
      [class.badge--default]="variant() === 'default'"
      [class.badge--primary]="variant() === 'primary'"
      [class.badge--success]="variant() === 'success'"
      [class.badge--warning]="variant() === 'warning'"
      [class.badge--danger]="variant() === 'danger'"
      [class.badge--info]="variant() === 'info'"
      [class.badge--sm]="size() === 'sm'"
      [class.badge--md]="size() === 'md'"
      [class.badge--lg]="size() === 'lg'"
    >
      <ng-content></ng-content>
    </span>
  `,
  styles: [
    `
      @reference "#theme";

      .badge {
        @apply inline-flex items-center justify-center;
        @apply px-2.5 py-1 rounded-md;
        @apply text-xs font-medium;
        @apply transition-colors;
        @apply border;
      }

      /* Sizes */
      .badge--sm {
        @apply px-2 py-0.5 text-xs;
      }

      .badge--md {
        @apply px-2.5 py-1 text-xs;
      }

      .badge--lg {
        @apply px-3 py-1.5 text-sm;
      }

      /* Variants */
      .badge--default {
        @apply bg-gray-100 text-gray-700 border-gray-200;
        @apply dark:bg-gray-800 dark:text-gray-300 dark:border-gray-700;
      }

      .badge--primary {
        background-color: rgba(75, 43, 238, 0.1);
        color: var(--color-pages-task-primary);
        border-color: rgba(75, 43, 238, 0.2);
      }

      .badge--success {
        @apply bg-green-100 text-green-700 border-green-200;
        @apply dark:bg-green-900 dark:text-green-300 dark:border-green-800;
      }

      .badge--warning {
        @apply bg-yellow-100 text-yellow-700 border-yellow-200;
        @apply dark:bg-yellow-900 dark:text-yellow-300 dark:border-yellow-800;
      }

      .badge--danger {
        @apply bg-red-100 text-red-700 border-red-200;
        @apply dark:bg-red-900 dark:text-red-300 dark:border-red-800;
      }

      .badge--info {
        @apply bg-blue-100 text-blue-700 border-blue-200;
        @apply dark:bg-blue-900 dark:text-blue-300 dark:border-blue-800;
      }
    `,
  ],
})
export class Badge {
  variant = input<BadgeVariant>('default');
  size = input<BadgeSize>('md');
}
```

#### B. Avatar Component (`libraries/shared-ui/src/lib/avatar/`)

**File**: `avatar.ts`

```typescript
import { Component, input } from '@angular/core';

export type AvatarSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

@Component({
  selector: 'lib-avatar',
  template: `
    <div
      class="avatar"
      [class.avatar--xs]="size() === 'xs'"
      [class.avatar--sm]="size() === 'sm'"
      [class.avatar--md]="size() === 'md'"
      [class.avatar--lg]="size() === 'lg'"
      [class.avatar--xl]="size() === 'xl'"
      [style.background-image]="avatarUrl() ? 'url(' + avatarUrl() + ')' : null"
      [class.avatar--no-image]="!avatarUrl()"
      [title]="name()"
    >
      @if (!avatarUrl() && initials()) {
        <span class="avatar_initials">{{ initials() }}</span>
      }
    </div>
  `,
  styles: [
    `
      @reference "#theme";

      .avatar {
        @apply rounded-full;
        @apply bg-cover bg-center;
        @apply flex items-center justify-center;
        @apply flex-shrink-0;
        @apply border-2 border-white dark:border-gray-900;
      }

      /* Sizes */
      .avatar--xs {
        @apply w-6 h-6;
      }

      .avatar--sm {
        @apply w-8 h-8;
      }

      .avatar--md {
        @apply w-10 h-10;
      }

      .avatar--lg {
        @apply w-12 h-12;
      }

      .avatar--xl {
        @apply w-16 h-16;
      }

      .avatar--no-image {
        background-color: var(--color-pages-task-primary);
      }

      .avatar_initials {
        @apply text-white font-bold;
      }

      .avatar--xs .avatar_initials {
        @apply text-xs;
      }

      .avatar--sm .avatar_initials,
      .avatar--md .avatar_initials {
        @apply text-sm;
      }

      .avatar--lg .avatar_initials {
        @apply text-base;
      }

      .avatar--xl .avatar_initials {
        @apply text-lg;
      }
    `,
  ],
})
export class Avatar {
  name = input.required<string>();
  avatarUrl = input<string>();
  initials = input<string>();
  size = input<AvatarSize>('md');
}
```

### 2.3 New App-Specific Components (App1 Shared Components)

#### A. Status Badge (`clients/app1/src/app/shared/components/status-badge/`)

**File**: `status-badge.ts`

```typescript
import { Component, input } from '@angular/core';
import { Badge } from 'shared-ui';
import { Icon } from 'shared-ui';

export type StatusType = 'todo' | 'in-progress' | 'review' | 'done' | 'blocked';

@Component({
  selector: 'app-status-badge',
  imports: [Badge, Icon],
  template: `
    <lib-badge
      class="status-badge"
      [class.status-badge--todo]="status() === 'todo'"
      [class.status-badge--in-progress]="status() === 'in-progress'"
      [class.status-badge--review]="status() === 'review'"
      [class.status-badge--done]="status() === 'done'"
      [class.status-badge--blocked]="status() === 'blocked'"
    >
      @if (showDot()) {
        <span class="status-badge_dot"></span>
      }
      @if (showIcon()) {
        <lib-icon [name]="iconName()" size="xs" class="status-badge_icon"></lib-icon>
      }
      <span class="status-badge_label">{{ label() }}</span>
    </lib-badge>
  `,
  styles: [
    `
      @reference "#mainstyles";

      /* Status color overrides */
      .status-badge--todo {
        background-color: rgba(155, 154, 151, 0.1);
        color: var(--color-pages-status-todo);
        border-color: rgba(155, 154, 151, 0.2);
      }

      .status-badge--in-progress {
        background-color: rgba(46, 204, 113, 0.1);
        color: var(--color-pages-status-progress);
        border-color: rgba(46, 204, 113, 0.2);
      }

      .status-badge--review {
        background-color: rgba(168, 108, 212, 0.1);
        color: var(--color-pages-status-review);
        border-color: rgba(168, 108, 212, 0.2);
      }

      .status-badge--done {
        background-color: rgba(15, 123, 108, 0.1);
        color: var(--color-pages-status-done);
        border-color: rgba(15, 123, 108, 0.2);
      }

      .status-badge--blocked {
        background-color: rgba(224, 62, 62, 0.1);
        color: var(--color-pages-priority-critical);
        border-color: rgba(224, 62, 62, 0.2);
      }

      /* Animated dot */
      .status-badge_dot {
        @apply w-2 h-2 rounded-full;
        background-color: currentColor;
      }

      .status-badge--in-progress .status-badge_dot {
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
      }

      @keyframes pulse {
        0%,
        100% {
          opacity: 1;
        }
        50% {
          opacity: 0.5;
        }
      }

      .status-badge_icon {
        flex-shrink: 0;
      }

      .status-badge_label {
        white-space: nowrap;
      }
    `,
  ],
})
export class StatusBadge {
  status = input.required<StatusType>();
  label = input.required<string>();
  showDot = input(false);
  showIcon = input(false);
  iconName = input<string>('circle');
}
```

#### B. Priority Indicator (`clients/app1/src/app/shared/components/priority-indicator/`)

**File**: `priority-indicator.ts`

```typescript
import { Component, input } from '@angular/core';
import { Icon } from 'shared-ui';

export type PriorityLevel = 'low' | 'medium' | 'high' | 'critical';

@Component({
  selector: 'app-priority-indicator',
  imports: [Icon],
  template: `
    <span
      class="priority-indicator"
      [class.priority-indicator--low]="priority() === 'low'"
      [class.priority-indicator--medium]="priority() === 'medium'"
      [class.priority--high]="priority() === 'high'"
      [class.priority-indicator--critical]="priority() === 'critical'"
      [title]="label()"
    >
      @if (showIcon()) {
        <lib-icon [name]="iconName()" size="xs" class="priority-indicator_icon"></lib-icon>
      }
      @if (showLabel()) {
        <span class="priority-indicator_label">{{ label() }}</span>
      }
    </span>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .priority-indicator {
        @apply inline-flex items-center gap-1;
        @apply text-xs font-bold;
      }

      .priority-indicator--low {
        color: var(--color-pages-priority-low);
      }

      .priority-indicator--medium {
        color: var(--color-pages-priority-medium);
      }

      .priority-indicator--high {
        color: var(--color-pages-priority-high);
      }

      .priority-indicator--critical {
        color: var(--color-pages-priority-critical);
      }

      .priority-indicator_icon {
        flex-shrink: 0;
      }
    `,
  ],
})
export class PriorityIndicator {
  priority = input.required<PriorityLevel>();
  label = input.required<string>();
  showIcon = input(true);
  showLabel = input(false);
  iconName = input<string>('flag');
}
```

#### C. Avatar Stack (`clients/app1/src/app/shared/components/avatar-stack/`)

**File**: `avatar-stack.ts`

```typescript
import { Component, input } from '@angular/core';
import { Avatar } from 'shared-ui';

export interface AvatarUser {
  id: string;
  name: string;
  avatarUrl?: string;
  initials?: string;
}

@Component({
  selector: 'app-avatar-stack',
  imports: [Avatar],
  template: `
    <div class="avatar-stack">
      @for (user of displayedUsers(); track user.id) {
        <lib-avatar
          [name]="user.name"
          [avatarUrl]="user.avatarUrl"
          [initials]="user.initials"
          size="sm"
          class="avatar-stack_avatar"
        />
      }
      @if (overflowCount() > 0) {
        <div class="avatar-stack_overflow" [title]="overflowTitle()">
          +{{ overflowCount() }}
        </div>
      }
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .avatar-stack {
        @apply flex items-center;
      }

      .avatar-stack_avatar {
        @apply cursor-pointer transition-transform;
        margin-left: -0.5rem; /* Overlap */
      }

      .avatar-stack_avatar:first-child {
        margin-left: 0;
      }

      .avatar-stack_avatar:hover {
        @apply transform scale-110 z-10;
      }

      .avatar-stack_overflow {
        @apply w-8 h-8 rounded-full;
        @apply bg-gray-200 dark:bg-gray-700;
        @apply border-2 border-white dark:border-gray-900;
        @apply flex items-center justify-center;
        @apply text-xs font-bold;
        @apply text-gray-600 dark:text-gray-300;
        @apply cursor-pointer;
        margin-left: -0.5rem;
      }
    `,
  ],
})
export class AvatarStack {
  users = input.required<AvatarUser[]>();
  maxDisplay = input(3);

  displayedUsers = () => this.users().slice(0, this.maxDisplay());
  overflowCount = () => Math.max(0, this.users().length - this.maxDisplay());
  overflowTitle = () => {
    const overflow = this.users().slice(this.maxDisplay());
    return overflow.map((u) => u.name).join(', ');
  };
}
```

#### D. Task Card (`clients/app1/src/app/shared/components/task-card/`)

**File**: `task-card.ts`

```typescript
import { Component, input, output } from '@angular/core';
import { StatusBadge } from '../status-badge/status-badge';
import { PriorityIndicator } from '../priority-indicator/priority-indicator';
import { AvatarStack } from '../avatar-stack/avatar-stack';
import type { StatusType } from '../status-badge/status-badge';
import type { PriorityLevel } from '../priority-indicator/priority-indicator';
import type { AvatarUser } from '../avatar-stack/avatar-stack';

export interface TaskCardData {
  id: string;
  title: string;
  description?: string;
  status: StatusType;
  priority: PriorityLevel;
  assignees: AvatarUser[];
  tags?: string[];
  issueNumber?: string;
  dueDate?: Date;
}

@Component({
  selector: 'app-task-card',
  imports: [StatusBadge, PriorityIndicator, AvatarStack],
  template: `
    <div
      class="task-card"
      [class.task-card--compact]="variant() === 'compact'"
      (click)="cardClicked.emit(task())"
    >
      <div class="task-card_header">
        <h3 class="task-card_title">{{ task().title }}</h3>
        @if (task().description && variant() === 'detailed') {
          <p class="task-card_description">{{ task().description }}</p>
        }
      </div>

      @if (task().tags && task().tags.length > 0) {
        <div class="task-card_tags">
          @for (tag of task().tags; track tag) {
            <span class="task-card_tag">{{ tag }}</span>
          }
        </div>
      }

      <div class="task-card_footer">
        <div class="task-card_meta">
          @if (task().issueNumber) {
            <span class="task-card_issue-number">{{ task().issueNumber }}</span>
          }
          <app-status-badge [status]="task().status" [label]="task().status" [showDot]="true" />
        </div>

        <div class="task-card_actions">
          <app-priority-indicator
            [priority]="task().priority"
            [label]="task().priority"
            [showIcon]="true"
            [showLabel]="false"
          />
          @if (task().assignees.length > 0) {
            <app-avatar-stack [users]="task().assignees" [maxDisplay]="2" />
          }
        </div>
      </div>
    </div>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .task-card {
        @apply p-3 rounded-lg;
        @apply border border-gray-300 dark:border-gray-700;
        @apply bg-white dark:bg-gray-800;
        @apply cursor-pointer;
        @apply transition-all;
        @apply hover:shadow-md;
        @apply hover:border-primary;
      }

      .task-card_header {
        @apply mb-3;
      }

      .task-card_title {
        @apply text-sm font-medium;
        @apply text-gray-900 dark:text-white;
        @apply leading-snug;
      }

      .task-card_description {
        @apply text-xs text-gray-600 dark:text-gray-400;
        @apply mt-1;
        @apply line-clamp-2;
      }

      .task-card_tags {
        @apply flex flex-wrap gap-1 mb-3;
      }

      .task-card_tag {
        @apply px-2 py-0.5 rounded-md;
        @apply bg-blue-100 dark:bg-blue-900;
        @apply text-blue-700 dark:text-blue-300;
        @apply text-xs font-medium;
      }

      .task-card_footer {
        @apply flex items-center justify-between;
      }

      .task-card_meta {
        @apply flex items-center gap-2;
      }

      .task-card_issue-number {
        @apply text-xs font-mono text-gray-500 dark:text-gray-400;
      }

      .task-card_actions {
        @apply flex items-center gap-2;
      }

      /* Compact variant */
      .task-card--compact {
        @apply p-2;
      }

      .task-card--compact .task-card_description {
        @apply hidden;
      }
    `,
  ],
})
export class TaskCard {
  task = input.required<TaskCardData>();
  variant = input<'compact' | 'detailed'>('compact');
  cardClicked = output<TaskCardData>();
}
```

---

## 3. Implementation Phases

### Phase 1: Foundation (Week 1)

**Goal**: Set up task management design tokens and update core components

**Tasks**:

1. ✅ Add task management color tokens to `libraries/shared-ui/src/styles.css`
2. ✅ Add dark theme overrides
3. ✅ Add custom scrollbar styles
4. ✅ Update Button component with task-primary variant
5. ✅ Test theme switching between Notion and task management styles

**Deliverables**:

- Updated `styles.css` with task management tokens
- Button component with task-primary support
- Documentation of new tokens

### Phase 2: New Components (Week 2)

**Goal**: Create base and task management components

**Tasks**:

1. ✅ Create Badge component in shared-ui
2. ✅ Create Avatar component in shared-ui
3. ✅ Add Badge and Avatar to shared-ui `public-api.ts`
4. ✅ Create `clients/app1/src/app/shared/components/` folder
5. ✅ Create StatusBadge component (uses Badge)
6. ✅ Create PriorityIndicator component
7. ✅ Create AvatarStack component (uses Avatar)
8. ✅ Create TaskCard component
9. ✅ Write unit tests for new components

**Deliverables**:

- 2 new base components in shared-ui (Badge, Avatar)
- 4 new app-specific components in app1/shared (StatusBadge, PriorityIndicator, AvatarStack, TaskCard)
- Component tests
- Storybook stories (optional)

### Phase 3: Kanban Board (Week 3)

**Goal**: Implement kanban board with drag-and-drop

**Tasks**:

1. ✅ Update existing KanbanBoard component
2. ✅ Integrate TaskCard component
3. ✅ Add drag-and-drop using Angular CDK
4. ✅ Style columns with new design
5. ✅ Add column headers with counts
6. ✅ Test drag-and-drop functionality

**Deliverables**:

- Functional kanban board
- Drag-and-drop support
- New styling applied

### Phase 4: Task Details View (Week 4)

**Goal**: Create detailed task view with activity timeline

**Tasks**:

1. ✅ Create TaskDetailsLayout component
2. ✅ Create ActivityTimeline component
3. ✅ Create CommentThread component
4. ✅ Create AttachmentList component
5. ✅ Integrate with existing issue service
6. ✅ Add subtasks support

**Deliverables**:

- Task details page
- Activity timeline
- Comment system
- Attachment display

### Phase 5: Enhanced Page Editor (Week 5-6)

**Goal**: Improve existing Lexical editor with new design

**Tasks**:

1. ✅ Update editor toolbar with new styling
2. ✅ Add block controls (drag handles, add buttons)
3. ✅ Improve inline editing UX
4. ✅ Add embedded issue cards
5. ✅ Style code blocks with new design
6. ✅ Add callout blocks

**Deliverables**:

- Enhanced editor with new design
- Block-based editing improvements
- Better UX for content creation

### Phase 6: Integration & Polish (Week 7)

**Goal**: Integrate new components into existing pages

**Tasks**:

1. ✅ Update project pages with new components
2. ✅ Add theme toggle for dark mode
3. ✅ Responsive design testing
4. ✅ Accessibility audit
5. ✅ Performance optimization
6. ✅ Cross-browser testing

**Deliverables**:

- Fully integrated new design
- Theme toggle functionality
- Accessibility compliance
- Performance report

---

## 4. Technical Guidelines

**Important**: All components must follow the guidelines in:
- `requirements/ANGULAR_STYLE_GUIDE.md` - Angular conventions, naming, and modern APIs
- `requirements/TECHNOLOGIES.md` - Technology stack, BEM methodology, and Tailwind usage

### 4.1 Component Development

**File Naming** (per `requirements/ANGULAR_STYLE_GUIDE.md`):
- Component files: `component-name.ts` (NOT `.component.ts`)
- Component classes: NO "Component" suffix (e.g., `Badge`, not `BadgeComponent`)
- Match file name to class name in kebab-case

**Examples**:
- Class: `StatusBadge` → File: `status-badge.ts`
- Class: `PriorityIndicator` → File: `priority-indicator.ts`
- Class: `AvatarStack` → File: `avatar-stack.ts`

**Use Modern Angular APIs**:

```typescript
// ✅ Good - Modern Angular 21
import { Component, input, output, computed } from '@angular/core';

@Component({
  selector: 'app-status-badge',
  imports: [Badge, Icon],
  template: `...`,
  styles: [`...`],
})
export class StatusBadge {
  status = input.required<StatusType>();
  label = input.required<string>();
  displayLabel = computed(() => this.label().toUpperCase());
  onStatusChange = output<StatusType>();
}
```

**Use BEM Naming Convention** (Block Object Modifier):

Per `requirements/TECHNOLOGIES.md`, we use **BOM** (Block Object Modifier):
- **Block**: Main component name (e.g., `card`, `button`, `status-badge`)
- **Object**: Child element (e.g., `card_header`, `button_icon`, `status-badge_dot`)
- **Modifier**: Variations (e.g., `card--large`, `button--primary`, `status-badge--in-progress`)

```css
/* Block */
.status-badge {
  /* Main component styles */
}

/* Object (child element) */
.status-badge_dot {
  /* Child element styles */
}

.status-badge_label {
  /* Another child element */
}

/* Modifier (variation) */
.status-badge--in-progress {
  /* Variant styles */
}

/* Object with Modifier */
.status-badge_dot--animated {
  /* Child element variant */
}
```

**Reference Theme in Styles**:

For shared-ui components, use `@reference "#theme"`:
```css
@reference "#theme";

.badge {
  @apply px-2.5 py-1 rounded-md text-xs font-medium;
  background-color: var(--color-pages-task-primary);
}
```

For app1 components, use `@reference "#mainstyles"`:
```css
@reference "#mainstyles";

.status-badge {
  @apply inline-flex items-center gap-1.5;
  color: var(--color-pages-status-progress);
}
```

### 4.2 Styling Best Practices

**Component Structure** (per `requirements/TECHNOLOGIES.md`):
- Single TypeScript file per component (inline template and styles)
- Template uses **only CSS classes** (BEM naming)
- Styles use **Tailwind `@apply` directive**

**Example**:
```typescript
@Component({
  selector: 'app-status-badge',
  template: `
    <lib-badge class="status-badge status-badge--{{ status() }}">
      <span class="status-badge_label">{{ label() }}</span>
    </lib-badge>
  `,
  styles: [
    `
      @reference "#mainstyles";

      .status-badge {
        @apply inline-flex items-center gap-1.5;
      }

      .status-badge--in-progress {
        background-color: var(--color-pages-status-progress);
        @apply border border-green-200;
      }

      .status-badge_label {
        @apply text-xs font-medium;
      }
    `,
  ],
})
export class StatusBadge {
  status = input.required<StatusType>();
  label = input.required<string>();
}
```

**Tailwind Usage**:
- Use `@apply` for Tailwind utilities in component styles
- Combine Tailwind utilities with CSS variables for theme colors
- Follow BEM naming for all CSS classes

### 4.3 Testing Strategy

**Component Tests**:

```typescript
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { StatusBadge } from './status-badge';

describe('StatusBadge', () => {
  let component: StatusBadge;
  let fixture: ComponentFixture<StatusBadge>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [StatusBadge],
    }).compileComponents();

    fixture = TestBed.createComponent(StatusBadge);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should display correct status', () => {
    fixture.componentRef.setInput('status', 'in-progress');
    fixture.componentRef.setInput('label', 'In Progress');
    fixture.detectChanges();

    const badge = fixture.nativeElement.querySelector('.status-badge');
    expect(badge).toHaveClass('status-badge--in-progress');
  });
});
```

### 4.4 Accessibility

**Required Practices**:

- ✅ Proper ARIA labels for icon-only buttons
- ✅ Keyboard navigation support
- ✅ Focus indicators (already in theme)
- ✅ Color contrast compliance (WCAG AA)
- ✅ Screen reader support

**Example**:

```html
<button aria-label="Close modal" class="icon-button">
  <lib-icon name="x" />
</button>
```

---

## 5. Migration Strategy

### 5.1 Gradual Rollout

**Approach**: Feature-by-feature migration, not all-at-once

1. **Phase 1**: New task management features use new design
2. **Phase 2**: Existing pages get theme toggle
3. **Phase 3**: Full rollout after user feedback

### 5.2 Backward Compatibility

**Keep existing components working**:

- Don't remove Notion-style tokens
- Add new variants, don't replace existing ones
- Use feature flags for new features

### 5.3 Theme Toggle

**Implementation**:

```typescript
// theme.service.ts
export class ThemeService {
  private themeSignal = signal<'notion' | 'v2'>('notion');
  theme = this.themeSignal.asReadonly();

  toggleTheme() {
    const current = this.themeSignal();
    const next = current === 'notion' ? 'v2' : 'notion';
    this.themeSignal.set(next);
    this.applyTheme(next);
  }

  private applyTheme(theme: 'notion' | 'v2') {
    document.documentElement.setAttribute('data-design', theme);
    localStorage.setItem('design-theme', theme);
  }
}
```

---

## 6. Success Metrics

### 6.1 Technical Metrics

- ✅ **Bundle Size**: < 500KB increase
- ✅ **Performance**: No degradation in page load times
- ✅ **Accessibility**: WCAG AA compliance maintained
- ✅ **Test Coverage**: > 80% for new components

### 6.2 User Experience Metrics

- ✅ **Task Completion Time**: 20% faster for common tasks
- ✅ **User Satisfaction**: > 4.5/5 rating
- ✅ **Feature Adoption**: 80% of users try new features within 1 month

---

## 7. Next Steps

### Immediate Actions (This Week)

1. **Review this plan** with the team
2. **Set up development environment** (already done)
3. **Start Phase 1**: Add task management tokens to styles.css
4. **Create feature branch**: `feature/design-v2`

### Short-term (Next 2 Weeks)

- Complete Phase 1 and Phase 2
- Have core task management components ready
- Begin integration testing

### Long-term (Next 2 Months)

- Complete all 6 phases
- User testing and feedback
- Full rollout

---

## 8. Resources

### Design References

- **Task Details**: `design/v2/task_details/code.html`
- **Kanban Board**: `design/v2/task_board_(kanban_view)/code.html`
- **Page Editor**: `design/v2/page_editor/code.html`

### Documentation

- **Project Style Guides**:
  - `requirements/ANGULAR_STYLE_GUIDE.md` - Angular conventions, naming, modern APIs
  - `requirements/TECHNOLOGIES.md` - Technology stack, BEM methodology, component structure
- **External Documentation**:
  - **Tailwind CSS 4**: https://tailwindcss.com/docs
  - **Angular 21**: https://angular.dev
  - **Lexical Editor**: https://lexical.dev

### Tools

- **Storybook**: For component development (optional)
- **Vitest**: For unit testing
- **Oxlint**: For linting

---

**Document Version**: 1.0  
**Last Updated**: December 15, 2025  
**Author**: Development Team  
**Status**: Ready for Implementation

