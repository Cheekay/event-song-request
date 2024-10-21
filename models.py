from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class SongRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    song_title = db.Column(db.String(100), nullable=False)
    artist_name = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    count = db.Column(db.Integer, default=1)
    username = db.Column(db.String(64), nullable=False)

    def __repr__(self):
        return f"<SongRequest {self.song_title} by {self.artist_name}>"
