# Chat functionality for Flask application

import os
import sys
from io import BytesIO
from xml.sax.saxutils import escape
from flask import (Blueprint, g, render_template, request, jsonify, send_file)
from flask_quorial.db import get_db
from flask_quorial.auth import login_required
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

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

def derive_session_title_from_message(message: str) -> str:
    """Create a concise session title based on the first user question."""
    cleaned = " ".join(message.strip().split())
    if not cleaned:
        return "New Chat"

    words = cleaned.split()
    snippet = " ".join(words[:8])

    # Enforce a hard limit so titles stay tidy in the sidebar
    if len(snippet) > 60:
        snippet = snippet[:57].rstrip() + "..."
    elif len(words) > 8:
        snippet = f"{snippet}..."

    return snippet

def generate_rag_response(user_message: str) -> dict:
    """Send the query + retrieved passages to the Mistral LLM for final answers.

    Returns a dict with keys `answer` (str) and `sources` (list).
    """

    mistral_key = os.environ.get("MISTRAL_API_KEY")
    if not mistral_key:
        return {"answer": (
            "Mistral API key missing. Set the MISTRAL_API_KEY environment variable "
            "before using the chat assistant."), "sources": []}

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
        return {"answer": "I encountered an error (APIKey missing) while generating an answer with the knowledge base.", "sources": []}

    answer = (rag_result or {}).get("answer")
    if not answer:
        return {"answer": "I could not generate an answer from the retrieved articles.", "sources": []}

    sources = rag_result.get("sources") or []
    return {"answer": answer, "sources": sources}

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
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=50,
        bottomMargin=50,
        title=f"Chat Export - {session_row['title']}"
    )

    styles = getSampleStyleSheet()
    title_style = styles['Title']
    metadata_style = ParagraphStyle(
        'Metadata',
        parent=styles['Normal'],
        fontSize=11,
        leading=16,
    )

    bubble_margin = doc.width * 0.15

    user_style = ParagraphStyle(
        'UserMessage',
        parent=styles['BodyText'],
        fontSize=11,
        leading=16,
        textColor=colors.HexColor('#000000'),
        leftIndent=bubble_margin,
        rightIndent=0,
        alignment=TA_RIGHT,
        spaceBefore=8,
        spaceAfter=8,
    )

    ai_style = ParagraphStyle(
        'AIMessage',
        parent=styles['BodyText'],
        fontSize=11,
        leading=16,
        textColor=colors.HexColor('#212529'),
        leftIndent=0,
        rightIndent=bubble_margin,
        alignment=TA_LEFT,
        spaceBefore=8,
        spaceAfter=8,
    )

    story = [
        Paragraph('Quorial Chat Export', title_style),
        Spacer(1, 12),
        Paragraph(f"Session: <b>{escape(session_row['title'])}</b>", metadata_style),
        Paragraph(f"Created: {session_row['created_at']}", metadata_style),
        Spacer(1, 16)
    ]

    if not messages:
        story.append(Paragraph('No messages in this chat session yet.', metadata_style))
    else:
        for message in messages:
            is_user = bool(message['is_user'])
            role = 'You' if is_user else 'Quorial'
            timestamp = message['timestamp']
            escaped_body = escape(message['message'] or '').replace('\n', '<br/>')
            block_html = (
                f"<b>{role}</b>"
                f"<br/><font size=9 color='#6c757d'>{timestamp}</font>"
                f"<br/>{escaped_body}"
            )

            style = user_style if is_user else ai_style
            story.append(Paragraph(block_html, style))
            story.append(Spacer(1, 4))

    doc.build(story)
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

    existing_count_row = db.execute(
        'SELECT COUNT(*) AS cnt FROM chat_messages WHERE session_id = ?',
        (session_id,)
    ).fetchone()
    is_first_user_message = existing_count_row is None or existing_count_row['cnt'] == 0
    
    # Add user message
    db.execute(
        'INSERT INTO chat_messages (session_id, message, is_user) VALUES (?, ?, ?)',
        (session_id, message, True)
    )
    
    # Generate AI response using RAG pipeline (structured output)
    rag_out = generate_rag_response(message)
    ai_response = rag_out.get('answer') if isinstance(rag_out, dict) else str(rag_out)
    sources = rag_out.get('sources') if isinstance(rag_out, dict) else []

    # Add AI response (store only the textual answer)
    db.execute(
        'INSERT INTO chat_messages (session_id, message, is_user) VALUES (?, ?, ?)',
        (session_id, ai_response, False)
    )
    
    session_title = None
    if is_first_user_message:
        session_title = derive_session_title_from_message(message)
        db.execute(
            'UPDATE chat_sessions SET title = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (session_title, session_id)
        )
    else:
        db.execute(
            'UPDATE chat_sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (session_id,)
        )

    db.commit()

    return jsonify({
        'user_message': message,
        'ai_response': ai_response,
        'sources': sources,
        'session_title': session_title,
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
