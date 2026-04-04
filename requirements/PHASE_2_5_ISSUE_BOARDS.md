# Phase 2.5: Issue Boards & Board Management (Weeks 25-32)

**Timeline**: Weeks 25-32 (8 weeks)  
**Goal**: Implémenter un système complet de Issue Boards avec labels, colonnes dynamiques, drag & drop avec label swapping, gestion de multiples boards, scope configuration, swimlanes, group boards et focus mode.

### Dependencies: Phase 1.3 (Issues), Phase 2.1 (Sprints)

**Note**: Cette phase implémente un système complet de boards pour la gestion visuelle des issues, inspiré de GitLab. Les boards permettent de créer des vues personnalisées avec des colonnes dynamiques basées sur des critères (labels, assignés, milestones).

**Implementation status** (backend + **Angular `clients/app1` frontend** audit):

| Phase   | Description                              | Status                                                                                                                 |
| ------- | ---------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| 2.5.1   | Labels System Backend                    | ✅ Done                                                                                                                |
| 2.5.2   | Labels System Frontend                   | 🟨 Partial — see §2.5.2; **component tests** still open                                                                |
| 2.5.3   | Issue Boards Data Model & CRUD Backend   | ✅ Done                                                                                                                |
| 2.5.4   | Issue Boards Basic Frontend              | 🟨 Partial — board **embedded in project detail** (no standalone `board-page`); quick create via API; see §2.5.4       |
| 2.5.5   | Board Lists (Columns) Backend            | ✅ Done                                                                                                                |
| 2.5.6   | Board Lists (Columns) Frontend           | 🟨 Partial — see §2.5.6; column **reorder** + comment/subtask counts on cards still open                               |
| 2.5.7   | Drag & Drop with Label Swapping Backend  | ✅ Done                                                                                                                |
| 2.5.8   | Drag & Drop with Label Swapping Frontend | 🟨 Partial — CDK + `moveBoardIssue` + rollback on error; **optimistic** + tests still open; same-column = client-only  |
| 2.5.9   | Multiple Boards Management Backend       | ✅ Done                                                                                                                |
| 2.5.10  | Multiple Boards Management Frontend      | 🟨 Partial — see §2.5.10; **edit board** + **reorder boards** + API `search` from UI still open                        |
| 2.5.11  | Board Scope Configuration Backend        | ✅ Done                                                                                                                |
| 2.5.12+ | Board Scope & filtering Frontend         | 🟨 Partial — see §2.5.12 / §2.5.14; full **scope modal** + spec **filter bar** still open                              |
| 2.5.13  | Real-Time Filtering Backend              | ✅ Done                                                                                                                |
| 2.5.14  | Real-Time Filtering Frontend             | 🟨 Partial — same as toolbar scope + per-column search (client); not full bar + debounced global search                |
| 2.5.15  | Swimlanes Backend                        | ✅ Done                                                                                                                |
| 2.5.16  | Swimlanes Frontend                       | 🟨 Partial — type toggle + API; **no swimlane rows** (lists flattened into one column strip); DnD across swimlanes N/A |
| 2.5.17  | Group Boards Backend                     | ✅ Done — includes `DELETE /boards/{id}/projects/{project_id}`                                                         |
| 2.5.18  | Group Boards Frontend                    | 🟨 Partial — create group board + badge + `project_key` on card; **manage projects** UI still open                     |
| 2.5.19  | Focus Mode Frontend                      | 🟨 Partial — per-project **localStorage**, focus toggle, hide header chrome, **ESC** + floating exit; see §2.5.19      |

**Frontend detail**: each phase below that ships UI includes a **“Frontend implementation status (`clients/app1`)”** table (files under `clients/app1/src/app/features/projects/…` and `shared/components/issue-card`).

---

## Phase 2.5.1: Labels System Backend ✅ (Done)

**Priority**: High  
**Estimated Time**: 3-4 days  
**Dependencies**: Phase 1.3.2  
**Assigned To**: BATATA1  
**Status**: Implemented (models, migration, API, unit/integration/functional tests)

**Backend Tasks**:

- Design label data model
  - Labels table (id, project_id, name, color, description, created_at, updated_at)
  - IssueLabels table (id, issue_id, label_id, created_at) - many-to-many relationship
