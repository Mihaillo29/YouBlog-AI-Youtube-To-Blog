import re
import streamlit as st
import textwrap
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai

def to_markdown(text):
    text = text.replace('•', '  *')
    return textwrap.indent(text, '>', predicate=lambda _: True)

# Function to extract YouTube video ID from URL
def get_youtube_video_id(url):
    video_id_regex_list = [
        r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})',
        r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]+)'
    ]
    for regex in video_id_regex_list:
        match = re.search(regex, url)
        if match:
            return match.group(1)
    return None

# Function to get transcript from YouTube video
def get_transcript(url):
    video_id = get_youtube_video_id(url)
    img_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
    transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
    transcript_text = " ".join(entry['text'] for entry in transcript_list)
    return [transcript_text,img_url]


KEY = "YOUR_API_KEY"  # Replace with your actual Google API key
genai.configure(api_key=KEY)


st.set_page_config(page_title="YouTube to Blog Converter", layout="wide")

st.title("🎥 YouTube to Blog Converter")
st.write("Enter a YouTube URL to generate a blog post from its transcript.")


youtube_url = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=example")


if st.button("Generate Blog Post"):
    if youtube_url:

        with st.spinner("Retrieving transcript..."):
            transcript,img_url = get_transcript(youtube_url)
            st.image(img_url,caption="Video Thumbnail")


        if transcript:
 
            with st.spinner("Generating blog..."):

                prompt = f"Create this a blog: {transcript}"
                model_name = "gemini-1.0-pro-latest"
                generation_config = {}  

                model = genai.GenerativeModel(model_name=model_name, generation_config=generation_config)

                response = model.generate_content(prompt)

            st.subheader("Generated Blog Post")
            blog_post = response.text
            st.markdown(to_markdown(blog_post))       
            st.button("Copy to Clipboard", on_click=st.experimental_set_query_params, kwargs={"blog": blog_post})

            st.video(youtube_url)
        else:
            st.write("Failed to retrieve transcript. Please check the YouTube URL and try again.")
    else:
        st.write("Please enter a YouTube URL.")
