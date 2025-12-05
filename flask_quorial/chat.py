# chat.py
# Chat functionality for Flask application

#import json
import os
import sys
from io import BytesIO
import textwrap
#from datetime import datetime
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify,
    send_file
)
from flask_quorial.db import get_db
from flask_quorial.auth import login_required
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Add the src directory to Python path for imports
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Import the full RAG pipeline
try:
    from src.rag_pipeline import complete_rag_pipeline
except ImportError:
    def complete_rag_pipeline(*_args, **_kwargs):  # type: ignore
        raise RuntimeError(
            "RAG pipeline is not available. Verify that src/ is on the PYTHONPATH."
        )

bp = Blueprint('chat', __name__, url_prefix='/chat')

def generate_rag_response(user_message: str) -> str:
    """Send the query + retrieved passages to the Mistral LLM for final answers."""

    mistral_key = os.environ.get("MISTRAL_API_KEY")
    if not mistral_key:
        return (
            "Mistral API key missing. Set the MISTRAL_API_KEY environment variable "
            "before using the chat assistant."
        )

    mistral_model = os.environ.get("MISTRAL_MODEL", "mistral-small-latest")

    try:
        rag_result = complete_rag_pipeline(
            query=user_message,
            api_key=mistral_key,
            provider="mistral",
            model=mistral_model,
            top_k=8,
            context_window=2,
            max_articles=2,
            where=None,
        )
    except Exception as exc:
        print(f"Error in RAG pipeline: {exc}")
        return "I encountered an error while generating an answer with the knowledge base."

    answer = (rag_result or {}).get("answer")
    if not answer:
        return "I could not generate an answer from the retrieved articles."

    sources = rag_result.get("sources") or []
    if not sources:
        return answer

    source_lines = ["Sources:"]
    for src in sources:
        idx = src.get("source_index")
        title = src.get("title") or "Untitled"
        article_id = src.get("article_id") or "N/A"
        score = src.get("score")
        score_text = f", score={score:.3f}" if isinstance(score, (int, float)) else ""
        source_lines.append(f"[Source {idx}] {title} (article_id={article_id}{score_text})")

    return f"{answer}\n\n" + "\n".join(source_lines)

@bp.route('/')
@login_required
def index():
    """Chat interface main page"""
    return render_template('chat/index.html')

@bp.route('/sessions')
@login_required
def get_sessions():
    """Get all chat sessions for the current user"""
    db = get_db()
    sessions = db.execute(
        'SELECT id, title, created_at, updated_at FROM chat_sessions '
        'WHERE user_id = ? ORDER BY updated_at DESC',
        (g.user['id'],)
    ).fetchall()
    
    return jsonify([{
        'id': session['id'],
        'title': session['title'],
        'created_at': session['created_at'],
        'updated_at': session['updated_at']
    } for session in sessions])

@bp.route('/session/<int:session_id>')
@login_required
def get_session(session_id):
    """Get messages from a specific chat session"""
    db = get_db()
    
    # Verify session belongs to current user
    session_check = db.execute(
        'SELECT id FROM chat_sessions WHERE id = ? AND user_id = ?',
        (session_id, g.user['id'])
    ).fetchone()
    
    if session_check is None:
        return jsonify({'error': 'Session not found'}), 404
    
    messages = db.execute(
        'SELECT id, message, is_user, timestamp FROM chat_messages '
        'WHERE session_id = ? ORDER BY timestamp ASC',
        (session_id,)
    ).fetchall()
    
    return jsonify([{
        'id': msg['id'],
        'message': msg['message'],
        'is_user': bool(msg['is_user']),
        'timestamp': msg['timestamp']
    } for msg in messages])

