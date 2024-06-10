from aiogram.fsm.state import StatesGroup, State


class States(StatesGroup):
    find_bug = State()
    find_user_username = State()
    find_user_id = State()
    support = State()
    check_prize = State()