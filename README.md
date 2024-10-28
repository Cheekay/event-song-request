# Event Song Request

A Flask-based web application that allows event guests to request songs and DJs to manage the playlist in real-time. The application features a user-friendly interface with WebSocket support for live updates and YouTube integration for song search.

## Features

- Real-time song request submission and playlist updates using WebSockets
- YouTube API integration for song search suggestions
- DJ interface for playlist management
- Rate limiting to prevent API abuse
- Timezone support for accurate timestamp display
- Dark theme UI using Bootstrap

## Technology Stack

- Python 3.11
- Flask
- SQLite
- WebSocket (Flask-SocketIO)
- YouTube Search Python
- Bootstrap 5

## Setup and Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   - `YOUTUBE_API_KEY`: YouTube Data API key
   - `FLASK_SECRET_KEY`: Secret key for Flask sessions

4. Run the application:
   ```bash
   python main.py
   ```

## Usage

### For Event Guests
1. Visit the homepage to submit song requests
2. Enter song title, artist name, and your name
3. Use the search suggestions to find the correct song
4. Submit your request

### For DJs
1. Access the DJ interface at `/dj_interface`
2. View all requested songs sorted by popularity or timestamp
3. Remove individual songs or clear the entire playlist
4. Monitor real-time updates as new requests come in

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
