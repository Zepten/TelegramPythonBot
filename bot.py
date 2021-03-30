from os import environ
from dotenv import load_dotenv
import telebot
import requests
import json
from time import sleep

# Загрузка переменных окружения
load_dotenv()

# Бот
bot = telebot.TeleBot(environ.get('TOKEN'))

# Словарь с настройками пользователей (вместо БД)
settings_dict = {}

# Обновление настроек пользователя
def update_settings(user_id: int):
	settings_dict.update({user_id: ['USD', False]})

def set_currency(user_id: int, currency: str):
	try:
		settings_dict[user_id][0] = currency
	except:
		update_settings(user_id)
		settings_dict[user_id][0] = currency

def get_currency(user_id: int):
	try:
		return settings_dict[user_id][0]
	except:
		update_settings(user_id)
		return settings_dict[user_id][0]

def toggle_newsletter(user_id: int):
	try:
		settings_dict[user_id][1] = not settings_dict[user_id][1]
	except:
		update_settings(user_id)
		settings_dict[user_id][1] = not settings_dict[user_id][1]

def get_newsletter(user_id: int):
	return settings_dict[user_id][1]

# Reply клавиатура
def get_reply_keyboard(user_id: int):
	reply_keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
	reply_keyboard.add(
		telebot.types.KeyboardButton('Курс Bitcoin 📈'),
		telebot.types.KeyboardButton('Выбрать валюту 💶'),
		telebot.types.KeyboardButton('Включить рассылку 🔔' if not get_newsletter(user_id) else 'Отключить рассылку 🔕'),
		telebot.types.KeyboardButton('Помощь 📎')
	)
	return reply_keyboard

# Получение данных с сайта
def get_bitcoin_data():
	return json.loads(requests.get(url='https://blockchain.info/ru/ticker').text)

# Start
@bot.message_handler(commands=['start'])
def welcome(message):
	bot.send_sticker(message.chat.id, open('stickers/anon.webp', 'rb'))
	update_settings(message.from_user.id)
	bot.send_message(
		message.chat.id,
		"Привет, я умею отслеживать курс Bitcoin!\nНапиши /help, чтобы узнать, что я могу",
		reply_markup=get_reply_keyboard(message.from_user.id)
	)

# Курс
@bot.message_handler(commands=['bitcoin'])
def bitcoin(message):
	data = get_bitcoin_data()
	cur = get_currency(message.from_user.id)
	bot.send_message(
		message.chat.id,
		f'Стоимость покупки Bitcoin: *{data[cur]["buy"]} {data[cur]["symbol"]}*'.replace('.', ','),
		parse_mode='MarkdownV2'
	)

# Выбор валюты
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

# Рассылка
@bot.message_handler(commands=['newsletter'])
def newsletter(message):
	toggle_newsletter(message.from_user.id)
	bot.send_message(
		message.chat.id,
		'Рассылка включена ✅' if get_newsletter(message.from_user.id) else 'Рассылка отключена ⛔️',
		reply_markup=get_reply_keyboard(message.from_user.id)
	)
	# TODO! Лучше сделать с помощью модуля schedule
	while get_newsletter(message.from_user.id):
		bitcoin(message)
		sleep(300) # Каждые 5 минут (300 секунд)

# Обработка нажатия на кнопки
@bot.message_handler(content_types=['text'])
def send_text(message):
	if message.text == 'Курс Bitcoin 📈':
		bitcoin(message)
	elif message.text == 'Выбрать валюту 💶':
		change_currency(message)
	elif message.text in ['Включить рассылку 🔔', 'Отключить рассылку 🔕']:
		newsletter(message)
	elif message.text == 'Помощь 📎':
		help(message)

# Помощь
@bot.message_handler(commands=['help'])
def help(message):
	bot.send_sticker(message.chat.id, open('stickers/help.webp', 'rb'))
	bot.send_message(
		message.chat.id,
		"""
		*Помощь*
		Каждой из нижеперечисленных команд \(кроме /start\) соответствует кнопка на панели кнопок\

		*Команды*
		/help \- Вызвать это меню 😳
		/start \- Вывести приветствие, а также сбросить валюту и рассылку
		/bitcoin \- Вывести курс Bitoin по выбранной валюте
		/currency \- Выбрать курс валюты \(по умолчанию USD\)
		/newsletter \- Включить/выключить рассылку \(каждые 5 минут будет приходить сообщение с текущим курсом Bitcoin по выбранной валюте\)
		""",
		parse_mode='MarkdownV2'
	)

# Выбор валюты из Inline-клавиатуры
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
	set_currency(call.from_user.id, call.data)
	bot.edit_message_text(
		chat_id=call.message.chat.id,
		message_id=call.message.message_id,
		text=f'Выбрана валюта *{get_currency(call.from_user.id)}*',
		reply_markup=None, parse_mode='MarkdownV2'
	)

# Поллинг
bot.polling(none_stop=True)
