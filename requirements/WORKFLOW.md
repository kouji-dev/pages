# Development Workflow

This document outlines the standard development workflow for contributing to the project.

## Overview

The development process follows a phase-based workflow: select a phase (e.g., 1.2), create a branch for that phase, then work through all subtasks within the phase one by one. For each subtask, we implement, test against Angular style guide, update the backlog, request review, and commit after confirmation. This continues until all subtasks in the phase are complete.

---

## Workflow Steps

### 1. Update Main Branch and Select a Phase

1. **Ensure you're on the main branch and up to date:**

   ```bash
   git checkout main
   git pull origin main
   ```

2. **Open the backlog files in `requirements/`:**
   - `PHASE_1_MVP_DEVELOPMENT.md`
   - `PHASE_2_ENHANCED_FEATURES_DEVELOPMENT.md`
   - `PHASE_3_ADVANCED_FEATURES_DEVELOPMENT.md`

3. **Select a phase to work on (e.g., 1.2, 1.3, 2.1):**
   - Select by priority order (Critical → High → Medium → Low)
   - Verify that all prerequisite phases/tasks are completed
   - Check task assignments if applicable
   - Example: Select Phase 1.2 (User & Organization Management)

4. **Review all subtasks within the selected phase:**
   - Note all subtasks that need to be completed
   - Identify dependencies between subtasks within the phase
   - Plan the order of implementation

---

### 2. Create Phase Branch

1. **Create a new branch for the entire phase:**

   ```bash
   git checkout -b phase/1.2-user-org-management
   ```

   **Branch naming convention:**
   - Format: `phase/{phase-id}-{short-description}`
   - Example: `phase/1.2-user-org-management`
   - Example: `phase/1.3-project-management`
   - Example: `phase/2.1-advanced-search`
   - Use kebab-case (lowercase with hyphens)
   - Keep description concise (2-4 words)
   - The branch will contain all commits for all subtasks within this phase

---

### 3. Work on Subtasks Iteratively

For each subtask within the selected phase, follow steps 4-13 below. Continue until all subtasks in the phase are complete.

**Example:** If working on Phase 1.2, you'll complete subtasks like:

- 1.2.1 User Management Backend
- 1.2.2 Organization Management Backend
- 1.2.10 User Profile Page
- etc.

---

### 4. Write Tests First (Test-Driven Development) - Optional but Recommended

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

### 5. Start Implementation

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

### 6. Build and Verify

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

### 7. Run Tests Again

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

### 8. Iterate Until Subtask Complete

Repeat steps 5-7 until:

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
- [ ] Subtask requirements met

---

### 9. Run Angular Style Guide Tests

**IMPORTANT: After implementation, verify code follows Angular style guide:**

1. **Run Angular style guide validation** (for frontend code):

   ```bash
   # Check Angular style guide compliance
   pnpm exec ng lint

   # Or use Angular's built-in style checker
   # Verify modern Angular patterns are followed:
   # - Use of signals, computed(), effect()
   # - inject() instead of constructor injection
   # - Standalone components
   # - OnPush change detection where appropriate
   ```

2. **Fix any style guide violations:**
   - Address Angular best practice violations
   - Ensure modern Angular APIs are used correctly
   - Fix architectural issues
   - Update code to match Angular style guide recommendations

3. **Verify style guide compliance:**
   - All Angular style guide checks should pass
   - Code should follow Angular best practices
   - Modern Angular patterns should be used consistently

**Note**: This step ensures our codebase maintains high quality and follows Angular best practices. For backend code, follow equivalent Python/FastAPI style guides.

---

### 10. Verify Code Compilation (Required Before Backlog Update)

**IMPORTANT: Before updating the backlog, ensure the code compiles without errors:**

1. **Run the build command to check for compilation errors:**

   ```bash
   # Frontend
   pnpm exec ng build

   # Backend
   # Follow backend build process (e.g., Poetry build, Docker build)
   ```

2. **Check for compilation errors:**
   - Look for TypeScript/compilation errors in the output
   - Check for missing imports, type errors, syntax errors
   - Verify all files are valid and compile correctly

