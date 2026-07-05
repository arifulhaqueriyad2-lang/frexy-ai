
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🤖 FREXY AI BOT 🤖                                        ║
║         Powered by Frexy | Advanced Multi-API Telegram Bot                   ║
║         Supports: Text Chat | Image Generation | Code Generation               ║
║         Private & Group Chat | Multi-Language | Chat History                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

📌 INSTRUCTIONS:
1. Install dependencies: pip install python-telegram-bot aiohttp
2. Set your BOT_TOKEN below (get from @BotFather)
3. Run: python frexy_bot.py
4. Bot will work in both Private & Group chats

🎯 COMMANDS (Text Only - No Buttons):
• /start - Start the bot
• /help - Show help menu
• /ai <name> - Switch AI (e.g., /ai gpt5, /ai deepseek)
• /image <type> - Generate image (e.g., /image cosplay, /image nsfw)
• /history - View chat history
• /clear - Clear chat history
• /code <prompt> - Generate Python code
"""

import asyncio
import aiohttp
import logging
import json
import time
from datetime import datetime
from collections import defaultdict
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)
from telegram.constants import ParseMode

# ═══════════════════════════════════════════════════════════════════════════════
# ⚙️ CONFIGURATION - EDIT THESE
# ═══════════════════════════════════════════════════════════════════════════════

BOT_TOKEN = "8893174784:AAELv6Cep-QR1JKrDwNOe8g8wDAozirO8RE"  # 🔴 Replace with your bot token from @BotFather
OWNER_USERNAME = "frexy1only"      # Your Telegram username

# ═══════════════════════════════════════════════════════════════════════════════
# 🔗 API CONFIGURATIONS
# ═══════════════════════════════════════════════════════════════════════════════

# 📝 TEXT APIs (5 APIs)
TEXT_APIS = {
    "gpt5": {
        "name": "🧠 GPT-5",
        "url": "https://r-bots-free-apis.co08.art/api/v1/api/gpt-5?q={}",
        "type": "text"
    },
    "deepai": {
        "name": "🌊 Deep AI",
        "url": "https://r-bots-free-apis.co08.art/api/v1/api/deep-ai?query={}",
        "type": "text"
    },
    "deepseek": {
        "name": "🔍 DeepSeek V3",
        "url": "https://r-bots-free-apis.co08.art/api/v1/api/deepseek-v3?q={}",
        "type": "text"
    },
    "gemini": {
        "name": "💎 Gemini",
        "url": "https://r-bots-free-apis.co08.art/api/v1/api/gemini?q={}",
        "type": "text"
    },
    "bible": {
        "name": "📖 Bible AI",
        "url": "https://r-bots-free-apis.co08.art/api/v1/api/bible-ai?q={}",
        "type": "text"
    }
}

# 🖼️ IMAGE APIs (5 APIs)
IMAGE_APIS = {
    "cosplay": {
        "name": "👘 Cosplay / Anime Girl",
        "url": "https://r-bots-free-apis.co08.art/api/v1/api/cosplay",
        "nsfw": False,
        "description": "Beautiful anime cosplay images"
    },
    "milf": {
        "name": "💋 Romantic / MILF",
        "url": "https://r-bots-free-apis.co08.art/api/v1/api/nsfw/milf",
        "nsfw": True,
        "description": "Romantic mature images"
    },
    "yuri": {
        "name": "🌸 Yuri (18+)",
        "url": "https://r-bots-free-apis.co08.art/api/v1/api/nsfw/yuri",
        "nsfw": True,
        "description": "Yuri themed images (18+)"
    },
    "cuckold": {
        "name": "🔥 Cuckold (18+)",
        "url": "https://r-bots-free-apis.co08.art/api/v1/api/nsfw/cuckold",
        "nsfw": True,
        "description": "Cuckold themed images (18+)"
    },
    "pussy": {
        "name": "🍑 Explicit (18+)",
        "url": "https://r-bots-free-apis.co08.art/api/v1/api/nsfw/pussy",
        "nsfw": True,
        "description": "Explicit adult images (18+)"
    }
}

# ═══════════════════════════════════════════════════════════════════════════════
# 🎨 STYLING & FORMATTING
# ═══════════════════════════════════════════════════════════════════════════════

POWERED_BY = "

═══════════════════════
⚡ 𝗣𝗢𝗪𝗘𝗥𝗘𝗗 𝗕𝗬 𝗙𝗥𝗘𝗫𝗬 ⚡
═══════════════════════"

TYPING_EMOJIS = ["⏳", "🔄", "✨", "🎯", "💫", "🔮"]

# ═══════════════════════════════════════════════════════════════════════════════
# 🗄️ DATA STORAGE (In-Memory)
# ═══════════════════════════════════════════════════════════════════════════════

# Chat history: {chat_id: [{"role": "user/ai", "content": "...", "time": "..."}]}
chat_history = defaultdict(list)

# User preferences: {user_id: {"ai": "gpt5", "language": "en"}}
user_prefs = defaultdict(lambda: {"ai": "gpt5", "language": "en"})

# ═══════════════════════════════════════════════════════════════════════════════
# 📝 LOGGING SETUP
# ═══════════════════════════════════════════════════════════════════════════════

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# 🔧 HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

async def fetch_api(session: aiohttp.ClientSession, url: str, timeout: int = 60):
    """Fetch data from API with timeout"""
    try:
        async with session.get(url, timeout=timeout) as response:
            if response.status == 200:
                content_type = response.headers.get('content-type', '')
                if 'application/json' in content_type:
                    try:
                        return await response.json()
                    except:
                        text = await response.text()
                        return {"text": text}
                else:
                    text = await response.text()
                    return {"text": text}
            else:
                return {"error": f"Status: {response.status}"}
    except asyncio.TimeoutError:
        return {"error": "⏰ Request timed out. Please try again."}
    except Exception as e:
        return {"error": f"❌ Error: {str(e)}"}


def get_current_time():
    """Get formatted current time"""
    return datetime.now().strftime("%H:%M:%S")


def add_to_history(chat_id, role, content):
    """Add message to chat history"""
    chat_history[chat_id].append({
        "role": role,
        "content": content,
        "time": get_current_time()
    })
    # Keep only last 50 messages
    if len(chat_history[chat_id]) > 50:
        chat_history[chat_id] = chat_history[chat_id][-50:]


def format_code_block(code: str, language: str = "python") -> str:
    """Format code in a copy-friendly way"""
    return f"```{language}
{code}
```"


def extract_text_from_response(result: dict) -> str:
    """Extract text from various API response formats"""
    if not isinstance(result, dict):
        return str(result)

    if "error" in result:
        return f"❌ {result['error']}"

    # Try common response keys
    for key in ["text", "response", "answer", "message", "result", "content", "output", "data"]:
        if key in result:
            return str(result[key])

    # If no known keys, return the whole dict as string
    return str(result)


# ═══════════════════════════════════════════════════════════════════════════════
# 🎯 COMMAND HANDLERS
# ═══════════════════════════════════════════════════════════════════════════════

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    chat_id = update.effective_chat.id

    welcome_msg = f"""
