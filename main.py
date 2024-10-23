from flask import Flask, render_template, request
import socketio
import eventlet
import os
from datetime import datetime
import json

# Initialize Flask app and Socket.IO
app = Flask(__name__,
            static_url_path='',
            static_folder='static',
            template_folder='templates')

sio = socketio.Server(async_mode='eventlet')
app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)

# Store songs in memory (for demonstration)
songs = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dj_interface')
def dj_interface():
    return render_template('dj_interface.html')

@sio.event
def connect(sid, environ):
    print('Client connected:', sid)
    # Send current song list to the newly connected client
    sio.emit('update_songs', songs, room=sid)

@sio.event
def disconnect(sid):
    print('Client disconnected:', sid)

@sio.event
def submit_request(sid, data):
    # Add new song request
    song = {
        'id': len(songs),
        'title': data['songTitle'],
        'artist': data['artistName'],
        'requester': data['requesterName'],
        'requests': 1,
        'lastRequested': datetime.now().strftime('%m-%d %H:%M')
    }
    songs.append(song)
    # Broadcast updated song list to all clients
    sio.emit('update_songs', songs)

@sio.event
def remove_song(sid, data):
    song_id = data['id']
    global songs
    songs = [song for song in songs if song['id'] != song_id]
    sio.emit('update_songs', songs)

@sio.event
def remove_all_songs(sid):
    global songs
    songs = []
    sio.emit('update_songs', songs)

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5000)), app)
