from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

btnSetMaxRequestPerDay = KeyboardButton("Установить макс. количество запросов в день")
btnLoadCsv = KeyboardButton("Загрузить CSV-файл")
btnEditMessage = KeyboardButton("Редактировать текстовые сообщения")
btnUsersDatabase = KeyboardButton("Прислать csv-файл с пользователями")
kbAdminStart = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3).add(btnSetMaxRequestPerDay, btnLoadCsv,
                                                                          btnUsersDatabase, btnEditMessage)