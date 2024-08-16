document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const messageInput = document.querySelector('#messageInput');
    const chatBox = document.querySelector('.chat-box');

    form.addEventListener('submit', function(event) {
        event.preventDefault();
        const userMessage = messageInput.value;

        if (userMessage.trim() === '') return;

        chatBox.innerHTML += `<p><strong>Você:</strong> ${userMessage}</p>`;
        messageInput.value = '';

        fetch('/api/message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: userMessage })
        })
        .then(response => response.json())
        .then(data => {
            chatBox.innerHTML += `<p><strong>Gemini:</strong> ${data.response}</p>`;
        })
        .catch(error => {
            console.error('Erro:', error);
        });
    });
});
