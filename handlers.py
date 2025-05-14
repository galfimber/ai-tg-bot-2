# handlers.py

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart

router = Router()

@router.message(CommandStart())
@router.message(F.text)
async def echo(message: Message):
    print(f"📩 Получено сообщение от пользователя: {message.from_user.id} — {message.text}")
    await message.answer(f"🟢 Я получил ваше сообщение:\n\n{message.text}")