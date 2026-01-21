"""
Telegram bot handlers
"""
import logging
from telegram import (
    Update, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup,
    ReplyKeyboardRemove
)
from telegram.ext import (
    ContextTypes, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler,
    ConversationHandler,
    filters
)

from utils import validate_domain, format_results, save_results_to_file, user_session
from generator import SubdomainGenerator
from scanner import get_scanner_for_mode

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
(
    START_ROUTES,
    AWAITING_DOMAIN,
    AWAITING_MODE,
    AWAITING_CONFIRMATION,
    SCANNING
) = map(chr, range(5))

# Channel links
CHANNEL_LINK = "https://t.me/example_channel"
DEVELOPER_LINK = "https://t.me/example_developer"

# Menu buttons
START_SCAN = "start_scan"
CHANNEL_LINK_BTN = "channel_link"
DEVELOPER_LINK_BTN = "developer_link"
NORMAL_MODE = "normal_mode"
MEDIUM_MODE = "medium_mode"
ULTIMATE_MODE = "ultimate_mode"
CONFIRM_START = "confirm_start"
CONFIRM_CANCEL = "confirm_cancel"


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    welcome_message = """
🔍 *Subdomain Enumeration Bot*

I can help you discover subdomains for any domain using AI-style enumeration techniques.

*Features:*
• Smart candidate generation
• DNS resolution checking
• HTTPS alive verification
• Multiple scan modes
• Results export to file

Select an option below to begin:
    """
    
    keyboard = [
        [
            InlineKeyboardButton("🚀 Start Scan", callback_data=START_SCAN),
        ],
        [
            InlineKeyboardButton("📢 Channel", callback_data=CHANNEL_LINK_BTN),
            InlineKeyboardButton("👨‍💻 Developer", callback_data=DEVELOPER_LINK_BTN),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(
            welcome_message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        await update.callback_query.edit_message_text(
            welcome_message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    return START_ROUTES


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline button presses"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    if data == START_SCAN:
        await query.edit_message_text(
            "Please enter the domain you want to scan (e.g., example.com):",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("↩️ Back to Menu", callback_data="back_to_menu")]
            ])
        )
        return AWAITING_DOMAIN
    
    elif data == CHANNEL_LINK_BTN:
        await query.edit_message_text(
            f"Join our channel for updates: {CHANNEL_LINK}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
            ])
        )
        return START_ROUTES
    
    elif data == DEVELOPER_LINK_BTN:
        await query.edit_message_text(
            f"Contact the developer: {DEVELOPER_LINK}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
            ])
        )
        return START_ROUTES
    
    elif data == "back_to_menu":
        return await start_command(update, context)
    
    return START_ROUTES


