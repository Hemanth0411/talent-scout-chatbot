# TalentScout AI Hiring Assistant

## Project Overview

This project is an intelligent AI Hiring Assistant chatbot created for "TalentScout," a fictional recruitment agency. The chatbot, named "Scout," is designed to conduct initial candidate screenings. It interactively gathers essential information (name, experience, etc.) and then dynamically generates and asks relevant technical questions based on the candidate's self-declared tech stack.

The application is built with Python, using Streamlit for the user interface and Google's Gemini 1.5 Flash model for its conversational and generative AI capabilities.

### Core Features
- **Structured Information Gathering:** A friendly, sequential conversation to collect candidate details.
- **Dynamic Technical Questioning:** Generates 3-5 unique technical questions based on the technologies a candidate provides.
- **Context-Aware Conversation:** Maintains the flow of the conversation using a state machine and a context-aware LLM session.
- **Robust Error Handling:** Includes fallback mechanisms for unexpected user inputs or LLM responses.
- **Clean User Interface:** A simple and intuitive chat interface built with Streamlit.

---

## Technical Details

- **Programming Language:** Python 3.10+
- **Frontend UI:** Streamlit
- **Large Language Model:** Google Gemini 1.5 Flash
- **Key Libraries:** `google-generativeai`, `streamlit`, `python-dotenv`

### Architectural Decisions

The application's architecture is centered around a state machine to manage the conversation flow. This was chosen over a single, massive prompt to provide more reliable control over the chatbot's behavior.

A key decision was to use **two separate LLM instances**:
1.  **`model_conversation`**: This instance is configured with a detailed system prompt that defines the "Scout" persona and its strict rules for gathering information. This ensures the chatbot stays on task during the initial screening.
2.  **`model_qgen`**: This is a "clean" instance with no system prompt. Its sole purpose is to handle the one-off task of generating technical questions in a JSON format. This separation prevents "prompt conflicts," where the LLM's core instructions would otherwise prevent it from performing the question-generation task.

---

## Installation and Setup

To run this application locally, please follow these steps:

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/Hemanth0411/talent-scout-chatbot
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

Your web browser will open a new tab with the chatbot interface. Simply follow the chatbot's prompts to complete the screening process.

---

## Prompt Design

The chatbot's effectiveness relies on two core prompts:

1.  **System Prompt (`SYSTEM_PROMPT` in `prompts.py`):** This is the master instruction set for the conversational agent. It defines its persona ("Scout"), its goal (information gathering), and a strict set of rules, such as asking one question at a time and staying on task. This makes the initial screening highly reliable.

2.  **Question Generation Prompt (`get_question_generation_prompt()` in `prompts.py`):** This prompt is a one-shot prompt, meaning it includes a clear example of the desired output. It instructs the LLM to act as a senior technical interviewer and, most importantly, to format its output as a JSON object. This structured output is crucial for allowing the Python application to easily parse the questions and ask them one by one.

---

## Challenges & Solutions

**Challenge:** The LLM, after being given a strong system prompt to be an information gatherer, would refuse to switch tasks to generate technical questions. It would politely decline, stating that its role was only to gather information.

**Solution:** This was resolved by implementing a two-model architecture. A primary model, configured with the system prompt, handles the conversation. A second, "clean" model instance, with no system prompt, is used exclusively for the question generation task. This separation of concerns completely resolved the prompt conflict.

**Challenge:** The LLM's JSON output was sometimes wrapped in markdown code blocks (` ```json ... ``` `), causing `json.loads()` to fail.

**Solution:** The application's code was made more robust by adding a cleaning step that strips these markdown artifacts from the LLM's text response before attempting to parse it as JSON.

---