3. **Fix compilation issues (if any):**
   - **Loop until all errors are fixed:**
     - Identify the compilation error
     - Fix the error in your code
     - Run the build command again
     - Repeat until build succeeds with no errors
   - Do not proceed to backlog update until code compiles successfully
   - All compilation errors must be resolved before moving forward

4. **Verify build succeeds:**
   - Build should complete without errors
   - No TypeScript compilation errors
   - All dependencies resolved correctly
   - Output confirms successful build

**Once the code compiles successfully, proceed to Step 11 (Update Backlog).**

**Note**: This step ensures that we never commit code that doesn't compile. If you encounter compilation errors, fix them in a loop until the build is successful before updating the backlog and committing.

---

### 11. Update Backlog

**IMPORTANT: Update the backlog BEFORE committing** so backlog changes are included in your commit:

1. **Open the backlog file**: `requirements/PHASE_1_MVP_DEVELOPMENT.md` (or appropriate phase file)
2. **Find the subtask**: Locate the subtask section matching your current work (e.g., `#### 1.2.10 User Profile Page`)
3. **Mark completed subtasks**: Change `- [ ]` to `- [x]` for completed subtasks
4. **Mark partially completed tasks**: Use `- [-]` for tasks that are partially done
5. **Update task status**: If subtask is complete, add `**Status**: ✅ Complete` to the subtask header
6. **Add notes if needed**: Add any relevant notes about progress or blockers

**Example:**

```bash
# Edit requirements/PHASE_1_MVP_DEVELOPMENT.md
# Find task 1.1.12 and mark completed subtasks:

- [x] Create loading spinner component (`spinner.component.ts`) in `shared-ui` library
  - [x] Standalone component
  - [x] Use `input()` for size variants (sm, md, lg)
  - [x] Use `input()` for color variants
- [x] Apply BOM CSS methodology
  - [x] Base `.spinner` class
  - [x] Size modifiers
  - [x] Use Tailwind `@apply` directives
- [x] Implement CSS animation for spinner
- [ ] Write component tests  # Still in progress
- [x] Export from `shared-ui` public API

# Save the file - it will be staged with your code changes in the next step
```

**Best Practices:**

- **Always update backlog before committing** - this ensures backlog changes are part of your commit
- Be accurate with your progress - don't mark tasks as complete until they're actually done
- Use `- [-]` for partially completed tasks to indicate progress
- Backlog updates should be staged and committed along with your code changes in the same commit

---

### 12. Stage Changes

1. **Stage your changes (including backlog updates):**

   ```bash
   git add .
   # Or selectively:
   git add <specific-files>
   git add requirements/PHASE_1_MVP_DEVELOPMENT.md  # Ensure backlog is included
   ```

   **Note**: The backlog file should be staged along with your code changes so backlog updates are committed together.

---

### 13. Request Review and Confirmation

**IMPORTANT: Always request review before committing:**

1. **Present a summary for review:**
   - List of changed files
   - Brief description of what was implemented for this subtask
   - Confirm that code compiles successfully (from Step 10)
   - Confirm that tests pass
   - Confirm that linting is clean
   - Confirm that Angular style guide tests pass (from Step 9)

2. **Wait for confirmation:**
   - Wait for explicit approval before proceeding to commit
   - Do not commit until confirmation is received
   - Address any feedback or requested changes before committing

3. **If confirmation is granted**, proceed to Step 14 (Commit Changes)
4. **If changes are requested**, address feedback and repeat from Step 10 (Verify Code Compilation)

**Example review request:**

```
I've completed subtask 1.2.10 (User Profile Page):

Changes:
- Created profile-page.ts with name editing functionality
- Created change-password-form.ts component
- Created avatar-upload.ts component
- Added /app/profile route
- Updated user-menu.ts to link to profile page
- Updated backlog to mark subtask as complete

✅ Code compiles successfully
✅ All tests pass
✅ Linting clean
✅ Angular style guide compliant

Ready for commit?
```

---

### 14. Commit Changes (After Confirmation)

**Only proceed if confirmation was received in Step 13:**

