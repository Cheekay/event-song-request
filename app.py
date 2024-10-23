# Ensure eventlet monkey patching is done first
import eventlet
eventlet.monkey_patch()


from flask import Flask
import os
from extensions import db, socketio, limiter
from models import SongRequest

app = Flask(__name__, 
    static_url_path='',
    static_folder='static'
)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "a secret key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///song_requests.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize extensions
db.init_app(app)
socketio.init_app(app, async_mode='eventlet')
limiter.init_app(app)

with app.app_context():
    db.create_all()
    import routes


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
