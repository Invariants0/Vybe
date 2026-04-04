from backend.app import create_app
from backend.app.config import create_tables

app = create_app()

with app.app_context():
    create_tables(safe=True)
    print("Database tables are ready.")
