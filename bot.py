import os
from dotenv import load_dotenv
import telebot
import requests
import json

# Загрузка переменных окружения
load_dotenv()

# Бот
bot = telebot.TeleBot(os.environ.get('TOKEN'))

# Валюта (по умолчанию - USD)
currency = 'USD'

# Клавиатура
markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
markup.add(
	telebot.types.KeyboardButton('Курс Bitcoin 📈'),
	telebot.types.KeyboardButton('Выбрать валюту 💶'),
	telebot.types.KeyboardButton('Помощь 📎')
)

# /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
	bot.send_sticker(message.chat.id, open('stickers/anon.webp', 'rb'))
	bot.send_message(
		message.chat.id,
		"Привет, я умею отслеживать курс Bitcoin!\nНапиши /help, чтобы узнать, что я могу",
		reply_markup=markup
	)

@bot.message_handler(commands=['help'])
def send_help(message):
	bot.send_sticker(message.chat.id, open('stickers/help.webp', 'rb'))
	bot.send_message(
		message.chat.id, "Помощь\n"
	)

# Парсинг курса
def bitcoin_course():
    data = json.loads(requests.get(url='https://blockchain.info/ru/ticker').text)
    return f'Стоимость покупки Bitcoin в {currency}: {data[currency]["buy"]} {data[currency]["symbol"]}'

# Обработка нажатия на кнопки
@bot.message_handler(content_types=['text'])
def send_text(message):
	if message.text == 'Курс Bitcoin 📈':
		bot.send_message(message.chat.id, bitcoin_course())
	elif message.text == 'Выбрать валюту 💶':
		data = json.loads(requests.get(url='https://blockchain.info/ru/ticker').text)

		# Inline-кнопки выбора валюты
		currency_markup = telebot.types.InlineKeyboardMarkup(row_width=4)
		items = [telebot.types.InlineKeyboardButton(f'{c} ({data[c]["symbol"]})', callback_data=c) for c in data]
		currency_markup.add(*items)

		bot.send_sticker(message.chat.id, open('stickers/cur.webp', 'rb'))
		bot.send_message(
			message.chat.id,
			"Выбери нужную валюту из списка:",
			reply_markup=currency_markup
		)
	elif message.text == 'Помощь 📎':
		send_help(message)

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
	global currency
	currency = call.data
	bot.edit_message_text(
		chat_id=call.message.chat.id,
		message_id=call.message.message_id,
		text=f'Выбрана валюта {currency}',
		reply_markup=None
	)

# Поллинг
bot.polling(none_stop=True, timeout=0)
