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

# Import the retriever function
try:
    from src.retriever import retrieve
except ImportError:
    # Fallback if retriever module is not available
    def retrieve(query, top_k=5, context_size=2, where=None):
        return []

bp = Blueprint('chat', __name__, url_prefix='/chat')

def generate_rag_response(user_message: str) -> str:
    """Generate response using semantic search from ChromaDB"""
    try:
        # Use semantic search to find relevant articles
        results = retrieve(
            query=user_message,
            top_k=5,
            context_size=2,
            where=None
        )
        
        if not results:
            return "I couldn't find any relevant information in the knowledge base for your query."
        
        # Format the response with retrieved content
        response_parts = []
        response_parts.append(f"Based on your query about '{user_message}', I found the following relevant information:\n")
        
        for i, result in enumerate(results[:3], 1):  # Show top 3 results
            title = result.get("title", "Unknown Article")
            article_id = result.get("article_id", "N/A")
            score = result.get("score", 0)
            content = result.get("combined_content", "")
            
            # Truncate content if too long
            max_content_length = 300
            if len(content) > max_content_length:
                content = content[:max_content_length] + "..."
            
            response_parts.append(f"\n**{i}. {title}** (ID: {article_id}, Relevance: {score:.3f})")
            if result.get("summary"):
                response_parts.append(f"*Summary: {result.get('summary')}*")
            response_parts.append(f"{content}")
        
        # Add note about search method
        response_parts.append(f"\n\n*Found {len(results)} relevant articles using semantic search.*")
        
        return "\n".join(response_parts)
        
    except Exception as e:
        print(f"Error in semantic search: {e}")
        return f"I encountered an error while searching the knowledge base: {str(e)}"

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