1. **Write a concise commit message:**

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

   git commit -m "feat(profile): complete subtask 1.2.10 - user profile page

   - Create profile page component with name editing
   - Create password change form with strength validation
   - Create avatar upload component with preview and progress
   - Add /app/profile route
   - Integrate all components with UserProfileService
   - Update backlog to mark subtask as complete"
   ```

2. **Commit the subtask:**
   - One commit per subtask (after review confirmation)
   - Include both code changes and backlog updates in the same commit
   - Make commits logical and self-contained
   - Each commit should represent a completed subtask

---

### 15. Move to Next Subtask or Complete Phase

1. **Check if there are more subtasks in the phase:**
   - Review the phase backlog
   - Identify the next subtask to work on
   - If more subtasks remain, return to Step 4 (Work on Subtasks Iteratively)

2. **If all subtasks in the phase are complete:**
   - All subtasks should be marked as complete in the backlog
   - Proceed to Step 16 (Push Phase Branch)

---

### 16. Push Phase Branch

1. **Push your phase branch:**

   ```bash
   git push -u origin phase/1.2-user-org-management
   ```

   If the branch already exists remotely:

   ```bash
   git push origin phase/1.2-user-org-management
   ```

2. **Verify push was successful:**
   - Check remote repository (GitHub/GitLab/etc.)
   - Branch should appear in remote
   - All commits for all subtasks should be visible

3. **Phase is complete:**
   - All subtasks within the phase have been committed
   - Branch is pushed and ready for merge/PR if applicable
   - Return to Step 1 to select the next phase

---

## Best Practices

### Branch Management

- **One branch per phase**: Each branch contains all subtasks for a complete phase (e.g., `phase/1.2-user-org-management`)
- **Keep branches focused**: Each branch should address a single phase
- **Don't mix phases**: Don't work on multiple phases in the same branch
- **Delete branches after merge**: Clean up merged branches once the phase is merged to main

### Commits

- **One commit per subtask**: After review confirmation, commit each completed subtask separately
- **Request review before commit**: Always present changes for review and wait for confirmation
- **Include backlog updates**: Commit backlog updates in the same commit as code changes for that subtask
- **Clear messages**: Write commit messages that explain "what" and "why" for the subtask
- **Atomic commits**: Each commit should represent one completed subtask

### Testing

- **Angular style guide tests**: Always run Angular style guide validation after implementation
- **Write tests first**: Follow TDD principles when possible
- **Test edge cases**: Don't just test the happy path
- **Maintain test coverage**: Aim for good coverage of critical paths

### Code Quality

- **Follow Angular best practices**: Ensure code follows Angular style guide
- **Follow linting rules**: Fix all linting errors before committing
- **Format code consistently**: Use Prettier for formatting
- **Review your own code**: Check your changes before requesting review
- **Verify compilation**: Always ensure code compiles before updating backlog and committing

### Documentation

- **Update backlog for each subtask**: Mark subtasks as complete in the backlog after implementation
- **Update documentation**: Keep docs in sync with code changes
- **Comment complex logic**: Add comments where code intent isn't obvious
- **Keep backlog accurate**: Only mark tasks as complete when they're actually finished

### Phase-Based Workflow

- **Work through subtasks sequentially**: Complete all subtasks in a phase before moving to the next phase
- **Maintain phase branch**: Keep all subtask commits on the same phase branch
- **Review before each commit**: Request review and confirmation before committing each subtask
- **Consistent commit pattern**: Follow the same process (implement → test → review → commit) for each subtask

---

## Workflow Diagram

```
┌─────────────────┐
│ Update Main     │
│ & Select Phase  │
│  (e.g., 1.2)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Create Phase    │
│ Branch          │
│ (phase/{id}-...)│
└────────┬────────┘
         │
         ▼
    ┌─────────┐
    │ For each│
    │ subtask │
    └────┬────┘
         │
         ▼
┌─────────────────┐
│  Write Tests    │
│  (TDD: Red)     │
│  (Optional)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Implement      │
│  Subtask        │
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
│ Run Angular     │   │
│ Style Guide     │   │
│   Tests         │   │
└────────┬────────┘   │
         │             │
         ▼             │
┌─────────────────┐   │
│ Verify Compile  │   │
│ (Loop Fix Errors)│   │
└────────┬────────┘   │
         │             │
         ▼             │
