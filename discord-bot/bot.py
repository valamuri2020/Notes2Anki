import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import aiohttp
from aiohttp import FormData
import asyncio
from datetime import datetime, timedelta
import json
from typing import Optional

# Load environment variables
load_dotenv()

# Bot configuration
TOKEN = os.getenv('DISCORD_TOKEN')
BACKEND_URL = os.getenv('BACKEND_URL')
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 15 * 1024 * 1024))  # 15 MB in bytes
MAX_FILES = int(os.getenv('MAX_FILES', 5))
COOLDOWN_SECONDS = int(os.getenv('COOLDOWN_SECONDS', 30))

# Initialize bot with intents
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent
bot = commands.Bot(command_prefix='!', intents=intents)

# User cooldown tracking
user_cooldowns = {}

def is_on_cooldown(user_id: int) -> bool:
    """Check if a user is on cooldown"""
    if user_id not in user_cooldowns:
        return False
    
    cooldown_end = user_cooldowns[user_id]
    if datetime.now() > cooldown_end:
        del user_cooldowns[user_id]
        return False
    return True

def set_cooldown(user_id: int):
    """Set cooldown for a user"""
    user_cooldowns[user_id] = datetime.now() + timedelta(seconds=COOLDOWN_SECONDS)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    # Check if bot is directly mentioned (not @everyone, @here, or @role)
    if bot.user in message.mentions:
        # Check for cooldown
        if is_on_cooldown(message.author.id):
            await message.reply("Please wait a moment before making another request! ⏳")
            return

        # Check for attachments
        if not message.attachments:
            await message.reply("Hey! Please attach a file for me to process – I can't help without one. 📎")
            return

        # Validate attachments
        if len(message.attachments) > MAX_FILES:
            await message.reply(f"Sorry, I can only process up to {MAX_FILES} files at a time. 📎")
            return

        
        # Check file sizes and types
        valid_files = []
        for attachment in message.attachments:
            if attachment.size > MAX_FILE_SIZE:
                await message.reply(f"File {attachment.filename} is too large. Maximum size is 15MB. 📎")
                return
            if attachment.filename.lower().endswith(('.pdf', '.txt', '.docx', '.pptx')):
                valid_files.append(attachment)
            else:
                await message.reply(f"Unsupported file type: {attachment.filename}. Please use PDF, TXT, DOCX, or PPTX. 🚫")
                return

        # Determine output format
        output_format = "apkg"  # default
        if "apkg" in message.content.lower():
            output_format = "apkg"
        elif "pdf" in message.content.lower():
            output_format = "pdf"
        elif "csv" in message.content.lower():
            output_format = "csv"

        # Process files
        await message.reply("Got it! This may take a few minutes. ⏳")
        set_cooldown(message.author.id)

        try:
            # Prepare request data
            request_data = {
                "id": str(message.id),
                "multiple_decks": len(valid_files) > 1,
                "output_format": output_format,
                "deck_names": {file.filename: file.filename.split(".")[0] for file in valid_files}
            }

            # Download files and prepare for upload
            form_data = FormData()
            form_data.add_field('request', json.dumps(request_data))
            
            for attachment in valid_files:
                async with aiohttp.ClientSession() as session:
                    async with session.get(attachment.url) as resp:
                        if resp.status == 200:
                            file_data = await resp.read()
                            form_data.add_field(
                                'files',
                                file_data,
                                filename=attachment.filename,
                                content_type='application/octet-stream'
                            )

            # Make request to backend
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{BACKEND_URL}/generate",
                    data=form_data
                ) as resp:
                    if resp.status == 200:
                        # Get the response file
                        content_disposition = resp.headers.get("Content-Disposition")
                        filename = content_disposition.split("filename=")[1].strip('"')
                        
                        # Save the file temporarily
                        file_data = await resp.read()
                        with open(filename, "wb") as f:
                            f.write(file_data)

                        # Send the file back to the user
                        await message.reply(
                            "Here's your converted file! 🎉 Note: AI can make mistakes, so double-check when using!*",
                            file=discord.File(filename)
                        )

                        # Clean up
                        os.remove(filename)
                    else:
                        await message.reply("Sorry, something went wrong. Please try again soon! ⚠️")

        except Exception as e:
            print(f"Error processing files: {e}")
            await message.reply("Sorry, something went wrong. Please try again soon! ⚠️")

    await bot.process_commands(message)

def main():
    bot.run(TOKEN)

if __name__ == "__main__":
    main() 