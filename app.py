# Ensure eventlet monkey patching is done first
import eventlet
eventlet.monkey_patch()

from flask import Flask
import os
from extensions import db, socketio, limiter
from models import SongRequest
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, 
    static_url_path='',
    static_folder='static'
)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "a secret key"
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
    ping_interval=25
)
limiter.init_app(app)

with app.app_context():
    db.create_all()
    import routes

if __name__ == "__main__":
    try:
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
