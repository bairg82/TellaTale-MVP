import os
from flask import Flask, render_template, request, jsonify

# Create the Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "tellatale-secret-key")

# Placeholder function for story generation
def get_story_from_ai(user_prompt):
    """
    This is a placeholder function that will later be replaced with actual AI integration.
    For now, it simply returns a dummy response based on the user's prompt.
    
    Args:
        user_prompt (str): The user's story prompt
        
    Returns:
        str: A placeholder story in Hungarian
    """
    return f"Ez egy helyőrző történet az Ön promptja alapján: '{user_prompt}'. A valódi történet a Geminitől később kerül ide."

# Route for the main page
@app.route('/')
def index():
    """Serve the main page of the application"""
    return render_template('index.html')

# Route for generating stories
@app.route('/generate_tale', methods=['POST'])
def generate_tale():
    """
    Process the user's story prompt and generate a placeholder story
    
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
        
        # Generate a story using the placeholder function
        story = get_story_from_ai(prompt_text)
        
        # Return the generated story as JSON
        return jsonify({'story': story})
    
    except Exception as e:
        # Handle any errors that occur
        return jsonify({'error': f'Hiba történt: {str(e)}'}), 500

# Run the Flask application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
