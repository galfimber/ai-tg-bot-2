# handlers.py

import logging
import asyncio
from aiogram import F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
import aiohttp

from bot import dp, bot
from config import OPENROUTER_API_KEY, REPLICATE_API_TOKEN, TEXT_MODEL, IMAGE_GEN_MODEL, INPAINTING_MODEL

# ========== Настройка логирования ==========
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== Клавиатура ==========
menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💬 Новый вопрос")],
        [KeyboardButton(text="🖼️ Сгенерировать картинку")],
        [KeyboardButton(text="✂️ Редактировать изображение")]
    ],
    resize_keyboard=True
)

# ========== Машина состояний ==========
class UserState(StatesGroup):
    waiting_for_text_prompt = State()
    waiting_for_image_prompt = State()
    waiting_for_image_upload = State()
    waiting_for_edit_prompt = State()

# ========== Хранилище истории ==========
user_histories = {}  # {user_id: [{"role": "user", "content": ...}, ...]}

# ========== Обработчики ==========
@dp.message(F.text == "💬 Новый вопрос")
async def ask_new_question(message: Message, state: FSMContext):
    await message.answer("Напиши свой вопрос:")
    await state.set_state(UserState.waiting_for_text_prompt)

@dp.message(F.text == "🖼️ Сгенерировать картинку")
async def ask_image_prompt(message: Message, state: FSMContext):
    await message.answer("Опиши, какую картинку ты хочешь:")
    await state.set_state(UserState.waiting_for_image_prompt)

@dp.message(F.text == "✂️ Редактировать изображение")
async def ask_for_image_upload(message: Message, state: FSMContext):
    await message.answer("Загрузи изображение, которое нужно отредактировать:")
    await state.set_state(UserState.waiting_for_image_upload)

# ========== Диалог с контекстом ==========
@dp.message(UserState.waiting_for_text_prompt)
async def handle_text_query(message: Message, state: FSMContext):
    user_query = message.text
    user_id = message.from_user.id

    if user_id not in user_histories:
        user_histories[user_id] = []

    user_histories[user_id].append({"role": "user", "content": user_query})
    history = user_histories[user_id]

    await message.answer("🧠 Обрабатываю ваш запрос...")

    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }

            data = {
                "model": TEXT_MODEL,
                "messages": history
            }

            async with session.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data) as resp:
                if resp.status != 200:
                    logger.error(f"OpenRouter error: {resp.status}")
                    await message.answer("Ошибка при получении ответа.")
                    return

                result = await resp.json()
                answer = result["choices"][0]["message"]["content"]
                user_histories[user_id].append({"role": "assistant", "content": answer})

                await message.answer(answer)

        await state.set_state(UserState.waiting_for_text_prompt)

    except Exception as e:
        logger.exception("Ошибка при обработке текстового запроса")
        await message.answer("Произошла ошибка. Попробуйте позже.")

# ========== Генерация изображения ==========
@dp.message(UserState.waiting_for_image_prompt)
async def handle_image_query(message: Message, state: FSMContext):
    image_prompt = message.text
    await message.answer("🎨 Генерирую изображение...")

    headers = {
        "Authorization": f"Token {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "version": IMAGE_GEN_MODEL,
        "input": {"prompt": image_prompt}
    }

    async with aiohttp
    () as session:
        async with session.post("https://api.replicate.com/v1/predictions", headers=headers, json=payload) as resp:
            if resp.status != 201:
                logger.error(f"Replicate image gen error: {resp.status}")
                await message.answer("Ошибка при создании задачи генерации изображения.")
                return

            prediction = await resp.json()
            prediction_id = prediction["id"]

            while True:
                await asyncio.sleep(2)
                status_url = f"https://api.replicate.com/v1/predictions/{prediction_id}"
                async with session.get(status_url, headers=headers) as status_resp:
                    status_data = await status_resp.json()
                    if status_data["status"] == "succeeded":
                        image_url = status_data["output"][0]
                        await message.answer_photo(photo=image_url)
                        break
                    elif status_data["status"] == "failed":
                        logger.error("Ошибка генерации изображения")
                        await message.answer("Ошибка при генерации изображения.")
                        break

    await state.clear()

# ========== Редактирование изображения ==========
@dp.message(UserState.waiting_for_image_upload, F.photo)
async def handle_image_upload(message: Message, state: FSMContext):
    photo = message.photo[-1]
    file_id = photo.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"

    await state.update_data(image_url=file_url)
    await message.answer("Опиши, что ты хочешь изменить на этом изображении:")
    await state.set_state(UserState.waiting_for_edit_prompt)

@dp.message(UserState.waiting_for_edit_prompt)
async def handle_edit_prompt(message: Message, state: FSMContext):
    edit_prompt = message.text
    data = await state.get_data()
    image_url = data["image_url"]

    await message.answer("🖌️ Редактирую изображение...")

    headers = {
        "Authorization": f"Token {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "version": INPAINTING_MODEL,
        "input": {
            "image": image_url,
            "prompt": edit_prompt
        }
    }

    async with aiohttp.ClientSession() as session:
        async with session.post("https://api.replicate.com/v1/predictions", headers=headers, json=payload) as resp:
            if resp.status != 201:
                logger.error(f"Replicate inpainting error: {resp.status}")
                await message.answer("Ошибка при создании задачи редактирования изображения.")
                return

            prediction = await resp.json()
            prediction_id = prediction["id"]

            while True:
                await asyncio.sleep(2)
                status_url = f"https://api.replicate.com/v1/predictions/{prediction_id}"
                async with session.get(status_url, headers=headers) as status_resp:
                    status_data = await status_resp.json()
                    if status_data["status"] == "succeeded":
                        edited_image_url = status_data["output"]
                        await message.answer_photo(photo=edited_image_url)
                        break
                    elif status_data["status"] == "failed":
                        logger.error("Ошибка редактирования изображения")
                        await message.answer("Ошибка при редактировании изображения.")
                        break

    await state.clear()

# ========== Команда /start ==========
@dp.message(F.text | F.command)
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Привет! Выбери действие:", reply_markup=menu_keyboard).ClientSession