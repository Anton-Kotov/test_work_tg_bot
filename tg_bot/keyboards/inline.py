from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


add_money = InlineKeyboardMarkup(row_width=1)
add_money.insert(InlineKeyboardButton(
                text="Пополнить баланс",
                callback_data="add_money"))

test_pay = InlineKeyboardMarkup(row_width=1)
test_pay.insert(InlineKeyboardButton(
                text="Проверить платеж",
                callback_data="test_pay"))
async  def admin_select():
    markup = InlineKeyboardMarkup(row_width=1)
    select_actions = [("Выгрузка пользователя", "get_user"), ("Выгрузка логов", "get_log"),
                      ("Изменить баланс", "change_balance"), ("Бан пользователя", "ban"),
                      ("Разбанить пользователя", "unban"), ("Удалить пользователя", "delete"),
                      ("Выгрузить всех пользователей", "get_all"), ("Удалить таблицу", "drop"),
                      ("Печать логов", "print_logs")]

    for text, call in select_actions:
        markup.insert(InlineKeyboardButton(
            text=text,
            callback_data=call))

    return markup
