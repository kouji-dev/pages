# Phase 2: Enhanced Features Development Tasks

**Timeline**: Months 6-12  
**Goal**: Add advanced project management features, documentation enhancements, and platform improvements

---

## Overview

This phase builds upon the MVP foundation, adding advanced features that enhance productivity, collaboration, and platform capabilities. Tasks are organized by dependency order and feature areas.

### Task Organization Principles

**Each task is designed to be:**

- **Concise**: Focused on a single, clear deliverable
- **Isolated**: Contains separated logic that doesn't overlap with other tasks
- **Independent**: Can be worked on independently by assigned developers
- **Testable**: Includes its own testing requirements
- **Parallelizable**: Multiple tasks can be worked on simultaneously when dependencies allow

**Task Structure:**

- Each task has a unique ID (e.g., `2.1.1`, `2.2.5`)
- Clear dependencies listed (minimal and specific)
- Single developer assignment (or shared for collaborative tasks)
- Estimated time for completion
- Deliverables clearly defined

---

## Phase 2.1: Project Management Enhancements - Sprints & Scrum (Weeks 1-4)

### Dependencies: Phase 1.3 (Issues, Kanban Board)

**Note**: Tasks in this phase are split into independent backend and frontend tasks that can be worked on in parallel after initial dependencies are met. Backend tasks (2.1.1-2.1.11) can be started once Phase 1.3.2 (Issue CRUD) is complete. Frontend tasks (2.1.4-2.1.14) depend on corresponding backend APIs and Phase 1 frontend foundation.

#### 2.1.1 Sprint Data Model and CRUD API

**Priority**: High  
**Estimated Time**: 3-4 days  
**Dependencies**: Phase 1.3.2  
**Assigned To**: BATATA1

**Backend Tasks**:

- [ ] Design sprint data model
  - [ ] Sprints table (id, project_id, name, goal, start_date, end_date, status)
  - [ ] SprintIssues table (sprint_id, issue_id, order)
- [ ] Create sprint creation endpoint (POST /api/projects/:id/sprints)
  - [ ] Validate dates (start < end)
  - [ ] Check for overlapping sprints
  - [ ] Set default sprint name (e.g., "Sprint 1")
  - [ ] Create sprint record
- [ ] Create sprint retrieval endpoint (GET /api/sprints/:id)
  - [ ] Include sprint issues
  - [ ] Include basic sprint info (name, goal, dates, status)
- [ ] Create sprint list endpoint (GET /api/projects/:id/sprints)
  - [ ] Filter by status (active, planned, completed)
  - [ ] Sort by start date
  - [ ] Pagination support
- [ ] Create sprint update endpoint (PUT /api/sprints/:id)
  - [ ] Update name, goal, dates
  - [ ] Update status
  - [ ] Validate date ranges
- [ ] Create sprint deletion endpoint (DELETE /api/sprints/:id)
  - [ ] Permission check (project admin)
  - [ ] Handle sprint issues (move to backlog or delete)
- [ ] Write sprint CRUD API tests

**Deliverables**:

- Sprint data model and migrations
- Sprint CRUD API endpoints
- API tests

---

#### 2.1.2 Sprint Issue Management API

**Priority**: High  
**Estimated Time**: 2-3 days  
**Dependencies**: 2.1.1  
**Assigned To**: BATATA1

**Backend Tasks**:

- [ ] Create add issue to sprint endpoint (PUT /api/sprints/:id/issues)
  - [ ] Validate issue belongs to same project
  - [ ] Check issue not already in another active sprint
  - [ ] Add issue to SprintIssues table with order
- [ ] Create remove issue from sprint endpoint (DELETE /api/sprints/:id/issues/:issueId)
  - [ ] Remove from SprintIssues table
  - [ ] Move issue back to backlog
- [ ] Create reorder sprint issues endpoint (PUT /api/sprints/:id/issues/reorder)
  - [ ] Update order of issues in sprint
- [ ] Write sprint issue management API tests

**Deliverables**:

- Sprint issue management endpoints
- API tests

---

#### 2.1.3 Sprint Metrics and Completion API

**Priority**: High  
**Estimated Time**: 2-3 days  
**Dependencies**: 2.1.1  
**Assigned To**: BATATA1

**Backend Tasks**:

- [ ] Implement sprint velocity calculation
  - [ ] Calculate completed story points per sprint
  - [ ] Track velocity over multiple sprints
  - [ ] Average velocity calculation
- [ ] Create sprint metrics endpoint (GET /api/sprints/:id/metrics)
  - [ ] Return velocity, completion percentage
  - [ ] Return issue counts by status
  - [ ] Return burndown data points
- [ ] Create sprint completion endpoint (POST /api/sprints/:id/complete)
  - [ ] Validate all issues moved to final status or handle incomplete
  - [ ] Move incomplete issues to backlog
  - [ ] Calculate and store sprint metrics
  - [ ] Update sprint status to completed
- [ ] Write sprint metrics API tests

**Deliverables**:

- Sprint velocity calculation
- Sprint metrics endpoint
- Sprint completion functionality
- API tests

---

#### 2.1.4 Sprint Selector Component

**Priority**: High  
**Estimated Time**: 1-2 days  
**Dependencies**: 2.1.1, Phase 1.3.8  
**Assigned To**: BATATA2

**Frontend Tasks**:

- [ ] Create sprint selector component (`sprint-selector.component.ts`)
  - [ ] Dropdown showing active/selected sprint
  - [ ] List of available sprints (active, planned, completed)
  - [ ] Create new sprint button (opens modal)
- [ ] Integrate with sprint list API
- [ ] Implement sprint switching functionality
- [ ] Apply BOM CSS methodology
- [ ] Write component tests

**Deliverables**:

- Sprint selector component
- Component tests

---

#### 2.1.5 Sprint Creation Modal

