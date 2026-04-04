# Workflow, sprint-scoped status & boards as filters — spec

**Status**: Draft  
**Date**: 2026-04-04  
**Replaces**: Per-board column model in `PHASE_2_5_ISSUE_BOARDS.md` (lists/moves) once implemented.

---

## Locked decisions

| Topic                   | Decision                                                                                                                              |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| Column source           | **Project workflow** only (ordered labels). No `board_lists` for columns.                                                             |
| Issue “status”          | **`workflow_label_id` on `sprint_issues`** (Approach A). No parallel enum as source of truth after cutover.                           |
| Backlog                 | Issue **not** in any sprint ⇒ **no** `sprint_issues` row ⇒ **no** workflow column label. UI term: **Backlog**.                        |
| Board                   | **Saved filter** (`scope_config` / rename to `filter_config` in API docs). Same workflow columns for every board in the project.      |
| Sprint board vs Backlog | **Separate surfaces**: sprint board = issues **in selected sprint** only; Backlog = issues with **zero** `sprint_issues` rows.        |
| Label split             | **`labels.kind`**: `column` \| `tag`. Only `column` labels may appear in `workflow_columns` and in `sprint_issues.workflow_label_id`. |

---

## F1 — Project workflow (columns)

### Functional

- Each project has **one active workflow** (`projects.active_workflow_id`).
- A workflow has an **ordered list of columns**; each column is **one project label** with `kind = column`.
- All boards in the project show **the same columns** in that order.
- Users can **reorder columns**, **add** a column (pick/create a `column` label), **remove** a column (blocked if any `sprint_issues` references that label — or force reassign first).

### Technical

- **Table `workflow_columns`**: `id`, `workflow_id` (FK `workflows.id`), `label_id` (FK `labels.id`), `position` (int, unique per `workflow_id`).
- **`labels`**: add `kind VARCHAR` check in `('column','tag')`, default `tag`; existing rows → migration sets `column` for seeded workflow labels.
- **`projects`**: add `active_workflow_id` UUID FK → `workflows.id`, nullable until backfill.
- **Constraints**: `workflow.project_id` = `labels.project_id` for every `(workflow_id, label_id)` via app validation + DB trigger optional.
- **API (indicative)**:
  - `GET /projects/{id}/workflow` → workflow id + columns `{ label_id, name, color, position }`.
  - `PUT /projects/{id}/workflow/columns` → replace ordered `label_ids[]` (transactional).
- **Errors**: `409` if removing/reordering breaks referenced `sprint_issues.workflow_label_id`.

### Actions

- [ ] BE: Migration `workflow_columns`, `labels.kind`, `projects.active_workflow_id`.
- [ ] BE: CRUD + validation + tests.
- [ ] BE: Seed: default workflow + 3–4 column labels per demo project.

---

## F2 — Sprint-scoped status

### Functional

- An issue **in sprint S** has exactly **one** workflow column: the label stored for that sprint membership.
- **Add to sprint**: create `sprint_issues` with `workflow_label_id` = **first** workflow column (`position = 0`).
- **Move on board**: change `workflow_label_id` within **same sprint**; label must be in **active** workflow columns.
- **Remove from sprint**: delete `sprint_issues` row → issue returns to **Backlog** (no column label).

### Technical

- **`sprint_issues`**: add `workflow_label_id` UUID NOT NULL FK → `labels.id` (after backfill).
- **Invariant**: for each row, `labels.kind = 'column'` and label ∈ `workflow_columns` for `project.active_workflow_id` (validate in use case).
- **API (indicative)**:
  - `POST /sprints/{sprint_id}/issues` body `{ issue_id }` → insert `sprint_issues` with default column + `order`.
  - `DELETE /sprints/{sprint_id}/issues/{issue_id}` → remove from sprint.
  - `PATCH /sprints/{sprint_id}/issues/{issue_id}/workflow` body `{ workflow_label_id }` → column move (replaces `move_board_issue` for label columns).
- **Errors**: `400` invalid label; `409` issue already in sprint; `404` not in sprint.

### Actions

- [ ] BE: Migration + backfill: existing sprint members → map `issues.status` → closest column label or first column.
- [ ] BE: Use cases + endpoints + deprecate label-swap path in `MoveBoardIssue` for new clients.
- [ ] BE: Tests: add, move, remove, constraint violations.

---

## F3 — Backlog

### Functional

- **Backlog query**: issues where `project_id = P` and **no** row in `sprint_issues` for that issue (any sprint).
- **Create issue**: lands in Backlog unless API explicitly adds to sprint.
- **Add to sprint** from Backlog: F2 `POST`.

### Technical

- **Query**: `NOT EXISTS (SELECT 1 FROM sprint_issues si WHERE si.issue_id = issues.id)` (+ project filter + soft-delete).
- **API**: `GET /projects/{id}/issues?backlog_only=true` or dedicated `GET /projects/{id}/backlog/issues` (pick one; document pagination).

### Actions

- [ ] BE: Backlog list endpoint + tests.
- [ ] FE: Backlog tab/view + “Add to sprint” bulk/single actions.

