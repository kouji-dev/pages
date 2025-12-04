# Development Workflow

This document outlines the standard development workflow for contributing to the project.

## Overview

The development process follows a structured cycle: task selection, branch creation, test-driven development, implementation, and iterative refinement until completion.

---

## Workflow Steps

### 1. Find and Select a Task

1. Open the backlog files in `requirements/`:
   - `PHASE_1_MVP_DEVELOPMENT.md`
   - `PHASE_2_ENHANCED_FEATURES_DEVELOPMENT.md`
   - `PHASE_3_ADVANCED_FEATURES_DEVELOPMENT.md`

2. **Select by priority order:**
   - Critical priority tasks first
   - High priority tasks second
   - Medium priority tasks third
   - Low priority tasks last

3. **Verify task dependencies:**
   - Check that all prerequisite tasks are completed
   - Review the "Dependencies" field in the task description
   - Ensure required infrastructure/features are in place

4. **Check task assignment:**
   - Verify the task is assigned to you (or your team)
   - Task assignments are noted in each task's "Assigned To" field

---

### 2. Create Feature Branch

1. **Ensure you're on the main branch and up to date:**

   ```bash
   git checkout main
   git pull origin main
   ```

2. **Create a new branch with task ID:**

   ```bash
   git checkout -b task/1.1.1-project-structure
   ```

   **Branch naming convention:**
   - Format: `task/{task-id}-{short-description}`
   - Example: `task/1.2.1-user-management-backend`
   - Example: `task/1.1.5-frontend-foundation`
   - Use kebab-case (lowercase with hyphens)
   - Keep description concise (2-4 words)

---

### 3. Write Tests First (Test-Driven Development)

1. **Identify what needs to be tested:**
   - Unit tests for functions/utilities
   - Component tests for Angular components
   - Integration tests for API endpoints
   - E2E tests for critical user flows

2. **Write tests before implementation:**
   - Frontend: Write tests in `.spec.ts` files
   - Backend: Write tests in `test_*.py` or `*_test.py` files
   - Start with failing tests (red phase)
   - Tests should clearly define expected behavior

3. **Run tests to verify they fail:**

   ```bash
   # Frontend
   pnpm exec ng test

   # Backend
   pytest tests/
   ```

---

### 4. Start Implementation

1. **Implement the feature to make tests pass:**
   - Follow project coding standards
   - Use modern Angular APIs (signals, input(), output(), inject(), etc.)
   - Follow DDD principles for architecture
   - Use BOM methodology for CSS (Tailwind with @apply)
   - Write clean, maintainable code

2. **Reference project guidelines:**
   - Check `requirements/TECHNOLOGIES.md` for tech stack details
   - Follow patterns established in existing code
   - Maintain consistency with project structure

---

### 5. Build and Verify

1. **Build the code:**

   ```bash
   # Frontend
   pnpm exec ng build

   # Backend
   # Follow backend build process (e.g., Poetry build, Docker build)
   ```

2. **Run linting:**

   ```bash
   pnpm exec oxlint
   pnpm exec prettier --check .
   ```

3. **Fix any build or linting errors:**
   - Address compilation errors
   - Fix linting violations
   - Resolve type errors
   - Format code with Prettier if needed

---

### 6. Run Tests Again

1. **Execute test suite:**

   ```bash
   # Frontend
   pnpm exec ng test --watch=false

   # Backend
   pytest tests/ -v
   ```

2. **Verify all tests pass:**
   - New tests should pass (green phase)
   - Existing tests should still pass (no regressions)
   - Check code coverage if configured

---

### 7. Iterate Until Complete

Repeat steps 4-6 until:

- ✅ All tests pass
- ✅ Code builds without errors
- ✅ Linting passes
- ✅ Feature matches task requirements
- ✅ Code follows project standards
- ✅ No regressions introduced

**Checklist before moving to commit:**

- [ ] Tests written and passing
- [ ] Code builds successfully
- [ ] Linting passes
- [ ] Type checking passes (TypeScript)
- [ ] Manual testing completed (if applicable)
- [ ] Task requirements met

---

### 8. Commit Changes

1. **Stage your changes:**

   ```bash
   git add .
   # Or selectively:
   git add <specific-files>
   ```

2. **Write a concise commit message:**

   **Commit message format:**

   ```
   <type>(<scope>): <subject>

   <body (optional)>
   ```

   **Types:**
   - `feat`: New feature
   - `fix`: Bug fix
   - `docs`: Documentation changes
   - `style`: Code style changes (formatting, etc.)
   - `refactor`: Code refactoring
   - `test`: Adding or updating tests
   - `chore`: Maintenance tasks
   - `build`: Build system changes
   - `ci`: CI/CD changes

   **Examples:**

   ```bash
   git commit -m "feat(auth): add user login endpoint"

   git commit -m "fix(ui): resolve button styling issue in card component"

   git commit -m "test(api): add integration tests for issue endpoints"

   git commit -m "feat(frontend): implement base layout component"
   ```

3. **Multiple commits per subtask are acceptable:**
   - You can commit after completing each subtask
   - This creates a clear history of progress
   - Example: Commit after writing tests, commit after implementing feature, commit after fixing bugs

4. **Commit frequently:**
   - Don't wait until everything is done
   - Make commits logical and self-contained
   - Each commit should represent a working state

---

### 9. Push to Remote

