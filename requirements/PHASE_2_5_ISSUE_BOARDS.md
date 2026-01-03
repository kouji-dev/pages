# Phase 2.5: Issue Boards & Board Management (Weeks 25-32)

**Timeline**: Weeks 25-32 (8 weeks)  
**Goal**: Implémenter un système complet de Issue Boards avec labels, colonnes dynamiques, drag & drop avec label swapping, gestion de multiples boards, scope configuration, swimlanes, group boards et focus mode.

### Dependencies: Phase 1.3 (Issues), Phase 2.1 (Sprints)

**Note**: Cette phase implémente un système complet de boards pour la gestion visuelle des issues, inspiré de GitLab. Les boards permettent de créer des vues personnalisées avec des colonnes dynamiques basées sur des critères (labels, assignés, milestones).

---

## Phase 2.5.1: Labels System Backend

**Priority**: High  
**Estimated Time**: 3-4 days  
**Dependencies**: Phase 1.3.2  
**Assigned To**: BATATA1

**Backend Tasks**:

- [ ] Design label data model
  - [ ] Labels table (id, project_id, name, color, description, created_at, updated_at)
  - [ ] IssueLabels table (id, issue_id, label_id, created_at) - many-to-many relationship
- [ ] Create label creation endpoint (POST /api/v1/projects/:id/labels)
  - [ ] Validate unique name per project
  - [ ] Validate color format (hex)
- [ ] Create label retrieval endpoint (GET /api/v1/labels/:id)
- [ ] Create label list endpoint (GET /api/v1/projects/:id/labels)
  - [ ] Pagination support
  - [ ] Search by name
- [ ] Create label update endpoint (PUT /api/v1/labels/:id)
- [ ] Create label deletion endpoint (DELETE /api/v1/labels/:id)
  - [ ] Handle cascade deletion from IssueLabels
- [ ] Create add label to issue endpoint (POST /api/v1/issues/:id/labels)
- [ ] Create remove label from issue endpoint (DELETE /api/v1/issues/:id/labels/:labelId)
- [ ] Create issue labels list endpoint (GET /api/v1/issues/:id/labels)
- [ ] Write label API tests (unit, integration, functional)

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

## Phase 2.5.3: Issue Boards Data Model & CRUD Backend

**Priority**: High  
**Estimated Time**: 4-5 days  
**Dependencies**: 2.5.1  
**Assigned To**: BATATA1

**Backend Tasks**:

- [ ] Design board data model
  - [ ] Boards table (id, project_id, name, description, scope_config (JSON), is_default, position, created_by, created_at, updated_at)
  - [ ] BoardLists table (id, board_id, list_type, list_config (JSON), position, created_at, updated_at)
    - [ ] list_type: 'label', 'assignee', 'milestone'
    - [ ] list_config: stores the specific label_id, user_id, or milestone_id
- [ ] Create board creation endpoint (POST /api/v1/projects/:id/boards)
  - [ ] Validate project access
  - [ ] Set default board if first board
- [ ] Create board retrieval endpoint (GET /api/v1/boards/:id)
  - [ ] Include board lists
  - [ ] Include scope configuration
- [ ] Create board list endpoint (GET /api/v1/projects/:id/boards)
  - [ ] Pagination support
  - [ ] Sort by position
- [ ] Create board update endpoint (PUT /api/v1/boards/:id)
  - [ ] Update name, description, scope_config
  - [ ] Update position
- [ ] Create board deletion endpoint (DELETE /api/v1/boards/:id)
  - [ ] Handle cascade deletion of board lists
  - [ ] Prevent deletion of last board
- [ ] Write board CRUD API tests (unit, integration, functional)

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

## Phase 2.5.5: Board Lists (Columns) Backend

**Priority**: High  
**Estimated Time**: 3-4 days  
**Dependencies**: 2.5.3, 2.5.1  
**Assigned To**: BATATA1

**Backend Tasks**:

- [ ] Create board list creation endpoint (POST /api/v1/boards/:id/lists)
  - [ ] Validate list_type (label, assignee, milestone)
  - [ ] Validate list_config based on type
  - [ ] Set position (append to end)
- [ ] Create board list update endpoint (PUT /api/v1/board-lists/:id)
  - [ ] Update position (reorder)
  - [ ] Update list_config
- [ ] Create board list deletion endpoint (DELETE /api/v1/board-lists/:id)
- [ ] Create board lists retrieval endpoint (GET /api/v1/boards/:id/lists)
  - [ ] Return lists ordered by position
- [ ] Create board issues endpoint (GET /api/v1/boards/:id/issues)
  - [ ] Apply board scope filters
  - [ ] Group issues by board lists
  - [ ] Include issue details (title, ID, labels, assignee, story_points, comment_count, subtask_count)
  - [ ] Optimize queries (N+1 prevention)
- [ ] Write board list API tests (unit, integration, functional)

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

## Phase 2.5.7: Drag & Drop with Label Swapping Backend

**Priority**: High  
**Estimated Time**: 3-4 days  
**Dependencies**: 2.5.5, 2.5.1  
**Assigned To**: BATATA1

**Backend Tasks**:

