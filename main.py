import os
import traceback
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
        print("Gemini API sikeresen konfigurálva")
    else:
        print("FIGYELEM: A GEMINI_API_KEY nincs beállítva a Replit Secrets-ben.")
except Exception as e:
    print(f"Hiba a Gemini API konfigurációja során: {str(e)}")
    print(traceback.format_exc())

def get_story_from_ai(user_prompt):
    """
    Generates a children's story using the Google Gemini API based on the user's prompt.
    
    Args:
        user_prompt (str): The user's story prompt
        
    Returns:
        str: A generated story in Hungarian or an error message if generation fails
    """
    # Check if the API key was configured successfully
    if not genai.api_key:
        print("API kulcs hiányzik: genai.api_key nincs beállítva")
        return "Hiányzik a Gemini API kulcs. Kérjük, ellenőrizze a konfigurációt."
    
    try:
        print("Modellek lekérése...")
        available_models = [m.name for m in genai.list_models()]
        print(f"Elérhető modellek: {available_models}")
        
        # Initialize the Gemini model
        print("Gemini model inicializálása...")
        model_name = 'gemini-1.5-flash'  # Use a more stable model name
        
        # Check if the selected model is available
        if model_name not in [m for m in available_models if model_name in m]:
            model_name = available_models[0] if available_models else 'gemini-1.0-pro'
            print(f"Eredeti modell nem található, használjuk ezt helyette: {model_name}")
        
        model = genai.GenerativeModel(model_name)
        print(f"Model sikeresen inicializálva: {model_name}")
        
        # Create a system prompt with instructions for the story - simplified to avoid any formatting issues
        system_prompt = """Írj egy magyar nyelvű gyerekmesét a megadott témáról. A mese legyen:
- Gyerekbarát (3-7 éveseknek szóló)
- Pozitív üzenettel rendelkező
- Egyszerű, könnyen követhető cselekménnyel
- Rövid és tömör (maximum 1-2 perc felolvasva)"""
        
        # Combine the system prompt with the user prompt
        full_prompt = f"{system_prompt}\n\nA mese témája: {user_prompt}"
        
        print(f"Prompt elkészítve, API hívás következik...")
        print(f"Prompt szövege: {full_prompt}")
        
        # Set safety settings to avoid blocking
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]
        
        # Generate content with the Gemini model
        response = model.generate_content(
            contents=full_prompt,
            safety_settings=safety_settings,
            generation_config={
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 800,
            }
        )
        
        print(f"API válasz beérkezett: {type(response)}")
        
        # Check if the response was blocked by safety filters
        if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
            if hasattr(response.prompt_feedback, 'block_reason') and response.prompt_feedback.block_reason:
                print(f"Prompt blokkolva: {response.prompt_feedback.block_reason}")
                return f"A kérést a biztonsági szűrő blokkolta. Kérjük, próbáljon más promptot megadni."
        
        # Extract the generated story text
        if response and hasattr(response, 'text'):
            print("Sikeres történet generálás")
            return response.text.strip()
        else:
            print(f"Nincs text a válaszban: {response}")
            # Try to inspect the response object more thoroughly
            response_details = str(dir(response))
            print(f"Response objektum részletei: {response_details}")
            return "Nem sikerült történetet generálni. Kérjük, próbálja újra később."
            
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"Hiba a történet generálása során: {str(e)}")
        print(error_trace)
        return f"Sajnos nem sikerült mesét alkotni ebben a pillanatban. Kérjük, próbálja újra később. Technikai hiba történt."

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
        print(f"Kérés érkezett: {data}")
        
        # Check if the required field exists
        if 'prompt_text' not in data or not data['prompt_text'].strip():
            return jsonify({'error': 'Kérjük, adjon meg egy promptot a történethez'}), 400
        
        # Get the prompt text from the request
        prompt_text = data['prompt_text']
        print(f"Prompt szöveg: {prompt_text}")
        
        # Generate a story using the Gemini API
        story = get_story_from_ai(prompt_text)
        print(f"Generált válasz: {story[:100]}...") # Print first 100 chars for debugging
        
        # Check if the response indicates an error
        if any(story.startswith(prefix) for prefix in ["Hiányzik", "Sajnos", "A kérést", "Nem sikerült"]):
            print(f"Hibaüzenet: {story}")
            return jsonify({'error': story}), 500
        
        # Return the generated story as JSON
        return jsonify({'story': story})
    
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"Hiba a /generate_tale útvonalon: {str(e)}")
        print(error_trace)
        return jsonify({'error': f'Hiba történt a szerveren. Kérjük, próbálja újra később.'}), 500

# Run the Flask application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
