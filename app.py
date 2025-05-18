import os
import random
import requests
import gradio as gr
import asyncio
import ollama
from dotenv import load_dotenv

load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
OLLAMA_MODEL = "llama3:8b"          

MOOD_TO_MOVIE_IDS = {
    "happy":       [13, 550, 278, 680, 105, 12, 293660],
    "sad":         [424, 500, 578, 597, 807, 497, 266],
    "adventurous": [122, 98, 140607, 22, 120, 8587, 177572],
    "romantic":    [1252309, 1064213, 950396, 372058, 1226406, 12244, 8966, 1323784, 937287, 402431],
    "nostalgic":   [11, 85, 9615, 11324, 100, 101, 581],
    "mystery":     [574475, 974576, 419430, 414906, 882598, 458723, 423108, 1029880, 516632, 10528],
}

# fetch data
def fetch_movie_details(mid:int)->dict|None:
    url = f"https://api.themoviedb.org/3/movie/{mid}"
    r   = requests.get(url, params={"api_key": TMDB_API_KEY, "language": "en-US"})
    if not r.ok:
        return None
    d = r.json()
    return {
        "title":    d["title"],
        "overview": d["overview"],
        "poster":   f"https://image.tmdb.org/t/p/w500{d['poster_path']}" if d.get("poster_path") else ""
    }

def generate_ai_description(mood:str, movies:list[dict]) -> str:
    movie_block = "\n".join(f"Title: {m['title']}\nOverview: {m['overview']}" for m in movies)
    prompt = (f'A user is feeling "{mood}". Explain in a fun, thoughtful way why these 3 '
              f'movies fit that mood.\n\n{movie_block}')
    res = ollama.chat(model=OLLAMA_MODEL,
                      messages=[{"role":"user", "content": prompt}],
                      stream=False)
    return res["message"]["content"]

# ────────── async main (placeholder first) ────────────────────────────────
async def recommend(mood:str)->str:
    mood = mood.lower().strip()
    if mood not in MOOD_TO_MOVIE_IDS:
        return f"❌ Mood not found. Try one of: {', '.join(MOOD_TO_MOVIE_IDS.keys())}"

    ids     = random.sample(MOOD_TO_MOVIE_IDS[mood], 3)
    loop    = asyncio.get_event_loop()
    movies  = await asyncio.gather(*[loop.run_in_executor(None, fetch_movie_details, i) for i in ids])
    movies  = [m for m in movies if m]
    if not movies:
        return " Could not fetch movie data."

    ai_text = await loop.run_in_executor(None, generate_ai_description, mood, movies)

    md = f"## 🧠 AI Insight for *{mood.title()}*\n\n{ai_text}\n\n---\n"
    for m in movies:
        md += f"### 🎬 {m['title']}\n{m['overview']}\n"
        if m['poster']:
            md += f"![Poster]({m['poster']})\n"
        md += "---\n"
    return md

# ────────── Gradio UI with loading placeholder ────────────────────────────
with gr.Blocks(title="Mood‑Based Movie Recommender") as demo:
    gr.Markdown("##  Mood‑Based Movie Recommender\nEnter a mood to get three AI‑curated films.")
    mood_input = gr.Textbox(label="Enter a mood like happy, sad, adventurous, romantic, nostalgic, or mystery to get personalized movie recommendations.")
    go_button  = gr.Button("Get Recommendations")
    output_md  = gr.Markdown()

    # 1) show loading msg instantly  2) then async generate real content
    go_button.click(lambda _:"⏳ Generating recommendations…", inputs=mood_input, outputs=output_md)\
             .then(recommend, inputs=mood_input, outputs=output_md)

demo.launch(share=True)   