**Priority**: High  
**Estimated Time**: 1-2 days  
**Dependencies**: 2.1.1, 1.1.10, 1.1.9  
**Assigned To**: BATATA2

**Frontend Tasks**:

- [ ] Create sprint creation modal component (`create-sprint-modal.component.ts`)
  - [ ] Sprint name input (use input component)
  - [ ] Start date picker
  - [ ] End date picker
  - [ ] Sprint goal textarea
  - [ ] Create and Cancel buttons (use button component)
- [ ] Integrate with sprint creation API
- [ ] Add form validation
  - [ ] Name required
  - [ ] Start date before end date
  - [ ] No overlapping sprints (async validation)
- [ ] Implement loading and error states
- [ ] Write component tests

**Deliverables**:

- Sprint creation modal
- Form validation
- Component tests

---

#### 2.1.6 Sprint Board Component

**Priority**: High  
**Estimated Time**: 3-4 days  
**Dependencies**: 2.1.1, 2.1.4, Phase 1.3.8  
**Assigned To**: BATATA2

**Frontend Tasks**:

- [ ] Create sprint board component (`sprint-board.component.ts`)
  - [ ] Similar to Kanban board but sprint-focused
  - [ ] Sprint header (name, dates, goal, progress bar)
  - [ ] Columns (Backlog, To Do, In Progress, In Review, Done)
  - [ ] Issue cards in columns
- [ ] Implement drag and drop for sprint issues
  - [ ] Move issues between columns (status change)
  - [ ] Update issue status on drop
  - [ ] Optimistic updates
- [ ] Integrate with sprint issues API
- [ ] Display sprint progress (completed vs total)
- [ ] Apply BOM CSS methodology
- [ ] Write component tests

**Deliverables**:

- Sprint board component
- Drag and drop functionality
- Component tests

---

#### 2.1.7 Sprint Detail View

**Priority**: High  
**Estimated Time**: 2-3 days  
**Dependencies**: 2.1.1, 2.1.3  
**Assigned To**: BATATA2

**Frontend Tasks**:

- [ ] Create sprint detail view component (`sprint-detail.component.ts`)
  - [ ] Sprint information panel (name, goal, dates, status)
  - [ ] Sprint metrics display (velocity, completion percentage)
  - [ ] Sprint issues list (all issues in sprint)
- [ ] Integrate with sprint metrics API
- [ ] Create burndown chart component (using ECharts)
  - [ ] Display burndown chart visualization
  - [ ] Show ideal vs actual progress
- [ ] Add loading states and error handling
- [ ] Write component tests

**Deliverables**:

- Sprint detail view
- Sprint metrics display
- Burndown chart component
- Component tests

---

#### 2.1.8 Sprint Planning UI

**Priority**: High  
**Estimated Time**: 2-3 days  
**Dependencies**: 2.1.1, 2.1.2, 2.1.6  
**Assigned To**: BATATA2

**Frontend Tasks**:

- [ ] Create sprint planning page/component (`sprint-planning.component.ts`)
  - [ ] Split view: backlog on left, sprint issues on right
  - [ ] Drag and drop from backlog to sprint
  - [ ] Remove issues from sprint (drag back or button)
- [ ] Implement drag and drop between backlog and sprint
  - [ ] Add issue to sprint on drop
  - [ ] Remove issue from sprint
  - [ ] Update sprint issue order
- [ ] Integrate with sprint issue management APIs
- [ ] Add loading states and error handling
- [ ] Write component tests

**Deliverables**:

- Sprint planning interface
- Drag and drop between backlog and sprint
- Component tests

---

#### 2.1.9 Sprint Completion UI

**Priority**: High  
**Estimated Time**: 1-2 days  
**Dependencies**: 2.1.3, 2.1.7  
**Assigned To**: BATATA2

**Frontend Tasks**:

- [ ] Create sprint completion modal component (`complete-sprint-modal.component.ts`)
  - [ ] Display incomplete issues list
  - [ ] Option to move incomplete issues to backlog
  - [ ] Complete sprint button
  - [ ] Confirmation message
- [ ] Integrate with sprint completion API
- [ ] Handle incomplete issues (show list, move to backlog)
- [ ] Show completion summary after sprint completion
- [ ] Add loading states and error handling
- [ ] Write component tests

**Deliverables**:

- Sprint completion UI
- Incomplete issue handling
- Component tests

---

#### 2.1.10 Backlog List API

**Priority**: High  
**Estimated Time**: 2-3 days  
**Dependencies**: 2.1.1  
**Assigned To**: HWIMDA1

**Backend Tasks**:

- [ ] Create backlog endpoint (GET /api/projects/:id/backlog)
  - [ ] Return issues not in any sprint
  - [ ] Include backlog order/priority
  - [ ] Filter options (by type, assignee, priority)
  - [ ] Sort options (priority, created date, updated date)
  - [ ] Pagination support
- [ ] Implement backlog filtering logic
  - [ ] Filter by issue type
  - [ ] Filter by assignee
  - [ ] Filter by priority
- [ ] Write backlog list API tests

**Deliverables**:

- Backlog list endpoint with filtering and pagination
- API tests

---

#### 2.1.11 Backlog Prioritization API

**Priority**: High  
**Estimated Time**: 1-2 days  
**Dependencies**: 2.1.10  
**Assigned To**: HWIMDA1

**Backend Tasks**:

- [ ] Design backlog order storage (add order field to issues table or separate table)
- [ ] Create backlog prioritization endpoint (PUT /api/projects/:id/backlog/prioritize)
  - [ ] Accept array of issue IDs in priority order
  - [ ] Update issue order in backlog
  - [ ] Store backlog order
- [ ] Create reorder single issue endpoint (PUT /api/projects/:id/backlog/issues/:issueId/reorder)
  - [ ] Move issue to specific position
