from database.db_handler import select_all_user_prizes, all_user_prizes_num

from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder


PRIZES_PER_PAGE = 3
PRIZES_KB_WIDTH = 1


async def generate_prizes_keyboard(user_id, page_number, max_page_number):
    keyboard = InlineKeyboardBuilder()
    start_index = (page_number - 1) * PRIZES_PER_PAGE
    end_index = start_index + PRIZES_PER_PAGE
    page_buttons = []
    prizes_data = await select_all_user_prizes(user_id)
    if len(prizes_data) < 1:
        page_buttons.append(types.InlineKeyboardButton(text=f"🥲 Нету подарков", callback_data=f"no_prizes"))
    else:
        for prize_name, prize_id in prizes_data[start_index:end_index]:
            page_buttons.append(
                types.InlineKeyboardButton(text=f"🎁 {prize_name}", callback_data=f"open_prize_{prize_id}"))

    keyboard.row(width=PRIZES_KB_WIDTH, *page_buttons)
    switch_page_buttons = [types.InlineKeyboardButton(text="⬅️", callback_data=f"next_page_prizes_{page_number - 1}"), types.InlineKeyboardButton(text=f"{page_number}/{max_page_number}", callback_data="current_page"), types.InlineKeyboardButton(text="➡️", callback_data=f"prev_page_prizes_{page_number + 1}")]
    keyboard.row(width=3, *switch_page_buttons)
    keyboard.row(types.InlineKeyboardButton(text="🚀 В меню", callback_data='back_main_menu'), width=1)
    return keyboard.as_markup(resize_keyboard=True)


async def calculate_max_prizes_pages(user_id):
    prizes_count = await all_user_prizes_num(user_id)
    max_pages = 0

    if prizes_count == 0:
        return 1
    else:
        max_pages += (prizes_count + PRIZES_PER_PAGE - 1) // PRIZES_PER_PAGE
    return max_pages
