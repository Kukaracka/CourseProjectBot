from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

main_menu = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Новая задача✅",
                                                                        callback_data="new_task"),
                                                   InlineKeyboardButton(text="Посмотреть задачи📋",
                                                                        callback_data="get_all_tasks")],
                                                   [InlineKeyboardButton(text="Настройки⚙️",
                                                                        callback_data="settings"),]])

to_main_from_anywhere = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="На главную🏠",
                                                                                    callback_data="to_main")]])

cancel = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Отмена❌",
                                                                     callback_data="to_main")]])

settings = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Изменить информацию✏️",
                                                                       callback_data="change_info"),
                                                  InlineKeyboardButton(text="На главную🏠",
                                                                       callback_data="to_main")]])

