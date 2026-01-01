"""Database seed script for development data."""

import asyncio
import random
import sys
from datetime import date, timedelta
from pathlib import Path
from uuid import uuid4

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.domain.value_objects import Password
from src.infrastructure.config import get_settings
from src.infrastructure.database import get_session_context, init_db
from src.infrastructure.database.models import (
    FavoriteModel,
    FolderModel,
    IssueModel,
    OrganizationMemberModel,
    OrganizationModel,
    PageModel,
    ProjectMemberModel,
    ProjectModel,
    SpaceModel,
    SprintIssueModel,
    SprintModel,
    UserModel,
)
from src.infrastructure.security import BcryptPasswordService


async def seed_database() -> None:
    """Seed the database with development data."""
    print("🌱 Starting database seed...")

    password_service = BcryptPasswordService()

    # Create default password for all test users
    default_password = Password("TestPass123!")
    hashed_password = password_service.hash(default_password)

    async with get_session_context() as session:
        # Check if data already exists
        from sqlalchemy import func, select

        result = await session.execute(select(func.count()).select_from(UserModel))
        user_count = result.scalar_one()

        if user_count > 0:
            print("⚠️ Database already has data. Skipping seed.")
            return

        # Create Users
        print("👤 Creating users...")
        admin_user = UserModel(
            id=uuid4(),
            email="admin@pages.dev",
            password_hash=hashed_password.value,
            name="Admin User",
            is_active=True,
            is_verified=True,
        )

        dev_user = UserModel(
            id=uuid4(),
            email="dev@pages.dev",
            password_hash=hashed_password.value,
            name="Developer User",
            is_active=True,
            is_verified=True,
        )

        test_user = UserModel(
            id=uuid4(),
            email="test@pages.dev",
            password_hash=hashed_password.value,
            name="Test User",
            is_active=True,
            is_verified=False,
        )

        session.add_all([admin_user, dev_user, test_user])
        await session.flush()

        # Create Organization
        print("🏢 Creating organization...")
        org = OrganizationModel(
            id=uuid4(),
            name="Pages Development",
            slug="pages-dev",
            description="Development organization for Pages project",
        )
        session.add(org)
        await session.flush()

        # Add members to organization
        print("👥 Adding organization members...")
        org_members = [
            OrganizationMemberModel(
                organization_id=org.id,
                user_id=admin_user.id,
                role="admin",
            ),
            OrganizationMemberModel(
                organization_id=org.id,
                user_id=dev_user.id,
                role="member",
            ),
            OrganizationMemberModel(
                organization_id=org.id,
                user_id=test_user.id,
                role="viewer",
            ),
        ]
        session.add_all(org_members)
        await session.flush()

        # Create Folder Structure
        print("📂 Creating folder structure...")
        # Root level folders
        engineering_folder = FolderModel(
            id=uuid4(),
            organization_id=org.id,
            name="Engineering",
            parent_id=None,
            position=0,
        )
        product_folder = FolderModel(
            id=uuid4(),
            organization_id=org.id,
            name="Product",
            parent_id=None,
            position=1,
        )
        marketing_folder = FolderModel(
            id=uuid4(),
            organization_id=org.id,
            name="Marketing",
            parent_id=None,
            position=2,
        )
        session.add_all([engineering_folder, product_folder, marketing_folder])
        await session.flush()

        # Subfolders
        frontend_folder = FolderModel(
            id=uuid4(),
            organization_id=org.id,
            name="Frontend",
            parent_id=engineering_folder.id,
            position=0,
        )
        backend_folder = FolderModel(
            id=uuid4(),
            organization_id=org.id,
            name="Backend",
            parent_id=engineering_folder.id,
            position=1,
        )
        docs_folder = FolderModel(
            id=uuid4(),
            organization_id=org.id,
            name="Documentation",
            parent_id=product_folder.id,
            position=0,
        )
        session.add_all([frontend_folder, backend_folder, docs_folder])
        await session.flush()

        folders = [engineering_folder, product_folder, marketing_folder, frontend_folder, backend_folder, docs_folder]
        folder_ids = [None] + [f.id for f in folders]  # Include None for root

        # Create Projects
        print("📁 Creating projects...")
        project_colors = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899"]
        project_statuses = ["in-progress", "in-progress", "in-progress", "complete", "on-hold"]
        projects = [
            ProjectModel(
                id=uuid4(),
                organization_id=org.id,
                folder_id=random.choice(folder_ids),
                name="Pages MVP",
                key="PAGES",
                description="Main Pages development project",
                color=random.choice(project_colors),
                status=random.choice(project_statuses),
            ),
            ProjectModel(
                id=uuid4(),
                organization_id=org.id,
                folder_id=random.choice(folder_ids),
                name="Mobile App",
                key="MOBILE",
                description="Mobile application development",
                color=random.choice(project_colors),
                status=random.choice(project_statuses),
            ),
            ProjectModel(
                id=uuid4(),
                organization_id=org.id,
                folder_id=random.choice(folder_ids),
                name="API Gateway",
                key="API",
                description="API gateway and microservices",
                color=random.choice(project_colors),
                status=random.choice(project_statuses),
            ),
            ProjectModel(
                id=uuid4(),
                organization_id=org.id,
                folder_id=random.choice(folder_ids),
                name="Design System",
                key="DESIGN",
                description="UI/UX design system and components",
                color=random.choice(project_colors),
                status=random.choice(project_statuses),
            ),
        ]
        session.add_all(projects)
        await session.flush()

        project = projects[0]  # Keep reference to first project for issues

        # Add members to project
        print("👥 Adding project members...")
        project_members = [
            ProjectMemberModel(
                project_id=project.id,
                user_id=admin_user.id,
                role="admin",
            ),
            ProjectMemberModel(
                project_id=project.id,
                user_id=dev_user.id,
                role="member",
            ),
        ]
        session.add_all(project_members)
        await session.flush()

        # Create Issues
        print("📋 Creating sample issues...")
        
        def calculate_story_points(issue_type: str, priority: str) -> int | None:
            """Calculate story points based on issue type and priority."""
            if issue_type not in ["story", "task", "epic"]:
                return None
            
            if priority == "critical":
                return random.choice([8, 13, 21])
            elif priority == "high":
                return random.choice([5, 8, 13])
            elif priority == "medium":
                return random.choice([3, 5, 8])
            else:
                return random.choice([1, 2, 3])
        
        def create_issue_from_template(
            template: dict,
            project_id,
            issue_number: int,
            admin_user_id,
            dev_user_id,
            test_user_id,
        ) -> IssueModel:
            """Create an issue from a template."""
            assignee = random.choice([admin_user_id, dev_user_id, None])
            reporter = random.choice([admin_user_id, dev_user_id, test_user_id])
            story_points = calculate_story_points(template["type"], template["priority"])
            
            return IssueModel(
                id=uuid4(),
                project_id=project_id,
                issue_number=issue_number,
                title=template["title"],
                description=template["description"],
                type=template["type"],
                status=template["status"],
                priority=template["priority"],
                reporter_id=reporter,
                assignee_id=assignee,
                story_points=story_points,
            )
        
        # All issue templates (original + backlog)
        all_issue_templates = [
            {
                "title": "Set up project infrastructure",
                "description": "Configure Docker, CI/CD, and development environment",
                "type": "task",
                "status": "done",
                "priority": "high",
            },
            {
                "title": "Implement user authentication",
                "description": "JWT-based authentication with login, register, and password reset",
                "type": "story",
                "status": "in_progress",
                "priority": "critical",
            },
            {
                "title": "Create database schema",
                "description": "Design and implement PostgreSQL schema with SQLAlchemy",
                "type": "task",
                "status": "in_progress",
                "priority": "high",
            },
            {
                "title": "Build organization management UI",
                "description": "Create organization CRUD pages in Angular",
                "type": "story",
                "status": "todo",
                "priority": "medium",
            },
            {
                "title": "Fix login form validation",
                "description": "Email validation not working correctly on login form",
                "type": "bug",
                "status": "todo",
                "priority": "low",
            },
            {
                "title": "Implement sprint planning feature",
                "description": "Add sprint creation, editing, and management functionality",
                "type": "story",
                "status": "todo",
                "priority": "high",
            },
            {
                "title": "Add issue drag and drop to kanban board",
                "description": "Enable drag and drop functionality for moving issues between columns",
                "type": "task",
                "status": "done",
                "priority": "medium",
            },
            {
                "title": "Create project dashboard",
                "description": "Build dashboard with project metrics and charts",
                "type": "story",
                "status": "todo",
                "priority": "medium",
            },
            {
                "title": "Fix issue assignee dropdown not loading",
                "description": "Assignee dropdown shows empty list when project has members",
                "type": "bug",
                "status": "in_progress",
                "priority": "high",
            },
            {
                "title": "Add issue comments feature",
                "description": "Allow users to add comments to issues for collaboration",
                "type": "story",
                "status": "todo",
                "priority": "low",
            },
            {
                "title": "Implement issue search and filters",
                "description": "Add advanced search and filtering capabilities for issues",
                "type": "task",
                "status": "todo",
                "priority": "medium",
            },
            {
                "title": "Add issue attachments",
                "description": "Enable file uploads and attachments for issues",
                "type": "story",
                "status": "todo",
                "priority": "low",
            },
            # Backlog issues (30 additional tasks)
            {
                "title": "Optimize database queries for better performance",
                "description": "Review and optimize slow database queries to improve application performance",
                "type": "task",
                "status": "todo",
                "priority": "high",
            },
            {
                "title": "Add unit tests for authentication service",
                "description": "Write comprehensive unit tests for the authentication service",
                "type": "task",
                "status": "todo",
                "priority": "medium",
            },
            {
                "title": "Implement dark mode theme",
                "description": "Add dark mode theme support across the application",
                "type": "story",
                "status": "todo",
                "priority": "low",
            },
            {
                "title": "Create API documentation page",
                "description": "Build a comprehensive API documentation page with examples",
                "type": "task",
                "status": "todo",
                "priority": "medium",
            },
            {
                "title": "Fix memory leak in issue list component",
                "description": "Identify and fix memory leak causing performance issues",
                "type": "bug",
                "status": "in_progress",
                "priority": "high",
            },
            {
                "title": "Add email notifications for issue updates",
                "description": "Implement email notifications when issues are updated",
                "type": "story",
                "status": "todo",
                "priority": "medium",
            },
            {
                "title": "Implement file upload validation",
                "description": "Add validation for file uploads including size and type checks",
                "type": "task",
                "status": "todo",
                "priority": "high",
            },
            {
                "title": "Create user profile page",
                "description": "Build user profile page with settings and preferences",
                "type": "story",
                "status": "todo",
                "priority": "medium",
            },
            {
                "title": "Add keyboard shortcuts for navigation",
                "description": "Implement keyboard shortcuts for common navigation actions",
                "type": "task",
                "status": "todo",
                "priority": "low",
            },
            {
                "title": "Implement issue templates",
                "description": "Create reusable issue templates for common task types",
                "type": "story",
                "status": "todo",
                "priority": "medium",
            },
            {
                "title": "Create project analytics dashboard",
                "description": "Build dashboard showing project metrics and analytics",
                "type": "story",
                "status": "todo",
                "priority": "high",
            },
            {
                "title": "Add export functionality for issues",
                "description": "Allow users to export issues to CSV or Excel format",
                "type": "task",
                "status": "todo",
                "priority": "medium",
            },
            {
                "title": "Implement real-time notifications",
                "description": "Add real-time notification system using WebSockets",
                "type": "story",
                "status": "todo",
                "priority": "high",
            },
            {
                "title": "Create onboarding flow for new users",
                "description": "Design and implement user onboarding experience",
                "type": "story",
                "status": "todo",
                "priority": "medium",
            },
            {
                "title": "Add issue dependency tracking",
                "description": "Allow users to link issues and track dependencies",
                "type": "story",
                "status": "todo",
                "priority": "high",
            },
            {
                "title": "Implement issue time tracking",
                "description": "Add time tracking functionality for issues",
                "type": "story",
                "status": "todo",
                "priority": "medium",
            },
            {
                "title": "Create custom field support",
                "description": "Allow projects to define custom fields for issues",
                "type": "epic",
                "status": "todo",
                "priority": "high",
            },
            {
                "title": "Add issue watchers feature",
                "description": "Allow users to watch issues and receive updates",
                "type": "story",
                "status": "todo",
                "priority": "low",
            },
            {
                "title": "Implement issue linking",
                "description": "Enable linking related issues together",
                "type": "story",
                "status": "todo",
                "priority": "medium",
            },
            {
                "title": "Create issue workflow automation",
                "description": "Build automation rules for issue workflows",
                "type": "epic",
                "status": "todo",
                "priority": "high",
            },
            {
                "title": "Add bulk issue operations",
                "description": "Enable bulk editing and operations on multiple issues",
                "type": "task",
                "status": "todo",
                "priority": "medium",
            },
            {
                "title": "Implement issue versioning",
                "description": "Track issue history and version changes",
                "type": "story",
                "status": "todo",
                "priority": "low",
            },
            {
                "title": "Create issue history timeline",
                "description": "Display chronological timeline of issue changes",
                "type": "task",
                "status": "todo",
                "priority": "medium",
            },
            {
                "title": "Add issue tags and labels",
                "description": "Implement tagging system for better issue organization",
                "type": "story",
                "status": "todo",
                "priority": "medium",
            },
            {
                "title": "Implement issue subtasks",
                "description": "Allow breaking down issues into smaller subtasks",
                "type": "story",
                "status": "todo",
                "priority": "high",
            },
            {
                "title": "Create issue reports and charts",
                "description": "Generate reports and visualizations for issue data",
                "type": "story",
                "status": "todo",
                "priority": "medium",
            },
            {
                "title": "Add issue filtering presets",
                "description": "Allow users to save and reuse filter presets",
                "type": "task",
                "status": "todo",
                "priority": "low",
            },
            {
                "title": "Implement issue archiving",
                "description": "Allow archiving old or completed issues",
                "type": "task",
                "status": "todo",
                "priority": "low",
            },
            {
                "title": "Create issue templates library",
                "description": "Build a library of reusable issue templates",
                "type": "story",
                "status": "todo",
                "priority": "medium",
            },
            {
                "title": "Add issue import from CSV",
                "description": "Enable importing issues from CSV files",
                "type": "task",
                "status": "todo",
                "priority": "medium",
            },
        ]
        
        # Create all issues from templates
        issues = []
        backlog_issues = []  # Track backlog issues separately for sprint assignment
        issue_number = 1
        
        # First 12 issues are original issues
        original_issues_count = 12
        for idx, template in enumerate(all_issue_templates):
            issue = create_issue_from_template(
                template,
                project.id,
                issue_number,
                admin_user.id,
                dev_user.id,
                test_user.id,
            )
            issues.append(issue)
            
            # Track backlog issues (issues after the first 12)
            if idx >= original_issues_count:
                backlog_issues.append(issue)
            
            issue_number += 1
        
        session.add_all(issues)
        await session.flush()

        # Create Sprints
        print("🏃 Creating sprints...")
        today = date.today()
        
        # Completed sprint (past)
        completed_sprint = SprintModel(
            id=uuid4(),
            project_id=project.id,
            name="Sprint 1 - Foundation",
            goal="Set up project infrastructure and core features",
            start_date=today - timedelta(days=28),
            end_date=today - timedelta(days=14),
            status="completed",
        )
        
        # Active sprint (current)
        active_sprint = SprintModel(
            id=uuid4(),
            project_id=project.id,
            name="Sprint 2 - Core Features",
            goal="Implement authentication, database schema, and organization management",
            start_date=today - timedelta(days=7),
            end_date=today + timedelta(days=7),
            status="active",
        )
        
        # Planned sprint (future)
        planned_sprint = SprintModel(
            id=uuid4(),
            project_id=project.id,
            name="Sprint 3 - Enhanced Features",
            goal="Add sprint planning, dashboard, and advanced issue features",
            start_date=today + timedelta(days=8),
            end_date=today + timedelta(days=22),
            status="planned",
        )
        
        sprints = [completed_sprint, active_sprint, planned_sprint]
        session.add_all(sprints)
        await session.flush()

        # Assign issues to sprints
        print("🔗 Assigning issues to sprints...")
        sprint_issues = []
        
        # Completed sprint gets done issues
        done_issues = [issue for issue in issues if issue.status == "done"]
        for idx, issue in enumerate(done_issues[:3]):  # First 3 done issues
            sprint_issues.append(
                SprintIssueModel(
                    sprint_id=completed_sprint.id,
                    issue_id=issue.id,
                    order=idx,
                )
            )
        
        # Active sprint gets in_progress and some todo issues
        active_issues = [issue for issue in issues if issue.status == "in_progress"]
        todo_issues = [issue for issue in issues if issue.status == "todo"]
        active_sprint_issues = active_issues + todo_issues[:2]  # All in_progress + 2 todo
        
        for idx, issue in enumerate(active_sprint_issues[:5]):  # Max 5 issues per sprint
            sprint_issues.append(
                SprintIssueModel(
                    sprint_id=active_sprint.id,
                    issue_id=issue.id,
                    order=idx,
                )
            )
        
        # Planned sprint gets remaining todo issues from original issues
        remaining_todo = [issue for issue in todo_issues if issue not in active_sprint_issues]
        planned_sprint_order = 0
        
        # Add some remaining todo issues from original issues
        for issue in remaining_todo[:3]:  # Max 3 from original
            sprint_issues.append(
                SprintIssueModel(
                    sprint_id=planned_sprint.id,
                    issue_id=issue.id,
                    order=planned_sprint_order,
                )
            )
            planned_sprint_order += 1
        
        # Randomly assign backlog issues to sprints
        # Each backlog issue has a 40% chance of being assigned to a sprint
        sprint_order_counters = {
            completed_sprint.id: len([si for si in sprint_issues if si.sprint_id == completed_sprint.id]),
            active_sprint.id: len([si for si in sprint_issues if si.sprint_id == active_sprint.id]),
            planned_sprint.id: planned_sprint_order,
        }
        
        for issue in backlog_issues:
            if random.random() < 0.4:  # 40% chance
                # Randomly choose which sprint to assign to
                sprint = random.choice([completed_sprint, active_sprint, planned_sprint])
                sprint_issues.append(
                    SprintIssueModel(
                        sprint_id=sprint.id,
                        issue_id=issue.id,
                        order=sprint_order_counters[sprint.id],
                    )
                )
                sprint_order_counters[sprint.id] += 1
        
        if sprint_issues:
            session.add_all(sprint_issues)
            await session.flush()

        # Create Spaces
        print("📚 Creating spaces...")
        space_icons = ["book", "book-open", "file-text", "folder", "file", "folder-tree", "library"]
        space_statuses = ["published", "published", "published", "in-review", "draft"]
        spaces = [
            SpaceModel(
                id=uuid4(),
                organization_id=org.id,
                folder_id=random.choice(folder_ids),
                name="Documentation",
                key="DOC",
                description="Project documentation and knowledge base",
                icon=random.choice(space_icons),
                status=random.choice(space_statuses),
                view_count=random.randint(0, 500),
                created_by=admin_user.id,
            ),
            SpaceModel(
                id=uuid4(),
                organization_id=org.id,
                folder_id=random.choice(folder_ids),
                name="Engineering Wiki",
                key="ENG",
                description="Engineering team knowledge base",
                icon=random.choice(space_icons),
                status=random.choice(space_statuses),
                view_count=random.randint(0, 500),
                created_by=dev_user.id,
            ),
            SpaceModel(
                id=uuid4(),
                organization_id=org.id,
                folder_id=random.choice(folder_ids),
                name="Product Specs",
                key="PROD",
                description="Product specifications and requirements",
                icon=random.choice(space_icons),
                status=random.choice(space_statuses),
                view_count=random.randint(0, 500),
                created_by=admin_user.id,
            ),
            SpaceModel(
                id=uuid4(),
                organization_id=org.id,
                folder_id=random.choice(folder_ids),
                name="Marketing Content",
                key="MKT",
                description="Marketing content and resources",
                icon=random.choice(space_icons),
                status=random.choice(space_statuses),
                view_count=random.randint(0, 500),
                created_by=test_user.id,
            ),
        ]
        session.add_all(spaces)
        await session.flush()

        space = spaces[0]  # Keep reference to first space for pages

        # Create Pages
        print("📄 Creating sample pages...")
        getting_started = PageModel(
            id=uuid4(),
            space_id=space.id,
            title="Getting Started",
            slug="getting-started",
            content="# Getting Started\n\nWelcome to Pages! This guide will help you get started.",
            created_by=admin_user.id,
            position=0,
        )
        session.add(getting_started)
        await session.flush()

        pages = [
            PageModel(
                id=uuid4(),
                space_id=space.id,
                parent_id=getting_started.id,
                title="Installation",
                slug="installation",
                content="# Installation\n\n```bash\ndocker-compose up\n```",
                created_by=dev_user.id,
                position=0,
            ),
            PageModel(
                id=uuid4(),
                space_id=space.id,
                parent_id=getting_started.id,
                title="Configuration",
                slug="configuration",
                content="# Configuration\n\nCopy `.env.example` to `.env` and configure your settings.",
                created_by=dev_user.id,
                position=1,
            ),
            PageModel(
                id=uuid4(),
                space_id=space.id,
                title="API Reference",
                slug="api-reference",
                content="# API Reference\n\nVisit `/docs` for the complete API documentation.",
                created_by=admin_user.id,
                position=1,
            ),
        ]
        session.add_all(pages)
        await session.flush()

        # Create Favorites (randomly for some projects and spaces)
        print("⭐ Creating favorites...")
        users = [admin_user, dev_user, test_user]
        favorites = []

        # Randomly favorite some projects
        for project in projects:
            if random.random() < 0.5:  # 50% chance
                user = random.choice(users)
                favorites.append(
                    FavoriteModel(
                        id=uuid4(),
                        user_id=user.id,
                        entity_type="project",
                        entity_id=project.id,
                    )
                )

        # Randomly favorite some spaces
        for space in spaces:
            if random.random() < 0.5:  # 50% chance
                user = random.choice(users)
                favorites.append(
                    FavoriteModel(
                        id=uuid4(),
                        user_id=user.id,
                        entity_type="space",
                        entity_id=space.id,
                    )
                )

        if favorites:
            session.add_all(favorites)
            await session.flush()

        print("✅ Database seed completed successfully!")
        print("\n📋 Created:")
        print(f"   - 3 users (password: TestPass123!)")
        print(f"   - 1 organization (pages-dev)")
        print(f"   - {len(folders)} folders (with hierarchical structure)")
        print(f"   - {len(projects)} projects")
        print(f"   - {len(issues)} issues")
        print(f"   - {len(sprints)} sprints (1 completed, 1 active, 1 planned)")
        print(f"   - {len(sprint_issues)} sprint-issue assignments")
        print(f"   - {len(spaces)} spaces")
        print(f"   - 4 pages")
        print(f"   - {len(favorites)} favorites")
        print("\n🔑 Test accounts:")
        print("   - admin@pages.dev (admin)")
        print("   - dev@pages.dev (developer)")
        print("   - test@pages.dev (viewer)")
        print("\n📂 Folder structure:")
        print("   - Engineering")
        print("     - Frontend")
        print("     - Backend")
        print("   - Product")
        print("     - Documentation")
        print("   - Marketing")


async def main() -> None:
    """Main entry point."""
    settings = get_settings()
    print(f"🔧 Environment: {settings.environment}")
    print(f"🗄️ Database: {settings.database_url}")

    # Initialize database tables first
    await init_db()

    # Seed data
    await seed_database()


if __name__ == "__main__":
    asyncio.run(main())