- Create label creation endpoint (POST /api/v1/projects/:id/labels)
  - Validate unique name per project
  - Validate color format (hex)
- Create label retrieval endpoint (GET /api/v1/labels/:id)
- Create label list endpoint (GET /api/v1/projects/:id/labels)
  - Pagination support
  - Search by name
- Create label update endpoint (PUT /api/v1/labels/:id)
- Create label deletion endpoint (DELETE /api/v1/labels/:id)
  - Handle cascade deletion from IssueLabels
- Create add label to issue endpoint (POST /api/v1/issues/:id/labels)
- Create remove label from issue endpoint (DELETE /api/v1/issues/:id/labels/:labelId)
- Create issue labels list endpoint (GET /api/v1/issues/:id/labels)
- Write label API tests (unit, integration, functional)

**Deliverables**:

- Label data model and migrations
- Label CRUD API endpoints
- Issue-label association endpoints
- API tests (unit, integration, functional)

---

## Phase 2.5.2: Labels System Frontend

**Priority**: High  
**Estimated Time**: 2-3 days  
**Dependencies**: 2.5.1, Phase 1.3.6  
**Assigned To**: BATATA2

### Frontend implementation status (`clients/app1`)

| Area             | Done | Notes                                                                                                                                          |
| ---------------- | ---- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| Label CRUD UI    | ✅   | `project-settings-page.ts` — list with color swatch, create / edit / delete via `create-label-modal`, `edit-label-modal`, `delete-label-modal` |
| Label selector   | ✅   | `label-selector.ts` — multi-select in dropdown, color dots, **search** filter on labels                                                        |
| Issue forms      | ✅   | `create-issue-modal.ts`, `edit-issue-modal.ts` — `LabelSelector`, optional inline create via `CreateLabelModal`, persists `label_ids`          |
| Issue cards      | ✅   | `issue-card.ts` — label chips with hex color styling                                                                                           |
| Loading / errors | ✅   | Settings labels section + toasts on mutations; selector empty states                                                                           |
| Component tests  | ⬜   | Spec calls for dedicated tests still open (`project-settings-page.spec.ts` may cover part of settings only)                                    |

**Frontend Tasks**:

- Create label management UI
  - Label list component
  - Create label modal
  - Edit label modal
  - Delete label confirmation
- Create label selector component
  - Multi-select dropdown
  - Color indicators
  - Search functionality
- Integrate labels into issue creation form
- Integrate labels into issue edit form
- Display labels on issue cards (with colors)
- Add loading states and error handling
- Write component tests

**Deliverables**:

- Label management UI
- Label selector component
- Labels in issue forms and cards
- Component tests

---

## Phase 2.5.3: Issue Boards Data Model & CRUD Backend ✅ (Done)

**Priority**: High  
**Estimated Time**: 4-5 days  
**Dependencies**: 2.5.1  
**Assigned To**: BATATA1  
**Status**: Implemented (models, migration, API, unit/integration/functional tests, 100% coverage use cases)

**Backend Tasks**:

- Design board data model
  - Boards table (id, project_id, name, description, scope_config (JSON), is_default, position, created_by, created_at, updated_at)
  - BoardLists table (id, board_id, list_type, list_config (JSON), position, created_at, updated_at)
    - list_type: 'label', 'assignee', 'milestone'
    - list_config: stores the specific label_id, user_id, or milestone_id
- Create board creation endpoint (POST /api/v1/projects/:id/boards)
  - Validate project access
  - Set default board if first board
- Create board retrieval endpoint (GET /api/v1/boards/:id)
  - Include board lists
  - Include scope configuration
- Create board list endpoint (GET /api/v1/projects/:id/boards)
  - Pagination support
  - Sort by position
- Create board update endpoint (PUT /api/v1/boards/:id)
  - Update name, description, scope_config
  - Update position
- Create board deletion endpoint (DELETE /api/v1/boards/:id)
  - Handle cascade deletion of board lists
  - Prevent deletion of last board
- Write board CRUD API tests (unit, integration, functional)

**Deliverables**:

- Board data model and migrations
- Board CRUD API endpoints
- API tests (unit, integration, functional)

---

## Phase 2.5.4: Issue Boards Basic Frontend

**Priority**: High  
**Estimated Time**: 3-4 days  
**Dependencies**: 2.5.3, Phase 1.3.8  
**Assigned To**: BATATA2

