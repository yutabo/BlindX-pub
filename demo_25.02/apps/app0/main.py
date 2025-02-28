# MIT License (c) 2024, 2025 Masakazu Suzuoki, AxTecChare
# See LICENSE.txt for details.

from blindx.backend import Backend
from blindx.login import Login
from blindx.misc import set_logger
from blindx.app_base import AppBase
from ft_viewer import FtViewer

import flet as ft
import logging

set_logger('app0')

logger = logging.getLogger(__name__)
backend = Backend()
login = Login()

async def main_async(page: ft.Page):

    login_name = await login.login_async()
    my_key = login_name
    viewer = FtViewer()

    app = AppBase(page, my_key, login.active_names, viewer, backend)

    async def on_connect_async(e):
        await login.connect_async(login_name)
        await app.connect_async()

    async def on_disconnect_async(e):
        await app.disconnect_async()
        await login.disconnect_async(login_name)

    page.on_connect = on_connect_async
    page.on_disconnect = on_disconnect_async
    await app.start_async()

backend.start()
ft.app(target=main_async)
backend.shutdown()
