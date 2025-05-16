function setupTranscription() {
    // Create toggle button
    const btnToggleTranscription = document.createElement('button');
    btnToggleTranscription.id = 'btn-toggle-transcription';
    btnToggleTranscription.className = 'btn btn-primary';
    btnToggleTranscription.innerHTML = '<i class="fas fa-comment-alt"></i> Start Transcription';
    document.querySelector('#video-controls').appendChild(btnToggleTranscription);
    
    // Create save button
    const btnSaveTranscription = document.createElement('button');
    btnSaveTranscription.id = 'btn-save-transcription';
    btnSaveTranscription.className = 'btn btn-success';
    btnSaveTranscription.innerHTML = '<i class="fas fa-save"></i> Save Transcription';
    btnSaveTranscription.style.marginLeft = '10px';
    btnSaveTranscription.disabled = true; // Disabled by default until there's content
    document.querySelector('#video-controls').appendChild(btnSaveTranscription);
    
    // Get existing transcription div and container
    const transcriptionDiv = document.querySelector('#transcription');
    const transcriptionContainer = document.querySelector('#transcription-container');
    
    // Initialize speech recognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.lang = 'es-ES';
    recognition.continuous = true;
    recognition.interimResults = true;
    
    let isTranscribing = false;
    let isPaused = false; // New state for pausing
    let finalTranscript = '';

    recognition.onresult = (event) => {
        let interimTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; ++i) {
            const result = event.results[i];
            const text = result[0].transcript;

            if (result.isFinal) {
                finalTranscript += text + ' ';
            } else {
                interimTranscript += text;
            }
        }

        transcriptionDiv.textContent = finalTranscript + interimTranscript;
        
        // Enable save button when we have content
        if (finalTranscript.trim() !== '') {
            btnSaveTranscription.disabled = false;
        }
    };
    
    // Handle recognition errors
    recognition.onerror = (event) => {
        console.error('Speech recognition error', event.error);
        stopTranscription();
    };
    
    // Add event listener for the toggle button
    btnToggleTranscription.addEventListener('click', () => {
        if (isTranscribing) {
            if (isPaused) {
                resumeTranscription();
            } else {
                pauseTranscription();
            }
        } else {
            startTranscription();
        }
    });
    
    // Add event listener for the save button
    btnSaveTranscription.addEventListener('click', saveTranscription);
    
    function startTranscription() {
        try {
            recognition.start();
            transcriptionContainer.style.display = 'block';
            btnToggleTranscription.innerHTML = '<i class="fas fa-comment-alt"></i> Pause Transcription';
            isTranscribing = true;
            isPaused = false;
        } catch (err) {
            console.error('Failed to start transcription:', err);
        }
    }
    
    function pauseTranscription() {
        try {
            recognition.stop(); // Stop recognition temporarily
            btnToggleTranscription.innerHTML = '<i class="fas fa-comment-alt"></i> Resume Transcription';
            isPaused = true;
        } catch (err) {
            console.error('Failed to pause transcription:', err);
        }
    }

    function resumeTranscription() {
        try {
            recognition.start(); // Resume recognition
            btnToggleTranscription.innerHTML = '<i class="fas fa-comment-alt"></i> Pause Transcription';
            isPaused = false;
        } catch (err) {
            console.error('Failed to resume transcription:', err);
        }
    }

    function stopTranscription() {
        try {
            recognition.stop();
            btnToggleTranscription.innerHTML = '<i class="fas fa-comment-alt"></i> Start Transcription';
            isTranscribing = false;
            isPaused = false; // Reset pause state
        } catch (err) {
            console.error('Failed to stop transcription:', err);
        }
    }
    
    function saveTranscription() {
        if (finalTranscript.trim() === '') {
            alert('No transcription content to save.');
            return;
        }
        
        // Create a Blob with the transcription text
        const blob = new Blob([finalTranscript], { type: 'text/plain' });
        
        // Create a temporary download link
        const downloadLink = document.createElement('a');
        downloadLink.href = URL.createObjectURL(blob);
        
        // Get current date and time for the filename
        const now = new Date();
        const dateStr = now.toISOString().replace(/:/g, '-').replace(/\..+/, '');
        
        // Set filename with timestamp
        downloadLink.download = `transcription_${dateStr}.txt`;
        
        // Trigger download
        document.body.appendChild(downloadLink);
        downloadLink.click();
        document.body.removeChild(downloadLink);
        
        // Clean up the URL object
        URL.revokeObjectURL(downloadLink.href);
    }
}

export default setupTranscription;