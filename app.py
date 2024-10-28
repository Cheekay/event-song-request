# Ensure eventlet monkey patching is done first
import eventlet
eventlet.monkey_patch()

from flask import Flask
import os
from extensions import db, socketio, limiter
from models import SongRequest
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add file handler for persistent logging
if not os.path.exists('logs'):
    os.makedirs('logs')
file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)

app = Flask(__name__, 
    static_url_path='',
    static_folder='static'
)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or os.urandom(24)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///song_requests.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize extensions
db.init_app(app)
socketio.init_app(app, 
    async_mode='eventlet',
    cors_allowed_origins='*',
    logger=True,
    engineio_logger=True,
    ping_timeout=20,
    ping_interval=25,
    max_http_buffer_size=1024 * 1024,
    reconnection=True,
    reconnection_attempts=5,
    reconnection_delay=1000,
    reconnection_delay_max=5000
)
limiter.init_app(app)

# Register error handlers
@app.errorhandler(500)
def internal_error(error):
    logger.error(f'Server Error: {error}')
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(404)
def not_found_error(error):
    logger.error(f'Not Found Error: {error}')
    return jsonify({'error': 'Resource not found'}), 404

with app.app_context():
    try:
        db.create_all()
        logger.info('Database tables created successfully')
    except Exception as e:
        logger.error(f'Error creating database tables: {e}')
        raise
    import routes

if __name__ == "__main__":
    try:
        logger.info('Starting Flask application...')
        socketio.run(app,
            host="0.0.0.0",
            port=5000,
            debug=True,
            use_reloader=True,
            log_output=True
        )
    except Exception as e:
        logger.error(f"Failed to start the server: {str(e)}")
        raise
