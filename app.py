"""
Main application file for the TalentScout AI Hiring Assistant.

This script runs a Streamlit web application that serves as an interactive chatbot
for the initial screening of job candidates. The chatbot follows a structured
conversation flow, gathers essential candidate information, and generates
technical questions based on the candidate's declared tech stack.

The application uses Google's Gemini 1.5 Flash model and manages the conversation
through a state machine.
"""

import streamlit as st
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
from prompts import SYSTEM_PROMPT, INITIAL_GREETING, get_question_generation_prompt, get_sentiment_analysis_prompt

def load_css(file_name):
    """Function to load and inject a local CSS file."""
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# --- Configuration and Initialization ---
load_dotenv()
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
except (AttributeError, TypeError):
    st.error("Error: The GOOGLE_API_KEY was not found. Please create a .env file and set your key.")
    st.stop()

# Set up the Streamlit page
st.set_page_config(
    page_title="TalentScout Hiring Assistant",
    page_icon="🤖"
)
st.title("🤖 TalentScout Hiring Assistant")

# --- UI Enhancements ---
load_css("style.css")

# --- Model Definitions ---
# By wrapping model loading in functions with @st.cache_resource, we ensure
# these heavy models are loaded only once, improving performance.

@st.cache_resource
def load_conversation_model():
    """Loads and caches the conversational model with its system prompt."""
    print("--- Loading Conversation Model ---") 
    return genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        system_instruction=SYSTEM_PROMPT
    )

@st.cache_resource
def load_qgen_model():
    """Loads and caches the question generation model."""
    print("--- Loading QGen Model ---") 
    return genai.GenerativeModel(model_name='gemini-1.5-flash')

# Load the models using the cached functions
model_conversation = load_conversation_model()
model_qgen = load_qgen_model()

# --- State Management ---
# The application follows a state machine to manage the conversation flow.
# CONVERSATION: Initial information gathering.
# QUESTION_GENERATION: A transient state to generate technical questions.
# TECHNICAL_INTERVIEW: Asking the generated technical questions.
# CONCLUSION: Final state to end the conversation.
if 'chat_state' not in st.session_state:
    st.session_state.chat_state = 'CONVERSATION'
    # 'messages' is our single source of truth for displaying the chat history.
    st.session_state.messages = [] 
    # 'chat_session' manages the conversation context with the LLM.
    st.session_state.chat_session = model_conversation.start_chat(history=[])

def add_message_to_display(role, content):
    """
    Adds a message to the display list (st.session_state.messages).
    This is the only function that should modify the display history.
    
    Args:
        role (str): The role of the message sender ('user' or 'assistant').
        content (str): The content of the message.
    """
    st.session_state.messages.append({"role": role, "content": content})


# --- Chat History Display ---
# Render the chat history from our managed list of messages.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# --- Initial Greeting ---
# If the chat is new, display the initial greeting from the assistant.
if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown(INITIAL_GREETING)
    add_message_to_display("assistant", INITIAL_GREETING)


# --- Main Chat Logic ---
# Wait for and process user input.
if prompt := st.chat_input("Please enter your response..."):
    # Add and display the user's message immediately.
    add_message_to_display("user", prompt)
    with st.chat_message("user"):
        st.markdown(prompt)

    # --- STATE: CONVERSATION ---
    if st.session_state.chat_state == 'CONVERSATION':
        # Check if the last bot message was asking for the tech stack to trigger a state change.
        last_bot_message = st.session_state.messages[-2]['content']
        is_asking_for_tech_stack = "tech stack" in last_bot_message.lower()

        if is_asking_for_tech_stack:
            # User has provided the tech stack, switch to question generation.
            st.session_state.tech_stack = prompt
            st.session_state.chat_state = 'QUESTION_GENERATION'
            
            with st.spinner("Analyzing your tech stack and preparing questions..."):
                # Generate the specific prompt for the question generation model.
                question_prompt = get_question_generation_prompt(st.session_state.tech_stack)
                # Use the 'untainted' model_qgen for this one-off task.
                response = model_qgen.generate_content(question_prompt)
                
                try:
                    # Clean the model's response to ensure it's valid JSON.
                    clean_response_text = response.text.strip().replace("```json", "").replace("```", "")
                    questions_json = json.loads(clean_response_text)
                    st.session_state.questions = questions_json["questions"]
                    
                    # Transition to the interview state and ask the first question.
                    st.session_state.chat_state = 'TECHNICAL_INTERVIEW'
                    st.session_state.question_index = 0
                    
                    next_question = st.session_state.questions[0]
                    add_message_to_display("assistant", next_question)
                    with st.chat_message("assistant"):
                        st.markdown(next_question)

                except (json.JSONDecodeError, KeyError, IndexError) as e:
                    # Handle failures in question generation gracefully.
                    error_message = "I had a little trouble generating specific questions. Let's try again. Could you please list just your top 2-3 main technologies?"
                    add_message_to_display("assistant", error_message)
                    with st.chat_message("assistant"):
                        st.markdown(error_message)
                    # Revert state to allow the user to try again.
                    st.session_state.chat_state = 'CONVERSATION'
        
        else:
            # Continue the standard information-gathering conversation.
            response = st.session_state.chat_session.send_message(prompt)
            add_message_to_display("assistant", response.text)
            with st.chat_message("assistant"):
                st.markdown(response.text)

    # --- STATE: TECHNICAL INTERVIEW ---
    elif st.session_state.chat_state == 'TECHNICAL_INTERVIEW':
        # The user has answered a technical question.
        # --- NEW: Sentiment Analysis Bonus Feature ---
        user_answer = prompt
        with st.spinner("Analyzing sentiment..."):
            # We use the qgen_model as it's our "tool" model with no system prompt
            sentiment_prompt = get_sentiment_analysis_prompt(user_answer)
            sentiment_response = model_qgen.generate_content(sentiment_prompt)
            
            # Print the sentiment to the terminal for the reviewer to see.
            # This demonstrates the capability without cluttering the UI.
            sentiment = sentiment_response.text.strip()
            print(f"--- Candidate Sentiment Detected: {sentiment} ---")
            # In a real application, this sentiment could be stored in a database
            # alongside the candidate's answer.
        # --- End of Sentiment Analysis ---


        # The assignment only requires us to *ask* the questions, not evaluate the answers.
        st.session_state.question_index += 1
        
        if st.session_state.question_index < len(st.session_state.questions):
            # Ask the next question.
            ack_message = "Thank you. Here is your next question:"
            add_message_to_display("assistant", ack_message)
            with st.chat_message("assistant"):
                st.markdown(ack_message)

            next_question = st.session_state.questions[st.session_state.question_index]
            add_message_to_display("assistant", next_question)
            with st.chat_message("assistant"):
                st.markdown(next_question)
        else:
            # All questions have been asked, move to conclusion.
            st.session_state.chat_state = 'CONCLUSION'
            conclusion_message = "Thank you for answering all the questions. That concludes the initial screening! The TalentScout team will review your profile and get in touch with you soon if there's a match. Have a wonderful day!"
            add_message_to_display("assistant", conclusion_message)
            with st.chat_message("assistant"):
                st.markdown(conclusion_message)

