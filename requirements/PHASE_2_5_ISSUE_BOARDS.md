# Phase 2.5: Issue Boards & Board Management (Weeks 25-32)

**Timeline**: Weeks 25-32 (8 weeks)  
**Goal**: Implémenter un système complet de Issue Boards avec labels, colonnes dynamiques, drag & drop avec label swapping, gestion de multiples boards, scope configuration, swimlanes, group boards et focus mode.

### Dependencies: Phase 1.3 (Issues), Phase 2.1 (Sprints)

**Note**: Cette phase implémente un système complet de boards pour la gestion visuelle des issues, inspiré de GitLab. Les boards permettent de créer des vues personnalisées avec des colonnes dynamiques basées sur des critères (labels, assignés, milestones).

**Implementation status**:
| Phase   | Description                          | Status   |
|---------|--------------------------------------|----------|
| 2.5.1   | Labels System Backend                | ✅ Done  |
| 2.5.2   | Labels System Frontend               | Pending  |
| 2.5.3   | Issue Boards Data Model & CRUD Backend | ✅ Done  |
| 2.5.4   | Issue Boards Basic Frontend          | Pending  |
| 2.5.5   | Board Lists (Columns) Backend        | ✅ Done  |
| 2.5.6   | Board Lists (Columns) Frontend       | Pending  |
| 2.5.7   | Drag & Drop with Label Swapping Backend | ✅ Done  |
| 2.5.8   | Drag & Drop with Label Swapping Frontend | Pending  |
| 2.5.9   | Multiple Boards Management Backend       | ✅ Done  |
| 2.5.10  | Multiple Boards Management Frontend      | Pending  |
| 2.5.11  | Board Scope Configuration Backend        | ✅ Done  |
| 2.5.12+ | Board Scope Frontend, etc.               | Pending  |

---

## Phase 2.5.1: Labels System Backend ✅ (Done)

**Priority**: High  
**Estimated Time**: 3-4 days  
**Dependencies**: Phase 1.3.2  
**Assigned To**: BATATA1  
**Status**: Implemented (models, migration, API, unit/integration/functional tests)

**Backend Tasks**:

- [x] Design label data model
  - [x] Labels table (id, project_id, name, color, description, created_at, updated_at)
  - [x] IssueLabels table (id, issue_id, label_id, created_at) - many-to-many relationship
- [x] Create label creation endpoint (POST /api/v1/projects/:id/labels)
  - [x] Validate unique name per project
  - [x] Validate color format (hex)
- [x] Create label retrieval endpoint (GET /api/v1/labels/:id)
- [x] Create label list endpoint (GET /api/v1/projects/:id/labels)
  - [x] Pagination support
  - [x] Search by name
- [x] Create label update endpoint (PUT /api/v1/labels/:id)
- [x] Create label deletion endpoint (DELETE /api/v1/labels/:id)
  - [x] Handle cascade deletion from IssueLabels
- [x] Create add label to issue endpoint (POST /api/v1/issues/:id/labels)
- [x] Create remove label from issue endpoint (DELETE /api/v1/issues/:id/labels/:labelId)
- [x] Create issue labels list endpoint (GET /api/v1/issues/:id/labels)
- [x] Write label API tests (unit, integration, functional)

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

**Frontend Tasks**:

- [ ] Create label management UI
  - [ ] Label list component
  - [ ] Create label modal
  - [ ] Edit label modal
  - [ ] Delete label confirmation
- [ ] Create label selector component
  - [ ] Multi-select dropdown
  - [ ] Color indicators
  - [ ] Search functionality
- [ ] Integrate labels into issue creation form
- [ ] Integrate labels into issue edit form
- [ ] Display labels on issue cards (with colors)
- [ ] Add loading states and error handling
- [ ] Write component tests

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

- [x] Design board data model
  - [x] Boards table (id, project_id, name, description, scope_config (JSON), is_default, position, created_by, created_at, updated_at)
  - [x] BoardLists table (id, board_id, list_type, list_config (JSON), position, created_at, updated_at)
    - [x] list_type: 'label', 'assignee', 'milestone'
    - [x] list_config: stores the specific label_id, user_id, or milestone_id
- [x] Create board creation endpoint (POST /api/v1/projects/:id/boards)
  - [x] Validate project access
  - [x] Set default board if first board
- [x] Create board retrieval endpoint (GET /api/v1/boards/:id)
  - [x] Include board lists
  - [x] Include scope configuration
