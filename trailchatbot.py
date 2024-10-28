import requests
import os
from openai import OpenAI
import streamlit as st

# Initialize OpenAI client
client = OpenAI(api_key='')

# Text generation feature and role for system
def get_completion(prompt, model="gpt-3.5-turbo"):
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "As an expert in nature trails, provide recommendations for creekside trails based on location, difficulty level, and visitor preferences."},
                {"role": "user", "content": prompt},
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        st.error(f"Error generating trail recommendation: {e}")
        return None

# Download images from generation
def download_image(filename, url):
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as file:
            file.write(response.content)
    else:
        st.error(f"Error downloading image from URL: {url}")

# Generates filename from user input
def filename_from_input(prompt):
    alphanum = "".join([char if char.isalnum() or char == " " else "" for char in prompt])
    words = alphanum.split()[:3]
    return "_".join(words)

# Create an image from a prompt in DALL-E-2
def get_image(prompt, model="dall-e-2"):
    n = 2  # Number of images to generate
    trail_prompt = f"creekside trail environment based on {prompt}"
    try:
        images = client.images.generate(
            prompt=trail_prompt,
            model=model,
            n=n,
            size="1024x1024"
        )
        filenames = []
        for i in range(n):
            filename = f"{filename_from_input(trail_prompt)}_{i + 1}.png"
            download_image(filename, images.data[i].url)
            filenames.append(filename)  
        return filenames 
    except Exception as e:
        st.error(f"Error generating image: {e}")
        return None

# Function for hiking information
def get_hiking_info(category, model="gpt-3.5-turbo"):
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert on hiking safety and trail information. Provide detailed, practical advice about hiking concerns and safety measures."},
                {"role": "user", "content": f"Provide comprehensive information about {category} on hiking trails, including potential risks and safety tips."}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        st.error(f"Error generating information: {e}")
        return None

# Streamlit App
st.title("Creekside Trail Explorer")
st.write("Get personalized creekside trail recommendations based on your preferences and location. Optionally, view generated images for a visual impression of the trails.")

# Sidebar for chat input and image generating
with st.sidebar:
    st.header("Trail Explorer Chat")
    messages = st.container()

    # Sidebar history storage
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # User input
    prompt = st.chat_input("Describe the type of trail (location, difficulty):")

    # Checkbox for image generation
    generate_images = st.checkbox("Generate personalized image based on prompt description?", value=True)

    if prompt:
        # Append user prompt to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})

        # Generate text response
        text_response = get_completion(prompt)

        # Save assistant response to history
        st.session_state.chat_history.append({"role": "assistant", "content": text_response})

        # Display chat history in the sidebar
        with messages:
            for message in st.session_state.chat_history:
                if message["role"] == "user":
                    messages.chat_message("user").write(message["content"])
                else:
                    messages.chat_message("assistant").write(message["content"])

        # Display generated images in main area if selected
        if generate_images:
            image_filenames = get_image(prompt) 
            st.subheader("Generated Trail Images:")
            if image_filenames:
                for i, display_filename in enumerate(image_filenames):
                    if os.path.exists(display_filename):
                        st.image(display_filename, caption=f"Image {i + 1} based on: {prompt}", use_column_width=True)
                    else:
                        st.warning(f"Image file {display_filename} not found.")

# Trail Information Guide Section
st.subheader("Trail Information Guide")
st.write("Select a topic to learn more about common hiking concerns and safety measures.")

# Create dropdown menu with expanded categories
category = st.selectbox(
    "What would you like to know about?",
    options=[
        "Wildlife Encounters & Safety",
        "Plant Hazards & Identification",
        "Weather Safety & Preparation",
        "Navigation & Trail Markers",
        "First Aid & Emergency Response",
        "Gear & Equipment Essentials",
        "Water Safety & Hydration",
        "Trail Etiquette & Rules",
        "Seasonal Hiking Tips",
        "Physical Preparation & Fitness"
    ]
)

# Generate and display information when category is selected
if category:
    st.write(f"### {category}")
    
    # Add a loading spinner while generating content
    with st.spinner(f"Generating information about {category}..."):
        response = get_hiking_info(category)
        
        if response:
            # Display the generated information in a nice format
            st.markdown(response)
            
            # Add a helpful tip box
            st.info("💡 **Pro Tip**: Save this information for offline reference when hiking!")

# AllTrails Section
st.markdown("## For More Creekside Trail Recommendations")

# Create columns for better layout
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # Display AllTrails logo image
    image_path = "alltrail.png"
    if os.path.exists(image_path):
        st.image(image_path, caption="AllTrails - Discover More Trails", use_column_width=True)
    else:
        st.warning("The 'alltrail.png' image was not found in the directory.")
    
    # Create a styled button that links to AllTrails
    st.markdown(
        """
        <div style='text-align: center'>
            <a href='https://www.alltrails.com/?ref=header' target='_blank'>
                <button style='
                    background-color: #2E7D32;
                    color: white;
                    padding: 10px 24px;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 16px;
                    margin: 10px 0;
                    width: 100%;
                '>
                    Explore Creekside Trails on AllTrails
                </button>
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )
