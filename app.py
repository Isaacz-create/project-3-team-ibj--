import os
import random
import requests
import gradio as gr
import ollama
from dotenv import load_dotenv

# load environment variables
load_dotenv()

# Get API Key from environment
TMDB_API_KEY  = os.getenv("TMDB_API_KEY")
if not TMDB_API_KEY:
   print("WARNING: TMBD_API_KEY not found in environment variables.")
   print("Please create a .env file with your API key")

OLLAMA_MODEL  = "tinyllama"
TMDB_BASE_URL = "https://api.themoviedb.org/3"

# Movie IDS that correlate to these moods, from the TMDB movie API
MOOD_TO_MOVIE_IDS = {
    "happy":       [552524, 315162, 13, 447365, 787699, 105, 12, 293660],
    "sad":         [424, 500, 578, 597, 807, 497, 266, 250546, 11036, 637, 14574, 965150, 
                    1402, 12477, 376867, 451915, 666277, 284293, 527641, 46705, 264644, 296096, 394117, 313369,
                    762975, 381289],

    "adventurous": [950387, 986056, 140607, 575265, 1011985, 693134, 177572, 346698, 11, 330459, 862, 337404],
    "romantic":    [1252309, 1064213, 950396, 372058, 1226406, 12244, 8966, 1323784, 937287, 402431],
    "nostalgic":   [11, 85, 9615, 11324, 100, 101, 581, 9340, 235, 59436, 85350, 9603, 9820],
    "mystery":     [574475, 974576, 419430, 414906, 882598, 458723, 423108, 1029880, 516632, 10528, 1098006],
}

# check to see if tinyllama is responding
def check_ollama_availability():
    """
    Returns True if the tinyllama model responds; False otherwise.
    """
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": OLLAMA_MODEL, 
                "prompt": "hello", 
                "stream": False
                },  
        )
        return response.status_code == 200
    except Exception:
        return False

# This function fetches movie data from TMDB API
def fetch_movie_data(movie_id: int) -> dict | None:
    """
    Query TMDB for a single movie. Returns minimal dict or None on failure.
    """
    try:
        response = requests.get(
            f"{TMDB_BASE_URL}/movie/{movie_id}",
            params={
                "api_key": TMDB_API_KEY, 
                "language": "en-US"
                },
        )
        if not response.ok:
            return None
        data = response.json()
        return {
            "title":    data["title"],
            "overview": data["overview"],
            "poster":   f"https://image.tmdb.org/t/p/w500{data['poster_path']}" if data.get("poster_path") else ""
        }
    except Exception:
        return None

def generate_description(mood: str, movies: list[dict]) -> str:
    """
    Ask tinyllama to explain why the selected three movies fit the mood.
    """
    movie_block = "\n".join(
        f"Title: {m['title']}\nOverview: {m['overview']}" for m in movies
    )
    prompt = (
        f'A user is feeling "{mood}". Explain in a concise, engaging way why these '
        f'three movies match the mood.\n\n{movie_block}'
    )

    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[{"role": "user", "content": prompt}],
        stream=False
    )
    return response["message"]["content"]


# Movie_recommend checks to the user inputted the moods provided to them, if not return an error message
def movie_recommend(mood: str) -> str:
    mood_key = mood.lower().strip()
    if mood_key not in MOOD_TO_MOVIE_IDS:
        return "Mood not found. Try one of: " + ", ".join(MOOD_TO_MOVIE_IDS.keys())
    
# Lets the user know that Tinyllama is not responding if the last argument was to fail
    if not check_ollama_availability():
        return "The tinyllama model is not responding on Ollama. Please ensure it is running."

# Depending on the mood the user chose, the list of movies selected for that mood is randomized
# (hence the random module imported)
# spit out 3 movies
    selected_ids = random.sample(MOOD_TO_MOVIE_IDS[mood_key], 3)
    movies = [fetch_movie_data(mid) for mid in selected_ids]
    movies = [m for m in movies if m]

    if len(movies) < 3:
        return "Could not retrieve movie data from TMDB."

    summary = generate_description(mood_key, movies)

# Tinyllama generates insight based on the mood

    md = f"## Insight for {mood_key.title()}\n\n{summary}\n\n---\n"
    for m in movies:
        md += f"### {m['title']}\n{m['overview']}\n"
        if m['poster']:
            md += f"![Poster]({m['poster']})\n"
        md += "---\n"
    return md


#This is the Gradio User Interface (UI)
with gr.Blocks(title="Mood‑Based Movie Recommender") as demo:
    gr.Markdown("## Mood‑Based Movie Recommender\nSelect or type a mood to get three curated films.")

#This provides a dropdown menu with all the moods
    mood_input = gr.Dropdown(
        choices=list(MOOD_TO_MOVIE_IDS.keys()),
        label="Mood",
        value="happy",
        allow_custom_value=True            # But this allows the user to type manually if they so choose
    )
    go_button = gr.Button("Get Recommendations")
    output_md = gr.Markdown()

    # This is a placeholder or a "loading bar", that visually shows the data being generated in the UI
    go_button.click(
        lambda _:"Generating recommendations…",
        inputs=mood_input,
        outputs=output_md
    ).then(
        movie_recommend,
        inputs=mood_input,
        outputs=output_md
    )

if __name__ == "__main__":
    demo.launch(share=True) # This creates shared link or public url where you can view the gradio app
