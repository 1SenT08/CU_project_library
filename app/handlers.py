from aiogram import Bot
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.types.input_file import FSInputFile
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (Message, InlineQueryResultArticle,
                            InputTextMessageContent, InlineQuery,
                              InlineKeyboardMarkup, InlineKeyboardButton
)

from typing import Any, Dict
from config import BOT_TOKEN, URL_DISK, MAIN_ADMINS

import app.keyboards as kb
from app.yandex_disk import File_disk
from app.filter import filter_punctuation
from app.search_algorithm import func_searching_files_v2
from app.database.requests import (
    post_user, post_admin, delete_admin,
    get_admins, get_files_by_id, get_id_files, post_file_v2,
    delete_file_on_bd, amount_files
)

import pandas as pd
import sqlite3


router = Router()


class Add_admin(StatesGroup):
    name = State()
    tg_id = State()


class Add_file(StatesGroup):
    file_path = State()
    tg_id_file = State()

    name_file_on_disk = State()

    name_file = State()
    autor  = State()
    name_book = State()
    main_words = State()
    availability_photo = State()
    photo_words = State()


@router.message(F.text == '/start')
async def cmd_start(message: Message) -> None:
    await post_user(message.from_user.id)

    if message.from_user.id in await get_admins(): # Проблема - всегда True
        await message.answer(f'Здравствуйте. Ваш статус - админ.',
                             reply_markup=kb.keyboards_admins)
    
    else:
        await message.answer(f'Здравствуйте.',
                          reply_markup=kb.keyboards_users)


@router.message(F.text.casefold() == "cancel")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    if message.from_user.id in await get_admins():
        await message.answer(f"Действие отменено.",
                             reply_markup=kb.panel_admins)
    else:
        await message.answer(
            f"Действие отменено.",
            reply_markup=kb.keyboards_users
        )


@router.message(F.text == 'Админ панель')
async def txt_admin_panel(message: Message) -> None:
    if message.from_user.id in await get_admins():
        await message.answer(f'Вы открыли админ панель.',
                            reply_markup=kb.panel_admins)


@router.message(F.text == 'Удалить файл')
async def txt_delete_file(message: Message) -> None:
    if message.from_user.id in await get_admins():
        await message.answer(f"1) Для того, чтобы удалить файл нужно знать название документа.\n2) Чтобы удалить файл напишите следуюущее: «/d [название файла]»")


@router.message(F.text == 'Добавить файл')
async def txt_add_file(message: Message) -> None:
    if message.from_user.id in await get_admins():
        await message.answer(f'Выберите какой размер вашего файла:',
                             reply_markup=kb.panel_add_file)


@router.message(F.text == 'Файл менее 20 МБ')
async def txt_add_file(message: Message, state: FSMContext) -> None:
    if message.from_user.id in await get_admins():
        await state.set_state(Add_file.file_path)
        await state.update_data(file20=True)
        await state.update_data(is_search=False)

        await message.answer('Вы начинаете вводить информацию о новом файле\n'
                             'Если вы неправильно ввели данные, то нажмите на кнопку ниже\n'
                             'Отправьте файл',
                             reply_markup=kb.button_cancel)


@router.message(Add_file.file_path)
async def add_file_path(message: Message, state: FSMContext) -> None:
    try:
        tg_id_file = message.document.file_id
        File = await Bot(token=BOT_TOKEN).get_file(tg_id_file)

        if File.file_path.split('.')[-1] != 'pdf':
            raise AttributeError

        await state.update_data(file_path=File.file_path)
        await state.update_data(tg_id_file=tg_id_file)

        await state.set_state(Add_file.name_file)
        await message.answer('Введите имя файла\n',
                            reply_markup=kb.button_cancel)
    
    except AttributeError:
        await state.set_state(Add_file.file_path)
        await message.answer('Ошибка. Вам требуется отпраить файл в формате PDF!',
                             reply_markup=kb.button_cancel)
    except:
        await state.set_state(Add_file.file_path)
        await message.answer('Файл весит больше 20 МБ! Вернитесь и нажмите на кнопку: «20 МБ и более»',
                             reply_markup=kb.button_cancel)

 
@router.message(F.text == 'Файл от 20 и более МБ')
async def txt_add_file(message: Message, state: FSMContext) -> None:
    if message.from_user.id in await get_admins():
        await state.set_state(Add_file.name_file_on_disk)
        await state.update_data(is_search=False)
        await state.update_data(file20=False)

        await message.answer(f"Введите название документа, которое присвоено документу на Яндекс диске",
                             reply_markup=kb.button_cancel)


