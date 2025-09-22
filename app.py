# app.py
from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from database import init_db, create_user, authenticate_user, get_user_by_id, save_message

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_super_secret_key'
socketio = SocketIO(app)

# Initialize the database on startup
init_db()

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('chat'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if create_user(username, email, password):
            return redirect(url_for('login'))
        else:
            return "Registration failed. User may already exist."
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = authenticate_user(username, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('chat'))
        else:
            return "Login failed. Check your username and password."
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/chat')
def chat():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('chat.html', username=session['username'])

# --- Socket.IO Event Handlers ---

@socketio.on('connect')
def handle_connect():
    """Handles a new client connection."""
    if 'user_id' in session:
        # User is logged in, join a private room based on their user ID
        join_room(session['user_id'])
        print(f"User {session['username']} connected and joined room {session['user_id']}")

@socketio.on('disconnect')
def handle_disconnect():
    """Handles a client disconnecting."""
    if 'user_id' in session:
        leave_room(session['user_id'])
        print(f"User {session['username']} disconnected.")

@socketio.on('send_message')
def handle_send_message(data):
    """Handles a new message from a client."""
    if 'user_id' in session:
        sender_id = session['user_id']
        sender_username = session['username']
        recipient_username = data.get('recipient')
        message_content = data.get('message')

        # To simplify, we'll assume a "room" is based on the recipient's username
        # In a real app, you'd find the recipient's ID and use a dedicated chat room ID
        # For a group chat, you'd emit to the whole room.
        
        # Save the message to the database (recipient_id would be looked up here)
        # For simplicity, let's just save a generic message for now
        save_message(sender_id, None, message_content, 'text')

        # Emit the message to the intended recipient's room
        # You would need to get the recipient's user_id from their username
        # For now, we'll just broadcast to all for demonstration
        emit('receive_message', {'sender': sender_username, 'message': message_content}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)