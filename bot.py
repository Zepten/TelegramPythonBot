import os
from dotenv import load_dotenv
import telebot
import requests
import json
import time

# Загрузка переменных окружения
load_dotenv()

# Бот
bot = telebot.TeleBot(os.environ.get('TOKEN'))

# Словарь с настройками пользователей (вместо БД)
settings_dict = {}

def open_settings_file():
	try:
		with open('settings.json', 'r') as file:
			global settings_dict
			settings_dict = json.load(file)
			print('Settings opened:')
			print(settings_dict)
	except:
		update_settings_file()

def update_settings_file():
	with open('settings.json', 'w+') as file:
		file.write(json.dumps(settings_dict))
		print('Settings updated:')
		print(settings_dict)

open_settings_file()

# Клавиатура
markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
markup.add(
	telebot.types.KeyboardButton('Курс Bitcoin 📈'),
	telebot.types.KeyboardButton('Выбрать валюту 💶'),
	telebot.types.KeyboardButton('Помощь 📎')
)

# Получение данных с сайта
def get_bitcoin_data():
	data = json.loads(requests.get(url='https://blockchain.info/ru/ticker').text)
	return data

@bot.message_handler(commands=['start'])
def welcome(message):
	bot.send_sticker(message.chat.id, open('stickers/anon.webp', 'rb'))
	bot.send_message(
		message.chat.id,
		"Привет, я умею отслеживать курс Bitcoin!\nНапиши /help, чтобы узнать, что я могу",
		reply_markup=markup
	)
	settings_dict.update({str(message.from_user.id): {'cur': 'USD', 'news': 0}})
	update_settings_file()
	print(settings_dict)

@bot.message_handler(commands=['bitcoin'])
def bitcoin(message):
	data = get_bitcoin_data()
	cur = settings_dict[str(message.from_user.id)]['cur']
	bot.send_message(
		message.chat.id,
		f'Стоимость покупки Bitcoin в {cur}: {data[cur]["buy"]} {data[cur]["symbol"]}'
	)

@bot.message_handler(commands=['currency'])
def change_currency(message):
	# Inline-кнопки выбора валюты
	currency_markup = telebot.types.InlineKeyboardMarkup(row_width=4)
	data = get_bitcoin_data()
	items = [telebot.types.InlineKeyboardButton(f'{c} ({data[c]["symbol"]})', callback_data=c) for c in data]
	currency_markup.add(*items)

	bot.send_sticker(message.chat.id, open('stickers/cur.webp', 'rb'))
	bot.send_message(
		message.chat.id,
		"Выбери нужную валюту из списка:",
		reply_markup=currency_markup
	)

@bot.message_handler(commands=['help'])
def help(message):
	bot.send_sticker(message.chat.id, open('stickers/help.webp', 'rb'))
	bot.send_message(
		message.chat.id, "Помощь\n"
	)

# Обработка нажатия на кнопки
@bot.message_handler(content_types=['text'])
def send_text(message):
	if message.text == 'Курс Bitcoin 📈':
		bitcoin(message)
	elif message.text == 'Выбрать валюту 💶':
		change_currency(message)
	elif message.text == 'Помощь 📎':
		help(message)

# Выбор валюты из Inline-клавиатуры
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
	settings_dict[str(call.from_user.id)]['cur'] = call.data
	print(call.data)
	bot.edit_message_text(
		chat_id=call.message.chat.id,
		message_id=call.message.message_id,
		text=f'Выбрана валюта {settings_dict[str(call.from_user.id)]["cur"]}',
		reply_markup=None
	)

	print(settings_dict)
	update_settings_file()

# Поллинг
bot.polling(none_stop=True)
