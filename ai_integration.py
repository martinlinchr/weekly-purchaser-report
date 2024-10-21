import os
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("___"))

def create_assistant():
    assistant = client.beta.assistants.create(
        name="Procurement Assistant GPT (general)",
        instructions="",
        model="gpt-4-turbo"
    )
    return assistant

def create_thread():
    thread = client.beta.threads.create()
    return thread

def add_message_to_thread(thread_id, content):
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=content
    )
    return message

def run_assistant(assistant_id, thread_id):
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )
    return run

def get_assistant_response(thread_id):
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    return messages.data[0].content[0].text.value

def chat_with_assistant(assistant_id, thread_id, user_input):
    add_message_to_thread(thread_id, user_input)
    run = run_assistant(assistant_id, thread_id)
    
    # Wait for the run to complete
    while run.status != "completed":
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
    
    return get_assistant_response(thread_id)
