# MIT License (c) 2024, 2025 Masakazu Suzuoki, AxTecChare
# See LICENSE.txt for details.

from blindx.frontend import Frontend
from blindx.auto_text import AutoText
from blindx.ft_settings import FtSettingDrawer

class AppBase():
    def __init__(self, page, my_key, active_names, viewer, backend):
        self.page = page
        self.my_key = my_key
        self.viewer = viewer
        self.frontend = Frontend(backend)
        self.settings = FtSettingDrawer(my_key, backend)
        self.auto_text = AutoText(my_key, active_names, page, viewer, self.frontend)

    def output_callback(self, lines):
        self.viewer.set_output(lines)

    async def start_async(self):    
        await self.viewer.start_async(
            self.page, 
            self.my_key, 
            self.on_keyboard_event_async, 
            self.on_change_event_async, 
            self.on_button_event_async
        )
        await self.connect_async()
        self.viewer.update()

    async def connect_async(self):
        self.frontend.set_output_callback(self.output_callback)
        self.frontend.invoke_output_callbacks()
                          
    async def disconnect_async(self):
        await self.auto_text.cancel_async()
        self.frontend.discard_output_callback()

    async def on_button_event_async(self, e):
        key = e.control.key
        if key == 'settings':
            self.page.open(self.settings)
        elif key == 'clear_all_lines':
            await self.viewer.set_input_async(self.frontend.clear_all_lines(None))
        elif key == 'clear_lines':
            await self.viewer.set_input_async(self.frontend.clear_all_lines(self.my_key)) 
        else:    
            self.frontend.invoke_output_callbacks()    
        self.viewer.update()

    async def on_keyboard_event_async(self, e):
        if e.key == 'F1':
            await self.auto_text.start_async(self.settings.sample_text)
            return
        elif e.key == 'F2':
            await self.auto_text.cancel_async()
            return
        elif self.viewer.get_input() == '' and e.key == 'Backspace':
            await self.viewer.set_input_async(self.frontend.clear_line(self.my_key)) 
            self.frontend.invoke_output_callbacks()

    async def on_change_event_async(self, e):
        input_text, output_lines = self.frontend.update(self.my_key, e.control.value)
        await self.viewer.set_input_async(input_text)
        self.frontend.invoke_output_callbacks()
