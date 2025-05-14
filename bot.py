# bot.py

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN, dafault=DefaultBotProperties(parse_mode=ParseMode.HTML)) 
dp = Dispatcher()