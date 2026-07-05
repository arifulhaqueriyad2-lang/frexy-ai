#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║   🤖 FREXY AI BOT - Telegram Chat Bot                                ║
║   No buttons, no commands - Pure text-based AI interaction           ║
║                                                                      ║
║   Features:                                                          ║
║   • 💬 Text Chat (5 AI models)                                       ║
║   • 🖼️ Image Generation (5 APIs)                                     ║
║   • 💻 Code Writing                                                  ║
║   • 🌍 Multi-language Support                                        ║
║   • 📚 Chat History (Groups + Private)                              ║
║                                                                      ║
║   🔥 POWERED BY FREXY 🔥                                             ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import re
import asyncio
import aiohttp
import logging
import random
from datetime import datetime
from typing import Optional, Dict, List, Any, Union

from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
    CommandHandler,
)
from telegram.constants import ParseMode

# ═══════════════════════════════════════════════════════════════════════
# ⚙️ CONFIGURATION - EDIT THESE VALUES
# ═══════════════════════════════════════════════════════════════════════

# 🔑 Your Telegram Bot Token from @BotFather
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# 👤 Bot Owner Info
OWNER_USERNAME = "frexy1only"
OWNER_ID = None  # Set your Telegram numeric ID here for admin access

# 🖼️ IMAGE GENERATION APIs (5 slots - all pre-configured)
IMAGE_APIS = {
    "nsfw_cuckold": {
        "url": "https://r-bots-free-apis.co08.art/api/v1/api/nsfw/cuckold",
        "category": "nsfw",
        "name": "🔞 Cuckold"
    },
    "nsfw_milf": {
        "url": "https://r-bots-free-apis.co08.art/api/v1/api/nsfw/milf",
        "category": "nsfw",
        "name": "🔞 MILF"
    },
    "nsfw_yuri": {
        "url": "https://r-bots-free-apis.co08.art/api/v1/api/nsfw/yuri",
        "category": "nsfw",
        "name": "🔞 Yuri"
    },
    "cosplay": {
        "url": "https://r-bots-free-apis.co08.art/api/v1/api/cosplay",
        "category": "safe",
        "name": "🎭 Cosplay"
    },
    "nsfw_pussy": {
        "url": "https://r-bots-free-apis.co08.art/api/v1/api/nsfw/pussy",
        "category": "nsfw",
        "name": "🔞 Pussy"
    },
}

# 💬 TEXT / CHAT APIs (5 slots - all pre-configured)
TEXT_APIS = {
    "gpt5": {
        "url": "https://r-bots-free-apis.co08.art/api/v1/api/gpt-5",
        "param": "q",
        "name": "🧠 GPT-5",
        "emoji": "🧠",
        "desc": "Latest GPT model"
    },
    "deep_ai": {
        "url": "https://r-bots-free-apis.co08.art/api/v1/api/deep-ai",
        "param": "query",
        "name": "🔥 Deep AI",
        "emoji": "🔥",
        "desc": "Deep AI responses"
    },
    "deepseek": {
        "url": "https://r-bots-free-apis.co08.art/api/v1/api/deepseek-v3",
        "param": "q",
        "name": "🚀 DeepSeek V3",
        "emoji": "🚀",
        "desc": "DeepSeek V3 model"
    },
    "gemini": {
        "url": "https://r-bots-free-apis.co08.art/api/v1/api/gemini",
        "param": "q",
        "name": "💎 Gemini",
        "emoji": "💎",
        "desc": "Google Gemini"
    },
    "bible": {
        "url": "https://r-bots-free-apis.co08.art/api/v1/api/bible-ai",
        "param": "q",
        "name": "📖 Bible AI",
        "emoji": "📖",
        "desc": "Bible-based AI"
    },
}

# ═══════════════════════════════════════════════════════════════════════
# ⚙️ BOT SETTINGS
# ═══════════════════════════════════════════════════════════════════════

MAX_HISTORY = 25          # Messages to remember per chat
API_TIMEOUT = 60            # API call timeout in seconds
IMAGE_TIMEOUT = 30          # Image API timeout
FOOTER = "\n\n━━━━━━━━━━━━━━━━━━━━━━━\n🔥 **POWERED BY FREXY** 🔥\n━━━━━━━━━━━━━━━━━━━━━━━"

ADMIN_IDS = []  # Add admin Telegram IDs here
if OWNER_ID:
    ADMIN_IDS.append(OWNER_ID)

# ═══════════════════════════════════════════════════════════════════════
# 📝 LOGGING SETUP
# ═══════════════════════════════════════════════════════════════════════

logging.basicConfig(
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log", encoding="utf-8")
    ]
)
logger = logging.getLogger("FrexyBot")

