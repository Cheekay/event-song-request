# Ensure eventlet monkey patching is done first
import eventlet
eventlet.monkey_patch()

# Now we can safely import the rest
from app import app, socketio

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
