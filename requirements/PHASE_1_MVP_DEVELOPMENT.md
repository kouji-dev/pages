# Phase 1: MVP Development Tasks

**Timeline**: Months 1-6  
**Goal**: Launch a minimum viable product with core project management and documentation features

---

## Overview

This phase focuses on building the foundational features required for a functional product. Tasks are organized by dependency order and logical groupings to ensure efficient development workflow.

### Task Organization Principles

**Each task is designed to be:**

- **Concise**: Focused on a single, clear deliverable
- **Isolated**: Contains separated logic that doesn't overlap with other tasks
- **Independent**: Can be worked on independently by assigned developers
- **Testable**: Includes its own testing requirements
- **Parallelizable**: Multiple tasks can be worked on simultaneously when dependencies allow

**Task Structure:**

- Each task has a unique ID (e.g., `1.1.5`, `1.2.1`)
- Clear dependencies listed (minimal and specific)
- Single developer assignment (or shared for collaborative tasks)
- Estimated time for completion
- Deliverables clearly defined

---

## Phase 1.1: Foundation & Infrastructure Setup (Weeks 1-3)

### Dependencies: None (Must be completed first)

#### 1.1.1 Project Structure & Repository Setup

**Priority**: Critical  
**Estimated Time**: 3-5 days  
**Assigned To**: BATATA1, HWIMDA1 (shared setup)

**Tasks**:

- [x] Initialize monorepo structure (clients/, libraries/, services/)
- [x] Set up version control (Git repository)
- [x] Configure `.gitignore` files
- [-] Create project documentation structure (README exists, CONTRIBUTING pending)
- [x] Set up code formatting (Prettier) and linting (oxlint) configurations
- [-] Initialize package.json/pyproject.toml with project metadata (package.json done, pyproject.toml pending)
- [-] Create directory structure for frontend and backend (frontend done: clients/, libraries/, backend pending: services/)
- [x] Set up environment variable templates (.env.example files) (environment.ts and environment.production.ts exist)
- [x] Configure TypeScript/JavaScript build tooling (Angular 21 with esbuild)
- [x] Set up pre-commit hooks (Husky with lint-staged)

**Deliverables**:

- Clean repository structure
- Development environment setup documented
- Code quality tools configured

---

#### 1.1.2 Database Schema Design & Setup

**Priority**: Critical  
**Estimated Time**: 5-7 days  
**Dependencies**: 1.1.1  
**Assigned To**: BATATA1

**Backend Tasks**:

- [ ] Design core database schema (users, organizations, projects, issues, pages, comments)
- [ ] Set up PostgreSQL database
- [ ] Choose and configure ORM (Prisma, TypeORM, SQLAlchemy, etc.)
- [ ] Create migration system setup
- [ ] Write initial migrations for:
  - [ ] Users table (id, email, password_hash, name, avatar_url, created_at, updated_at, deleted_at)
  - [ ] Organizations table (id, name, slug, settings, created_at, updated_at)
  - [ ] OrganizationMembers table (organization_id, user_id, role, created_at)
  - [ ] Projects table (id, organization_id, name, key, description, created_at, updated_at)
  - [ ] ProjectMembers table (project_id, user_id, role, created_at)
  - [ ] Issues table (id, project_id, type, title, description, status, priority, assignee_id, reporter_id, created_at, updated_at)
  - [ ] Comments table (id, issue_id, user_id, content, created_at, updated_at)
  - [ ] Pages table (id, space_id, title, content, parent_id, created_by, updated_by, created_at, updated_at)
  - [ ] Spaces table (id, organization_id, name, key, description, created_at, updated_at)
  - [ ] Attachments table (id, entity_type, entity_id, file_name, file_size, mime_type, storage_path, uploaded_by, created_at)
  - [ ] Notifications table (id, user_id, type, title, content, read, created_at)
- [ ] Create database indexes for performance (foreign keys, search fields, timestamps)
- [ ] Set up database connection pooling
- [ ] Create seed scripts for development data
- [ ] Write database schema documentation

**Deliverables**:

- Complete database schema
- Migration scripts
- Database documentation

---

#### 1.1.3 Authentication & Authorization Foundation

**Priority**: Critical  
**Estimated Time**: 7-10 days  
**Dependencies**: 1.1.2  
**Assigned To**: HWIMDA1

**Backend Tasks**:

- [ ] Implement password hashing (bcrypt/Argon2)
- [ ] Create user registration endpoint (POST /api/auth/register)
  - [ ] Validate email format and uniqueness
  - [ ] Validate password strength
  - [ ] Hash password before storing
  - [ ] Create user record
  - [ ] Generate and return JWT token
  - [ ] Send welcome email (async)
- [ ] Create user login endpoint (POST /api/auth/login)
  - [ ] Validate credentials
  - [ ] Generate JWT access token
  - [ ] Generate refresh token (optional)
  - [ ] Return user data and tokens
- [ ] Create password reset flow
  - [ ] Request reset endpoint (POST /api/auth/password/reset-request)
  - [ ] Reset token generation and storage
  - [ ] Reset email sending
  - [ ] Password reset endpoint (POST /api/auth/password/reset)
- [ ] Implement JWT middleware for protected routes
  - [ ] Token validation
  - [ ] User context injection
  - [ ] Token refresh handling
- [ ] Create permission/role system foundation
  - [ ] Define base roles (admin, member, viewer)
  - [ ] Create role checking utilities
  - [ ] Implement organization-level permissions
- [ ] Create email verification flow (optional for MVP)
- [ ] Write authentication API documentation
- [ ] Write unit tests for auth endpoints

**Frontend Tasks**:

- [ ] Create authentication context/provider
- [ ] Implement login page UI
  - [ ] Email/password form
  - [ ] Form validation
  - [ ] Error handling and display
  - [ ] Loading states
- [ ] Implement registration page UI
  - [ ] User registration form
  - [ ] Password strength indicator
  - [ ] Terms of service checkbox
- [ ] Implement password reset pages
  - [ ] Request reset page
  - [ ] Reset password page
- [ ] Create protected route wrapper component
- [ ] Implement token storage (localStorage or httpOnly cookies)
- [ ] Create logout functionality
- [ ] Add form validation libraries (React Hook Form + Zod/Yup)

**Deliverables**:

- Working authentication system
- Login/register UI
- Protected route system

---

#### 1.1.4 Basic API Structure & Infrastructure

**Priority**: Critical  
**Estimated Time**: 5-7 days  
**Dependencies**: 1.1.1, 1.1.2  
**Assigned To**: BATATA1

**Backend Tasks**:

- [ ] Set up Express/Fastify/FastAPI server
- [ ] Configure CORS middleware
- [ ] Set up request/response logging middleware
- [ ] Create error handling middleware
  - [ ] Global error handler
  - [ ] Error response formatting
  - [ ] Logging errors
- [ ] Set up request validation middleware (express-validator, Pydantic)
- [ ] Create API response formatting utilities
- [ ] Set up API versioning structure (/api/v1)
- [ ] Create health check endpoint (GET /api/health)
- [ ] Set up API documentation (Swagger/OpenAPI)
- [ ] Configure rate limiting
- [ ] Set up request ID tracking
- [ ] Create API testing utilities

**Deliverables**:

- Functional API server
- Error handling system
- API documentation framework

---

#### 1.1.5 Base Layout Component

**Priority**: Critical  
**Estimated Time**: 2-3 days  
**Dependencies**: 1.1.1  
**Assigned To**: BATATA2

**Frontend Tasks**:

- [x] Create base layout component (`base-layout.ts`)
  - [x] Component with standalone directive
  - [x] Layout structure (header, sidebar, main, footer sections)
  - [x] Use modern Angular APIs (signals, input(), computed())
- [x] Implement header/navbar section
  - [x] Responsive header component (Jira/Confluence style toolbar, 56px height)
  - [x] Logo/branding area
  - [x] Navigation menu slots (nav, breadcrumbs, search, quick-actions, notifications, user-menu)
  - [x] User menu placeholder
- [x] Implement sidebar navigation
  - [x] Collapsible sidebar component (toggleSidebar() method, sidebarOpen signal)
  - [x] Navigation menu structure (sidebar-nav slot)
  - [x] Responsive behavior (hidden on mobile, overlay on open)
- [x] Implement main content area
  - [x] Router outlet wrapper
  - [x] Content container with padding (Notion-style: ~96px sides on desktop, max-width 1000px)
- [x] Implement footer section (optional)
  - [x] Footer component with links (footer-links slot)
  - [x] Copyright information (currentYear computed signal)
