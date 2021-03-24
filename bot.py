import os
from dotenv import load_dotenv
import telebot
import bitcoin_parser


# Загрузка переменных окружения (токена)
load_dotenv()

# Бот
bot = telebot.TeleBot(os.environ.get("TOKEN"))

# /Start /Help
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.send_message(message.chat.id, "Привет, я умею отслеживать курс Биткоина!")

# /bitcoin
@bot.message_handler(commands=['bitcoin'])
def send_bitcoin_course(message):
	bot.send_message(message.chat.id, bitcoin_parser.bitcoin_course())

# Поллинг
bot.polling()
