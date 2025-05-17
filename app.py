import random
import gradio as gr
import os
from dotenv import load_dotenv
import requests

load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

MOOD_TO_MOVIE_IDS = {
    "happy": [13, 550, 278, 680, 105, 12, 293660],
    "sad": [424, 500, 578, 597, 807, 497, 266, 667],
    "adventurous": [122, 98, 140607, 22, 120, 8587, 177572, 122917],
    "romantic": [194, 281, 348, 534, 12405, 12244, 227],  # Add more
    "nostalgic": [11, 85, 9615, 11324, 100, 101, 581],    # Add more
    "mystery": [274, 155, 807, 614, 345, 862, 915]         # Add more
}

def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {
            "title": data["title"],
            "overview": data["overview"],
            "poster": f"https://image.tmdb.org/t/p/w500{data['poster_path']}"
        }
    else:
        return None

def recommend_movies(mood):
    mood = mood.lower().strip()
    if mood not in MOOD_TO_MOVIE_IDS:
        return f"Sorry, we don't have recommendations for the mood '{mood}'. Try: {', '.join(MOOD_TO_MOVIE_IDS.keys())}"
    
    selected_ids = random.sample(MOOD_TO_MOVIE_IDS[mood], 3)
    recommendations = []
    for movie_id in selected_ids:
        details = fetch_movie_details(movie_id)
        if details:
            recommendations.append(f"🎬 **{details['title']}**\n{details['overview']}\n![Poster]({details['poster']})")
    
    return "\n\n---\n\n".join(recommendations)

iface = gr.Interface(
    fn=recommend_movies,
    inputs=gr.Textbox(label="Enter your mood"),
    outputs=gr.Markdown(),
    title="Mood-Based Movie Recommender",
    description="Enter a mood like Happy, Sad, Adventurous, Romantic, Nostalgic, or Mystery to get personalized movie recommendations."
)

iface.launch(share=True)

