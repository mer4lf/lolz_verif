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

# TODO: допистаь удаление и добавить кнопку назад к списку

# @router.callback_query(F.data.startswith("edit_ad"))
# async def edit_ad_price(callback: CallbackQuery, state: FSMContext):
#     await callback.answer()
#     if callback.data != "edit_ad_delete":
#         await callback.message.edit_text(LEXICON_RU[callback.data])
#         await state.set_state(UserState.edit_ad)
#         await state.update_data(edit_type=callback.data[8:])
#     else:
#         data = await state.get_data()
#         await db.delete_ad(data['ad_num'])
#         await callback.message.edit_text(LEXICON_RU[callback.data])

# #   ---Рекламная компания
# @router.callback_query(StateFilter(UserState.default),
#                        F.data.in_(["advertising_campaign", "back_to_adv_companies_list"]))
# async def adv_company(callback: CallbackQuery, state: FSMContext):
#     await callback.answer()
#     adv_companies = await db.get_adv_companies(callback.from_user.id)
#     if callback.data == "advertising_campaign":
#         await callback.message.edit_text(LEXICON_RU['adv_company'],
#                                          reply_markup=await kb.adv_company(adv_companies))
#     else:
#         await callback.message.answer(LEXICON_RU['adv_company'],
#                                       reply_markup=await kb.adv_company(adv_companies))
#
#
# @router.callback_query(StateFilter(UserState.default), F.data == "new_adv_company")
# async def new_adv_company(callback: CallbackQuery, state: FSMContext):
#     await callback.answer()
#     await callback.message.edit_text(LEXICON_RU['new_adv_company'][0])
#     await state.set_state(UserState.new_adv_company)
#
#
# @router.message(StateFilter(UserState.new_adv_company))
# async def new_adv_company_title(message: Message, state: FSMContext):
#     await message.answer(LEXICON_RU['new_adv_company'][1])
#     adv_company_info = {
#         'title': message.text
#     }
#     await state.update_data(adv_company_info=adv_company_info)
#     await state.set_state(UserState.new_adv_company_post)
#
#
# @router.message(StateFilter(UserState.new_adv_company_post))
# async def save_new_adv_company(message: Message, state: FSMContext):
#     data = await state.get_data()
#     adv_company_info = data['adv_company_info']
#     adv_company_info['message_id'] = message.message_id
#     await db.new_adv_company(message.from_user.id, adv_company_info)
#     mes = await message.answer(LEXICON_RU['new_adv_company_done'])
#     await asyncio.sleep(1.5)
#     adv_companies = await db.get_adv_companies(message.from_user.id)
#     await mes.edit_text(LEXICON_RU['adv_company'], reply_markup=await kb.adv_company(adv_companies))
#     await state.set_state(UserState.default)
#
#
# @router.callback_query(StateFilter(UserState.default), F.data.startswith("adv_company"))
# async def check_adv_company(callback: CallbackQuery, state: FSMContext):
#     await callback.answer()
#     adv_company_id = int(callback.data[len("adv_company_"):])
#     adv_company_info = await db.get_adv_company(adv_company_id)
#     await state.update_data(adv_company_id=adv_company_id)
#     await bot.copy_message(callback.from_user.id, callback.from_user.id, adv_company_info.message_id,
#                            reply_markup=kb.back_to_adv_companies_list)
#
#
# @router.callback_query(StateFilter(UserState.default), F.data == "delete_adv_company")
# async def delete_adv_company(callback: CallbackQuery, state: FSMContext):
#     await callback.answer()
#     data = await state.get_data()
#     adv_company_id = data['adv_company_id']
#     await db.delete_adv_company(adv_company_id)
#     mes = await callback.message.answer(LEXICON_RU['delete_adv_company'])
#     await asyncio.sleep(1.5)
#     adv_companies = await db.get_adv_companies(callback.from_user.id)
#     await mes.edit_text(LEXICON_RU['adv_company'], reply_markup=await kb.adv_company(adv_companies))
#
#
# @router.message(StateFilter(UserState.default), F.text == "Купить рекламу")
# async def buy_ads(message: Message, state: FSMContext):
#     page = 0
#     await message.answer(LEXICON_RU['buy_ads'], reply_markup=await kb.buy_ads(page))
#     await state.update_data(page=page, data_filter={}, ads_filter=[])
#
#
# @router.callback_query(StateFilter(UserState.default),
#                        (F.data.startswith("buy_ads_page") | F.data == "back_to_ads_list"))
# async def next_page_buy_ads(callback: CallbackQuery, state: FSMContext):
#     data = await state.get_data()
#     if callback.data == "back_to_ads_list":
#         page = data['page']
#     else:
#         if callback.data.split("_")[3] == "next":
#             page = data['page'] + 1
#         else:
#             page = data['page'] - 1
#     await callback.message.edit_text(LEXICON_RU['buy_ads'], reply_markup=await kb.buy_ads(page))
#     await state.update_data(page=page)
#
#
# @router.callback_query(StateFilter(UserState.default), F.data.startswith("filter_button"))
# async def add_filters(callback: CallbackQuery, state: FSMContext):
#     data = await state.get_data()
#     await state.update_data(filter_button=callback.data[len("filter_button_"):])
#     if data['ads_filter']:
#         await callback.message.edit_reply_markup(
#             reply_markup=await kb.buy_ads(data['page'], callback.data[len("filter_button_"):],
#                                           ads_filter=data['ads_filter']))
#     else:
#         await callback.message.edit_reply_markup(
#             reply_markup=await kb.buy_ads(data['page'], callback.data[len("filter_button_"):]))
#
#
# @router.callback_query(StateFilter(UserState), F.data.startswith("filter_"))
# async def filters(callback: CallbackQuery, state: FSMContext):
#     data = await state.get_data()
#     ads_filter = data['ads_filter']
#     data_filter = data['data_filter']
#     if callback.data.split("_")[1] in ["type", "tags", "reputation"]:
#         await state.update_data(filter_now=callback.data.split("_")[1])
#         if callback.data not in ads_filter:
#             ads_filter.append(callback.data)
#         else:
#             ads_filter.remove(callback.data)
#         await callback.message.edit_reply_markup(
#             reply_markup=await kb.buy_ads(data['page'], data["filter_button"], ads_filter=ads_filter))
#     elif callback.data.split("_")[1] == "done":
#         filters = data['filter_now']
#         data_filters = export_tags(callback.message.reply_markup.inline_keyboard)
#         data_filter[filters] = data_filters.split(", ")
#         await state.update_data(data_filter=data_filter)
#         await callback.message.edit_reply_markup(
#             reply_markup=await kb.buy_ads(data['page'], data_filter=data_filter))
#     elif callback.data.split("_")[1] == "clear":
#         await callback.message.edit_text(LEXICON_RU['buy_ads'], reply_markup=await kb.buy_ads(data['page']))
#         await state.update_data(data_filter={}, ads_filter=[])
#
#
# @router.callback_query(StateFilter(UserState.default), F.data.startswith("ad_id_"))
# async def check_ad_description(callback: CallbackQuery, state: FSMContext):
#     data = await state.get_data()
#     ad_info = await db.get_ad(int(callback.data[len("ad_id_"):]))
#     await callback.message.edit_text(
#         LEXICON_RU['check_ad_description'].format(title=ad_info.title, number_of_users=ad_info.number_of_users,
#                                                   price=ad_info.price,
#                                                   reputation=LEXICON_RU["reputation"][ad_info.reputation]),
#         reply_markup=await kb.check_ad_description(int(callback.data[len("ad_id_"):])), parse_mode="HTML")
#
#
# @router.callback_query(StateFilter(UserState.default),
#                        (F.data.startswith("order_ad") | F.data.startswith("back_order_")))
# async def order_ad(callback: CallbackQuery, state: FSMContext):
#     await state.update_data(order_id=callback.data.split("_")[2])
#     adv_companies = await db.get_adv_companies(callback.from_user.id)
#     await callback.message.edit_text(LEXICON_RU['order_ad'],
#                                      reply_markup=await kb.order_ad(adv_companies))
#
#
# # TODO: сделать так, чтобы order_id тоже передавался дальше, проверить работу системы
#
# @router.callback_query(StateFilter(UserState.default), F.data.startswith("send_adv_company"))
# async def send_adv_company(callback: CallbackQuery, state: FSMContext):
#     await callback.answer()
#     data = await state.get_data()
#     adv_company_id = int(callback.data.split("_")[3])
#     adv_company_info = await db.get_adv_company(adv_company_id)
#     await bot.copy_message(callback.from_user.id, callback.from_user.id, adv_company_info.message_id,
#                            reply_markup=await kb.accept_sending_adv_company(adv_company_id, data['order_id']))
#
#
# @router.callback_query(StateFilter(UserState.default), F.data.startswith("purchase_done_"))
# async def order_ad(callback: CallbackQuery, state: FSMContext):
#     ad_id = int(callback.data.split("_")[3])
#     user = await db.get_user(callback.from_user.id)
#     ad = await db.get_ad(ad_id)
#     if user.balance < ad.price:
#         await callback.message.answer(LEXICON_RU['not enough balance'],
#                                       reply_markup=await kb.not_enough_balance(ad_id))
#     else:
#         adv_company_id = int(callback.data.split("_")[2])
#         adv_company_info = await db.get_adv_company(adv_company_id)
#         await db.new_purchase(ad_id, ad.user_id, callback.from_user.id, adv_company_id)
#         await db.edit_balance(ad.user_id, "topup_u", ad.price)
#         await db.edit_balance(callback.from_user.id, "withdraw", ad.price)
#         await callback.message.answer(LEXICON_RU['success purchase'])
#         await bot.send_message(ad.user_id, LEXICON_RU['new_deal'])
#
#
# @router.callback_query(StateFilter(UserState.default), F.data.in_(["my_purchases", "my_sales"]))
# async def my_purchases(callback: CallbackQuery, state: FSMContext):
#     page = 0
#     await callback.message.edit_text(LEXICON_RU[f'my {callback.data.split("_")[1]}'],
#                                      reply_markup=await kb.my_operations(page, callback.from_user.id,
#                                                                          f'{callback.data.split("_")[1]}'))
#     await state.update_data(page=page)
#
#
# @router.callback_query(StateFilter(UserState.default),
#                        (F.data.startswith("purchases_page") | F.data.startswith("sales_page")))
# async def purchases_page(callback: CallbackQuery, state: FSMContext):
#     data = await state.get_data()
#     if callback.data.split("_")[2] == "next":
#         page = data['page'] + 1
#     else:
#         page = data['page'] - 1
#     await callback.message.edit_text(LEXICON_RU[f'my {callback.data.split("_")[2]}'],
#                                      reply_markup=await kb.my_operations(page, callback.from_user.id,
#                                                                          f'{callback.data.split("_")[1]}'))
#     await state.update_data(page=page)
#
#
# @router.callback_query(StateFilter(UserState.default),
#                        (F.data.startswith("purchases_id_") | F.data.startswith("sales_id_")))
# async def check_operation(callback: CallbackQuery, state: FSMContext):
#     data = await state.get_data()
#     operation_info = await db.get_purchase(int(callback.data.split("_")[2]))
#     await callback.message.edit_text(
#         LEXICON_RU['check operation description'].format(id=operation_info.id, seller_id=operation_info.seller_id,
#                                                          state=LEXICON_RU["deal state"][operation_info.state]),
#         reply_markup=await kb.check_ad_description(int(callback.data.split("_")[2])), parse_mode="HTML")
#
#