### Frontend implementation status (`clients/app1`)

| Area            | Done | Notes                                                                                                                                                                 |
| --------------- | ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Board surface   | ✅   | **Board tab** on `project-detail-page.ts` — toolbar + `app-kanban-board` (not a separate `board-page` route)                                                          |
| Board selector  | ✅   | `board-selector.ts` — dropdown, **client-side** name filter (`lib-input`), create project board + **Create Group Board**                                              |
| Create board    | 🟨   | `handleCreateBoard` / `handleCreateGroupBoard` in `project-detail-page.ts` — **API-only** default names (`Board N`, `Group Board N`); no name/description/scope modal |
| Switch board    | ✅   | `boardSelected` → `selectedBoardId` → `app-kanban-board [boardId]`                                                                                                    |
| Board list API  | ✅   | `board.service.ts` + load in project detail                                                                                                                           |
| BOM CSS         | ✅   | Kanban / project-detail use scoped component styles                                                                                                                   |
| Component tests | ⬜   | Open per spec                                                                                                                                                         |

**Frontend Tasks**:

- Create board page component (`board-page.ts`)
  - Board header (name, description, actions)
  - Board content area (columns container)
- Create board selector component
  - Dropdown with search
  - List of available boards
  - Create new board button
- Create board creation modal
  - Name and description inputs
  - Scope configuration (initial)
- Integrate with board list API
- Implement board switching functionality
- Apply BOM CSS methodology
- Write component tests

**Deliverables**:

- Board page component
- Board selector component
- Board creation modal
- Component tests

---

## Phase 2.5.5: Board Lists (Columns) Backend ✅ (Done)

**Priority**: High  
**Estimated Time**: 3-4 days  
**Dependencies**: 2.5.3, 2.5.1  
**Assigned To**: BATATA1  
**Status**: Implemented (use cases, API, unit/integration/functional tests)

**Backend Tasks**:

- Create board list creation endpoint (POST /api/v1/boards/:id/lists)
  - Validate list_type (label, assignee, milestone)
  - Validate list_config based on type
  - Set position (append to end)
- Create board list update endpoint (PUT /api/v1/board-lists/:id)
  - Update position (reorder)
  - Update list_config
- Create board list deletion endpoint (DELETE /api/v1/board-lists/:id)
- Create board lists retrieval endpoint (GET /api/v1/boards/:id/lists)
  - Return lists ordered by position
- Create board issues endpoint (GET /api/v1/boards/:id/issues)
  - Apply board scope filters (scope_config.label_ids)
  - Group issues by board lists
  - Include issue details (title, ID, labels, assignee, story_points, comment_count, subtask_count)
  - Limit per column, N+1-aware loading
- Write board list API tests (unit, integration, functional)

**Deliverables**:

- Board list CRUD endpoints
- Board issues endpoint with grouping
- API tests (unit, integration, functional)

---

## Phase 2.5.6: Board Lists (Columns) Frontend

**Priority**: High  
**Estimated Time**: 4-5 days  
**Dependencies**: 2.5.5, 2.5.4  
**Assigned To**: BATATA2

### Frontend implementation status (`clients/app1`)

| Area                             | Done | Notes                                                                                                                                                                                      |
| -------------------------------- | ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Column layout                    | ✅   | `kanban-board.ts` — headers with title + count badge, `cdkDropList` per column                                                                                                             |
| Issue card                       | ✅   | `issue-card.ts` — title, key, type icon, priority badge, assignee avatar, **colored labels**; story points supported via `showStoryPoints` input (**not** enabled from `kanban-board` yet) |
| Activity metrics                 | ⬜   | **No** comment count / subtask count icons on card (not wired in template)                                                                                                                 |
| Add column                       | ✅   | `add-board-column-modal.ts` — opened from column header `+`; list type + config (label / assignee / milestone)                                                                             |
| Group by API                     | ✅   | Issues loaded via `getBoardIssues`, columns from board lists                                                                                                                               |
| Column reorder (horizontal drag) | ⬜   | Grip icon present; **no** reorder handler / API hookup                                                                                                                                     |
| Per-column search                | ✅   | Client-side filter on column issues (disables drag while active)                                                                                                                           |
| Component tests                  | ⬜   | Open                                                                                                                                                                                       |

