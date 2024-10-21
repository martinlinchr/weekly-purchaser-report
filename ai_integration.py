import streamlit as st
import os
from openai import OpenAI

# Check if the API key is available in secrets
if "OPENAI_API_KEY" not in st.secrets:
    st.error("OPENAI_API_KEY is not found in Streamlit Secrets. Please add it to your app's secrets.")
    st.stop()

def get_openai_api_key():
    # Try to get the API key from Streamlit secrets
    api_key = st.secrets.get("OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in Streamlit secrets")
    
    return api_key

try:
    api_key = get_openai_api_key()
    client = OpenAI(api_key=api_key)
except Exception as e:
    st.error(f"Error initializing OpenAI client: {str(e)}")
    st.stop()

# Initialize the OpenAI client with the API key from Streamlit Secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def analyze_image(client, image_url, question):
    try:
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",  # Use the correct model name
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": question},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url,
                            },
                        },
                    ],
                }
            ],
            max_tokens=300,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"An error occurred while analyzing the image: {str(e)}"

def create_assistant(client):
    assistant = client.beta.assistants.create(
        name="Procurement Assistant GPT (general)",
        instructions="",
        model="gpt-4o-mini"
    )
    return assistant

def create_thread(client):
    thread = client.beta.threads.create()
    return thread

def add_message_to_thread(client, thread_id, content):
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=content
    )
    return message

def run_assistant(client, assistant_id, thread_id):
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )
    return run

def get_assistant_response(client, thread_id):
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    return messages.data[0].content[0].text.value

def chat_with_assistant(client, assistant_id, thread_id, user_input):
    add_message_to_thread(client, thread_id, user_input)
    run = run_assistant(client, assistant_id, thread_id)
    
    # Wait for the run to complete
    while run.status != "completed":
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
    
    return get_assistant_response(client, thread_id)