- [x] Apply BOM CSS methodology with Tailwind
  - [x] Use `@reference "#mainstyles"` in component styles (references app1 styles which includes #theme)
  - [x] Apply Tailwind utilities with `@apply`
  - [x] Use Pages design tokens (CSS custom properties from shared-ui theme)
- [x] Write component tests (base-layout.spec.ts with comprehensive test coverage)
- [x] Ensure mobile responsiveness (responsive breakpoints, mobile sidebar overlay, responsive header adjustments)

**Deliverables**:

- Base layout component with header, sidebar, main, and footer
- Responsive design
- Component tests

**Note**: ✅ **COMPLETED** - Production-ready base layout component fully implemented with:

- Complete header toolbar (Jira/Confluence style) with logo, breadcrumbs, search, navigation, quick actions, notifications, and user menu slots
- Collapsible sidebar (Notion style) with responsive mobile overlay
- Main content area with Notion-style generous padding and readable max-width
- Footer with links slot and copyright
- Full mobile responsiveness
- Pages design tokens integration via #mainstyles reference
- Comprehensive test coverage

---

#### 1.1.6 Routing Configuration

**Priority**: Critical  
**Estimated Time**: 1-2 days  
**Dependencies**: 1.1.5  
**Assigned To**: HWIMDA2

**Frontend Tasks**:

- [-] Define route structure in `app.routes.ts`
  - [ ] Public routes (landing, login, register) (routes array exists but empty)
  - [ ] Protected routes (dashboard, projects, etc.) (routes array exists but empty)
  - [x] Route configuration with path, component (Router configured in app.config.ts)
- [ ] Create route guard service (`auth.guard.ts`)
  - [ ] Check authentication status
  - [ ] Redirect to login if not authenticated
  - [ ] Use `inject()` for dependencies
- [ ] Create 404 not found component (`not-found.component.ts`)
  - [ ] 404 page with navigation link
  - [ ] Responsive design
- [ ] Apply guards to protected routes
- [ ] Test routing behavior
- [ ] Write route guard tests

**Deliverables**:

- Complete routing configuration
- Authentication route guards
- 404 error page

---

#### 1.1.7 HTTP Client Configuration

**Priority**: Critical  
**Estimated Time**: 1-2 days  
**Dependencies**: 1.1.1  
**Assigned To**: HWIMDA2

**Frontend Tasks**:

- [ ] Create request interceptor (`auth.interceptor.ts`)
  - [ ] Add JWT token to request headers
  - [ ] Handle token refresh logic
  - [ ] Use `inject()` for dependencies
- [ ] Create response interceptor (`error.interceptor.ts`)
  - [ ] Handle 401 (unauthorized) responses
  - [ ] Handle 403 (forbidden) responses
  - [ ] Handle 500 (server error) responses
  - [ ] Extract and format error messages
- [-] Register interceptors in `app.config.ts` (HttpClient configured with `withInterceptorsFromDi()`, but no interceptors created yet)
- [ ] Create error handling service (`error-handler.service.ts`)
  - [ ] Centralized error handling
  - [ ] User-friendly error messages
- [ ] Write interceptor tests
- [ ] Test error scenarios

**Deliverables**:

- HTTP interceptors for authentication and error handling
- Error handling service
- Interceptor tests

---

**Note**: Card component exists in `libraries/shared-ui/src/lib/card/card.ts` as an example implementation demonstrating BOM CSS methodology, modern Angular APIs (input(), output(), model(), computed()), and Tailwind `@apply` directives. It serves as a reference for creating other design system components.

#### 1.1.8 Button Component

**Priority**: High  
**Estimated Time**: 1 day  
**Dependencies**: 1.1.1  
**Assigned To**: BATATA2

**Frontend Tasks**:

- [x] Create button component (`button.ts`) in `shared-ui` library
  - [x] Standalone component
  - [x] Use `input()` for variants (primary, secondary, danger, ghost)
  - [x] Use `input()` for sizes (sm, md, lg)
  - [x] Use `input()` for disabled state
  - [x] Use `output()` for click events
- [x] Apply BOM CSS methodology
  - [x] Base `.button` class
  - [x] Modifier classes (`.button--primary`, `.button--secondary`, etc.)
  - [x] Size modifiers (`.button--sm`, `.button--md`, `.button--lg`)
  - [x] Use Tailwind `@apply` directives
  - [x] Use Pages design tokens via CSS custom properties
- [x] Implement loading state (spinner)
- [x] Support icon buttons
- [x] Write component tests
- [x] Export from `shared-ui` public API

**Deliverables**:

- Reusable button component with variants
- Component tests
- Exported from shared-ui library

---

#### 1.1.9 Icon Component

**Priority**: High  
**Estimated Time**: 1 day  
**Dependencies**: 1.1.1  
**Assigned To**: BATATA2  
**Status**: ✅ Complete

**Frontend Tasks**:

- [x] Install lucide-angular package
- [x] Create icon component (`icon.ts`) in `shared-ui` library
  - [x] Standalone component wrapper for Lucide icons
  - [x] Use `input()` for icon name (string type)
  - [x] Use `input()` for size (xs, sm, md, lg, xl, 2xl)
  - [x] Use `input()` for color (string or CSS custom property)
  - [x] Use `input()` for strokeWidth (number)
  - [x] Support dynamic icon loading from Lucide library
- [x] Apply BOM CSS methodology
  - [x] Base `.icon` class
  - [x] Size modifiers (`.icon--xs`, `.icon--sm`, `.icon--md`, `.icon--lg`, `.icon--xl`, `.icon--2xl`)
  - [x] Use Tailwind `@apply` directives
  - [x] Use Pages design tokens for default colors (color inheritance)
- [x] Implement icon registry/selector logic
  - [x] Map icon names to Lucide icon components (kebab-case to PascalCase conversion)
  - [x] Support all common Lucide icons
- [x] Write component tests
- [x] Export from `shared-ui` public API
- [x] Animation support (spin, pulse, bounce) using Tailwind CSS 4 built-in animations

**Deliverables**:

- Reusable icon component using Lucide Angular
- Support for common icons (menu, user, search, settings, etc.)
- Component tests
- Exported from shared-ui library

---

#### 1.1.10 Input Component

**Priority**: High  
**Estimated Time**: 1-2 days  
**Dependencies**: 1.1.1  
**Assigned To**: HWIMDA2  
**Status**: ✅ Complete

**Frontend Tasks**:

- [x] Create input component (`input.ts`) in `shared-ui` library
  - [x] Standalone component
  - [x] Use `input()` for type (text, email, password, textarea, etc.)
  - [x] Use `input()` for placeholder, label, required
  - [x] Use `input()` for disabled, readonly states
  - [x] Use `model()` for two-way binding
  - [x] Use `output()` for focus, blur events
- [x] Apply BOM CSS methodology
  - [x] Base `.input` class
  - [x] Modifier classes (`.input--error`, `.input--disabled`, `.input--readonly`, `.input--textarea`)
  - [x] Use Tailwind `@apply` directives
- [x] Implement error state and error message display
- [x] Support label and helper text
- [x] Support left/right icons and password toggle
- [x] Custom styled number input spinner buttons
- [x] Textarea support with configurable rows
- [x] Write component tests
- [x] Export from `shared-ui` public API

**Deliverables**:

- ✅ Reusable input component with validation states
- ✅ Textarea support
- ✅ Component tests
- ✅ Exported from shared-ui library

---

#### 1.1.11 Modal/Dialog Component

**Priority**: High  
**Estimated Time**: 2-3 days  
**Dependencies**: 1.1.1  
**Assigned To**: BATATA2  
**Status**: ✅ Complete

**Frontend Tasks**:

- [x] Create modal component using Angular CDK Overlay (`modal.ts` service)
  - [x] Modal service with CDK Overlay
  - [x] ModalContainer, ModalHeader, ModalContent, ModalFooter components
  - [x] Size variants (sm, md, lg) via config
  - [x] Closable option via config
  - [x] Implement backdrop/overlay with CDK
- [x] Apply BOM CSS methodology
  - [x] Base `.modal-container` class
  - [x] Size classes for CDK overlay panels (`.lib-modal-panel--sm/md/lg`)
  - [x] Use Tailwind `@apply` directives
- [x] Implement keyboard handling (ESC to close) via CDK Overlay
- [x] Implement backdrop click to close via CDK Overlay
- [x] Support modal content projection (ng-content) via component structure
- [ ] Write component tests (TODO)
- [x] Export from `shared-ui` public API

**Deliverables**:

- Reusable modal/dialog component
- Keyboard and focus management
- Component tests
- Exported from shared-ui library

---

#### 1.1.12 Loading Spinner Component

**Priority**: High  
**Estimated Time**: 0.5-1 day  
**Dependencies**: 1.1.1  
**Assigned To**: HWIMDA2  
**Status**: ✅ Complete

**Frontend Tasks**:

- [x] Create loading spinner component (`spinner.component.ts`) in `shared-ui` library
  - [x] Standalone component (directive-based approach)
  - [x] Use `input()` and `@Input()` for size variants (sm, md, lg)
  - [x] Use `@Input()` for color variants
  - [x] Structural directive `*spinner` for encapsulating content
  - [x] SpinnerContent component with Lucide loader icon
- [x] Apply BOM CSS methodology
  - [x] Base `.spinner` class
  - [x] Size modifiers
  - [x] Use Tailwind `@apply` directives
- [x] Implement CSS animation for spinner (using Lucide icon with spin animation)
- [x] Write component tests
- [x] Export from `shared-ui` public API

**Deliverables**:

- ✅ Reusable loading spinner directive and component
- ✅ Component tests
- ✅ Exported from shared-ui library

---

#### 1.1.13 Toast/Notification Component

**Priority**: Medium  
**Estimated Time**: 2-3 days  
**Dependencies**: 1.1.1  
**Assigned To**: BATATA2  
**Status**: ✅ Complete

**Frontend Tasks**:

- [x] Create toast component (`toast.ts`) in `shared-ui` library
  - [x] Standalone component
  - [x] Use `input()` for type (success, error, warning, info)
  - [x] Use `input()` for message, duration
  - [x] Auto-dismiss after duration
- [x] Create toast service (`toast.service.ts`)
  - [x] Service for programmatic toast display
  - [x] Methods: `show()`, `success()`, `error()`, `warning()`, `info()`
  - [x] Toast queue management with position tracking
- [x] Toast container (handled by Angular CDK Overlay)
  - [x] Multiple toasts support with stacking
  - [x] Position management (top-right, top-left, bottom-right, bottom-left, top-center, bottom-center)
  - [x] Proper spacing and repositioning when toasts close
- [x] Apply BOM CSS methodology
- [x] Implement animations (slide in/out)
- [ ] Write component and service tests
- [x] Export from `shared-ui` public API

**Deliverables**:

- ✅ Reusable toast/notification system
- ✅ Toast service for programmatic usage
- ⏳ Component tests (pending)
- ✅ Exported from shared-ui library

---

#### 1.1.14 Loading and Error State Components

**Priority**: High  
**Estimated Time**: 1-2 days  
**Dependencies**: 1.1.12  
**Assigned To**: HWIMDA2  
**Status**: ✅ Complete

**Frontend Tasks**:

- [x] Create loading state component (`loading-state.component.ts`)
  - [x] Display spinner with optional message
  - [x] Use `input()` for message
  - [x] Reuse spinner component (using Icon component with loader icon)
- [x] Create error state component (`error-state.component.ts`)
  - [x] Display error message with retry button
  - [x] Use `input()` for error message, retry action
  - [x] Use `output()` for retry event
- [x] Create empty state component (`empty-state.component.ts`)
  - [x] Display empty state with optional action
  - [x] Use `input()` for message, action label
  - [x] Use `output()` for action event
- [x] Apply BOM CSS methodology
- [x] Write component tests
- [x] Export from `shared-ui` public API

**Deliverables**:

- ✅ Loading, error, and empty state components
- ✅ Component tests
- ✅ Exported from shared-ui library

---

#### 1.1.15 Landing Page - Hero Section

**Priority**: High  
**Estimated Time**: 1-2 days  
**Dependencies**: 1.1.6, 1.1.8, 1.1.9  
**Assigned To**: BATATA2

**Frontend Tasks**:

- [ ] Create landing page route in `app.routes.ts` (public route)
- [ ] Create landing page component (`landing.component.ts`)
- [ ] Create hero section component (`hero-section.component.ts`)
  - [ ] Headline and subheading
  - [ ] Value proposition text
  - [ ] Primary CTA button (Sign Up) - reuse button component
  - [ ] Secondary CTA button (Learn More)
  - [ ] Hero image/illustration placeholder
- [ ] Apply BOM CSS methodology with Tailwind
- [ ] Ensure mobile responsiveness
- [ ] Write component tests

**Deliverables**:

- Landing page route and hero section
- Responsive design

---

#### 1.1.16 Landing Page - Features Section

**Priority**: High  
**Estimated Time**: 1-2 days  
**Dependencies**: 1.1.15  
**Assigned To**: HWIMDA2

**Frontend Tasks**:

- [ ] Create features section component (`features-section.component.ts`)
  - [ ] Section heading
  - [ ] Feature cards (3-4 key features)
  - [ ] Feature icons/illustrations
  - [ ] Feature titles and descriptions
  - [ ] Reuse card component from shared-ui
- [ ] Apply BOM CSS methodology with Tailwind
- [ ] Ensure mobile responsiveness (grid layout)
- [ ] Write component tests

**Deliverables**:

- Features section component
- Responsive grid layout

---

#### 1.1.17 Landing Page - Footer and Navigation

**Priority**: High  
**Estimated Time**: 1-2 days  
**Dependencies**: 1.1.6  
**Assigned To**: BATATA2

**Frontend Tasks**:

- [ ] Create public navigation component (`public-nav.component.ts`)
  - [ ] Logo/branding
  - [ ] Navigation links (Home, Features, Pricing)
  - [ ] Sign Up button (links to register route)
  - [ ] Log In button (links to login route)
  - [ ] Responsive mobile menu
- [ ] Create footer component (`footer.component.ts`)
  - [ ] Product links section
  - [ ] Legal links (Terms, Privacy Policy - placeholders)
  - [ ] Social media links
  - [ ] Contact information
  - [ ] Copyright notice
- [ ] Apply BOM CSS methodology with Tailwind
- [ ] Ensure mobile responsiveness
- [ ] Write component tests

**Deliverables**:

- Public navigation bar
- Footer component
- Mobile-responsive design

---

#### 1.1.18 Landing Page - SEO and Optimization

**Priority**: Medium  
**Estimated Time**: 1 day  
**Dependencies**: 1.1.15, 1.1.16, 1.1.17  
**Assigned To**: HWIMDA2

**Frontend Tasks**:

- [ ] Add meta tags to landing page
  - [ ] Title tag
  - [ ] Description tag
  - [ ] Keywords tag
- [ ] Add Open Graph tags
  - [ ] og:title, og:description, og:image
  - [ ] og:type, og:url
- [ ] Add structured data (JSON-LD)
  - [ ] Organization schema
  - [ ] Product schema (optional)
- [ ] Ensure semantic HTML structure
- [ ] Add analytics integration (optional)
  - [ ] Google Analytics script
  - [ ] Conversion tracking events

**Deliverables**:

- SEO-optimized landing page
- Structured data
- Analytics integration (optional)

---

## Phase 1.2: Core User & Organization Management (Weeks 3-5)

### Dependencies: 1.1.3, 1.1.4, 1.1.5, 1.1.6, 1.1.7, 1.1.8, 1.1.9, 1.1.10, 1.1.11, 1.1.12, 1.1.13, 1.1.14

**Note**: Tasks in this phase are split into independent backend and frontend tasks that can be worked on in parallel after initial dependencies are met. Backend tasks (1.2.1-1.2.9) can be started once authentication and API infrastructure (1.1.3, 1.1.4) are complete. Frontend tasks (1.2.10-1.2.17) depend on corresponding backend APIs and frontend foundation components.

#### 1.2.1 User Profile API Endpoints

**Priority**: High  
**Estimated Time**: 2-3 days  
**Dependencies**: 1.1.3, 1.1.4  
**Assigned To**: HWIMDA1

**Backend Tasks**:

- [ ] Create user profile endpoint (GET /api/users/me)
  - [ ] Return current user profile data
  - [ ] Include name, email, avatar_url, created_at
  - [ ] Require authentication
- [ ] Create user profile update endpoint (PUT /api/users/me)
  - [ ] Update name field
  - [ ] Validate input (name not empty)
  - [ ] Return updated user data
- [ ] Create email update endpoint (PUT /api/users/me/email)
  - [ ] Validate email format and uniqueness
  - [ ] Send verification email (async)
  - [ ] Require current password for security
- [ ] Create password update endpoint (PUT /api/users/me/password)
  - [ ] Require current password
  - [ ] Validate new password strength
  - [ ] Hash new password
  - [ ] Update password_hash in database
- [ ] Write API tests for profile endpoints
- [ ] Write integration tests

**Deliverables**:

- User profile CRUD endpoints
- Email and password update endpoints
- API tests

---

#### 1.2.2 User Avatar Upload API

**Priority**: Medium  
**Estimated Time**: 2-3 days  
**Dependencies**: 1.2.1, 1.1.4  
**Assigned To**: HWIMDA1

**Backend Tasks**:

- [ ] Create avatar upload endpoint (POST /api/users/me/avatar)
  - [ ] Accept multipart/form-data
  - [ ] Validate file type (image/jpeg, image/png, image/webp)
  - [ ] Validate file size (max 5MB)
  - [ ] Generate unique filename
  - [ ] Save file to storage (local or S3)
  - [ ] Update user.avatar_url in database
- [ ] Implement image processing
  - [ ] Resize image to standard sizes (64x64, 128x128, 256x256)
  - [ ] Optimize image quality
  - [ ] Store multiple sizes for different use cases
- [ ] Create avatar deletion endpoint (DELETE /api/users/me/avatar)
  - [ ] Remove file from storage
  - [ ] Clear avatar_url in database
- [ ] Write API tests for avatar upload
- [ ] Write integration tests with file upload

**Deliverables**:

- Avatar upload endpoint
- Image processing and storage
- API tests

---

#### 1.2.3 User Preferences API

**Priority**: Low  
**Estimated Time**: 1-2 days  
**Dependencies**: 1.2.1  
**Assigned To**: HWIMDA1

**Backend Tasks**:

- [ ] Design user preferences schema (JSON field in users table or separate table)
- [ ] Create get preferences endpoint (GET /api/users/me/preferences)
  - [ ] Return user preferences JSON
  - [ ] Default preferences if none set
- [ ] Create update preferences endpoint (PUT /api/users/me/preferences)
  - [ ] Validate preferences JSON schema
  - [ ] Update preferences in database
  - [ ] Return updated preferences
- [ ] Define default preferences structure
  - [ ] Theme preference (light/dark)
  - [ ] Notification preferences
  - [ ] Language preference
- [ ] Write API tests

**Deliverables**:

- User preferences API endpoints
- Default preferences structure
- API tests

---

#### 1.2.4 User List API

**Priority**: Medium  
**Estimated Time**: 1-2 days  
**Dependencies**: 1.1.3, 1.1.4  
**Assigned To**: HWIMDA1

**Backend Tasks**:

- [ ] Create user list endpoint (GET /api/users)
  - [ ] Filter by organization membership (optional query param)
  - [ ] Search by name or email (optional query param)
  - [ ] Pagination support (page, limit)
  - [ ] Return user id, name, email, avatar_url
- [ ] Implement search functionality
  - [ ] Case-insensitive search on name and email
  - [ ] Use database indexes for performance
- [ ] Implement pagination
  - [ ] Default limit (e.g., 20 users per page)
  - [ ] Return total count, page, limit in response
- [ ] Add permission check (organization members only if filtering by org)
- [ ] Write API tests

**Deliverables**:

- User list endpoint with search and pagination
- API tests

---

#### 1.2.5 User Deactivation API

**Priority**: Low  
**Estimated Time**: 1 day  
**Dependencies**: 1.2.1  
**Assigned To**: HWIMDA1

**Backend Tasks**:

- [ ] Create user deactivation endpoint (POST /api/users/me/deactivate)
  - [ ] Soft delete (set deleted_at timestamp)
  - [ ] Invalidate all user sessions/tokens
  - [ ] Prevent login after deactivation
- [ ] Update authentication logic to check deleted_at
- [ ] Create user reactivation endpoint (admin only, optional)
- [ ] Write API tests

**Deliverables**:

- User deactivation endpoint
- Updated authentication logic
- API tests

---

#### 1.2.6 Organization CRUD API

**Priority**: High  
**Estimated Time**: 3-4 days  
**Dependencies**: 1.1.2, 1.1.4  
**Assigned To**: BATATA1

**Backend Tasks**:

- [ ] Create organization creation endpoint (POST /api/organizations)
  - [ ] Validate organization name (required, min length)
  - [ ] Auto-generate slug from name
  - [ ] Validate slug uniqueness
  - [ ] Create organization record
  - [ ] Add creator as admin member in OrganizationMembers table
  - [ ] Return created organization with member info
- [ ] Create organization retrieval endpoint (GET /api/organizations/:id)
  - [ ] Include organization details (name, slug, description, settings)
  - [ ] Permission check (organization member only)
  - [ ] Include member count
- [ ] Create organization list endpoint (GET /api/organizations)
  - [ ] Filter by current user membership (only show user's orgs)
  - [ ] Pagination support (page, limit)
  - [ ] Return organization id, name, slug, member count
- [ ] Create organization update endpoint (PUT /api/organizations/:id)
  - [ ] Permission check (admin only)
  - [ ] Update name, description fields
  - [ ] Validate name and slug uniqueness if changed
  - [ ] Return updated organization
- [ ] Create organization deletion endpoint (DELETE /api/organizations/:id)
  - [ ] Permission check (admin only)
  - [ ] Soft delete (set deleted_at timestamp)
  - [ ] Cascade delete or archive projects
- [ ] Write API tests for CRUD operations
- [ ] Write integration tests

**Deliverables**:

- Organization CRUD endpoints
- Permission checks
- API tests

---

#### 1.2.7 Organization Members API

**Priority**: High  
**Estimated Time**: 3-4 days  
**Dependencies**: 1.2.6  
**Assigned To**: BATATA1

**Backend Tasks**:

- [ ] Create add member endpoint (POST /api/organizations/:id/members)
  - [ ] Validate user_id exists
  - [ ] Check user is not already a member
  - [ ] Add member with default role (member)
  - [ ] Permission check (admin only)
  - [ ] Return added member info
- [ ] Create list members endpoint (GET /api/organizations/:id/members)
  - [ ] Return members with user details (name, email, avatar_url)
  - [ ] Include role for each member
  - [ ] Pagination support
  - [ ] Permission check (organization member)
- [ ] Create update member role endpoint (PUT /api/organizations/:id/members/:userId)
  - [ ] Update member role (member, admin)
  - [ ] Permission check (admin only)
  - [ ] Prevent removing last admin
  - [ ] Return updated member info
- [ ] Create remove member endpoint (DELETE /api/organizations/:id/members/:userId)
  - [ ] Permission check (admin only, or user removing themselves)
  - [ ] Prevent removing last admin
  - [ ] Remove member from organization
- [ ] Write API tests for member management
- [ ] Write integration tests

**Deliverables**:

- Organization member management endpoints
- Role-based permissions
- API tests

---

#### 1.2.8 Organization Invitation System

**Priority**: Medium  
**Estimated Time**: 4-5 days  
**Dependencies**: 1.2.7  
**Assigned To**: BATATA1

**Backend Tasks**:

- [ ] Create invitation model/table
  - [ ] Fields: id, organization_id, email, token, role, invited_by, expires_at, accepted_at, created_at
  - [ ] Migration for invitations table
- [ ] Create send invitation endpoint (POST /api/organizations/:id/members/invite)
  - [ ] Validate email format
  - [ ] Check user is not already a member
  - [ ] Check invitation not already sent (pending)
  - [ ] Generate secure invitation token
  - [ ] Create invitation record (expires in 7 days)
  - [ ] Send invitation email (async) with invitation link
  - [ ] Permission check (admin only)
  - [ ] Return invitation info
- [ ] Create accept invitation endpoint (POST /api/organizations/invitations/:token/accept)
  - [ ] Validate token exists and not expired
  - [ ] Check user email matches invitation email (if authenticated) or allow registration
  - [ ] Add user to organization with specified role
  - [ ] Mark invitation as accepted
  - [ ] Send welcome notification (async)
  - [ ] Return organization info
- [ ] Create list invitations endpoint (GET /api/organizations/:id/invitations)
  - [ ] Return pending invitations
  - [ ] Permission check (admin only)
- [ ] Create cancel invitation endpoint (DELETE /api/organizations/invitations/:id)
  - [ ] Cancel pending invitation
  - [ ] Permission check (admin only)
- [ ] Implement invitation email template
- [ ] Write API tests for invitation system
- [ ] Write integration tests

**Deliverables**:

- Organization invitation system
- Invitation email handling
- API tests

---

#### 1.2.9 Organization Settings API

**Priority**: Low  
**Estimated Time**: 1-2 days  
**Dependencies**: 1.2.6  
**Assigned To**: BATATA1

**Backend Tasks**:

- [ ] Design organization settings schema (JSON field in organizations table)
- [ ] Create get settings endpoint (GET /api/organizations/:id/settings)
  - [ ] Return organization settings JSON
  - [ ] Include default settings if none set
  - [ ] Permission check (organization member)
- [ ] Create update settings endpoint (PUT /api/organizations/:id/settings)
  - [ ] Validate settings JSON schema
  - [ ] Update settings in database
  - [ ] Permission check (admin only)
  - [ ] Return updated settings
- [ ] Define default settings structure
  - [ ] Feature flags
  - [ ] Notification preferences
  - [ ] Custom branding (optional)
- [ ] Write API tests

**Deliverables**:

- Organization settings API endpoints
- Default settings structure
- API tests

---

#### 1.2.10 User Profile Page

**Priority**: High  
**Estimated Time**: 2-3 days  
**Dependencies**: 1.2.1, 1.1.5, 1.1.8, 1.1.9  
**Assigned To**: BATATA2

**Frontend Tasks**:

- [ ] Create user profile route (`/profile`)
- [ ] Create profile page component (`profile.component.ts`)
  - [ ] Display current user information
  - [ ] Edit name form (use input component)
  - [ ] Email display (read-only, link to change email)
  - [ ] Save button (use button component)
- [ ] Create password change form component (`change-password.component.ts`)
  - [ ] Current password input
  - [ ] New password input with strength indicator
  - [ ] Confirm password input
  - [ ] Form validation
  - [ ] Submit handler
- [ ] Create avatar upload component (`avatar-upload.component.ts`)
  - [ ] Display current avatar
  - [ ] File input for image upload
  - [ ] Image preview before upload
  - [ ] Upload progress indicator
  - [ ] Remove avatar option
- [ ] Integrate with user profile API endpoints
- [ ] Add form validation
- [ ] Implement loading and error states
- [ ] Write component tests

**Deliverables**:

- User profile page with edit functionality
- Password change form
- Avatar upload component

---

#### 1.2.11 Organization Creation Modal

**Priority**: High  
**Estimated Time**: 1-2 days  
**Dependencies**: 1.2.6, 1.1.5, 1.1.11, 1.1.9  
**Assigned To**: HWIMDA2

**Frontend Tasks**:

- [ ] Create organization creation modal component (`create-organization-modal.component.ts`)
  - [ ] Organization name input (use input component)
  - [ ] Slug input (auto-generated from name, editable)
  - [ ] Slug preview/validation
  - [ ] Description textarea (optional)
  - [ ] Create and Cancel buttons (use button component)
- [ ] Integrate with organization creation API
- [ ] Add form validation
  - [ ] Name required, min length
  - [ ] Slug format validation (lowercase, hyphens only)
  - [ ] Slug uniqueness check (async validation)
- [ ] Implement loading and error states
- [ ] Show success toast and redirect after creation
- [ ] Write component tests

**Deliverables**:

- Organization creation modal
- Form validation
- Component tests

---

#### 1.2.12 Organization List Page

**Priority**: High  
**Estimated Time**: 1-2 days  
**Dependencies**: 1.2.6, 1.1.5, 1.1.8  
**Assigned To**: BATATA2

**Frontend Tasks**:

- [ ] Create organization list route (`/organizations`)
- [ ] Create organization list page component (`organizations.component.ts`)
  - [ ] Display list of user's organizations
  - [ ] Organization cards (use card component)
  - [ ] Organization name, description, member count
  - [ ] "Create Organization" button (opens modal from 1.2.11)
  - [ ] Click organization to navigate to organization detail
- [ ] Create organization card component (`organization-card.component.ts`)
  - [ ] Organization name and description
  - [ ] Member count
  - [ ] Actions menu (settings, leave)
- [ ] Integrate with organization list API
- [ ] Implement loading and error states (use loading/error components)
- [ ] Implement empty state (no organizations)
- [ ] Write component tests

**Deliverables**:

- Organization list page
- Organization card components
- Component tests

---

#### 1.2.13 Organization Settings Page

**Priority**: High  
**Estimated Time**: 2-3 days  
**Dependencies**: 1.2.6, 1.1.5, 1.1.8, 1.1.9  
**Assigned To**: HWIMDA2

**Frontend Tasks**:

- [ ] Create organization settings route (`/organizations/:id/settings`)
- [ ] Create organization settings page component (`organization-settings.component.ts`)
  - [ ] Organization details form (name, description)
  - [ ] Save button
  - [ ] Delete organization button (with confirmation)
- [ ] Integrate with organization update API
- [ ] Integrate with organization delete API
- [ ] Add form validation
- [ ] Implement loading and error states
- [ ] Show confirmation modal before deletion (use modal component)
- [ ] Write component tests

**Deliverables**:

- Organization settings page
- Organization details update
- Delete organization functionality

---

#### 1.2.14 Organization Member Management

**Priority**: High  
**Estimated Time**: 2-3 days  
**Dependencies**: 1.2.7, 1.1.5, 1.1.8, 1.1.9, 1.1.11  
**Assigned To**: BATATA2

**Frontend Tasks**:

- [ ] Create member list component (`member-list.component.ts`)
  - [ ] Display list of organization members
  - [ ] Member cards with name, email, avatar, role
  - [ ] Role badge/display
  - [ ] Actions menu for each member (change role, remove)
- [ ] Create add member modal component (`add-member-modal.component.ts`)
  - [ ] User search/select input (integrate with user list API)
  - [ ] Role selection (member, admin)
  - [ ] Add button
- [ ] Create change role modal component (`change-role-modal.component.ts`)
  - [ ] Current role display
  - [ ] Role selection dropdown
  - [ ] Save button
- [ ] Integrate with member management APIs
  - [ ] List members
  - [ ] Add member
  - [ ] Update role
  - [ ] Remove member
- [ ] Add permission checks (admin only actions)
- [ ] Implement loading and error states
- [ ] Write component tests

**Deliverables**:

- Member list component
- Add/remove member functionality
- Role management UI

---

#### 1.2.15 Organization Invitation UI

**Priority**: Medium  
**Estimated Time**: 2-3 days  
**Dependencies**: 1.2.8, 1.1.5, 1.1.8, 1.1.9, 1.1.11  
**Assigned To**: HWIMDA2

**Frontend Tasks**:

- [ ] Create send invitation modal component (`invite-member-modal.component.ts`)
  - [ ] Email input (use input component)
  - [ ] Role selection (member, admin)
  - [ ] Send invitation button
  - [ ] Form validation (email format)
- [ ] Create pending invitations list component (`pending-invitations.component.ts`)
  - [ ] Display list of pending invitations
  - [ ] Email, role, invited by, expiration date
  - [ ] Cancel invitation button
- [ ] Integrate with invitation APIs
  - [ ] Send invitation
  - [ ] List pending invitations
  - [ ] Cancel invitation
- [ ] Create invitation acceptance page (`/invitations/:token`)
  - [ ] Display invitation details
  - [ ] Accept button (if logged in)
  - [ ] Sign up link (if not logged in)
- [ ] Integrate with accept invitation API
- [ ] Implement loading and error states
- [ ] Write component tests

**Deliverables**:

- Send invitation modal
- Pending invitations list
- Invitation acceptance page

---

#### 1.2.16 Organization Selector Component

**Priority**: High  
**Estimated Time**: 1-2 days  
**Dependencies**: 1.2.6, 1.1.5  
**Assigned To**: BATATA2

**Frontend Tasks**:

- [ ] Create organization selector component (`organization-selector.component.ts`)
  - [ ] Dropdown/select component showing current organization
  - [ ] List of user's organizations
  - [ ] Switch organization functionality
- [ ] Create organization context/service (`organization.service.ts`)
  - [ ] Current organization state (signal)
  - [ ] Switch organization method
  - [ ] Load user's organizations
  - [ ] Persist selected organization (localStorage)
- [ ] Integrate with organization list API
- [ ] Add organization selector to base layout header
- [ ] Implement loading state
- [ ] Write component and service tests

**Deliverables**:

- Organization selector component
- Organization context service
- Integration with base layout

---

#### 1.2.17 User Dropdown Menu

**Priority**: High  
**Estimated Time**: 1 day  
**Dependencies**: 1.1.5, 1.1.8  
**Assigned To**: HWIMDA2

**Frontend Tasks**:

- [ ] Create user dropdown menu component (`user-menu.component.ts`)
  - [ ] User avatar display
  - [ ] User name display
  - [ ] Dropdown menu with:
    - [ ] Profile link
    - [ ] Settings link (placeholder)
    - [ ] Logout button
- [ ] Add logout functionality
  - [ ] Clear authentication tokens
  - [ ] Redirect to login page
- [ ] Integrate with authentication service
- [ ] Apply BOM CSS methodology
- [ ] Ensure mobile responsiveness
- [ ] Write component tests

**Deliverables**:

- User dropdown menu component
- Logout functionality
- Component tests

---

## Phase 1.3: Core Project Management Features (Weeks 5-10)

### Dependencies: 1.2.2, 1.1.4, 1.1.5

#### 1.3.1 Project Management Backend - Projects

**Priority**: Critical  
**Estimated Time**: 7-10 days  
**Dependencies**: 1.2.2, 1.1.4  
**Assigned To**: HWIMDA1

**Tasks**:

- [ ] Create project creation endpoint (POST /api/projects)
  - [ ] Validate project name and key uniqueness within organization
  - [ ] Auto-generate project key if not provided
  - [ ] Create project record
  - [ ] Add creator as project admin
- [ ] Create project retrieval endpoint (GET /api/projects/:id)
  - [ ] Include project members
  - [ ] Include issue counts
- [ ] Create project list endpoint (GET /api/projects)
  - [ ] Filter by organization
  - [ ] Search by name/key
  - [ ] Pagination support
- [ ] Create project update endpoint (PUT /api/projects/:id)
  - [ ] Permission check (project member)
  - [ ] Update name, description
- [ ] Create project deletion endpoint (DELETE /api/projects/:id)
  - [ ] Permission check (project admin)
  - [ ] Cascade delete or archive
- [ ] Create project members management endpoints
  - [ ] Add member (POST /api/projects/:id/members)
  - [ ] List members (GET /api/projects/:id/members)
  - [ ] Remove member (DELETE /api/projects/:id/members/:userId)
- [ ] Implement project-level permissions
- [ ] Write project API tests

**Deliverables**:

- Project CRUD APIs
- Project member management

---

#### 1.3.2 Project Management Backend - Issues (Part 1: Core CRUD)

**Priority**: Critical  
**Estimated Time**: 10-14 days  
**Dependencies**: 1.3.1, 1.1.4  
**Assigned To**: BATATA1

**Tasks**:

- [ ] Create issue creation endpoint (POST /api/issues)
  - [ ] Validate required fields (title, project_id, type)
  - [ ] Auto-assign issue key (PROJ-123 format)
  - [ ] Set default status (e.g., "To Do")
  - [ ] Create issue record
  - [ ] Generate activity log entry
  - [ ] Send notifications to project members (async)
- [ ] Create issue retrieval endpoint (GET /api/issues/:id)
  - [ ] Include assignee, reporter, project details
  - [ ] Include comments count
  - [ ] Include attachments count
  - [ ] Permission check (project member)
- [ ] Create issue list endpoint (GET /api/issues)
  - [ ] Filter by project, assignee, reporter, status, type
  - [ ] Search by title/description
  - [ ] Sort by created_at, updated_at, priority
  - [ ] Pagination support
- [ ] Create issue update endpoint (PUT /api/issues/:id)
  - [ ] Permission check (project member)
  - [ ] Update title, description, status, priority, assignee, due_date
  - [ ] Generate activity log entries for changes
  - [ ] Send notifications on status/assignee changes (async)
- [ ] Create issue deletion endpoint (DELETE /api/issues/:id)
  - [ ] Permission check (project member or admin)
  - [ ] Soft delete with confirmation
- [ ] Implement issue types (Task, Bug, Story)
  - [ ] Default issue types per project
  - [ ] Type-specific validation
- [ ] Implement issue statuses (To Do, In Progress, Done)
  - [ ] Default statuses per project
  - [ ] Status workflow validation
- [ ] Implement issue priorities (Low, Medium, High, Critical)
- [ ] Create activity log system for issue changes
  - [ ] Activity log table/migration
  - [ ] Log creation on issue changes
  - [ ] Activity log retrieval endpoint (GET /api/issues/:id/activities)
- [ ] Write issue API tests

**Deliverables**:

- Issue CRUD APIs
- Activity logging system

---

#### 1.3.3 Project Management Backend - Issues (Part 2: Comments)

**Priority**: High  
**Estimated Time**: 5-7 days  
**Dependencies**: 1.3.2  
**Assigned To**: HWIMDA1

**Tasks**:

- [ ] Create comment creation endpoint (POST /api/issues/:id/comments)
  - [ ] Validate content (not empty)
  - [ ] Create comment record
  - [ ] Link to issue
  - [ ] Send notifications to issue watchers (async)
- [ ] Create comment retrieval endpoint (GET /api/comments/:id)
- [ ] Create comment list endpoint (GET /api/issues/:id/comments)
  - [ ] Order by created_at
  - [ ] Include user details
- [ ] Create comment update endpoint (PUT /api/comments/:id)
  - [ ] Permission check (comment author only)
  - [ ] Update content
  - [ ] Mark as edited
- [ ] Create comment deletion endpoint (DELETE /api/comments/:id)
  - [ ] Permission check (comment author or project admin)
  - [ ] Soft delete
- [ ] Implement @mentions in comments
  - [ ] Parse @mentions from content
  - [ ] Create mention records
  - [ ] Send notifications to mentioned users (async)
- [ ] Implement comment reactions (optional for MVP, can defer)
- [ ] Write comment API tests

**Deliverables**:

- Comment CRUD APIs
- @mention functionality

---

#### 1.3.4 Project Management Backend - File Attachments

**Priority**: Medium  
**Estimated Time**: 7-10 days  
**Dependencies**: 1.3.2, 1.1.4  
**Assigned To**: BATATA1

**Tasks**:

- [ ] Set up file storage (S3 or local filesystem)
- [ ] Create file upload endpoint (POST /api/attachments)
  - [ ] Validate file type (whitelist)
  - [ ] Validate file size (max 10MB for MVP)
  - [ ] Generate unique filename
  - [ ] Upload to storage
  - [ ] Create attachment record
  - [ ] Return attachment metadata
- [ ] Create file download endpoint (GET /api/attachments/:id/download)
  - [ ] Permission check
  - [ ] Stream file from storage
  - [ ] Set proper content-type headers
- [ ] Create attachment list endpoint (GET /api/issues/:id/attachments)
- [ ] Create attachment deletion endpoint (DELETE /api/attachments/:id)
  - [ ] Permission check
  - [ ] Delete from storage
  - [ ] Delete database record
- [ ] Implement image preview/thumbnail generation (for images)
- [ ] Add virus scanning (optional, can use cloud service)
- [ ] Write attachment API tests

**Deliverables**:

- File upload/download system
- Attachment management APIs

---

#### 1.3.5 Project Management Frontend - Projects

**Priority**: Critical  
**Estimated Time**: 7-10 days  
**Dependencies**: 1.3.1, 1.1.5  
**Assigned To**: HWIMDA2

**Tasks**:

- [ ] Create project list page
  - [ ] Display projects in grid/list view
  - [ ] Project card component
  - [ ] Create project button/modal
  - [ ] Search/filter projects
- [ ] Create project detail page
  - [ ] Project header with name, description
  - [ ] Project tabs (Issues, Settings, Members)
  - [ ] Project settings tab
  - [ ] Project members tab
- [ ] Create project creation modal/form
  - [ ] Name input
  - [ ] Key input (with auto-generation)
  - [ ] Description textarea
- [ ] Create project settings page
  - [ ] Edit project details
  - [ ] Delete project (with confirmation)
- [ ] Create project member management UI
  - [ ] Member list
  - [ ] Add member dropdown/search
  - [ ] Remove member functionality
- [ ] Implement project context/provider
- [ ] Add loading states and error handling

**Deliverables**:

- Project management UI
- Project creation and settings

---

#### 1.3.6 Project Management Frontend - Issues (Part 1: List & Detail)

**Priority**: Critical  
**Estimated Time**: 10-14 days  
**Dependencies**: 1.3.2, 1.1.5  
**Assigned To**: BATATA2

**Tasks**:

- [ ] Create issue list page
  - [ ] Issue table/list view
  - [ ] Issue card component
  - [ ] Column headers (Key, Title, Type, Status, Assignee, Priority, Created)
  - [ ] Sorting functionality
  - [ ] Basic filtering UI (status, assignee, type)
  - [ ] Pagination controls
  - [ ] Create issue button
- [ ] Create issue detail page
  - [ ] Issue header (key, title, status badge)
  - [ ] Issue metadata sidebar (Type, Priority, Assignee, Reporter, Created date, Due date)
  - [ ] Issue description section
  - [ ] Comments section
  - [ ] Attachments section
  - [ ] Activity log section
- [ ] Create issue creation modal/form
  - [ ] Project selector
  - [ ] Issue type selector
  - [ ] Title input
  - [ ] Description textarea (rich text or markdown)
  - [ ] Priority selector
  - [ ] Assignee selector (optional)
  - [ ] Due date picker (optional)
- [ ] Create issue edit modal/form
  - [ ] Edit title, description
  - [ ] Change status dropdown
  - [ ] Change assignee dropdown
  - [ ] Change priority dropdown
  - [ ] Update due date
- [ ] Create issue type badges (Task, Bug, Story)
- [ ] Create status badges (To Do, In Progress, Done)
- [ ] Create priority indicators (Low, Medium, High, Critical)
- [ ] Implement issue search functionality
- [ ] Add loading states and error handling
- [ ] Implement optimistic updates for better UX

**Deliverables**:

- Issue list UI
- Issue detail UI
- Issue creation/editing forms

---

#### 1.3.7 Project Management Frontend - Comments & Attachments

**Priority**: High  
**Estimated Time**: 7-10 days  
**Dependencies**: 1.3.3, 1.3.4, 1.3.6  
**Assigned To**: HWIMDA2

**Tasks**:

- [ ] Create comment component
  - [ ] Display comment author, timestamp
  - [ ] Display comment content (with markdown/rich text)
  - [ ] Edit comment functionality (inline)
  - [ ] Delete comment functionality
  - [ ] Show edited indicator
- [ ] Create comment input component
  - [ ] Rich text editor or markdown editor
  - [ ] @mention autocomplete (user picker)
  - [ ] Submit button
  - [ ] Preview mode (optional)
- [ ] Create comment list component
  - [ ] Display comments in chronological order
  - [ ] Threaded comments (optional, can be Phase 2)
- [ ] Create attachment list component
  - [ ] Display attachment cards with file name, size, uploader
  - [ ] Download button
  - [ ] Delete button (with permission check)
  - [ ] Image preview thumbnails
- [ ] Create file upload component
  - [ ] Drag and drop zone
  - [ ] File picker button
  - [ ] Upload progress indicator
  - [ ] Multiple file upload support
  - [ ] File type validation
  - [ ] File size validation
- [ ] Implement file preview modal (for images, PDFs)
- [ ] Add loading states and error handling

**Deliverables**:

- Comment UI components
- File attachment UI components

---

#### 1.3.8 Project Management Frontend - Kanban Board

**Priority**: Critical  
**Estimated Time**: 10-14 days  
**Dependencies**: 1.3.6, 1.1.5  
**Assigned To**: BATATA2

**Tasks**:

- [ ] Create Kanban board component
  - [ ] Board layout (columns for statuses)
  - [ ] Column headers (status name, issue count)
  - [ ] Issue cards in columns
- [ ] Implement drag and drop functionality
  - [ ] Drag issue cards between columns
  - [ ] Update issue status on drop
  - [ ] Visual feedback during drag
  - [ ] Optimistic updates
- [ ] Create issue card component for board
  - [ ] Issue key and title
  - [ ] Issue type badge
  - [ ] Priority indicator
  - [ ] Assignee avatar
  - [ ] Due date indicator (if overdue)
- [ ] Implement board filtering
  - [ ] Filter by assignee
  - [ ] Filter by issue type
  - [ ] Filter by priority
- [ ] Create board settings (optional for MVP)
  - [ ] Show/hide columns
  - [ ] Custom column order
- [ ] Add loading states and error handling
- [ ] Implement board persistence (save column widths, etc.)

**Deliverables**:

- Functional Kanban board
- Drag and drop issue management

---

## Phase 1.4: Core Documentation Features (Weeks 10-14)

### Dependencies: 1.2.2, 1.1.4, 1.1.5

#### 1.4.1 Documentation Backend - Spaces

**Priority**: High  
**Estimated Time**: 5-7 days  
**Dependencies**: 1.2.2, 1.1.4  
**Assigned To**: HWIMDA1

**Tasks**:

- [ ] Create space creation endpoint (POST /api/spaces)
  - [ ] Validate space name and key uniqueness within organization
  - [ ] Create space record
  - [ ] Set default permissions
- [ ] Create space retrieval endpoint (GET /api/spaces/:id)
  - [ ] Include page count
  - [ ] Include recent pages
- [ ] Create space list endpoint (GET /api/spaces)
  - [ ] Filter by organization
  - [ ] Search by name/key
  - [ ] Pagination support
- [ ] Create space update endpoint (PUT /api/spaces/:id)
  - [ ] Permission check (space admin)
  - [ ] Update name, description
- [ ] Create space deletion endpoint (DELETE /api/spaces/:id)
  - [ ] Permission check (space admin)
  - [ ] Cascade delete or archive pages
- [ ] Implement space-level permissions
- [ ] Write space API tests

**Deliverables**:

- Space CRUD APIs
- Space permissions

---

#### 1.4.2 Documentation Backend - Pages (Part 1: Core CRUD)

**Priority**: Critical  
**Estimated Time**: 10-14 days  
**Dependencies**: 1.4.1, 1.1.4  
**Assigned To**: BATATA1

**Tasks**:

- [ ] Create page creation endpoint (POST /api/pages)
  - [ ] Validate required fields (title, space_id, content)
  - [ ] Set parent page (for hierarchy)
  - [ ] Create page record
  - [ ] Generate page slug
  - [ ] Generate activity log entry
- [ ] Create page retrieval endpoint (GET /api/pages/:id)
  - [ ] Include author, editor details
  - [ ] Include parent/children pages
  - [ ] Include comment count
  - [ ] Permission check (space member)
- [ ] Create page list endpoint (GET /api/pages)
  - [ ] Filter by space, parent
  - [ ] Search by title/content
  - [ ] Pagination support
  - [ ] Tree structure support (for hierarchy)
- [ ] Create page update endpoint (PUT /api/pages/:id)
  - [ ] Permission check (space member)
  - [ ] Update title, content, parent
  - [ ] Create new version (for version history - can be Phase 2)
  - [ ] Generate activity log entry
- [ ] Create page deletion endpoint (DELETE /api/pages/:id)
  - [ ] Permission check (page author or space admin)
  - [ ] Soft delete or hard delete
  - [ ] Handle children pages (move or delete)
- [ ] Implement page hierarchy
  - [ ] Parent-child relationships
  - [ ] Tree traversal utilities
  - [ ] Breadcrumb generation
- [ ] Create page tree endpoint (GET /api/spaces/:id/pages/tree)
  - [ ] Return nested page structure
  - [ ] Optimize for tree rendering
- [ ] Write page API tests

**Deliverables**:

- Page CRUD APIs
- Page hierarchy system

---

#### 1.4.3 Documentation Backend - Pages (Part 2: Comments)

**Priority**: High  
**Estimated Time**: 3-5 days  
**Dependencies**: 1.4.2  
**Assigned To**: HWIMDA1

**Tasks**:

- [ ] Create page comment creation endpoint (POST /api/pages/:id/comments)
  - [ ] Similar to issue comments
  - [ ] Link to page instead of issue
- [ ] Create page comment list endpoint (GET /api/pages/:id/comments)
- [ ] Create page comment update endpoint (PUT /api/comments/:id)
  - [ ] Reuse issue comment logic
- [ ] Create page comment deletion endpoint (DELETE /api/comments/:id)
  - [ ] Reuse issue comment logic
- [ ] Implement @mentions in page comments
- [ ] Write page comment API tests

**Deliverables**:

- Page comment APIs

---

#### 1.4.4 Documentation Backend - Rich Text & Templates

**Priority**: Medium  
**Estimated Time**: 5-7 days  
**Dependencies**: 1.4.2  
**Assigned To**: BATATA1

**Tasks**:

- [ ] Set up rich text storage format (HTML, Markdown, or JSON)
- [ ] Create content sanitization utilities (XSS prevention)
- [ ] Implement markdown to HTML conversion (if using markdown)
- [ ] Create page template system
  - [ ] Template table/migration
  - [ ] Template CRUD endpoints
  - [ ] Default templates (Meeting Notes, Requirements, etc.)
- [ ] Create template creation endpoint (POST /api/templates)
- [ ] Create template list endpoint (GET /api/templates)
- [ ] Implement template variables/placeholders (optional)
- [ ] Write template API tests

**Deliverables**:

- Rich text content handling
- Page template system

---

#### 1.4.5 Documentation Frontend - Spaces

**Priority**: High  
**Estimated Time**: 5-7 days  
**Dependencies**: 1.4.1, 1.1.5  
**Assigned To**: HWIMDA2

**Tasks**:

- [ ] Create space list page
  - [ ] Display spaces in grid/list view
  - [ ] Space card component
  - [ ] Create space button/modal
  - [ ] Search/filter spaces
- [ ] Create space detail page
  - [ ] Space header
  - [ ] Space navigation (pages tree)
  - [ ] Page list view
- [ ] Create space creation modal/form
- [ ] Create space settings page
- [ ] Add loading states and error handling

**Deliverables**:

- Space management UI

---

#### 1.4.6 Documentation Frontend - Page Editor

**Priority**: Critical  
**Estimated Time**: 10-14 days  
**Dependencies**: 1.4.2, 1.4.4, 1.1.5  
**Assigned To**: BATATA2

**Tasks**:

- [ ] Choose and integrate rich text editor (Tiptap, Slate, Draft.js, or similar)
- [ ] Create page editor component
  - [ ] Title input
  - [ ] Rich text editor toolbar
  - [ ] Editor content area
  - [ ] Formatting options (bold, italic, headings, lists, links, etc.)
- [ ] Implement markdown support (optional)
  - [ ] Markdown syntax highlighting
  - [ ] Markdown preview
  - [ ] Markdown shortcuts
- [ ] Create page view/display component
  - [ ] Render rich text content
  - [ ] Display page metadata (author, last updated)
  - [ ] Display breadcrumbs
- [ ] Create page creation page
  - [ ] Space selector
  - [ ] Parent page selector (for hierarchy)
  - [ ] Template selector (if using templates)
  - [ ] Page editor
  - [ ] Save/publish button
- [ ] Create page edit page
  - [ ] Load existing page content
  - [ ] Edit mode toggle
  - [ ] Auto-save draft (optional for MVP)
  - [ ] Save changes button
- [ ] Create page detail/view page
  - [ ] Display page content
  - [ ] Edit button (with permission check)
  - [ ] Page actions menu
- [ ] Implement page hierarchy UI
  - [ ] Page tree sidebar
  - [ ] Parent page selector
  - [ ] Breadcrumb navigation
- [ ] Add loading states and error handling

**Deliverables**:

- Rich text page editor
- Page creation and editing UI

---

#### 1.4.7 Documentation Frontend - Page Comments

**Priority**: High  
**Estimated Time**: 3-5 days  
**Dependencies**: 1.4.3, 1.4.6  
**Assigned To**: HWIMDA2

**Tasks**:

- [ ] Reuse comment components from issue comments (1.3.7)
  - [ ] Adapt for page context
  - [ ] Display comments on page detail view
- [ ] Add comment section to page view
- [ ] Implement inline commenting (optional, can be Phase 2)
- [ ] Add loading states and error handling

**Deliverables**:

- Page comments UI

---

## Phase 1.5: Search & Basic Features (Weeks 14-16)

### Dependencies: 1.3.2, 1.4.2

#### 1.5.1 Basic Search Backend

**Priority**: Medium  
**Estimated Time**: 7-10 days  
**Dependencies**: 1.3.2, 1.4.2, 1.1.4  
**Assigned To**: HWIMDA1

**Tasks**:

- [ ] Set up search solution (PostgreSQL full-text search or basic Elasticsearch)
- [ ] Create search indexing utilities
  - [ ] Index issues (title, description)
  - [ ] Index pages (title, content)
- [ ] Create unified search endpoint (GET /api/search)
  - [ ] Search across issues and pages
  - [ ] Query parameter for search term
  - [ ] Filter by entity type (issues, pages, all)
  - [ ] Filter by project/space
  - [ ] Pagination support
- [ ] Create issue-specific search endpoint (GET /api/issues/search)
  - [ ] Advanced filtering (status, assignee, type, etc.)
- [ ] Create page-specific search endpoint (GET /api/pages/search)
  - [ ] Filter by space
- [ ] Implement search result ranking/scoring
- [ ] Add search result highlighting (optional)
- [ ] Write search API tests

**Deliverables**:

- Basic search functionality
- Unified search API

---

#### 1.5.2 Search Frontend

**Priority**: Medium  
**Estimated Time**: 5-7 days  
**Dependencies**: 1.5.1, 1.1.5  
**Assigned To**: BATATA2

**Tasks**:

- [ ] Create search bar component (in header)
  - [ ] Search input with icon
  - [ ] Keyboard shortcut (Cmd/Ctrl+K)
- [ ] Create search results page
  - [ ] Display results grouped by type (Issues, Pages)
  - [ ] Result cards with preview
  - [ ] Highlight search terms
  - [ ] Pagination
- [ ] Implement search autocomplete/suggestions (optional)
- [ ] Add recent searches (optional)
- [ ] Add loading states and error handling

**Deliverables**:

- Search UI
- Search results page

---

## Phase 1.6: Notifications System (Weeks 16-18)

### Dependencies: 1.3.2, 1.4.2

#### 1.6.1 Notifications Backend

**Priority**: High  
**Estimated Time**: 7-10 days  
**Dependencies**: 1.3.2, 1.4.2, 1.1.4  
**Assigned To**: BATATA1

**Tasks**:

- [ ] Design notification system architecture
- [ ] Create notification types (issue_assigned, issue_mentioned, comment_added, etc.)
- [ ] Create notification creation utilities
  - [ ] Issue assignment notifications
  - [ ] Comment notifications
  - [ ] @mention notifications
  - [ ] Status change notifications
- [ ] Create notification list endpoint (GET /api/notifications)
  - [ ] Filter by read/unread
  - [ ] Pagination support
  - [ ] Sort by created_at
- [ ] Create notification mark as read endpoint (PUT /api/notifications/:id/read)
- [ ] Create mark all as read endpoint (PUT /api/notifications/read-all)
- [ ] Create notification count endpoint (GET /api/notifications/unread-count)
- [ ] Implement email notification sending (async queue)
  - [ ] Set up email service (SendGrid, AWS SES, etc.)
  - [ ] Create email templates
  - [ ] Send email on notification creation
  - [ ] User email preferences
- [ ] Set up background job queue (Bull, Celery, etc.)
- [ ] Write notification API tests

**Deliverables**:

- Notification system
- Email notifications

---

#### 1.6.2 Notifications Frontend

**Priority**: High  
**Estimated Time**: 5-7 days  
**Dependencies**: 1.6.1, 1.1.5  
**Assigned To**: HWIMDA2

**Tasks**:

- [ ] Create notification bell icon component (in header)
  - [ ] Unread count badge
  - [ ] Click to open dropdown
- [ ] Create notification dropdown component
  - [ ] List recent notifications
  - [ ] Group by date
  - [ ] Mark as read on click
  - [ ] Link to related issue/page
- [ ] Create notifications page
  - [ ] Full notification list
  - [ ] Filter by read/unread
  - [ ] Mark all as read button
- [ ] Implement real-time notifications (WebSocket - optional for MVP, can use polling)
  - [ ] WebSocket connection setup
  - [ ] Receive new notifications in real-time
  - [ ] Update notification count
- [ ] Create email notification preferences page
  - [ ] Toggle notification types
  - [ ] Save preferences
- [ ] Add loading states and error handling

**Deliverables**:

- Notification UI
- Real-time notification updates (or polling)

---

## Phase 1.7: API & Basic Integrations (Weeks 18-20)

### Dependencies: 1.3.2, 1.4.2

#### 1.7.1 REST API Documentation & Authentication

**Priority**: Medium  
**Estimated Time**: 5-7 days  
**Dependencies**: 1.1.4, 1.1.3  
**Assigned To**: HWIMDA1

**Tasks**:

- [ ] Set up API authentication for external access
  - [ ] API key generation
  - [ ] API key storage
  - [ ] API key authentication middleware
- [ ] Create API key management endpoints
  - [ ] Generate API key (POST /api/api-keys)
  - [ ] List API keys (GET /api/api-keys)
  - [ ] Revoke API key (DELETE /api/api-keys/:id)
- [ ] Complete OpenAPI/Swagger documentation
  - [ ] Document all endpoints
  - [ ] Add request/response examples
  - [ ] Add authentication documentation
- [ ] Create API rate limiting (per API key)
- [ ] Write API usage documentation

**Deliverables**:

- API authentication system
- Complete API documentation

---

#### 1.7.2 Basic Integrations - Slack

**Priority**: Medium  
**Estimated Time**: 7-10 days  
**Dependencies**: 1.7.1, 1.3.2  
**Assigned To**: BATATA1

**Tasks**:

- [ ] Set up Slack app in Slack API
- [ ] Create Slack OAuth flow
  - [ ] Slack app installation endpoint
  - [ ] OAuth callback handler
  - [ ] Store Slack workspace tokens
- [ ] Create webhook endpoints for Slack
  - [ ] Receive Slack events
  - [ ] Verify Slack request signatures
- [ ] Implement Slack notification sending
  - [ ] Send issue updates to Slack channels
  - [ ] Format messages with Slack blocks
- [ ] Create Slack command handlers (optional)
  - [ ] /create-issue command
  - [ ] /search-issues command
- [ ] Create integration management UI
  - [ ] Connect Slack workspace
  - [ ] Configure notification channels
  - [ ] Disconnect integration
- [ ] Write Slack integration tests

**Deliverables**:

- Slack integration
- Integration management UI

---

#### 1.7.3 Basic Integrations - GitHub

**Priority**: Medium  
**Estimated Time**: 7-10 days  
**Dependencies**: 1.7.1, 1.3.2  
**Assigned To**: HWIMDA1

**Tasks**:

- [ ] Set up GitHub OAuth app
- [ ] Create GitHub OAuth flow
  - [ ] GitHub app installation endpoint
  - [ ] OAuth callback handler
  - [ ] Store GitHub tokens
- [ ] Create GitHub webhook receiver
  - [ ] Verify webhook signatures
  - [ ] Handle push events
  - [ ] Handle pull request events
  - [ ] Handle issue events
- [ ] Implement GitHub issue linking
  - [ ] Link GitHub commits to issues
  - [ ] Link GitHub PRs to issues
  - [ ] Display GitHub links in issue detail
- [ ] Create GitHub integration management UI
  - [ ] Connect GitHub repository
  - [ ] Configure webhook settings
  - [ ] Disconnect integration
- [ ] Write GitHub integration tests

**Deliverables**:

- GitHub integration
- GitHub issue linking

---

## Phase 1.8: Mobile Responsive & Polish (Weeks 20-22)

### Dependencies: All previous phases

#### 1.8.1 Mobile Responsive Design

**Priority**: High  
**Estimated Time**: 10-14 days  
**Dependencies**: All frontend tasks  
**Assigned To**: BATATA2, HWIMDA2 (shared)

**Tasks**:

- [ ] Audit all pages for mobile responsiveness
- [ ] Update layout components for mobile
  - [ ] Responsive navigation (hamburger menu)
  - [ ] Responsive sidebar (collapse on mobile)
  - [ ] Responsive tables (convert to cards on mobile)
- [ ] Optimize forms for mobile
  - [ ] Touch-friendly inputs
  - [ ] Mobile keyboard types
  - [ ] Mobile-friendly date pickers
- [ ] Optimize Kanban board for mobile
  - [ ] Horizontal scroll or vertical stack
  - [ ] Touch-optimized drag and drop
- [ ] Optimize page editor for mobile
  - [ ] Mobile-friendly toolbar
  - [ ] Touch-optimized formatting
- [ ] Test on various screen sizes (320px - 1920px)
- [ ] Fix mobile-specific bugs

**Deliverables**:

- Fully responsive application
- Mobile-optimized UX

---

#### 1.8.2 Performance Optimization

**Priority**: Medium  
**Estimated Time**: 5-7 days  
**Dependencies**: All frontend tasks  
**Assigned To**: BATATA2

**Tasks**:

- [ ] Implement code splitting
  - [ ] Route-based code splitting
  - [ ] Component lazy loading
- [ ] Optimize bundle size
  - [ ] Tree shaking
  - [ ] Remove unused dependencies
  - [ ] Optimize images
- [ ] Implement caching strategies
  - [ ] API response caching
  - [ ] Static asset caching
- [ ] Add loading skeletons
- [ ] Optimize database queries
  - [ ] Add missing indexes
  - [ ] Optimize N+1 queries
  - [ ] Add query result caching (Redis)
- [ ] Performance testing and profiling
- [ ] Set up performance monitoring

**Deliverables**:

- Optimized application performance
- Performance monitoring

---

#### 1.8.3 Error Handling & User Feedback

**Priority**: High  
**Estimated Time**: 5-7 days  
**Dependencies**: All tasks  
**Assigned To**: HWIMDA2

**Tasks**:

- [ ] Create comprehensive error boundary components
- [ ] Implement global error handling
- [ ] Create user-friendly error messages
- [ ] Add toast notifications for user actions
- [ ] Implement loading states consistently
- [ ] Add form validation error messages
- [ ] Create 404 and error pages
- [ ] Set up error tracking (Sentry or similar)
- [ ] Test error scenarios

**Deliverables**:

- Robust error handling
- Better user feedback

---

## Phase 1.9: Testing & QA (Weeks 22-24)

### Dependencies: All previous phases

#### 1.9.1 Backend Testing

**Priority**: Critical  
**Estimated Time**: 10-14 days  
**Dependencies**: All backend tasks  
**Assigned To**: BATATA1, HWIMDA1 (shared)

**Tasks**:

- [ ] Set up testing framework (Jest, pytest, etc.)
- [ ] Write unit tests for utilities and helpers
- [ ] Write integration tests for API endpoints
  - [ ] Authentication endpoints
  - [ ] Organization endpoints
  - [ ] Project endpoints
  - [ ] Issue endpoints
  - [ ] Comment endpoints
  - [ ] Page endpoints
  - [ ] Search endpoints
  - [ ] Notification endpoints
- [ ] Write database migration tests
- [ ] Write integration tests for third-party services (Slack, GitHub)
- [ ] Set up test database and fixtures
- [ ] Achieve minimum 70% code coverage
- [ ] Set up CI/CD to run tests automatically

**Deliverables**:

- Comprehensive backend test suite
- CI/CD test pipeline

---

#### 1.9.2 Frontend Testing

**Priority**: High  
**Estimated Time**: 10-14 days  
**Dependencies**: All frontend tasks  
**Assigned To**: BATATA2, HWIMDA2 (shared)

**Tasks**:

- [ ] Set up testing framework (Jest, Vitest, etc.)
- [ ] Set up component testing library (React Testing Library, Vue Test Utils)
- [ ] Write unit tests for utility functions
- [ ] Write component tests for key components
  - [ ] Form components
  - [ ] List components
  - [ ] Modal components
- [ ] Write integration tests for user flows
  - [ ] User registration/login flow
  - [ ] Create issue flow
  - [ ] Create page flow
  - [ ] Comment flow
- [ ] Set up E2E testing (Playwright, Cypress)
  - [ ] Critical user journeys
- [ ] Achieve minimum 60% code coverage
- [ ] Set up CI/CD to run tests automatically

**Deliverables**:

- Comprehensive frontend test suite
- E2E test coverage

---

## Phase 1.10: Deployment & Launch Preparation (Weeks 24-26)

### Dependencies: All previous phases

#### 1.10.1 Infrastructure Setup

**Priority**: Critical  
**Estimated Time**: 10-14 days  
**Dependencies**: All tasks  
**Assigned To**: BATATA1, HWIMDA1 (shared)

**Tasks**:

- [ ] Set up cloud infrastructure (AWS/GCP/Azure)
  - [ ] Application servers
  - [ ] Database servers (PostgreSQL)
  - [ ] Redis cache
  - [ ] File storage (S3 or similar)
  - [ ] Load balancer
- [-] Set up containerization (Docker)
  - [x] Create Dockerfiles for frontend (app1 production and dev)
  - [x] Create docker-compose for local development
  - [ ] Create Dockerfiles for backend (pending)
- [ ] Set up CI/CD pipeline
  - [ ] Build process
  - [ ] Automated testing
  - [ ] Deployment process
  - [ ] Environment management (dev, staging, prod)
- [ ] Set up monitoring and logging
  - [ ] Application monitoring (Datadog, New Relic)
  - [ ] Error tracking (Sentry)
  - [ ] Log aggregation
- [ ] Set up backup system
  - [ ] Database backups
  - [ ] File storage backups
- [ ] Set up SSL certificates
- [ ] Configure domain and DNS

**Deliverables**:

- Production infrastructure
- CI/CD pipeline

---

#### 1.10.2 Security & Compliance

**Priority**: Critical  
**Estimated Time**: 7-10 days  
**Dependencies**: All tasks  
**Assigned To**: HWIMDA1

**Tasks**:

- [ ] Security audit
  - [ ] Code security review
  - [ ] Dependency vulnerability scan
  - [ ] OWASP Top 10 checklist
- [ ] Implement security headers
- [ ] Set up rate limiting
- [ ] Implement CORS properly
- [ ] Set up DDoS protection
- [ ] Create security documentation
- [ ] Set up security monitoring
- [ ] Prepare privacy policy and terms of service

**Deliverables**:

- Secure application
- Security documentation

---

#### 1.10.3 Documentation & Launch Materials

**Priority**: High  
**Estimated Time**: 7-10 days  
**Dependencies**: All tasks  
**Assigned To**: BATATA2, HWIMDA2 (shared)

**Tasks**:

- [ ] Write user documentation
  - [ ] Getting started guide
  - [ ] Feature documentation
  - [ ] FAQ
- [ ] Create video tutorials (optional)
- [ ] Prepare marketing website
- [ ] Write blog posts for launch
- [ ] Create help center/knowledge base
- [ ] Prepare launch announcement
- [ ] Set up customer support system

**Deliverables**:

- Complete documentation
- Launch materials

---

## Summary

**Total Estimated Timeline**: 26 weeks (6 months)

**Key Milestones**:

- Week 3: Foundation complete
- Week 5: User/Organization management complete
- Week 10: Project management core complete
- Week 14: Documentation core complete
- Week 18: Notifications complete
- Week 20: Integrations complete
- Week 22: Mobile responsive complete
- Week 24: Testing complete
- Week 26: Launch ready

**Team Size Recommendations**:

- 2-3 Backend developers
- 2-3 Frontend developers
- 1 DevOps engineer
- 1 QA engineer
- 1 Product designer

**Critical Path**:

1. Foundation (Auth, Database, API, Frontend)
2. Project Management (Issues, Kanban)
3. Documentation (Pages, Editor)
4. Polish (Mobile, Testing, Deployment)