@bp.route('/session/<int:session_id>/export', methods=['GET'])
@login_required
def export_session_pdf(session_id):
    """Export an individual chat session as a downloadable PDF."""
    db = get_db()

    session_row = db.execute(
        'SELECT title, created_at, updated_at FROM chat_sessions '
        'WHERE id = ? AND user_id = ?',
        (session_id, g.user['id'])
    ).fetchone()

    if session_row is None:
        return jsonify({'error': 'Session not found'}), 404

    messages = db.execute(
        'SELECT message, is_user, timestamp FROM chat_messages '
        'WHERE session_id = ? ORDER BY timestamp ASC',
        (session_id,)
    ).fetchall()

    pdf_buffer = BytesIO()
    pdf = canvas.Canvas(pdf_buffer, pagesize=letter)
    width, height = letter
    margin = 50
    line_height = 16
    text_width = 90  # characters per line for wrapping

    pdf.setTitle(f"Chat Export - {session_row['title']}")

    def ensure_space(current_y: float) -> float:
        """Start a new page if there's not enough room for another line."""
        if current_y <= margin:
            pdf.showPage()
            pdf.setFont('Helvetica', 10)
            return height - margin
        return current_y

    y = height - margin
    pdf.setFont('Helvetica-Bold', 16)
    pdf.drawString(margin, y, 'Quorial Chat Export')
    y -= line_height * 1.5
    pdf.setFont('Helvetica', 11)
    pdf.drawString(margin, y, f"Session: {session_row['title']}")
    y -= line_height
    pdf.drawString(margin, y, f"Created: {session_row['created_at']}")
    y -= line_height
    pdf.drawString(margin, y, f"Last updated: {session_row['updated_at']}")
    y -= line_height * 1.5
    pdf.setFont('Helvetica', 10)

    if not messages:
        y = ensure_space(y)
        pdf.drawString(margin, y, 'No messages in this chat session yet.')
    else:
        for message in messages:
            role = 'You' if message['is_user'] else 'Quorial'
            entry = f"[{message['timestamp']}] {role}: {message['message']}"
            lines = textwrap.wrap(entry, width=text_width) or ['']

            for line in lines:
                y = ensure_space(y)
                pdf.drawString(margin, y, line)
                y -= line_height

            y -= line_height / 2

    pdf.save()
    pdf_buffer.seek(0)

    filename = f"chat-session-{session_id}.pdf"
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )

@bp.route('/session', methods=['POST'])
@login_required
def create_session():
    """Create a new chat session"""
    data = request.get_json()
    title = data.get('title', 'New Chat')
    
    db = get_db()
    cursor = db.execute(
        'INSERT INTO chat_sessions (user_id, title) VALUES (?, ?)',
        (g.user['id'], title)
    )
    db.commit()
    
    session_id = cursor.lastrowid
    return jsonify({'session_id': session_id, 'title': title})

@bp.route('/session/<int:session_id>/message', methods=['POST'])
@login_required
def send_message(session_id):
    """Send a message to a chat session"""
    db = get_db()
    
    # Verify session belongs to current user
    session_check = db.execute(
        'SELECT id FROM chat_sessions WHERE id = ? AND user_id = ?',
        (session_id, g.user['id'])
    ).fetchone()
    
    if session_check is None:
        return jsonify({'error': 'Session not found'}), 404
    
    data = request.get_json()
    message = data.get('message', '').strip()
    
    if not message:
        return jsonify({'error': 'Message cannot be empty'}), 400
    
    # Add user message
    db.execute(
        'INSERT INTO chat_messages (session_id, message, is_user) VALUES (?, ?, ?)',
        (session_id, message, True)
    )
    
    # Generate AI response using RAG pipeline
    ai_response = generate_rag_response(message)
    
    # Add AI response
    db.execute(
        'INSERT INTO chat_messages (session_id, message, is_user) VALUES (?, ?, ?)',
        (session_id, ai_response, False)
    )
    
    # Update session timestamp
    db.execute(
        'UPDATE chat_sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?',
        (session_id,)
    )
    
    db.commit()
    
    return jsonify({
        'user_message': message,
        'ai_response': ai_response
    })

@bp.route('/session/<int:session_id>/delete', methods=['DELETE'])
@login_required
def delete_session(session_id):
    """Delete a chat session"""
    db = get_db()
    
    # Verify session belongs to current user
    session_check = db.execute(
        'SELECT id FROM chat_sessions WHERE id = ? AND user_id = ?',
        (session_id, g.user['id'])
    ).fetchone()
    
    if session_check is None:
        return jsonify({'error': 'Session not found'}), 404
    
    db.execute('DELETE FROM chat_sessions WHERE id = ?', (session_id,))
    db.commit()
    
    return jsonify({'success': True})

@bp.route('/session/<int:session_id>/rename', methods=['PUT'])
@login_required
def rename_session(session_id):
    """Rename a chat session"""
    db = get_db()
    
    # Verify session belongs to current user
    session_check = db.execute(
        'SELECT id FROM chat_sessions WHERE id = ? AND user_id = ?',
        (session_id, g.user['id'])
    ).fetchone()
    
    if session_check is None:
        return jsonify({'error': 'Session not found'}), 404
    
    data = request.get_json()
    new_title = data.get('title', '').strip()
    
    if not new_title:
        return jsonify({'error': 'Title cannot be empty'}), 400
    
    db.execute(
        'UPDATE chat_sessions SET title = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
        (new_title, session_id)
    )
    db.commit()
    
    return jsonify({'success': True, 'title': new_title})
