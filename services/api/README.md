# Pages API

Backend API service built with FastAPI following Domain-Driven Design (DDD) and Clean Architecture principles.

## Architecture

```
src/
├── domain/                 # Domain Layer (Business Logic)
│   ├── entities/          # Domain entities (User, Organization, etc.)
│   ├── value_objects/     # Value objects (Email, Password, etc.)
│   ├── repositories/      # Repository interfaces (abstract)
│   ├── services/          # Domain services
│   └── exceptions/        # Domain exceptions
│
├── application/           # Application Layer (Use Cases)
│   ├── dtos/             # Data Transfer Objects
│   ├── use_cases/        # Application use cases
│   ├── services/         # Application services
│   └── interfaces/       # Port interfaces
│
├── infrastructure/        # Infrastructure Layer (External)
│   ├── database/         # Database implementation
│   │   ├── repositories/ # Repository implementations
│   │   └── migrations/   # Alembic migrations
│   ├── security/         # JWT, password hashing
│   ├── services/         # External service implementations
│   └── config/           # Configuration
│
└── presentation/          # Presentation Layer (API)
    ├── api/v1/           # API v1 routes
    ├── middlewares/      # FastAPI middlewares
    └── dependencies/     # FastAPI dependencies
```

## Getting Started

### Prerequisites

- Python 3.12+
- Poetry
- PostgreSQL 17+
- Redis 8+

### Installation

```bash
# Install dependencies
poetry install

# Run development server
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src

# Run specific test file
poetry run pytest tests/unit/test_auth.py
```

### Linting & Formatting

```bash
# Format code
poetry run black .

# Lint code
poetry run ruff check .

# Type checking
poetry run mypy src
```

## API Documentation

Once the server is running, access the API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## Environment Variables

Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/pages

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# App
DEBUG=true
ALLOWED_ORIGINS=http://localhost:4200
```

## License

MIT License

