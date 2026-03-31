# Postman Collection Generator - Agent Rules

## Priority

1. User request in current chat
2. Project-level `AGENTS.md` in current workspace
3. This skill defaults

## Non-Negotiable Output Rules

- Output must be valid Postman Collection v2.1.0 JSON.
- Keep request method and endpoint exactly as parsed from source or project rules.
- Never invent unavailable auth tokens. Use profile defaults or variables only.
- If parsing fails for a row, skip that row and report it.

## Project Override Scope

Project `AGENTS.md` may override:

- naming convention for collection and request names
- preferred auth type and token variable
- required default headers
- field extraction regex patterns

Project `AGENTS.md` must not override:

- collection schema version (`v2.1.0`)
- JSON validity requirement

## Temp File Rules

- **NEVER write temp/helper scripts to disk** (`_*.py`, `_*.ps1`, `_check_*.py`, etc.)
- For Python logic: use `python3 -X utf8 -c "..."` inline in Bash
- For file ops: use Read / Edit / Write tools directly
