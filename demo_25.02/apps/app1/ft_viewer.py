# MIT License (c) 2024, 2025 Masakazu Suzuoki, AxTecChare
# See LICENSE.txt for details.

from blindx.viewer_base import ViewerBase
import flet as ft
from ft_chat import FtChat

class FtViewer(ViewerBase):
    async def start_async(
            self, page, key, on_keyboard_event_async, on_change_event_async, on_button_event_async):

        width = 640
        height = page.height
        self.page = page
        self.page.on_keyboard_event = on_keyboard_event_async
        self.page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
        self.page.title = 'BlindX Chat'
        self.page.window.width = width
        self.page.window.height = height
        self.chat = FtChat(key, on_change_event_async, on_button_event_async, width, height)
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

if __name__ == '__main__':
    viewer = FtViewer()

    def main(page: ft.Page):
        viewer.start(page, 'Alice', None, None, None)

    ft.app(target=main)
