# Codex Workflow Rules

## Project Context
- Backend: FastAPI
- Database: SQLite3
- Python environment: .venv (must be used for all commands)

---

## Branching Rules
- Always create a new branch before making changes
- Branch format:
  - feature/<short-description>
  - fix/<short-description>
  - refactor/<short-description>
- Base branch: master (or main if master does not exist)

---

## Development Workflow
When implementing a change:

1. Create a new branch
2. Make code changes
3. Run tests:
   python -m pytest

4. If tests fail:
   - Fix issues before proceeding

---

## Environment Rules
- NEVER use sudo or apt-get
- ALWAYS use the virtual environment:
  source .venv/bin/activate

- Install dependencies with:
  pip install -r requirements.txt

---

## Database Rules (SQLite)
- Use sqlite3-compatible queries only
- Avoid database-specific features from other engines
- Ensure migrations or schema changes are safe

---

## Commit Workflow
Before committing:

- Ask the user:
  "Do you want to commit these changes?"

If user approves:

1. Stage all changes:
   git add .

2. Generate a structured commit message:

Format:
<type>: <short summary>

- What was added/changed
- Key files affected
- Any important notes

Types:
- feat
- fix
- refactor
- test
- chore

---

## After Commit
- Ask:
  "Do you want to push this branch?"

If yes:
  git push -u origin <branch-name>

---

## Code Quality
- Keep functions small and readable
- Add docstrings where helpful
- Prefer clarity over cleverness

---

## Safety Rules
- Do not delete files unless necessary
- Do not modify .env or secrets
- Do not run destructive commands

---

## Goal
Act like a careful junior engineer:
- Make safe, incremental changes
- Validate with tests
- Ask before committing or pushing