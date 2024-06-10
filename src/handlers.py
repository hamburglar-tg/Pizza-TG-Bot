from src.pagination import generate_prizes_keyboard, calculate_max_prizes_pages
from src.states import States
from src.utils import (
    profile_text,
    get_referrer,
    hello_text,
    check_chat_member,
    send_notify,
    info_text,
    referral_program_text,
    referral_user_text,
    admin_text,
    find_user_text
)
from database.db_handler import *
from src.keyboard import *
from scripts.config import (
    bot_token,
    channel_tag,
    main_image,
    bug_manager_id,
    latitude,
    longitude,
    random_prizes,
    invite_num
)

from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandObject, Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery


bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())


@dp.message(Command('info'))
async def command_opening_hours(message: Message, state: FSMContext):
    await state.set_state(None)
    user_id = message.from_user.id
    if not await check_chat_member(channel_tag, user_id):
        await bot.send_message(user_id, "⭐️<b> Чтобы пользоваться ботом, подпишитесь на наш телеграмм канал.</b>", reply_markup=channels_kb())
    else:
        if not await check_user(user_id):
            await message.answer("<b>⚠️ Пропишите /start</b>", close_kb())
        else:
            await bot.send_message(user_id, text=await info_text(), reply_markup=close_kb())


@dp.message(Command('support'))
async def command_opening_hours(message: Message, state: FSMContext):
    await state.set_state(None)
    user_id = message.from_user.id
    isUserBanned = await get_user_ban(user_id)
    if isUserBanned[0]:
        await message.answer("❗️ Ты забанен")
        await bot.delete_message(user_id, message.message_id)
    else:
        if not await check_chat_member(channel_tag, user_id):
            await bot.send_message(user_id, "⭐️<b> Чтобы пользоваться ботом, подпишитесь на наш телеграмм  канал.</b>", reply_markup=channels_kb())
        else:
            await message.answer("<b>🤔 Возникли сложности или появились вопросы? Смело пишите в поддержку, разберёмся вместе!</b>", reply_markup=close_kb())
            await state.set_state(States.support)


@dp.message(Command('start'))
async def command_start_handler(message: Message, command: CommandObject, state: FSMContext):
    if message.chat.type != "private":
        pass
    else:
        await state.set_state(None)

        user_id = message.chat.id
        user_username = message.from_user.username
        if not await check_user(user_id):
            user_referrer = await get_referrer(command)

            if await check_user(user_referrer):
                if int(user_referrer) != 0:
                    referrer_chat = message.chat if user_referrer == user_id else await bot.get_chat(user_referrer)
                    referrer_username = referrer_chat.username
                    referrer_full_name = referrer_chat.full_name
                    referrer_invite_num = await get_user_invite_num(user_referrer)

                    new_invite_num = referrer_invite_num[0] + 1
                    if int(new_invite_num) >= invite_num:
                        new_invite_num = 0
                        random_prize = random.choice(random_prizes)
                        prize_id = await generate_prize_id()
                        await insert_prize(user_referrer, random_prize, prize_id)
                        await bot.send_message(user_referrer, text=f"<b>🎉 Спасибо за активность, <code>{referrer_full_name}</code>! Ты привел {invite_num} новых пользователей и заслужили награду: {random_prize}.</b>", reply_markup=close_kb())
                    else:
                        await bot.send_message(user_referrer, text=await referral_user_text(referrer_username, user_username, new_invite_num), reply_markup=close_kb())
                    await update_referrer_invite_num(new_invite_num, user_referrer)

            await insert_user(user_id, user_username, message.from_user.full_name, user_referrer)
        else:
            isUserBanned = await get_user_ban(user_id)
            if isUserBanned[0]:
                await message.answer("❗️ Ты забанен")
                await bot.delete_message(user_id, message.message_id)
            else:
                await update_user(user_id, message)

                if not await check_chat_member(channel_tag, user_id):
                    await bot.send_message(user_id, "⭐️<b> Чтобы пользоваться ботом, подпишитесь на наш телеграмм канал.</b>", reply_markup=channels_kb())
                else:
                    await bot.send_photo(user_id, main_image, caption=f"<i>Главное меню</i>\n\n{await hello_text(message)}", reply_markup=main_menu_kb(user_id))


