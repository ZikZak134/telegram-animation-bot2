import telebot
import replicate
import os
import google.generativeai as genai

# --- НАСТРОЙКА API (ключи будут добавлены в Render) ---
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
REPLICATE_API_TOKEN = os.environ.get('REPLICATE_API_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# Инициализация сервисов
bot = telebot.TeleBot(TELEGRAM_TOKEN)
os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-pro')

# --- ЛОГИКА БОТА ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Отправь мне фотографию, и я попробую её оживить. А мой друг Gemini придумает красивую подпись!")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        bot.reply_to(message, "Фото получил! Начинаю творить магию... ✨ Пожалуйста, подождите, это может занять несколько минут.")

        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        image_path = "temp_image.jpg"
        with open(image_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        with open(image_path, "rb") as file:
            animation_url = replicate.run(
                "stability-ai/stable-video-diffusion:3f0457e4619daac51203dedb472816fd4af51f3149fa7a9e0b5ffcf1b8172638",
                input={"image": file}
            )

        bot.send_message(message.chat.id, "Видео готово! Теперь прошу Gemini придумать красивую подпись...")
        prompt_for_gemini = "Ты — креативный ассистент. Придумай одну короткую, красивую и немного загадочную подпись для ожившей фотографии. Не используй кавычки."
        response = gemini_model.generate_content(prompt_for_gemini)
        caption_text = response.text

        bot.send_video(message.chat.id, animation_url, caption=caption_text)

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        bot.reply_to(message, "Ой, что-то пошло не так. Попробуйте отправить другое фото.")

# --- ЗАПУСК БОТА ---
print("Бот запущен...")
bot.polling()
