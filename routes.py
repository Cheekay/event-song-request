from flask import render_template, request, redirect, url_for, jsonify, session
from extensions import db, socketio, limiter
from models import SongRequest
from app import app
from youtubesearchpython import VideosSearch
from sqlalchemy import func
import pytz
from datetime import datetime
import logging
from flask_limiter.errors import RateLimitExceeded

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit_request', methods=['POST'])
@limiter.limit("5 per minute")
def submit_request():
    try:
        song_title = request.form['song_title']
        artist_name = request.form['artist_name']
        username = request.form['username']

        existing_request = SongRequest.query.filter_by(song_title=song_title, artist_name=artist_name).first()

        if existing_request:
            existing_request.count += 1
            existing_request.timestamp = func.now()
        else:
            new_request = SongRequest(song_title=song_title, artist_name=artist_name, username=username)
            db.session.add(new_request)

        db.session.commit()
        socketio.emit('song_list_updated')
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error in submit_request: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to submit request'}), 500

@app.route('/get_song_list')
@limiter.limit("10 per minute")
def get_song_list():
    try:
        sort_by = request.args.get('sort_by', 'count')
        user_timezone = request.args.get('timezone', 'UTC')
        
        try:
            pytz.timezone(user_timezone)
        except pytz.exceptions.UnknownTimeZoneError:
            logger.warning(f"Invalid timezone received: {user_timezone}")
            user_timezone = 'UTC'

        if sort_by == 'count':
            songs = SongRequest.query.order_by(SongRequest.count.desc()).all()
        else:
            songs = SongRequest.query.order_by(SongRequest.timestamp.desc()).all()
        
        song_list = []
        for song in songs:
            utc_time = song.timestamp.replace(tzinfo=pytz.UTC)
            local_time = utc_time.astimezone(pytz.timezone(user_timezone))
            song_list.append({
                'title': song.song_title,
                'artist': song.artist_name,
                'count': song.count,
                'timestamp': local_time.strftime('%m-%d %H:%M'),
                'username': song.username
            })
        
        return jsonify(song_list)
    except RateLimitExceeded:
        logger.warning(f"Rate limit exceeded for IP: {request.remote_addr}")
        return jsonify({'error': 'Rate limit exceeded. Please wait before trying again.'}), 429
    except Exception as e:
        logger.error(f"Error in get_song_list: {str(e)}")
        return jsonify({'error': 'Failed to fetch song list'}), 500

@app.route('/dj_interface')
def dj_interface():
    try:
        songs = SongRequest.query.order_by(SongRequest.count.desc()).all()
        return render_template('dj_interface.html', songs=songs)
    except Exception as e:
        logger.error(f"Error in dj_interface: {str(e)}")
        return render_template('error.html', error='Failed to load DJ interface'), 500

@app.route('/remove_song/<int:song_id>', methods=['POST'])
@limiter.limit("10 per minute")
def remove_song(song_id):
    try:
        song = SongRequest.query.get_or_404(song_id)
        db.session.delete(song)
        db.session.commit()
        socketio.emit('song_list_updated')
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error in remove_song: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to remove song'}), 500

@app.route('/search_songs')
@limiter.limit("10 per minute")
def search_songs():
    try:
        query = request.args.get('query', '')
        if not query or len(query.strip()) < 3:
            return jsonify([])

        videos_search = VideosSearch(query, limit=5)
        results = videos_search.result()
        
        if not results or 'result' not in results:
            logger.warning(f"No results found for query: {query}")
            return jsonify([])
            
        songs = []
        for video in results['result']:
            songs.append({
                'title': video['title'],
                'artist': video['channel']['name']
            })
        
        return jsonify(songs)
    except RateLimitExceeded:
        logger.warning(f"YouTube search rate limit exceeded for IP: {request.remote_addr}")
        return jsonify({'error': 'Rate limit exceeded. Please wait before searching again.'}), 429
    except Exception as e:
        logger.error(f"Error in YouTube search: {str(e)}")
        return jsonify({'error': 'Failed to search songs. Please try again later.'}), 500

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429

# WebSocket event handlers
@socketio.on('connect')
def handle_connect():
    logger.info(f'Client connected: {request.sid}')

@socketio.on('disconnect')
def handle_disconnect():
    logger.info(f'Client disconnected: {request.sid}')

@socketio.on_error()
def error_handler(e):
    logger.error(f'SocketIO error: {str(e)}')
