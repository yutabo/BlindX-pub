# MIT License (c) 2024, 2025 Masakazu Suzuoki, AxTecChare
# See LICENSE.txt for details.

from blindx.ft_app_base import FtAppBase
from ft_chat import FtChat
import flet as ft

class FtApp(FtAppBase):
    async def start_async_internal(self):

        width = 640
        height = self.page.height
        self.page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
        self.page.title = 'BlindX Chat'
        self.page.window.width = width
        self.page.window.height = height
        self.chat = FtChat(self.my_key, self.on_change_event_async, self.on_button_event_async, width, height)
        self.page.add(self.chat)

    def update(self):
        self.page.update()
        self.chat.input_text.focus()

    def get_input(self):
        return self.chat.get_input()

    async def set_input_async(self, text):
        await self.chat.set_input_async(text)

    def set_output(self, lines):
        self.chat.set_output(lines)