1. **Push your branch:**

   ```bash
   git push origin task/1.1.1-project-structure
   ```

   If the branch doesn't exist remotely yet:

   ```bash
   git push -u origin task/1.1.1-project-structure
   ```

2. **Verify push was successful:**
   - Check remote repository (GitHub/GitLab/etc.)
   - Branch should appear in remote
   - Commits should be visible

---

### 10. Update Backlog and Repeat

1. **Update task status in backlog:**
   - Mark completed subtasks with `[x]`
   - Mark partially completed tasks with `[-]`
   - Add notes about progress if needed
   - Commit backlog updates:
     ```bash
     git add requirements/*.md
     git commit -m "docs(backlog): update task 1.1.1 status"
     git push
     ```

2. **If task is fully complete:**
   - Mark all subtasks as done
   - Prepare for code review (if applicable)
   - Create pull request/merge request if working with a team

3. **Repeat the workflow:**
   - Return to step 1 (Find and Select a Task)
   - Select the next priority task
   - Start a new branch for the new task

---

## Best Practices

### Branch Management

- **One branch per task**: Don't mix multiple tasks in one branch
- **Keep branches focused**: Each branch should address a single task
- **Delete branches after merge**: Clean up merged branches

### Commits

- **Atomic commits**: Each commit should be a logical unit of work
- **Clear messages**: Write commit messages that explain "what" and "why"
- **Avoid large commits**: Break down work into smaller, manageable commits

### Testing

- **Write tests first**: Follow TDD principles when possible
- **Test edge cases**: Don't just test the happy path
- **Maintain test coverage**: Aim for good coverage of critical paths

### Code Quality

- **Follow linting rules**: Fix all linting errors before committing
- **Format code consistently**: Use Prettier for formatting
- **Review your own code**: Check your changes before committing

### Documentation

- **Update documentation**: Keep docs in sync with code changes
- **Comment complex logic**: Add comments where code intent isn't obvious
- **Update backlog**: Mark tasks as complete when done

---

## Workflow Diagram

```
┌─────────────────┐
│  Select Task    │
│  (by priority)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Create Branch   │
│ (task/{id}-...) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Write Tests    │
│  (TDD: Red)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Implement      │
│  Feature        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Build & Lint   │
│  (Fix Errors)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Run Tests      │
│  (Verify Pass)  │
└────────┬────────┘
         │
    ┌────┴────┐
    │  Done?  │───No───┐
    └────┬────┘        │
         │ Yes         │
         ▼             │
┌─────────────────┐   │
│  Commit Changes │   │
│  (Concise MSG)  │   │
└────────┬────────┘   │
         │             │
         ▼             │
┌─────────────────┐   │
│  Push to Remote │   │
└────────┬────────┘   │
         │             │
         ▼             │
┌─────────────────┐   │
│ Update Backlog  │   │
└────────┬────────┘   │
         │             │
         ▼             │
    ┌─────────┐        │
    │ Repeat  │────────┘
    └─────────┘
```

---

## Example Workflow Session

**Task Selected:** 1.1.5 Frontend Foundation - Create base layout component

```bash
# Step 1: Update and create branch
git checkout main
git pull origin main
git checkout -b task/1.1.5-base-layout

# Step 2: Write tests (if applicable)
# Create app.component.spec.ts with layout tests
# Run: pnpm exec ng test

# Step 3: Implement feature
# Create base-layout.component.ts with header, sidebar, main, footer
# Use modern Angular APIs, BOM CSS methodology

# Step 4: Build and lint
pnpm exec ng build
pnpm exec oxlint
pnpm exec prettier --write .

# Step 5: Run tests
pnpm exec ng test --watch=false

# Step 6: Commit (can be multiple commits)
git add .
git commit -m "test(layout): add tests for base layout component"
git commit -m "feat(layout): implement base layout with header and sidebar"
git commit -m "style(layout): apply BOM CSS methodology to layout styles"

# Step 7: Push
git push -u origin task/1.1.5-base-layout

# Step 8: Update backlog
# Edit requirements/PHASE_1_MVP_DEVELOPMENT.md
# Mark base layout subtasks as complete
git add requirements/PHASE_1_MVP_DEVELOPMENT.md
git commit -m "docs(backlog): mark base layout component as complete"
git push

# Step 9: Repeat with next task
```

---

## Troubleshooting

### Build Errors

- Check TypeScript errors: `pnpm exec ng build --verbose`
- Verify dependencies: `pnpm install`
- Check environment configuration

### Test Failures

- Run tests individually: `pnpm exec ng test --include='**/specific.spec.ts'`
- Check test isolation: Ensure tests don't depend on each other
- Verify mock data and fixtures

### Linting Errors

- Auto-fix when possible: `pnpm exec oxlint --fix`
- Format code: `pnpm exec prettier --write .`
- Check `.oxlintrc.json` for rule configuration

### Git Issues

- Branch conflicts: Rebase on main before pushing
- Commit issues: Use `git commit --amend` to fix last commit message
- Undo changes: `git reset --soft HEAD~1` to undo last commit, keep changes

---

## Additional Resources

- **Technologies**: See `requirements/TECHNOLOGIES.md` for tech stack details
- **Backlog**: See `requirements/PHASE_*_DEVELOPMENT.md` for task details
- **Git Workflow**: Follow standard Git best practices
- **Code Style**: Follow project linting and formatting rules

---

_Last Updated: December 2024_
