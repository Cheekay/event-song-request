document.addEventListener('DOMContentLoaded', function() {
    const sortSelect = document.getElementById('sort_select');
    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            updateSongList();
        });
    }

    // Set up WebSocket connection and song list if we're on the appropriate page
    if (document.getElementById('song_list')) {
        setupWebSocket();
        updateSongList();
    }

    // Set up search functionality
    const songTitleInput = document.getElementById('song_title');
    if (songTitleInput) {
        songTitleInput.addEventListener('input', debounce(searchSongs, 300));
    }
});

function setupWebSocket() {
    const socket = io({
        reconnection: true,
        reconnectionAttempts: 5,
        reconnectionDelay: 1000,
        reconnectionDelayMax: 5000,
        timeout: 20000
    });

    socket.on('connect', function() {
        console.log('Connected to WebSocket');
    });

    socket.on('connect_error', function(error) {
        console.error('WebSocket connection error:', error.message || 'Connection failed');
    });

    socket.on('reconnect_attempt', function(attemptNumber) {
        console.log(`Attempting to reconnect (${attemptNumber}/5)...`);
    });

    socket.on('song_list_updated', function() {
        updateSongList();
    });

    socket.on('disconnect', function() {
        console.log('Disconnected from WebSocket');
    });

    return socket;
}

function escapeHtml(unsafe) {
    if (typeof unsafe !== 'string') return '';
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

async function updateSongList() {
    const songListElement = document.getElementById('song_list');
    if (!songListElement) return;

    const sortSelect = document.getElementById('sort_select');
    const sortBy = sortSelect ? sortSelect.value : 'count';
    const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    
    try {
        const response = await fetch(`/get_song_list?sort_by=${sortBy}&timezone=${encodeURIComponent(userTimezone)}`);
        if (!response.ok) {
            throw new Error(response.status === 429 ? 
                'Rate limit exceeded. Please wait a moment before refreshing.' : 
                `Failed to fetch song list (Status: ${response.status})`);
        }

        const data = await response.json();
        if (!data) {
            throw new Error('No data received from server');
        }
        
        if (data.error) {
            throw new Error(data.error);
        }

        songListElement.innerHTML = '';
        data.forEach(song => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${escapeHtml(song.title)}</td>
                <td>${escapeHtml(song.artist)}</td>
                <td>${escapeHtml(song.username)}</td>
                <td>${song.count}</td>
                <td>${escapeHtml(song.timestamp)}</td>
            `;
            songListElement.appendChild(row);
        });
    } catch (error) {
        const errorMessage = error.message || 'Failed to update song list. Please try again.';
        console.error('Error updating song list:', errorMessage);
        songListElement.innerHTML = `
            <tr>
                <td colspan="5" class="text-center text-danger">
                    ${errorMessage}
                </td>
            </tr>
        `;
    }
}

async function searchSongs() {
    const query = document.getElementById('song_title').value;
    const suggestionsElement = document.getElementById('song_suggestions');
    
    if (!query || query.length < 3) {
        suggestionsElement.innerHTML = '';
        return;
    }

    try {
        const response = await fetch(`/search_songs?query=${encodeURIComponent(query)}`);
        if (!response.ok) {
            throw new Error(response.status === 429 ? 
                'Too many search requests. Please wait a moment.' : 
                `Failed to search songs (Status: ${response.status})`);
        }

        const data = await response.json();
        if (!data) {
            throw new Error('No data received from server');
        }

        suggestionsElement.innerHTML = '';
        if (!Array.isArray(data)) {
            throw new Error('Invalid response format from server');
        }

        if (data.length === 0) {
            suggestionsElement.innerHTML = `
                <div class="list-group-item text-muted">
                    No songs found matching your search
                </div>
            `;
            return;
        }

        data.forEach(song => {
            const item = document.createElement('a');
            item.href = '#';
            item.classList.add('list-group-item', 'list-group-item-action');
            item.textContent = `${song.title} - ${song.artist}`;
            item.addEventListener('click', (e) => {
                e.preventDefault();
                document.getElementById('song_title').value = song.title;
                document.getElementById('artist_name').value = song.artist;
                suggestionsElement.innerHTML = '';
            });
            suggestionsElement.appendChild(item);
        });
    } catch (error) {
        const errorMessage = error.message || 'Failed to search songs. Please try again.';
        console.error('Error searching songs:', errorMessage);
        suggestionsElement.innerHTML = `
            <div class="list-group-item list-group-item-danger">
                ${errorMessage}
            </div>
        `;
    }
}

function debounce(func, delay) {
    let timeoutId;
    return function() {
        const context = this;
        const args = arguments;
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(context, args), delay);
    };
}