# ═══════════════════════════════════════════════════════════════════════
# 💾 DATA STORAGE (JSON-based persistent storage)
# ═══════════════════════════════════════════════════════════════════════

class ChatStore:
    """Persistent storage for chat history and preferences"""

    def __init__(self):
        self.history: Dict[str, List[Dict]] = {}
        self.user_prefs: Dict[str, Dict] = {}
        self.chat_prefs: Dict[str, Dict] = {}
        self.stats: Dict[str, Any] = {"total_messages": 0, "start_time": datetime.now().isoformat()}
        self._load_all()

    def _file_path(self, name: str) -> str:
        return f"bot_data_{name}.json"

    def _load_json(self, fname: str) -> dict:
        try:
            with open(self._file_path(fname), "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_json(self, fname: str, data: dict):
        try:
            with open(self._file_path(fname), "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Save error ({fname}): {e}")

    def _load_all(self):
        self.history = self._load_json("history")
        self.user_prefs = self._load_json("users")
        self.chat_prefs = self._load_json("chats")
        self.stats = self._load_json("stats")
        if not self.stats:
            self.stats = {"total_messages": 0, "start_time": datetime.now().isoformat()}

    def get_history(self, chat_id: str) -> List[Dict]:
        return self.history.get(chat_id, [])

    def add_message(self, chat_id: str, role: str, content: str):
        if chat_id not in self.history:
            self.history[chat_id] = []
        self.history[chat_id].append({
            "role": role,
            "content": content,
            "time": datetime.now().isoformat()
        })
        if len(self.history[chat_id]) > MAX_HISTORY:
            self.history[chat_id] = self.history[chat_id][-MAX_HISTORY:]
        self._save_json("history", self.history)
        self.stats["total_messages"] = self.stats.get("total_messages", 0) + 1
        self._save_json("stats", self.stats)

    def clear_history(self, chat_id: str):
        if chat_id in self.history:
            self.history[chat_id] = []
            self._save_json("history", self.history)

    def get_user_pref(self, user_id: str, key: str, default=None):
        return self.user_prefs.get(user_id, {}).get(key, default)

    def set_user_pref(self, user_id: str, key: str, value: Any):
        if user_id not in self.user_prefs:
            self.user_prefs[user_id] = {}
        self.user_prefs[user_id][key] = value
        self._save_json("users", self.user_prefs)

    def get_chat_pref(self, chat_id: str, key: str, default=None):
        return self.chat_prefs.get(chat_id, {}).get(key, default)

    def set_chat_pref(self, chat_id: str, key: str, value: Any):
        if chat_id not in self.chat_prefs:
            self.chat_prefs[chat_id] = {}
        self.chat_prefs[chat_id][key] = value
        self._save_json("chats", self.chat_prefs)


store = ChatStore()

# ═══════════════════════════════════════════════════════════════════════
# 🤖 AI API HANDLERS
# ═══════════════════════════════════════════════════════════════════════

async def fetch_text_api(session: aiohttp.ClientSession, api_key: str, query: str) -> str:
    """Call a text AI API and return the response"""
    api = TEXT_APIS.get(api_key)
    if not api:
        return "❌ Invalid AI selected."

    url = f"{api['url']}?{api['param']}={query}"

    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=API_TIMEOUT)) as resp:
            text = await resp.text()

            # Try JSON parsing first
            try:
                data = json.loads(text)
                if isinstance(data, dict):
                    for key in ["response", "answer", "result", "text", "message", 
                                "content", "output", "reply", "data", "output_text"]:
                        if key in data and data[key]:
                            val = data[key]
                            if isinstance(val, str):
                                return val
                            elif isinstance(val, dict):
                                for subkey in ["text", "content", "message", "response"]:
                                    if subkey in val and val[subkey]:
                                        return str(val[subkey])
                            return str(val)
                    # Return first non-empty string value
                    for v in data.values():
                        if isinstance(v, str) and len(v.strip()) > 3:
                            return v
                        elif isinstance(v, (list, dict)) and v:
                            return str(v)
                elif isinstance(data, str):
                    return data
                elif isinstance(data, list) and len(data) > 0:
                    return str(data[0])
            except json.JSONDecodeError:
                pass

            # Return raw text
            cleaned = text.strip()
            if cleaned and len(cleaned) > 2:
                return cleaned
            return "⚠️ API returned empty response"

    except asyncio.TimeoutError:
        return "⏱️ Request timed out. The API is taking too long. Please try again!"
    except aiohttp.ClientError as e:
        return f"❌ Connection error: {str(e)[:100]}"
    except Exception as e:
        return f"❌ Error: {str(e)[:150]}"


