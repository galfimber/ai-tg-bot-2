# app.py

import os
import asyncio
from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

# Импорты
from bot import bot, dp
from config import SECRET_TOKEN, WEBHOOK_PATH

async def on_startup(app):
    webhook_url=f"{os.getenv('WEBHOOK_HOST')}{WEBHOOK_PATH}"
    await bot.set_webhook(webhook_url, secret_token=SECRET_TOKEN)

app = web.Application()
SimpleRequestHandler(dispatcher=dp, bot=bot, secret_token=SECRET_TOKEN).register(app, path=WEBHOOK_PATH)
setup_application(app, dp, bot=bot)
app.on_startup.append(on_startup)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))