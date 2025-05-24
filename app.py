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
    "happy":       [552524, 315162, 13, 447365, 787699, 105, 12, 293660, 11631, 350, 808, 809, 238713, 
                    8392, 114, 449176, 505600, 194, 2062, 86577, 346648, 8835, 9880, 9602, 114150 ],

    "sad":         [424, 500, 578, 597, 807, 497, 266, 250546, 11036, 637, 14574, 965150, 
                    1402, 12477, 376867, 451915, 666277, 284293, 527641, 46705, 264644, 296096, 
                    394117, 313369, 762975, 381289],

    "adventurous": [950387, 986056, 140607, 575265, 1011985, 693134, 177572, 346698, 11, 330459, 862, 337404
                    , 569094, 822119, 1098006, 8844, 365177, 436969, 497582, 406759, 87827, 560016
                    , 746036, 539972, 37958],

    "romantic":    [1252309, 1064213, 950396, 372058, 1226406, 12244, 8966, 1323784, 937287, 402431, 
                    1072790, 22971, 1302916, 1010581, 1824, 417261, 43347, 200727, 566675, 2288, 1440,
                     492188, 222935, 1079091, 1381 ],

    "nostalgic":   [11, 85, 9615, 11324, 100, 101, 581, 9340, 235, 59436, 85350, 9603, 9820, 10830, 9444, 
                    137, 11846, 38365, 2109, 5174, 38575, 64682, 8587, 11224, 16859 ],

    "mystery":     [574475, 974576, 419430, 414906, 882598, 458723, 423108, 1029880, 516632, 10528, 1098006,
                    210577, 823766, 915935, 1124, 726209, 49026, 346364, 561, 1949, 146233, 484247, 503919,
                    514999, 645886],
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
with gr.Blocks(title="Mood‑Based Movie Recommender") as demo:
    gr.Markdown("## Mood‑Based Movie Recommender\nSelect or type a mood to get three curated films.")
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

    # This is a placeholder or a "loading bar", that visually shows the data being generated in the UI
    submit_button.click(
        lambda _:"Generating recommendations…",
        inputs=mood_input,
        outputs=output_markdown
    ).then(
        movie_recommend,
        inputs=mood_input,
        outputs=output_markdown
    )


if __name__ == "__main__":
    demo.launch(share=True) # This creates shared link or public url where you can view the gradio app
