# Repository Guidelines

## Project Overview

This repository serves as a working directory. The project is initialized and ready for development.

## Project Structure

```
/Users/rudlord/ORGANIZED/TRADING/COPYSNIPIN/
├── AGENTS.md              # This file — AI agent contributor guidelines
├── README.md              # Project documentation (to be created)
├── .gitignore             # Git ignore patterns
├── src/                   # Source code (to be organized)
├── tests/                 # Test files (to be organized)
└── docs/                  # Documentation (to be created)
```

## Build, Test, and Development Commands

| Command | Description |
|---------|-------------|
| `python3 -m pytest` | Run test suite |
| `python3 -m mypy src/` | Run type checking |
| `python3 -m ruff check .` | Run linting with ruff |
| `python3 -m ruff format .` | Auto-format code |

## Coding Style

- **Indentation**: 4 spaces (no tabs)
- **Line length**: 88 characters (ruff default)
- **Type hints**: Use full type annotations for function signatures
- **Naming**:
  - Modules/functions: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_SNAKE_CASE`
- **Formatting**: Auto-format with `ruff format` before committing

## Testing Guidelines

- Place tests in `tests/` directory mirroring `src/` structure
- Name test files `test_<module>.py`
- Use `pytest` as the test runner
- Aim for meaningful assertions over trivial checks

## Git Workflow

### Commits

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

Examples:
```
feat(auth): add login endpoint
fix(api): handle nil pointer in user lookup
docs(readme): update installation steps
```

### Pull Requests

- Provide a clear description of changes
- Link related issues (e.g., "Closes #123")
- Ensure all checks pass before requesting review
- Squash-merge is preferred for clean history

## Environment Setup

- **Python**: 3.13+
- **Dependency management**: `pip` or `uv`
- **Install dependencies**: `pip install -r requirements.txt` (when created)

## Agent-Specific Instructions

When making changes:

1. Prefer small, focused commits over large sweeping changes
2. Run linting and type checks before committing
3. Never commit secrets, API keys, or credentials
4. Update this file if project conventions change
