export interface DemoExample {
  id: string
  name: string
  language: string
  fileTree: string
  codeSnippet: string
  baseOutput: string
  fineTunedOutput: string
}

export const demoExamples: DemoExample[] = [
  {
    id: 'fastapi-todo',
    name: 'fastapi-todo-app',
    language: 'Python',
    fileTree: `app/
app/__init__.py
app/main.py
app/models.py
app/database.py
app/schemas.py
app/routers/
app/routers/__init__.py
app/routers/todos.py
app/routers/users.py
tests/
tests/test_todos.py
tests/test_users.py
requirements.txt
Dockerfile
docker-compose.yml
.env.example
alembic.ini
alembic/
alembic/versions/`,
    codeSnippet: `--- requirements.txt ---
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.2
alembic==1.13.0
python-jose==3.3.0
passlib==1.7.4
pytest==7.4.3

--- app/main.py ---
from fastapi import FastAPI
from app.routers import todos, users
from app.database import engine
from app import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Todo API", version="1.0.0")
app.include_router(todos.router, prefix="/api/todos", tags=["todos"])
app.include_router(users.router, prefix="/api/users", tags=["users"])

@app.get("/health")
def health_check():
    return {"status": "healthy"}

--- app/models.py ---
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    todos = relationship("Todo", back_populates="owner")

class Todo(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="todos")`,
    baseOutput: `# Todo App

This is a todo app. It uses Python and FastAPI.

## How to run

Run the app with python.

## Files

- main.py - the main file
- models.py - the models
- requirements.txt - requirements

The app has todos and users. You can create todos and users.
It uses a database.`,
    fineTunedOutput: `# FastAPI Todo App

A RESTful todo management API built with FastAPI, SQLAlchemy, and JWT authentication. Supports full CRUD operations for todos and users with PostgreSQL storage and Docker deployment.

## Features

- **User Authentication** — Register and login with JWT token-based auth
- **Todo CRUD** — Create, read, update, and delete todo items
- **User Ownership** — Todos are scoped to authenticated users
- **Database Migrations** — Schema versioning with Alembic
- **Containerized** — Docker and Docker Compose for easy deployment
- **Tested** — Unit tests with pytest

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL (or use Docker)

### Installation

\`\`\`bash
git clone https://github.com/user/fastapi-todo-app.git
cd fastapi-todo-app
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
\`\`\`

Copy the environment template and configure:

\`\`\`bash
cp .env.example .env
\`\`\`

Run database migrations:

\`\`\`bash
alembic upgrade head
\`\`\`

Start the server:

\`\`\`bash
uvicorn app.main:app --reload
\`\`\`

### Docker

\`\`\`bash
docker-compose up --build
\`\`\`

## API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | /api/users/ | Register new user | No |
| POST | /api/users/login | Login, get JWT token | No |
| GET | /api/todos/ | List user's todos | Required |
| POST | /api/todos/ | Create a todo | Required |
| PUT | /api/todos/{id} | Update a todo | Required |
| DELETE | /api/todos/{id} | Delete a todo | Required |
| GET | /health | Health check | No |

## Project Structure

\`\`\`
app/
├── main.py          # FastAPI app initialization
├── models.py        # SQLAlchemy ORM models (User, Todo)
├── schemas.py       # Pydantic request/response schemas
├── database.py      # Database engine and session config
└── routers/
    ├── todos.py     # Todo CRUD endpoints
    └── users.py     # User auth endpoints
tests/
├── test_todos.py    # Todo endpoint tests
└── test_users.py    # User endpoint tests
\`\`\`

## Testing

\`\`\`bash
pytest tests/ -v
\`\`\`

## Tech Stack

- **FastAPI** — Modern async Python web framework
- **SQLAlchemy 2.0** — ORM with async support
- **Pydantic v2** — Data validation and serialization
- **Alembic** — Database migration tool
- **python-jose** — JWT token handling
- **passlib** — Password hashing
- **Docker** — Containerization`,
  },
  {
    id: 'react-ui-kit',
    name: 'react-ui-kit',
    language: 'TypeScript',
    fileTree: `src/
src/index.ts
src/components/
src/components/Button/
src/components/Button/Button.tsx
src/components/Button/Button.test.tsx
src/components/Button/Button.module.css
src/components/Modal/
src/components/Modal/Modal.tsx
src/components/Modal/Modal.test.tsx
src/components/TextField/
src/components/TextField/TextField.tsx
src/components/Select/
src/components/Select/Select.tsx
src/components/Toast/
src/components/Toast/Toast.tsx
src/components/Tabs/
src/components/Tabs/Tabs.tsx
.storybook/
.storybook/main.ts
.storybook/preview.ts
stories/
stories/Button.stories.tsx
stories/Modal.stories.tsx
package.json
tsconfig.json
rollup.config.js
jest.config.ts`,
    codeSnippet: `--- package.json ---
{
  "name": "@org/react-ui-kit",
  "version": "1.2.0",
  "main": "dist/cjs/index.js",
  "module": "dist/esm/index.js",
  "types": "dist/types/index.d.ts",
  "scripts": {
    "build": "rollup -c",
    "test": "jest",
    "storybook": "storybook dev -p 6006",
    "lint": "eslint src/"
  },
  "peerDependencies": {
    "react": "^18.0.0",
    "react-dom": "^18.0.0"
  }
}

--- src/components/Button/Button.tsx ---
import React from 'react';
import styles from './Button.module.css';

interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  onClick?: () => void;
  children: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  disabled = false,
  onClick,
  children,
}) => (
  <button
    className={\`\${styles.button} \${styles[variant]} \${styles[size]}\`}
    disabled={disabled}
    onClick={onClick}
  >
    {children}
  </button>
);

--- src/index.ts ---
export { Button } from './components/Button/Button';
export { Modal } from './components/Modal/Modal';
export { TextField } from './components/TextField/TextField';
export { Select } from './components/Select/Select';
export { Toast } from './components/Toast/Toast';
export { Tabs } from './components/Tabs/Tabs';`,
    baseOutput: `# React Components

A react component library.

## Install

npm install

## Usage

Import the components and use them in your react app.

## Components

There are several components available.`,
    fineTunedOutput: `# React UI Kit

A lightweight, accessible React component library built with TypeScript. Ships ESM and CJS bundles with full type definitions.

## Installation

\`\`\`bash
npm install @org/react-ui-kit
\`\`\`

## Usage

\`\`\`tsx
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
\`\`\`

## Components

| Component | Description |
|-----------|-------------|
| Button | Primary, secondary, ghost variants with sm/md/lg sizes |
| Modal | Accessible dialog with focus trap |
| TextField | Input with label and validation |
| Select | Dropdown with search and filter |
| Toast | Notification popups |
| Tabs | Tab navigation component |

## Development

\`\`\`bash
# Install dependencies
npm install

# Start Storybook
npm run storybook

# Run tests
npm test

# Build library
npm run build
\`\`\`

## Publishing

\`\`\`bash
npm run build
npm publish --access public
\`\`\`

## Tech Stack

- React 18 + TypeScript
- Rollup for bundling (ESM + CJS)
- Storybook 7 for component development
- Jest + React Testing Library
- CSS Modules for styling`,
  },
  {
    id: 'kubedeploy-cli',
    name: 'kubedeploy',
    language: 'Go',
    fileTree: `cmd/
cmd/kubedeploy/
cmd/kubedeploy/main.go
internal/
internal/deployer/
internal/deployer/deployer.go
internal/deployer/rollback.go
internal/config/
internal/config/config.go
internal/k8s/
internal/k8s/client.go
internal/k8s/pods.go
internal/k8s/deployments.go
pkg/
pkg/logger/
pkg/logger/logger.go
go.mod
go.sum
Makefile
Dockerfile
.goreleaser.yaml`,
    codeSnippet: `--- go.mod ---
module github.com/user/kubedeploy

go 1.21

require (
    github.com/spf13/cobra v1.8.0
    github.com/spf13/viper v1.18.2
    k8s.io/client-go v0.29.0
    k8s.io/apimachinery v0.29.0
)

--- cmd/kubedeploy/main.go ---
package main

import (
    "fmt"
    "os"

    "github.com/spf13/cobra"
    "github.com/user/kubedeploy/internal/deployer"
    "github.com/user/kubedeploy/internal/config"
)

var rootCmd = &cobra.Command{
    Use:   "kubedeploy",
    Short: "Streamlined Kubernetes deployment management",
}

var applyCmd = &cobra.Command{
    Use:   "apply",
    Short: "Deploy or update an application",
    RunE:  deployer.Apply,
}

var statusCmd = &cobra.Command{
    Use:   "status",
    Short: "Check deployment rollout status",
    RunE:  deployer.Status,
}

var rollbackCmd = &cobra.Command{
    Use:   "rollback",
    Short: "Roll back to a previous revision",
    RunE:  deployer.Rollback,
}

func init() {
    rootCmd.AddCommand(applyCmd, statusCmd, rollbackCmd)
}

func main() {
    if err := rootCmd.Execute(); err != nil {
        fmt.Fprintln(os.Stderr, err)
        os.Exit(1)
    }
}`,
    baseOutput: `# K8s Tool

A kubernetes tool written in Go.

It helps manage kubernetes. You can use it from the command line.

## Build

go build`,
    fineTunedOutput: `# kubedeploy

A CLI tool for streamlined Kubernetes deployment management. Wraps common kubectl workflows into simple, opinionated commands.

## Installation

\`\`\`bash
go install github.com/user/kubedeploy@latest
\`\`\`

Or download from [Releases](https://github.com/user/kubedeploy/releases).

## Usage

\`\`\`bash
# Deploy an application
kubedeploy apply --app myservice --env production --image myservice:v1.2.3

# Check deployment status
kubedeploy status --app myservice --env production

# Roll back to previous version
kubedeploy rollback --app myservice --env production
\`\`\`

## Commands

- \`apply\` — Deploy or update an application
- \`status\` — Check rollout status and pod health
- \`rollback\` — Roll back to a previous deployment revision

## Configuration

\`\`\`yaml
# ~/.kubedeploy.yaml
clusters:
  production:
    context: prod-cluster
    namespace: default
  staging:
    context: staging-cluster
    namespace: staging
\`\`\`

## Building from Source

\`\`\`bash
git clone https://github.com/user/kubedeploy.git
cd kubedeploy
make build
\`\`\`

## Tech Stack

- **Go 1.21** — Core language
- **Cobra** — CLI framework
- **Viper** — Configuration management
- **client-go** — Kubernetes API client
- **GoReleaser** — Release automation

## License

MIT`,
  },
]

export const metrics = {
  rouge1: { base: 0.18, finetuned: 0.34 },
  rouge2: { base: 0.06, finetuned: 0.14 },
  rougeL: { base: 0.15, finetuned: 0.29 },
  avgHeadings: { base: 2.1, finetuned: 5.8 },
  hasInstall: { base: 31, finetuned: 87 },
  hasUsage: { base: 24, finetuned: 91 },
  avgCodeBlocks: { base: 0.4, finetuned: 3.2 },
  avgLength: { base: 189, finetuned: 1247 },
}