- [x] Create board list endpoint (GET /api/v1/projects/:id/boards)
  - [x] Pagination support
  - [x] Sort by position
- [x] Create board update endpoint (PUT /api/v1/boards/:id)
  - [x] Update name, description, scope_config
  - [x] Update position
- [x] Create board deletion endpoint (DELETE /api/v1/boards/:id)
  - [x] Handle cascade deletion of board lists
  - [x] Prevent deletion of last board
- [x] Write board CRUD API tests (unit, integration, functional)

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

**Frontend Tasks**:

- [ ] Create board page component (`board-page.ts`)
  - [ ] Board header (name, description, actions)
  - [ ] Board content area (columns container)
- [ ] Create board selector component
  - [ ] Dropdown with search
  - [ ] List of available boards
  - [ ] Create new board button
- [ ] Create board creation modal
  - [ ] Name and description inputs
  - [ ] Scope configuration (initial)
- [ ] Integrate with board list API
- [ ] Implement board switching functionality
- [ ] Apply BOM CSS methodology
- [ ] Write component tests

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

- [x] Create board list creation endpoint (POST /api/v1/boards/:id/lists)
  - [x] Validate list_type (label, assignee, milestone)
  - [x] Validate list_config based on type
  - [x] Set position (append to end)
- [x] Create board list update endpoint (PUT /api/v1/board-lists/:id)
  - [x] Update position (reorder)
  - [x] Update list_config
- [x] Create board list deletion endpoint (DELETE /api/v1/board-lists/:id)
- [x] Create board lists retrieval endpoint (GET /api/v1/boards/:id/lists)
  - [x] Return lists ordered by position
- [x] Create board issues endpoint (GET /api/v1/boards/:id/issues)
  - [x] Apply board scope filters (scope_config.label_ids)
  - [x] Group issues by board lists
  - [x] Include issue details (title, ID, labels, assignee, story_points, comment_count, subtask_count)
  - [x] Limit per column, N+1-aware loading
- [x] Write board list API tests (unit, integration, functional)

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

**Frontend Tasks**:

- [ ] Create board column component (`board-column.component.ts`)
  - [ ] Column header (list name, issue count)
  - [ ] Column content (issue cards container)
- [ ] Create issue card component (`issue-card.component.ts`)
  - [ ] Display issue title, ID (e.g., PROJ-123)
  - [ ] Display labels with colors
  - [ ] Display assignee avatar
  - [ ] Display story points (weight)
  - [ ] Display activity icons (comments count, subtasks count)
- [ ] Create add list button/modal
  - [ ] List type selector (Label, Assignee, Milestone)
  - [ ] Configuration based on type
- [ ] Integrate with board lists API
- [ ] Display issues grouped by columns
- [ ] Implement column reordering (horizontal drag)
- [ ] Apply BOM CSS methodology
- [ ] Write component tests

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

- [x] Create move issue endpoint (PUT /api/v1/boards/:id/issues/:issueId/move)
  - [x] Accept source_list_id and target_list_id (MoveBoardIssueRequest)
  - [x] Validate issue belongs to board scope (scope_config.label_ids when present)
  - [x] Implement label swapping logic:
    - [x] If source list is label-based: remove source label
    - [x] If target list is label-based: add target label
    - [x] If source list is assignee-based: clear assignee
    - [x] If target list is assignee-based: set assignee from list_config.user_id
    - [x] If source list is milestone-based: remove from milestone (sprint)
    - [x] If target list is milestone-based: add to milestone (sprint, order = max+1)
  - [x] Create activity log entry (board_move, board_list in payload)
  - [x] Return updated issue (BoardIssueItemResponse) with labels, assignee, etc.
- [x] Implement label swapping validation
  - [x] ConflictException/EntityNotFoundException on label/sprint handled (no-op or re-raise as 404)
- [x] Handle edge cases (same column = no-op, invalid moves = 404)
- [x] Write drag & drop API tests (unit, integration, functional)

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

**Frontend Tasks**:

- [ ] Integrate drag and drop library (dnd-kit or similar)
- [ ] Implement issue card drag functionality
  - [ ] Make issue cards draggable
  - [ ] Visual feedback during drag
- [ ] Implement column drop zones
  - [ ] Accept dropped issues
  - [ ] Visual feedback on hover
- [ ] Implement move issue API call
  - [ ] Optimistic updates
  - [ ] Error handling and rollback
- [ ] Update issue card after move (refresh labels/assignee)
- [ ] Handle drag within same column (reorder)
- [ ] Add loading states during move
- [ ] Write component tests

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

