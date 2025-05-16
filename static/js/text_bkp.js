
const chatSocket = new WebSocket(`ws://${window.location.host}/ws/transcription/`);
const messageInput = document.getElementById('message-input');
const chatMessages = document.getElementById('chat-messages');
const username = document.body.dataset.username;
let lastSentMessage = '';

chatSocket.onmessage = ({data}) => {
    const parsedData = JSON.parse(data);
    if (parsedData.message !== lastSentMessage) {
        addMessage(parsedData.message, 'bot-message');
    }
};

chatSocket.onclose = () => console.error('Chat socket closed unexpectedly');

// Envía un mensaje al socket cuando se presiona Enter
function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;

    const userMessage = `${username}: ${message}`;
    lastSentMessage = userMessage;

    chatSocket.send(JSON.stringify({ message: userMessage }));
    addMessage(userMessage, 'user-message');
    messageInput.value = '';
}

// Crea un nuevo elemento de mensaje y lo agrega al chat
function addMessage(message, className) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${className}`;
    messageDiv.textContent = message;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

messageInput.addEventListener('keypress', e => {
    if (e.key === 'Enter') sendMessage();
});
