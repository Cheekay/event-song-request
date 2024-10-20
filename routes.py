from flask import render_template, request, redirect, url_for, jsonify
from app import app, db
from models import SongRequest
from youtubesearchpython import VideosSearch
from sqlalchemy import func

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit_request', methods=['POST'])
def submit_request():
    song_title = request.form['song_title']
    artist_name = request.form['artist_name']
    username = request.form['username']

    # Search for the song on YouTube
    search_query = f"{song_title} {artist_name}"
    videos_search = VideosSearch(search_query, limit=1)
    results = videos_search.result()

    if results['result']:
        song_title = results['result'][0]['title']
        artist_name = results['result'][0]['channel']['name']

        # Check if the song already exists in the database
        existing_request = SongRequest.query.filter_by(song_title=song_title, artist_name=artist_name).first()

        if existing_request:
            existing_request.count += 1
            existing_request.timestamp = func.now()
        else:
            new_request = SongRequest(song_title=song_title, artist_name=artist_name, username=username)
            db.session.add(new_request)

        db.session.commit()

        return redirect(url_for('song_list'))
    else:
        return "Song not found", 404

@app.route('/song_list')
def song_list():
    sort_by = request.args.get('sort_by', 'count')
    if sort_by == 'count':
        songs = SongRequest.query.order_by(SongRequest.count.desc()).all()
    else:
        songs = SongRequest.query.order_by(SongRequest.timestamp.desc()).all()
    return render_template('song_list.html', songs=songs, sort_by=sort_by)

@app.route('/get_song_list')
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