**Frontend Tasks**:

- Create board column component (`board-column.component.ts`)
  - Column header (list name, issue count)
  - Column content (issue cards container)
- Create issue card component (`issue-card.component.ts`)
  - Display issue title, ID (e.g., PROJ-123)
  - Display labels with colors
  - Display assignee avatar
  - Display story points (weight)
  - Display activity icons (comments count, subtasks count)
- Create add list button/modal
  - List type selector (Label, Assignee, Milestone)
  - Configuration based on type
- Integrate with board lists API
- Display issues grouped by columns
- Implement column reordering (horizontal drag)
- Apply BOM CSS methodology
- Write component tests

**Deliverables**:

- Board column component
- Issue card component
- Add list functionality
- Column reordering
- Component tests

---

## Phase 2.5.7: Drag & Drop with Label Swapping Backend ✅ (Done)

**Priority**: High  
**Estimated Time**: 3-4 days  
**Dependencies**: 2.5.5, 2.5.1  
**Assigned To**: BATATA1  
**Status**: Implemented (MoveBoardIssueUseCase, API, unit/integration/functional tests, 100% coverage on use case)

**Backend Tasks**:

- Create move issue endpoint (PUT /api/v1/boards/:id/issues/:issueId/move)
  - Accept source_list_id and target_list_id (MoveBoardIssueRequest)
  - Validate issue belongs to board scope (scope_config.label_ids when present)
  - Implement label swapping logic:
    - If source list is label-based: remove source label
    - If target list is label-based: add target label
    - If source list is assignee-based: clear assignee
    - If target list is assignee-based: set assignee from list_config.user_id
    - If source list is milestone-based: remove from milestone (sprint)
    - If target list is milestone-based: add to milestone (sprint, order = max+1)
  - Create activity log entry (board_move, board_list in payload)
  - Return updated issue (BoardIssueItemResponse) with labels, assignee, etc.
- Implement label swapping validation
  - ConflictException/EntityNotFoundException on label/sprint handled (no-op or re-raise as 404)
- Handle edge cases (same column = no-op, invalid moves = 404)
- Write drag & drop API tests (unit, integration, functional)

**Deliverables**:

- Issue move endpoint with label swapping
- Label swapping logic (label, assignee, milestone)
- API tests (unit, integration, functional)

---

## Phase 2.5.8: Drag & Drop with Label Swapping Frontend

**Priority**: High  
**Estimated Time**: 4-5 days  
**Dependencies**: 2.5.7, 2.5.6  
**Assigned To**: BATATA2

### Frontend implementation status (`clients/app1`)

| Area              | Done | Notes                                                                                                                |
| ----------------- | ---- | -------------------------------------------------------------------------------------------------------------------- |
| Library           | ✅   | **Angular CDK** `DragDropModule` — `cdkDrag` on `app-issue-card`, `cdkDropList` on columns                           |
| Cross-column move | ✅   | `handleDrop` → `boardService.moveBoardIssue` with `source_list_id` / `target_list_id` → `loadBoardIssues` on success |
| Visual feedback   | ✅   | Default CDK drag preview / placeholder                                                                               |
| Rollback          | ✅   | On API error: `transferArrayItem` back + toast                                                                       |
| Optimistic        | ⬜   | UI moves immediately but **no** optimistic label/assignee patch; refresh after success                               |
| Same column       | 🟨   | `moveItemInArray` **local only** — not persisted as board reorder                                                    |
| Loading on move   | ⬜   | No dedicated per-card loading; full board reload after move                                                          |
| Component tests   | ⬜   | Open                                                                                                                 |

**Frontend Tasks**:

- Integrate drag and drop library (dnd-kit or similar)
- Implement issue card drag functionality
  - Make issue cards draggable
  - Visual feedback during drag
- Implement column drop zones
  - Accept dropped issues
  - Visual feedback on hover
- Implement move issue API call
  - Optimistic updates
  - Error handling and rollback
- Update issue card after move (refresh labels/assignee)
- Handle drag within same column (reorder)
- Add loading states during move
- Write component tests

**Deliverables**:

- Drag and drop functionality
- Label swapping on move
- Optimistic updates
- Component tests

---

## Phase 2.5.9: Multiple Boards Management Backend ✅ (Done)

