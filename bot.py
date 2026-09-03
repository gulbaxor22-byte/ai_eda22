import asyncio
import io
import logging
import sys

# Windows konsolida UTF-8 ni to'g'ri ishlashi uchun
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from aiogram import Bot, Dispatcher, F, types
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup

from aiohttp import web
from ai_service import analyze_food_image
from config import BOT_TOKEN, PORT, validate_config

# Loglarni sozlash
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Dispatcher va Bot obyekti
dp = Dispatcher()

async def handle_health_check(request):
    """Bulutli serverlar (Render, Koyeb va h.k.) uchun 200 OK qaytaruvchi health check"""
    return web.json_response({
        "status": "ok",
        "service": "AI Calorie Telegram Bot",
        "message": "Bot muvaffaqiyatli ishlamoqda!"
    })

async def start_web_server():
    """Health-check veb-serverini ishga tushirish (404 xatoliklarini oldini oladi)"""
    app = web.Application()
    app.router.add_get("/", handle_health_check)
    app.router.add_get("/health", handle_health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logger.info(f"🌐 Health-check veb-server {PORT}-portda ishga tushirildi.")
    return runner

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    """
    /start buyrug'i uchun handler.
    """
    user_name = message.from_user.first_name if message.from_user else "Foydalanuvchi"
    text = (
        f"Salom, <b>{user_name}</b>! 👋\n\n"
        f"Men 🥗 <b>AI Calorie Bot</b>man.\n"
        f"Menga istalgan taom yoki mahsulot rasmini yuboring, men uning:\n"
        f"• 🔥 <b>Kaloriyasi (kkal)</b>\n"
        f"• 🥩 <b>Oqsil, Yog', Uglevodlar (BJU)</b>\n"
        f"• 🥗 <b>Tarkibi va porsiya hajmini</b>\n"
        f"sun'iy intellekt (AI Vision) yordamida aniqlab beraman!\n\n"
        f"📸 <i>Boshlash uchun hoziroq taom rasmini yuboring!</i>"
    )
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="ℹ️ Bot haqida / Yordam", callback_data="help_info")
            ]
        ]
    )
    await message.answer(text, parse_mode=ParseMode.HTML, reply_markup=keyboard)


@dp.message(Command("help"))
@dp.callback_query(F.data == "help_info")
async def cmd_help(event: types.Message | types.CallbackQuery):
    """
    /help buyrug'i va Yordam tugmasi uchun handler.
    """
    text = (
        "📖 <b>Botdan qanday foydalanish kerak?</b>\n\n"
        "1️⃣ O'zingiz iste'mol qilayotgan yoki tayyorlagan taomni suratga oling.\n"
        "2️⃣ Rasmni to'g'ridan-to'g'ri ushbu botga yuboring.\n"
        "3️⃣ AI bir necha soniya ichida taomni taniydi va to'liq kaloriyalar hisobini taqdim etadi!\n\n"
        "💡 <b>Tavsiya:</b> Rasmda taom yaxshi yoritilgan va aniq ko'ringan bo'lsa, natija yanada aniqroq bo'ladi."
    )
    
    if isinstance(event, types.CallbackQuery):
        await event.message.answer(text, parse_mode=ParseMode.HTML)
        await event.answer()
    else:
        await event.answer(text, parse_mode=ParseMode.HTML)


@dp.message(F.photo | (F.document & F.document.mime_type.startswith("image/")))
async def handle_photo(message: types.Message, bot: Bot):
    """
    Foydalanuvchi yuborgan rasmni qabul qilib, AI orqali kaloriya hisoblash.
    """
    # Kutish xabarini yuborish
    status_msg = await message.reply("⏳ <b>Taom rasmi tahlil qilinmoqda...</b>\n<i>Iltimos, bir oz kuting.</i>", parse_mode=ParseMode.HTML)
    
    # Telegramda 'yozmoqda...' indikatorini ko'rsatish
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")

    try:
        # Eng yuqori sifatli rasmni yoki hujjatni olish
        photo_bytes_io = io.BytesIO()
        if message.photo:
            photo = message.photo[-1]
            await bot.download(photo, destination=photo_bytes_io)
        elif message.document:
            await bot.download(message.document, destination=photo_bytes_io)
        else:
            await status_msg.edit_text("❌ Rasm topilmadi. Iltimos, qaytadan yuboring.", parse_mode=ParseMode.HTML)
            return

        photo_bytes = photo_bytes_io.getvalue()

        # AI servisiga yuborish va natija olish
        result_text = await analyze_food_image(photo_bytes)

        # Holat xabarini o'chirish
        try:
            await status_msg.delete()
        except Exception:
            pass
        
        # Natijani yuborish (Markdown yoki HTML yoki oddiy matn)
        try:
            await message.reply(result_text, parse_mode=ParseMode.MARKDOWN)
        except Exception:
            # Agar Markdown xatosi bo'lsa, oddiy matn sifatida chiqarish
            await message.reply(result_text)

    except Exception as e:
        logger.error(f"Rasm qayta ishlashda xatolik: {e}")
        try:
            await status_msg.edit_text(
                "❌ Rasmni qayta ishlashda xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.",
                parse_mode=ParseMode.HTML
            )
        except Exception:
            await message.reply("❌ Rasmni qayta ishlashda xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")


@dp.message(F.text)
async def handle_text(message: types.Message):
    """
    Foydalanuvchi matn yuborganida yo'riqnoma berish.
    """
    await message.reply(
        "📷 Iltimos, taomning <b>rasmini</b> yuboring. Men faqat fotosuratlar orqali kaloriya hisoblay olaman!",
        parse_mode=ParseMode.HTML
    )


async def set_main_menu(bot: Bot):
    """
    Bot menyu tugmalarini o'rnatish.
    """
    main_menu_commands = [
        BotCommand(command="/start", description="Botni qayta ishga tushirish"),
        BotCommand(command="/help", description="Yordam va qo'llanma"),
    ]
    await bot.set_my_commands(main_menu_commands)


async def main():
    """
    Botni ishga tushirish funksiyasi.
    """
    if not validate_config():
        sys.exit(1)

    bot = Bot(token=BOT_TOKEN)
    
    # Menyu buyruqlarini sozlash
    await set_main_menu(bot)
    
    # Eski webhook va ziddiyatlarni tozalash (404/Conflict xatolarining oldini oladi)
    await bot.delete_webhook(drop_pending_updates=True)
    
    web_runner = None
    try:
        web_runner = await start_web_server()
    except Exception as e:
        logger.warning(f"Veb-server ogohlantirishi (Polling davom etadi): {e}")

    print("🚀 AI Calorie Telegram Bot muvaffaqiyatli ishga tushdi!")
    print("Bot xabarlarni kutmoqda...")
    
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        if web_runner:
            try:
                await web_runner.cleanup()
            except Exception:
                pass
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("\n🛑 Bot to'xtatildi.")
