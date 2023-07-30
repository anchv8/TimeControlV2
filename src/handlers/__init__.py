# У каждого хенделра своё название роутера
from .edit_work import edit_work_router
from .end_work import end_work_router
from .get_work import get_work_router
from .get_xlsx import get_xlsx_router
from .menu_keyboard import menu_router
from .start import start_router
from .start_work import start_work_router

# Массив с роутерами для диспетчера
routers = (start_router, start_work_router,
           end_work_router, edit_work_router,
           get_work_router, get_xlsx_router,
           menu_router)
# Массив с коммандами
commands = (
    ('menu', 'Меню'),
    ('start', 'регистрация'),
    ('startwork', 'Отметка о начале работы'),
    ('endwork', 'Отметка об окончании работы'),
    ('editwork', 'Изменить рабочее время'),
    ('getwork', 'Получить данные о рабочих сменах'),
    ('xlsx', 'Получить табель (для руководителей отделов)')
)