- [ ] Write backlog prioritization API tests

**Deliverables**:

- Backlog prioritization endpoints
- API tests

---

#### 2.1.12 Backlog View Component

**Priority**: High  
**Estimated Time**: 3-4 days  
**Dependencies**: 2.1.10, Phase 1.3.6  
**Assigned To**: HWIMDA2

**Frontend Tasks**:

- [ ] Create backlog view component (`backlog.component.ts`)
  - [ ] Display issue list
  - [ ] Priority indicators
  - [ ] Issue cards with key info (title, type, assignee, priority)
- [ ] Implement drag-and-drop ordering
  - [ ] Reorder issues by dragging
  - [ ] Update priority order on drop
  - [ ] Visual feedback during drag
- [ ] Integrate with backlog list API
- [ ] Integrate with backlog prioritization API
- [ ] Apply BOM CSS methodology
- [ ] Write component tests

**Deliverables**:

- Backlog view component
- Drag-and-drop prioritization
- Component tests

---

#### 2.1.13 Backlog Filtering UI

**Priority**: High  
**Estimated Time**: 1-2 days  
**Dependencies**: 2.1.10, 2.1.12  
**Assigned To**: HWIMDA2

**Frontend Tasks**:

- [ ] Create backlog filter component (`backlog-filters.component.ts`)
  - [ ] Filter by issue type (dropdown)
  - [ ] Filter by assignee (user selector)
  - [ ] Filter by priority (checkbox group)
  - [ ] Clear filters button
- [ ] Implement search functionality
  - [ ] Search by issue title/description
- [ ] Integrate filters with backlog API
- [ ] Apply BOM CSS methodology
- [ ] Write component tests

**Deliverables**:

- Backlog filtering UI
- Search functionality
- Component tests

---

#### 2.1.14 Backlog to Sprint Integration

**Priority**: High  
**Estimated Time**: 1-2 days  
**Dependencies**: 2.1.12, 2.1.8  
**Assigned To**: HWIMDA2

**Frontend Tasks**:

- [ ] Add "Add to Sprint" functionality to backlog view
  - [ ] Button/menu item on each backlog issue
  - [ ] Sprint selector dropdown
  - [ ] Add to selected sprint
- [ ] Integrate with sprint issue management API
- [ ] Update backlog after adding to sprint (remove from backlog list)
- [ ] Add loading states and error handling
- [ ] Write component tests

**Deliverables**:

- Add to Sprint functionality from backlog
- Component tests

---

## Phase 2.2: Project Management Enhancements - Advanced Features (Weeks 5-10)

### Dependencies: Phase 1.3

#### 2.2.1 Custom Workflows Backend

**Priority**: High  
**Estimated Time**: 10-14 days  
**Dependencies**: Phase 1.3.2  
**Assigned To**: HWIMDA1

**Tasks**:

- [ ] Design workflow data model
  - [ ] Workflows table (id, project_id, name, is_default)
  - [ ] WorkflowStatuses table (id, workflow_id, name, order, is_initial, is_final)
  - [ ] WorkflowTransitions table (id, workflow_id, from_status_id, to_status_id, name)
- [ ] Create workflow creation endpoint (POST /api/projects/:id/workflows)
- [ ] Create workflow retrieval endpoint (GET /api/workflows/:id)
- [ ] Create workflow list endpoint (GET /api/projects/:id/workflows)
- [ ] Create workflow update endpoint (PUT /api/workflows/:id)
  - [ ] Add/remove statuses
  - [ ] Add/remove transitions
  - [ ] Update status order
- [ ] Create workflow deletion endpoint (DELETE /api/workflows/:id)
- [ ] Implement workflow validation
  - [ ] Ensure valid transitions
  - [ ] Check for required statuses
- [ ] Update issue status change to respect workflows
  - [ ] Validate transitions
  - [ ] Reject invalid transitions
- [ ] Create default workflow templates
- [ ] Write workflow API tests

**Deliverables**:

- Custom workflow system
- Workflow validation

---

#### 2.2.2 Custom Workflows Frontend

**Priority**: High  
**Estimated Time**: 10-14 days  
**Dependencies**: 2.2.1, Phase 1.3.6  
**Assigned To**: HWIMDA2

**Tasks**:

- [ ] Create workflow builder UI
  - [ ] Visual workflow editor
  - [ ] Status nodes
  - [ ] Transition arrows
  - [ ] Drag-and-drop status positioning
- [ ] Create workflow settings page
  - [ ] List workflows
  - [ ] Create/edit/delete workflows
  - [ ] Set default workflow
- [ ] Update issue status dropdown to show valid transitions
- [ ] Visualize workflow on issue detail page
- [ ] Add loading states and error handling

**Deliverables**:

- Workflow builder UI
- Workflow visualization

---

#### 2.2.3 Custom Fields Backend

**Priority**: High  
**Estimated Time**: 10-14 days  
**Dependencies**: Phase 1.3.2  
**Assigned To**: BATATA1

**Tasks**:

- [ ] Design custom field data model
  - [ ] CustomFields table (id, project_id, name, type, is_required, default_value, options)
  - [ ] CustomFieldValues table (id, custom_field_id, issue_id, value)
- [ ] Implement custom field types
  - [ ] Text
  - [ ] Number
  - [ ] Date
  - [ ] Select (dropdown)
  - [ ] Multi-select
  - [ ] User (single)
  - [ ] User (multiple)
- [ ] Create custom field creation endpoint (POST /api/projects/:id/custom-fields)
- [ ] Create custom field retrieval endpoint (GET /api/custom-fields/:id)
- [ ] Create custom field list endpoint (GET /api/projects/:id/custom-fields)
- [ ] Create custom field update endpoint (PUT /api/custom-fields/:id)
- [ ] Create custom field deletion endpoint (DELETE /api/custom-fields/:id)
- [ ] Update issue creation/update to handle custom fields
- [ ] Implement custom field validation
- [ ] Write custom field API tests

