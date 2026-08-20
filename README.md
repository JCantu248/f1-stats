# F1 Stats

A Django REST API for modeling and serving Formula 1 season, constructor, driver, qualifying, and race-result data.

This project is being built as a small end-to-end engineering project with an emphasis on clean backend design, automated testing, containerization, and portable CI workflows that run in both GitHub Actions and Bitrise.

## Features

- Django 5 backend with Django REST Framework
- Formula 1 domain models for:
  - Seasons
  - Constructors
  - Race cars
  - Drivers and season entries
  - Circuits
  - Races
  - Qualifying results
  - Race results
- JSON-based management commands for loading season and race data
- REST API endpoints for races, constructors, and drivers
- Django admin interface
- Automated backend tests
- Ruff linting and formatting checks
- Django system and migration consistency checks
- Docker support
- CI support for GitHub Actions and Bitrise

## Tech Stack

- **Python**
- **Django 5**
- **Django REST Framework**
- **SQLite** for local development
- **Ruff** for linting and formatting
- **Docker / Docker Compose**
- **GitHub Actions**
- **Bitrise CI**

## Project Structure

```text
f1-stats/
├── config/                 # Active Django project configuration
├── racing/                 # F1 domain models, views, URLs, tests, and commands
│   ├── management/
│   │   └── commands/
│   │       ├── seed_season.py
│   │       └── import_race_results.py
│   ├── migrations/
│   ├── admin.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── data/                   # JSON season and race data
├── scripts/                # Repository-owned CI scripts
├── .github/
│   └── workflows/          # GitHub Actions workflows
├── bitrise.yml             # Bitrise workflow configuration
├── Dockerfile
├── docker-compose.yml
├── manage.py
├── pyproject.toml          # Ruff configuration
└── requirements.txt
```

## Local Development

### 1. Clone the repository

```bash
git clone git@github.com:<your-username>/f1-stats.git
cd f1-stats
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Apply database migrations

```bash
python manage.py migrate
```

### 5. Load sample 2026 season data

The season must be loaded before individual race results because race imports reference drivers and constructors already associated with that season.

```bash
python manage.py seed_season data/2026-f1-season.json
```

Then import race data:

```bash
python manage.py import_race_results data/2026-australian-grand-prix.json
python manage.py import_race_results data/2026-chinese-grand-prix.json
python manage.py import_race_results data/2026-japaneese-grand-prix.json
```

### 6. Run the development server

```bash
python manage.py runserver
```

The API will be available at:

```text
http://localhost:8000/api/
```

The Django admin is available at:

```text
http://localhost:8000/admin/
```

To create an administrator account:

```bash
python manage.py createsuperuser
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/races/` | List races |
| `GET` | `/api/races/<race_id>/` | Retrieve a race |
| `GET` | `/api/constructors/` | List constructors |
| `GET` | `/api/constructors/<constructor_id>/` | Retrieve a constructor |
| `GET` | `/api/drivers/` | List drivers |
| `GET` | `/api/drivers/<driver_number>/` | Retrieve a driver by permanent number |

Example:

```bash
curl http://localhost:8000/api/races/
```

## Testing

Run the Django test suite with:

```bash
python manage.py test
```

The tests use Django's isolated test database and do not depend on manually seeded local data.

## Code Quality

The backend uses Ruff for static checks, import ordering, and formatting.

Run lint checks:

```bash
ruff check .
```

Verify formatting:

```bash
ruff format --check .
```

Apply formatting locally when needed:

```bash
ruff format .
```

Django-specific validation is also part of the quality gate:

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
```

## Continuous Integration

The backend CI workflow is intentionally platform-independent. GitHub Actions and Bitrise run the same repository-owned validation process so that application quality checks are not coupled to a single CI provider.

The backend quality gate performs:

```text
Install dependencies
        ↓
Ruff lint
        ↓
Ruff formatting check
        ↓
Django system check
        ↓
Migration consistency check
        ↓
Backend tests
```

### GitHub Actions

GitHub Actions runs the backend checks on pushes and pull requests to the configured branch.

Workflow configuration:

```text
.github/workflows/backend-ci.yml
```

### Bitrise

Bitrise runs the equivalent backend validation workflow from:

```text
bitrise.yml
```

This allows the same repository to demonstrate CI execution across both a general-purpose CI platform and Bitrise.

## Docker

Build and run the backend with Docker Compose:

```bash
docker compose up --build
```

The application will be exposed on:

```text
http://localhost:8000
```

Stop the services with:

```bash
docker compose down
```

## Data Import Design

Season and race data are stored as JSON fixtures under `data/` and loaded through custom Django management commands rather than being embedded directly in application code.

The expected import order is:

```text
Season
  ↓
Constructors / Race Cars / Drivers
  ↓
Race
  ↓
Qualifying Results
  ↓
Race Results
```

Imports run inside database transactions so a failed import does not leave partially written race data.

## Goals

The project is designed to demonstrate practical software-engineering concerns beyond simply exposing REST endpoints:

- Domain-oriented relational data modeling
- Deterministic automated tests
- Reproducible local development
- Static code-quality enforcement
- Database migration validation
- Containerized execution
- CI portability between GitHub Actions and Bitrise

## Roadmap

Planned work includes:

- Expand backend test coverage
- Add additional 2026 race data
- Improve API serialization and error handling
- Add an Android client
- Add Android build and unit-test stages to Bitrise
- Produce build artifacts through the mobile CI pipeline

## License

This project is intended for educational and portfolio use.
