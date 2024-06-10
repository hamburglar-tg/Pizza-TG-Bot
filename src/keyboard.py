from database.db_handler import get_user_ban
from scripts.config import (
    admins,
    channel_kb_name,
    channel_full_url,
    menu_web_app_url
)

from aiogram.types import InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

def channels_kb():
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text=channel_kb_name, url=channel_full_url), width=1)
    markup.row(InlineKeyboardButton(text="Проверить", callback_data="check_channel"), width=1)
    return markup.as_markup(resize_keyboard=True)


def main_menu_kb(user_id):
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text="👤 Профиль", callback_data="user_profile"), InlineKeyboardButton(text="🔮 Информация", callback_data="info"), width=2)
    markup.row(InlineKeyboardButton(text="📤 Реферальная программа", callback_data="referral_program"), width=1)
    markup.row(InlineKeyboardButton(text="🍴 Меню", web_app=WebAppInfo(url=menu_web_app_url)), InlineKeyboardButton(text="🎁 Подарки", callback_data="prizes"), width=2)
    if user_id in admins:
        markup.row(InlineKeyboardButton(text="🧑‍💻 Админ панель", callback_data="admin_panel"), width=1)
    return markup.as_markup(resize_keyboard=True)


def profile_kb():
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text="⚠️ Нашел проблему", callback_data="find_bug"), width=1)
    markup.row(InlineKeyboardButton(text="🚀 В меню", callback_data="back_main_menu"), width=1)
    return markup.as_markup(resize_keyboard=True)


def close_kb():
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text="❌ Закрыть", callback_data="delete_message"), width=1)
    return markup.as_markup(resize_keyboard=True)


def info_kb():
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text="🌐 Получить геолокацию", callback_data="get_geolocation"), width=1)
    markup.row(InlineKeyboardButton(text="🚀 В меню", callback_data="back_main_menu"), width=1)
    return markup.as_markup(resize_keyboard=True)


def back_menu_kb():
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text="🚀 В меню", callback_data="back_main_menu"), width=1)
    return markup.as_markup(resize_keyboard=True)


def admin_kb():
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text="🔍 Поиск пользователя", callback_data="find_user"), width=1)
    markup.row(InlineKeyboardButton(text="🔍 Проверить ID приза", callback_data="check_prize_id"), width=1)
    markup.row(InlineKeyboardButton(text="🚀 В меню", callback_data="back_main_menu"), width=1)
    return markup.as_markup(resize_keyboard=True)


def find_user_kb():
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text="🔍 Username", callback_data="find_user_username"), InlineKeyboardButton(text="🔍 ID", callback_data="find_user_id"), width=2)
    markup.row(InlineKeyboardButton(text="🚀 В админ меню", callback_data="back_admin_menu"), width=1)
    return markup.as_markup(resize_keyboard=True)


async def find_user_actions_kb(user_id):
    markup = InlineKeyboardBuilder()
    user_ban_status = await get_user_ban(user_id)
    if user_ban_status[0]:
        markup.row(InlineKeyboardButton(text="🎉 Разбанить", callback_data=f"unban_user_{user_id}"), width=1)
    else:
        markup.row(InlineKeyboardButton(text="⛓ Забанить", callback_data=f"ban_user_{user_id}"), width=1)
    markup.row(InlineKeyboardButton(text="🗑 Удалить данные", callback_data=f"reset_user_data_{user_id}"), width=1)
    markup.row(InlineKeyboardButton(text="❌ Закрыть", callback_data="delete_message"), width=1)
    return markup.as_markup(resize_keyboard=True)


async def ban_kb(user_id):
    markup = InlineKeyboardBuilder()
    user_ban_status = await get_user_ban(user_id)
    if not user_ban_status[0]:
        markup.row(InlineKeyboardButton(text="⛓ Забанить", callback_data=f"ban_user_{user_id}"), width=1)
    return markup.as_markup(resize_keyboard=True)


async def prize_menu_kb():
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text="🚀 В меню призов", callback_data="back_prizes_menu"), width=1)
    return markup.as_markup(resize_keyboard=True)


def admin_prize_menu_kb(prize_id):
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text="✅ Выдать", callback_data=f"prize_issued_{prize_id}"), width=1)
    markup.row(InlineKeyboardButton(text="❌ Закрыть", callback_data="delete_message"), width=1)
    return markup.as_markup(resize_keyboard=True)