async def receive_domain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive and validate domain input"""
    user_id = update.message.from_user.id
    domain = update.message.text.strip()
    
    if not validate_domain(domain):
        await update.message.reply_text(
            "❌ Invalid domain format. Please enter a valid domain (e.g., example.com):",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("↩️ Back to Menu", callback_data="back_to_menu")]
            ])
        )
        return AWAITING_DOMAIN
    
    # Store domain in session
    session = user_session.create(user_id)
    session['domain'] = domain
    
    # Ask for mode selection
    keyboard = [
        [
            InlineKeyboardButton("🟢 Normal", callback_data=NORMAL_MODE),
            InlineKeyboardButton("🟡 Medium", callback_data=MEDIUM_MODE),
            InlineKeyboardButton("🔴 Ultimate", callback_data=ULTIMATE_MODE),
        ],
        [InlineKeyboardButton("↩️ Back", callback_data=START_SCAN)]
    ]
    
    await update.message.reply_text(
        f"Domain: *{domain}*\n\n"
        "Select scan mode:\n"
        "• 🟢 *Normal*: Quick scan (~50 candidates)\n"
        "• 🟡 *Medium*: Balanced scan (~150 candidates)\n"
        "• 🔴 *Ultimate*: Comprehensive scan (~500 candidates)",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    
    return AWAITING_MODE


async def select_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle mode selection"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    session = user_session.get(user_id)
    
    if not session:
        return await start_command(update, context)
    
    mode_map = {
        NORMAL_MODE: 'normal',
        MEDIUM_MODE: 'medium',
        ULTIMATE_MODE: 'ultimate'
    }
    
    mode = mode_map.get(query.data)
    if not mode:
        return await start_command(update, context)
    
    session['mode'] = mode
    domain = session['domain']
    estimated = SubdomainGenerator.estimate_count(mode)
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Start Scan", callback_data=CONFIRM_START),
            InlineKeyboardButton("❌ Cancel", callback_data=CONFIRM_CANCEL),
        ]
    ]
    
    await query.edit_message_text(
        f"📋 *Scan Configuration*\n\n"
        f"• Domain: `{domain}`\n"
        f"• Mode: *{mode.capitalize()}*\n"
        f"• Estimated candidates: *{estimated}*\n\n"
        f"Click *Start Scan* to begin or *Cancel* to go back.",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    
    return AWAITING_CONFIRMATION


async def confirm_scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle scan confirmation"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    session = user_session.get(user_id)
    
    if query.data == CONFIRM_CANCEL:
        return await start_command(update, context)
    
    if not session or 'domain' not in session or 'mode' not in session:
        return await start_command(update, context)
    
    domain = session['domain']
    mode = session['mode']
    
    # Generate candidates
    await query.edit_message_text(
        f"🔍 *Generating subdomain candidates...*\n\n"
        f"Domain: `{domain}`\n"
        f"Mode: *{mode.capitalize()}*",
        parse_mode='Markdown'
    )
    
    try:
        candidates = SubdomainGenerator.generate_candidates(domain, mode)
        session['candidates'] = candidates
        
        estimated = len(candidates)
        await query.edit_message_text(
            f"🎯 *Starting Scan...*\n\n"
            f"• Domain: `{domain}`\n"
            f"• Mode: *{mode.capitalize()}*\n"
            f"• Candidates: *{estimated}*\n\n"
            f"🔄 This may take a moment...",
            parse_mode='Markdown'
        )
        
        # Start scanning
        scanner = get_scanner_for_mode(mode)
        https_alive, dns_resolved = await scanner.scan_subdomains(candidates)
        
        session['https_alive'] = https_alive
        session['dns_resolved'] = dns_resolved
        
        # Format results
        results_text = format_results(https_alive, dns_resolved)
        
        # Save to file
        filepath = save_results_to_file(domain, https_alive, dns_resolved)
        
        # Send results
        await query.edit_message_text(
            results_text,
            parse_mode='Markdown'
        )
        
        # Send file
        with open(filepath, 'rb') as f:
            await context.bot.send_document(
                chat_id=query.message.chat_id,
                document=f,
                filename=f"subdomain_scan_{domain}.txt",
                caption=f"Results for {domain}"
            )
        
        # Clean up session
        user_session.delete(user_id)
        
    except Exception as e:
        logger.error(f"Scan error: {e}")
        await query.edit_message_text(
            f"❌ An error occurred during scanning:\n`{str(e)}`\n\n"
            f"Please try again or use a different domain.",
            parse_mode='Markdown'
        )
    
    # Return to main menu
    return await start_command(update, context)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the conversation"""
    user_id = update.message.from_user.id
    user_session.delete(user_id)
    
    await update.message.reply_text(
        "Operation cancelled.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message"""
    help_text = """
📚 *Bot Commands*

/start - Start the bot and show main menu
/help - Show this help message
/cancel - Cancel current operation

*How to use:*
1. Click *Start Scan*
2. Enter a domain (e.g., example.com)
3. Select scan mode
4. Confirm and wait for results
5. Receive text file with all findings

*Scan Modes:*
• Normal: Quick scan with common subdomains
• Medium: More comprehensive with additional patterns
• Ultimate: Full enumeration with extensive heuristics
    """
    
    await update.message.reply_text(
        help_text,
        parse_mode='Markdown'
    )


def get_handlers():
    """Return all handlers for the bot"""
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_command)],
        states={
            START_ROUTES: [
                CallbackQueryHandler(button_handler),
            ],
            AWAITING_DOMAIN: [
                CallbackQueryHandler(button_handler),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_domain),
            ],
            AWAITING_MODE: [
                CallbackQueryHandler(select_mode),
            ],
            AWAITING_CONFIRMATION: [
                CallbackQueryHandler(confirm_scan),
            ],
        },
        fallbacks=[
            CommandHandler('cancel', cancel),
            CommandHandler('start', start_command),
            CommandHandler('help', help_command),
        ],
    )
    
    return [
        conv_handler,
        CommandHandler('help', help_command),
        CommandHandler('cancel', cancel),
    ]
