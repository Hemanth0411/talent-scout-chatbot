# TalentScout AI Hiring Assistant

## Project Overview

This project is an intelligent AI Hiring Assistant chatbot created for "TalentScout," a fictional recruitment agency. The chatbot, named "Scout," is designed to conduct initial candidate screenings. It interactively gathers essential information (name, experience, etc.) and then dynamically generates and asks relevant technical questions based on the candidate's self-declared tech stack.

This enhanced version includes performance optimizations, a professionally styled UI, and real-time sentiment analysis to create a robust and polished user experience.

---

## Advanced Features & Enhancements (Bonus)

This project goes beyond the basic requirements by implementing several advanced features:

1.  **Performance Optimization:** The application uses Streamlit's `@st.cache_resource` decorator to cache the large language models. This means the models are loaded into memory only once at startup, significantly improving response times and application efficiency during user interaction.

2.  **Professional UI Enhancements:** The user interface has been restyled with custom CSS to provide a clean, modern, and professional aesthetic. This includes custom backgrounds, styled chat bubbles that align for user and assistant, and improved typography for better readability, mimicking popular messaging applications.

3.  **Real-time Sentiment Analysis:** During the technical interview phase, the application discreetly analyzes the sentiment of the candidate's answers. It uses a dedicated LLM call to classify the text as `Positive`, `Negative`, or `Neutral`. This demonstrates a deeper, multi-tasking use of AI and provides valuable (simulated) metadata for recruiters. The results are printed to the terminal to showcase this capability.

---

## Core Features

- **Structured Information Gathering:** A friendly, sequential conversation to collect candidate details.
- **Dynamic Technical Questioning:** Generates 3-5 unique technical questions based on the technologies a candidate provides.
- **Context-Aware Conversation:** Maintains the flow of the conversation using a state machine and a context-aware LLM session.
- **Robust Error Handling:** Includes fallback mechanisms for unexpected user inputs or LLM responses.

---

## Technical Details

- **Programming Language:** Python 3.10+
- **Frontend UI:** Streamlit with custom CSS
- **Large Language Model:** Google Gemini 1.5 Flash
- **Key Libraries:** `google-generativeai`, `streamlit`, `python-dotenv`

### Architectural Decisions

The application's architecture is centered around a state machine to manage the conversation flow. This was chosen over a single, massive prompt to provide more reliable control over the chatbot's behavior.

A key decision was to use **two separate, cached LLM instances**:
1.  **`model_conversation`**: This instance is configured with a detailed system prompt that defines the "Scout" persona and its strict rules for gathering information. This ensures the chatbot stays on task during the initial screening.
2.  **`model_qgen`**: This is a "clean" instance with no system prompt. Its purpose is to act as a general-purpose "tool" for one-off tasks like generating the JSON for technical questions and performing sentiment analysis. This separation prevents "prompt conflicts" and is crucial for the application's stability.

---

## Installation and Setup

To run this application locally, please follow these steps:

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/Hemanth0411/talent-scout-chatbot.git
    
    cd talent-scout-chatbot
    ```

2.  **Create a Virtual Environment:**
    ```bash
    # On macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # On Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up Environment Variables:**
    Create a file named `.env` in the root of the project directory. Add your Google Gemini API key to this file:
    ```
    GOOGLE_API_KEY='your_api_key_here'
    ```

---

## Usage Guide

Once the setup is complete, run the Streamlit application from your terminal:

```bash
streamlit run app.py
```

Your web browser will open a new tab with the chatbot interface. Simply follow the chatbot's prompts to complete the screening process. **To see the sentiment analysis in action, keep an eye on the terminal window where you launched the app while answering the technical questions.**

---

## Prompt Design

The chatbot's effectiveness relies on three core prompts located in `prompts.py`:

1.  **System Prompt (`SYSTEM_PROMPT`):** The master instruction set for the conversational agent ("Scout"). It defines its persona, goal, and strict rules, making the initial screening highly reliable.

2.  **Question Generation Prompt (`get_question_generation_prompt()`):** A one-shot prompt that includes a clear example of the desired JSON output. This structured output is crucial for allowing the application to easily parse the questions.

3.  **Sentiment Analysis Prompt (`get_sentiment_analysis_prompt()`):** A zero-shot prompt that instructs the model to classify text and respond with only a single word, making the output lightweight and easy to parse.

---

## Challenges & Solutions

**Challenge:** The LLM, after being given a strong system prompt to be an information gatherer, would refuse to switch tasks to generate technical questions.

**Solution:** This was resolved by implementing a two-model architecture. A primary model, configured with the system prompt, handles the conversation. A second, "clean" model instance is used exclusively for tool-like tasks (question generation, sentiment analysis). This separation of concerns completely resolved the prompt conflict.

**Challenge:** The LLM's JSON output was sometimes wrapped in markdown code blocks (` ```json ... ``` `), causing parsing to fail.

**Solution:** The application's code was made more robust by adding a cleaning step that strips these markdown artifacts from the LLM's text response before attempting to parse it as JSON.

**Challenge:** Reloading the large models on every user interaction would cause performance degradation.

**Solution:** Streamlit's `@st.cache_resource` was implemented to cache the models on their first load. This ensures high performance and a snappy user experience throughout the conversation.