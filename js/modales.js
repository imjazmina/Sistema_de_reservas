function openEditModal(id) {
        document.getElementById('editModal-' + id).classList.remove('hidden');
        document.getElementById('editModal-' + id).classList.add('flex');
    }

function closeEditModal(id) {
    document.getElementById('editModal-' + id).classList.remove('flex');
    document.getElementById('editModal-' + id).classList.add('hidden');
}

