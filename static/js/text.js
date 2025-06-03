const username = document.body.dataset.username;
const roomid = document.body.dataset.roomid;
const chatMessages = document.getElementById('chat-messages');
var chatSocket;
let lastSentMessage = '';
let recognition;
let isRecognizing = false; // Flag to track recognition state
const conversation = [];

// Speech Recognition Setup
function initializeSpeechRecognition() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.lang = 'es-ES';
        recognition.continuous = true;
        recognition.interimResults = true;

        recognition.onresult = (event) => {
            let interimTranscript = '';
            let finalTranscript = '';
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript;
                } else {
                    interimTranscript += transcript;
                }
            }
            if (finalTranscript) {
                sendMessage(finalTranscript);
                saveToConversation(username, finalTranscript);
            }
            if (interimTranscript) {
                updateInterimMessage(interimTranscript);
            }
        };
        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
        };
        recognition.onend = () => {
            console.log('Speech recognition API finished.');
            isRecognizing = false;
        };
        console.log('Speech recognition API initialized.');
    } else {
        console.error('Speech Recognition API not supported in this browser.');
    }
}

// Recognition Control Functions
function startRecognition() {
    if (!recognition) {
        initializeSpeechRecognition();
    }
    recognition.start();
    isRecognizing = true;
    console.log('Speech recognition ON.');
}

function stopRecognition() {
    if (recognition && isRecognizing) {
        recognition.stop();
        isRecognizing = false;
        console.log('Speech recognition OFF.');
    }
}

// Message Handling Functions
function sendMessage(message) {
    if (!message.trim()) return;
    const userMessage = `${username}: ${message}`;
    lastSentMessage = userMessage;
    chatSocket.send(JSON.stringify({ message: userMessage }));
    addMessage(userMessage, 'user-message');
}

function addMessage(message, className) {
    const interimDiv = document.getElementById('interim-message');
    if (interimDiv) interimDiv.remove();

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${className}`;
    messageDiv.textContent = message;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function updateInterimMessage(interimMessage) {
    const interimDiv = document.getElementById('interim-message') || createInterimDiv();
    interimDiv.textContent = interimMessage;
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function createInterimDiv() {
    const messageDiv = document.createElement('div');
    messageDiv.id = 'interim-message';
    messageDiv.className = 'message interim-message';
    messageDiv.style.color = 'gray';
    chatMessages.appendChild(messageDiv);
    return messageDiv;
}

// Conversation Management
function saveToConversation(speaker, message) {
    const timestamp = new Date().toISOString();
    conversation.push({ speaker, message, timestamp });
    console.log('Conversation updated:', conversation);
}

function exportConversation() {
    if (conversation.length === 0) {
        alert('Cannot export an empty conversation.');
        return;
    }

    // Get the room ID from the body tag
    const appointmentId = document.body.dataset.roomid;

    const text = conversation.map(entry => 
        `${entry.speaker}: ${entry.message}`
    ).join('\n');

    fetch(`/videochat/${appointmentId}/save_conversation/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
        },
        body: JSON.stringify({ text }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('Conversation saved! ID: ' + data.id);
        } else {
            alert('Error saving conversation.');
        }
    })
    .catch(error => {
        console.error('Save failed:', error);
        alert('Network or server error.');
    });
}

function getCSRFToken() {
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
    return cookieValue;
}


// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    var loc = window.location;
    var serverIP = "192.168.0.108";
    var port = "8000"; 
    var wsStart = "wss://"; 
    var endpoint = wsStart + serverIP + ":" + "/text/" + roomid + "/";

    console.log("Attempting connection to:", endpoint);
    chatSocket = new WebSocket(endpoint);

    // Set up WebSocket handlers
    chatSocket.onmessage = ({ data }) => {
        const parsedData = JSON.parse(data);
        if (parsedData.message !== lastSentMessage) {
            saveToConversation('Bot', parsedData.message);
            addMessage(parsedData.message, 'bot-message');
        }
    };

    chatSocket.onclose = () => console.error('Chat socket closed unexpectedly');

    const toggleButton = document.getElementById('btn-start-recognition');
    if (!toggleButton) {
        console.error('Toggle button not found in the DOM.');
        return;
    }
    toggleButton.addEventListener('click', () => {
        if (isRecognizing) {
            stopRecognition();
            toggleButton.textContent = 'Recognition On';
        } else {
            startRecognition();
            toggleButton.textContent = 'Recognition Off';
        }
    });
    toggleButton.textContent = 'Recognition On';

    const exportButton = document.getElementById('btn-export-conversation');
    if (!exportButton) {
        console.error('Export button not found in the DOM.');
        return;
    }
    exportButton.addEventListener('click', exportConversation);
});