@router.message(Add_file.name_file_on_disk)
async def add_name_file(message: Message, state: FSMContext) -> None:
    if message.from_user.id in await get_admins():
        answer_message = message.text
        exam_disk = File_disk(URL_DISK, BOT_TOKEN)
        exam_file = await exam_disk.check_file(answer_message)
        exam_file_pdf = await exam_disk.check_file(f"{answer_message}.pdf")

        if exam_file or exam_file_pdf:
            await state.update_data(name_file_on_disk=answer_message)
            await state.update_data(name_file=answer_message)
            await message.answer('Введите ФИО автора\n',
                            reply_markup=kb.button_cancel)
            await state.set_state(Add_file.autor)

        else:
            await message.answer('Данного файла не существует на Яндекс диске,\n возможно, вы некорректно ввели название, попробуйте снова',
                                 reply_markup=kb.button_cancel)
            await state.set_state(Add_file.name_file_on_disk)


@router.message(F.text == 'Найти файл')
async def txt_find_file(message: Message, state: FSMContext) -> None:
    await state.set_state(Add_file.name_file)
    await state.update_data(is_search=True)

    await message.answer(f'Введите название файла, который вы ищите.')



@router.message(Add_file.name_file)
async def add_name_file(message: Message, state: FSMContext) -> None:
    await state.update_data(name_file=message.text.strip())

    await message.answer('Введите имя автора',
                        reply_markup=kb.button_cancel)
    await state.set_state(Add_file.autor)


@router.message(Add_file.autor)
async def add_autor(message: Message, state: FSMContext) -> None:
    await state.update_data(autor=message.text.strip())
    await message.answer('Введите название книги\n',
                        reply_markup=kb.button_cancel)
    await state.set_state(Add_file.name_book)


@router.message(Add_file.name_book)
async def add_name_book(message: Message, state: FSMContext) -> None:
    await state.update_data(name_book=message.text.strip())
    await message.answer('Введите ключевые слова, которые характерезуют документ.\nСлова должные писаться через ЗНАК «_»',
                        reply_markup=kb.button_cancel)
    await state.set_state(Add_file.main_words)


@router.message(Add_file.main_words)
async def add_main_words(message: Message, state: FSMContext) -> None:
    answer_message = message.text
    flag_punctuation = filter_punctuation(answer_message)

    if flag_punctuation:
        await state.update_data(main_words=answer_message.strip())
        await message.answer('Отметьте наличие фотографий в вашем файле/книге \n',
                            reply_markup=kb.availability_photo_inkb)
        await state.set_state(Add_file.availability_photo)

    else:
        await message.answer('Некорректо введены ключевые слова. Поробуйте снова\n',
                            reply_markup=kb.button_cancel)
        await state.set_state(Add_file.main_words)


