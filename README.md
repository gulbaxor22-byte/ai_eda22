# 🥗 AI Calorie Tracker Telegram Bot

Ushbu Telegram bot foydalanuvchi yuborgan taom rasmini **Google Gemini AI (Vision)** orqali tahlil qilib, uning tarkibidagi kaloriyalar, oqsillar, yog'lar, uglevodlar (BJU) va mahsulotlar ro'yxatini hisoblab beradi.

---

## 📌 Asosiy Xususiyatlar
- 📸 **Rasm orqali tahlil**: Taom fotosuratini yuborishning o'zi kifoya.
- 🔥 **Kaloriya hisobi**: Aniq va taxminiy umumiy kkal miqdori.
- 🥩 **BJU balansi**: Oqsil (Protein), Yog' (Fats), Uglevodlar (Carbs).
- 🥗 **Tarkib tafsilotlari**: Taomdagi har bir masalliq va uning taxminiy vazni (gramm).
- 💡 **Dietolog maslahati**: Taomni iste'mol qilish bo'yicha tavsiyalar.
- 🇺🇿 **To'liq o'zbek tilida**.

---

## 🚀 Ishga tushirish bo'yicha qo'llanma

### 1. Kerakli kalitlarni olish

#### A. Telegram Bot Token:
1. Telegramda [@BotFather](https://t.me/BotFather) botiga kiring.
2. `/newbot` buyrug'ini yuboring.
3. Botingizga nom va username bering.
4. BotFather sizga bergan `HTTP API token`ni nusxalab oling.

#### B. Google Gemini API Kaliti (Bepul):
1. [Google AI Studio](https://aistudio.google.com/) saytiga kiring.
2. Google hisobingiz bilan tizimga kiring.
3. **"Get API key"** tugmasini bosing va yangi kalit (API Key) yarating.
4. Ushbu kalitni nusxalab oling.

---

### 2. Sozlamalarni kiritish (.env)

Loyiha papkasidagi `.env` faylini oching va kalitlaringizni kiriting:

```env
BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ
GEMINI_API_KEY=AIzaSyD...sizning_gemini_kalitingiz...
```

---

### 3. Kutubxonalarni o'rnatish

Terminal / CMD ochib, loyiha papkasida quyidagi buyruqni bajaring:

```bash
pip install -r requirements.txt
```

---

### 4. Botni ishga tushirish

Botingizni bir necha usulda ishga tushirishingiz mumkin:

#### 1-usul: Oddiy terminal orqali
```bash
python bot.py
```

#### 2-usul: 1 marta bosish orqali (`start_bot.bat`)
`start_bot.bat` fayliga 2 marta bosing. Bot alohida oynada ochiladi va avtomatik qayta ishga tushish (auto-restart) xususiyatiga ega bo'ladi.

#### 3-usul: Orqa fonda oynasiz ishga tushirish (`run_background.vbs`)
`run_background.vbs` faylini ishga tushiring. Bot fonda (yashirin) ishlayveradi va siz Antigravity yoki boshqa oynalarni bemalol yopishingiz mumkin!
Botni to'xtatish uchun esa `stop_bot.bat` faylini bosish kifoya.

---

## 📁 Loyiha Strukturasi
```
aieda/
├── bot.py             # Asosiy Telegram bot kodi (aiogram 3 + aiohttp health check)
├── ai_service.py      # OpenAI & Gemini Vision bilan rasm tahlili
├── config.py          # Sozlamalar va .env fayli tekshiruvi
├── requirements.txt   # Kerakli Python kutubxonalari
├── start_bot.bat      # Botni alohida oynada ishga tushirish (auto-restart bilan)
├── run_background.vbs # Botni orqa fonda (yashirin) ishga tushirish
├── stop_bot.bat       # Ishlayotgan botni to'xtatish
├── .env               # API kalitlar fayli
├── .env.example       # Namunaviy parametrlar
└── README.md          # Qo'llanma
```
