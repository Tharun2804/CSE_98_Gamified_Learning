const items = document.querySelectorAll('.item');
const earthZone = document.getElementById('earth-zone');
const danger = document.getElementById('danger');
const message = document.getElementById('message');

items.forEach(item => {
    item.addEventListener('dragstart', () => {
        item.classList.add('dragging');
    });

    item.addEventListener('dragend', () => {
        item.classList.remove('dragging');
    });
});

earthZone.addEventListener('dragover', e => {
    e.preventDefault();
});

earthZone.addEventListener('drop', () => {
    const draggedItem = document.querySelector('.dragging');

    if (draggedItem.classList.contains('harmful')) {
        danger.style.display = 'block';
        message.textContent = "⚠️ This harms the Earth!";
        message.style.color = "red";
    } else {
        danger.style.display = 'none';
        message.textContent = "🌱 Good job! Earth is safe!";
        message.style.color = "green";
    }
});
