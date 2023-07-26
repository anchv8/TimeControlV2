from aiogram import types
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


class MainMenu:
    @staticmethod
    def start_menu() -> ReplyKeyboardMarkup:
        menu_kb = ReplyKeyboardBuilder()
        menu_buttons = ['⏳ Начало работы', '⌛ Конец работы', '✏️ Изменить время', '📄 Мои смены', '🗄️ Табель (для руководителей отделов)']
        for i in menu_buttons:
            menu_kb.add(types.KeyboardButton(text=i))
        menu_kb.adjust(3, 3)
        return menu_kb.as_markup(resize_keyboard=True, input_field_placeholder='Главное меню', is_persistent=True)