---

## F4 — Board as filter + sprint view

### Functional

- **Board** = name + **filter** (assignee, reporter, text, tag labels, type, priority — same dimensions as today’s `scope_config` where still relevant).
- **Default board**: empty filter = all issues in scope (project board) **still subject to sprint/backlog context** (see below).
- **Sprint board page**: user picks **sprint** + **board**; response = columns from workflow; each cell = issues **in that sprint**, **matching board filter**, with that `workflow_label_id`.

### Technical

- **`boards`**: keep `scope_config` JSON schema; **stop reading** `board_lists` for column layout.
- **New or refactored** `GET` (indicative):  
  `GET /projects/{project_id}/boards/{board_id}/sprint/{sprint_id}/view`  
  Response: `{ columns: [{ label_id, name, color, position, issues: IssueDTO[] }] }`  
  Server-side filter application order: sprint membership → board filter → group by `workflow_label_id`.
- **Remove** (eventually): `GET .../boards/{id}/issues` that used `board_lists` grouping, or shim to new shape during transition.

### Actions

- [ ] BE: New view endpoint + filter reuse from `GetBoardIssues` scope helpers (refactor).
- [ ] BE: Delete/stop creating `board_lists` rows; migration drop or orphan table after cutover.
- [ ] FE: Kanban loads columns from response keys, not from `board_lists`; board settings = filter editor only.

---

## F5 — Cutover: `issues.status` & old board moves

### Functional

- After cutover, **no** user-facing `todo`/`in_progress`/… on issue; display **workflow label** for current sprint context; Backlog shows **no** status column or shows “—” / “Backlog”.

### Technical

- **Migration**: `issues.status` → optional drop column after dual-read period; or keep **read-only** derived for admin export only (YAGNI: drop).
- **DTOs**: remove `status` from create/update; `GET issue` includes `workflow_label` **when** `?sprint_id=` provided or embed “current sprint” from query param.
- **Delete** `MoveBoardIssue` list-based label logic; **replace** with F2 PATCH.
- **Group boards**: same rules; `workflow_label_id` still references **project** column labels (per issue’s project).

### Actions

- [ ] BE: DTO + OpenAPI updates; migration script; seed rewrite.
- [ ] FE: Remove status select where replaced by column move; issue detail shows sprint + label.

---

## F6 — Sprint complete (optional v1.1)

### Functional

- Completing a sprint should **not** silently delete history needed for velocity; either **archive** `sprint_issues` rows to `sprint_issues_archive` or mark sprint + rows read-only.

### Technical

- Extend `POST /sprints/{id}/complete` to document behavior; optional table `sprint_issue_snapshots(sprint_id, issue_id, workflow_label_id, captured_at)`.

### Actions

- [ ] BE: Decide snapshot vs read-only; implement; tests.

---

## F7 — Org workflow template (optional)

### Functional

- Admin defines template (ordered names + colors); **Apply to project** creates labels (`kind=column`), workflow, sets `active_workflow_id`.

### Technical

- Tables `workflow_templates`, `workflow_template_columns` at org level; `POST /organizations/{id}/workflow-templates/{tid}/apply` `{ project_id }`.

### Actions

- [ ] BE: Template CRUD + apply + tests.

---

## Frontend — mapped actions

| ID  | Depends on | Actions                                                                                     |
| --- | ---------- | ------------------------------------------------------------------------------------------- |
| FE1 | F1 API     | Project settings: workflow editor (order/add/remove column labels).                         |
| FE2 | F3 API     | Backlog list + Add to sprint.                                                               |
| FE3 | F4 API     | Sprint board: columns from API; CDK drop → `PATCH .../workflow`.                            |
| FE4 | F4 API     | Board selector: create/edit **filter only**; remove add-column modal tied to `board_lists`. |
| FE5 | F5 API     | Issue create/edit: no legacy status; optional sprint picker.                                |
| FE6 | —          | i18n: Backlog, Sprint, column names from labels.                                            |
| FE7 | —          | Tests: backlog → sprint → move column → remove from sprint.                                 |

---

## Delivery order

1. **F1** → **F2** → **F4** (view + move) can ship a vertical slice.
2. **F3** Backlog endpoint in parallel once F2 exists.
3. **F5** cutover when FE3/FE4 ready.
4. **F6** / **F7** anytime after F2.

---

## Post-cutover cleanup

- [ ] Remove dead `move_board_issue` / `board_lists` code paths and obsolete modals.
- [ ] Mark superseded sections in `PHASE_2_5_ISSUE_BOARDS.md`; API changelog / OpenAPI.

---

## Traceability

| Old concept                       | New concept                                                    |
| --------------------------------- | -------------------------------------------------------------- |
| `issues.status`                   | `sprint_issues.workflow_label_id` (in sprint) / none (Backlog) |
| `board_lists` + list_type `label` | `workflow_columns`                                             |
| `move_board_issue` (label swap)   | `PATCH .../sprint/.../workflow`                                |
| Board scope only                  | Board scope + workflow columns from project                    |

---

_End of spec_