@router.message(Add_file.availability_photo)
async def add_availability_photo(message: Message, state: FSMContext) -> None:
    answer_message = message.text
    await state.update_data(availability_photo=answer_message)

    if answer_message.lower() == "да":
        await message.answer('Введите ключевые слова, которые описывают, кто находится на фото документа/книги.\nСлова должные писаться через ЗНАК «_»',
                            reply_markup=kb.button_cancel)
        await state.set_state(Add_file.photo_words)

    else:
        data = await state.update_data(photo_words="AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
        await state.clear()
        await show_summary_file_v2(message=message, data=data)


@router.message(Add_file.photo_words)
async def add_photo_words(message: Message, state: FSMContext) -> None:
    answer_message = message.text
    flag_punctuation = filter_punctuation(answer_message)

    if flag_punctuation:
        data = await state.update_data(photo_words=answer_message.strip())
        await state.clear()
        await show_summary_file_v2(message=message, data=data)

    else:
        await message.answer('Некорректо введены ключевые слова. Поробуйте снова\n',
                            reply_markup=kb.button_cancel)
        await state.set_state(Add_file.photo_words)



async def show_summary_file_v2(message: Message, data: Dict[str, Any], positive: bool = True) -> None:
    autor = '_'.join(data['autor'].strip().lower().split())
    name_book = '_'.join(data['name_book'].strip().lower().split())
    main_words = data['main_words'].strip().lower()
    availability_photo = data['availability_photo']
    photo_words = '_'.join(data['photo_words'].strip().lower().split())


    if not data['is_search']:

        # Только для файлов < 20 мб
        if not data['is_search'] and data['file20']:
            name_file = '_'.join(data['name_file'].strip().lower().split())
            file_path = data['file_path']
            tg_id_file = data['tg_id_file']
            name_file_on_disk = "-"
        # Только для файлов от 20 до 50 мб
        elif not data['is_search'] and not data['file20']:
            name_file = data['name_file']
            name_file_on_disk = data['name_file_on_disk']
            file_path = "-"
            tg_id_file = "-"

        flag_db = await post_file_v2(file_path, tg_id_file, name_file_on_disk, name_file,
                       autor, name_book, main_words, availability_photo,
                       photo_words)

        if flag_db and data['file20']:
            print("Файл размером < 20 МБ начал размещаться на яндекс диске")

            post_disk = File_disk(URL_DISK, BOT_TOKEN)
            flag_disk = await post_disk.post_file(name_file, file_path)

            print(f"Статус размещения: {flag_disk[0]}")

            if flag_disk[0]:
                await message.answer(f"Файл был успешно добавлен.",
                            reply_markup=kb.panel_admins)
            else:

                delete = await delete_file_on_bd(name_file)
                if delete:
                    await message.answer(f"Ошибка: \n {flag_disk[1]}\nФайл удалось убрать из БД",
                                reply_markup=kb.panel_admins)
                else:
                    await message.answer(f"Ошибка: \n {flag_disk[1]}\nФайл НЕ удалось убрать из БД",
                                reply_markup=kb.panel_admins)

        elif flag_db:
            await message.answer(f"Файл успешно получил хэш-тэги.",
                            reply_markup=kb.panel_admins)

        else:
            await message.answer(f"Ошибка:",
                            reply_markup=kb.panel_admins)

    else:
        name_file = '_'.join(data['name_file'].strip().lower().split())

        searched_files_id = await func_searching_files_v2(data)
        answer = (f"1) Название документа: {data['name_file']}\n"
                  f"2) Автор: {data["autor"]}\n"
                  f"3) Название книги: {data['name_book']}\n"
                  f"4) Ключевые слова: {data['main_words']}\n"
                  f"5) Наличие фотографий: {data['availability_photo']}\n"
                  f"6) Ключевые слова фото: {data['photo_words']}\n")

        if searched_files_id[1]:
            search_file_inline = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Найти", switch_inline_query_current_chat=".".join(searched_files_id[0]))],
                ])
            await message.answer(f"Ваш запрос сформирован. \n{answer}\n{'.'.join(searched_files_id[0])}",
                                 reply_markup=search_file_inline)
        else:
            await message.answer(f"Файлов по вашему запросу не найдено \n{answer}",
                                 reply_markup=kb.panel_admins)


@router.inline_query(F.query)
async def show_needed_files(query: InlineQuery) -> None:
    all_id = await get_id_files()
    needed_files_id = [int(id) for id in query.query.split('.') if int(id) in all_id]
    files = await get_files_by_id(needed_files_id)
    all_files = []
    get_disk = File_disk(URL_DISK, BOT_TOKEN)

    for index, file in enumerate(files):
        url_file = await get_disk.get_url_file(f'{file["name_file"]}.pdf')
        all_files.append(InlineQueryResultArticle(
            id=str(index),
            title=file["name_file"],
            description=file["autor"],
            input_message_content=InputTextMessageContent(
                message_text=url_file,
                parse_mode="HTML"
            )
        ))


    await query.answer(all_files, cache_time=3, is_personal=True)


@router.message(F.text == 'Добавить админа')
async def txt_add(message: Message, state: FSMContext) -> None:
    if message.from_user.id in MAIN_ADMINS:
        await state.set_state(Add_admin.name)
        await message.answer('Вы начинаете вводить инфоромацию о новой админе\nЕсли вы неправильно ввели данные, то нажмите на кнопку ниже\nВведите имя админа',
                            reply_markup=kb.button_cancel)
    else:
        await message.answer(f'У вас недостаточно прав.')


@router.message(Add_admin.name)
async def add_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(Add_admin.tg_id)
    await message.answer('Введите Телеграмм id админа\n',
                         reply_markup=kb.button_cancel)


@router.message(Add_admin.tg_id)
async def add_tg_id(message: Message, state: FSMContext) -> None:
    data = await state.update_data(tg_id=message.text)
    await state.clear()
    await show_summary_admin(message=message, data=data)


async def show_summary_admin(message: Message, data: Dict[str, Any], positive: bool = True) -> None:
    name = data["name"]
    tg_id = data["tg_id"]
    flag = await post_admin(tg_id, name)
    if flag:
        await message.answer(f"Админ был успешно добавлен.",
                            reply_markup=kb.panel_admins)
    else:
        await message.answer(f"Вы ввели некорректный telegram id.",
                            reply_markup=kb.panel_admins)


