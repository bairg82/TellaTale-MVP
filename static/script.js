/**
 * TellaTale MVP JavaScript
 * 
 * This script handles the story generation request to the backend
 * and updates the UI accordingly. It now supports streaming responses
 * from the server, showing the story as it's being generated.
 */

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Get references to the important elements
    const promptTextarea = document.getElementById('storyPrompt');
    const generateButton = document.getElementById('generateButton');
    const storyOutput = document.getElementById('storyOutput');
    
    // Add event listener to the Generate Tale button
    generateButton.addEventListener('click', generateStory);
    
    // Also generate a story when the user presses Enter in the textarea
    // (but only if they're not also pressing Shift for a new line)
    promptTextarea.addEventListener('keydown', function(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault(); // Prevent adding a new line
            generateStory();
        }
    });
    
    /**
     * Function to send the user's prompt to the backend and display the generated story
     * with streaming support to handle long responses without timeout
     */
    function generateStory() {
        // Get the text from the textarea
        const promptText = promptTextarea.value.trim();
        
        // Validate that there is text in the prompt
        if (!promptText) {
            showError('Kérjük, adjon meg egy mesepromptot.');
            return;
        }
        
        // Show loading state
        setLoadingState(true);
        
        try {
            // Send the request to the backend
            fetch('/generate_tale', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ prompt_text: promptText }),
            })
            .then(response => {
                // Check if the response is successful
                if (!response.ok) {
                    // Try to parse error as JSON first
                    if (response.headers.get('content-type')?.includes('application/json')) {
                        return response.json().then(data => {
                            throw new Error(data.error || 'Nem sikerült létrehozni a mesét.');
                        });
                    } else {
                        throw new Error('Nem sikerült létrehozni a mesét.');
                    }
                }
                
                // Prepare the story output area
                storyOutput.innerHTML = '<p></p>';
                const storyParagraph = storyOutput.querySelector('p');
                
                // Get the readable stream from the response
                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let accumulatedText = '';
                
                // Function to process the stream
                function readStream() {
                    // Read from the stream
                    reader.read().then(({ done, value }) => {
                        // If we're done, finish up
                        if (done) {
                            // Apply final formatting
                            const formattedStory = accumulatedText.replace(/\n/g, '<br>');
                            storyParagraph.innerHTML = formattedStory;
                            
                            // Remove loading state
                            setLoadingState(false);
                            return;
                        }
                        
                        // Decode the received chunk
                        const chunk = decoder.decode(value, { stream: true });
                        accumulatedText += chunk;
                        
                        // Update the story display with accumulated text
                        const formattedStory = accumulatedText.replace(/\n/g, '<br>');
                        storyParagraph.innerHTML = formattedStory;
                        
                        // Continue reading
                        readStream();
                    }).catch(error => {
                        showError('Hiba történt az adatok olvasása közben: ' + error.message);
                        setLoadingState(false);
                    });
                }
                
                // Start reading the stream
                readStream();
            })
            .catch(error => {
                // Show error message
                showError(error.message || 'Hiba történt a mese létrehozása közben.');
                console.error('Error:', error);
                setLoadingState(false);
            });
        } catch (error) {
            showError('Váratlan hiba történt: ' + error.message);
            console.error('Error:', error);
            setLoadingState(false);
        }
    }
    
    /**
     * Shows an error message in the story output area
     */
    function showError(message) {
        storyOutput.innerHTML = `<p class="text-danger"><strong>Hiba:</strong> ${message}</p>`;
    }
    
    /**
     * Sets or removes the loading state from the UI
     */
    function setLoadingState(isLoading) {
        if (isLoading) {
            generateButton.disabled = true;
            generateButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Mese készül...';
            storyOutput.classList.add('loading');
            storyOutput.innerHTML = '<p class="text-muted">A mese íródik...</p>';
        } else {
            generateButton.disabled = false;
            generateButton.textContent = 'Mese Generálása';
            storyOutput.classList.remove('loading');
        }
    }
});
