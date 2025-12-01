# Quorial_SoftwareDev
this is a university project for the course software engineering for language technologies and we aim to provide a chatbot specialized in providing civil society perspective on political issues upon a query 

## Database

- The application uses a local SQLite database. On first run the database is created automatically using the SQL scripts in `flask_quorial/tools/`.
- Default database file: `flask_quorial/instance/flaskauu.sqlite` (this path is configured by the app's `DATABASE` setting).
- The server start script (`run_chat_app.py`) will initialize the database only when the file does not already exist. This prevents accidental loss of data on normal restarts.

### Resetting the database (safe)

1. Stop the server.
2. Back up the existing database file before making changes:

```bash
cp flask_quorial/instance/flaskauu.sqlite flask_quorial/instance/flaskauu.sqlite.bak
```

3. To reset (recreate) the database, remove the current DB file and then start the app — the initialization scripts will run on first start and recreate schema and seed data:

```bash
rm flask_quorial/instance/flaskauu.sqlite
poetry run chat-app
# or: poetry run python run_chat_app.py
```

4. Alternatively, you can call the Flask CLI command that registers with the app (it will also re-run the initialization scripts). Make sure you are running from the project root and the package is importable:

```bash
poetry run flask --app flask_quorial init-db
```

Warning: `init-db` and re-running the schema will drop and re-create tables. Always back up the DB file before resetting to avoid data loss.

If you want an intentional way to force reinitialization in development without manual deletion, let me know and I can add an environment flag (for example `RESET_DB=1`) to `run_chat_app.py` to control that behavior.

### Force reinitialization with environment flag (dev)

You can force the application to back up and recreate the database on startup by setting the `RESET_DB` environment variable. This is useful in development when you want to reset the database quickly while preserving a backup.

```bash
# backup + recreate database on start
RESET_DB=1 poetry run chat-app
# or
RESET_DB=1 poetry run python run_chat_app.py
```

The start script will back up the existing DB to `flask_quorial/instance/flaskauu.sqlite.bak`, remove the original file, and then initialize a new DB with schema and seed data.
