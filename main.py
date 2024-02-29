import os
import telebot
import logging
from dotenv import load_dotenv
from pytube import YouTube
from datetime import date

load_dotenv()

TOKEN = os.environ["TOKEN"]

bot = telebot.TeleBot(TOKEN, parse_mode=None)

logging.basicConfig(filename="info.log", level=logging.INFO)


def get_chat_id(message):
    return message.chat.id


@bot.message_handler(commands=["start"])
def handle_start_command(message):
    chat_id = get_chat_id(message)

    bot.send_message(
        chat_id,
        "Привіт! 👋\nНадішли посилання на пісню з YouTube або YouTube Music та я скачаю її для тебе.\n\n Я працюю дуже швидко та без реклами 🤝\n\n За наявності питань та/або проблем з ботом звертатись: @gnatuk2312",
    )


@bot.message_handler(commands=["help"])
def handle_help_command(message):
    chat_id = get_chat_id(message)

    bot.send_message(
        chat_id,
        "Щоб почати роботу зі мною надсилай посилання на YouTube або YouTube Music, який хочеш скачати.\n\nПриклад посилання: https://music.youtube.com/watch?v=CLjKo_XkxJI&list=RDAMVMCLjKo_XkxJI",
    )


@bot.message_handler(func=lambda m: True)
def echo_all(message):
    chat_id = get_chat_id(message)
    # send loading indicator and save in variable to delete later
    downloading_message = bot.send_message(chat_id, "Завантаження ⏳")

    try:
        # find and download audio from YouTube in mp3 format
        video = YouTube(message.text)
        stream = video.streams.filter(only_audio=True).first()
        filename = f"{video.title} - {video.author}.mp3"
        stream.download(filename=filename, output_path="./music")

        # read binary file
        filepath = f"./music/{filename}"
        # send audio
        bot.send_audio(
            chat_id, open(filepath, "rb"), title=video.title, performer=video.author
        )
        # delete audio
        os.remove(filepath)

        # log information
        log_text = f"{date.today()} - User: {message.chat.first_name} {message.chat.last_name} - Music: {video.title} - {video.author}"
        logging.info(log_text)
    except Exception as error:
        bot.send_message(
            chat_id,
            f"Не вдалось завантажити файл... 🤨\n\nМожливі причини:\n- Некоректне посилання \n- Відео захищено правами доступу від завантажень\n\nТекст помилки: {error}",
        )
    finally:
        # delete loading indicator
        bot.delete_message(chat_id, downloading_message.id)


bot.polling(non_stop=True, interval=0)