**Deliverables**:

- Custom field system
- Custom field value storage

---

#### 2.2.4 Custom Fields Frontend

**Priority**: High  
**Estimated Time**: 10-14 days  
**Dependencies**: 2.2.3, Phase 1.3.6  
**Assigned To**: BATATA2

**Tasks**:

- [ ] Create custom field form component
  - [ ] Dynamic form based on field type
  - [ ] Validation
  - [ ] Date picker
  - [ ] User selector
  - [ ] Select dropdown
- [ ] Create custom field management UI
  - [ ] List custom fields
  - [ ] Create custom field modal
  - [ ] Edit custom field
  - [ ] Delete custom field
- [ ] Integrate custom fields into issue creation form
- [ ] Integrate custom fields into issue edit form
- [ ] Display custom fields on issue detail page
- [ ] Add custom fields to issue list columns (optional)
- [ ] Add loading states and error handling

**Deliverables**:

- Custom field management UI
- Custom fields in issue forms

---

#### 2.2.5 Issue Linking Backend

**Priority**: Medium  
**Estimated Time**: 5-7 days  
**Dependencies**: Phase 1.3.2  
**Assigned To**: HWIMDA1

**Tasks**:

- [ ] Design issue link data model
  - [ ] IssueLinks table (id, source_issue_id, target_issue_id, link_type)
- [ ] Implement link types (Blocks, Blocked by, Relates to, Duplicate, etc.)
- [ ] Create create link endpoint (POST /api/issues/:id/links)
- [ ] Create link list endpoint (GET /api/issues/:id/links)
- [ ] Create delete link endpoint (DELETE /api/issue-links/:id)
- [ ] Implement bidirectional link handling
- [ ] Create link validation (prevent circular links)
- [ ] Write issue linking API tests

**Deliverables**:

- Issue linking system
- Link validation

---

#### 2.2.6 Issue Linking Frontend

**Priority**: Medium  
**Estimated Time**: 5-7 days  
**Dependencies**: 2.2.5, Phase 1.3.6  
**Assigned To**: HWIMDA2

**Tasks**:

- [ ] Create issue link component
  - [ ] Display linked issues
  - [ ] Link type indicators
  - [ ] Click to navigate
- [ ] Create add link modal
  - [ ] Search/select issue
  - [ ] Select link type
  - [ ] Add link
- [ ] Integrate into issue detail page
- [ ] Show link graph/visualization (optional)
- [ ] Add loading states and error handling

**Deliverables**:

- Issue linking UI
- Link management interface

---

#### 2.2.7 Advanced Search & Filters Backend

**Priority**: Medium  
**Estimated Time**: 7-10 days  
**Dependencies**: Phase 1.5.1, 2.2.3  
**Assigned To**: BATATA1

**Tasks**:

- [ ] Enhance search with advanced filters
  - [ ] Filter by custom fields
  - [ ] Filter by date ranges
  - [ ] Filter by multiple values
  - [ ] Complex boolean logic (AND, OR, NOT)
- [ ] Create saved filter endpoint (POST /api/filters)
  - [ ] Store filter criteria
  - [ ] Associate with user
- [ ] Create filter list endpoint (GET /api/filters)
- [ ] Create filter deletion endpoint (DELETE /api/filters/:id)
- [ ] Implement filter query language (similar to JQL)
- [ ] Optimize search queries for performance
- [ ] Write advanced search API tests

**Deliverables**:

- Advanced search system
- Saved filters

---

#### 2.2.8 Advanced Search & Filters Frontend

**Priority**: Medium  
**Estimated Time**: 7-10 days  
**Dependencies**: 2.2.7, Phase 1.5.2  
**Assigned To**: BATATA2

**Tasks**:

- [ ] Create advanced filter builder UI
  - [ ] Add filter conditions
  - [ ] Select field, operator, value
  - [ ] Group conditions (AND/OR)
  - [ ] Remove conditions
- [ ] Create saved filters UI
  - [ ] List saved filters
  - [ ] Save current filter
  - [ ] Load saved filter
  - [ ] Delete saved filter
- [ ] Enhance search UI with filter builder
- [ ] Display filter summary
- [ ] Add loading states and error handling

**Deliverables**:

- Advanced filter UI
- Saved filters interface

---

#### 2.2.9 Time Tracking Backend

**Priority**: Medium  
**Estimated Time**: 7-10 days  
**Dependencies**: Phase 1.3.2  
**Assigned To**: HWIMDA1

**Tasks**:

- [ ] Design time tracking data model
  - [ ] TimeEntries table (id, issue_id, user_id, hours, date, description, created_at)
- [ ] Create time entry creation endpoint (POST /api/issues/:id/time-entries)
- [ ] Create time entry list endpoint (GET /api/issues/:id/time-entries)
- [ ] Create time entry update endpoint (PUT /api/time-entries/:id)
- [ ] Create time entry deletion endpoint (DELETE /api/time-entries/:id)
- [ ] Create time tracking summary endpoint (GET /api/issues/:id/time-summary)
  - [ ] Total time logged
  - [ ] Time by user
  - [ ] Time by date range
- [ ] Implement time entry validation (positive hours, valid date)
- [ ] Write time tracking API tests

**Deliverables**:

- Time tracking system
- Time entry APIs

---

#### 2.2.10 Time Tracking Frontend

**Priority**: Medium  
**Estimated Time**: 5-7 days  
**Dependencies**: 2.2.9, Phase 1.3.6  
**Assigned To**: HWIMDA2

**Tasks**:

- [ ] Create time entry form component
  - [ ] Hours input
  - [ ] Date picker
  - [ ] Description textarea
