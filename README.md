


````markdown
# AI Blog Article Generator

A Django web application that generates blog articles based on YouTube video transcripts. Users can submit YouTube video links, and the app transcribes the audio, then uses AI to create high-quality blog posts from the transcription.

---

## Features

- User authentication (signup, login, logout)
- YouTube video audio extraction and transcription (using AssemblyAI)
- Blog article generation from transcription (using Cohere API)
- Save and view generated blog posts
- Secure access to blog generation and viewing features

---

## AI Services Used

- **AssemblyAI**: For automatic transcription of YouTube video audio.
- **Cohere**: For natural language generation of blog content based on the transcript.

---

## Setup Instructions

### Prerequisites

- Python 3.10+
- Django 4.x
- `yt_dlp` for YouTube audio extraction
- API keys for AssemblyAI and Cohere

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/darkraider01/Ai-blog-article-generator.git
   cd Ai-blog-article-generator
````

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate    # On Windows: venv\Scripts\activate
   ```

3. Install required packages:

   ```bash
   pip install -r requirements.txt
   ```

4. Set environment variables or add the following keys to your Django `settings.py` file:

   ```python
   # settings.py
   ASSEMBLYAI_API_KEY = 'your_assemblyai_api_key_here'
   COHERE_API_KEY = 'your_cohere_api_key_here'
   MEDIA_ROOT = BASE_DIR / 'media'  # Ensure this directory exists or is created
   ```

5. Run migrations and start the server:

   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

---

## How to Switch from Cohere to OpenAI API for Blog Generation

If you prefer to use OpenAI's GPT API instead of Cohere for generating blog posts, follow these steps:

1. **Install OpenAI Python client:**

   ```bash
   pip install openai
   ```

2. **Add your OpenAI API key to `settings.py`:**

   ```python
   OPENAI_API_KEY = 'your_openai_api_key_here'
   ```

3. **Modify the blog generation function in `views.py`:**

   Replace the current `generate_blog_from_transcription` function with the following:

   ```python
   import openai

   def generate_blog_from_transcription(transcription):
       try:
           openai.api_key = settings.OPENAI_API_KEY
           prompt = (
               "Write a high-quality, well-structured, informative blog post based on this video transcript. "
               "The content should be engaging and not merely repeat the transcript.\n\n"
               f"Transcript:\n{transcription}\n\nBlog Post:"
           )
           response = openai.Completion.create(
               engine="text-davinci-003",
               prompt=prompt,
               max_tokens=1000,
               temperature=0.7,
               n=1,
               stop=None,
           )
           return response.choices[0].text.strip()
       except Exception as e:
           logging.exception("Error generating blog using OpenAI")
           return None
   ```

4. **Remove or comment out the Cohere import and code:**

   ```python
   # import cohere
   ```

5. **Update your `requirements.txt`** to include OpenAI instead of Cohere:

   ```
   openai
   ```

---


---

## Notes

* Make sure the `media/` folder exists for storing downloaded audio files.
* Use Django's development server only for testing and development. For production, configure a proper WSGI/ASGI server.
* Protect your API keys and never commit them to public repositories. Use environment variables or Django’s secrets management.

---
Got it! Here’s the updated snippet to **add the PostgreSQL database setup info** in your `README.md` under a new section called **Database Configuration**:

---

````markdown
## Database Configuration

This project uses **PostgreSQL** as the database backend.

To configure your PostgreSQL database, update your `settings.py` with the following:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '',                     # Your PostgreSQL database name
        'USER': '',                 # Your PostgreSQL username
        'PASSWORD': '',       # Your PostgreSQL password
        'HOST': '',                  # Usually localhost for local setups
        'PORT': '',                       # Default PostgreSQL port
    }
}
````

### Steps to set up PostgreSQL locally

1. Install PostgreSQL if not already installed:
   [https://www.postgresql.org/download/](https://www.postgresql.org/download/)

2. Create a database and user matching the above credentials:

   ```bash
   psql postgres
   CREATE DATABASE yourdb;
   CREATE USER brandybuck WITH PASSWORD 'brandybuck04iam';
   ALTER ROLE brandybuck SET client_encoding TO 'utf8';
   ALTER ROLE brandybuck SET default_transaction_isolation TO 'read committed';
   ALTER ROLE brandybuck SET timezone TO 'UTC';
   GRANT ALL PRIVILEGES ON DATABASE yourdb TO brandybuck;
   \q
   ```

3. Run migrations to set up your database schema:

   ```bash
   python manage.py migrate
   ```

---

Make sure PostgreSQL service is running before you start the Django server.

---


