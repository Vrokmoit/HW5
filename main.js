document.addEventListener('DOMContentLoaded', () => {
    const ws = new WebSocket('ws://localhost:8080');
    const formChat = document.getElementById('formChat');
    const textField = document.getElementById('textField');
    const messagesContainer = document.getElementById('messages');

    formChat.addEventListener('submit', (event) => {
        event.preventDefault();
        const message = textField.value.trim();
        if (message !== '') {
            ws.send(message);
            textField.value = '';
        }
    });

    ws.onopen = () => {
        console.log('WebSocket connection opened');
    };

    ws.onmessage = (event) => {
        console.log('Message received:', event.data);
        const messageElement = document.createElement('div');
        messageElement.textContent = event.data;
        messagesContainer.appendChild(messageElement);
    };

    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
        console.log('WebSocket connection closed');
    };
});