- [ ] Create move issue endpoint (PUT /api/v1/boards/:id/issues/:issueId/move)
  - [ ] Accept source_list_id and target_list_id
  - [ ] Validate issue belongs to board scope
  - [ ] Implement label swapping logic:
    - [ ] If source list is label-based: remove source label
    - [ ] If target list is label-based: add target label
    - [ ] If source list is assignee-based: clear assignee (optional)
    - [ ] If target list is assignee-based: set assignee
    - [ ] If source list is milestone-based: remove from milestone
    - [ ] If target list is milestone-based: add to milestone
  - [ ] Create activity log entry
  - [ ] Return updated issue with new labels/assignee
- [ ] Implement label swapping validation
  - [ ] Prevent invalid label combinations (if needed)
- [ ] Handle edge cases (same column, invalid moves)
- [ ] Write drag & drop API tests (unit, integration, functional)

**Deliverables**:

- Issue move endpoint with label swapping
- Label swapping logic
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

## Phase 2.5.9: Multiple Boards Management Backend

**Priority**: Medium  
**Estimated Time**: 2-3 days  
**Dependencies**: 2.5.3  
**Assigned To**: HWIMDA1

**Backend Tasks**:

- [ ] Enhance board list endpoint with search
  - [ ] Search by board name
  - [ ] Filter by project
- [ ] Create set default board endpoint (PUT /api/v1/boards/:id/set-default)
  - [ ] Unset previous default
  - [ ] Set new default
- [ ] Create duplicate board endpoint (POST /api/v1/boards/:id/duplicate)
  - [ ] Copy board configuration
  - [ ] Copy board lists
  - [ ] Generate new name
- [ ] Implement board position management
  - [ ] Update board positions endpoint (PUT /api/v1/boards/reorder)
  - [ ] Accept array of board IDs in order
- [ ] Write board management API tests

**Deliverables**:

- Board search functionality
- Default board management
- Board duplication
- Board reordering
- API tests

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

## Phase 2.5.11: Board Scope Configuration Backend

**Priority**: Medium  
**Estimated Time**: 3-4 days  
**Dependencies**: 2.5.3, 2.5.1  
**Assigned To**: HWIMDA1

**Backend Tasks**:

- [ ] Design scope configuration schema (JSON)
  - [ ] Global filters: labels, assignee, milestone, type, priority
  - [ ] Fixed assignment: user_id (board dedicated to specific user)
- [ ] Create update board scope endpoint (PUT /api/v1/boards/:id/scope)
  - [ ] Validate scope configuration
  - [ ] Update scope_config in board
- [ ] Enhance board issues endpoint to apply scope filters
  - [ ] Filter by labels (include/exclude)
  - [ ] Filter by assignee
  - [ ] Filter by milestone
  - [ ] Filter by type
  - [ ] Filter by priority
- [ ] Implement scope validation
  - [ ] Ensure scope doesn't conflict with board lists
- [ ] Write scope configuration API tests

**Deliverables**:

- Board scope configuration system
- Scope filtering in board issues
- API tests

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

## Phase 2.5.13: Real-Time Filtering Backend

**Priority**: Medium  
**Estimated Time**: 2-3 days  
**Dependencies**: 2.5.5  
**Assigned To**: BATATA1

**Backend Tasks**:

- [ ] Enhance board issues endpoint with real-time filters
  - [ ] Filter by author (reporter_id)
  - [ ] Filter by text (search in title/description)
  - [ ] Filter by milestone
  - [ ] Filter by label
  - [ ] Filter by weight (story_points range)
- [ ] Implement efficient filtering queries
  - [ ] Use database indexes
  - [ ] Optimize for large issue sets
- [ ] Create filter combination logic (AND conditions)
- [ ] Write filtering API tests

**Deliverables**:

- Real-time filtering in board issues endpoint
- Efficient filter queries
- API tests

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

**Backend Tasks**:

- [ ] Design swimlane data model
  - [ ] Add swimlane_type to Boards table ('none', 'epic', 'assignee')
  - [ ] Store swimlane configuration in board
- [ ] Enhance board issues endpoint for swimlanes
  - [ ] Group issues by swimlane type
  - [ ] Return issues organized by swimlanes and columns
  - [ ] Include swimlane metadata (epic info, assignee info)
- [ ] Implement epic-based swimlanes
  - [ ] Group issues by parent_issue_id (epic)
  - [ ] Include epic details in response
- [ ] Implement assignee-based swimlanes
  - [ ] Group issues by assignee_id
  - [ ] Include assignee details in response
- [ ] Create update swimlane type endpoint (PUT /api/v1/boards/:id/swimlanes)
- [ ] Write swimlane API tests

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

**Backend Tasks**:

- [ ] Design group board data model
  - [ ] Add organization_id to Boards table (nullable)
  - [ ] Add board_type to Boards table ('project', 'group')
  - [ ] Create GroupBoardProjects table (id, group_board_id, project_id, position)
- [ ] Create group board creation endpoint (POST /api/v1/organizations/:id/boards)
  - [ ] Validate organization access
  - [ ] Allow selecting multiple projects
- [ ] Enhance board issues endpoint for group boards
  - [ ] Aggregate issues from multiple projects
  - [ ] Include project information in issue response
  - [ ] Apply scope filters across all projects
- [ ] Create add/remove projects from group board endpoints
  - [ ] POST /api/v1/boards/:id/projects
  - [ ] DELETE /api/v1/boards/:id/projects/:projectId
- [ ] Implement project filtering in group boards
- [ ] Write group board API tests

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

