import streamlit as st
import tweepy
import zipfile
import os
import tempfile
import schedule
import time
from datetime import datetime, timedelta

# Function to authenticate to Twitter
def authenticate_to_twitter(api_key, api_secret_key, access_token, access_token_secret):
    auth = tweepy.OAuth1UserHandler(api_key, api_secret_key, access_token, access_token_secret)
    return tweepy.API(auth)

# Function to upload and post an image with a caption
def post_image(api, image_path, caption):
    try:
        api.update_with_media(image_path, status=caption)
        st.write(f"Posted image: {image_path}")
    except Exception as e:
        st.write(f"Failed to post image: {image_path}, error: {e}")

# Function to schedule all images
def schedule_images(api, image_folder, caption, frequency, interval):
    images = [os.path.join(image_folder, img) for img in os.listdir(image_folder) if img.lower().endswith(('jpg', 'jpeg', 'png', 'gif'))]
    start_date = datetime.now()
    
    for i, image in enumerate(images):
        schedule_time = start_date + timedelta(**{frequency: i * interval})
        schedule.every(interval).seconds.do(post_image, api=api, image_path=image, caption=caption)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

# Streamlit app layout
st.title("Automated Twitter Posting Tool")

st.header("Step 1: Enter Twitter API Credentials")
api_key = st.text_input("API Key")
api_secret_key = st.text_input("API Secret Key")
access_token = st.text_input("Access Token")
access_token_secret = st.text_input("Access Token Secret")

st.header("Step 2: Upload Images and Set Caption")
uploaded_file = st.file_uploader("Upload a ZIP file containing images", type=["zip"])
caption = st.text_input("Enter a caption for the images", value="made with brAInstormer")

st.header("Step 3: Set Posting Frequency")
frequency_option = st.selectbox("Select Frequency", ["Hourly", "Daily"])
interval = st.number_input("Interval", min_value=1, max_value=24, value=1, step=1)

if frequency_option == "Hourly":
    frequency = 'hours'
else:
    frequency = 'days'

if st.button("Start Posting Images"):
    if api_key and api_secret_key and access_token and access_token_secret and uploaded_file:
        with tempfile.TemporaryDirectory() as tmp_dir:
            with zipfile.ZipFile(uploaded_file, "r") as zip_ref:
                zip_ref.extractall(tmp_dir)
            
            st.write("Images extracted and ready to be posted.")
            
            # Authenticate to Twitter
            api = authenticate_to_twitter(api_key, api_secret_key, access_token, access_token_secret)
            
            # Schedule images
            schedule_images(api, tmp_dir, caption, frequency, interval)
            st.write("Posting scheduled. The app will handle posting automatically.")
    else:
        st.write("Please fill in all fields.")
