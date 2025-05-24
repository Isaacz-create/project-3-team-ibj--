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

Create a ```.env``` file in the root directory of your project.

Add your TMDB API key to the file using the following format:
```TMDB_API_KEY=your_api_key_here```

Run the app using the following command:
```python app.py```

If ```share=True ``` is set in your Gradio app, it will start a local server and provide a public link you can use to access the app from anywhere.

 Live Gradio App Link
[Click here to open the app](https://cb39c8fa04527f8f5d.gradio.live)

**Group Members**
Jahmar Lawrence
Brian
Isaac

**Example Mood Prompts**
Try typing in moods like:

- Happy
- Romantic
- Mystery
- Adventurous
- Nostalgic
- Sad

**Sample Output**
For the mood "adventurous", the app might return:

- Indiana Jones and the Last Crusade
- The Revenant
- Mad Max: Fury Road

**Tech Used**
- Python
- Gradio
- Ollama
- TMDB API
- Requests
- Dotenv
