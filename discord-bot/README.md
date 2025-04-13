# Notes2Anki Discord Bot

A Discord bot that allows users to convert their notes into Anki flashcards directly from Discord.

## Features

- Convert notes to Anki flashcards by mentioning the bot
- Support for multiple file formats (pptx, pdf, docx, md, txt)
- Multiple output formats (apkg, pdf, csv)
- Rate limiting to prevent spam
- User-friendly error messages

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.template` to `.env` and fill in your Discord bot token
4. Run the bot:
   ```bash
   python bot.py
   ```

## Usage

1. Mention the bot in a message with attached files
2. Optionally specify the desired output format (e.g., `.apkg`, `.pdf`, `.csv`)
3. Wait for the bot to process your files
4. Receive your converted files!

## Rate Limiting

- Users can make one request every 30 seconds
- Maximum file size: 15MB per file
- Maximum files per request: 5

## Error Handling

The bot will provide clear error messages for:
- Missing file attachments
- File size limits
- Processing errors
- Rate limiting

## Support

For issues or questions, please open an issue in the repository. 