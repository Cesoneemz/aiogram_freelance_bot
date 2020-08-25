from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

btnSendRequest = KeyboardButton("Отправить запрос")
btnOurServices = KeyboardButton("Наши услуги")
btnAboutBot = KeyboardButton("О боте")
kbUserMain = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).add(btnSendRequest, btnOurServices, btnAboutBot)