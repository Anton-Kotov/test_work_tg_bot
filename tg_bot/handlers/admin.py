from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

from tg_bot.config import load_config
from tg_bot.keyboards.inline import admin_select
from tg_bot.modules.logging_set import logger


async def admin(message: types.Message, state: FSMContext):
    config = load_config(".env")
    admins = config.tg_bot.admin_ids
    if message.from_user.id in admins:
        logger.info(f"Пользователь {message.from_user.id} вошел в панель администратора")
        markup = await admin_select()
        await message.answer(text="Выберите необходимое действие", reply_markup=markup)
    else:
        await message.answer(text="Эти функции доступны только администраторам!")

async def get_user(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(text="Введите telegram id пользователя")
    await state.set_state("get_user")

async def get_user_action(message: types.Message, state: FSMContext):
    telegram_id = message.text
    db = message.bot["db"]
    if telegram_id.isdigit():
        exist = await db.exist_user(telegram_id)
        if exist["exists"]:
            user = await db.get_user(telegram_id)
            await message.answer(text=f"telegram_id = {user['telegram_id']}\n"
                                      f"first_name = {user['first_name']}\n"
                                      f"last_name = {user['last_name']}\n"
                                      f"balance = {user['balance']}\n"
                                      f"state = {user['state']}\n")
        else:
            await message.answer(text="Пользователя с таким telegram_id\n"
                                      "нет в БД.")
        await state.finish()
    else:
        await message.answer(text="Введите telegram id пользователя")


async def change_balance(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(text="Введите telegram id пользователя\n"
                                       "и новый баланс через пробел")
    await state.set_state("change_balance")


async def change_balance_action(message: types.Message, state: FSMContext):
    try:
        telegram_id, new_balance = message.text.split()
        db = message.bot["db"]
        if telegram_id.isdigit() and new_balance.isdigit():
            exist = await db.exist_user(telegram_id)
            if exist["exists"]:
                await db.new_balance(telegram_id, new_balance)
                await message.answer(text="Баланс изменен")
            else:
                await message.answer(text="Пользователя с таким telegram_id\n"
                                          "нет в БД.")
            await state.finish()
        else:
            await message.answer(text="Введите telegram id пользователя\n"
                                      "и новый баланс через пробел")
    except:
        await message.answer(text="Введите telegram id пользователя\n"
                                  "и новый баланс через пробел")

async def ban_user(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(text="Введите telegram id пользователя,\n"
                                       "которого заносим в бан.")
    await state.set_state("ban")


async def ban_user_action(message: types.Message, state: FSMContext):
    telegram_id = message.text
    db = message.bot["db"]
    if telegram_id.isdigit():
        exist = await db.exist_user(telegram_id)
        if exist["exists"]:
            await db.ban_user(telegram_id)
            await message.answer(text="Пользователь забанен!")
        else:
            await message.answer(text="Пользователя с таким telegram_id\n"
                                      "нет в БД.")
        await state.finish()
    else:
        await message.answer(text="Введите telegram id пользователя\n"
                                  "которого заносим в бан.")

async def unban_user(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(text="Введите telegram id пользователя,\n"
                                       "которого удаляем из бана.")
    await state.set_state("unban")

async def unban_user_action(message: types.Message, state: FSMContext):
    telegram_id = message.text
    db = message.bot["db"]
    if telegram_id.isdigit():
        exist = await db.exist_user(telegram_id)
        if exist["exists"]:
            await db.unban_user(telegram_id)
            await message.answer(text="Пользователь разбанен!")
        else:
            await message.answer(text="Пользователя с таким telegram_id\n"
                                      "нет в БД.")
        await state.finish()
    else:
        await message.answer(text="Введите telegram id пользователя\n"
                                  "которого удаляем из бана.")

async def delete_user(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(text="Введите telegram id пользователя,\n"
                                       "которого удаляем из БД.")
    await state.set_state("delete")

async def delete_user_action(message: types.Message, state: FSMContext):
    telegram_id = message.text
    db = message.bot["db"]
    if telegram_id.isdigit():
        exist = await db.exist_user(telegram_id)
        if exist["exists"]:
            await db.delete_user(telegram_id)
            await message.answer(text="Пользователь удален из БД!")
        else:
            await message.answer(text="Пользователя с таким telegram_id\n"
                                      "нет в БД.")
        await state.finish()
    else:
        await message.answer(text="Введите telegram id пользователя\n"
                                  "которого удаляем из БД.")

async def get_all(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    db = callback.bot["db"]
    all_users = await db.get_all()
    print(all_users)
    await state.finish()

async def drop_table(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    db = callback.bot["db"]
    await db.drop_table()
    await callback.message.answer(text="Таблица удалена")
    await state.finish()

async def print_logs(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    with open("warning.log", "r") as file:
        print(file.read())

def register_admin(dp: Dispatcher):
    dp.register_message_handler(admin, Command("admin"))
    dp.register_callback_query_handler(get_user, text="get_user")
    dp.register_message_handler(get_user_action, state="get_user")
    dp.register_callback_query_handler(change_balance, text="change_balance")
    dp.register_message_handler(change_balance_action, state="change_balance")
    dp.register_callback_query_handler(ban_user, text="ban")
    dp.register_message_handler(ban_user_action, state="ban")
    dp.register_callback_query_handler(unban_user, text="unban")
    dp.register_message_handler(unban_user_action, state="unban")
    dp.register_callback_query_handler(delete_user, text="delete")
    dp.register_message_handler(delete_user_action, state="delete")
    dp.register_callback_query_handler(drop_table, text="drop")
    dp.register_callback_query_handler(get_all, text="get_all")
    dp.register_callback_query_handler(print_logs, text="print_logs")