┌─────────────────┐   │
│ Update Backlog  │   │
│ (After Compile) │   │
└────────┬────────┘   │
         │             │
         ▼             │
┌─────────────────┐   │
│ Stage Changes   │   │
└────────┬────────┘   │
         │             │
         ▼             │
┌─────────────────┐   │
│ Request Review  │   │
│  & Confirmation │   │
└────────┬────────┘   │
         │             │
         ▼             │
    ┌────┴────┐        │
    │Confirmed│───No───┐
    └────┬────┘        │
         │ Yes         │
         ▼             │
┌─────────────────┐   │
│  Commit Subtask │   │
│  (One per task) │   │
└────────┬────────┘   │
         │             │
         ▼             │
    ┌─────────┐        │
    │ More    │        │
    │ Subtasks│───Yes──┘
    │  in     │
    │ Phase?  │
    └────┬────┘
         │ No
         ▼
┌─────────────────┐
│  Push Phase     │
│  Branch         │
└────────┬────────┘
         │
         ▼
    ┌─────────┐
    │ Select  │
    │ Next    │
    │ Phase   │
    └─────────┘
```

---

## Example Workflow Session

**Phase Selected:** Phase 1.2 - User & Organization Management

```bash
# Step 1: Update main and select phase
git checkout main
git pull origin main
# Review Phase 1.2 subtasks in requirements/PHASE_1_MVP_DEVELOPMENT.md

# Step 2: Create phase branch
git checkout -b phase/1.2-user-org-management

# === Subtask 1.2.10: User Profile Page ===

# Step 4: Write tests (optional)
# Create profile-page.spec.ts, change-password-form.spec.ts, etc.
# Run: pnpm exec ng test

# Step 5: Implement subtask
# Create profile-page.ts, change-password-form.ts, avatar-upload.ts
# Use modern Angular APIs, BOM CSS methodology

# Step 6: Build and lint
pnpm exec ng build
pnpm exec oxlint
pnpm exec prettier --write .

# Step 7: Run tests
pnpm exec ng test --watch=false

# Step 8: Iterate until subtask complete (if needed)

# Step 9: Run Angular style guide tests
pnpm exec ng lint
# Verify modern Angular patterns are used correctly

# Step 10: Verify code compilation (REQUIRED)
pnpm exec ng build
# If there are compilation errors, fix them and run again
# Loop until build succeeds:
#   - Fix error
#   - Run: pnpm exec ng build
#   - Repeat until no errors

# Step 11: Update backlog (AFTER code compiles)
# Edit requirements/PHASE_1_MVP_DEVELOPMENT.md
# Find subtask 1.2.10 and mark completed subtasks as [x]
# Save the file

# Step 12: Stage changes
git add .
git add requirements/PHASE_1_MVP_DEVELOPMENT.md  # Backlog updates included

# Step 13: Request review and confirmation
# Present summary:
# "I've completed subtask 1.2.10 (User Profile Page):
# - Created profile-page.ts, change-password-form.ts, avatar-upload.ts
# - Added /app/profile route
# - Updated user-menu.ts
# - Updated backlog
# ✅ Code compiles, tests pass, linting clean, Angular style guide compliant
# Ready for commit?"

# Step 14: Commit (only after confirmation)
git commit -m "feat(profile): complete subtask 1.2.10 - user profile page

- Create profile page component with name editing
- Create password change form with strength validation
- Create avatar upload component with preview and progress
- Add /app/profile route
- Update backlog to mark subtask as complete"

# Step 15: Move to next subtask
# Review Phase 1.2 backlog, identify next subtask (e.g., 1.2.11)
# Return to Step 4 for the next subtask

# === Subtask 1.2.11: Organization Settings Page ===
# Repeat Steps 4-14 for this subtask...

# === After all subtasks in Phase 1.2 are complete ===

# Step 16: Push phase branch
git push -u origin phase/1.2-user-org-management

# All subtasks in Phase 1.2 are now committed and pushed
# Ready for merge/PR if applicable

# Return to Step 1 to select next phase (e.g., Phase 1.3)
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
