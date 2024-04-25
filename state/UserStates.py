from aiogram.fsm.state import State, StatesGroup


class UserState(StatesGroup):
    accept_rules = State()
    create_book_1 = State()
    create_book_2 = State()
    create_book_3 = State()
    create_book_4 = State()
    search_book = State()
    search_book_genre = State()