╔══════════════════════════════════════════╗
║     🤖 𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗙𝗥𝗘𝗫𝗬 𝗔𝗜 𝗕𝗢𝗧 🤖     ║
╚══════════════════════════════════════════╝

👋 Hello, {user.first_name}!

🎯 I am your advanced AI assistant powered by multiple APIs.

📋 𝗔𝘃𝗮𝗶𝗹𝗮𝗯𝗹𝗲 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💬 /ai <name>    → Switch AI (gpt5, deepai, deepseek, gemini, bible)
🖼️ /image <type> → Generate images (cosplay, milf, yuri, cuckold, pussy)
💻 /code <prompt>→ Generate Python code
📜 /history      → View chat history
🧹 /clear        → Clear chat history
❓ /help         → Show this help menu
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🤖 𝗖𝘂𝗿𝗿𝗲𝗻𝘁 𝗔𝗜: {TEXT_APIS[user_prefs[user.id]['ai']]['name']}

💡 Just send me a message and I'll respond!
💡 For images, say things like: "send me an anime girl" or "generate cosplay image"
💡 For code, say: "write code for calculator"
{POWERED_BY}
    """

    await update.message.reply_text(welcome_msg, parse_mode=ParseMode.MARKDOWN)
    add_to_history(chat_id, "system", "User started the bot")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_msg = f"""