- [ ] Create time entry list component
  - [ ] Display time entries
  - [ ] Edit/delete time entries
  - [ ] Time summary display
- [ ] Integrate into issue detail page
- [ ] Create time tracking widget/section
- [ ] Add time tracking to issue list (optional)
- [ ] Add loading states and error handling

**Deliverables**:

- Time tracking UI
- Time entry management

---

#### 2.2.11 Subtasks Backend

**Priority**: Medium  
**Estimated Time**: 5-7 days  
**Dependencies**: Phase 1.3.2  
**Assigned To**: BATATA1

**Tasks**:

- [ ] Extend issue model to support parent-child relationships
  - [ ] Add parent_issue_id to issues table
  - [ ] Add migration
- [ ] Update issue creation to support parent issue
- [ ] Create subtasks list endpoint (GET /api/issues/:id/subtasks)
- [ ] Implement subtask validation
  - [ ] Prevent circular references
  - [ ] Limit nesting depth
- [ ] Update issue queries to include subtasks
- [ ] Implement subtask completion affecting parent (optional)
- [ ] Write subtask API tests

**Deliverables**:

- Subtask system
- Subtask APIs

---

#### 2.2.12 Subtasks Frontend

**Priority**: Medium  
**Estimated Time**: 5-7 days  
**Dependencies**: 2.2.11, Phase 1.3.6  
**Assigned To**: BATATA2

**Tasks**:

- [ ] Create subtask list component
  - [ ] Display subtasks
  - [ ] Indent/hierarchy display
  - [ ] Checkbox for completion
- [ ] Create add subtask form
  - [ ] Quick add input
  - [ ] Create subtask
- [ ] Integrate into issue detail page
- [ ] Update issue list to show subtask indicators
- [ ] Add loading states and error handling

**Deliverables**:

- Subtask UI
- Subtask management

---

#### 2.2.13 Basic Dashboards Backend

**Priority**: Medium  
**Estimated Time**: 7-10 days  
**Dependencies**: Phase 1.3.2, 2.1.1  
**Assigned To**: HWIMDA1

**Tasks**:

- [ ] Design dashboard data model
  - [ ] Dashboards table (id, project_id, user_id, name, layout)
  - [ ] DashboardWidgets table (id, dashboard_id, type, config, position)
- [ ] Create dashboard creation endpoint (POST /api/dashboards)
- [ ] Create dashboard retrieval endpoint (GET /api/dashboards/:id)
- [ ] Create dashboard list endpoint (GET /api/dashboards)
- [ ] Create dashboard update endpoint (PUT /api/dashboards/:id)
- [ ] Create dashboard deletion endpoint (DELETE /api/dashboards/:id)
- [ ] Implement widget types
  - [ ] Issue status breakdown (pie/bar chart)
  - [ ] Issue count over time (line chart)
  - [ ] Assigned issues list
  - [ ] Recent activity feed
- [ ] Create widget data endpoints for each widget type
- [ ] Write dashboard API tests

**Deliverables**:

- Dashboard system
- Widget data APIs

---

#### 2.2.14 Basic Dashboards Frontend

**Priority**: Medium  
**Estimated Time**: 10-14 days  
**Dependencies**: 2.2.13, Phase 1.1.5  
**Assigned To**: HWIMDA2

**Tasks**:

- [ ] Choose charting library (Recharts, Chart.js, etc.)
- [ ] Create dashboard page layout
  - [ ] Grid layout system
  - [ ] Drag-and-drop widget positioning
  - [ ] Resizable widgets
- [ ] Create widget components
  - [ ] Issue status chart widget
  - [ ] Issue timeline widget
  - [ ] Assigned issues widget
  - [ ] Activity feed widget
- [ ] Create add widget UI
  - [ ] Widget type selector
  - [ ] Widget configuration
- [ ] Create dashboard settings
  - [ ] Edit dashboard name
  - [ ] Add/remove widgets
  - [ ] Configure widgets
- [ ] Add loading states and error handling

**Deliverables**:

- Dashboard UI
- Widget system

---

## Phase 2.3: Documentation Enhancements (Weeks 11-16)

### Dependencies: Phase 1.4

#### 2.3.1 Real-Time Collaboration Backend

**Priority**: High  
**Estimated Time**: 10-14 days  
**Dependencies**: Phase 1.4.2  
**Assigned To**: BATATA1

**Tasks**:

- [ ] Set up WebSocket server (Socket.io or similar)
- [ ] Implement room-based connections (per page)
- [ ] Create presence tracking
  - [ ] Track active users per page
  - [ ] Track user cursors/selections
- [ ] Implement operational transforms (OT) or CRDT for conflict resolution
- [ ] Create document synchronization
  - [ ] Broadcast edits to other users
  - [ ] Handle concurrent edits
  - [ ] Maintain document consistency
- [ ] Implement cursor broadcasting
  - [ ] Send cursor positions
  - [ ] Display other users' cursors
- [ ] Create user presence API (GET /api/pages/:id/presence)
- [ ] Handle connection/disconnection events
- [ ] Write collaboration API tests

**Deliverables**:

- Real-time collaboration system
- Presence tracking

---

#### 2.3.2 Real-Time Collaboration Frontend

**Priority**: High  
**Estimated Time**: 10-14 days  
**Dependencies**: 2.3.1, Phase 1.4.6  
**Assigned To**: BATATA2

**Tasks**:

- [ ] Integrate WebSocket client
- [ ] Create presence indicator component
  - [ ] Show active users on page
  - [ ] Display user avatars
- [ ] Update page editor for real-time sync
  - [ ] Connect to WebSocket room
  - [ ] Send edit events
  - [ ] Receive and apply remote edits
  - [ ] Display remote cursors
- [ ] Create user cursor component
  - [ ] Display other users' cursors
  - [ ] Show user name/avatar
