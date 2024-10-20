let socket;

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
    socket = io();

    socket.on('connect', function() {
        console.log('Connected to WebSocket');
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
    
    fetch(`/get_song_list?sort_by=${sortBy}`)
        .then(response => response.json())
        .then(songs => {
            songListElement.innerHTML = '';
            
            songs.forEach(song => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${song.title}</td>
                    <td>${song.artist}</td>
                    <td>${song.count}</td>
                    <td>${song.timestamp}</td>
                `;
                songListElement.appendChild(row);
            });
        });
}
