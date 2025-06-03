from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings

import json
import os
import yt_dlp
import assemblyai as aai
import logging
import cohere
from .models import BlogPost
from django.shortcuts import get_object_or_404

# Home Page
@login_required
def index(request):
    return render(request, 'index.html')

# Blog Generator View
@csrf_exempt
@login_required
def generate_blog(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    try:
        data = json.loads(request.body)
        yt_link = data.get('link')
        if not yt_link:
            return JsonResponse({'error': 'Missing YouTube link'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    title = yt_title(yt_link)
    if not title:
        return JsonResponse({'error': 'Unable to fetch YouTube title. Please check the link.'}, status=400)

    transcription = get_transcription(yt_link)
    if not transcription:
        return JsonResponse({'error': 'Failed to transcribe video'}, status=500)

    blog_content = generate_blog_from_transcription(transcription)
    if not blog_content:
        return JsonResponse({'error': 'Failed to generate blog'}, status=500)

    new_blog_article = BlogPost.objects.create(
        user=request.user,
        youtube_title=title,
        youtube_link=yt_link,
        generated_content=blog_content,
    )
    new_blog_article.save()

    return JsonResponse({'title': title, 'content': blog_content})

# Get YouTube video title
def yt_title(link):
    try:
        ydl_opts = {'quiet': True, 'skip_download': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=False)
            return info.get('title')
    except Exception:
        logging.exception("Error fetching YouTube title")
        return None

# Download audio from YouTube
def download_audio(link):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(settings.MEDIA_ROOT, '%(title)s.%(ext)s'),
            'quiet': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=True)
            filename = f"{info['title']}.mp3"
            audio_path = os.path.join(settings.MEDIA_ROOT, filename)
            if os.path.exists(audio_path):
                return audio_path
            else:
                print(f"File not found at: {audio_path}")
                return None
    except Exception as e:
        logging.exception(f"Error downloading audio: {e}")
        return None


# Transcribe audio using AssemblyAI
def get_transcription(link):
    audio_file = download_audio(link)
    if not audio_file:
        logging.error("Audio file could not be downloaded.")
        return None

    aai.settings.api_key = settings.ASSEMBLYAI_API_KEY
    transcriber = aai.Transcriber()

    try:
        transcript = transcriber.transcribe(audio_file)
        return transcript.text
    except Exception:
        logging.exception("Error during transcription")
        return None

# Generate blog from transcription using Cohere
def generate_blog_from_transcription(transcription):
    try:
        co = cohere.Client(settings.COHERE_API_KEY)
        prompt = (
            "Write a high-quality, well-structured, informative blog post based on this video transcript. "
            "The content should be engaging and not merely repeat the transcript.\n\n"
            f"Transcript:\n{transcription}\n\nBlog Post:"
        )
        response = co.generate(
            model="command-r-plus",
            prompt=prompt,
            max_tokens=1000,
            temperature=0.7
        )
        return response.generations[0].text.strip()
    except Exception:
        logging.exception("Error generating blog using Cohere")
        return None

# Show all blogs
@login_required
def blog_list(request):
    blog_articles = BlogPost.objects.filter(user=request.user)
    return render(request, "all_blogs.html", {'blog_articles': blog_articles})
#Blog article details 
def blog_details(request, pk):
    blog_article_detail = get_object_or_404(BlogPost, id=pk)
    if request.user == blog_article_detail.user:
        return render(request, 'blog_details.html', {'blog_article_detail': blog_article_detail})
    else:
        return redirect('/')


# User login view
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        return render(request, 'login.html', {'error_message': 'Invalid credentials'})
    return render(request, 'login.html')

# User signup view
def user_signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        repeat_password = request.POST['repeatPassword']

        if password != repeat_password:
            return render(request, 'signup.html', {'error_message': 'Passwords do not match'})

        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            return redirect('/')
        except IntegrityError:
            return render(request, 'signup.html', {'error_message': 'Username already exists'})
        except Exception as e:
            return render(request, 'signup.html', {'error_message': str(e)})

    return render(request, 'signup.html')

# Logout view
def user_logout(request):
    logout(request)
    return redirect('/login/')