╔══════════════════════════════════════════╗
║     📖 𝗙𝗥𝗘𝗫𝗬 𝗔𝗜 𝗕𝗢𝗧 - 𝗛𝗘𝗟𝗣 𝗠𝗘𝗡𝗨 📖     ║
╚══════════════════════════════════════════╝

🤖 𝗔𝗜 𝗦𝘄𝗶𝘁𝗰𝗵𝗶𝗻𝗴:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• /ai gpt5      → 🧠 GPT-5 (Default)
• /ai deepai    → 🌊 Deep AI
• /ai deepseek  → 🔍 DeepSeek V3
• /ai gemini    → 💎 Gemini
• /ai bible     → 📖 Bible AI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🖼️ 𝗜𝗺𝗮𝗴𝗲 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗶𝗼𝗻:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• /image cosplay  → 👘 Anime Cosplay
• /image milf     → 💋 Romantic/MILF (18+)
• /image yuri     → 🌸 Yuri (18+)
• /image cuckold  → 🔥 Cuckold (18+)
• /image pussy    → 🍑 Explicit (18+)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💻 𝗖𝗼𝗱𝗲 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗶𝗼𝗻:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• /code <description>
  Example: /code create a calculator in python
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🗣️ 𝗡𝗮𝘁𝘂𝗿𝗮𝗹 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 (just type):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• "send me an image" or "generate anime"
• "write code for..." or "create python script"
• "18+ image" or "nsfw pic"
• Any normal chat message
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📜 𝗢𝘁𝗵𝗲𝗿:
• /history → View last 20 messages
• /clear   → Clear your chat history

🔞 𝗡𝗦𝗙𝗪 𝗪𝗮𝗿𝗻𝗶𝗻𝗴: Adult content APIs are marked (18+)
{POWERED_BY}
    """

    await update.message.reply_text(help_msg, parse_mode=ParseMode.MARKDOWN)


async def ai_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /ai command to switch AI"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    if not context.args:
        ai_list = "\n".join([f"• `{key}` → {value['name']}" for key, value in TEXT_APIS.items()])
        msg = f"""
🤖 𝗖𝘂𝗿𝗿𝗲𝗻𝘁 𝗔𝗜: {TEXT_APIS[user_prefs[user_id]['ai']]['name']}

📋 𝗔𝘃𝗮𝗶𝗹𝗮𝗯𝗹𝗲 𝗔𝗜𝘀:
{ai_list}

