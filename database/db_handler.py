import random

import aiosqlite

from scripts.config import db_name


async def create_tables():
    async with aiosqlite.connect(db_name) as db:
        await db.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER, username INTEGER, full_name INTEGER, referrer INTEGER, prizes_num INTEGER, invite_num INTEGER, banned INTEGER)')
        await db.execute('CREATE TABLE IF NOT EXISTS prizes (user_id INTEGER, prize_name INTEGER, prize_id INTEGER)')
        await db.commit()


async def check_user(user_id):
    async with aiosqlite.connect(db_name) as db:
        result = await db.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
        await db.commit()
        return bool(await result.fetchone())


async def insert_user(user_id, username, full_name, referrer):
    async with aiosqlite.connect(db_name) as db:
        await db.execute('INSERT INTO users (user_id, username, full_name, referrer, prizes_num, invite_num, banned) VALUES (?, ?, ?, ?, ?, ?, ?)', (user_id, username, full_name, referrer, 0, 0, False))
        await db.commit()


async def get_user_names(user_id):
    async with aiosqlite.connect(db_name) as db:
        result = await db.execute('SELECT username, full_name FROM users WHERE user_id = ?', (user_id,))
        await db.commit()
        return await result.fetchone()


async def get_user_invite_num(user_id):
    async with aiosqlite.connect(db_name) as db:
        result = await db.execute('SELECT invite_num FROM users WHERE user_id = ?', (user_id,))
        await db.commit()
        return await result.fetchone()


async def update_user(user_id, message):
    db_username, db_full_name = await get_user_names(user_id)
    async with aiosqlite.connect(db_name) as db:
        if db_username != message.from_user.username:
            await db.execute('UPDATE users SET username = ? WHERE user_id = ?', (message.from_user.username, user_id))

        if db_full_name != message.from_user.full_name:
            await db.execute('UPDATE users SET full_name = ? WHERE user_id = ?', (message.from_user.full_name, user_id))

        await db.commit()


async def get_user_profile(user_id):
    async with aiosqlite.connect(db_name) as db:
        result = await db.execute('SELECT referrer, prizes_num, invite_num FROM users WHERE user_id = ?', (user_id,))
        await db.commit()
        return await result.fetchone()


async def update_referrer_invite_num(current_invite_num, user_id):
    async with aiosqlite.connect(db_name) as db:
        result = await db.execute('UPDATE users SET invite_num = ? WHERE user_id = ?', (current_invite_num, user_id))
        await db.commit()
        return await result.fetchone()


async def get_users_count():
    async with aiosqlite.connect(db_name) as db:
        response = await db.execute('SELECT COUNT() FROM users')
        result, = await response.fetchone()
        await db.commit()
        return result


async def get_user(select, select_data):
    async with aiosqlite.connect(db_name) as db:
        result = await db.execute(f'SELECT * FROM users WHERE {select} = ?', (select_data,))
        await db.commit()
        return await result.fetchone()


async def update_user_data(column, data, user_id):
    async with aiosqlite.connect(db_name) as db:
        await db.execute(f'UPDATE users SET {column} = ? WHERE user_id = ?', (data, user_id))
        await db.commit()


async def get_user_ban(user_id):
    async with aiosqlite.connect(db_name) as db:
        result = await db.execute(f'SELECT banned FROM users WHERE user_id = ?', (user_id,))
        await db.commit()
        return await result.fetchone()


async def delete_user(user_id):
    async with aiosqlite.connect(db_name) as db:
        await db.execute(f'DELETE FROM users WHERE user_id = ?', (user_id,))
        await db.commit()


async def insert_prize(user_id, prize_name, prize_id):
    async with aiosqlite.connect(db_name) as db:
        await db.execute("INSERT INTO prizes (user_id, prize_name, prize_id) VALUES (?,?,?)", (user_id, prize_name, prize_id))
        await db.commit()


async def generate_prize_id():
    async with aiosqlite.connect(db_name) as db:
        while True:
            new_id = random.randint(0, 999999)
            async with db.execute("SELECT user_id FROM prizes WHERE prize_id=?", (new_id,)) as cursor:
                result = await cursor.fetchone()
                if not result:
                    return new_id


async def select_all_user_prizes(user_id):
    async with aiosqlite.connect(db_name) as db:
        async with db.execute("SELECT prize_name, prize_id FROM prizes WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchall()


async def all_user_prizes_num(user_id):
    async with aiosqlite.connect(db_name) as db:
        async with db.execute("SELECT prize_id FROM prizes WHERE user_id = ?", (user_id,)) as cursor:
            result = await cursor.fetchall()
            return len(result)


async def get_prize(prize_id):
    async with aiosqlite.connect(db_name) as db:
        async with db.execute('SELECT prize_name, user_id FROM prizes WHERE prize_id = ?', (prize_id,)) as cursor:
            result = await cursor.fetchone()
            return result


async def delete_prize(prize_id):
    async with aiosqlite.connect(db_name) as db:
        await db.execute(f'DELETE FROM prizes WHERE prize_id = ?', (prize_id,))
        await db.commit()


async def check_prize(prize_id):
    async with aiosqlite.connect(db_name) as db:
        result = await db.execute('SELECT user_id FROM prizes WHERE prize_id = ?', (prize_id,))
        await db.commit()
        return bool(await result.fetchone())
