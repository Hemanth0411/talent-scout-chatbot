import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from prompts import SYSTEM_PROMPT, INITIAL_GREETING

# --- Configuration ---
load_dotenv()
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
except (AttributeError, TypeError):
    st.error("The GOOGLE_API_KEY was not found. Please set it in your .env file.")
    st.stop()

# --- Model and State Initialization ---
st.set_page_config(
    page_title="TalentScout Assistant",
    page_icon="🤖"
)

st.title("🤖 TalentScout Hiring Assistant")

# Initialize the Gemini model
model = genai.GenerativeModel(
    'gemini-1.5-flash',
    system_instruction=SYSTEM_PROMPT
)

# Initialize chat session in Streamlit's session state
if "chat_session" not in st.session_state:
    # Add the initial greeting to the history as a dictionary
    initial_history = [{'role': 'model', 'parts': [{'text': INITIAL_GREETING}]}]
    st.session_state.chat_session = model.start_chat(history=initial_history)
else:
    # If session exists, just reload it (Streamlit re-runs script)
    # The history is already preserved in st.session_state.chat_session
    pass

# --- Chat History Management ---
# Display chat history from the session
for message in st.session_state.chat_session.history:
    # CORRECTED: Access role and text safely for both object types
    role = "assistant" if message.role == "model" else message.role
    with st.chat_message(role):
        st.markdown(message.parts[0].text)


# --- User Interaction ---
if prompt := st.chat_input("Please enter your response here..."):
    # Display user's message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Send user's message to the Gemini model
    try:
        response = st.session_state.chat_session.send_message(prompt)
        # Display model's response
        with st.chat_message("assistant"):
            st.markdown(response.text)
    except Exception as e:
        st.error(f"An error occurred: {e}")