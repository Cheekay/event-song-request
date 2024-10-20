document.addEventListener('DOMContentLoaded', function() {
    const sortSelect = document.getElementById('sort_select');
    if (sortSelect) {
        sortSelect.addEventListener('change', updateSortOrder);
    }

    // If we're on the song list page, update it every 30 seconds
    if (document.getElementById('song_list')) {
        updateSongList();
        setInterval(updateSongList, 30000);
    }
});

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
