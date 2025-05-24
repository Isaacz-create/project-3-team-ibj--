import os
import requests
import random
import gradio as gr
from dotenv import load_dotenv
import ollama

# Load environment variables
load_dotenv()

# API Key and configuration
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
if not TMDB_API_KEY:
    print("Warning: TMDB_API_KEY not found. Please check your .env file.")

TMDB_BASE_URL = "https://api.themoviedb.org/3"
OLLAMA_MODEL = "tinyllama"

# Movies categorized by moods (TMDB IDs)
MOOD_TO_MOVIE_IDS = {
    "happy":       [552524, 315162, 13, 447365, 787699, 105, 12, 293660],
    "sad":         [424, 500, 578, 597, 807, 497, 266],
    "adventurous": [950387, 986056, 140607, 575265, 1011985, 693134, 177572, 346698, 11, 330459, 862],
    "romantic":    [1252309, 1064213, 950396, 372058, 1226406, 12244, 8966, 1323784, 937287, 402431],
    "nostalgic":   [11, 85, 9615, 11324, 100, 101, 581],
    "mystery":     [574475, 974576, 419430, 414906, 882598, 458723, 423108, 1029880, 516632, 10528],
}

# Check Ollama availability
def check_ollama_availability():
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": OLLAMA_MODEL, "prompt": "hello", "stream": False},
        )
        return response.status_code == 200
    except:
        return False

# Fetch movie data from TMDB
def fetch_movie_data(movie_id: int):
    url = f"{TMDB_BASE_URL}/movie/{movie_id}"
    params = {"api_key": TMDB_API_KEY, "language": "en-US"}
    try:
        response = requests.get(url, params=params)
        if response.ok:
            data = response.json()
            return {
                "title": data.get("title"),
                "overview": data.get("overview"),
                "poster": f"https://image.tmdb.org/t/p/w500{data.get('poster_path')}" if data.get("poster_path") else ""
            }
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Exception occurred: {e}")
        return None

# Generate explanation using Ollama
def generate_description(mood, movies):
    prompt = f'A user is feeling "{mood}". Explain concisely why these three movies match their mood:\n'
    for movie in movies:
        prompt += f"\nTitle: {movie['title']}\nOverview: {movie['overview']}\n"

    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": prompt}],
            stream=False
        )
        return response["message"]["content"]
    except Exception as e:
        print(f"Ollama Error: {e}")
        return "Could not generate insight from Ollama."

# Main recommendation function
def movie_recommend(mood: str):
    mood = mood.lower().strip()

    if mood not in MOOD_TO_MOVIE_IDS:
        return f"Mood not found. Try one of: {', '.join(MOOD_TO_MOVIE_IDS.keys())}"

    if not check_ollama_availability():
        return "Tinyllama is not responding. Please ensure Ollama is running."

    selected_ids = random.sample(MOOD_TO_MOVIE_IDS[mood], 3)
    movies = [fetch_movie_data(mid) for mid in selected_ids if fetch_movie_data(mid)]

    if len(movies) < 3:
        return "Error fetching movie details from TMDB."

    insight = generate_description(mood, movies)

    markdown = f"## Movie Recommendations for {mood.title()} Mood\n\n"
    markdown += f"### Insight\n{insight}\n\n---\n"

    for movie in movies:
        markdown += f"### {movie['title']}\n{movie['overview']}\n"
        if movie["poster"]:
            markdown += f"![Poster]({movie['poster']})\n"
        markdown += "---\n"

    return markdown

# Gradio UI
with gr.Blocks(title="Mood-Based Movie Recommender") as demo:
    gr.Markdown("# 🎬 Mood-Based Movie Recommender")
    mood_input = gr.Dropdown(
        choices=list(MOOD_TO_MOVIE_IDS.keys()),
        label="Select Your Mood",
        value="happy",
        allow_custom_value=True
    )
    submit_button = gr.Button("Get Recommendations")
    output_markdown = gr.Markdown()

    submit_button.click(
        fn=movie_recommend,
        inputs=mood_input,
        outputs=output_markdown
    )

if __name__ == "__main__":
    demo.launch(share=True)
