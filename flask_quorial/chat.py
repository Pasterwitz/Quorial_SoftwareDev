# chat.py
# Chat functionality for Flask application

#import json
import os
import sys
#from datetime import datetime
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
from flask_quorial.db import get_db
from flask_quorial.auth import login_required

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
        return {"answer": "I encountered an error while generating an answer with the knowledge base.", "sources": []}

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
    
    # Generate AI response using RAG pipeline (structured output)
    rag_out = generate_rag_response(message)
    ai_response = rag_out.get('answer') if isinstance(rag_out, dict) else str(rag_out)
    sources = rag_out.get('sources') if isinstance(rag_out, dict) else []

    # Add AI response (store only the textual answer)
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
        'ai_response': ai_response,
        'sources': sources,
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
