import base64
import io
from config import GEMINI_API_KEY, OPENAI_API_KEY

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

async def analyze_food_with_openai(image_bytes: bytes) -> str:
    """OpenAI Vision (gpt-4o-mini) orqali rasmni tahlil qilish"""
    from openai import AsyncOpenAI
    
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    base64_image = base64.b64encode(image_bytes).decode("utf-8")
    
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
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
    return response.choices[0].message.content


async def analyze_food_with_gemini(image_bytes: bytes) -> str:
    """Google Gemini orqali rasmni tahlil qilish"""
    import google.generativeai as genai
    from PIL import Image
    
    genai.configure(api_key=GEMINI_API_KEY)
    image = Image.open(io.BytesIO(image_bytes))
    
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=SYSTEM_PROMPT
    )
    
    response = await model.generate_content_async(
        [image, "Ushbu rasmdagi taomning kaloriyasini va ozuqaviy qiymatini tahlil qilib ber."]
    )
    return response.text if response and response.text else "⚠️ Tahlil natijasi bo'sh qaytdi."


async def analyze_food_image(image_bytes: bytes) -> str:
    """
    Rasm baytlarini qabul qiladi va OpenAI yoki Gemini AI yordamida tahlil qiladi.
    """
    try:
        if OPENAI_API_KEY:
            return await analyze_food_with_openai(image_bytes)
        elif GEMINI_API_KEY:
            return await analyze_food_with_gemini(image_bytes)
        else:
            return "❌ AI API kaliti topilmadi (.env faylini tekshiring)."
    except Exception as e:
        print(f"AI Service Error: {e}")
        return f"⚠️ Tahlil jarayonida xatolik yuz berdi: {str(e)}"
