// All previous content remains the same until line 104
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

// Rest of the file remains the same until line 180
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

// Rest of the file remains the same
