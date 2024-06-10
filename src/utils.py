import asyncio

import src.handlers as hd

from database.db_handler import get_user_invite_num, get_users_count
from scripts.config import (
    phone_number,
    address,
    opening_hours,
    admins,
    invite_num
)

from aiogram.enums import ChatMemberStatus
from aiogram.utils.payload import decode_payload
from aiogram.utils.deep_linking import create_start_link


async def send_notify(call_id, text, show_alert):
    await hd.bot.answer_callback_query(call_id, show_alert=show_alert, text=text)


async def send_message_with_delay(user_id, message, delay):
    await hd.bot.send_message(user_id, message)
    await asyncio.sleep(delay)


async def send_message_with_delay_markup(user_id, message, markup, delay):
    await hd.bot.send_message(user_id, message, reply_markup=markup)
    await asyncio.sleep(delay)


async def send_animation_with_delay(user_id, animation, delay):
    await hd.bot.send_animation(user_id, animation)
    await asyncio.sleep(delay)


async def check_chat_member(chat_id, user_id):
    user_channel_status = await hd.bot.get_chat_member(chat_id=chat_id, user_id=user_id)
    return True if user_channel_status.status != ChatMemberStatus.LEFT else False


async def hello_text(message):
    return f"<b>⭐️ Добро пожаловать в точку вкуса, <code>{message.from_user.full_name}</code>!</b>" if message.from_user.full_name else "<b>⭐️ Добро пожаловать в точку вкуса!</b>"


async def get_referrer(command):
    try:
        decoded = decode_payload(command.args)
    except:
        decoded = 0
    return decoded


async def profile_text(referrer_username, user_prizes_num, user_invite_num):
    user_referrer_text = "" if referrer_username == 0 else f"🤝 Пригласил(а): <code>@{referrer_username}</code>\n\n"
    return f"<b>{user_referrer_text}🎁 Подарков открыто: <code>{user_prizes_num}</code>\n👥 Приглашено друзей: <code>{user_invite_num}</code></b>"


async def info_text():
    opening_hours_text = ""
    if len(set(opening_hours.values())) == 1:
        opening_hours_text = f"С понедельника по воскресенье: {list(opening_hours.values())[0]}"
    else:
        for key, value in opening_hours.items():
            opening_hours_text += f"<i>{key}: {value}</i>\n"
    return f"<b>☎️ Телефон: <code>{phone_number}</code>\n\n🏠 Адрес: <i>{address}</i>\n\nЧасы работы:\n\n{opening_hours_text}</b>"


async def referral_program_text(user_id):
    user_link = await create_start_link(hd.bot, str(user_id), encode=True)
    user_invite_num, = await get_user_invite_num(user_id)
    return f"<b>🎉 Приглашайте друзей и получайте подарки!\n\n🎁 За каждые {invite_num} приглашенных друзей вы получите подарочную коробку с сюрпризом!\n\n🔗 Ваша реферальная ссылка: <code>{user_link}</code>\n\n👥 Приглашено друзей: <i>{user_invite_num} друзей</i>\n🎁 До следующей подарочной коробки осталось пригласить {invite_num - int(user_invite_num)} друзей\n\n👉🏻 Поделитесь своей ссылкой с друзьями и получайте еще больше подарков!</b>"


async def referral_user_text(referrer_username, user_username, referrer_invite_num):
    return f"<b>🚀 <code>{referrer_username}</code>, отличная работа!\n\n<code>{user_username}</code> стал твоим рефералом. Ты на шаг ближе к получению бонуса! 😉\n\n🎁 До следующей подарочной коробки осталось пригласить {invite_num - int(referrer_invite_num)} друзей</b>"


async def admin_text():
    return f"<b>👥 Количество пользователей: <code>{await get_users_count()}</code>\n🧑‍💻 Количество администраторов: <code>{len(admins)}</code></b>"


async def find_user_text(user_id, username, referrer, user_prizes_num, user_invite_num, user_ban_status):
    user_referrer_text = "" if referrer == 0 else f"🤝 Пригласил(а): <code>@{referrer}</code>\n"
    ban_text = "⛓ Забанен\n\n" if user_ban_status else ""
    return f"<b>👤 Информация о пользователе <code>@{username}</code>\n\n{user_referrer_text}{ban_text}🆔 ID: <code>{user_id}</code>\n🎁 Подарков открыто: <code>{user_prizes_num}</code>\n👥 Приглашено друзей: <code>{user_invite_num}</code></b>"
