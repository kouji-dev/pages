"""Database seed script for development data."""

import asyncio
import random
import sys
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
        issues = [
            IssueModel(
                id=uuid4(),
                project_id=project.id,
                issue_number=1,
                title="Set up project infrastructure",
                description="Configure Docker, CI/CD, and development environment",
                type="task",
                status="done",
                priority="high",
                reporter_id=admin_user.id,
                assignee_id=dev_user.id,
            ),
            IssueModel(
                id=uuid4(),
                project_id=project.id,
                issue_number=2,
                title="Implement user authentication",
                description="JWT-based authentication with login, register, and password reset",
                type="story",
                status="in_progress",
                priority="critical",
                reporter_id=admin_user.id,
                assignee_id=dev_user.id,
            ),
            IssueModel(
                id=uuid4(),
                project_id=project.id,
                issue_number=3,
                title="Create database schema",
                description="Design and implement PostgreSQL schema with SQLAlchemy",
                type="task",
                status="in_progress",
                priority="high",
                reporter_id=dev_user.id,
                assignee_id=dev_user.id,
            ),
            IssueModel(
                id=uuid4(),
                project_id=project.id,
                issue_number=4,
                title="Build organization management UI",
                description="Create organization CRUD pages in Angular",
                type="story",
                status="todo",
                priority="medium",
                reporter_id=admin_user.id,
            ),
            IssueModel(
                id=uuid4(),
                project_id=project.id,
                issue_number=5,
                title="Fix login form validation",
                description="Email validation not working correctly on login form",
                type="bug",
                status="todo",
                priority="low",
                reporter_id=test_user.id,
            ),
        ]
        session.add_all(issues)
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
        print(f"   - 5 issues")
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
