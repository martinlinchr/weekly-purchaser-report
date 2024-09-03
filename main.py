import sys
import subprocess
from scraper import run_scraper
from ai_integration import create_assistant, create_thread, chat_with_assistant
from scheduler import start_scheduler

def install_requirements():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

websites = [
    {
        'url': 'https://example.com',
        'selectors': {
            'title': 'h1',
            'description': 'meta[name="description"]',
            'first_paragraph': 'p',
        }
    },
    # Add more websites and selectors as needed
]

def main():
    install_requirements()

    # Run initial scraping
    all_data, filename = run_scraper(websites)
    print(f"Data saved to {filename}")
    
    # Set up AI assistant
    assistant = create_assistant()
    thread = create_thread()
    
    # Example of chatting with the assistant about the scraped data
    while True:
        user_input = input("Ask a question about the scraped data (or type 'quit' to exit): ")
        if user_input.lower() == 'quit':
            break
        response = chat_with_assistant(assistant.id, thread.id, user_input)
        print("AI response:", response)
    
    # Start the scheduler for weekly reports
    recipient_email = "recipient@example.com"  # Replace with actual email
    start_scheduler(websites, recipient_email)

if __name__ == "__main__":
    main()
