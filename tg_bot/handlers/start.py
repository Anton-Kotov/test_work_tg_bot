from aiogram.types import ContentType


from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart

from tg_bot.config import load_config
from tg_bot.database.sql import create_table_users
from tg_bot.keyboards.inline import add_money
from tg_bot.modules.logging_set import logger


async def bot_start(message: types.Message):
    db = message.bot["db"]

    await db.create_table(create_table_users)
    await db.add_user(message.from_user.id,
                      message.from_user.first_name,
                      message.from_user.last_name)
    ban = await db.get_state(message.from_user.id)

    if ban["state"]:
        await message.answer(text=f"Привет, {message.from_user.first_name}.\n"
                                  "Я - бот для пополнения баланса.\n"
                                  "Нажмите на кнопку, чтобы пополнить баланс.\n"
                                  'Снизу инлайн кнопка с текстом "Пополнить баланс"',
                             reply_markup=add_money)
    else:
        logger.info(f"Пользователь {message.from_user.id} в бане и пытался войти")

async def enter_money(callback: types.CallbackQuery, state: FSMContext):
    db = callback.bot["db"]
    ban = await db.get_state(callback.from_user.id)
    if ban["state"]:
        await callback.message.answer(text="Введите сумму, на которую вы хотите пополнить баланс")
        await callback.answer()
        await state.set_state("enter_money")


async def get_bill(message: types.Message, state: FSMContext):
    amount = message.text

    async with state.proxy() as data:
        # для выбраной нами платежной системы (PayMaster) сумма должны быть в копейках
        data["amount"] = int(amount)
        data["id"] = message.from_user.id
    # проверяем, что пользователь ввел число корректно
    if amount.isdigit():
        logger.info(f"Пользователь {message.from_user.id} ввел {amount} р")
        PRICE = types.LabeledPrice(label='Перевод', amount=int(amount) * 100)
        await message.bot.send_invoice(
            chat_id=message.from_user.id,
            title=f"Перевод {amount} р.",
            description="тест",
            currency="rub",
            provider_token=load_config(".env").other.payments_token,
            prices=[PRICE],
            payload="test-invoice-payload",
        )

    else:
        await message.answer(text="Вы ввели некорректную сумму.\n"
                                  "Введите сумму, на которую вы хотите пополнить баланс")


async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery, state: FSMContext):
    await pre_checkout_q.bot.answer_pre_checkout_query(pre_checkout_query_id=pre_checkout_q.id, ok=True)
    await pre_checkout_q.bot.send_message("Перевод совершен")
    logger.info(f"Платеж совершен")
    db = pre_checkout_q.bot["db"]
    async with state.proxy() as data:
        telegram_id = data["id"]
        amount = data["amount"]
    # добавляем сумму в БД
    try:
        logger.info(f"добавляем сумму в БД")
        await db.add_balance(telegram_id, amount)
    except:
        logger.error(f"Платеж не добавлен в БД")



def register_start(dp: Dispatcher):
    dp.register_message_handler(bot_start, CommandStart())
    dp.register_callback_query_handler(enter_money, text="add_money")
    dp.register_message_handler(get_bill, state="enter_money")
    dp.pre_checkout_query_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)