- [ ] Handle connection states
  - [ ] Show disconnected state
  - [ ] Reconnect on connection loss
- [ ] Implement conflict resolution UI (if needed)
- [ ] Add loading states and error handling

**Deliverables**:

- Real-time collaboration UI
- Live editing with cursors

---

#### 2.3.3 Version History Backend

**Priority**: High  
**Estimated Time**: 7-10 days  
**Dependencies**: Phase 1.4.2  
**Assigned To**: HWIMDA1

**Tasks**:

- [ ] Design version history data model
  - [ ] PageVersions table (id, page_id, content, title, created_by, created_at, version_number)
- [ ] Create version on page update
  - [ ] Store snapshot of page state
  - [ ] Increment version number
  - [ ] Store editor/author info
- [ ] Create version list endpoint (GET /api/pages/:id/versions)
- [ ] Create version retrieval endpoint (GET /api/page-versions/:id)
- [ ] Create restore version endpoint (POST /api/page-versions/:id/restore)
  - [ ] Create new version from restored content
- [ ] Implement version diff calculation
- [ ] Create diff endpoint (GET /api/page-versions/:id/diff?compare_to=:versionId)
- [ ] Implement version cleanup policy (keep last N versions)
- [ ] Write version history API tests

**Deliverables**:

- Version history system
- Version restoration

---

#### 2.3.4 Version History Frontend

**Priority**: High  
**Estimated Time**: 7-10 days  
**Dependencies**: 2.3.3, Phase 1.4.6  
**Assigned To**: HWIMDA2

**Tasks**:

- [ ] Create version history sidebar/panel
  - [ ] List versions with timestamps
  - [ ] Show author for each version
- [ ] Create version preview component
  - [ ] Display version content
  - [ ] Compare with current version
- [ ] Create version diff viewer
  - [ ] Show added/removed/changed content
  - [ ] Side-by-side or unified diff view
- [ ] Create restore version functionality
  - [ ] Restore button
  - [ ] Confirmation dialog
- [ ] Integrate into page detail view
- [ ] Add loading states and error handling

**Deliverables**:

- Version history UI
- Version comparison and restoration

---

#### 2.3.5 Advanced Templates & Macros Backend

**Priority**: Medium  
**Estimated Time**: 7-10 days  
**Dependencies**: Phase 1.4.4  
**Assigned To**: BATATA1

**Tasks**:

- [ ] Expand template system
  - [ ] Template categories
  - [ ] Template variables/placeholders
  - [ ] Template inheritance
- [ ] Create macro system
  - [ ] Macros table (id, name, code, config_schema)
  - [ ] Macro types (table, code block, info panel, etc.)
- [ ] Create macro execution engine
  - [ ] Parse macro syntax in content
  - [ ] Execute macros
  - [ ] Render macro output
- [ ] Create macro list endpoint (GET /api/macros)
- [ ] Create macro execution endpoint (POST /api/macros/execute)
- [ ] Implement default macros
  - [ ] Info/Warning/Error panels
  - [ ] Code blocks with syntax highlighting
  - [ ] Tables
  - [ ] Page tree
  - [ ] Issue embed
- [ ] Write macro API tests

**Deliverables**:

- Macro system
- Template enhancements

---

#### 2.3.6 Advanced Templates & Macros Frontend

**Priority**: Medium  
**Estimated Time**: 7-10 days  
**Dependencies**: 2.3.5, Phase 1.4.6  
**Assigned To**: BATATA2

**Tasks**:

- [ ] Create template gallery UI
  - [ ] Browse templates by category
  - [ ] Preview templates
  - [ ] Use template button
- [ ] Create macro selector in editor
  - [ ] Insert macro button
  - [ ] Macro picker modal
  - [ ] Macro configuration form
- [ ] Implement macro rendering in page view
  - [ ] Parse and render macros
  - [ ] Handle macro errors gracefully
- [ ] Create macro preview in editor
- [ ] Add loading states and error handling

**Deliverables**:

- Template gallery UI
- Macro editor integration

---

#### 2.3.7 Whiteboards Backend

**Priority**: Medium  
**Estimated Time**: 10-14 days  
**Dependencies**: Phase 1.4.2  
**Assigned To**: HWIMDA1

**Tasks**:

- [ ] Design whiteboard data model
  - [ ] Whiteboards table (id, space_id, name, data (JSON), created_by, updated_by)
- [ ] Create whiteboard creation endpoint (POST /api/whiteboards)
- [ ] Create whiteboard retrieval endpoint (GET /api/whiteboards/:id)
- [ ] Create whiteboard update endpoint (PUT /api/whiteboards/:id)
  - [ ] Store whiteboard state (drawings, shapes, text)
- [ ] Create whiteboard list endpoint (GET /api/whiteboards)
- [ ] Create whiteboard deletion endpoint (DELETE /api/whiteboards/:id)
- [ ] Implement whiteboard export to image/PDF
- [ ] Integrate whiteboard with real-time collaboration
- [ ] Write whiteboard API tests

**Deliverables**:

- Whiteboard system
- Whiteboard APIs

---

#### 2.3.8 Whiteboards Frontend

**Priority**: Medium  
**Estimated Time**: 10-14 days  
**Dependencies**: 2.3.7, 2.3.1  
**Assigned To**: HWIMDA2

**Tasks**:

- [ ] Choose whiteboard library (Excalidraw, Fabric.js, etc.) or build custom
- [ ] Create whiteboard component
  - [ ] Infinite canvas
  - [ ] Drawing tools (pen, shapes, text)
  - [ ] Selection and manipulation
  - [ ] Zoom and pan
- [ ] Create whiteboard toolbar
  - [ ] Tool selector
  - [ ] Color picker
  - [ ] Undo/redo
  - [ ] Export button
