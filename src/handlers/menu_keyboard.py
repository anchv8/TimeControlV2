from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.middlewares.is_register import IsRegister
from src.utils.main_menu import MainMenu

menu_router = Router(name='menu')
menu_router.message.outer_middleware(IsRegister())


@menu_router.message(Command('menu'))
async def menu(message: Message):
    await message.answer('Главное меню', reply_markup=MainMenu.start_menu())
