**Mood-Based Movie Recommender**

This AI-enhanced web app recommends movies based on your current mood. Using real-time data from the TMDB API and natural-language generation (optional), 
it offers personalized movie suggestions with titles, overviews, and poster images — all through an easy-to-use Gradio interface.

**Project Overview**

- Pulls movie data from **The Movie Database (TMDB)** API  
- Users enter a **mood** (e.g., happy, sad, nostalgic)  
- Recommends 2–3 movies that match that mood  
- Uses **AI** to generate custom descriptions  
- Interactive **Gradio** web interface  

**Setup Guide**

1. **Clone the Repository**
   Clone the repository into the folder you created using git bash, then change the directory to project-3-team-ibj-- 
   ```bash
   git clone https://github.com/Isaacz-create/project-3-team-ibj--.git
   cd project-3-team-ibj--

3. **Install the Required Libraries**

bash
Copy
Edit
Create a .env File in the Root Directory
Add your TMDB API key like this:

ini
Copy
Edit
TMDB_API_KEY=your_api_key_here
Run the App

bash
Copy
Edit
python app.py
Gradio will start a local server and provide a public link if share=True.

🔗 Live Gradio App Link
👉 [Click here to open the app]( https://b150079f4042ea83c4.gradio.live)

**Group Members**
Jahmar Lawrence
Brian
Isaac

**Example Mood Prompts**
Try typing in moods like:

- Happy
- Romantic
- Melancholy
- Adventurous
- Nostalgic
- Curious

**Sample Output**
For the mood "adventurous", the app might return:

- Indiana Jones and the Last Crusade
- The Revenant
- Mad Max: Fury Road

**Tech Used**
- Python
- Gradio
- TMDB API
- Requests
- Dotenv
