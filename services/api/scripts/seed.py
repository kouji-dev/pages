"""Database seed script for development data."""

import asyncio
import sys
from pathlib import Path
from uuid import uuid4

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.domain.value_objects import Email, Password
from src.infrastructure.config import get_settings
from src.infrastructure.database import get_session_context, init_db
from src.infrastructure.database.models import (
    UserModel,
    OrganizationModel,
    OrganizationMemberModel,
    ProjectModel,
    ProjectMemberModel,
    SpaceModel,
    PageModel,
    IssueModel,
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
        from sqlalchemy import select, func

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

        # Create Project
        print("📁 Creating project...")
        project = ProjectModel(
            id=uuid4(),
            organization_id=org.id,
            name="Pages MVP",
            key="PAGES",
            description="Main Pages development project",
        )
        session.add(project)
        await session.flush()

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

        # Create Space
        print("📚 Creating documentation space...")
        space = SpaceModel(
            id=uuid4(),
            organization_id=org.id,
            name="Documentation",
            key="DOC",
            description="Project documentation and knowledge base",
        )
        session.add(space)
        await session.flush()

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

        print("✅ Database seed completed successfully!")
        print("\n📋 Created:")
        print(f"   - 3 users (password: TestPass123!)")
        print(f"   - 1 organization (pages-dev)")
        print(f"   - 1 project (PAGES)")
        print(f"   - 5 issues")
        print(f"   - 1 space (DOC)")
        print(f"   - 4 pages")
        print("\n🔑 Test accounts:")
        print("   - admin@pages.dev (admin)")
        print("   - dev@pages.dev (developer)")
        print("   - test@pages.dev (viewer)")


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
