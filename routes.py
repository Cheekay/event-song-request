from flask import render_template, request, redirect, url_for, jsonify
from app import app, db, socketio, limiter
from models import SongRequest
from youtubesearchpython import VideosSearch
from sqlalchemy import func

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit_request', methods=['POST'])
@limiter.limit("5 per minute")
def submit_request():
    song_title = request.form['song_title']
    artist_name = request.form['artist_name']
    username = request.form['username']

    # Check if the song already exists in the database
    existing_request = SongRequest.query.filter_by(song_title=song_title, artist_name=artist_name).first()

    if existing_request:
        existing_request.count += 1
        existing_request.timestamp = func.now()
    else:
        new_request = SongRequest(song_title=song_title, artist_name=artist_name, username=username)
        db.session.add(new_request)

    db.session.commit()

    # Emit a Socket.IO event to update clients
    socketio.emit('song_list_updated')

    return jsonify({'success': True})

@app.route('/get_song_list')
@limiter.limit("10 per minute")
def get_song_list():
    sort_by = request.args.get('sort_by', 'count')
    if sort_by == 'count':
        songs = SongRequest.query.order_by(SongRequest.count.desc()).all()
    else:
        songs = SongRequest.query.order_by(SongRequest.timestamp.desc()).all()
    
    song_list = []
    for song in songs:
        song_list.append({
            'title': song.song_title,
            'artist': song.artist_name,
            'count': song.count,
            'timestamp': song.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return jsonify(song_list)

@app.route('/dj_interface')
def dj_interface():
    songs = SongRequest.query.order_by(SongRequest.count.desc()).all()
    return render_template('dj_interface.html', songs=songs)

@app.route('/remove_song/<int:song_id>', methods=['POST'])
@limiter.limit("10 per minute")
def remove_song(song_id):
    song = SongRequest.query.get_or_404(song_id)
    db.session.delete(song)
    db.session.commit()
    socketio.emit('song_list_updated')
    return jsonify({'success': True})

@app.route('/search_songs')
@limiter.limit("10 per minute")
def search_songs():
    query = request.args.get('query', '')
    videos_search = VideosSearch(query, limit=5)
    results = videos_search.result()
    
    songs = []
    for video in results['result']:
        songs.append({
            'title': video['title'],
            'artist': video['channel']['name']
        })
    
    return jsonify(songs)

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')
