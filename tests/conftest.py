import pytest

from flask_quorial import create_app
from flask_quorial import db


@pytest.fixture
def app(tmp_path):
    """Provide a fresh Flask app (and database) for each test."""
    test_db = tmp_path / "test.sqlite"

    app = create_app({
        "TESTING": True,
        "DATABASE": str(test_db),
    })

    with app.app_context():
        db.init_db()

    yield app
