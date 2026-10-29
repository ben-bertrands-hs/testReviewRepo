# Notes service

A small REST API for storing and searching team notes, with file attachments and webhook
notifications.

## Running

```bash
pip install -r requirements.txt
make run
```

The service stores notes in PostgreSQL. Set `DATABASE_URL` before starting it.

## API

| Method | Path | Description |
|---|---|---|
| `POST` | `/login` | Returns a session token |
| `GET` | `/notes?q=&page=` | Search notes |
| `POST` | `/notes` | Create a note |
| `GET` | `/notes/<id>` | Fetch a note |
| `POST` | `/notes/import` | Bulk import notes |
| `GET` | `/notes/export?name=` | Export all notes to a file |
| `GET` | `/attachments/<name>` | Download an attachment |
| `POST` | `/webhooks/register` | Register a webhook |
| `DELETE` | `/admin/notes` | Delete all notes |

## Tests

```bash
pytest
```

## CI

The pipeline definition lives in `ci/github-actions.yml` and is synced into `.github/workflows/` by
the platform team.
