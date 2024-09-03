import schedule
import time
from scraper import run_scraper
from ai_integration import create_assistant, create_thread, chat_with_assistant
from email_sender import send_email

def run_weekly_report(websites, recipient_email):
    all_data, filename = run_scraper(websites)
    
    assistant = create_assistant()
    thread = create_thread()
    
    report_prompt = f"Analyze this web scraping report and provide key insights:\n\n{all_data}"
    ai_comment = chat_with_assistant(assistant.id, thread.id, report_prompt)
    
    email_body = f"Please find attached the weekly web scraping report.\n\nAI-generated insights:\n{ai_comment}"
    send_email(recipient_email, "Weekly Web Scraping Report", email_body, filename)

def start_scheduler(websites, recipient_email):
    schedule.every().monday.at("05:00").do(run_weekly_report, websites, recipient_email)
    
    while True:
        schedule.run_pending()
        time.sleep(1)
