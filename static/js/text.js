const username = document.body.dataset.username;
const userRole = document.body.dataset.role; // 'doctor' or 'patient'
const roomid = document.body.dataset.roomid;
const serverIp = document.body.dataset.server;
const port = document.body.dataset.port;
const chatMessages = document.getElementById('chat-messages');
var chatSocket;
let lastSentMessage = '';
let recognition;
let isRecognizing = false; // Flag to track recognition state
let isRecording = false; // Flag to track if conversation is being recorded
let isAudioEnabled = false; // Flag to track audio button state - initially disabled
let restartAttempts = 0; // Track restart attempts to prevent infinite loops
const conversation = [];

// Speech Recognition Setup
function initializeSpeechRecognition() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.lang = 'en-US';
        recognition.continuous = true;
        recognition.interimResults = true;

        recognition.onresult = (event) => {
            if (!isRecognizing || !isAudioEnabled) {
                return;
            }
            
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
                restartAttempts = 0; // Reset counter on successful recognition
                sendMessage(finalTranscript);
                // Only save to conversation if recording is active
                if (isRecording) {
                    saveToConversation(userRole, finalTranscript);
                }
            }
            if (interimTranscript) {
                updateInterimMessage(interimTranscript);
            }
        };
        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            
            // Don't restart on certain errors or if too many attempts
            if (event.error === 'no-speech' || event.error === 'audio-capture' || event.error === 'not-allowed' || restartAttempts >= 3) {
                isRecognizing = false;
                if (restartAttempts >= 3) {
                    console.warn('Too many restart attempts, stopping speech recognition');
                    disableAudio(); // Disable audio to stop the loop
                }
                return;
            }
            restartAttempts++;
        };
        recognition.onend = () => {
            console.log('Speech recognition API finished.');
            isRecognizing = false;
            
            // Only auto-restart if audio is enabled and not too many attempts
            if (isAudioEnabled && restartAttempts < 3) {
                setTimeout(() => {
                    startRecognition();
                }, 2000); // Increased delay to prevent rapid restarts
            } else if (restartAttempts >= 3) {
                console.warn('Maximum restart attempts reached, stopping recognition');
                disableAudio();
            }
        };
        console.log('Speech recognition API initialized.');
    } else {
        console.error('Speech Recognition API not supported in this browser.');
    }
}

// Recognition Control Functions - Now tied to audio button
function startRecognition() {
    if (!isAudioEnabled) return;
    
    if (!recognition) {
        initializeSpeechRecognition();
    }
    if (!isRecognizing) {
        try {
            recognition.start();
            isRecognizing = true;
            console.log('Speech recognition ON.');
        } catch (error) {
            console.error('Failed to start recognition:', error);
            isRecognizing = false;
        }
    }
}

function stopRecognition() {
    if (recognition && isRecognizing) {
        recognition.stop();
        isRecognizing = false;
        
        // Clear interim message when stopping
        const interimDiv = document.getElementById('interim-message');
        if (interimDiv) interimDiv.remove();
        
        console.log('Speech recognition OFF.');
    }
}

// Audio Control Functions - These will be called by the audio button
function enableAudio() {
    isAudioEnabled = true;
    restartAttempts = 0; // Reset restart counter when enabling audio
    startRecognition();
    console.log('Audio enabled - starting transcription');
}

function disableAudio() {
    isAudioEnabled = false;
    stopRecognition();
    console.log('Audio disabled - stopping transcription');
}

// Make functions available globally for videochat.js
window.transcriptionAudioEnabled = enableAudio;
window.transcriptionAudioDisabled = disableAudio;

// Message Handling Functions
function sendMessage(message) {
    if (!message.trim()) return;
    const userMessage = `${username}: ${message}`;
    lastSentMessage = userMessage;
    
    // Check WebSocket state before sending
    if (chatSocket && chatSocket.readyState === WebSocket.OPEN) {
        try {
            // Send in the original format to avoid server compatibility issues
            chatSocket.send(JSON.stringify({ message: userMessage }));
            addMessage(userMessage, 'user-message');
        } catch (error) {
            console.error('Error sending message:', error);
            addMessage(userMessage, 'user-message'); // Still show locally
        }
    } else {
        console.warn('WebSocket not ready, message not sent');
        addMessage(userMessage, 'user-message'); // Still show locally
    }
}

