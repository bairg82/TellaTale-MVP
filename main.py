import os
import requests
import json
from flask import Flask, render_template, request, jsonify

# Create the Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "tellatale-secret-key")

def get_story_from_ai(user_prompt):
    """
    Generates a children's story using the Google Gemini API based on the user's prompt.
    
    Args:
        user_prompt (str): The user's story prompt
        
    Returns:
        str: A generated story in Hungarian or an error message if generation fails
    """
    # Get the API key from environment variables
    api_key = os.environ.get("GEMINI_API_KEY")
    
    # Check if the API key is available
    if not api_key:
        return "Hiányzik a Gemini API kulcs. Kérjük, ellenőrizze a konfigurációt."
    
    try:
        # Direct REST API call to Gemini API
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
        
        # Create a simpler system prompt with instructions for the story
        prompt = f"""
Kérlek, írj egy gyerekeknek szóló mesét magyarul a következő téma alapján: {user_prompt}

A mese legyen:
- 3-7 éves gyerekeknek megfelelő
- Pozitív üzenetű, kedves történet
- Egyszerű, érthető szövegezéssel
- Rövid, max. 1-2 perces felolvasással
- Meseterápiás alapelveket tartalmazzon

FONTOS: Csak magát a mesét add vissza, semmilyen bevezetőt, kommentárt vagy kérdést ne csatolj hozzá!
"""
        
        # Prepare the request data according to Gemini API documentation
        request_data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 800,
                "topP": 0.8,
                "topK": 40
            }
        }
        
        # Send the request to the Gemini API
        response = requests.post(
            api_url,
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            response_data = response.json()
            
            # Extract the generated text from the response
            if (response_data and 
                'candidates' in response_data and 
                len(response_data['candidates']) > 0 and
                'content' in response_data['candidates'][0] and
                'parts' in response_data['candidates'][0]['content'] and
                len(response_data['candidates'][0]['content']['parts']) > 0 and
                'text' in response_data['candidates'][0]['content']['parts'][0]):
                
                # Get the story text
                story_text = response_data['candidates'][0]['content']['parts'][0]['text'].strip()
                
                # Remove any potential HTML tags or special characters
                story_text = story_text.replace('<', '&lt;').replace('>', '&gt;')
                
                return story_text
            else:
                return "Nem sikerült történetet generálni. Kérjük, próbálja újra később."
        else:
            # Log the error for debugging
            print(f"Gemini API hiba: {response.status_code} - {response.text}")
            return "Nem sikerült kapcsolódni a Gemini API-hoz. Kérjük, próbálja újra később."
            
    except Exception as e:
        # Log the error for debugging
        print(f"Hiba a történet generálása során: {str(e)}")
        # Return a simpler error message without the technical details
        return "Sajnos nem sikerült mesét alkotni ebben a pillanatban. Kérjük, próbálja újra később."

# Route for the main page
@app.route('/')
def index():
    """Serve the main page of the application"""
    return render_template('index.html')

# Route for generating stories
@app.route('/generate_tale', methods=['POST'])
def generate_tale():
    """
    Process the user's story prompt and generate a story using the Gemini API
    
    Expects JSON data with a 'prompt_text' field
    Returns JSON with a 'story' field containing the generated story
    """
    try:
        # Get data from the request
        data = request.get_json()
        
        # Check if the required field exists
        if 'prompt_text' not in data or not data['prompt_text'].strip():
            return jsonify({'error': 'Kérjük, adjon meg egy promptot a történethez'}), 400
        
        # Get the prompt text from the request
        prompt_text = data['prompt_text']
        
        # Generate a story using the Gemini API
        story = get_story_from_ai(prompt_text)
        
        # Check if the response indicates an error
        if story.startswith("Hiányzik a Gemini API kulcs") or story.startswith("Sajnos nem sikerült"):
            return jsonify({'error': story}), 500
        
        # Return the generated story as JSON
        return jsonify({'story': story})
    
    except Exception as e:
        # Handle any errors that occur
        return jsonify({'error': f'Hiba történt: {str(e)}'}), 500

# Run the Flask application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
