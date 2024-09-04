import streamlit as st
import pandas as pd
import sys
import subprocess
import os
from dotenv import load_dotenv

def install_requirements():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

# Call this function at the beginning of your script
install_requirements()

# Load environment variables
load_dotenv()

# Get the API key
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
    st.stop()

from scraper import run_scraper
from ai_integration import create_assistant, create_thread, chat_with_assistant

# Initialize OpenAI client with the API key
import openai
openai.api_key = api_key

from scraper import run_scraper
from ai_integration import create_assistant, create_thread, chat_with_assistant

# Initialize session state
if 'assistant' not in st.session_state:
    st.session_state.assistant = create_assistant()
if 'thread' not in st.session_state:
    st.session_state.thread = create_thread()
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

st.title("Web Scraper with AI Analysis")

# Sidebar for configuring websites to scrape
st.sidebar.header("Configure Websites")
websites = []
for i in range(3):  # Allow up to 3 websites
    st.sidebar.subheader(f"Website {i+1}")
    url = st.sidebar.text_input(f"URL {i+1}")
    title_selector = st.sidebar.text_input(f"Title Selector {i+1}", value="h1")
    description_selector = st.sidebar.text_input(f"Description Selector {i+1}", value='meta[name="description"]')
    paragraph_selector = st.sidebar.text_input(f"Paragraph Selector {i+1}", value="p")
    
    if url:
        websites.append({
            'url': url,
            'selectors': {
                'title': title_selector,
                'description': description_selector,
                'first_paragraph': paragraph_selector,
            }
        })

if st.button("Run Scraper"):
    if websites:
        with st.spinner("Scraping websites..."):
            all_data, filename = run_scraper(websites)
        st.success(f"Data saved to {filename}")
        
        # Display scraped data
        df = pd.DataFrame(all_data)
        st.dataframe(df)
        
        # Store scraped data in session state
        st.session_state.scraped_data = all_data
    else:
        st.warning("Please configure at least one website to scrape.")

# AI Chat Interface
st.header("Chat with AI about Scraped Data")
user_input = st.text_input("Ask a question about the scraped data:")
if st.button("Send"):
    if 'scraped_data' in st.session_state:
        with st.spinner("AI is thinking..."):
            response = chat_with_assistant(st.session_state.assistant.id, st.session_state.thread.id, user_input)
        st.session_state.chat_history.append(("You", user_input))
        st.session_state.chat_history.append(("AI", response))
    else:
        st.warning("Please run the scraper first to gather data for the AI to analyze.")

# Display chat history
st.subheader("Chat History")
for role, message in st.session_state.chat_history:
    st.text(f"{role}: {message}")

# Run the Streamlit app
if __name__ == "__main__":
    st.sidebar.info("Configure the websites to scrape in the sidebar, then click 'Run Scraper' to start.")
