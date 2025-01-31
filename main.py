
import nest_asyncio
nest_asyncio.apply()



import os
import io
import logging
import PIL.Image
import nest_asyncio
import asyncio
from pyrogram.types import Message
import google.generativeai as genai
from pyrogram import Client, filters
from pyrogram.enums import ParseMode

# ✅ Apply Fix for Colab's async conflict
nest_asyncio.apply()

# ✅ Replace with your actual credentials
API_ID = "20686080"
API_HASH = "c28b20c7e8d8776e585c2afb44aeabee"
BOT_TOKEN = "8014992057:AAGn9gUOyxsulvMRJMpY7dfHCyUy3B4tyq0"
GOOGLE_API_KEY = "AIzaSyCSVTUUPZ5DQGCFxIzgObPASjwAAh0p3B0"  # 👈 Replace with your Gemini API Key
MODEL_NAME = "gemini-1.5-flash-latest"

# ✅ Pyrogram Bot Client (Use in-memory session by giving session name as a unique string)
app = Client(
    "gemini_session_in_memory",  # Unique session name for in-memory storage
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    parse_mode=ParseMode.MARKDOWN
)

# ✅ Configure Google Gemini AI
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel(MODEL_NAME)

# ✅ Command: /start
@app.on_message(filters.command("start"))
async def start_handler(client: Client, message: Message):
    welcome_message = (
        "Hello! 👋\n\n"
        "Welcome to **Infosphere** 🧠💬, your AI-powered chatbot.\n\n"
        "I'm here to assist you in generating content and understanding images using cutting-edge AI models. "
        "Simply type your request, or if you want to generate content, use /gem <prompt>! "
        "Feel free to reply to a photo to generate descriptions with /imgai. 😊\n\n"
        "Let me know how I can help you today!"
    )

    await message.reply_text(welcome_message)

# ✅ Command: /gem <your_prompt>
@app.on_message(filters.command("gem"))
async def gemi_handler(client: Client, message: Message):
    loading_message = None
    try:
        loading_message = await message.reply_text("**Generating response, please wait...**")

        if len(message.text.strip()) <= 5:
            await message.reply_text("**Provide a prompt after the command.**")
            return

        prompt = message.text.split(maxsplit=1)[1]
        response = model.generate_content(prompt)
        response_text = response.text if hasattr(response, 'text') else "⚠ No response received!"

        # ✅ Send response in chunks if too long
        if len(response_text) > 4000:
            parts = [response_text[i:i + 4000] for i in range(0, len(response_text), 4000)]
            for part in parts:
                await message.reply_text(part)
        else:
            await message.reply_text(response_text)

    except Exception as e:
        await message.reply_text(f"**An error occurred:** `{str(e)}`")
    finally:
        if loading_message:
            await loading_message.delete()

# ✅ Command: /imgai (Reply to an image)
@app.on_message(filters.command("imgai"))
async def generate_from_image(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.photo:
        await message.reply_text("**Please reply to a photo for a response.**")
        return

    prompt = message.command[1] if len(message.command) > 1 else message.reply_to_message.caption or "Describe this image."

    processing_message = await message.reply_text("**Generating response, please wait...**")

    try:
        # ✅ Download image in memory
        img_data = await client.download_media(message.reply_to_message, in_memory=True)
        img = PIL.Image.open(io.BytesIO(img_data.getbuffer()))

        # ✅ Get image-based AI response
        response = model.generate_content([prompt, img])
        response_text = response.text if hasattr(response, 'text') else "⚠ No response received!"

        await message.reply_text(response_text, parse_mode=None)

    except Exception as e:
        logging.error(f"Error during image analysis: {e}")
        await message.reply_text("**An error occurred. Please try again.**")
    finally:
        await processing_message.delete()

# ✅ Start Bot in Google Colab (Fixed!)
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(app.start())  # ✅ Fix for Google Colab
    print("Bot is running...")
    loop.run_forever()  # Keeps the bot running