💡 Usage: /ai <name>
Example: /ai deepseek
{POWERED_BY}
        """
        await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
        return

    ai_name = context.args[0].lower()

    if ai_name not in TEXT_APIS:
        await update.message.reply_text(
            f"❌ Invalid AI name! Use: gpt5, deepai, deepseek, gemini, or bible\n{POWERED_BY}",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    user_prefs[user_id]["ai"] = ai_name
    await update.message.reply_text(
        f"✅ 𝗔𝗜 𝗦𝘄𝗶𝘁𝗰𝗵𝗲𝗱 𝘁𝗼: {TEXT_APIS[ai_name]['name']}\n{POWERED_BY}",
        parse_mode=ParseMode.MARKDOWN
    )
    add_to_history(chat_id, "system", f"User switched AI to {ai_name}")


async def image_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /image command"""
    chat_id = update.effective_chat.id

    if not context.args:
        img_list = "\n".join([f"• `{key}` → {value['name']}" for key, value in IMAGE_APIS.items()])
        msg = f"""
🖼️ 𝗜𝗺𝗮𝗴𝗲 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗶𝗼𝗻

📋 𝗔𝘃𝗮𝗶𝗹𝗮𝗯𝗹𝗲 𝗧𝘆𝗽𝗲𝘀:
{img_list}

💡 Usage: /image <type>
Example: /image cosplay
{POWERED_BY}
        """
        await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
        return

    img_type = context.args[0].lower()

    if img_type not in IMAGE_APIS:
        await update.message.reply_text(
            f"❌ Invalid image type!\n{POWERED_BY}",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    await generate_image(update, context, img_type)


async def code_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /code command"""
    chat_id = update.effective_chat.id

    if not context.args:
        await update.message.reply_text(
            f"💻 Usage: /code <description>\nExample: /code create a calculator\n{POWERED_BY}",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    prompt = " ".join(context.args)
    await generate_code(update, context, prompt)


async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /history command"""
    chat_id = update.effective_chat.id
    history = chat_history.get(chat_id, [])

    if not history:
        await update.message.reply_text(f"📭 No chat history found.\n{POWERED_BY}", parse_mode=ParseMode.MARKDOWN)
        return

    msg = "📜 𝗖𝗵𝗮𝘁 𝗛𝗶𝘀𝘁𝗼𝗿𝘆\n━━━━━━━━━━━━━━━━━━━━━━━━\n"
    for i, entry in enumerate(history[-20:], 1):
        role = "👤" if entry["role"] == "user" else "🤖"
        msg += f"{role} [{entry['time']}]\n{entry['content'][:100]}...\n\n"

    msg += POWERED_BY
    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)


async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /clear command"""
    chat_id = update.effective_chat.id
    chat_history[chat_id] = []
    await update.message.reply_text(f"🧹 𝗖𝗵𝗮𝘁 𝗵𝗶𝘀𝘁𝗼𝗿𝘆 𝗰𝗹𝗲𝗮𝗿𝗲𝗱!\n{POWERED_BY}", parse_mode=ParseMode.MARKDOWN)


# ═══════════════════════════════════════════════════════════════════════════════
# 🧠 CORE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

async def generate_text_response(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    """Generate text response using selected AI API"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    ai_key = user_prefs[user_id]["ai"]
    ai_config = TEXT_APIS[ai_key]

    # Show typing indicator
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    # Build API URL
    encoded_text = text.replace(" ", "%20")
    api_url = ai_config["url"].format(encoded_text)

    async with aiohttp.ClientSession() as session:
        result = await fetch_api(session, api_url, timeout=60)

    # Extract response text using smart extractor
    response_text = extract_text_from_response(result)

    # Format response
    formatted_response = f"""
🤖 {ai_config['name']}
━━━━━━━━━━━━━━━━━━━━━━━━
{response_text}
{POWERED_BY}
    """

    add_to_history(chat_id, "user", text)
    add_to_history(chat_id, "ai", response_text)

    await update.message.reply_text(formatted_response, parse_mode=ParseMode.MARKDOWN)


