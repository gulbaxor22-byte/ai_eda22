import os
from dotenv import load_dotenv

# .env faylidan o'zgaruvchilarni yuklash
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def validate_config():
    if not BOT_TOKEN:
        print("❌ Xatolik: BOT_TOKEN .env faylida topilmadi!")
        return False
    
    if not OPENAI_API_KEY and not GEMINI_API_KEY:
        print("❌ Xatolik: OPENAI_API_KEY yoki GEMINI_API_KEY dan biri .env faylida bo'lishi shart!")
        return False
        
    return True
