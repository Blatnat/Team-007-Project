
import os
import openai
import base64
from typing import List, Optional
import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime
import folium
from streamlit_folium import st_folium
import googlemaps


# Initialize OpenAI client
openai.api_key = os.environ["OPENAI_API_KEY"]

# Configure page
st.set_page_config(
    page_title="Plant and Animal Visualizer - Creekside Trail Explorer",
    page_icon="🏞️",
    layout="wide"
)

# Sidebar Enhancement
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; padding: 1rem;'>
        <h2 style='color: #ffffff;'>💭 Trail Chat Assistant</h2>
    </div>
    """, unsafe_allow_html=True)
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Chat container
    messages = st.container()
    with messages:
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.write(message["content"])
    
    # Chat input with styling
    prompt = st.chat_input("Ask about trails...")
    if prompt:
        st.session_state.chat_history.append({"role": "user", "content": prompt})

#Alvin Liu UI work
# Enhanced CSS with nature theme
st.markdown("""
    <style>
        .stApp {
            background-color: #f5f7f9;
        }
        
        .main-header {
            color: #2c3e50;
            font-family: 'Helvetica Neue', sans-serif;
            padding: 1.5rem 0;
            text-align: center;
            background: linear-gradient(90deg, #a8e6cf 0%, #dcedc1 100%);
            border-radius: 10px;
            margin-bottom: 2rem;
        }
        
        h1, h2, h3, h4 {
            color: black !important;
            font-family: 'Helvetica Neue', sans-serif;
            margin-bottom: 1rem;
        }
        
        .stButton>button {
            border-radius: 20px;
            background-color: #3498db;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            transition: background-color 0.3s;
        }
        
        .stButton>button:hover {
            background-color: #2980b9;
        }
        
        .stTabs [data-baseweb="tab"] {
            color: black !important;
            font-weight: 500;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            background-color: #ffffff;
            border-radius: 10px;
            padding: 0.5rem;
            margin-bottom: 1rem;
        }
        
        .upload-text, .stMarkdown p {
            color: black !important;
            margin: 1rem 0;
        }
        
        .analysis-result {
            color: black !important;
            background-color: #ffffff;
            padding: 1rem;
            border-radius: 10px;
            margin-top: 1rem;
        }
        
        .stSelectbox {
            color: black;
        }
        
        .stTextInput>div>div {
            color: black;
        }
        
        .stInfo {
            background-color: rgba(168, 230, 207, 0.2);
            border: 1px solid #a8e6cf;
        }
        
        .stFileUploader {
            background-color: white;
            padding: 1rem;
            border-radius: 10px;
            border: 2px dashed #a8e6cf;
        }
        
        .caption {
            color: black !important;
            font-style: italic;
            text-align: center;
            margin-top: 0.5rem;
        }
    </style>
""", unsafe_allow_html=True)

#Dandy Bien (Wildlife Visualizer)
# Creek Trail Species Data
CREEK_TRAIL_SPECIES = {
    "Plant": {
        "Trees": ["Western Red Cedar", "Red Alder", "Big Leaf Maple", "Western Hemlock", "Black Cottonwood"],
        "Shrubs": ["Salmonberry", "Oregon Grape", "Red Elderberry", "Thimbleberry", "Indian Plum"],
        "Ferns & Ground Cover": ["Sword Fern", "Lady Fern", "Maidenhair Fern", "Wild Ginger", "False Solomon's Seal"],
        "Wildflowers": ["Trillium", "Stream Violet", "Skunk Cabbage", "Pacific Bleeding Heart", "Wood Sorrel"]
    },
    "Animal": {
        "Birds": ["American Dipper", "Great Blue Heron", "Belted Kingfisher", "Wood Duck", "Pacific Wren"],
        "Mammals": ["River Otter", "Black-tailed Deer", "Raccoon", "Douglas Squirrel", "Beaver"],
        "Amphibians": ["Pacific Tree Frog", "Red-legged Frog", "Pacific Giant Salamander", "Rough-skinned Newt", "Western Toad"],
        "Fish": ["Cutthroat Trout", "Coho Salmon", "Steelhead", "Pacific Lamprey", "Sculpin"]
    }
}

# Helper Functions
def encode_uploaded_image(uploaded_file) -> str:
    """Encode uploaded image to base64 string."""
    return base64.b64encode(uploaded_file.getbuffer()).decode('utf-8')

def analyze_image(uploaded_file) -> str:
    """Analyze uploaded image using OpenAI's GPT-4 Vision."""
    try:
        base64_image = encode_uploaded_image(uploaded_file)
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": "What is in this image? Please identify and describe any plants, animals, and natural features."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error analyzing image: {str(e)}"

def download_image(filename: str, url: str) -> None:
    """Download image from URL and save to file."""
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as file:
            file.write(response.content)
    else:
        st.error(f"Error downloading image from URL: {url}")

def filename_from_input(prompt: str) -> str:
    """Generate filename from input prompt."""
    alphanum = "".join(char if char.isalnum() or char == " " else "" for char in prompt)
    return "_".join(alphanum.split()[:3])

def get_image(prompt: str, category: str, model: str = "dall-e-3") -> Optional[List[str]]:
    """Generate image using OpenAI's DALL-E."""
    if category == "Plant":
        base_prompt = "Detailed botanical illustration of"
    else:
        base_prompt = "Detailed wildlife illustration of"
        
    full_prompt = f"{base_prompt} {prompt} in its natural creek trail habitat, photorealistic style"
    
    try:
        images = openai.Image.create(
            prompt=full_prompt,
            model=model,
            n=1,
            size="1024x1024"
        )
        filenames = []
        for i, image_data in enumerate(images.data):
            filename = f"{filename_from_input(prompt)}_{i + 1}.png"
            download_image(filename, image_data.url)
            filenames.append(filename)
        return filenames
    except Exception as e:
        st.error(f"Error generating image: {e}")
        return None

def main():
    # Main header with enhanced nature theme
    st.markdown("""
        <div class="main-header">
            <h1>🌿 Creek Trail Species Explorer</h1>
            <p style='font-size: 1.2em; color: #34495e;'>
                Discover and document the diverse wildlife and plants along our creek trails
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Create tabs with nature-themed icons
    tab1, tab2 = st.tabs(["🎨 Generate Illustrations", "🔍 Analyze Images"])

    with tab1:
        st.markdown("<h3 style='color: black;'>Generate Species Illustrations</h3>", unsafe_allow_html=True)
        st.markdown("""
            <p style='color: black;'>
            1. Select a category (Plant/Animal)<br>
            2. Choose a specific species or enter your own<br>
            3. Click 'Generate' to create a detailed illustration
            </p>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 2])
        with col1:
            category = st.selectbox("Choose category", ["Plant", "Animal"])

        with col2:
            subcategory = st.selectbox(
                f"Select {category.lower()} type",
                list(CREEK_TRAIL_SPECIES[category].keys())
            )
            species_selection = st.selectbox(
                "Select species or enter custom",
                ["Custom Entry"] + CREEK_TRAIL_SPECIES[category][subcategory]
            )
            
            if species_selection == "Custom Entry":
                species_description = st.text_input(
                    f"Enter custom {category.lower()} description",
                    placeholder=f"e.g., {CREEK_TRAIL_SPECIES[category][subcategory][0]}"
                )
            else:
                species_description = species_selection

        if st.button("🎨 Generate Illustration", type="primary") and species_description:
            with st.spinner(f"Creating illustration of {species_description}..."):
                if image_filenames := get_image(species_description, category):
                    st.markdown(f"<h4 style='color: black;'>Your {category} Illustration:</h4>", unsafe_allow_html=True)
                    for filename in image_filenames:
                        if os.path.exists(filename):
                            st.image(filename, use_container_width=True)
                            st.markdown(
                                f"<p class='caption'>AI-generated illustration of {species_description} in its natural habitat</p>",
                                unsafe_allow_html=True
                            )
                        else:
                            st.warning("Could not generate illustration. Please try again.")