- [x] Enhance board list endpoint with search
  - [x] Search by board name (GET /api/v1/projects/:id/boards?search=...)
  - [x] Filter by project (already scoped by project_id)
- [x] Create set default board endpoint (PUT /api/v1/boards/:id/set-default)
  - [x] Unset previous default (set_default_board in repository)
  - [x] Set new default
- [x] Create duplicate board endpoint (POST /api/v1/boards/:id/duplicate)
  - [x] Copy board configuration (name "Copy of …", description, scope_config)
  - [x] Copy board lists (same list_type, list_config, position)
  - [x] Generate new name
- [x] Implement board position management
  - [x] Update board positions endpoint (PUT /api/v1/projects/:id/boards/reorder)
  - [x] Accept array of board IDs in order (ReorderBoardsRequest.board_ids)
- [x] Write board management API tests (unit, integration, functional)

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

**Frontend Tasks**:

- [ ] Enhance board selector with search
  - [ ] Search input in dropdown
  - [ ] Filter boards by name
- [ ] Create board settings panel
  - [ ] Edit board name/description
  - [ ] Set as default button
  - [ ] Duplicate board button
  - [ ] Delete board button
- [ ] Create board list page (optional)
  - [ ] List all boards
  - [ ] Reorder boards (drag & drop)
- [ ] Add board management actions to board header
- [ ] Add loading states and error handling
- [ ] Write component tests

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

- [x] Design scope configuration schema (JSON)
  - [x] Global filters: labels, assignee, milestone, type, priority (stored in board.scope_config)
  - [x] Fixed assignment: user_id (fixed_user_id, treated as global assignee filter)
- [x] Create update board scope endpoint (PUT /api/v1/boards/:id/scope)
  - [x] Validate scope configuration via DTO + use case
  - [x] Update scope_config in board (JSON-serializable schema)
- [x] Enhance board issues endpoint to apply scope filters
  - [x] Filter by labels (include/exclude via label_ids / exclude_label_ids)
  - [x] Filter by assignee (assignee_id or fixed_user_id)
  - [x] Filter by milestone (milestone_id → sprint filter)
  - [x] Filter by type (types list: task, bug, story, epic)
  - [x] Filter by priority (priorities list: low, medium, high, critical)
- [x] Implement scope validation
  - [x] Ensure scope doesn't conflict with board lists (assignee lists vs fixed_user_id/assignee_id)
  - [x] Prevent overlapping include / exclude labels
- [x] Write scope configuration API tests
  - [x] Unit tests for UpdateBoardScopeUseCase and GetBoardIssuesUseCase scope helpers
  - [x] Integration test for PUT /boards/:id/scope
  - [x] Functional workflow test (create boards/issues, set scope, verify filtered issues)

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

**Frontend Tasks**:

- [ ] Create scope configuration modal
  - [ ] Label filters (multi-select)
  - [ ] Assignee filter (single select)
  - [ ] Milestone filter (single select)
  - [ ] Type filter (multi-select)
  - [ ] Priority filter (multi-select)
  - [ ] Fixed assignment toggle
- [ ] Integrate scope configuration with board creation
- [ ] Integrate scope configuration with board settings
- [ ] Display active scope filters in board header
  - [ ] Show applied filters as badges
  - [ ] Clear filters button
- [ ] Add loading states and error handling
- [ ] Write component tests

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

- [x] Enhance board issues endpoint with real-time filters
  - [x] Filter by author (reporter_id) via `scope_config.reporter_id` appliqué dans `GetBoardIssuesUseCase`
  - [x] Filter by text (search in title/description) via `scope_config.search_text` (lowercase contains)
  - [x] Filter by milestone (déjà couvert via `milestone_id` / sprint scope)
  - [x] Filter by label (déjà couvert via `label_ids` / `exclude_label_ids`)
  - [x] Filter by weight (story_points range) via `story_points_min` / `story_points_max`
- [x] Implement efficient filtering queries
  - [x] Utilise les filtres natifs de `IssueRepository.get_all` (assignee, label_ids, sprint_id, reporter_id)
  - [x] Applique les autres filtres (texte, poids) en mémoire sur le résultat paginé par colonne
- [x] Create filter combination logic (AND conditions)
  - [x] Tous les filtres de scope sont combinés en AND (labels, assignee, milestone, type, priority, reporter, texte, poids)