// Recording Control Functions (Doctor only)
function startRecording() {
    isRecording = true;
    // For now, let's not send recording state through WebSocket to avoid connection issues
    // chatSocket.send(JSON.stringify({ type: 'recording_state', recording: true }));
    console.log('Recording started locally');
    updateRecordingUI();
}

function stopRecording() {
    isRecording = false;
    // For now, let's not send recording state through WebSocket to avoid connection issues
    // chatSocket.send(JSON.stringify({ type: 'recording_state', recording: false }));
    console.log('Recording stopped locally');
    updateRecordingUI();
}

function updateRecordingUI() {
    const recordingButton = document.getElementById('btn-start-recording');
    
    if (isRecording) {
        if (recordingButton) {
            recordingButton.textContent = 'Stop Recording';
            recordingButton.className = 'btn btn-danger';
        }
        // Add visual indicator for all users
        if (!document.getElementById('recording-indicator')) {
            const indicator = document.createElement('div');
            indicator.id = 'recording-indicator';
            indicator.className = 'alert alert-warning mt-2';
            indicator.innerHTML = '<i class="fas fa-record-vinyl"></i> Recording in progress...';
            document.getElementById('chat-container').insertBefore(indicator, document.getElementById('chat-messages'));
        }
    } else {
        if (recordingButton) {
            recordingButton.textContent = 'Start Recording';
            recordingButton.className = 'btn btn-primary';
        }
        // Remove visual indicator
        const indicator = document.getElementById('recording-indicator');
        if (indicator) indicator.remove();
    }
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
            // Clear the conversation array after successful export
            conversation.length = 0;
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
    var wsStart = "wss://"; 
    var endpoint = wsStart + serverIp + ":" + port  + "/text/" + roomid + "/";

    console.log("Attempting connection to:", endpoint);
    
    function connectWebSocket() {
        chatSocket = new WebSocket(endpoint);

        chatSocket.onopen = () => {
            console.log('WebSocket connection opened');
        };

        chatSocket.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        // Set up WebSocket handlers
        chatSocket.onmessage = ({ data }) => {
            try {
                const parsedData = JSON.parse(data);
                
                // Handle regular transcription messages
                if (parsedData.message) {
                    const message = parsedData.message;
                    if (message !== lastSentMessage) {
                        // Extract speaker and text from message
                        const colonIndex = message.indexOf(': ');
                        if (colonIndex > 0) {
                            const speaker = message.substring(0, colonIndex);
                            const text = message.substring(colonIndex + 2);
                            
                            // Only save to conversation if recording is active
                            if (isRecording) {
                                saveToConversation(speaker, text);
                            }
                        }
                        addMessage(message, 'bot-message');
                    }
                }
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
            }
        };

        chatSocket.onclose = (event) => {
            console.error('Chat socket closed unexpectedly', event.code, event.reason);
            
            // Try to reconnect after 3 seconds
            setTimeout(() => {
                console.log('Attempting to reconnect...');
                connectWebSocket();
            }, 3000);
        };
    }

    // Initial connection
    connectWebSocket();

    // Recording control button (doctor only)
    const recordingButton = document.getElementById('btn-start-recording');
    if (recordingButton) {
        recordingButton.addEventListener('click', () => {
            if (isRecording) {
                stopRecording();
            } else {
                startRecording();
            }
            updateRecordingUI();
        });
    }

    // Export button (doctor only)
    const exportButton = document.getElementById('btn-export-conversation');
    if (exportButton) {
        exportButton.addEventListener('click', exportConversation);
    }

    // Initialize UI state
    updateRecordingUI();
});

