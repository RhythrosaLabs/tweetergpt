import streamlit as st
import tweepy
import zipfile
import os
import tempfile
import schedule
import time
from datetime import datetime, timedelta

# Twitter API credentials
API_KEY = 'your_api_key'
API_SECRET_KEY = 'your_api_secret_key'
ACCESS_TOKEN = 'your_access_token'
ACCESS_TOKEN_SECRET = 'your_access_token_secret'

# Authenticate to Twitter
auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET_KEY, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

# Function to upload and post an image with a caption
def post_image(image_path, caption):
    try:
        api.update_with_media(image_path, status=caption)
        st.write(f"Posted image: {image_path}")
    except Exception as e:
        st.write(f"Failed to post image: {image_path}, error: {e}")

# Function to schedule all images
def schedule_images(image_folder, caption):
    images = [os.path.join(image_folder, img) for img in os.listdir(image_folder) if img.lower().endswith(('jpg', 'jpeg', 'png', 'gif'))]
    start_date = datetime.now()
    
    for i, image in enumerate(images):
        schedule_time = start_date + timedelta(days=i)
        schedule.every().day.at(schedule_time.strftime("%H:%M")).do(post_image, image_path=image, caption=caption)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

# Streamlit app layout
st.title("Automated Twitter Posting Tool")

uploaded_file = st.file_uploader("Upload a ZIP file containing images", type=["zip"])
caption = st.text_input("Enter a caption for the images", value="made with brAInstormer")

if uploaded_file and caption:
    # Extract ZIP file to a temporary directory
    with tempfile.TemporaryDirectory() as tmp_dir:
        with zipfile.ZipFile(uploaded_file, "r") as zip_ref:
            zip_ref.extractall(tmp_dir)
        
        st.write("Images extracted and ready to be posted.")
        
        if st.button("Start Posting Images"):
            schedule_images(tmp_dir, caption)
            st.write("Posting scheduled. Check your Twitter feed for updates.")
