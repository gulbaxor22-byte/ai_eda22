import base64
import io
import json
import logging
import aiohttp
from PIL import Image
from config import GEMINI_API_KEY, OPENAI_API_KEY

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
Sen professional dietolog va ozuqa tahlilchisi (AI Nutritionist) yordamchisisan.
Vazifang: Foydalanuvchi yuborgan rasm(lar)dagi taomlarni aniqlash va ularning kaloriyasi hamda ozuqaviy qiymatini o'zbek tilida, aniq va chiroyli formatda tahlil qilib berish.

Agar rasmda taom, yegulik yoki ichimlik bo'lsa, quyidagi tartibda javob ber:

🍽 **Taom nomi**: [Taom yoki mahsulotlarning aniq nomi]
🔥 **Umumiy kaloriya**: [Taxminiy umumiy kkal miqdori, masalan: ~550 kkal]

📊 **Ozuqaviy qiymat (BJU / Makronutrientlar)**:
• 🥩 **Oqsillar (Protein)**: ~XX g
• 🧈 **Yog'lar (Fats)**: ~XX g
• 🍞 **Uglevodlar (Carbs)**: ~XX g

🥗 **Tarkibi va porsiya miqdori**:
• [Mahsulot 1] — taxminan [XX g] (~YY kkal)
• [Mahsulot 2] — taxminan [XX g] (~YY kkal)
• [Mahsulot 3] — taxminan [XX g] (~YY kkal)

💡 **Foydali maslahat / Eslatma**:
[Taomning sog'liq uchun foydasi, iste'mol qilish vaqti (nonushta, tushlik, kechki ovqat) yoki parhez bo'yicha qisqa tavsiya.]

Muhim qoidalar:
1. Agar rasmda taom yoki yegulik bo'lmasa, xushmuomalalik bilan: "❌ Rasmda taom yoki oziq-ovqat mahsuloti aniqlanmadi. Iltimos, taom yoki yegulik rasmini yuboring!" deb javob ber.
2. Har doim o'zbek tilida, tushunarli, chiroyli emojilar bilan Markdown formatida javob yoz.
3. Hisob-kitoblar vizual ko'rinishga asoslangan taxminiy o'rtacha qiymat ekanligini unutmang.
"""

def prepare_image(image_bytes: bytes) -> bytes:
    """Rasmni standart RGB JPEG formatiga o'tkazish va o'lchamini optimallashtirish"""
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img.thumbnail((1024, 1024))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)
        return buf.getvalue()
    except Exception:
        return image_bytes


async def analyze_food_with_openai(image_bytes: bytes) -> str:
    """OpenAI Vision (gpt-4o-mini / gpt-4o) orqali rasmni tahlil qilish"""
    from openai import AsyncOpenAI
    
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    opt_bytes = prepare_image(image_bytes)
    base64_image = base64.b64encode(opt_bytes).decode("utf-8")
    
    models_to_try = ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini", "gpt-4-turbo"]
    last_error = None

    for model_name in models_to_try:
        try:
            response = await client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Ushbu rasmdagi taomning kaloriyasini va ozuqaviy qiymatini tahlil qilib ber."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )
            if response.choices and response.choices[0].message.content:
                return response.choices[0].message.content
        except Exception as e:
            last_error = e
            continue
            
    raise last_error if last_error else RuntimeError("OpenAI javob qaytarmadi.")


async def analyze_food_with_gemini_rest(image_bytes: bytes) -> str:
    """To'g'ridan-to'g'ri Google Gemini REST API orqali rasmni tahlil qilish"""
    opt_bytes = prepare_image(image_bytes)
    base64_img = base64.b64encode(opt_bytes).decode("utf-8")
    
    models = [
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-flash-8b",
        "gemini-1.5-flash-latest",
        "gemini-1.5-pro",
        "gemini-2.0-flash-exp"
    ]
    api_versions = ["v1beta", "v1"]
    
    # 1. Payload with system prompt embedded
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": SYSTEM_PROMPT + "\n\nUshbu rasmdagi taomning kaloriyasini va ozuqaviy qiymatini tahlil qilib ber."
                    },
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": base64_img
                        }
                    }
                ]
            }
        ],
        "generationConfig": {
            "maxOutputTokens": 1000,
            "temperature": 0.4
        }
    }
    
    last_err = None
    headers = {"Content-Type": "application/json"}
    
    async with aiohttp.ClientSession() as session:
        for ver in api_versions:
            for model_name in models:
                url = f"https://generativelanguage.googleapis.com/{ver}/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
                try:
                    async with session.post(url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=35)) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            candidates = data.get("candidates", [])
                            if candidates and "content" in candidates[0]:
                                parts = candidates[0]["content"].get("parts", [])
                                if parts and "text" in parts[0]:
                                    return parts[0]["text"]
                        else:
                            body = await resp.text()
                            last_err = f"HTTP {resp.status} ({model_name}, {ver})"
                except Exception as e:
                    last_err = str(e)
                    continue
                    
    raise RuntimeError(last_err or "Gemini REST API dan javob olinmadi.")


async def analyze_food_image(image_bytes: bytes) -> str:
    """
    Rasm baytlarini qabul qiladi va OpenAI yoki Gemini AI yordamida tahlil qiladi.
    Biri ishlamay qolsa, ikkinchisiga avtomatik o'tadi.
    """
    errors = []
    
    # 1. OpenAI orqali urinib ko'rish (eng aniq va barqaror)
    if OPENAI_API_KEY:
        try:
            return await analyze_food_with_openai(image_bytes)
        except Exception as e:
            err_msg = f"OpenAI xatoligi: {e}"
            logger.warning(err_msg)
            errors.append(err_msg)
            
    # 2. Gemini REST API orqali urinib ko'rish
    if GEMINI_API_KEY:
        try:
            return await analyze_food_with_gemini_rest(image_bytes)
        except Exception as e:
            err_msg = f"Gemini xatoligi: {e}"
            logger.warning(err_msg)
            errors.append(err_msg)
            
    if not OPENAI_API_KEY and not GEMINI_API_KEY:
        return (
            "❌ AI API kaliti topilmadi!\n\n"
            "Iltimos, Railway Variables yoki .env faylida `OPENAI_API_KEY` yoki `GEMINI_API_KEY` mavjudligini tekshiring."
        )
        
    return f"⚠️ Tahlil jarayonida xatolik yuz berdi:\n" + "\n".join(errors)
