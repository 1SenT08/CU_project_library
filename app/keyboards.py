from aiogram.types import (ReplyKeyboardMarkup,
                            KeyboardButton)


starts_keyboards_users_btns = [
    [KeyboardButton(text="Найти файл")],
    [KeyboardButton(text="Помощь")]
]
keyboards_users = ReplyKeyboardMarkup(keyboard=starts_keyboards_users_btns,
                                      resize_keyboard=True)


starts_keyboards_admins_btns = [
    [KeyboardButton(text="Найти файл")],
    [KeyboardButton(text="Помощь")],
    [KeyboardButton(text="Админ панель")]
]
keyboards_admins = ReplyKeyboardMarkup(keyboard=starts_keyboards_admins_btns,
                                 resize_keyboard=True)


panel_admins_btns = [
    [KeyboardButton(text="Добавить файл")],
    [KeyboardButton(text="Удалить файл")],
    [KeyboardButton(text="Добавить админа")],
    [KeyboardButton(text="Удалить админа")],
    [KeyboardButton(text="Назад")]
]

panel_admins = ReplyKeyboardMarkup(keyboard=panel_admins_btns,
                                   resize_keyboard=True)

panel_add_file_btns = [
     [KeyboardButton(text="Файл менее 20 МБ")],
     [KeyboardButton(text="Файл от 20 и более МБ")]
 ]

panel_add_file = ReplyKeyboardMarkup(keyboard=panel_add_file_btns,
                                     resize_keyboard=True)


button_cancel = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="cancel")]],
                                 resize_keyboard=True)






availability_photo = [
     [KeyboardButton(text="Да")],
     [KeyboardButton(text="Нет")]
 ]

availability_photo_inkb = ReplyKeyboardMarkup(keyboard=availability_photo,
                                     resize_keyboard=True)