**Priority**: Medium  
**Estimated Time**: 2-3 days  
**Dependencies**: 2.5.3  
**Assigned To**: HWIMDA1  
**Status**: Implemented (search, set-default, duplicate, reorder; unit/integration/functional tests, 100% coverage on new use cases)

**Backend Tasks**:

- Enhance board list endpoint with search
  - Search by board name (GET /api/v1/projects/:id/boards?search=...)
  - Filter by project (already scoped by project_id)
- Create set default board endpoint (PUT /api/v1/boards/:id/set-default)
  - Unset previous default (set_default_board in repository)
  - Set new default
- Create duplicate board endpoint (POST /api/v1/boards/:id/duplicate)
  - Copy board configuration (name "Copy of …", description, scope_config)
  - Copy board lists (same list_type, list_config, position)
  - Generate new name
- Implement board position management
  - Update board positions endpoint (PUT /api/v1/projects/:id/boards/reorder)
  - Accept array of board IDs in order (ReorderBoardsRequest.board_ids)
- Write board management API tests (unit, integration, functional)

**Deliverables**:

- Board search functionality
- Default board management
- Board duplication
- Board reordering
- API tests (unit, integration, functional)

---

## Phase 2.5.10: Multiple Boards Management Frontend

**Priority**: Medium  
**Estimated Time**: 2-3 days  
**Dependencies**: 2.5.9, 2.5.4  
**Assigned To**: HWIMDA2

### Frontend implementation status (`clients/app1`)

| Area                  | Done | Notes                                                      |
| --------------------- | ---- | ---------------------------------------------------------- |
| Selector search       | ✅   | `board-selector.ts` — filters `boards()` by name in memory |
| API search param      | ⬜   | `listProjectBoards` not passed `search=` from UI           |
| Set default           | ✅   | Star action → `setDefaultBoard`                            |
| Duplicate / delete    | ✅   | Copy / trash actions → `duplicateBoard`, `deleteBoard`     |
| Edit name/description | ⬜   | No settings panel or modal                                 |
| Reorder boards        | ⬜   | No drag reorder UI → `reorder` API unused from frontend    |
| Board list page       | ⬜   | Not implemented (optional in spec)                         |

**Frontend Tasks**:

- Enhance board selector with search
  - Search input in dropdown
  - Filter boards by name
- Create board settings panel
  - Edit board name/description
  - Set as default button
  - Duplicate board button
  - Delete board button
- Create board list page (optional)
  - List all boards
  - Reorder boards (drag & drop)
- Add board management actions to board header
- Add loading states and error handling
- Write component tests

**Deliverables**:

- Enhanced board selector with search
- Board settings panel
- Board management UI
- Component tests

---

## Phase 2.5.11: Board Scope Configuration Backend ✅ (Done)

**Priority**: Medium  
**Estimated Time**: 3-4 days  
**Dependencies**: 2.5.3, 2.5.1  
**Assigned To**: HWIMDA1  
**Status**: Implemented (scope schema, update endpoint, scope filters, validation; unit/integration/functional tests, 100% coverage on new use case)

**Backend Tasks**:

- Design scope configuration schema (JSON)
  - Global filters: labels, assignee, milestone, type, priority (stored in board.scope_config)
  - Fixed assignment: user_id (fixed_user_id, treated as global assignee filter)
- Create update board scope endpoint (PUT /api/v1/boards/:id/scope)
  - Validate scope configuration via DTO + use case
  - Update scope_config in board (JSON-serializable schema)
- Enhance board issues endpoint to apply scope filters
  - Filter by labels (include/exclude via label_ids / exclude_label_ids)
  - Filter by assignee (assignee_id or fixed_user_id)
  - Filter by milestone (milestone_id → sprint filter)
  - Filter by type (types list: task, bug, story, epic)
  - Filter by priority (priorities list: low, medium, high, critical)
- Implement scope validation
  - Ensure scope doesn't conflict with board lists (assignee lists vs fixed_user_id/assignee_id)
  - Prevent overlapping include / exclude labels
- Write scope configuration API tests
  - Unit tests for UpdateBoardScopeUseCase and GetBoardIssuesUseCase scope helpers
  - Integration test for PUT /boards/:id/scope
  - Functional workflow test (create boards/issues, set scope, verify filtered issues)

**Deliverables**:

