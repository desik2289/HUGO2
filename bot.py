import asyncio
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ================== НАСТРОЙКИ ==================
TOKEN = "9225850817:AAHCdSXEWqvaBCy7zgWQ0toY-YX7ieiZqoA"
# Ссылка на твой сайт в Netlify (не забудь менять ?v=... при обновлениях)
WEBAPP_URL = "https://fabulous-torte-14f005.netlify.app/?v=6" 

# ================== БАЗА ДАННЫХ (ТОВАРЫ) ==================
PRODUCTS = [
    {"id": 1, "badge": "6 PCS", "bank": "VISA", "title": "VISA NL Netherlands CC 2DS Debit", "desc": "Bin: 416357 Country: NL", "price": 65.00},
    {"id": 2, "badge": "6 PCS", "bank": "AMEX", "title": "GR Greece American Express NO-VBV Credit", "desc": "Bin: 379995 Country: GR", "price": 60.00},
]

# ================== FASTAPI (ДЛЯ MINI APP) ==================
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/api/products")
async def get_products():
    return {"status": "ok", "products": PRODUCTS}

# ================== TELEGRAM БОТ ==================
router = Router()

def get_main_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="💳 Open mini-app", web_app=WebAppInfo(url=WEBAPP_URL))
    builder.button(text="ℹ️ Info", callback_data="info")
    builder.button(text="💰 Balance", callback_data="balance")
    builder.button(text="🗂 Your cards", callback_data="your_cards")
    builder.adjust(1, 2, 1) 
    return builder.as_markup()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Обновляю меню...", reply_markup=ReplyKeyboardRemove())
    await message.answer(f"Hello {message.from_user.full_name}!", reply_markup=get_main_keyboard())

@router.callback_query(F.data == "info")
async def info_handler(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("🛠 Info about bot.")

@router.callback_query(F.data == "balance")
async def balance_handler(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("💸 Your balance: $0.00")

@router.callback_query(F.data == "your_cards")
async def your_cards_handler(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("You don't have any cards saved yet.")

async def run_bot():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    print("Бот запущен в фоне!")
    await dp.start_polling(bot)

# ================== ЗАПУСК ВСЕГО СРАЗУ ==================
@app.on_event("startup")
async def startup_event():
    # При старте сервера запускаем бота
    asyncio.create_task(run_bot())

if __name__ == "__main__":
    # Bothost сам передаст правильный порт
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
