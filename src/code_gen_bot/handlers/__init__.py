from aiogram import Dispatcher

from .admin import admin_router
from .user import user_router


def register_all_routers(dp: Dispatcher):
    dp.include_router(admin_router)
    dp.include_router(user_router)
