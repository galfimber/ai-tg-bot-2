# app.py

import os
from aiohttp import web
from aiogram.webhook.aiohttp_server import setup_application
from aiogram.webhook import SimpleRequestHandler

# Импорты из других файлов
from bot import bot, dp

async def on_startup(app):
    print("✅ Бот успешно запущен")
    webhook_url = f"{os.getenv('WEBHOOK_HOST')}/webhook"
    try:
        await bot.set_webhook(webhook_url)
        print(f"🟢 Webhook установлен: {webhook_url}")
    except Exception as e:
        print(f"⚠️ Не удалось установить webhook: {e}")

async def handle_request(request):
    print("📥 Получен запрос:", request.method, request.path, dict(request.headers))
    return web.Response(text="OK", status=200)

app = web.Application()
app.router.add_get("/webhook", handle_request)  # GET для проверки
app.router.add_post("/webhook", handle_request)  # POST от Telegram

setup_application(app, dp, bot=bot)
app.on_startup.append(on_startup)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))  # Render использует порт 10000
    web.run_app(app, host="0.0.0.0", port=port)