- Board scope configuration system
- Scope filtering in board issues
- API tests (unit, integration, functional)

---

## Phase 2.5.12: Board Scope Configuration Frontend

**Priority**: Medium  
**Estimated Time**: 3-4 days  
**Dependencies**: 2.5.11, 2.5.4  
**Assigned To**: HWIMDA2

### Frontend implementation status (`clients/app1`)

| Area                    | Done | Notes                                                                                                                                                 |
| ----------------------- | ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| Scope modal             | ⬜   | No dedicated modal for labels / milestone / reporter / text / story-point range                                                                       |
| Toolbar filters → API   | ✅   | `kanban-board.ts` — filter dropdown: assignee, type, priority; **debounced ~250ms** `applyScope` → `boardService.updateBoardScope` then reload issues |
| Board creation scope    | ⬜   | Quick-create boards do not set `scope_config`                                                                                                         |
| Badges in header        | ⬜   | Board header is minimal; filter state not shown as chips on the board chrome (clear via dropdown)                                                     |
| Fixed assignment toggle | ⬜   | Not exposed                                                                                                                                           |

**Frontend Tasks**:

- Create scope configuration modal
  - Label filters (multi-select)
  - Assignee filter (single select)
  - Milestone filter (single select)
  - Type filter (multi-select)
  - Priority filter (multi-select)
  - Fixed assignment toggle
- Integrate scope configuration with board creation
- Integrate scope configuration with board settings
- Display active scope filters in board header
  - Show applied filters as badges
  - Clear filters button
- Add loading states and error handling
- Write component tests

**Deliverables**:

- Scope configuration UI
- Scope display in board header
- Component tests

---

## Phase 2.5.13: Real-Time Filtering Backend ✅ (Done)

**Priority**: Medium  
**Estimated Time**: 2-3 days  
**Dependencies**: 2.5.5  
**Assigned To**: BATATA1  
**Status**: Implemented via board scope (`scope_config`) on `GET /boards/:id/issues` (unit/integration/functional tests, 100% coverage des nouveaux use cases)

**Backend Tasks**:

- Enhance board issues endpoint with real-time filters
  - Filter by author (reporter_id) via `scope_config.reporter_id` appliqué dans `GetBoardIssuesUseCase`
  - Filter by text (search in title/description) via `scope_config.search_text` (lowercase contains)
  - Filter by milestone (déjà couvert via `milestone_id` / sprint scope)
  - Filter by label (déjà couvert via `label_ids` / `exclude_label_ids`)
  - Filter by weight (story_points range) via `story_points_min` / `story_points_max`
- Implement efficient filtering queries
  - Utilise les filtres natifs de `IssueRepository.get_all` (assignee, label_ids, sprint_id, reporter_id)
  - Applique les autres filtres (texte, poids) en mémoire sur le résultat paginé par colonne
- Create filter combination logic (AND conditions)
  - Tous les filtres de scope sont combinés en AND (labels, assignee, milestone, type, priority, reporter, texte, poids)
- Write filtering API tests
  - Unit tests pour `UpdateBoardScopeUseCase` (validation story_points, cohérence user) et `GetBoardIssuesUseCase` (reporter/search/poids)
  - Integration test sur `PUT /boards/:id/scope` + `GET /boards/:id/issues`
  - Functional workflow `test_board_scope_configuration_workflow` vérifiant le filtrage par labels + texte/poids

**Deliverables**:

- Real-time filtering in board issues endpoint
- Efficient filter queries (via `IssueRepository.get_all` + filtrage ciblé en mémoire)
- API tests (unit, integration, functional)

---

## Phase 2.5.14: Real-Time Filtering Frontend

**Priority**: Medium  
**Estimated Time**: 2-3 days  
**Dependencies**: 2.5.13, 2.5.6  
**Assigned To**: BATATA2

### Frontend implementation status (`clients/app1`)

| Area                  | Done | Notes                                                                                                                                                                                 |
| --------------------- | ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Global filter bar     | ⬜   | No single bar with author, global text (300ms), milestone, labels, weight range                                                                                                       |
| Server-driven filters | 🟨   | Assignee / type / priority update **board `scope_config`** (backend applies on `GET` issues). Reporter, `search_text`, story point range, label include/exclude **not** wired from UI |
| Per-column search     | ✅   | Client-only search input per column (`columnSearchQueries`) — filters loaded issues, no API                                                                                           |
| Active filter badges  | 🟨   | “Clear filters” for toolbar scope only; no badge row                                                                                                                                  |
| No full page reload   | ✅   | In-place reload via `loadBoardIssues`                                                                                                                                                 |

