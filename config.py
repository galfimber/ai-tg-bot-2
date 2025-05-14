# config.py

from os import getenv

# Токены и ключи API (берутся из переменных окружения)
BOT_TOKEN = getenv("BOT_TOKEN")
OPENROUTER_API_KEY = getenv("OPENROUTER_API_KEY")
REPLICATE_API_TOKEN = getenv("REPLICATE_API_TOKEN")

# Webhook
WEBHOOK_HOST = getenv("WEBHOOK_HOST", "ai-tg-bot-2.railway.internal")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
SECRET_TOKEN = getenv("SECRET_TOKEN")

# Модели AI
TEXT_MODEL = "google/gemma-7b-it"
IMAGE_GEN_MODEL = "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b"
INPAINTING_MODEL = "arielreplicate/rembg:476680b575388b5cd2d0ce93fb7a51658ff1d4ef7f35c334f69630ab25a3da736"