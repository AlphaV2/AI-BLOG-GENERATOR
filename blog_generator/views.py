import json
from django.shortcuts import render
import httpx # We'll use this library to make HTTP requests
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

def home(request):
    """
    Renders the main page and handles form submissions to generate a blog post.
    """
    generated_content = {}
    if request.method == 'POST':
        # Get the topic and keywords from the form submission.
        topic = request.POST.get('topic', '')
        keywords = request.POST.get('keywords', '')

        # Construct the prompt for the AI model to request a structured response.
        # We ask for a title, introduction, body with subheadings, and a conclusion.
        prompt = f"""
        Generate a comprehensive and well-structured blog post on the topic: '{topic}'.
        The blog post should be written in a professional yet engaging tone with story telling capabilities, use  metaphors and hooks to engage more users.

        The response should be structured as follows:
        - A compelling title.
        - An engaging introduction paragraph of why we need this technology/concept/topic with real life application .
        - A body of at least 500 words, broken down into multiple  paragraphs and sections with bold subheadings and relevant examples.
        - A concluding paragraph that summarizes the key points.
        
        The content must incorporate the following keywords: {keywords}.
        Please return the response as a single, well-formatted Markdown string.
        """

        # Prepare the payload for the Gemini API call.
        chat_history = []
        chat_history.append({"role": "user", "parts": [{"text": prompt}]})
        payload = {"contents": chat_history}

        # API URL and key.
        api_key = os.getenv("API_KEY")
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={api_key}"

        # Make the API call to the Gemini API using httpx.
        try:
            response = httpx.post(api_url, json=payload, timeout=60)
            response.raise_for_status() # Raise an exception for bad status codes

            result = response.json()
            
            # Extract the generated text from the API response.
            if result.get("candidates"):
                generated_content['blog_post'] = result["candidates"][0]["content"]["parts"][0]["text"]
            else:
                generated_content['blog_post'] = "Sorry, I could not generate a blog post. Please try again with a different prompt."

        except Exception as e:
            # Handle any errors during the API call.
            generated_content['error'] = f"An error occurred: {e}"

        # Render the template with the generated text.
        return render(request, 'index.html', {'content': generated_content})

    # Render the initial page with no generated text.
    return render(request, 'index.html', {'content': generated_content})
