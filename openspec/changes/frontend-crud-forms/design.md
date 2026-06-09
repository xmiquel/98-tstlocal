# Design: Frontend CRUD Forms

## Technical Approach

Add HTML-form routes with `/html` suffix to `app/main.py` — fully additive to existing JSON endpoints. A shared `form.html` template handles both create (empty) and edit (pre-filled). All form mutations (POST/PUT/DELETE) return the full list page; HTMX extracts and swaps `#strategies-table`. Delete gets a new HTML-specific route returning the list partial, since the JSON endpoint returns 204 with no body.

## Architecture Decisions

| Decision | Choice | Alternatives | Rationale |
|---|---|---|---|
| Route pattern | `/html` suffix | Same route with content-negotiation | Additive — JSON clients and existing tests untouched |
| Delete response | New `DELETE /.../html` route | Reuse JSON `DELETE /...` (204) | 204 has no body for HTMX to swap; HTML route returns list |
| Form template | Single `form.html` (create + edit) | Separate create/edit templates | Identical fields; edit pre-fills from optional `strategy` context |
| Post-mutation response | Full `list.html` page | Dedicated table partial | Simpler — HTMX extracts `#strategies-table` from full HTML |
| Validation | Server-side Pydantic + form re-render | Client-side only | Spec requires server-side validation; re-render shows inline errors |

## Data Flow

```
── CREATE ──
GET /strategies/new → form.html (empty fields)
HTMX POST /strategies/html → Pydantic validate → store.create() → list.html → HTMX swaps #strategies-table
                                    ↓ (on error)
                              form.html with field errors

── EDIT ──
GET /strategies/{id}/edit → store.get() → form.html (pre-filled fields)
HTMX PUT /strategies/{id}/html → Pydantic validate → store.update() → list.html → HTMX swaps #strategies-table
                                      ↓ (on error)
                                form.html with field errors

── DELETE ──
HTMX DELETE /strategies/{id}/html → hx-confirm → store.delete() → list.html → HTMX swaps #strategies-table
```

## Routes

| Method | Path | Returns | Notes |
|---|---|---|---|
| `GET` | `/strategies/new` | `form.html` | Empty form; context: `action="/strategies/html"`, `method="post"` |
| `POST` | `/strategies/html` | `list.html` / `form.html` | 200 (list) on success; 422 (form with errors) on validation failure |
| `GET` | `/strategies/{id}/edit` | `form.html` | Pre-filled via `strategy` context; `action`, `method` for PUT |
| `PUT` | `/strategies/{id}/html` | `list.html` / `form.html` | Same success/error pattern as POST |
| `DELETE` | `/strategies/{id}/html` | `list.html` | Returns list after deletion; 404 raises HTTPException |

## HTMX Interaction Pattern

| Action | HTMX Attribute | Target | Swap | Confirm |
|---|---|---|---|---|
| Submit create | `hx-post="/strategies/html"` | `#strategies-table` | `outerHTML` | — |
| Submit edit | `hx-put="/strategies/{id}/html"` | `#strategies-table` | `outerHTML` | — |
| Delete | `hx-delete="/strategies/{id}/html"` | `#strategies-table` | `outerHTML` | "Delete this strategy?" |

## Template Details

**`form.html`** context:
- `strategy` — optional `Strategy` object (None for create, populated for edit)
- `action` — form post URL (e.g. `/strategies/html` or `/strategies/{id}/html`)
- `method` — `post` or `put` (HTMX supports PUT via `hx-put`)
- `errors` — optional dict of field → error message (re-render on validation failure)

**`list.html`** changes:
- Add `<th>Actions</th>` column header
- Each row: Edit link (`href="/strategies/{id}/edit"`) + Delete button (`hx-delete`, `hx-confirm`, `hx-target="#strategies-table"`, `hx-swap="outerHTML"`)

## Spec Deviation

The spec scenario `DELETE /strategies/{id} via HTMX` targets the JSON endpoint. The design introduces `DELETE /strategies/{id}/html` instead because the JSON endpoint returns 204 (no body), which cannot carry an HTMX-swappable list. The spec will be updated during archive.

## Testing Strategy

| Layer | What | Approach |
|---|---|---|
| Integration | Form renders (create) | `GET /strategies/new` → assert `<form>` in response |
| Integration | Form renders (edit pre-filled) | `GET /strategies/1/edit` → assert pre-filled name value |
| Integration | Create via HTMX | `POST /strategies/html` with valid data → assert 200 + new strategy in response |
| Integration | Edit via HTMX | `PUT /strategies/1/html` → assert updated name in response |
| Integration | Delete via HTMX | `DELETE /strategies/1/html` → assert removed from response list |
| Integration | Validation error | `POST /strategies/html` with empty name → assert 422 + error message |
| Integration | Delete button attributes | Parse `list.html` → assert `hx-delete`, `hx-confirm`, `hx-target` on delete button |

## Migration / Rollout

No migration required. All new routes are additive; existing JSON routes and page tests remain untouched. Rollback: revert `main.py`, delete `form.html`, revert `list.html`.

## Open Questions

- None — all decisions resolved in architecture table above.