@dp.callback_query()
async def main_callback_query(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    message_id = call.message.message_id
    username = call.from_user.username
    if call.data == "check_channel":
        if not await check_chat_member(channel_tag, user_id):
            await bot.send_message(user_id, f"⚠️<b> Вы не подписались на наш канал.</b>")
        else:
            await bot.delete_message(user_id, message_id)
            await bot.send_photo(user_id, main_image, caption=f"<i>Главное меню</i>\n\n🆔 Ваш ID: <code>{user_id}</code>", reply_markup=main_menu_kb(user_id))
    else:
        if not await check_chat_member(channel_tag, user_id):
            await bot.send_message(user_id, "⭐️<b> Чтобы пользоваться ботом, подпишитесь на наш телеграмм канал.</b>", reply_markup=channels_kb())
        else:
            if not await check_user(user_id):
                await send_notify(call.id, "⚠️ Пропишите /start", True)
                await bot.delete_message(user_id, message_id)
            else:
                isUserBanned = await get_user_ban(user_id)
                if isUserBanned[0]:
                    await send_notify(call.id, "❗️Ты забанен", True)
                    await bot.delete_message(user_id, message_id)
                else:
                    if call.data == "user_profile":
                        user_referrer, user_prizes_num, user_invite_num = await get_user_profile(user_id)
                        try:
                            referrer_username = dict(await bot.get_chat(user_referrer))["username"]
                        except:
                            referrer_username = 0
                        await bot.edit_message_caption(user_id, message_id, caption=f"<i>Главное меню > Профиль</i>\n\n{await profile_text(referrer_username, user_prizes_num, user_invite_num)}", reply_markup=profile_kb())

                    elif call.data == "back_main_menu":
                        await bot.edit_message_caption(user_id, message_id, caption=f"<i>Главное меню</i>\n\n🆔 Ваш ID: <code>{user_id}</code>", reply_markup=main_menu_kb(user_id))

                    elif call.data == "find_bug":
                        await bot.send_message(user_id, "<b>🐞 Нашли проблему? Опишите ёё подробнее.</b>", reply_markup=close_kb())
                        await state.set_state(States.find_bug)

                    elif call.data == "delete_message":
                        await state.set_state(None)
                        await bot.delete_message(user_id, message_id)

                    elif call.data == "info":
                        await bot.edit_message_caption(user_id, message_id, caption=f"<i>Главное меню > Информация</i>\n\n{await info_text()}", reply_markup=info_kb())

                    elif call.data == "get_geolocation":
                        await bot.send_location(user_id, latitude=latitude, longitude=longitude, reply_markup=close_kb())

                    elif call.data == "referral_program":
                        await bot.edit_message_caption(user_id, message_id, caption=f"<i>Главное меню > Реферальная программа</i>\n\n{await referral_program_text(user_id)}", reply_markup=back_menu_kb())

                    elif call.data == "admin_panel":
                        if user_id in admins:
                            await bot.edit_message_caption(user_id, message_id, caption=f"<i>Главное меню > Админ панель</i>\n\n{await admin_text()}", reply_markup=admin_kb())
                        else:
                            await send_notify(call.id, "⚠️ Ты не администратор", True)
                            await bot.delete_message(user_id, message_id)

                    elif call.data == "find_user":
                        if user_id in admins:
                            await bot.edit_message_caption(user_id, message_id, caption="<i>Главное меню > Админ панель > Поиск пользователя</i><b>\n\n❗Выберите данные которые у вас есть о пользователе:</b>", reply_markup=find_user_kb())
                        else:
                            await send_notify(call.id, "⚠️ Ты не администратор", True)
                            await bot.delete_message(user_id, message_id)

                    elif call.data == "back_admin_menu":
                        if user_id in admins:
                            await bot.edit_message_caption(user_id, message_id, caption=f"<i>Главное меню > Админ панель</i>\n\n{await admin_text()}", reply_markup=admin_kb())
                        else:
                            await send_notify(call.id, "⚠️ Ты не администратор", True)
                            await bot.delete_message(user_id, message_id)

                    elif call.data.startswith("find_user_"):
                        if user_id in admins:
                            user_data = call.data[10:]

                            await state.set_state(States.find_user_username if user_data == "username" else States.find_user_id)
                            await bot.send_message(user_id, text=f"<b>📝 Введите {user_data} пользователя.</b>", reply_markup=close_kb())
                        else:
                            await send_notify(call.id, "⚠️ Ты не администратор", True)
                            await bot.delete_message(user_id, message_id)

                    elif call.data.startswith("ban_user_"):
                        if user_id in admins:
                            data_user_id = call.data[9:]
                            if int(data_user_id) == user_id:
                                await send_notify(call.id, "⚠️ Ты не можешь забанить сам себя", True)
                            else:
                                await update_user_data("banned", True, data_user_id)
                                await bot.send_message(data_user_id, f"<b>❌ Вы были забанены администратором <code>@{username}</code></b>", reply_markup=close_kb())
                                await send_notify(call.id, "✅ Пользователь успешно забанен.", True)
                                await bot.delete_message(user_id, message_id)
                        else:
                            await send_notify(call.id, "⚠️ Ты не администратор", True)
                            await bot.delete_message(user_id, message_id)

                    elif call.data.startswith("unban_user_"):
                        if user_id in admins:
                            data_user_id = call.data[11:]
                            if int(data_user_id) == user_id:
                                await send_notify(call.id, "⚠️ Ты не можешь разбанить сам себя", True)
                            else:
                                await update_user_data("banned", False, data_user_id)
                                await bot.send_message(data_user_id, f"<b>✅ Вас разбанил администратор <code>@{username}</code></b>", reply_markup=close_kb())
                                await send_notify(call.id, "✅ Пользователь успешно разбанен.", True)
                                await bot.delete_message(user_id, message_id)
                        else:
                            await send_notify(call.id, "⚠️ Ты не администратор", True)
                            await bot.delete_message(user_id, message_id)

                    elif call.data.startswith("reset_user_data_"):
                        if user_id in admins:
                            data_user_id = call.data[16:]

                            await delete_user(data_user_id)
                            await send_notify(call.id, "✅ Данные пользователя успешно удалены.", True)
                            await bot.delete_message(user_id, message_id)
                        else:
                            await send_notify(call.id, "⚠️ Ты не администратор", True)
                            await bot.delete_message(user_id, message_id)

                    elif call.data == "prizes":
                        max_page_number = await calculate_max_prizes_pages(user_id)
                        keyboard = await generate_prizes_keyboard(user_id, 1, max_page_number)
                        await bot.edit_message_caption(user_id, message_id, caption="<i>Главное меню > Призы</i>", reply_markup=keyboard)

                    elif call.data.startswith("next_page_prizes_"):
                        page_number = int(call.data.split('_')[-1])
                        if page_number < 1:
                            pass
                        else:
                            max_pages = await calculate_max_prizes_pages(user_id)
                            keyboard = await generate_prizes_keyboard(user_id, page_number, max_pages)
                            await bot.edit_message_caption(user_id, message_id, caption="<i>Главное меню > Призы</i>", reply_markup=keyboard)

                    elif call.data.startswith("prev_page_prizes_"):
                        page_number = int(call.data.split('_')[-1])
                        max_pages = await calculate_max_prizes_pages(user_id)
                        if page_number > max_pages:
                            pass
                        else:
                            keyboard = await generate_prizes_keyboard(user_id, page_number, max_pages)
                            await bot.edit_message_caption(user_id, message_id, caption="<i>Главное меню > Призы</i>", reply_markup=keyboard)

                    elif call.data.startswith("open_prize_"):
                        prize_id = call.data[11:]
                        prize_data = await get_prize(prize_id)
                        if prize_data:
                            prize_name = prize_data[0]
                            await bot.edit_message_caption(user_id, message_id, caption=f"<i>Главное меню > Призы > {prize_name}</i>\n\n<b>🆔 ID подарка: <code>{prize_id}</code>\n🆔 Ваш ID: <code>{user_id}</code>\n🎁 Приз: <i>{prize_name}</i>\n\n😉 Чтобы забрать этот подарок, покажи ID подарка на кассе</b>", reply_markup=await prize_menu_kb())
                        else:
                            await send_notify(call.id, f"⚠️ Приз с ID {prize_id} не найден", True)
                            await bot.delete_message(user_id, message_id)

                    elif call.data == "back_prizes_menu":
                        max_page_number = await calculate_max_prizes_pages(user_id)
                        keyboard = await generate_prizes_keyboard(user_id, 1, max_page_number)
                        await bot.edit_message_caption(call.from_user.id, call.message.message_id, caption="<i>Главное меню > Призы</i>", reply_markup=keyboard)

                    elif call.data == "check_prize_id":
                        if user_id in admins:
                            await bot.send_message(user_id, text="<b>📝 Введите ID приза</b>", reply_markup=close_kb())
                            await state.set_state(States.check_prize)
                        else:
                            await send_notify(call.id, "⚠️ Ты не администратор", True)
                            await bot.delete_message(user_id, message_id)

                    elif call.data.startswith("prize_issued_"):
                        if user_id in admins:
                            prize_id = call.data[13:]
                            if await check_prize(prize_id):
                                await delete_prize(prize_id)
                                await send_notify(call.id, f"✅ Приз с ID {prize_id} успешно выдан", True)
                            else:
                                await send_notify(call.id, f"⚠️ Приз с ID {prize_id} не найден", True)
                            await bot.delete_message(user_id, message_id)
                        else:
                            await send_notify(call.id, "⚠️ Ты не администратор", True)
                            await bot.delete_message(user_id, message_id)


@dp.message(States.find_bug)
async def state_find_bug(message: Message, state: FSMContext):
    if message.content_type == 'text':
        await state.set_state(None)

        text = message.text
        user_id = message.from_user.id
        isUserBanned = await get_user_ban(user_id)

        if isUserBanned[0]:
            await message.answer("❗️ Ты забанен")
            await bot.delete_message(user_id, message.message_id)
        else:
            await bot.delete_message(user_id, message.message_id)
            await bot.send_message(bug_manager_id, f"<b>⚠️ Пользователь <code>@{message.from_user.username}</code> сообщил о баге.\n\n📝 Информация:</b>\n<i>{text}</i>", reply_markup=await ban_kb(user_id))
            await bot.send_message(user_id, "<b>✅ Спасибо за помощь в развитии нашего бота!</b>", reply_markup=close_kb())
    else:
        await message.answer('<b>❗ Можно отправлять только текст</b>', reply_markup=close_kb())


@dp.message(States.find_user_username)
async def state_find_user_username(message: Message, state: FSMContext):
    if message.content_type == 'text':
        username_text = message.text
        id = message.from_user.id
        isUserBanned = await get_user_ban(id)

        if isUserBanned[0]:
            await state.set_state(None)
            await message.answer("❗️ Ты забанен")
            await bot.delete_message(id, message.message_id)
        else:
            user_data = await get_user("username", username_text)

            await bot.delete_message(id, message.message_id)
            if user_data:
                await state.set_state(None)
                user_id, username, full_name, referrer, prizes_num, invites_num, banned = user_data
                await bot.send_message(id, await find_user_text(user_id, username, referrer, prizes_num, invites_num, banned), reply_markup=await find_user_actions_kb(user_id))
            else:
                await message.answer(f"<b>⚠️ Пользователь с Username <code>{username_text}</code> не найден. Введите существующий Username</b>", reply_markup=close_kb())
    else:
        await message.answer('<b>❗ Можно отправлять только текст</b>', reply_markup=close_kb())


@dp.message(States.find_user_id)
async def state_find_user_id(message: Message, state: FSMContext):
    if message.content_type == 'text':
        user_id_text = message.text
        id = message.from_user.id
        isUserBanned = await get_user_ban(id)

        if isUserBanned[0]:
            await state.set_state(None)
            await message.answer("❗️ Ты забанен")
            await bot.delete_message(id, message.message_id)
        else:
            user_data = await get_user("user_id", user_id_text)

            await bot.delete_message(id, message.message_id)
            if user_data:
                await state.set_state(None)
                user_id, username, full_name, referrer, prizes_num, invites_num, banned = user_data
                await bot.send_message(id, await find_user_text(user_id, username, referrer, prizes_num, invites_num, banned), reply_markup=await find_user_actions_kb(user_id))
            else:
                await message.answer(f"<b>⚠️ Пользователь с ID <code>{user_id_text}</code> не найден. Введите существующий Username</b>", reply_markup=close_kb())
    else:
        await message.answer('<b>❗ Можно отправлять только текст</b>', reply_markup=close_kb())


@dp.message(States.support)
async def state_support(message: Message, state: FSMContext):
    if message.content_type == 'text':
        support_text = message.text
        user_id = message.from_user.id
        isUserBanned = await get_user_ban(user_id)

        if isUserBanned[0]:
            await state.set_state(None)
            await message.answer("❗️ Ты забанен")
            await bot.delete_message(user_id, message.message_id)
        else:
            await bot.send_message(bug_manager_id, text=f"<b>🧑‍💻 Новое обращение в поддержку от пользователя с ID <code>{user_id}</code>\n\n📝 Информация:</b>\n<i>{support_text}</i>", reply_markup=await ban_kb(user_id))
            await bot.send_message(user_id, "<b>✅ Спасибо за помощь в развитии нашего бота!</b>", reply_markup=close_kb())
    else:
        await message.answer('<b>❗ Можно отправлять только текст</b>', reply_markup=close_kb())


@dp.message(States.check_prize)
async def state_check_prize(message: Message, state: FSMContext):
    if message.content_type == 'text':
        prize_id_text = message.text
        user_id = message.from_user.id
        isUserBanned = await get_user_ban(user_id)

        if isUserBanned[0]:
            await state.set_state(None)
            await message.answer("❗️ Ты забанен")
            await bot.delete_message(user_id, message.message_id)
        else:
            if user_id in admins:
                prize_data = await get_prize(prize_id_text)
                if prize_data:
                    prize_name = prize_data[0]
                    prize_user = prize_data[1]
                    await state.set_state(None)
                    await bot.send_message(user_id, f"<b>🆔 ID подарка: <code>{prize_id_text}</code>\n🆔 ID получателя: <code>{prize_user}</code>\n🎁 Приз: <i>{prize_name}</i></b>", reply_markup=admin_prize_menu_kb(prize_id_text))
                else:
                    await message.answer(f"<b>⚠️ Приз с ID <code>{prize_id_text}</code> не найден. Введите верный ID</b>", reply_markup=close_kb())
                    await bot.delete_message(user_id, message.message_id)
            else:
                await state.set_state(None)
                await message.answer("<b>⚠️ Ты не администратор</b>", reply_markup=close_kb())
                await bot.delete_message(user_id, message.message_id)
    else:
        await message.answer('<b>❗ Можно отправлять только текст</b>', reply_markup=close_kb())