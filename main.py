import os
from flask import Flask, render_template, request, jsonify, Response
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
    This is a generator function that yields chunks of the story as they arrive from the API.
    
    Args:
        user_prompt (str): The user's story prompt
        
    Yields:
        str: Chunks of the generated story in Hungarian or error messages if generation fails
    """
    # Check if the API key is available
    if not os.environ.get("GEMINI_API_KEY"):
        yield "Hiányzik a Gemini API kulcs. Kérjük, ellenőrizze a konfigurációt."
        return
    
    try:
        # Initialize the Gemini model
        model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')
        
        # Create a system prompt with instructions for the story
        system_prompt = """
Egy kedves mesélő vagy, aki járatos a gyermekpszichológiában, különösképp a meseterápiában. Most egy szülőnek segítesz mesét írni, amit felolvashat gyermekeinek. Az a feladatod, hogy a felhasználói prompt kívánságainak a figyelembevételével esti mesét írj a gyermekeidnek. A szereplőknek mindig adj valami játékos nevet. A mese tekintetében, vedd figyelembe a meseterápiás elveket:
### 1. Hagyományos mesestruktúra
A mese kövesse a klasszikus mesék jól ismert szerkezetét. Ez általában a következőket jelenti:
1.  **Kezdet:** Nyugalmi állapot bemutatása, a főszereplő és a helyzet megismerése.
2.  **Konfliktus vagy Hiány:** Megjelenik egy probléma, egy kihívás, vagy valami hiányzik (pl. a királylány elrablása, szegénység, betegség). Ez indítja el a cselekményt.
3.  **Út vagy Vándorlás:** A főszereplő útnak indul a probléma megoldására. Ez az út lehet fizikai vagy metaforikus. Itt találkozik segítőkkel és akadályokkal.
4.  **Próbák és Megmérettetések:** A főszereplőnek különböző feladatokat kell megoldania, nehézségeket kell leküzdenie. Ezek a próbák fejlesztik a képességeit, bátorságát.
5.  **Tetőpont:** A legnagyobb próba, a konfliktus csúcspontja (pl. küzdelem a sárkánnyal, a gonosz legyőzése).
6.  **Megoldás és Hazatérés:** A konfliktus megoldódik, a főszereplő eléri célját, megszerzi, amit keresett, és hazatér.
7.  **Végkifejlet:** Az új, rendezett állapot bemutatása, a "boldogan éltek, amíg meg nem haltak" rész.

### 2. Egyértelmű Szereplők (Archetípusok)
A mesében megjelenő szereplők legyenek tipikusak, archetipikusak (pl. hős, gonosz mostoha, bölcs öreg, segítő állat vagy lény, királylány/királyfi). Ezek a karakterek nem bonyolultak lélektanilag, ami lehetővé teszi a könnyű azonosulást vagy épp a negatív tulajdonságok kivetítését. A jó és a rossz általában tisztán elválik.

### 3. Szimbolikus Nyelv
A mese gazdag legyen szimbólumokban (pl. erdő, víz, hegy, állatok, tárgyak, színek, számok mint 3, 7, 12). Ezek a szimbólumok mélyebb, tudattalan tartalmakat hordoznak, és lehetővé teszik, hogy a hallgató/olvasó saját belső élményeit, érzéseit kapcsolja hozzájuk anélkül, hogy expliciten kimondaná.

### 4. Nincs Explicit Tanulság
A mesék, szemben a fabulákkal, általában nem fogalmaznak meg direkt erkölcsi vagy tanító célt. A tanulság, a felismerés a történet átélésén, a szimbólumok megfejtésén és a mesével való foglalkozáson keresztül jön létre.

### 5. Metaforikus Jelleg
A történet ne literalizálja túlságosan a problémákat. A nehézségek, kihívások legyenek metaforikusak, így tág teret engednek a hallgató/olvasó saját problémáinak behelyettesítésére és feldolgozására.

### 6. Reményteli Végkifejlet
Bár a mese tartalmazhat nehézségeket, szorongást keltő elemeket, a végkifejletnek a megküzdés, a fejlődés és a helyreállás reményét kell hordoznia. A "boldog vég" (vagy legalábbis a konfliktus megoldása) biztosítja a biztonságot és azt az üzenetet, hogy a nehézségeket le lehet győzni.

### 7. Egyszerű, Ritmusos Nyelv
A mese nyelvezete legyen tiszta, világos, esetenként ismétlődő fordulatokkal, ritmusos elemekkel. Ez segíti a bevonódást és a történet memorizálását.

### 8. Belső Utazás Lehetősége
A mese szerkezete és tartalma adja meg a lehetőséget a hallgatónak/olvasónak, hogy belső utazást tegyen, feldolgozza saját félelmeit, vágyait, és megtalálja a benne rejlő erőforrásokat a kihívások legyőzéséhez.

Csak a mesét add vissza, ne adj alcímeket.

A mese végén adj tanácsot a szülőnek, milyen kérdésekkel, hogyan beszélgessen a gyermekeivel a meséről, hogy a meseterápia a lehető leghasznosabb legyen.
        """
        
        # Combine the system prompt with the user prompt
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        # Generate content with the Gemini model with streaming enabled
        response = model.generate_content(full_prompt, stream=True)
        
        # Loop through the chunks provided by the streaming response
        for chunk in response:
            # Check if the chunk has text content
            if hasattr(chunk, 'text') and chunk.text:
                # Yield each text chunk as it arrives
                yield chunk.text
            
    except Exception as e:
        print(f"Hiba a történet generálása során: {str(e)}")
        yield f"Sajnos nem sikerült mesét alkotni ebben a pillanatban. Kérjük, próbálja újra később. (Hiba: {str(e)})"

# Route for the main page
@app.route('/')
def index():
    """Serve the main page of the application"""
    return render_template('index.html')

# Route for generating stories
@app.route('/generate_tale', methods=['POST'])
def generate_tale():
    """
    Process the user's story prompt and generate a story using the Gemini API.
    Streams the response from the API to the client as it's generated.
    
    Expects JSON data with a 'prompt_text' field
    Returns a streaming Response with plain text content
    """
    try:
        # Get data from the request
        data = request.get_json()
        
        # Check if the required field exists
        if 'prompt_text' not in data or not data['prompt_text'].strip():
            return jsonify({'error': 'Kérjük, adjon meg egy promptot a történethez'}), 400
        
        # Get the prompt text from the request
        prompt_text = data['prompt_text']
        
        # Create a streaming response using the generator function
        return Response(
            get_story_from_ai(prompt_text),
            mimetype='text/plain'
        )
    
    except Exception as e:
        # Handle any errors that occur
        return jsonify({'error': f'Hiba történt: {str(e)}'}), 500

