import os
from pathlib import Path
from dotenv import load_dotenv

# Fayl joylashgan papkadan .env faylni aniq yuklash (har qanday joydan mustaqil ishga tushirish uchun)
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

BOT_TOKEN = (os.getenv("BOT_TOKEN") or "").strip().strip('"').strip("'")
OPENAI_API_KEY = (os.getenv("OPENAI_API_KEY") or "").strip().strip('"').strip("'")
GEMINI_API_KEY = (os.getenv("GEMINI_API_KEY") or "").strip().strip('"').strip("'")
PORT = int(os.getenv("PORT", "8080"))

def validate_config():
    if not BOT_TOKEN:
        print("❌ Xatolik: BOT_TOKEN topilmadi!")
        print(f"👉 .env fayl manzili: {ENV_PATH}")
        return False
    
    if not OPENAI_API_KEY and not GEMINI_API_KEY:
        print("❌ Xatolik: OPENAI_API_KEY yoki GEMINI_API_KEY dan biri .env faylida bo'lishi shart!")
        return False
        
    return True