async def fetch_image_api(session: aiohttp.ClientSession, api_key: str) -> Optional[str]:
    """Fetch image from API - returns direct image URL or None"""
    api = IMAGE_APIS.get(api_key)
    if not api:
        return None

    try:
        async with session.get(
            api["url"], 
            timeout=aiohttp.ClientTimeout(total=IMAGE_TIMEOUT),
            allow_redirects=True
        ) as resp:
            content_type = resp.headers.get("Content-Type", "").lower()

            # Direct image response
            if "image" in content_type:
                return str(resp.url)

            # JSON response with image URL
            text = await resp.text()
            try:
                data = json.loads(text)
                for key in ["url", "image", "link", "src", "photo", "picture", 
                           "media", "image_url", "direct_url", "file"]:
                    if key in data and data[key]:
                        return str(data[key])
            except:
                pass

            # Check if response is a URL
            text_clean = text.strip()
            if text_clean.startswith("http") and len(text_clean) < 500:
                return text_clean

            return None

    except Exception as e:
        logger.error(f"Image API error ({api_key}): {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════
# 🧠 INTENT DETECTION ENGINE
# ═══════════════════════════════════════════════════════════════════════

def detect_intent(text: str) -> Dict[str, Any]:
    """Smart intent detection from user message"""
    text_lower = text.lower().strip()
    result = {"type": "chat", "query": text, "api": None, "image_key": None, "is_code": False}

    # ──────────────────────────────────────────
    # 🖼️ IMAGE GENERATION DETECTION
    # ──────────────────────────────────────────
    img_triggers = [
        "image", "photo", "pic", "picture", "generate image", "make image",
        "draw", "create image", "send image", "image of", "photo of",
        "show me", "give me image", "generate pic", "make pic",
        "ছবি", "পিক", "ফটো", "ইমেজ", "চিত্র", "ছবি দেখাও", "ছবি পাঠাও",
        "तस्वीर", "फोटो", "चित्र", "फोटो भेजो", "तस्वीर दिखाओ",
        "صورة", "foto", "imagen", "imagem", "bild", "画像", "图片", "圖片",
        "imagem", "fotografia", "send pic", "send photo"
    ]

    nsfw_triggers = [
        "nsfw", "18+", "adult", "nude", "naked", "porn", "sex", "xxx",
        "hentai", "cuckold", "milf", "yuri", "pussy", "boobs", "dick",
        "fuck", "blowjob", "cum", "orgasm", "erotic", "lust", "horny",
        "hot girl", "sexy", "naked girl", "nude girl", "adult image",
        "বড় ছবি", "নগ্ন", "যৌন", "xxx ছবি", "হট ছবি",
        "हॉट", "नंगी", "सेक्सी", "अश्लील", "पोर्न",
        "porno", "erotik", "desnuda", "desnudo", "erótica"
    ]

    romantic_triggers = [
        "romantic", "love", "couple", "kiss", "hug", "cute couple",
        "romance", "sweet", "lovely", "valentine", "heart",
        "প্রেম", "ভালোবাসা", "রোমান্টিক", "কাপল",
        "रोमांटिक", "प्यार", "प्रेम", "कपल"
    ]

    anime_triggers = [
        "anime", "cosplay", "waifu", "manga", "otaku", "2d", "anime girl",
        "anime boy", "kawaii", "weeb", "anime pic",
        "অ্যানিমে", "কসপ্লে", "ওয়াইফু", "মাঙ্গা",
        "एनीमे", "कॉसप्ले", "वाइफू", "动漫", "アニメ", "코스프레"
    ]

    is_image = any(t in text_lower for t in img_triggers)
    is_nsfw = any(t in text_lower for t in nsfw_triggers)
    is_romantic = any(t in text_lower for t in romantic_triggers)
    is_anime = any(t in text_lower for t in anime_triggers)

    if is_image or is_nsfw or is_romantic or is_anime:
        result["type"] = "image"

        # Determine which image API to use
        if "cuckold" in text_lower:
            result["image_key"] = "nsfw_cuckold"
        elif "milf" in text_lower or (is_romantic and is_nsfw):
            result["image_key"] = "nsfw_milf"
        elif "yuri" in text_lower or "lesbian" in text_lower:
            result["image_key"] = "nsfw_yuri"
        elif "pussy" in text_lower:
            result["image_key"] = "nsfw_pussy"
        elif is_nsfw:
            result["image_key"] = "nsfw_pussy"  # Default NSFW
        elif is_anime or "cosplay" in text_lower:
            result["image_key"] = "cosplay"
        elif is_romantic:
            result["image_key"] = "nsfw_milf"
        else:
            result["image_key"] = "cosplay"  # Default safe image

    # ──────────────────────────────────────────
    # 🔄 AI SELECTION DETECTION
    # ──────────────────────────────────────────
    ai_patterns = [
        (r"\buse\s+(?:the\s+)?(gpt[-]?5|gpt5)\b", "gpt5"),
        (r"\buse\s+(?:the\s+)?deep[-_]?ai\b", "deep_ai"),
        (r"\buse\s+(?:the\s+)?deepseek(?:[-_]?v?3)?\b", "deepseek"),
        (r"\buse\s+(?:the\s+)?gemini\b", "gemini"),
        (r"\buse\s+(?:the\s+)?bible(?:[-_]?ai)?\b", "bible"),
        (r"\bswitch\s+(?:to\s+)?(gpt[-]?5|gpt5)\b", "gpt5"),
        (r"\bswitch\s+(?:to\s+)?deep[-_]?ai\b", "deep_ai"),
        (r"\bswitch\s+(?:to\s+)?deepseek(?:[-_]?v?3)?\b", "deepseek"),
        (r"\bswitch\s+(?:to\s+)?gemini\b", "gemini"),
        (r"\bswitch\s+(?:to\s+)?bible(?:[-_]?ai)?\b", "bible"),
        (r"\bset\s+(?:ai\s+)?(?:to\s+)?(gpt[-]?5|gpt5)\b", "gpt5"),
        (r"\bset\s+(?:ai\s+)?(?:to\s+)?deep[-_]?ai\b", "deep_ai"),
        (r"\bset\s+(?:ai\s+)?(?:to\s+)?deepseek(?:[-_]?v?3)?\b", "deepseek"),
        (r"\bset\s+(?:ai\s+)?(?:to\s+)?gemini\b", "gemini"),
        (r"\bset\s+(?:ai\s+)?(?:to\s+)?bible(?:[-_]?ai)?\b", "bible"),
        (r"\bchange\s+(?:ai\s+)?(?:to\s+)?(gpt[-]?5|gpt5)\b", "gpt5"),
        (r"\bchange\s+(?:ai\s+)?(?:to\s+)?deep[-_]?ai\b", "deep_ai"),
        (r"\bchange\s+(?:ai\s+)?(?:to\s+)?deepseek(?:[-_]?v?3)?\b", "deepseek"),
        (r"\bchange\s+(?:ai\s+)?(?:to\s+)?gemini\b", "gemini"),
        (r"\bchange\s+(?:ai\s+)?(?:to\s+)?bible(?:[-_]?ai)?\b", "bible"),
        (r"\bselect\s+(gpt[-]?5|gpt5)\b", "gpt5"),
        (r"\bselect\s+deep[-_]?ai\b", "deep_ai"),
        (r"\bselect\s+deepseek(?:[-_]?v?3)?\b", "deepseek"),
        (r"\bselect\s+gemini\b", "gemini"),
        (r"\bselect\s+bible(?:[-_]?ai)?\b", "bible"),
    ]

    for pattern, api_key in ai_patterns:
        if re.search(pattern, text_lower):
            result["api"] = api_key
            result["type"] = "set_ai"
            break

    # ──────────────────────────────────────────
    # 💻 CODE WRITING DETECTION
    # ──────────────────────────────────────────
    code_triggers = [
        "write code", "code for", "python code", "javascript code", "js code",
        "html code", "css code", "program", "script", "function", "class",
        "algorithm", "leetcode", "solve this", "debug this", "fix code",
        "create code", "make code", "build code", "develop code",
        "কোড লেখ", "পাইথন কোড", "জাভাস্ক্রিপ্ট কোড", "প্রোগ্রাম লেখ",
        "कोड लिखो", "कोड बनाओ", "पाइथन कोड", "जावास्क्रिप्ट कोड",
        "escribe código", "código python", "código javascript", "programa",
        "코드 작성", "코드", "程式", "代码", "寫代碼", "写代码"
    ]

    if any(t in text_lower for t in code_triggers):
        result["is_code"] = True

    # ──────────────────────────────────────────
    # 🧹 CLEAR HISTORY DETECTION
    # ──────────────────────────────────────────
    clear_triggers = [
        "clear history", "forget everything", "reset chat", "new chat",
        "start fresh", "clear memory", "delete history", "bhul jao",
        "সব ভুলে যাও", "ভুলে যাও", "ইতিহাস মুছে ফেল", "নতুন চ্যাট",
        "सब भूल जाओ", "भूल जाओ", "इतिहास मिटाओ", "नया चैट",
        "borrar historial", "limpiar chat", "nuevo chat", "olvidar todo",
        "清除历史", "忘记一切", "新聊天"
    ]
    if any(t in text_lower for t in clear_triggers):
        result["type"] = "clear"

    # ──────────────────────────────────────────
    # ❓ HELP DETECTION
    # ──────────────────────────────────────────
    help_triggers = [
        "help", "commands", "what can you do", "how to use", "guide",
        "instructions", "tutorial", "usage", "info about bot",
        "সাহায্য", "কিভাবে ব্যবহার করব", "বট সম্পর্কে",
        "मदद", "कैसे उपयोग करें", "बॉट के बारे में",
        "ayuda", "comandos", "cómo usar", "guía",
        "帮助", "如何使用", "关于机器人"
    ]
    if any(t in text_lower for t in help_triggers) and len(text_lower) < 50:
        result["type"] = "help"

    # ──────────────────────────────────────────
    # 📊 STATUS / INFO DETECTION
    # ──────────────────────────────────────────
    status_triggers = [
        "what ai", "which ai", "current ai", "show ai", "ai status",
        "কোন এআই", "কারেন্ট এআই", "এআই স্ট্যাটাস",
        "कौन सा AI", "current AI", "AI status"
    ]
    if any(t in text_lower for t in status_triggers):
        result["type"] = "status"

    return result


# ═══════════════════════════════════════════════════════════════════════
# 📝 RESPONSE FORMATTING
# ═══════════════════════════════════════════════════════════════════════

def format_code_response(text: str) -> str:
    """Format code responses with proper markdown blocks"""
    if "```" in text:
        return text

    code_indicators = [
        "def ", "import ", "from ", "class ", "function", "const ", "let ", 
        "var ", ">>>", "print(", "return ", "if __name__", "export ",
        "async ", "await ", "try:", "except", "for ", "while ", "if ",
        "<!DOCTYPE", "<html", "<div", "<script", "<style", "body {",
        "#include", "public class", "function(", "=> {", "console.log"
    ]

    lines = text.split("\n")
    formatted = []
    code_buffer = []
    in_code = False
    lang = "python"

    for line in lines:
        stripped = line.strip()

        # Detect language
        if stripped.startswith("<") and not in_code:
            lang = "html"
        elif "console.log" in stripped or "function" in stripped or "=>" in stripped:
            if not in_code:
                lang = "javascript"
        elif "#include" in stripped or "int main" in stripped:
            if not in_code:
                lang = "cpp"

        is_code = any(stripped.startswith(ind) for ind in code_indicators) or \
                  (in_code and (stripped.startswith("    ") or stripped.startswith("\t") or 
                   stripped.startswith("  ") or stripped == ""))

        if is_code and not in_code:
            in_code = True
            if code_buffer:
                formatted.extend(code_buffer)
                code_buffer = []
            formatted.append(f"```{lang}")
            formatted.append(line)
        elif is_code and in_code:
            formatted.append(line)
        elif not is_code and in_code:
            in_code = False
            formatted.append("```")
            formatted.append(line)
        else:
            formatted.append(line)

    if in_code:
        formatted.append("```")

    return "\n".join(formatted)


def escape_markdown(text: str) -> str:
    """Escape special markdown characters"""
    chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in chars:
        text = text.replace(char, f"\{char}")
    return text


def add_footer(text: str) -> str:
    """Add POWERED BY FREXY footer"""
    if "POWERED BY FREXY" in text:
        return text
    return text + FOOTER


def split_long_message(text: str, max_length: int = 4000) -> List[str]:
    """Split long messages into chunks"""
    if len(text) <= max_length:
        return [text]

    parts = []
    while text:
        if len(text) <= max_length:
            parts.append(text)
            break

        # Try to split at newline
        split_at = text.rfind("\n", 0, max_length)
        if split_at == -1:
            split_at = max_length

        parts.append(text[:split_at])
        text = text[split_at:].lstrip()

    return parts


# ═══════════════════════════════════════════════════════════════════════
# 🤖 TELEGRAM HANDLERS
# ═══════════════════════════════════════════════════════════════════════

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.message.from_user
    welcome = (
        f"👋 **Welcome {user.first_name or 'there'}!**\n\n"
        f"🤖 I'm **Frexy AI Bot** - your smart assistant!\n\n"
        f"✨ **Just send me text messages!** No buttons needed!\n\n"
        f"📋 **What I can do:**\n"
        f"• 💬 **Chat** - Talk about anything in any language\n"
        f"• 🖼️ **Images** - Say "send image of..."\n"
        f"• 💻 **Code** - Say "write code for..."\n"
        f"• 🔄 **Switch AI** - Say "use gpt5" or "switch to deepseek"\n\n"
        f"🧠 **Available AIs:**\n"
        f"• 🧠 GPT-5 | 🔥 Deep AI | 🚀 DeepSeek V3 | 💎 Gemini | 📖 Bible AI\n\n"
        f"🎨 **Image Types:**\n"
        f"• 🎭 Cosplay/Anime | 🔞 NSFW (18+) | 💕 Romantic\n\n"
        f"💡 **Just text me and I'll respond!** 🚀"
    )
    await update.message.reply_text(add_footer(welcome), parse_mode=ParseMode.MARKDOWN)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = (
        "📖 **Frexy AI Bot - Complete Guide**\n\n"
        "🗣️ **Just send text messages! No buttons needed!**\n\n"
        "💬 **Chat Examples:**\n"
        "• "Hello, how are you?"\n"
        "• "Explain quantum physics in Bengali"\n"
        "• "Tell me a joke in Hindi"\n"
        "• "What is the meaning of life?"\n\n"
        "🖼️ **Image Examples:**\n"
        "• "Send image of anime girl" → 🎭 Cosplay\n"
        "• "Generate romantic photo" → 💕 Romantic\n"
        "• "Send 18+ image" → 🔞 NSFW\n"
        "• "Photo of cosplay girl" → 🎭 Anime\n"
        "• "Send nsfw milf image" → 🔞 Specific type\n\n"
        "💻 **Code Examples:**\n"
        "• "Write Python code for calculator"\n"
        "• "Code a login system in JavaScript"\n"
        "• "Debug this code: [paste code]"\n"
        "• "Write HTML CSS for a navbar"\n\n"
        "🔄 **Switch AI (just say):**\n"
        "• "Use gpt5" / "Switch to gpt5"\n"
        "• "Use deepseek" / "Switch to deepseek"\n"
        "• "Use gemini" / "Set AI to gemini"\n"
        "• "Use deep ai" / "Change to deep ai"\n"
        "• "Use bible" / "Switch to bible ai"\n\n"
        "🧹 **Clear Chat:**\n"
        "• "Clear history" / "Forget everything"\n"
        "• "Reset chat" / "New chat"\n"
        "• "সব ভুলে যাও" / "सब भूल जाओ"\n\n"
        "📊 **Check AI:**\n"
        "• "What AI?" / "Which AI?" / "Current AI"\n\n"
        "🌍 **Languages:** English, Bengali, Hindi, Urdu, Spanish, French, "
        "Arabic, Chinese, Japanese, Korean + more!"
    )
    await update.message.reply_text(add_footer(help_text), parse_mode=ParseMode.MARKDOWN)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Main message handler - processes ALL text messages"""

    if not update.message or not update.message.text:
        return

    message = update.message
    user = message.from_user
    chat = message.chat
    text = message.text.strip()

    chat_id = str(chat.id)
    user_id = str(user.id)
    user_name = user.first_name or "User"

    # Show typing indicator
    await context.bot.send_chat_action(chat_id=chat.id, action="typing")

    # Detect intent
    intent = detect_intent(text)

    # ═══════════════════════════════════════════════════════════
    # 🔄 HANDLE SET AI
    # ═══════════════════════════════════════════════════════════
    if intent["type"] == "set_ai" and intent["api"]:
        store.set_user_pref(user_id, "selected_ai", intent["api"])
        store.set_chat_pref(chat_id, "selected_ai", intent["api"])
        ai_info = TEXT_APIS[intent["api"]]
        reply = (
            f"✅ **AI Switched Successfully!** 🎉\n\n"
            f"🤖 Now using: {ai_info['name']}\n"
            f"📌 {ai_info['desc']}\n\n"
            f"💬 Start chatting with {ai_info['emoji']} {ai_info['name']} now!"
        )
        await message.reply_text(add_footer(reply), parse_mode=ParseMode.MARKDOWN)
        return

    # ═══════════════════════════════════════════════════════════
    # 🧹 HANDLE CLEAR HISTORY
    # ═══════════════════════════════════════════════════════════
    if intent["type"] == "clear":
        store.clear_history(chat_id)
        reply = (
            f"🧹 **Chat History Cleared!** ✨\n\n"
            f"Hi {user_name}! Let's start a fresh conversation! 👋\n\n"
            f"💬 What would you like to talk about?"
        )
        await message.reply_text(add_footer(reply), parse_mode=ParseMode.MARKDOWN)
        return

    # ═══════════════════════════════════════════════════════════
    # ❓ HANDLE HELP
    # ═══════════════════════════════════════════════════════════
    if intent["type"] == "help":
        await help_command(update, context)
        return

    # ═══════════════════════════════════════════════════════════
    # 📊 HANDLE STATUS
    # ═══════════════════════════════════════════════════════════
    if intent["type"] == "status":
        current_ai = store.get_user_pref(user_id, "selected_ai") or \
                     store.get_chat_pref(chat_id, "selected_ai") or "gpt5"
        ai_info = TEXT_APIS.get(current_ai, TEXT_APIS["gpt5"])
        reply = (
            f"📊 **Current AI Status**\n\n"
            f"🤖 Active AI: {ai_info['name']}\n"
            f"📌 Description: {ai_info['desc']}\n\n"
            f"🔄 To switch, just say:\n"
            f"• "Use gpt5" | "Use deepseek" | "Use gemini"\n"
            f"• "Use deep ai" | "Use bible""
        )
        await message.reply_text(add_footer(reply), parse_mode=ParseMode.MARKDOWN)
        return

    # ═══════════════════════════════════════════════════════════
    # 🖼️ HANDLE IMAGE GENERATION
    # ═══════════════════════════════════════════════════════════
    if intent["type"] == "image":
        image_key = intent.get("image_key", "cosplay")
        api_info = IMAGE_APIS.get(image_key, IMAGE_APIS["cosplay"])

        # Send generating message
        gen_msg = await message.reply_text(
            f"🎨 **Generating image...**\n"
            f"📌 Type: {api_info['name']}\n"
            f"⏳ Please wait!",
            parse_mode=ParseMode.MARKDOWN
        )

        try:
            async with aiohttp.ClientSession() as session:
                image_url = await fetch_image_api(session, image_key)

                if image_url:
                    await gen_msg.delete()

                    caption = (
                        f"🖼️ **Here is your image!**\n"
                        f"📌 Type: `{api_info['name']}`\n"
                        f"👤 Requested by: {user_name}"
                    ) + FOOTER

                    await message.reply_photo(
                        photo=image_url,
                        caption=caption,
                        parse_mode=ParseMode.MARKDOWN
                    )
                else:
                    await gen_msg.edit_text(
                        "❌ **Failed to generate image.**\n"
                        "The API might be temporarily down. Please try again later!" + FOOTER,
                        parse_mode=ParseMode.MARKDOWN
                    )
        except Exception as e:
            logger.error(f"Image generation error: {e}")
            try:
                await gen_msg.edit_text(
                    "❌ **Image generation failed.**\n"
                    "Please try again in a moment!" + FOOTER,
                    parse_mode=ParseMode.MARKDOWN
                )
            except:
                pass
        return

    # ═══════════════════════════════════════════════════════════
    # 💬 HANDLE TEXT CHAT / CODE
    # ═══════════════════════════════════════════════════════════

    # Get selected AI priority: user > chat > default
    selected_ai = store.get_user_pref(user_id, "selected_ai") or \
                  store.get_chat_pref(chat_id, "selected_ai") or \
                  "gpt5"

    ai_info = TEXT_APIS.get(selected_ai, TEXT_APIS["gpt5"])

    # Add user message to history
    store.add_message(chat_id, "user", text)

    # Build conversation context
    history = store.get_history(chat_id)
    context_text = ""
    if len(history) > 1:
        recent = history[-8:]  # Last 8 messages for context
        context_parts = []
        for msg in recent[:-1]:
            role_label = "User" if msg["role"] == "user" else "Assistant"
            context_parts.append(f"{role_label}: {msg['content'][:250]}")
        if context_parts:
            context_text = "Previous conversation:\n" + "\n".join(context_parts) + "\n\n"

    # Prepare query based on intent
    if intent["is_code"]:
        query = (
            f"{context_text}Write clean, well-commented, production-ready code for this request. "
            f"Use proper markdown code blocks with language specified. "
            f"Include explanations as comments.\n\n"
            f"Request: {text}"
        )
    else:
        query = (
            f"{context_text}You are a helpful, friendly AI assistant. "
            f"Respond naturally and helpfully. Use emojis where appropriate. "
            f"Reply in the SAME LANGUAGE as the user. Be conversational and engaging.\n\n"
            f"User: {text}"
        )

    # Call the API
    try:
        async with aiohttp.ClientSession() as session:
            response_text = await fetch_text_api(session, selected_ai, query)
    except Exception as e:
        logger.error(f"API call error: {e}")
        response_text = (
            "❌ **Oops! Something went wrong.**\n\n"
            "The AI API seems to be unavailable right now. \n"
            "Please try again in a few moments! 🙏"
        )

    # Format code if needed
    if intent["is_code"]:
        response_text = format_code_response(response_text)

    # Build response with AI header
    header = f"{ai_info['emoji']} **{ai_info['name']}**\n\n"
    full_response = header + response_text

    # Add footer
    full_response = add_footer(full_response)

    # Store bot response
    store.add_message(chat_id, "assistant", response_text)

    # Send response (handle long messages)
    parts = split_long_message(full_response)
    for i, part in enumerate(parts):
        try:
            if i == len(parts) - 1 and "POWERED BY FREXY" not in part:
                part = part + FOOTER
            await message.reply_text(part, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            # Fallback: send without markdown
            try:
                clean_part = part.replace("*", "").replace("`", "'").replace("_", " ")
                await message.reply_text(clean_part[:4000])
            except Exception as e2:
                logger.error(f"Failed to send message: {e2}")


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo messages"""
    if not update.message or not update.message.photo:
        return

    user = update.message.from_user

    reply = (
        f"📸 **Photo received!**\n\n"
        f"Hey {user.first_name or 'there'}! 👋\n"
        f"I can see your image! Currently I acknowledge photos.\n"
        f"Image analysis feature coming soon! 🚀\n\n"
        f"💬 Send me a text message to chat!"
    ) + FOOTER

    await update.message.reply_text(reply, parse_mode=ParseMode.MARKDOWN)


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle document/file messages"""
    if not update.message or not update.message.document:
        return

    reply = (
        "📄 **File received!**\n\n"
        "I can see you sent a file! 📎\n"
        "Currently I can only process text messages and images.\n"
        "For code, just paste it as text! 💻"
    ) + FOOTER

    await update.message.reply_text(reply, parse_mode=ParseMode.MARKDOWN)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors gracefully"""
    logger.error(f"Update {update} caused error: {context.error}")
    try:
        if update and update.message:
            await update.message.reply_text(
                "⚠️ **Oops! Something went wrong.**\n"
                "Please try again! 🙏" + FOOTER,
                parse_mode=ParseMode.MARKDOWN
            )
    except:
        pass


# ═══════════════════════════════════════════════════════════════════════
# 👤 ADMIN COMMANDS
# ═══════════════════════════════════════════════════════════════════════

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show bot statistics"""
    user_id = str(update.message.from_user.id)
    username = update.message.from_user.username

    is_admin = int(user_id) in ADMIN_IDS or username == OWNER_USERNAME

    if not is_admin:
        await update.message.reply_text(
            "❌ **Admin only command!**" + FOOTER,
            parse_mode=ParseMode.MARKDOWN
        )
        return

    total_chats = len(store.history)
    total_users = len(store.user_prefs)
    total_msgs = store.stats.get("total_messages", 0)
    start_time = store.stats.get("start_time", "Unknown")

    stats_text = (
        "📊 **Bot Statistics**\n\n"
        f"💬 Total Chats: `{total_chats}`\n"
        f"👥 Unique Users: `{total_users}`\n"
        f"💭 Total Messages: `{total_msgs}`\n"
        f"🤖 Owner: @{OWNER_USERNAME}\n"
        f"⏰ Started: `{start_time}`"
    ) + FOOTER

    await update.message.reply_text(stats_text, parse_mode=ParseMode.MARKDOWN)


async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast message to all users"""
    user_id = str(update.message.from_user.id)
    username = update.message.from_user.username

    is_admin = int(user_id) in ADMIN_IDS or username == OWNER_USERNAME

    if not is_admin:
        await update.message.reply_text(
            "❌ **Admin only command!**" + FOOTER,
            parse_mode=ParseMode.MARKDOWN
        )
        return

    if not context.args:
        await update.message.reply_text(
            "📢 **Broadcast Usage:**\n"
            "`/broadcast Your message here`" + FOOTER,
            parse_mode=ParseMode.MARKDOWN
        )
        return

    broadcast_msg = " ".join(context.args)
    sent = 0
    failed = 0

    for chat_id in list(store.history.keys())[:100]:  # Limit to 100 chats
        try:
            await context.bot.send_message(
                chat_id=int(chat_id),
                text=f"📢 **Broadcast from @{OWNER_USERNAME}**\n\n{broadcast_msg}" + FOOTER,
                parse_mode=ParseMode.MARKDOWN
            )
            sent += 1
        except:
            failed += 1

    await update.message.reply_text(
        f"✅ **Broadcast Complete!**\n\n"
        f"📤 Sent: `{sent}`\n"
        f"❌ Failed: `{failed}`" + FOOTER,
        parse_mode=ParseMode.MARKDOWN
    )


# ═══════════════════════════════════════════════════════════════════════
# 🚀 MAIN FUNCTION
# ═══════════════════════════════════════════════════════════════════════

def main():
    """Start the bot"""
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 14 + "🤖 FREXY AI BOT" + " " * 27 + "║")
    print("║" + " " * 10 + "🔥 POWERED BY FREXY 🔥" + " " * 25 + "║")
    print("╠" + "═" * 58 + "╣")
    print("║  💬 Text Chat    |  🖼️ Image Gen  |  💻 Code Writer         ║")
    print("║  🧠 5 AI Models  |  🌍 Multi-lang  |  📚 Chat History        ║")
    print("╚" + "═" * 58 + "╝")
    print()

    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ ERROR: Please set your BOT_TOKEN in the code!")
        print("   Get your token from @BotFather on Telegram")
        return

    # Build application
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("broadcast", broadcast_command))

    # Message handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    # Error handler
    application.add_error_handler(error_handler)

    print("✅ Bot initialized successfully!")
    print("💬 Users can now send text messages to interact")
    print("🛑 Press Ctrl+C to stop the bot")
    print("─" * 60)

    # Run
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
