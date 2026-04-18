---
name: generate-postman-collection
description: Generate Postman collection JSON from project-specific API test case templates (CSV/JSON) using configurable field mapping profiles. Use when user asks to export API test cases to Postman, convert spreadsheet or test case files to Postman, or support multiple project formats without hardcoding.
---

# Postman Collection Generator

Generate a Postman Collection v2.1.0 from CSV or JSON input with a template-agnostic profile.

## Core Idea

- Do not hardcode per-project column names in code.
- Normalize each project template through a profile JSON.
- Keep generation logic stable and only adjust profile for each project.

## Required Scripts

- `scripts/build_profile.py`
  - Detects likely field mapping from a sample template file.
  - Outputs a profile JSON that can be edited for project-specific rules.
- `scripts/generate_postman_collection.py`
  - Reads input file + profile.
  - Converts rows to canonical test cases.
  - Outputs a `.postman_collection.json` file.

## ⛔ Temp File Rules

**NEVER** write helper/temp script files to disk (`_*.py`, `_*.ps1`, `_check_*.py`, etc.). Use `python3 -X utf8 -c "..."` inline in Bash, or use Read/Edit/Write tools directly.

---

## Workflow

### Step 0: Bootstrap Request Signature (Mandatory)

Before full conversion, inspect the first 5-10 valid test cases to infer a base request pattern:

- method and endpoint
- default headers
- base body template
- cURL/raw request style if present in `PreConditions` or `Details`

This prevents wrong parsing when the template stores request details in mixed text blocks.

### Request Reconstruction Strategy

- Prefer full request baseline from cURL blocks when available.
- Supported cURL extraction:
  - method, endpoint, headers
  - query from URL and `--data-urlencode`/`-G`
  - raw JSON body (`-d`, `--data-raw`, `--data-binary`)
  - `form-data` (`-F/--form`) including file entries (`@file`)
  - `x-www-form-urlencoded` body (`--data-urlencode` for non-GET)
- Apply `Step` mutations on top of the baseline request:
  - replace key values (query/body/form fields)
  - remove keys with phrases like `xoa` / `khong truyen` / ...

### Step 1: Build profile from a sample file

Run:

```bash
python3 scripts/build_profile.py --input <sample.csv|sample.json> --output data/profiles/<project>.json
```

Or build directly from Google Sheet URL:

```bash
python3 scripts/build_profile.py \
  --sheet-url "https://docs.google.com/spreadsheets/d/<SPREADSHEET_ID>/edit#gid=<GID>" \
  --sheet-name "<Tab Name>" \
  --output data/profiles/<project>.json
```

Then review and edit:

- `aliases` for column mapping
- `defaults` for missing values
- `regex_extractors` when method/endpoint/body is embedded in text fields
- `row_filters` to remove suite headers/metadata rows
- `bootstrap` to control initial sample size for request signature inference

### Step 2: Generate collection

Run:

```bash
python3 scripts/generate_postman_collection.py \
  --input <test-cases.csv|test-cases.json> \
  --output <collection.postman_collection.json> \
  --profile data/profiles/<project>.json \
  --collection-name "<Project API Collection>"
```

Generate directly from Google Sheet URL:

```bash
python3 scripts/generate_postman_collection.py \
  --sheet-url "https://docs.google.com/spreadsheets/d/<SPREADSHEET_ID>/edit#gid=<GID>" \
  --sheet-name "<Tab Name>" \
  --output <collection.postman_collection.json> \
  --profile data/profiles/<project>.json \
  --collection-name "<Project API Collection>"
```

## Input Support

- CSV with headers
- JSON list of objects
- JSON object containing one list value (`items`, `rows`, etc.)
- Google Sheet URL (`docs.google.com/spreadsheets/...`) with OAuth Desktop authentication

## Google Auth

- Reuses shared `google_auth.py` from installed `generate-test-case-api` or `generate-test-case-frontend` skill.
- Optional credentials override:
  - `--credentials /path/to/credentials.json`
- First run may open browser for OAuth consent.

## Profile Rules

Profile file structure and options are documented in:

- `references/profile-schema.md`

Default profile template:

- `data/profiles/default.json`

## Fallback Behavior

- If profile is missing field aliases, script uses default aliases.
- If method/endpoint columns are missing, script attempts regex extraction from text fields.
- If headers/body cannot be parsed as JSON, script falls back to plain text raw body and key-value headers.
- Query params are only extracted from `Step` when a clear `Params` marker exists (to avoid false positives).
  - Disable this behavior by setting `query_parsing.from_step_when_get = false` in profile.

## Validation

The generation script runs automated verification immediately after writing the output file.

**Automated checks (built into `generate_postman_collection.py`):**

| Check | What it verifies |
|---|---|
| Schema version | `info.schema` contains `v2.1.0` |
| Item count | `collection.item` count == expected test case count |
| Flat structure | No item contains a nested `item[]` (no folders) |
| ID presence | Every test case ID appears as a request name |
| Method accuracy | Each request method matches the source test case |
| Endpoint in URL | `url.raw` contains the test case endpoint path |
| Auth block | Each request has an `auth` object |
| Status assertion | Each test event includes `pm.response.to.have.status(...)` |

**Exit behavior:**

- Exit code `0` — verification passed, collection is complete and correct.
- Exit code `1` — one or more checks failed; issues are logged as `ERROR` lines before the process exits.

**When verification fails:**

1. Read the `ERROR` lines — each one names the test case ID and the exact mismatch.
2. Fix the profile (wrong alias, bad regex extractor, missing `base_url_variable`) or the input data.
3. Re-run generation. Verification re-runs automatically.

**Post-generation spot-checks (manual, in Postman UI):**

- Auth token variable matches environment variable name.
- Body mode (`raw` / `formdata` / `urlencoded`) is correct for the API type.
- Query params appear in the URL for GET requests.
