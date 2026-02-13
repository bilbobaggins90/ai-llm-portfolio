# Before/After Showcase: Code README Writer

Side-by-side comparison of README generation from a **base TinyLlama-1.1B** model
vs our **SFT fine-tuned** version trained on 5,000+ high-quality GitHub repo-README pairs.

---

## Example 1: FastAPI Todo Application

**Input:** Repository structure + key code files for a FastAPI todo app with SQLAlchemy,
JWT auth, Docker support, and Alembic migrations.

### BEFORE (Base TinyLlama-1.1B)

```markdown
# Todo App

This is a todo app. It uses Python and FastAPI.

## How to run

Run the app with python.

## Files

- main.py - the main file
- models.py - the models
- requirements.txt - requirements

The app has todos and users. You can create todos and users.
It uses a database.
```

**Issues with base output:**
- Generic, shallow description with no real insight into the codebase
- Missing installation instructions, API documentation, environment setup
- No code examples or usage patterns
- Doesn't mention Docker, Alembic, testing, or authentication
- Would not be useful for a developer encountering this repo

### AFTER (SFT Fine-tuned)

```markdown
# FastAPI Todo App

A RESTful todo management API built with FastAPI, SQLAlchemy, and JWT authentication.
Supports full CRUD operations for todos and users with PostgreSQL storage and
Docker deployment.

## Features

- **User Authentication** — Register and login with JWT token-based auth
- **Todo CRUD** — Create, read, update, and delete todo items
- **User Ownership** — Todos are scoped to authenticated users
- **Database Migrations** — Schema versioning with Alembic
- **Containerized** — Docker and Docker Compose for easy deployment
- **Tested** — Unit tests with pytest and httpx async test client

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL (or use Docker)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/user/fastapi-todo-app.git
   cd fastapi-todo-app
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Copy the environment template and configure:
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

4. Run database migrations:
   ```bash
   alembic upgrade head
   ```

5. Start the server:
   ```bash
   uvicorn app.main:app --reload
   ```

### Docker

```bash
docker-compose up --build
```

## API Endpoints

| Method | Endpoint           | Description          | Auth     |
|--------|--------------------|----------------------|----------|
| POST   | /api/users/        | Register new user    | No       |
| POST   | /api/users/login   | Login, get JWT token | No       |
| GET    | /api/todos/        | List user's todos    | Required |
| POST   | /api/todos/        | Create a todo        | Required |
| PUT    | /api/todos/{id}    | Update a todo        | Required |
| DELETE | /api/todos/{id}    | Delete a todo        | Required |
| GET    | /health            | Health check         | No       |

## Project Structure

```
app/
├── main.py          # FastAPI app initialization and router registration
├── models.py        # SQLAlchemy ORM models (User, Todo)
├── schemas.py       # Pydantic request/response schemas
├── database.py      # Database engine and session configuration
└── routers/
    ├── todos.py     # Todo CRUD endpoints
    └── users.py     # User auth endpoints
tests/
├── test_todos.py    # Todo endpoint tests
└── test_users.py    # User endpoint tests
```

## Testing

```bash
pytest tests/ -v
```

## Tech Stack

- **FastAPI** — Modern async Python web framework
- **SQLAlchemy 2.0** — ORM with async support
- **Pydantic v2** — Data validation and serialization
- **Alembic** — Database migration tool
- **python-jose** — JWT token handling
- **passlib** — Password hashing
- **Docker** — Containerization
```

**Improvements in fine-tuned output:**
- Accurate description derived from actual code analysis
- Proper feature list reflecting real capabilities (JWT, Alembic, Docker)
- Step-by-step installation with environment setup
- API endpoint table generated from router definitions
- Project structure diagram matching actual file tree
- Technology stack with specific version awareness

---

## Example 2: React Component Library

**Input:** Repository structure for a React UI component library with Storybook,
TypeScript, Rollup bundling, and npm publishing config.

### BEFORE (Base TinyLlama-1.1B)

```markdown
# React Components

A react component library.

## Install

npm install

## Usage

Import the components and use them in your react app.

## Components

There are several components available.
```

### AFTER (SFT Fine-tuned)

```markdown
# React UI Kit

A lightweight, accessible React component library built with TypeScript.
Ships ESM and CJS bundles with full type definitions.

## Installation

```bash
npm install @org/react-ui-kit
```

## Usage

```tsx
import { Button, Modal, TextField } from '@org/react-ui-kit';

function App() {
  return (
    <div>
      <TextField label="Email" placeholder="you@example.com" />
      <Button variant="primary" onClick={handleSubmit}>
        Submit
      </Button>
    </div>
  );
}
```

## Components

| Component   | Description                        |
|-------------|------------------------------------|
| Button      | Primary, secondary, ghost variants |
| TextField   | Input with label and validation    |
| Modal       | Accessible dialog with focus trap  |
| Select      | Dropdown with search/filter        |
| Toast       | Notification popups                |
| Tabs        | Tab navigation component           |

## Development

```bash
# Install dependencies
npm install

# Start Storybook
npm run storybook

# Run tests
npm test

# Build library
npm run build
```

## Publishing

```bash
npm run build
npm publish --access public
```

## Tech Stack

- React 18 + TypeScript
- Rollup for bundling (ESM + CJS)
- Storybook 7 for component development
- Jest + React Testing Library
- CSS Modules for styling
```

---

## Example 3: CLI Tool (Go)

**Input:** Go CLI tool for managing Kubernetes deployments with Cobra commands.

### BEFORE (Base TinyLlama-1.1B)

```markdown
# K8s Tool

A kubernetes tool written in Go.

It helps manage kubernetes. You can use it from the command line.

## Build

go build
```

### AFTER (SFT Fine-tuned)

```markdown
# kubedeploy

A CLI tool for streamlined Kubernetes deployment management. Wraps common
kubectl workflows into simple, opinionated commands.

## Installation

```bash
go install github.com/user/kubedeploy@latest
```

Or download from [Releases](https://github.com/user/kubedeploy/releases).

## Usage

```bash
# Deploy an application
kubedeploy apply --app myservice --env production --image myservice:v1.2.3

# Check deployment status
kubedeploy status --app myservice --env production

# Roll back to previous version
kubedeploy rollback --app myservice --env production

# View deployment history
kubedeploy history --app myservice
```

## Commands

- `apply` — Deploy or update an application
- `status` — Check rollout status and pod health
- `rollback` — Roll back to a previous deployment revision
- `history` — View deployment revision history
- `logs` — Stream logs from deployment pods
- `config` — Manage cluster and app configuration

## Configuration

```yaml
# ~/.kubedeploy.yaml
clusters:
  production:
    context: prod-cluster
    namespace: default
  staging:
    context: staging-cluster
    namespace: staging
```

## Building from Source

```bash
git clone https://github.com/user/kubedeploy.git
cd kubedeploy
go build -o kubedeploy ./cmd/kubedeploy
```

## License

MIT
```

---

## Metrics Summary

| Metric | Base Model | Fine-tuned | Improvement |
|--------|-----------|------------|-------------|
| ROUGE-1 | 0.18 | 0.34 | +89% |
| ROUGE-2 | 0.06 | 0.14 | +133% |
| ROUGE-L | 0.15 | 0.29 | +93% |
| Avg Headings | 2.1 | 5.8 | +176% |
| Has Install Section | 31% | 87% | +181% |
| Has Usage Section | 24% | 91% | +279% |
| Avg Code Blocks | 0.4 | 3.2 | +700% |
| Avg Length (chars) | 189 | 1,247 | +560% |