async def generate_image(update: Update, context: ContextTypes.DEFAULT_TYPE, img_type: str = None, prompt: str = None):
    """Generate and send image"""
    chat_id = update.effective_chat.id
    message = update.message

    # Determine image type from prompt if not provided
    if not img_type and prompt:
        prompt_lower = prompt.lower()
        for key in IMAGE_APIS:
            if key in prompt_lower:
                img_type = key
                break
        if not img_type:
            img_type = "cosplay"  # Default

    if not img_type or img_type not in IMAGE_APIS:
        img_type = "cosplay"

    img_config = IMAGE_APIS[img_type]

    # Send "creating" message with fancy text
    creating_msg = await message.reply_text(
        f"""
🎨 𝗬𝗼𝘂𝗿 𝗶𝗺𝗮𝗴𝗲 𝗶𝘀 𝗰𝗿𝗲𝗮𝘁𝗶𝗻𝗴...

⏳ 𝗣𝗹𝗲𝗮𝘀𝗲 𝘄𝗮𝗶𝘁...
        """,
        parse_mode=ParseMode.MARKDOWN
    )

    # Show typing action
    await context.bot.send_chat_action(chat_id=chat_id, action="upload_photo")

    # Animate with emojis
    for emoji in TYPING_EMOJIS[:3]:
        await asyncio.sleep(0.5)
        await creating_msg.edit_text(
            f"""
🎨 𝗬𝗼𝘂𝗿 𝗶𝗺𝗮𝗴𝗲 𝗶𝘀 𝗰𝗿𝗲𝗮𝘁𝗶𝗻𝗴...

{emoji} 𝗣𝗹𝗲𝗮𝘀𝗲 𝘄𝗮𝗶𝘁...
            """,
            parse_mode=ParseMode.MARKDOWN
        )

    # Fetch image
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(img_config["url"], timeout=60) as response:
                if response.status == 200:
                    image_data = await response.read()

                    # Delete creating message
                    await creating_msg.delete()

                    # Send image with caption
                    caption = f"""
🖼️ {img_config['name']}
✨ 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲𝗱 𝗯𝘆 𝗙𝗿𝗲𝘅𝘆 𝗔𝗜
{POWERED_BY}
                    """

                    await context.bot.send_photo(
                        chat_id=chat_id,
                        photo=image_data,
                        caption=caption,
                        parse_mode=ParseMode.MARKDOWN
                    )

                    add_to_history(chat_id, "user", f"Requested image: {img_type}")
                    add_to_history(chat_id, "ai", f"Sent image: {img_type}")
                else:
                    await creating_msg.edit_text(
                        f"❌ 𝗙𝗮𝗶𝗹𝗲𝗱 𝘁𝗼 𝗴𝗲𝗻𝗲𝗿𝗮𝘁𝗲 𝗶𝗺𝗮𝗴𝗲 (Status: {response.status})\n{POWERED_BY}",
                        parse_mode=ParseMode.MARKDOWN
                    )
        except Exception as e:
            await creating_msg.edit_text(
                f"❌ 𝗘𝗿𝗿𝗼𝗿: {str(e)}\n{POWERED_BY}",
                parse_mode=ParseMode.MARKDOWN
            )


async def generate_code(update: Update, context: ContextTypes.DEFAULT_TYPE, prompt: str):
    """Generate Python code using AI"""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    ai_key = user_prefs[user_id]["ai"]
    ai_config = TEXT_APIS[ai_key]

    # Show typing
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    # Create code generation prompt
    code_prompt = f"Write Python code for: {prompt}. Only return the code, no explanations."
    encoded_prompt = code_prompt.replace(" ", "%20")
    api_url = ai_config["url"].format(encoded_prompt)

    async with aiohttp.ClientSession() as session:
        result = await fetch_api(session, api_url, timeout=60)

    # Extract code
    code_text = extract_text_from_response(result)

    # Clean up code (remove markdown if present)
    code_text = code_text.replace("```python", "").replace("```", "").strip()

    # Format with code block for easy copying
    formatted_code = f"""
💻 𝗣𝘆𝘁𝗵𝗼𝗻 𝗖𝗼𝗱𝗲 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲𝗱
🤖 𝗨𝘀𝗶𝗻𝗴: {ai_config['name']}
━━━━━━━━━━━━━━━━━━━━━━━━

{format_code_block(code_text)}

━━━━━━━━━━━━━━━━━━━━━━━━
💡 𝗧𝗮𝗽 𝘁𝗼 𝗰𝗼𝗽𝘆 𝘁𝗵𝗲 𝗰𝗼𝗱𝗲 𝗮𝗯𝗼𝭧e
{POWERED_BY}
    """

    add_to_history(chat_id, "user", f"Code request: {prompt}")
    add_to_history(chat_id, "ai", f"Generated code for: {prompt}")

    await update.message.reply_text(formatted_code, parse_mode=ParseMode.MARKDOWN)


