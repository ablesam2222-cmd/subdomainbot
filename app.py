"""
Main application entry point
"""
import os
from dotenv import load_dotenv
from telegram.ext import Application
from telegram import Update
from handlers import get_handlers

# Load environment variables
load_dotenv()

# Get bot token from environment
BOT_TOKEN = '8482288227:AAGxJkZYoaTS_VrlLxhGipCzmocDCSAmzqU'
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set!")


async def post_init(application: Application):
    """Run after bot is initialized"""
    await application.bot.set_my_commands([
        ('start', 'Start the bot'),
        ('help', 'Show help'),
        ('cancel', 'Cancel current operation'),
    ])


def main():
    """Start the bot"""
    # Create Application
    application = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    
    # Add handlers
    for handler in get_handlers():
        application.add_handler(handler)
    
    # Start the bot
    print("🤖 Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()