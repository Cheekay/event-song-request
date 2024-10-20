function updateSortOrder() {
    const sortSelect = document.getElementById('sort_select');
    const sortBy = sortSelect.value;
    window.location.href = `/song_list?sort_by=${sortBy}`;
}

function updateSongList() {
    const sortSelect = document.getElementById('sort_select');
    const sortBy = sortSelect.value;
    
    fetch(`/get_song_list?sort_by=${sortBy}`)
        .then(response => response.json())
        .then(songs => {
            const songListElement = document.getElementById('song_list');
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

// Update song list every 30 seconds
setInterval(updateSongList, 30000);
