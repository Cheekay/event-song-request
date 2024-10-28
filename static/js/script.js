document.addEventListener('DOMContentLoaded', function() {
    const sortSelect = document.getElementById('sort_select');
    if (sortSelect) {
        sortSelect.addEventListener('change', updateSortOrder);
    }

    // If we're on the song list page, set up WebSocket connection
    if (document.getElementById('song_list')) {
        setupWebSocket();
        updateSongList();
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
        console.error('WebSocket connection error:', error);
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
}

function updateSortOrder() {
    const sortSelect = document.getElementById('sort_select');
    if (sortSelect) {
        const sortBy = sortSelect.value;
        window.location.href = `/song_list?sort_by=${sortBy}`;
    }
}

function updateSongList() {
    const songListElement = document.getElementById('song_list');
    if (!songListElement) return;

    const sortSelect = document.getElementById('sort_select');
    const sortBy = sortSelect ? sortSelect.value : 'count';
    const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    
    fetch(`/get_song_list?sort_by=${sortBy}&timezone=${encodeURIComponent(userTimezone)}`)
        .then(response => {
            if (!response.ok) {
                if (response.status === 429) {
                    throw new Error('Rate limit exceeded. Please wait a moment before refreshing.');
                }
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(songs => {
            songListElement.innerHTML = '';
            if (!Array.isArray(songs)) {
                throw new Error('Invalid response format');
            }
            
            songs.forEach(song => {
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
        })
        .catch(error => {
            console.warn('Error updating song list:', error);
            songListElement.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center text-danger">
                        ${error.message || 'Failed to update song list. Please try again later.'}
                    </td>
                </tr>
            `;
        });
}

// Utility function to prevent XSS
function escapeHtml(unsafe) {
    if (typeof unsafe !== 'string') return '';
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
