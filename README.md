# Email Parser

This script parses emails from a specified mailbox and extracts information about messages containing specific email addresses. The output is saved to a CSV file containing the subject line, received date, and matching email addresses.

## Features

- Filters emails by date range (default: last 30 days)
- Shows real-time progress while processing emails
- Extracts emails matching specific patterns (currently set to 'some-email@')
- Outputs data in CSV format with daily timestamps
- Supports Gmail and other IMAP email providers

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file by copying `.env.example`:
```bash
cp .env.example .env
```

3. Edit the `.env` file with your email credentials:
```
EMAIL=your-email@domain.com
PASSWORD=your-password  # For Gmail, use App Password
IMAP_SERVER=imap.gmail.com #
```

### Gmail-Specific Setup

If using Gmail:
1. Enable 2-Step Verification in your Google Account
2. Generate an App Password:
   - Go to Google Account Settings > Security
   - Under "2-Step Verification", click "App passwords"
   - Select "Mail" and your device
   - Use the generated 16-character password in your `.env` file

## Usage

1. List available mailbox folders:
```bash
python email_parser.py --list-folders
```

2. Process emails from the last 30 days in INBOX (default):
```bash
python email_parser.py
```

3. Process emails from a specific folder:
```bash
python email_parser.py --folder "[Gmail]/Sent Mail"  # Process sent emails
```

4. Process emails from a specific number of days:
```bash
python email_parser.py --days 7  # Process last 7 days
```

5. Combine options:
```bash
python email_parser.py --days 7 --folder "[Gmail]/Sent Mail"  # Process last 7 days of sent mail
```

Common folder names:
- `INBOX` - Received emails
- `[Gmail]/Sent Mail` - Sent emails
- `[Gmail]/Drafts` - Draft emails
- `[Gmail]/All Mail` - All emails
- `[Gmail]/Spam` - Spam folder

Note: Folder names might vary depending on your email provider and settings. Use `--list-folders` to see available folders.

3. Automated Running with Cron

To set up automated daily runs, follow these steps:

1. Make the scripts executable:
```bash
chmod +x email_parser.py run_scraper.sh
```

2. Set proper permissions for the .env file (for security):
```bash
chmod 600 .env
```

3. Open your crontab for editing:
```bash
crontab -e
```

4. Add one of these example cron schedules (replace path with your actual path):

```bash
# Run daily at midnight (00:00)
0 0 * * * /path/to/file/run_scraper.sh >> /path/to/file/cron.log 2>&1

# OR run daily at 8 AM
0 8 * * * /path/to/file/run_scraper.sh >> /path/to/file/cron.log 2>&1

# OR run every 6 hours
0 */6 * * * /path/to/file/run_scraper.sh >> /path/to/file/cron.log 2>&1

# OR run at 9 AM on weekdays only
0 9 * * 1-5 /path/to/file/run_scraper.sh >> /path/to/file/cron.log 2>&1
```

Cron format explanation:
```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of the month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of the week (0 - 6) (Sunday to Saturday)
│ │ │ │ │
* * * * * command to execute
```

5. Verify your cron job is set up:
```bash
crontab -l
```

6. Monitor the cron job:
- Check the log file for any errors:
```bash
tail -f /path/to/file/cron.log
```
- Check the output directory for new files:
```bash
ls -l /path/to/file/output/
```

## Output

- Files are saved in the `output` directory
- Naming format: `email_data_YYYYMMDD.csv`
- CSV contains three columns:
  - subject: Email subject line
  - date: Date received (YYYY-MM-DD)
  - external_email: Matching email address

## Progress Tracking

The script provides real-time feedback:
- Shows the date range being processed
- Displays total number of emails found
- Updates progress every 10 emails
- Shows count of matching emails found
- Provides completion summary
