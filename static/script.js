/**
 * TellaTale MVP JavaScript
 * 
 * This script handles the story generation request to the backend
 * and updates the UI accordingly.
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
                return response.json().then(data => {
                    throw new Error(data.error || 'Nem sikerült létrehozni a mesét.');
                });
            }
            return response.json();
        })
        .then(data => {
            // Display the generated story
            displayStory(data.story);
        })
        .catch(error => {
            // Show error message
            showError(error.message || 'Hiba történt a mese létrehozása közben.');
            console.error('Error:', error);
        })
        .finally(() => {
            // Remove loading state
            setLoadingState(false);
        });
    }
    
    /**
     * Updates the UI to show the generated story
     */
    function displayStory(story) {
        // Replace newlines with HTML line breaks for proper formatting
        const formattedStory = story.replace(/\n/g, '<br>');
        storyOutput.innerHTML = `<p>${formattedStory}</p>`;
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
            generateButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Generálás...';
            storyOutput.classList.add('loading');
            storyOutput.innerHTML = '<p class="text-muted">Mese generálása folyamatban...</p>';
        } else {
            generateButton.disabled = false;
            generateButton.textContent = 'Mese Generálása';
            storyOutput.classList.remove('loading');
        }
    }
});
