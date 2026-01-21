import os
import logging
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
CHANNEL_ID = os.getenv("CHANNEL_ID")  # masalan: -1001234567890
BOT_USERNAME = os.getenv("BOT_USERNAME")  # masalan: @MyMovieBot
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # masalan: https://your-app.onrender.com/webhook

bot = Bot(token=TOKEN)
dp = Dispatcher()
app = FastAPI()

# Admin video yuboradi
@dp.message()
async def save_video(message: types.Message):
    if message.video and message.from_user.id == ADMIN_ID:
        if not message.caption:
            await message.answer("❗ Iltimos, captionda video ID yuboring (masalan: 1)")
            return
        video_id = message.caption.strip()
        await bot.send_video(
            chat_id=CHANNEL_ID,
            video=message.video.file_id,
            caption=f"VIDEO_ID:{video_id}"
        )
        await message.answer(f"✅ Video kanalga saqlandi (ID: {video_id})")

# Foydalanuvchi ID yuboradi
@dp.message()
async def get_video(message: types.Message):
    if message.text and message.text.isdigit():
        video_id = message.text.strip()
        async for msg in bot.get_chat_history(CHANNEL_ID, limit=1000):
            if msg.caption and msg.caption.startswith("VIDEO_ID:"):
                stored_id = msg.caption.split(":")[1]
                if stored_id == video_id:
                    await message.answer_video(
                        video=msg.video.file_id,
                        caption=f"KINO KODI : {video_id}\n{BOT_USERNAME}"
                    )
                    return
        await message.answer("❌ Bunday ID topilmadi.")

# Webhook endpoint
@app.post(WEBHOOK_PATH)
async def webhook(request: Request):
    data = await request.json()
    update = types.Update.model_validate(data)
    await dp.feed_update(bot, update)
    return {"status": "ok"}

@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(WEBHOOK_URL)

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()
