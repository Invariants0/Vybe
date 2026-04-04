# Database Notes

The application uses PostgreSQL through Peewee's pooled connection support.

Tables:
- `short_urls`: canonical short-link records
- `link_visits`: append-only click analytics

Initialize schema locally:

```powershell
uv run python scripts/init_db.py
```
