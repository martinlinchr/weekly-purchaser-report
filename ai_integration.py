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

# Use a constant for the model name
GPT_MODEL = "gpt-4o"

def analyze_image(client, image_data, question):
    try:
        response = client.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": question},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_data,
                            },
                        },
                    ],
                }
            ],
            max_tokens=500,
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

def chat_with_assistant(client, data_description, user_input, image_data=None):
    try:
        messages = [
            {"role": "system", "content": "You are an AI assistant that analyzes economic data and answers questions about it."},
            {"role": "user", "content": [{"type": "text", "text": f"Based on the following economic data:\n\n{data_description}\n\nUser question: {user_input}"}]}
        ]
        
        if image_data:
            messages[1]["content"].append({
                "type": "image_url",
                "image_url": {
                    "url": image_data,
                }
            })

        response = client.chat.completions.create(
            model=GPT_MODEL,
            messages=messages,
            max_tokens=500,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"An error occurred while communicating with the AI: {str(e)}"
