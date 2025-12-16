# Design V2 - Quick Summary

## What We're Building

A modern, dark-themed task management UI with:

- 🎨 Purple/blue color scheme (`#4b2bee`)
- 📋 Kanban boards with drag-and-drop
- 🎯 Task cards with status badges and priority indicators
- 💬 Activity timelines and comments
- 📝 Enhanced block-based page editor

## What We Already Have

✅ Tailwind CSS 4 with design tokens  
✅ Shared-UI component library  
✅ Angular 21 with modern APIs  
✅ Lexical editor for rich text  
✅ Notion-inspired light theme

## What We Need to Build

### New Base Components in Shared-UI (2)

1. **Badge** - Generic badge component with variants
2. **Avatar** - Generic avatar component with sizes

### New App-Specific Components in App1 (4)

1. **StatusBadge** - Shows task status with animated dot (uses Badge)
2. **PriorityIndicator** - Shows priority with colored icon
3. **AvatarStack** - Overlapping user avatars (uses Avatar)
4. **TaskCard** - Card for kanban board

### Updated Components (2)

1. **Button** - Add task-primary variant
2. **KanbanBoard** - Update with new styling

### New Pages/Views (2)

1. **Task Details** - Full task view with timeline
2. **Enhanced Editor** - Block-based editing improvements

## Implementation Timeline

| Phase | Duration | Focus                      |
| ----- | -------- | -------------------------- |
| 1     | Week 1   | Design tokens & Button     |
| 2     | Week 2   | New components             |
| 3     | Week 3   | Kanban board               |
| 4     | Week 4   | Task details view          |
| 5     | Week 5-6 | Enhanced page editor       |
| 6     | Week 7   | Integration & polish       |
| **Total** | **7 weeks** | **Complete V2 implementation** |

## Key Design Tokens to Add

```css
--color-pages-task-primary: #4b2bee;
--color-pages-bg-dark: #131022;
--color-pages-surface-dark: #1d1933;
--color-pages-text-secondary-dark: #9b92c9;
--color-pages-status-progress: #2ecc71;
--color-pages-priority-high: #d9730d;
```

## Migration Strategy

1. **Add task management tokens** without removing existing ones
2. **Create base components** (Badge, Avatar) in shared-ui library
3. **Create app-specific components** in app1/shared folder
4. **Update existing components** with new variants
5. **Gradual rollout** - feature by feature
6. **Theme toggle** - let users choose themes

## Files to Modify

### Core Files

- `libraries/shared-ui/src/styles.css` - Add task management tokens
- `libraries/shared-ui/src/lib/button/button.ts` - Add task-primary variant

### New Files to Create (Shared-UI)

- `libraries/shared-ui/src/lib/badge/badge.ts`
- `libraries/shared-ui/src/lib/avatar/avatar.ts`

### New Files to Create (App1 Shared)

- `clients/app1/src/app/shared/components/status-badge/status-badge.ts`
- `clients/app1/src/app/shared/components/priority-indicator/priority-indicator.ts`
- `clients/app1/src/app/shared/components/avatar-stack/avatar-stack.ts`
- `clients/app1/src/app/shared/components/task-card/task-card.ts`

## Success Criteria

✅ All new components have unit tests  
✅ No performance degradation  
✅ WCAG AA accessibility maintained  
✅ Works in all major browsers  
✅ User satisfaction > 4.5/5

## Next Steps

1. Review the full plan: `DESIGN_V2_IMPLEMENTATION_PLAN.md`
2. Create feature branch: `feature/design-v2`
3. Start Phase 1: Add task management design tokens
4. Create Badge and Avatar base components
5. Create StatusBadge component
6. Test and iterate

---

**For detailed implementation instructions, see**: `DESIGN_V2_IMPLEMENTATION_PLAN.md`

