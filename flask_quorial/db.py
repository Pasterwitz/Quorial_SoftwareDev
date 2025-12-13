import sqlite3 
import click  # CLI helper to register custom Flask commands.
from flask import current_app, g  # current_app points to the active Flask app; g stores request-scoped data.

def get_db():
        print('get_db(): before db is accessed...', flush=True)  # Trace whenever a DB connection is requested.

        # Lazily create and cache a connection the first time this request needs it.
        if 'db' not in g:
            # Open a connection to the SQLite file specified in the Flask config.
            g.db = sqlite3.connect(
                current_app.config['DATABASE'],
                detect_types=sqlite3.PARSE_DECLTYPES  # Enable automatic conversion of SQLite types to Python types.
            )
            # Configure the connection to return rows as dict-like objects for convenient column access.
            g.db.row_factory = sqlite3.Row

        return g.db  # Reuse the cached connection for the rest of the request.

def close_db(e=None):
    db = g.pop('db', None)  # Remove and retrieve the cached connection, if any.

    # Close the connection to avoid leaking resources.
    if db is not None:
        db.close()

def init_db():
    db = get_db()  # Obtain the shared connection for initialization work.
    print('init_db(): get_db()...', flush=True)  # Log that initialization is underway.

    # Create the schema from the bundled SQL file (path is relative to the Flask package).
    with current_app.open_resource('tools/schema.sql') as f:
        db.executescript(f.read().decode('utf8'))  # Execute the entire schema script at once.
        print('init_db(): schema successfully created...', flush=True)  # Confirm schema creation.

    # Populate the tables with seed data using the second SQL script.
    with current_app.open_resource('tools/db_insertdata.sql') as f:
        db.executescript(f.read().decode('utf8'))  # Insert the initial content bundled with the project.
        print('init_db(): data successfully inserted...', flush=True)  # Confirm data insertion.

@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()  # Run the initialization logic when the CLI command is invoked.
    print('init_db_command(): init_db() done...', flush=True)  # Provide feedback to the terminal user.

def init_app(app):
        app.teardown_appcontext(close_db)  # Register the cleanup hook so connections close after each request.
        app.cli.add_command(init_db_command)  # Make `flask init-db` available via the CLI.
