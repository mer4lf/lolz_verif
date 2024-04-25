import math

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from database.AsyncDatabase import DataBase
from lexicon.lexicon import LEXICON_RU
from utils.utils import deals_per_page

DATABASE_URL = "postgresql+asyncpg://postgres:1111@localhost/lolz_books"

db = DataBase(DATABASE_URL)


# Функция для формирования инлайн-клавиатуры на лету
def create_inline_kb(width: int,
                     *args: str,
                     **kwargs: str) -> InlineKeyboardMarkup:
    # Инициализируем билдер
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    # Инициализируем список для кнопок
    buttons: list[InlineKeyboardButton] = []

    # Заполняем список кнопками из аргументов args и kwargs
    if args:
        for button in args:
            buttons.append(InlineKeyboardButton(
                text=LEXICON_RU[button] if button in LEXICON_RU else button,
                callback_data=button))
    if kwargs:
        for button, text in kwargs.items():
            buttons.append(InlineKeyboardButton(
                text=text,
                callback_data=button))
    # Распаковываем список с кнопками в билдер методом row c параметром width
    kb_builder.row(*buttons, width=width)

    # Возвращаем объект инлайн-клавиатуры
    return kb_builder.as_markup(resize_keyboard=True)


def create_reply_kb(width: int,
                    btn: list, ) -> ReplyKeyboardMarkup:
    # Инициализируем билдер
    kb_builder: ReplyKeyboardBuilder = ReplyKeyboardBuilder()
    # Инициализируем список для кнопок
    buttons: list[KeyboardButton] = []

    # Заполняем список кнопками из аргументов args и kwargs
    if btn:
        for button in btn:
            buttons.append(KeyboardButton(
                text=LEXICON_RU[button] if button in LEXICON_RU else button))
    # Распаковываем список с кнопками в билдер методом row c параметром width
    kb_builder.row(*buttons, width=width)

    # Возвращаем объект инлайн-клавиатуры
    return kb_builder.as_markup(resize_keyboard=True)


def create_inline_kb_dict(width: int,
                          dict) -> InlineKeyboardMarkup:
    # Инициализируем билдер
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    # Инициализируем список для кнопок
    buttons: list[InlineKeyboardButton] = []

    # Заполняем список кнопками из аргументов args и kwargs
    for button, text in dict.items():
        buttons.append(InlineKeyboardButton(
            text=text,
            callback_data=button))
    # Распаковываем список с кнопками в билдер методом row c параметром width
    kb_builder.row(*buttons, width=width)

    # Возвращаем объект инлайн-клавиатуры
    return kb_builder.as_markup(resize_keyboard=True)


def create_inline_kb_books(width: int, buttons_dict: dict, filters=None) -> InlineKeyboardMarkup:
    # Инициализируем билдер
    kb_builder = InlineKeyboardBuilder()

    # Создаем список кнопок из словаря
    buttons = [InlineKeyboardButton(text=text, callback_data=button) for button, text in buttons_dict.items()]

    # Если количество кнопок больше, чем ширина клавиатуры, распределяем кнопки с учетом последних двух
    if len(buttons) > width:
        for i in range(0, len(buttons) - 2, width):
            kb_builder.row(*buttons[i:i + width])
        kb_builder.row(*buttons[-2:])
    else:
        # Если кнопок меньше или равно ширине, добавляем их все в один ряд
        kb_builder.add(*buttons)

    # Возвращаем объект инлайн-клавиатуры
    return kb_builder.as_markup(resize_keyboard=True)


class StartKeyboards:
    start = create_inline_kb(1, accept="Принять")


class UserKeyboards:
    menu = create_reply_kb(2, ["Добавить книгу", "Найти книгу", "Список книг"])

    back_to_menu = create_inline_kb(1, back_to_menu="Назад")

    search_book = create_inline_kb(1, books_by_genre="По жанру", all_books="Все книги")

    back_to_books_list = create_inline_kb(1, back_to_books_list='назад к списку')

    async def genres(self):
        buttons = dict()
        sort_genres = set()
        genres = await db.get_genres()
        for i in genres:
            sort_genres.add(i.lower())
        for i in sort_genres:
            buttons[f'select_genre_{i}'] = i
        buttons['enter_new_genre'] = 'Ввести другой'
        return create_inline_kb_dict(3, buttons)

    async def check_book(self, book_id):
        buttons = dict()
        buttons[f'delete_book_{book_id}'] = 'Удалить'
        buttons[f'back_to_books_list'] = 'Назад'
        return create_inline_kb_dict(1, buttons)

    async def filtered_books(self, current_page, filtered_books):
        buttons = dict()

        total_pages = math.ceil(len(filtered_books) / deals_per_page)

        current_page = current_page % total_pages

        start_index = current_page * deals_per_page
        end_index = min(start_index + deals_per_page, len(filtered_books))
        for i in filtered_books[start_index:end_index]:
            buttons[
                f'book_id_{i.id}'] = f'{i.title} | {i.author}'
        buttons[f'books_page_prev'] = '<'
        buttons[f'books_page_next'] = '>'

        return create_inline_kb_books(1, buttons)
