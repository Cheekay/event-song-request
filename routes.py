from flask import render_template, request, redirect, url_for, jsonify, session
from extensions import db, socketio, limiter
from models import SongRequest
from app import app
from youtubesearchpython import VideosSearch
from sqlalchemy import func
import pytz
from datetime import datetime
import logging
import os

# Configure logging
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit_request', methods=['POST'])
@limiter.limit("5 per minute")
def submit_request():
    song_title = request.form['song_title']
    artist_name = request.form['artist_name']
    username = request.form['username']

    existing_request = SongRequest.query.filter_by(song_title=song_title, artist_name=artist_name).first()

    if existing_request:
        existing_request.count += 1
        existing_request.timestamp = func.now()
    else:
        new_request = SongRequest(
            song_title=song_title,
            artist_name=artist_name,
            username=username
        )
        db.session.add(new_request)

    try:
        db.session.commit()
        socketio.emit('song_list_updated')
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error submitting request: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Database error'}), 500

@app.route('/get_song_list')
@limiter.limit("10 per minute")
def get_song_list():
    sort_by = request.args.get('sort_by', 'count')
    user_timezone = request.args.get('timezone', 'UTC')
    
    try:
        pytz.timezone(user_timezone)
    except pytz.exceptions.UnknownTimeZoneError:
        user_timezone = 'UTC'

    try:
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
    except Exception as e:
        logger.error(f"Error getting song list: {str(e)}")
        return jsonify([])

@app.route('/dj_interface')
def dj_interface():
    try:
        songs = SongRequest.query.order_by(SongRequest.count.desc()).all()
        return render_template('dj_interface.html', songs=songs)
    except Exception as e:
        logger.error(f"Error loading DJ interface: {str(e)}")
        return render_template('dj_interface.html', songs=[])

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
        logger.error(f"Error removing song: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/remove_all_songs', methods=['POST'])
@limiter.limit("5 per minute")
def remove_all_songs():
    try:
        num_deleted = db.session.query(SongRequest).delete()
        db.session.commit()
        socketio.emit('song_list_updated')
        return jsonify({'success': True, 'songs_removed': num_deleted})
    except Exception as e:
        logger.error(f"Error removing all songs: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/search_songs')
@limiter.limit("10 per minute")
def search_songs():
    try:
        query = request.args.get('query', '')
        if not query or len(query.strip()) < 3:
            return jsonify([])

        api_key = os.environ.get('YOUTUBE_API_KEY')
        if not api_key:
            logger.error("YouTube API key not found in environment variables")
            return jsonify({'error': 'API configuration error'}), 500

        # Validate API key format
        if not isinstance(api_key, str) or len(api_key.strip()) < 10:
            logger.error("Invalid YouTube API key format")
            return jsonify({'error': 'Invalid API configuration'}), 500

        try:
            videos_search = VideosSearch(query, limit=5)
            results = videos_search.result()
            
            if not results:
                logger.error("Empty response from YouTube search")
                return jsonify([])

            if not isinstance(results, dict):
                logger.error(f"Unexpected response type from YouTube search: {type(results)}")
                return jsonify([])

            if 'result' not in results:
                logger.error("Missing 'result' key in YouTube search response")
                return jsonify([])
            
            songs = []
            for video in results.get('result', []):
                try:
                    title = video.get('title', '').strip()
                    channel = video.get('channel', {})
                    artist = channel.get('name', '').strip() if isinstance(channel, dict) else ''
                    
                    if title and artist:
                        songs.append({
                            'title': title,
                            'artist': artist
                        })
                except (KeyError, AttributeError) as e:
                    logger.error(f"Error parsing video data: {str(e)}")
                    continue
            
            if not songs:
                logger.warning("No valid songs found in search results")
                return jsonify([])

            return jsonify(songs)
        except Exception as e:
            logger.error(f"YouTube search error: {str(e)}")
            return jsonify({'error': 'Search service unavailable'}), 503

    except Exception as e:
        logger.error(f"Unexpected error in search_songs: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@socketio.on('connect')
def handle_connect():
    logger.info('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    logger.info('Client disconnected')

@socketio.on_error()
def error_handler(e):
    logger.error(f'SocketIO error: {str(e)}')
