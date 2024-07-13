function sendMessage() {
    const inputBox = document.getElementById('input-box');
    const message = inputBox.value.trim();
    if (message === '') return;
    appendMessage(message, 'user-message');
    inputBox.value = '';
    sendToBot(message);
}

function appendMessage(message, className) {
    const chatBox = document.getElementById('chat-box');
    const messageElement = document.createElement('div');
    messageElement.className = `message ${className}`;
    messageElement.textContent = message;
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function sendToBot(message) {
    fetch('/receive_gratitude', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ gratitude: message })
    })
    .then(response => response.json())
    .then(data => {
        const delay = Math.floor(Math.random() * 1000) + 500; // Random delay between 500ms to 1500ms
        setTimeout(() => {
            appendMessage(data.message, 'bot-message');
        }, delay);
    })
    .catch(error => console.error('Error:', error));
}

document.getElementById('send-button').addEventListener('click', sendMessage);
document.getElementById('input-box').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
});

// Initial daily prompt
fetch('/send_daily_prompt')
    .then(response => response.json())
    .then(data => {
        appendMessage(data.message, 'bot-message');
    })
    .catch(error => console.error('Error:', error));