- [x] Write filtering API tests
  - [x] Unit tests pour `UpdateBoardScopeUseCase` (validation story_points, cohérence user) et `GetBoardIssuesUseCase` (reporter/search/poids)
  - [x] Integration test sur `PUT /boards/:id/scope` + `GET /boards/:id/issues`
  - [x] Functional workflow `test_board_scope_configuration_workflow` vérifiant le filtrage par labels + texte/poids

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

**Frontend Tasks**:

- [ ] Create board filter bar component
  - [ ] Author filter (user selector)
  - [ ] Text search input (with debouncing)
  - [ ] Milestone filter (dropdown)
  - [ ] Label filter (multi-select)
  - [ ] Weight filter (range slider or input)
- [ ] Implement real-time filtering
  - [ ] Update board issues on filter change
  - [ ] Debounce text search (300ms)
  - [ ] No page reload
- [ ] Display active filters
  - [ ] Show active filter badges
  - [ ] Clear individual filters
  - [ ] Clear all filters button
- [ ] Integrate with board issues API
- [ ] Add loading states during filtering
- [ ] Write component tests

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

- [x] Design swimlane data model
  - [x] Add swimlane_type to Boards table ('none', 'epic', 'assignee')
  - [x] Store swimlane configuration in board
- [x] Enhance board issues endpoint for swimlanes
  - [x] Group issues by swimlane type
  - [x] Return issues organized by swimlanes and columns
  - [x] Include swimlane metadata (epic info, assignee info)
- [x] Implement epic-based swimlanes
  - [x] Group issues by parent_issue_id (epic)
  - [x] Include epic details in response
- [x] Implement assignee-based swimlanes
  - [x] Group issues by assignee_id
  - [x] Include assignee details in response
- [x] Create update swimlane type endpoint (PUT /api/v1/boards/:id/swimlanes)
- [x] Write swimlane API tests

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

**Frontend Tasks**:

- [ ] Create swimlane container component
  - [ ] Horizontal rows (swimlanes)
  - [ ] Columns within each swimlane
- [ ] Create swimlane header component
  - [ ] Epic name/icon or assignee avatar/name
  - [ ] Issue count per swimlane
- [ ] Implement swimlane toggle
  - [ ] Switch between 'none', 'epic', 'assignee'
  - [ ] Update board configuration
- [ ] Update board layout for swimlanes
  - [ ] Render issues in swimlane rows
  - [ ] Maintain column structure within swimlanes
- [ ] Implement drag & drop within swimlanes
  - [ ] Allow moving issues between columns in same swimlane
  - [ ] Allow moving issues between swimlanes (update epic/assignee)
- [ ] Add loading states and error handling
- [ ] Write component tests

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

- [x] Design group board data model
  - [x] Add organization_id to Boards table (nullable)
  - [x] Add board_type to Boards table ('project', 'group')
  - [x] Create GroupBoardProjects table (id, group_board_id, project_id, position)
- [x] Create group board creation endpoint (POST /api/v1/organizations/:id/boards)
  - [x] Validate organization access
  - [x] Allow selecting multiple projects
- [x] Enhance board issues endpoint for group boards
  - [x] Aggregate issues from multiple projects
  - [x] Include project information in issue response
  - [x] Apply scope filters across all projects
- [ ] Create add/remove projects from group board endpoints
  - [x] POST /api/v1/boards/:id/projects
  - [ ] DELETE /api/v1/boards/:id/projects/:projectId
- [x] Implement project filtering in group boards
- [x] Write group board API tests

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

**Frontend Tasks**:

- [ ] Create group board creation modal
  - [ ] Select organization
  - [ ] Select multiple projects
  - [ ] Configure board name and scope
- [ ] Enhance board selector for group boards
  - [ ] Show board type indicator
  - [ ] Filter by board type
- [ ] Display project indicator on issue cards
  - [ ] Show project key/name
  - [ ] Project color indicator
- [ ] Create group board settings
  - [ ] Add/remove projects
  - [ ] Reorder projects
- [ ] Add project filter in board filter bar
- [ ] Add loading states and error handling
- [ ] Write component tests

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

**Frontend Tasks**:

- [ ] Create focus mode toggle button
  - [ ] Toggle in board header
  - [ ] Store preference (localStorage)
- [ ] Implement focus mode layout
  - [ ] Hide navigation menus
  - [ ] Hide sidebars
  - [ ] Maximize board area
  - [ ] Full-screen board view
- [ ] Add exit focus mode button
  - [ ] Floating button or keyboard shortcut (ESC)
- [ ] Apply BOM CSS methodology
- [ ] Write component tests

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

