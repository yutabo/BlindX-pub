# MIT License (c) 2024, 2025 Masakazu Suzuoki, AxTecChare
# See LICENSE.txt for details.

from backend_share import BackendShare
from blindx.backend import Backend
from blindx.login import Login
from blindx.misc import set_logger
from blindx.app_base import AppBase
from ft_viewer import FtViewer

import flet as ft
import logging
import asyncio

set_logger('app0_static')

logger = logging.getLogger(__name__)
backend = Backend()
login = Login()

async def main_async(page: ft.Page):

    login_name = await login.login_async()
    my_key = login_name
    active_names = login.active_names
    viewer = FtViewer()


    backend_share = BackendShare()

    backend_share.backend = backend
    await backend_share.start_async()
    my_key = backend_share.my_key
    active_names = backend_share.active_names

    print(my_key)
    print(active_names)

    app = AppBase(page, my_key, active_names, viewer, backend)

    async def on_connect_async(e):
        await login.connect_async(login_name)
        await app.connect_async()
        await backend_share.start_async()

    async def on_disconnect_async(e):
        await backend_share.shutdown_async()
        await app.disconnect_async()
        await login.disconnect_async(login_name)

    page.on_connect = on_connect_async
    page.on_disconnect = on_disconnect_async
    await app.start_async()

backend.start()
ft.app(target=main_async)
backend.shutdown()
