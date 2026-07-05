# 🤖 Frexy AI Bot - Telegram Chat Bot

**No buttons, no commands - Just text and chat!**

A powerful Telegram bot that supports text chat, image generation, and code writing with multiple AI APIs.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 💬 **Smart Chat** | Talk naturally in any language |
| 🖼️ **Image Generation** | Generate images by just asking |
| 💻 **Code Writer** | Write Python, JS, HTML, CSS code |
| 🧠 **5 AI Models** | GPT-5, Deep AI, DeepSeek V3, Gemini, Bible AI |
| 🌍 **Multi-Language** | Auto-detects and replies in your language |
| 📝 **Chat History** | Remembers conversation in groups & private |
| 🔞 **NSFW Support** | 18+ image generation available |
| 🎨 **Anime/Cosplay** | Beautiful anime girl images |
| 📸 **Photo Support** | Can receive and process photos |
| ⚡ **Fast & Smooth** | Async handling, no lag |

---

## 🚀 Quick Setup

### Step 1: Install Requirements
```bash
pip install -r requirements.txt
```

### Step 2: Get Bot Token
1. Go to [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot`
3. Follow instructions to create your bot
4. Copy the **HTTP API Token**

### Step 3: Configure Bot
Open `frexy_ai_bot.py` and replace:
```python
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
```
with your actual token:
```python
BOT_TOKEN = "123456789:ABCdefGHIjklMNOpqrSTUvwxyz"
```

### Step 4: Run the Bot
```bash
python frexy_ai_bot.py
```

---

## 💬 How to Use (Just Text!)

### 🗨️ Normal Chat
Simply send any message:
- `"Hello, how are you?"`
- `"Explain quantum physics in Bengali"`
- `"Tell me a joke"`

### 🖼️ Generate Images
Just ask for an image:
- `"Send image of anime girl"` → Cosplay image
- `"Generate romantic photo"` → Romantic image
- `"Send 18+ image"` → NSFW image
- `"Photo of cosplay girl"` → Anime cosplay

**Available Image Types:**
| Ask For | Result |
|---------|--------|
| `anime`, `cosplay`, `waifu` | Beautiful anime girl |
| `romantic`, `love`, `couple` | Romantic image |
| `nsfw`, `18+`, `adult` | 18+ image (default: pussy) |
| `cuckold` | NSFW cuckold image |
| `milf` | NSFW milf image |
| `yuri` | NSFW yuri image |
| `pussy` | NSFW pussy image |

### 💻 Write Code
Just ask for code:
- `"Write Python code for calculator"`
- `"Code a login system in JavaScript"`
- `"Debug this code: [paste your code]"`

Code will be formatted with proper markdown for easy copying!

### 🔄 Switch AI Model
Just say:
- `"Use gpt5"` or `"Switch to gpt5"`
- `"Use deepseek"` or `"Switch to deepseek"`
- `"Use gemini"` or `"Set AI to gemini"`
- `"Use deep ai"` or `"Switch to deep-ai"`
- `"Use bible"` or `"Set AI to bible"`

### 🧹 Clear Chat History
- `"Clear history"`
- `"Forget everything"`
- `"Reset chat"`
- `"New chat"`

### 🆘 Get Help
- `"Help"`
- `"How to use"`
- `"What can you do"`

---

## 🧠 Available AI Models

| AI | Command | Description |
|----|---------|-------------|
| 🧠 GPT-5 | `use gpt5` | Latest GPT model |
| 🔥 Deep AI | `use deep ai` | Deep AI responses |
| 🚀 DeepSeek V3 | `use deepseek` | DeepSeek model |
| 💎 Gemini | `use gemini` | Google Gemini |
| 📖 Bible AI | `use bible` | Bible-based AI |

---

## 🌍 Supported Languages

The bot auto-detects your language and replies in the same language:
- 🇺🇸 English
- 🇧🇩 Bengali (বাংলা)
- 🇮🇳 Hindi (हिन्दी)
- 🇵🇰 Urdu (اردو)
- 🇪🇸 Spanish (Español)
- 🇫🇷 French (Français)
- 🇸🇦 Arabic (العربية)
- 🇨🇳 Chinese (中文)
- 🇯🇵 Japanese (日本語)
- 🇰🇷 Korean (한국어)
- And many more!

---

## 🔧 Admin Commands

| Command | Access | Description |
|---------|--------|-------------|
| `/stats` | Admin only | View bot statistics |
| `/broadcast <msg>` | Admin only | Send message to all users |

To set admin, add your Telegram ID to `ADMIN_IDS` list in the code.

---

## 📁 File Structure

```
📂 frexy-ai-bot/
├── 📄 frexy_ai_bot.py      # Main bot code
├── 📄 requirements.txt      # Python dependencies
├── 📄 README.md             # This file
├── 📄 bot_data_history.json # Chat history (auto-created)
├── 📄 bot_data_users.json   # User preferences (auto-created)
└── 📄 bot_data_chats.json   # Chat preferences (auto-created)
```

---

## ⚙️ API Configuration

### Text APIs (Already Configured)
All 5 text APIs are pre-configured in the code. You can modify them in the `TEXT_APIS` dictionary.

### Image APIs (Already Configured)
All 5 image APIs are pre-configured in the `IMAGE_APIS` dictionary.

### Adding More APIs
To add a new API, edit the dictionaries:

```python
# Add new text API
TEXT_APIS["my_new_ai"] = {
    "url": "https://your-api.com/chat",
    "param": "query",  # URL parameter name
    "name": "🌟 My AI",
    "type": "query"
}

# Add new image API
IMAGE_APIS["my_image"] = "https://your-api.com/image"
```

---

## 🛠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| Bot not responding | Check if BOT_TOKEN is correct |
| API timeout | APIs might be down, try again |
| Image not sending | Check if image API URL is working |
| Code formatting broken | Telegram might strip markdown, try again |
| Bot crashes | Check logs for error messages |

---

## 🔒 Safety Notes

- NSFW content is available - use responsibly
- Chat history is stored locally in JSON files
- No data is sent to third parties except the configured APIs
- Admin commands are restricted to configured admins

---

## 👤 Owner

**Powered by FREXY** 🔥
- Telegram: [@frexy1only](https://t.me/frexy1only)

---

## 📜 License

Free to use and modify. Give credit to FREXY if sharing! 💪
