#!/usr/bin/env python3
import imaplib
import email
from email.utils import parsedate_to_datetime
import os
from datetime import datetime, timedelta
import csv
from dotenv import load_dotenv
import re

def connect_to_email():
    """Connect to the email server using credentials from environment variables."""
    load_dotenv()
    
    EMAIL = os.getenv('EMAIL')
    PASSWORD = os.getenv('PASSWORD')
    IMAP_SERVER = os.getenv('IMAP_SERVER', 'imap.gmail.com')
    
    if not all([EMAIL, PASSWORD, IMAP_SERVER]):
        raise ValueError("Missing required environment variables. Please check .env file.")
    
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL, PASSWORD)
        return mail
    except imaplib.IMAP4.error as e:
        if 'AUTHENTICATIONFAILED' in str(e):
            if IMAP_SERVER == 'imap.gmail.com':
                print("\nFor Gmail accounts, you need to use an App Password instead of your regular password:")
                print("1. Enable 2-Step Verification in your Google Account Security settings")
                print("2. Go to Security > 2-Step Verification > App passwords")
                print("3. Generate a new App password for 'Mail'")
                print("4. Use that 16-character password in your .env file")
                print("\nMore info: https://support.google.com/accounts/answer/185833")
            raise ValueError("Authentication failed. Please check your email credentials.")
        raise

def extract_claudia_email(email_body):
    """Extract email addresses containing 'example@' from email content."""
    email_pattern = r'[\w\.-]+@[\w\.-]+'
    emails = re.findall(email_pattern, str(email_body))
    claudia_emails = [email for email in emails if 'example@' in email.lower()]
    return claudia_emails[0] if claudia_emails else None

def parse_emails(days=30):
    """Parse emails and extract required information.
    Args:
        days (int): Number of days to look back for emails
    """
    mail = connect_to_email()
    mail.select('inbox')
    
    # Calculate date for filtering
    date_since = (datetime.now() - timedelta(days=days)).strftime("%d-%b-%Y")
    search_criterion = f'(SINCE {date_since})'
    print(f"\nSearching for emails since {date_since}...")
    
    # Search for emails within date range
    _, messages = mail.search(None, search_criterion)
    message_numbers = messages[0].split()
    total_messages = len(message_numbers)
    
    print(f"Found {total_messages} emails to process")
    
    email_data = []
    processed = 0
    matching = 0
    
    for message_number in message_numbers:
        try:
            processed += 1
            if processed % 10 == 0:
                print(f"Processing email {processed}/{total_messages} (Found {matching} matching emails)")
                
            _, msg_data = mail.fetch(message_number, '(RFC822)')
            email_body = msg_data[0][1]
            email_message = email.message_from_bytes(email_body)
            
            # Extract date and convert to desired format
            date_str = email_message['date']
            if date_str:
                date = parsedate_to_datetime(date_str).strftime('%Y-%m-%d')
            else:
                continue
            
            # Extract subject
            subject = email_message['subject']
            if not subject:
                continue
                
            # Extract shop email
            shop_email = extract_claudia_email(email_body)
            if not shop_email:
                continue
            
            matching += 1
            email_data.append({
                'subject': subject,
                'date': date,
                'external_email': shop_email
            })
            
        except Exception as e:
            print(f"Error processing message {processed}/{total_messages}: {e}")
            continue
    
    mail.logout()
    print(f"\nProcessing complete! Found {matching} matching emails out of {total_messages} processed")
    return email_data

def save_to_csv(email_data):
    """Save the extracted data to a CSV file with blank lines between entries."""
    if not email_data:
        print("No matching emails found.")
        return
        
    output_dir = 'output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    timestamp = datetime.now().strftime('%Y%m%d')
    filename = f'{output_dir}/email_data_{timestamp}.csv'
    
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['subject', 'date', 'external_email'])
        writer.writeheader()
        
        # Write each entry followed by a blank line
        for entry in email_data:
            writer.writerow(entry)
            writer.writerow(dict.fromkeys(['subject', 'date', 'external_email'], ''))  # Empty row
    print(f"Data saved to {filename}")

def main():
    try:
        import sys
        days = int(sys.argv[1]) if len(sys.argv) > 1 else 30
        email_data = parse_emails(days=days)
        save_to_csv(email_data)
    except Exception as e:
        print(f"Error: {e}")
        if 'AUTHENTICATIONFAILED' not in str(e):
            print("\nUsage: python email_parser.py [days]")
            print("  days: Number of days to look back (default: 30)")

if __name__ == "__main__":
    main()
