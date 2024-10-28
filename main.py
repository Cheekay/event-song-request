# Ensure eventlet monkey patching is done first
import eventlet
eventlet.monkey_patch()

# Now we can safely import the rest
from app import app, socketio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
