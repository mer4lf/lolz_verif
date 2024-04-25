from aiogram import Router
from aiogram.filters import StateFilter, CommandStart
from aiogram.types import Message

from config_data.config import Config, load_config

from database.AsyncDatabase import DataBase
from keyboards.keyboard import StartKeyboards
from lexicon.lexicon import LEXICON_RU
from aiogram import Bot
from aiogram.fsm.context import FSMContext
from state.UserStates import UserState

config: Config = load_config('.env')

DATABASE_URL = "postgresql+asyncpg://postgres:1111@localhost/lolz_books"
# Инициализируем роутер уровня модуля
router: Router = Router()
db = DataBase(DATABASE_URL)
bot: Bot = Bot(token=config.tg_bot.token)
kb = StartKeyboards()


@router.message(StateFilter(UserState.accept_rules))
@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    if not await db.user_exists(message.from_user.id):
        await state.set_state(UserState.accept_rules)
        await message.answer(LEXICON_RU['start'], reply_markup=kb.start)
    else:
        await message.answer(LEXICON_RU['help'])
        await state.clear()
