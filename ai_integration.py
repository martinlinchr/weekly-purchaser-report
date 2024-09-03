import os
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("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"))

def create_assistant():
    assistant = client.beta.assistants.create(
        name="Web Scraping Analyst",
        instructions="You are an AI assistant specializing in analyzing web scraping reports. Your role is to provide insights and answer questions about the scraped data.",
        model="gpt-4-turbo-preview"
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