# ═══════════════════════════════════════════════════════════════════════════════
# 💬 MESSAGE HANDLER (Main Logic)
# ═══════════════════════════════════════════════════════════════════════════════

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all text messages"""
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    # Detect intent from message
    text_lower = text.lower()

    # Image generation keywords
    image_keywords = ["image", "photo", "pic", "picture", "generate image", "send image", 
                      "anime", "cosplay", "nsfw", "18+", "porn", "nude", "sexy", "hot pic"]

    # Code generation keywords
    code_keywords = ["code", "python", "script", "program", "write code", "create code",
                     "make a", "build a", "function", "class", "algorithm"]

    # Check for image request
    is_image_request = any(keyword in text_lower for keyword in image_keywords)

    # Check for code request
    is_code_request = any(keyword in text_lower for keyword in code_keywords)

    # Check for specific image type mentions
    for img_type in IMAGE_APIS:
        if img_type in text_lower:
            is_image_request = True
            await generate_image(update, context, img_type=img_type, prompt=text)
            return

    if is_image_request and not any(t in text_lower for t in IMAGE_APIS):
        await generate_image(update, context, prompt=text)
        return

    if is_code_request:
        # Extract the actual request (remove code keywords)
        code_prompt = text
        for keyword in ["write code for", "create code for", "make a", "build a", "code:", "python:"]:
            code_prompt = code_prompt.replace(keyword, "").strip()
        await generate_code(update, context, code_prompt)
        return

    # Default: Text chat
    await generate_text_response(update, context, text)


# ═══════════════════════════════════════════════════════════════════════════════
# ❌ ERROR HANDLER
# ═══════════════════════════════════════════════════════════════════════════════

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors gracefully"""
    logger.error(f"Update {update} caused error {context.error}")

    if update and update.effective_message:
        error_msg = f"""
❌ 𝗢𝗼𝗽𝘀! 𝗦𝗼𝗺𝗲𝘁𝗵𝗶𝗻𝗴 𝘄𝗲𝗻𝘁 𝘄𝗿𝗼𝗻𝗴.

🔄 𝗣𝗹𝗲𝗮𝘀𝗲 𝘁𝗿𝘆 𝗮𝗴𝗮𝗶𝗻 𝗹𝗮𝘁𝗲𝗿.

📋 𝗘𝗿𝗿𝗼𝗿: {str(context.error)[:100]}
{POWERED_BY}
        """
        try:
            await update.effective_message.reply_text(error_msg, parse_mode=ParseMode.MARKDOWN)
        except:
            pass


# ═══════════════════════════════════════════════════════════════════════════════
# 🚀 MAIN FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Start the bot"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║     🤖  𝗙𝗥𝗘𝗫𝗬 𝗔𝗜 𝗕𝗢𝗧  𝗦𝗧𝗔𝗥𝗧𝗜𝗡𝗚...  🤖                                      ║
║                                                                              ║
║     ⚡ Powered by Frexy | Multi-API Telegram Bot                            ║
║     📝 5 Text APIs | 🖼️ 5 Image APIs | 💻 Code Generation                   ║
║     🌍 Private & Group Chat | 🗣️ Multi-Language Support                     ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ ERROR: Please set your BOT_TOKEN in the configuration!")
        print("   Get your token from @BotFather on Telegram")
        return

    # Build application with extended timeouts
    application = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .read_timeout(60)
        .write_timeout(60)
        .connect_timeout(30)
        .pool_timeout(60)
        .build()
    )

    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ai", ai_command))
    application.add_handler(CommandHandler("image", image_command))
    application.add_handler(CommandHandler("code", code_command))
    application.add_handler(CommandHandler("history", history_command))
    application.add_handler(CommandHandler("clear", clear_command))

    # Add message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Add error handler
    application.add_error_handler(error_handler)

    print("✅ Bot is running! Press Ctrl+C to stop.")
    print(f"🔗 Bot Owner: @{OWNER_USERNAME}")
    print("═══════════════════════════════════════════════════════════════════════════════")

    # Run the bot with polling
    application.run_polling(
        poll_interval=1.0,
        timeout=60,
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()