@router.message(F.text == 'Удалить админа')
async def txt_delete_admin(message: Message) -> None:
    if message.from_user.id in MAIN_ADMINS:
        await message.answer(f'''
                             1) Чтобы удалить админа скопируйте данный текст - `/delete `.\n2) Теперь вставьте его в поле для ввода и напишите telegram id человека, чьи права вы хотите забрать\n3) Это должно выглядит так: «/delete [telegram id]»
                             ''',
                             reply_markup=kb.panel_admins, parse_mode="MARKDOWN")
    else:
        await message.answer(f'У вас недостаточно прав.')


@router.message(F.text.startswith('/delete '))
async def cmd_delete_admin(message: Message) -> None:
    if message.from_user.id in await get_admins():
        list_text = message.text.split()

        if len(list_text) == 2 and list_text[1].strip().isdigit():
            tg_id_admin = list_text[1].strip()

            if await delete_admin(int(tg_id_admin)):
                await message.answer(f'Админ был успешно удален.',
                                    reply_markup=kb.panel_admins)
            else:
                await message.answer(f'Админа с таким id не существует.')


        else:
            await message.answer(f'Вы некорректно использывали команду.')


@router.message(F.text == 'Назад')
async def txt_back(message: Message) -> None:
    if message.from_user.id in await get_admins():
        await message.answer(f'Вы вернулись в меню.',
                            reply_markup=kb.keyboards_admins)


@router.message(F.text == '/id')
async def cmd_id(message: Message) -> None:
    await message.answer(f"{message.from_user.id}")


@router.message(F.text.startswith('/d '))
async def cmd_test(message: Message) -> None:
    if message.from_user.id in await get_admins():
        message_text = message.text
        list_text = message_text.split()

        if len(list_text) >= 2:
            name_file = message_text[3:]
    
            if ".pdf" in name_file:
                name_file = name_file[:-4]

            delet = await delete_file_on_bd(name_file)
            if delet:
                disk = File_disk(URL_DISK, BOT_TOKEN)
                delete_file_on_disk = await disk.delete_file(f"{name_file}.pdf")
                
                if delete_file_on_disk:
                    await message.answer(f"Файл был успешно удален.",
                                        reply_markup=kb.panel_admins)
                else:
                    await message.answer(f"Такого файла не существует на Яндекс диске. Данные о файле(хэш-тэги) стерты с БД",
                                    reply_markup=kb.panel_admins)
            else:
                await message.answer(f"Неправильно введено название файла",
                                    reply_markup=kb.panel_admins)
    
    else:
        await message.answer(f'У вас недостаточно прав.')


@router.message(F.text == 'таблица')
async def txt_data_files(message: Message) -> None:
    if message.from_user.id in await get_admins():
        conn = sqlite3.connect('db.sqlite3')
        df = pd.read_sql('select * from file_library_kgu', conn)
        df.to_excel('result.xlsx', index=False)
        file_exel = FSInputFile(path="result.xlsx")

        await message.answer_document(file_exel, caption="Таблица с файлами")


@router.message(F.text == "/help")
async def txt_help(message: Message) -> None:
    if message.from_user.id in await get_admins():
        await message.answer(
"""
Рекомендации пользования Телеграм ботом для админов\n
При вводе информации о файле НЕЛЬЗЯ:\n
-  Пользоваться знаками препинания.\n
НЕправильно: «трилогия книг: книга1, книга2.»\n
ПРАВИЛЬНО: «трилогия книг книга1 книга2»\n
 
- Писать сокращенно инициалы.\n
НЕправильно: «А С Пушкину»\n
ПРАВИЛЬНО: «Пушкин» или «Александр Сергеевич Пушкин»\n
 
При заполнении разделов: «Ключевые слова» и «Ключевые слова фото» ЖЕЛАТЕЛЬНО писать слова хотя бы в 2 формах слова\n
НЕжелательно: «калмыкия»\n
ЖЕЛАТЕЛЬНО: «калмык_калмыцкий_калмыкия»\n
 
При заполнении разделов: «Ключевые слова» и «Ключевые слова фото» ЖЕЛАТЕЛЬНО писать слово как в ед числе, так и во мн.\n
НЕжелательно: «калмык»\n
ЖЕЛАТЕЛЬНО: «калмык_калмыки»\n
 
Для того чтобы получить EXEL таблицу следует написать в личку бота: «таблица». Бот отправит вам таблицу файлов и их «хэш-тэгов», которые хранятся на данный момент в базе данных и на Яндекс диске\n
 
Для того чтобы удалить/добавит файл/админа нажмите на соответствующие кнопки и следуйте нструкции.
""")


@router.message(F.text)
async def answer(message: Message):
    await message.answer(f"Я вас не понимаю.")

