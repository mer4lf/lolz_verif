import asyncio

from aiogram import Dispatcher
from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message

from config_data.config import Config, load_config
from database.AsyncDatabase import DataBase

from keyboards.keyboard import UserKeyboards
from lexicon.lexicon import LEXICON_RU
from aiogram import F, Bot
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from state.UserStates import UserState
from utils.utils import is_card, MoneyWays, Ways, ProjectTypes, export_tags

DATABASE_URL = "postgresql+asyncpg://postgres:1111@localhost/lolz_books"

# Инициализируем роутер уровня модуля
router: Router = Router()
config: Config = load_config('.env')
db = DataBase(DATABASE_URL)
storage = MemoryStorage()
bot: Bot = Bot(token=config.tg_bot.token)
dp: Dispatcher = Dispatcher(storage=storage)
kb = UserKeyboards()


@router.message(Command('menu'))
async def menu_command(message: Message, state: FSMContext):
    if await db.user_exists(message.from_user.id):
        await state.set_state(UserState.default)
        await message.answer(LEXICON_RU['menu'], reply_markup=kb.menu, parse_mode="HTML")
    else:
        await message.answer(LEXICON_RU['no_access'])


@router.callback_query(F.data == "accept")
async def menu(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.answer()
    await state.set_state(UserState.default)
    await db.set_user(callback.from_user.id)
    await callback.message.edit_text(LEXICON_RU['menu'], reply_markup=kb.menu, parse_mode="HTML")


#   ---создание новой книги
@router.message(F.text == "Добавить книгу")
async def create_book(message: Message, state: FSMContext):
    await message.answer(LEXICON_RU['create_book'][0])
    await state.set_state(UserState.create_book_1)


@router.message(StateFilter(UserState.create_book_1))
async def book_title(message: Message, state: FSMContext):
    book_info = dict()
    book_info['title'] = message.text
    await message.answer(LEXICON_RU['create_book'][1])
    await state.set_state(UserState.create_book_2)
    await state.update_data(book_info=book_info)


@router.message(StateFilter(UserState.create_book_2))
async def book_author(message: Message, state: FSMContext):
    data = await state.get_data()
    book_info = data['book_info']
    book_info['author'] = message.text
    await message.answer(LEXICON_RU['create_book'][2], reply_markup=await kb.genres())
    await state.update_data(book_info=book_info)


@router.callback_query(StateFilter(UserState.create_book_2), F.data.startswith("select_genre"))
async def select_genre(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    book_info = data['book_info']
    book_info['genres'] = callback.data.split("_")[2]
    await callback.message.edit_text(LEXICON_RU['create_book'][3])
    await state.set_state(UserState.create_book_4)
    await state.update_data(book_info=book_info)


@router.callback_query(StateFilter(UserState.create_book_2), F.data.startswith("enter_new_genre"))
async def select_genre(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(LEXICON_RU['enter new genre'])
    await state.set_state(UserState.create_book_3)


@router.message(StateFilter(UserState.create_book_3))
async def book_genre(message: Message, state: FSMContext):
    data = await state.get_data()
    book_info = data['book_info']
    book_info['genres'] = message.text
    await message.answer(LEXICON_RU['create_book'][3])
    await state.set_state(UserState.create_book_4)
    await state.update_data(book_info=book_info)


@router.message(StateFilter(UserState.create_book_4))
async def book_description(message: Message, state: FSMContext):
    data = await state.get_data()
    book_info = data['book_info']
    book_info['description'] = message.text
    await state.clear()
    await message.answer(LEXICON_RU['create_book'][4])
    await db.create_new_book(message.from_user.id, book_info)


#   ---мои книги
@router.message(F.text == "Найти книгу")
async def search_book(message: Message, state: FSMContext):
    await message.answer(LEXICON_RU['search_book'])
    await state.set_state(UserState.search_book)


@router.message(StateFilter(UserState.search_book))
async def search_book_1(message: Message, state: FSMContext):
    filtered_books = await db.search_books(message.text)
    if filtered_books:
        await message.answer(LEXICON_RU['fitered_books'], reply_markup=await kb.filtered_books(0, filtered_books))
        await state.update_data(page=0, filter=message.text)
        await state.set_state()
    else:
        await message.answer(LEXICON_RU['no books'])
        await state.clear()


@router.callback_query((F.data.startswith("books_page") | F.data == "back_to_books_list"))
async def edit_page(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    if 'filter' in data.keys():
        if data['filter'].split(" ")[0] == "genre":
            filtered_books = await db.search_books_genre(data['filter'].split(" ")[1])
        else:
            filtered_books = await db.search_books(data['filter'])
    else:
        filtered_books = await db.get_all_books()
    if callback.data.split("_")[1] == "next":
        page = data['page'] + 1
    elif callback.data.split("_")[0] == "back":
        page = data['page']
    else:
        page = data['page'] - 1
    await callback.message.edit_text(LEXICON_RU['fitered_books'],
                                     reply_markup=await kb.filtered_books(page, filtered_books))
    await state.update_data(page=page)


@router.message(F.text == "Список книг")
async def search_book(message: Message, state: FSMContext):
    await message.answer(LEXICON_RU['list_book'], reply_markup=kb.search_book)


@router.callback_query(F.data == "all_books")
async def all_books(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    filtered_books = await db.get_all_books()
    if filtered_books:
        await callback.message.edit_text(LEXICON_RU['fitered_books'],
                                         reply_markup=await kb.filtered_books(0, filtered_books))
        await state.update_data(page=0)
    else:
        await callback.message.answer(LEXICON_RU['no all books'])


@router.callback_query(F.data == "books_by_genre")
async def all_books(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(LEXICON_RU['search book by genre'])
    await state.set_state(UserState.search_book_genre)


@router.message(UserState.search_book_genre)
async def all_books(message: Message, state: FSMContext):
    filtered_books = await db.search_books_genre(message.text)
    if filtered_books:
        await message.answer(LEXICON_RU['fitered_books'], reply_markup=await kb.filtered_books(0, filtered_books))
        await state.clear()
        await state.update_data(page=0, filter=f'genre {message.text}')
    else:
        await message.answer(LEXICON_RU['no books'])
        await state.clear()


@router.callback_query(F.data.startswith("book_id_"))
async def check_book(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    book_id = int(callback.data.split("_")[2])
    book_info = await db.get_book(book_id)
    await callback.message.edit_text(
        LEXICON_RU['check book description'].format(title=book_info.title, author=book_info.author,
                                                    description=book_info.description,
                                                    genre=book_info.genres),
        reply_markup=await kb.check_book(book_id), parse_mode="HTML")


@router.callback_query(F.data.startswith("delete"))
async def delete_book(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    book_id = int(callback.data.split("_")[2])
    await db.delete_book(book_id)
    await callback.message.edit_text(LEXICON_RU['delete book'], reply_markup=kb.back_to_books_list)