#Alvin Liu (Image Analysis)
    with tab2:
        st.markdown("<h3 style='color: black;'>Analyze Trail Images</h3>", unsafe_allow_html=True)
        st.markdown("""
            <p style='color: black;'>
            1. Upload a photo from your trail explorations<br>
            2. Click 'Analyze' to identify species<br>
            3. Get detailed information about what's in your image
            </p>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Upload a trail image",
            type=['jpg', 'jpeg', 'png'],
            help="Upload a clear photo of plants, animals, or landscapes from your trail adventures"
        )
        
        if uploaded_file:
            st.image(uploaded_file, caption="Your uploaded image", use_container_width=True)
            
            if st.button("🔍 Analyze Image", type="primary"):
                with st.spinner("Analyzing your image..."):
                    if analysis_result := analyze_image(uploaded_file):
                        st.markdown("<h4 style='color: black;'>Analysis Results</h4>", unsafe_allow_html=True)
                        st.markdown(
                            f"<div class='analysis-result'>{analysis_result}</div>",
                            unsafe_allow_html=True
                        )
                        st.info("💡 Analysis powered by AI. Always verify findings with local expertise.")

    # Nature-themed footer
    st.markdown("""
        <div style='text-align: center; padding: 2rem; margin-top: 3rem; color: black;'>
            <p>Created with 🌿 for trail explorers and nature enthusiasts</p>
            <p style='font-size: 0.8em;'>© 2024 Creekside Trail Explorer | Preserving and celebrating our natural heritage</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