**Frontend Tasks**:

- Create board filter bar component
  - Author filter (user selector)
  - Text search input (with debouncing)
  - Milestone filter (dropdown)
  - Label filter (multi-select)
  - Weight filter (range slider or input)
- Implement real-time filtering
  - Update board issues on filter change
  - Debounce text search (300ms)
  - No page reload
- Display active filters
  - Show active filter badges
  - Clear individual filters
  - Clear all filters button
- Integrate with board issues API
- Add loading states during filtering
- Write component tests

**Deliverables**:

- Board filter bar component
- Real-time filtering without page reload
- Filter management UI
- Component tests

---

## Phase 2.5.15: Swimlanes Backend

**Priority**: Low  
**Estimated Time**: 4-5 days  
**Dependencies**: 2.5.5, Phase 2.2.11 (Epics if available)  
**Assigned To**: HWIMDA1  
**Status**: Done (model, endpoint, board issues grouping, unit/integration/functional tests, 100% coverage on new use cases)

**Backend Tasks**:

- Design swimlane data model
  - Add swimlane_type to Boards table ('none', 'epic', 'assignee')
  - Store swimlane configuration in board
- Enhance board issues endpoint for swimlanes
  - Group issues by swimlane type
  - Return issues organized by swimlanes and columns
  - Include swimlane metadata (epic info, assignee info)
- Implement epic-based swimlanes
  - Group issues by parent_issue_id (epic)
  - Include epic details in response
- Implement assignee-based swimlanes
  - Group issues by assignee_id
  - Include assignee details in response
- Create update swimlane type endpoint (PUT /api/v1/boards/:id/swimlanes)
- Write swimlane API tests

**Deliverables**:

- Swimlane data model
- Swimlane grouping in board issues
- Epic and assignee swimlanes
- API tests

---

## Phase 2.5.16: Swimlanes Frontend

**Priority**: Low  
**Estimated Time**: 4-5 days  
**Dependencies**: 2.5.15, 2.5.6  
**Assigned To**: HWIMDA2

### Frontend implementation status (`clients/app1`)

| Area                  | Done | Notes                                                                                                                                                               |
| --------------------- | ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Swimlane toggle       | ✅   | `kanban-board.ts` settings dropdown — `lib-select` for `none` / `epic` / `assignee` → `updateBoardSwimlanes`                                                        |
| API consumption       | ✅   | `getBoardIssues` response includes `swimlane_type` and `swimlanes` when enabled                                                                                     |
| Row layout + headers  | ⬜   | **`extractLists` flattens** all lists from all swimlanes into **one** horizontal column strip (deduped by `list.id`) — **no** per-swimlane rows, headers, or counts |
| DnD between swimlanes | ⬜   | N/A until row UI exists                                                                                                                                             |

**Frontend Tasks**:

- Create swimlane container component
  - Horizontal rows (swimlanes)
  - Columns within each swimlane
- Create swimlane header component
  - Epic name/icon or assignee avatar/name
  - Issue count per swimlane
- Implement swimlane toggle
  - Switch between 'none', 'epic', 'assignee'
  - Update board configuration
- Update board layout for swimlanes
  - Render issues in swimlane rows
  - Maintain column structure within swimlanes
- Implement drag & drop within swimlanes
  - Allow moving issues between columns in same swimlane
  - Allow moving issues between swimlanes (update epic/assignee)
- Add loading states and error handling
- Write component tests

**Deliverables**:

- Swimlane UI components
- Swimlane toggle functionality
- Drag & drop within swimlanes
- Component tests

---

## Phase 2.5.17: Group Boards Backend

**Priority**: Low  
**Estimated Time**: 5-7 days  
**Dependencies**: 2.5.3, Phase 1.2 (Organizations)  
**Assigned To**: BATATA1
**Status**: Implemented (data model, group board use cases, API endpoints, unit/integration/functional tests, 100% coverage on new use cases)

**Backend Tasks**:

