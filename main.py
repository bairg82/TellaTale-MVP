import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

# Create the Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "tellatale-secret-key")

# Configure the Gemini API with the API key from environment variables
try:
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f"Hiba a Gemini API konfigurációja során: {str(e)}")

def get_story_from_ai(user_prompt):
    """
    Generates a children's story using the Google Gemini API based on the user's prompt.
    
    Args:
        user_prompt (str): The user's story prompt
        
    Returns:
        str: A generated story in Hungarian or an error message if generation fails
    """
    # Check if the API key is available
    if not os.environ.get("GEMINI_API_KEY"):
        return "Hiányzik a Gemini API kulcs. Kérjük, ellenőrizze a konfigurációt."
    
    try:
        # Initialize the Gemini model
        model = genai.GenerativeModel('gemini-2.5-pro-preview-05-06')
        
        # Create a system prompt with instructions for the story
        system_prompt = """
        Mint gyermek-mesemondó, a feladatod, hogy egy kedves, képzeletgazdag magyar nyelvű mesét alkoss fiatal gyermekek számára (3-7 évesek). 
        
        A történetnek a következő jellemzőkkel kell rendelkeznie:
        - Legyen kornak megfelelő, biztonságos és gyermekbarát
        - Alkalmazzon meseterápiás elveket (pozitív megoldások, empátia, gyengéd tanulságok, érzelmi kifejezés biztonságos környezetben)
        - Kövessen egy világos történeti struktúrát (egyszerű kezdet, kihívás vagy kaland, és kielégítő megoldás vagy tanulság)
        - Legyen lebilincselő, képzeletgazdag és kedves a hangvétele
        
        A végső kimenetnek csak a mesét kell tartalmaznia, készen arra, hogy megjelenjen a felhasználó számára.
        
        A felhasználó által megadott prompt a következő:
        """
        
        # Combine the system prompt with the user prompt
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        # Generate content with the Gemini model
        response = model.generate_content(full_prompt)
        
        # Extract the generated story text
        if response and hasattr(response, 'text'):
            return response.text.strip()
        else:
            return "Nem sikerült történetet generálni. Kérjük, próbálja újra később."
            
    except Exception as e:
        print(f"Hiba a történet generálása során: {str(e)}")
        return f"Sajnos nem sikerült mesét alkotni ebben a pillanatban. Kérjük, próbálja újra később. (Hiba: {str(e)})"

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
