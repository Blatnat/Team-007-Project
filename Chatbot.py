import streamlit as st
import openai

# Set up OpenAI API key Carlos
openai.api_key = 'Your-API-KeY'

# Helper function to generate assistant's response
def get_completion(prompt, model="gpt-3.5-turbo-instruct"):
    # Adjust model name as needed for latest OpenAI models
    response = openai.completions.create(
        model=model,
        prompt=prompt,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.7,
    )
    return response.choices[0].text.strip()

# Streamlit app title and session state setup
st.set_page_config(page_title="Trail Explorer Chatbot", page_icon="🏞️", layout="wide")
st.title("🤖🌄 Trail Explorer Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []  # Initialize chat history

# Display chat history 
chat_container = st.container()
with chat_container:
    st.subheader("Chat History")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# User input in the chat
user_input = st.chat_input("Ask a question about trails, locations, or difficulty levels:")
if user_input:
    # Show user's message in chat
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Add user's message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Generate assistant's response and update chat history
    assistant_response = get_completion(user_input)
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})

    # Display assistant's response in chat
    with st.chat_message("assistant"):
        st.markdown(assistant_response)

# Sidebar for trail exploration input
with st.sidebar:
    st.header("🌿 Trail Query")
    st.info("Provide details about trails such as location, difficulty, and features.")
    trail_description = st.text_area("Describe the trail (location, difficulty, features):")

    if trail_description:
        st.write("**User:**", trail_description)
        response = get_completion(trail_description)

        # Display assistant's response in the sidebar
        with st.expander("See response from Assistant"):
            st.write("**Assistant:**", response)

#UI styling
st.markdown(
    """
    <style>
    .stChatMessage {
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
    }
    .stChatMessageUser {
        background-color: #f0f9ff;
    }
    .stChatMessageAssistant {
        background-color: #e0ffe0;
    }
    </style>
    """,
    unsafe_allow_html=True
)