- [ ] Integrate real-time collaboration
  - [ ] Sync drawings in real-time
  - [ ] Show other users' cursors
- [ ] Create whiteboard list page
- [ ] Integrate whiteboard embedding in pages (optional)
- [ ] Add loading states and error handling

**Deliverables**:

- Whiteboard UI
- Real-time whiteboard collaboration

---

#### 2.3.9 Advanced Permissions Backend

**Priority**: Medium  
**Estimated Time**: 7-10 days  
**Dependencies**: Phase 1.4.1  
**Assigned To**: BATATA1

**Tasks**:

- [ ] Extend permission system
  - [ ] Page-level permissions (read, edit, delete, admin)
  - [ ] Space-level permissions (view, create, edit, delete, admin)
- [ ] Create permission management endpoints
  - [ ] Get permissions (GET /api/pages/:id/permissions)
  - [ ] Update permissions (PUT /api/pages/:id/permissions)
- [ ] Implement permission inheritance
  - [ ] Space permissions inherit to pages
  - [ ] Override inheritance for specific pages
- [ ] Create permission checking utilities
- [ ] Write permission API tests

**Deliverables**:

- Advanced permission system
- Permission inheritance

---

#### 2.3.10 Advanced Permissions Frontend

**Priority**: Medium  
**Estimated Time**: 5-7 days  
**Dependencies**: 2.3.9, Phase 1.4.5  
**Assigned To**: BATATA2

**Tasks**:

- [ ] Create permission management UI
  - [ ] Permission matrix/grid
  - [ ] User/group permission assignment
  - [ ] Permission level selector
- [ ] Create page permission settings
- [ ] Create space permission settings
- [ ] Display permission indicators (lock icons, etc.)
- [ ] Add loading states and error handling

**Deliverables**:

- Permission management UI

---

#### 2.3.11 Export Functionality Backend

**Priority**: Low  
**Estimated Time**: 5-7 days  
**Dependencies**: Phase 1.4.2  
**Assigned To**: HWIMDA1

**Tasks**:

- [ ] Create PDF export endpoint (GET /api/pages/:id/export/pdf)
  - [ ] Convert page content to PDF
  - [ ] Include images and formatting
- [ ] Create Markdown export endpoint (GET /api/pages/:id/export/markdown)
- [ ] Create HTML export endpoint (GET /api/pages/:id/export/html)
- [ ] Create space export endpoint (GET /api/spaces/:id/export)
  - [ ] Export all pages in space
  - [ ] Include hierarchy
- [ ] Implement export queuing for large exports
- [ ] Write export API tests

**Deliverables**:

- Export functionality
- Multiple export formats

---

#### 2.3.12 Export Functionality Frontend

**Priority**: Low  
**Estimated Time**: 3-5 days  
**Dependencies**: 2.3.11, Phase 1.4.6  
**Assigned To**: HWIMDA2

**Tasks**:

- [ ] Create export menu/button
- [ ] Create export options UI
  - [ ] Format selector (PDF, Markdown, HTML)
  - [ ] Export button
- [ ] Handle export download
- [ ] Show export progress for large exports
- [ ] Add loading states and error handling

**Deliverables**:

- Export UI
- Export functionality

---

## Phase 2.4: Platform Improvements (Weeks 17-24)

### Dependencies: Phase 1

#### 2.4.1 Mobile Apps - iOS/Android Setup

**Priority**: High  
**Estimated Time**: 5-7 days  
**Dependencies**: Phase 1.7.1  
**Assigned To**: BATATA2, HWIMDA2 (shared)

**Tasks**:

- [ ] Choose mobile framework (React Native, Flutter)
- [ ] Set up mobile project structure
- [ ] Configure iOS project (Xcode)
- [ ] Configure Android project (Android Studio)
- [ ] Set up navigation (React Navigation or similar)
- [ ] Set up API client for mobile
- [ ] Set up authentication flow for mobile
- [ ] Create basic app shell/navigation

**Deliverables**:

- Mobile app foundation
- Basic navigation

---

#### 2.4.2 Mobile Apps - Core Features

**Priority**: High  
**Estimated Time**: 14-21 days  
**Dependencies**: 2.4.1, Phase 1  
**Assigned To**: BATATA2, HWIMDA2 (shared)

**Tasks**:

- [ ] Implement authentication screens (login, register)
- [ ] Implement issue list screen
- [ ] Implement issue detail screen
- [ ] Implement issue creation/edit screens
- [ ] Implement page list screen
- [ ] Implement page detail/view screen
- [ ] Implement page editor screen
- [ ] Implement Kanban board screen (mobile-optimized)
- [ ] Implement notifications screen
- [ ] Implement search functionality
- [ ] Implement offline mode (sync when online)
- [ ] Add push notifications
- [ ] Test on iOS devices
- [ ] Test on Android devices

**Deliverables**:

- Mobile apps for iOS and Android
- Core features on mobile

---

#### 2.4.3 Advanced API - Webhooks

**Priority**: Medium  
**Estimated Time**: 7-10 days  
**Dependencies**: Phase 1.7.1  
**Assigned To**: BATATA1

**Tasks**:

- [ ] Design webhook data model
  - [ ] Webhooks table (id, organization_id, url, events, secret, active)
- [ ] Create webhook creation endpoint (POST /api/webhooks)
- [ ] Create webhook list endpoint (GET /api/webhooks)
- [ ] Create webhook update endpoint (PUT /api/webhooks/:id)
- [ ] Create webhook deletion endpoint (DELETE /api/webhooks/:id)
- [ ] Implement webhook event system
  - [ ] Define event types (issue.created, issue.updated, etc.)
  - [ ] Trigger webhooks on events
  - [ ] Retry logic for failed webhooks
  - [ ] Webhook signature generation
- [ ] Create webhook delivery logging
- [ ] Create webhook test endpoint (POST /api/webhooks/:id/test)
- [ ] Write webhook API tests

**Deliverables**:

- Webhook system
- Webhook management APIs

---

#### 2.4.4 Advanced API - GraphQL (Optional)

**Priority**: Low  
**Estimated Time**: 10-14 days  
**Dependencies**: Phase 1.7.1  
**Assigned To**: HWIMDA1

**Tasks**:

- [ ] Set up GraphQL server (Apollo Server, GraphQL.js)
- [ ] Define GraphQL schema
  - [ ] Types (User, Issue, Page, etc.)
  - [ ] Queries
  - [ ] Mutations
  - [ ] Subscriptions (for real-time)
- [ ] Implement resolvers
- [ ] Set up GraphQL authentication
- [ ] Create GraphQL documentation
- [ ] Write GraphQL tests
- [ ] Create GraphQL client examples

**Deliverables**:

- GraphQL API
- GraphQL documentation

---

#### 2.4.5 Additional Integrations

**Priority**: Medium  
**Estimated Time**: 5-7 days per integration  
**Dependencies**: Phase 1.7.1  
**Assigned To**: BATATA1, HWIMDA1 (shared)

**Tasks**:

- [ ] **GitLab Integration** (similar to GitHub)
  - [ ] OAuth setup
  - [ ] Webhook receiver
  - [ ] Issue linking
- [ ] **Bitbucket Integration**
  - [ ] OAuth setup
  - [ ] Webhook receiver
  - [ ] Issue linking
- [ ] **Microsoft Teams Integration**
  - [ ] Bot setup
  - [ ] Notification sending
  - [ ] Command handling
- [ ] **Discord Integration**
  - [ ] Bot setup
  - [ ] Notification sending
- [ ] **Email Integration**
  - [ ] Create issue from email
  - [ ] Reply to comments via email

**Deliverables**:

- Multiple integrations
- Integration documentation

---

#### 2.4.6 Automation Rules Backend

**Priority**: High  
**Estimated Time**: 10-14 days  
**Dependencies**: Phase 1.3.2, 2.2.1  
**Assigned To**: HWIMDA1

**Tasks**:

- [ ] Design automation rule data model
  - [ ] AutomationRules table (id, project_id, name, trigger, conditions, actions, enabled)
- [ ] Implement trigger types
  - [ ] Issue created
  - [ ] Issue updated
  - [ ] Issue status changed
  - [ ] Comment added
  - [ ] Scheduled (cron)
- [ ] Implement condition types
  - [ ] Field equals/contains/matches
  - [ ] Boolean logic (AND, OR, NOT)
- [ ] Implement action types
  - [ ] Assign issue
  - [ ] Change status
  - [ ] Add comment
  - [ ] Update fields
  - [ ] Send notification
  - [ ] Create issue
- [ ] Create automation rule execution engine
- [ ] Create automation rule CRUD endpoints
- [ ] Create automation rule testing endpoint
- [ ] Write automation rule API tests

**Deliverables**:

- Automation rule system
- Rule execution engine

---

#### 2.4.7 Automation Rules Frontend

**Priority**: High  
**Estimated Time**: 10-14 days  
**Dependencies**: 2.4.6, Phase 1.1.5  
**Assigned To**: HWIMDA2

**Tasks**:

- [ ] Create automation rule list page
- [ ] Create automation rule builder UI
  - [ ] Trigger selector
  - [ ] Condition builder
  - [ ] Action builder
  - [ ] Rule name and description
- [ ] Create rule testing UI
  - [ ] Test rule button
  - [ ] Show test results
- [ ] Create rule enable/disable toggle
- [ ] Create rule execution log/history
- [ ] Add loading states and error handling

**Deliverables**:

- Automation rule builder UI
- Rule management interface

---

#### 2.4.8 Advanced Reporting Backend

**Priority**: Medium  
**Estimated Time**: 10-14 days  
**Dependencies**: Phase 1.3.2, 2.1.1, 2.2.9  
**Assigned To**: BATATA1

**Tasks**:

- [ ] Create report generation system
  - [ ] Velocity reports
  - [ ] Burndown charts data
  - [ ] Burnup charts data
  - [ ] Cumulative flow diagrams
  - [ ] Time tracking reports
- [ ] Create report endpoints
  - [ ] Sprint velocity (GET /api/reports/sprint-velocity)
  - [ ] Burndown (GET /api/reports/burndown)
  - [ ] Time tracking (GET /api/reports/time-tracking)
- [ ] Implement report data aggregation
- [ ] Create report scheduling (optional)
- [ ] Write report API tests

**Deliverables**:

- Reporting system
- Report data APIs

---

#### 2.4.9 Advanced Reporting Frontend

**Priority**: Medium  
**Estimated Time**: 7-10 days  
**Dependencies**: 2.4.8, 2.2.14  
**Assigned To**: BATATA2

**Tasks**:

- [ ] Create report selection UI
- [ ] Create velocity chart visualization
- [ ] Create burndown chart visualization
- [ ] Create burnup chart visualization
- [ ] Create cumulative flow diagram
- [ ] Create time tracking report tables
- [ ] Add report filters (date range, project, etc.)
- [ ] Add report export (PDF, CSV)
- [ ] Add loading states and error handling

**Deliverables**:

- Report visualizations
- Report UI

---

## Summary

**Total Estimated Timeline**: 24 weeks (6 months)

**Key Milestones**:

- Week 4: Sprints and Scrum complete
- Week 10: Advanced PM features complete
- Week 16: Documentation enhancements complete
- Week 24: Platform improvements complete

**Team Size Recommendations**:

- 2-3 Backend developers
- 2-3 Frontend developers
- 1-2 Mobile developers
- 1 DevOps engineer
- 1 QA engineer
