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

function handleError(error, defaultMessage) {
    if (error.message) {
        return error.message;
    } else if (error.error) {
        return error.error;
    } else {
        return defaultMessage;
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
            if (!Array.isArray(songs)) {
                if (songs.error) {
                    throw new Error(songs.error);
                }
                throw new Error('Invalid response format');
            }
            
            songListElement.innerHTML = '';
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
            console.error('Error updating song list:', handleError(error, 'Failed to update song list'));
            songListElement.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center text-danger">
                        ${handleError(error, 'Failed to update song list. Please try again later.')}
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

// Add search functionality with better error handling
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
                'Failed to search songs');
        }

        const data = await response.json();
        if (data.error) {
            throw new Error(data.error);
        }

        suggestionsElement.innerHTML = '';
        if (Array.isArray(data)) {
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
        }
    } catch (error) {
        console.error('Error searching songs:', handleError(error, 'Failed to search songs'));
        suggestionsElement.innerHTML = `
            <div class="list-group-item list-group-item-danger">
                ${handleError(error, 'Failed to search songs. Please try again.')}
            </div>
        `;
    }
}

// Add debounce function for search
function debounce(func, delay) {
    let timeoutId;
    return function() {
        const context = this;
        const args = arguments;
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(context, args), delay);
    };
}

// Add event listener for search input with debounce
document.addEventListener('DOMContentLoaded', function() {
    const songTitleInput = document.getElementById('song_title');
    if (songTitleInput) {
        songTitleInput.addEventListener('input', debounce(searchSongs, 300));
    }
});
