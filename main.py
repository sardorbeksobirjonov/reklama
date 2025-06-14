import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ContentType
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from datetime import datetime

# 🔧 SOZLAMALAR
TOKEN = "7662961863:AAEIKABaw7MfaLdnu8JRTSCWcpv6VTztcrc"
CHANNEL_ID = "@reklama_konol"
ADMIN_PAROL = "Love10"
ADMIN_USERNAME = "@sardorbeksobirjonov"

# 🔐 BIR MARTALIK PAROLLAR RO‘YXATI
parollar = {"parol1", "parol123", "reklama2454","love","reklama1020","Love you","289","paroluz","parolOld","reklamaMr","kodL","Prol_sw",}  # Admin bu yerga yangi parollar qo‘shadi

# 📋 FOYDALANUVCHI RO‘YXATI
foydalanuvchilar = []

# 🔄 BOT VA DISPATCHER
logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())

# 🧠 HOLATLAR (FSM)
class Holatlar(StatesGroup):
    reklama_parol = State()
    reklama = State()
    admin_parol = State()
    admin_kirish = State()

# 🚀 /start
@dp.message(F.text == "/start")
async def start(message: Message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text="📢 Reklama berish")],
        [KeyboardButton(text="Admn 👑")]
    ])
    await message.answer("👋 Xush kelibsiz! Quyidagi tugmalardan foydalaning:", reply_markup=kb)

# 📢 Reklama bosilganda
@dp.message(F.text == "📢 Reklama berish")
async def reklama_start(message: Message, state: FSMContext):
    await message.answer(
        f"🔐 Reklama berish uchun parol kiriting.\n"
        f"💵 Narxi: 5 000 so‘m\n"
        f"👤 Parol uchun: {ADMIN_USERNAME}"
    )
    await state.set_state(Holatlar.reklama_parol)

# 🔑 Reklama parol tekshirish
@dp.message(Holatlar.reklama_parol)
async def reklama_parol(message: Message, state: FSMContext):
    global parollar
    kirilgan_parol = message.text.strip()
    if kirilgan_parol in parollar:
        parollar.remove(kirilgan_parol)  # Parolni o‘chiramiz
        await message.answer("✅ Parol to‘g‘ri. Endi reklamangizni yuboring.")
        await state.set_state(Holatlar.reklama)
    else:
        await message.answer("❌ Parol noto‘g‘ri yoki allaqachon ishlatilgan. Yangi parol uchun admin bilan bog‘laning.")
        await state.clear()

# 📤 Reklama yuborish
@dp.message(Holatlar.reklama)
async def reklama_ber(message: Message, state: FSMContext):
    try:
        user_info = f"{message.from_user.full_name} (@{message.from_user.username or 'no_username'})"
        vaqt = datetime.now().strftime("%Y-%m-%d %H:%M")
        reklama_matni = ""

        if message.content_type == ContentType.TEXT:
            reklama_matni = message.text.strip()
            await bot.send_message(CHANNEL_ID, f"📢 Yangi Reklama:\n\n{reklama_matni}")

        elif message.content_type == ContentType.PHOTO:
            reklama_matni = message.caption or ""
            await bot.send_photo(CHANNEL_ID, photo=message.photo[-1].file_id, caption=reklama_matni)

        elif message.content_type == ContentType.VIDEO:
            reklama_matni = message.caption or ""
            await bot.send_video(CHANNEL_ID, video=message.video.file_id, caption=reklama_matni)

        elif message.content_type == ContentType.DOCUMENT:
            reklama_matni = message.caption or ""
            await bot.send_document(CHANNEL_ID, document=message.document.file_id, caption=reklama_matni)

        else:
            await message.answer("❌ Bu turdagi faylni yuborib bo‘lmaydi.")
            return

        foydalanuvchilar.append({
            "ism": user_info,
            "vaqt": vaqt,
            "reklama": reklama_matni or f"{message.content_type} fayl"
        })

        await message.answer(
            f"✅ Reklama kanalga yuborildi!\n"
            f"📡 Kanal: <b>{CHANNEL_ID}</b>"
        )
    except Exception as e:
        await message.answer(f"⚠️ Xatolik:\n{e}")
    await state.clear()

# 👑 Admin panel
@dp.message(F.text == "Admn 👑")
async def admin_bosildi(message: Message, state: FSMContext):
    await message.answer("🔐 Admin parolni kiriting:")
    await state.set_state(Holatlar.admin_parol)

# Admin parol tekshirish
@dp.message(Holatlar.admin_parol)
async def admin_parol(message: Message, state: FSMContext):
    if message.text.strip() == ADMIN_PAROL:
        kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
            [KeyboardButton(text="👥 Foydalanuvchilarni ko‘rish")],
            [KeyboardButton(text="⬅️ Ortga")]
        ])
        await message.answer("✅ Admin paneliga xush kelibsiz!", reply_markup=kb)
        await state.set_state(Holatlar.admin_kirish)
    else:
        await message.answer("❌ Noto‘g‘ri parol.")
        await state.clear()

# 👥 Foydalanuvchilar ro‘yxatini ko‘rsatish
@dp.message(Holatlar.admin_kirish, F.text == "👥 Foydalanuvchilarni ko‘rish")
async def foydalanuvchilarni_korish(message: Message):
    if not foydalanuvchilar:
        await message.answer("📭 Hozircha hech kim reklama bermagan.")
    else:
        javob = "📋 Reklama berganlar:\n\n"
        for i, user in enumerate(foydalanuvchilar, 1):
            javob += (
                f"{i}. 👤 {user['ism']}\n"
                f"   🕒 {user['vaqt']}\n"
                f"   📢 {user['reklama'][:100]}...\n\n"
            )
        await message.answer(javob)

# ⬅️ Ortga
@dp.message(F.text == "⬅️ Ortga")
async def ortga(message: Message, state: FSMContext):
    await state.clear()
    await start(message)

# ▶️ Botni ishga tushirish
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