- Design group board data model
  - Add organization_id to Boards table (nullable)
  - Add board_type to Boards table ('project', 'group')
  - Create GroupBoardProjects table (id, group_board_id, project_id, position)
- Create group board creation endpoint (POST /api/v1/organizations/:id/boards)
  - Validate organization access
  - Allow selecting multiple projects
- Enhance board issues endpoint for group boards
  - Aggregate issues from multiple projects
  - Include project information in issue response
  - Apply scope filters across all projects
- Create add/remove projects from group board endpoints
  - POST /api/v1/boards/:id/projects
  - DELETE /api/v1/boards/:id/projects/:projectId
- Implement project filtering in group boards
- Write group board API tests

**Deliverables**:

- Group board data model
- Group board CRUD endpoints
- Multi-project issue aggregation
- API tests

---

## Phase 2.5.18: Group Boards Frontend

**Priority**: Low  
**Estimated Time**: 4-5 days  
**Dependencies**: 2.5.17, 2.5.4  
**Assigned To**: BATATA2

### Frontend implementation status (`clients/app1`)

| Area                  | Done | Notes                                                                       |
| --------------------- | ---- | --------------------------------------------------------------------------- |
| Create group board    | ✅   | `board-selector` → “Create Group Board” → `createGroupBoard` (default name) |
| Type indicator        | ✅   | **Group** `lib-badge` on selector rows                                      |
| Project on card       | ✅   | `issue-card.ts` — `project_key` badge when present (group board payload)    |
| Manage projects       | ⬜   | No UI for add/remove/reorder projects on a group board                      |
| Project filter in bar | ⬜   | Not implemented                                                             |

**Frontend Tasks**:

- Create group board creation modal
  - Select organization
  - Select multiple projects
  - Configure board name and scope
- Enhance board selector for group boards
  - Show board type indicator
  - Filter by board type
- Display project indicator on issue cards
  - Show project key/name
  - Project color indicator
- Create group board settings
  - Add/remove projects
  - Reorder projects
- Add project filter in board filter bar
- Add loading states and error handling
- Write component tests

**Deliverables**:

- Group board creation UI
- Multi-project board display
- Project management in group boards
- Component tests

---

## Phase 2.5.19: Focus Mode Frontend

**Priority**: Low  
**Estimated Time**: 1-2 days  
**Dependencies**: 2.5.4  
**Assigned To**: HWIMDA2

### Frontend implementation status (`clients/app1`)

| Area                 | Done | Notes                                                                                                                              |
| -------------------- | ---- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Toggle + persistence | ✅   | `project-detail-page.ts` — `BOARD_FOCUS_MODE_STORAGE_KEY` (`pages.projectBoardFocusMode`) JSON map **per project**                 |
| Layout               | ✅   | `shouldHideBoardChrome()` hides page header / board toolbar / nav chrome when focus on; maximizes board area                       |
| Exit                 | ✅   | Floating exit control + **ESC** listener (`fromEvent` + `debounceTime`)                                                            |
| Full sidebar hide    | 🟨   | Hides **project** chrome in template; app shell sidebar depends on parent layout (may still show unless shell also respects focus) |

**Frontend Tasks**:

- Create focus mode toggle button
  - Toggle in board header
  - Store preference (localStorage)
- Implement focus mode layout
  - Hide navigation menus
  - Hide sidebars
  - Maximize board area
  - Full-screen board view
- Add exit focus mode button
  - Floating button or keyboard shortcut (ESC)
- Apply BOM CSS methodology
- Write component tests

**Deliverables**:

- Focus mode toggle
- Full-screen board layout
- Component tests

---

## Summary

**Total Estimated Timeline**: 8 weeks (Weeks 25-32)

**Key Milestones**:

- Week 26: Labels and basic boards complete
- Week 28: Drag & drop and multiple boards complete
- Week 30: Scope configuration and filtering complete
- Week 32: Advanced features (swimlanes, group boards) complete

**Dependencies Summary**:

- Labels system (2.5.1-2.5.2) must be completed before boards
- Board data model (2.5.3) required for all board features
- Board lists (2.5.5-2.5.6) required for drag & drop
- Drag & drop (2.5.7-2.5.8) can be developed in parallel with multiple boards management

**Team Size Recommendations**:

- 2 Backend developers (BATATA1, HWIMDA1)
- 2 Frontend developers (BATATA2, HWIMDA2)
