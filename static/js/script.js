
document.addEventListener('DOMContentLoaded', function() {
    const socket = io();
    
    socket.on('connect', () => {
        console.log('Connected to WebSocket');
    });

    socket.on('update_songs', (data) => {
        updateSongList(data);
    });

    // Song request form submission
    const songRequestForm = document.getElementById('songRequestForm');
    if (songRequestForm) {
        songRequestForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = {
                songTitle: document.getElementById('songTitle').value,
                artistName: document.getElementById('artistName').value,
                requesterName: document.getElementById('requesterName').value
            };
            socket.emit('submit_request', formData);
            songRequestForm.reset();
        });
    }

    // DJ interface remove buttons
    const removeAllBtn = document.getElementById('removeAllSongs');
    if (removeAllBtn) {
        removeAllBtn.addEventListener('click', function() {
            if (confirm('Are you sure you want to remove all songs?')) {
                socket.emit('remove_all_songs');
            }
        });
    }

    function updateSongList(songs) {
        const songList = document.getElementById('songList') || document.getElementById('djSongList');
        if (!songList) return;

        songList.innerHTML = '';
        songs.forEach(song => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${song.title}</td>
                <td>${song.artist}</td>
                <td>${song.requester}</td>
                <td>${song.requests}</td>
                <td>${song.lastRequested}</td>
            `;
            
            if (document.getElementById('djSongList')) {
                row.innerHTML += `
                    <td>
                        <button class="btn btn-danger btn-sm" onclick="removeSong('${song.id}')">
                            Remove
                        </button>
                    </td>
                `;
            }
            
            songList.appendChild(row);
        });
    }

    window.removeSong = function(songId) {
        socket.emit('remove_song', { id: songId });
    };
});
