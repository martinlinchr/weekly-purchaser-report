import streamlit as st
import pandas as pd
from scraper import run_scraper
from ai_integration import create_assistant, create_thread, chat_with_assistant

# Initialize session state
if 'assistant' not in st.session_state:
    st.session_state.assistant = create_assistant()
if 'thread' not in st.session_state:
    st.session_state.thread = create_thread()

st.title("Economic Data Scraper with AI Analysis")

if st.button("Run Scraper"):
    with st.spinner("Scraping websites..."):
        all_data, filename = run_scraper()
    st.success(f"Data saved to {filename}")
    
    # Display scraped data
    for key, df in all_data.items():
        st.subheader(key)
        st.dataframe(df)

# AI Chat Interface
st.header("Chat with AI about Scraped Data")
user_input = st.text_input("Ask a question about the scraped economic data:")
if st.button("Send"):
    if 'all_data' in locals():
        context = f"Here's a summary of the scraped economic data:\n\n"
        for key, df in all_data.items():
            context += f"{key}:\n{df.head().to_string()}\n\n"
        
        prompt = f"{context}\nUser question: {user_input}"
        
        with st.spinner("AI is thinking..."):
            response = chat_with_assistant(st.session_state.assistant.id, st.session_state.thread.id, prompt)
        st.text_area("AI Response:", value=response, height=200, max_chars=None, key=None)
    else:
        st.warning("Please run the scraper first to gather data for the AI to analyze.")

# Run the Streamlit app
if __name__ == "__main__":
    st.sidebar.info("Click 'Run Scraper' to start gathering economic data.")
