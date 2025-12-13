from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort

from flask_quorial.auth import login_required
from flask_quorial.db import get_db

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    # If user is logged in, redirect to chat
    if g.user is not None:
        return redirect(url_for('chat.index'))
    # If not logged in, redirect to login page
    return redirect(url_for('auth.login'))
