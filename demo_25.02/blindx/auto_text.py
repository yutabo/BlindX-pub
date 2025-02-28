# MIT License (c) 2024, 2025 Masakazu Suzuoki, AxTecChare
# See LICENSE.txt for details.

import asyncio
import logging

class AutoMessage():
    def __init__(self, session_id, input_text):
        self.session_id = session_id
        self.input_text = input_text
    
class AutoText():
    def __init__(self, my_key, active_names, page, viewer, frontend):
        self.logger = logging.getLogger(__name__)
        self.my_key = my_key
        self.active_names = active_names
        self.page = page
        self.viewer = viewer
        self.frontend = frontend
        self.page.pubsub.subscribe_topic('auto_text', self.on_message_async)
        self.task = None

    async def on_message_async(self, topic, message):
        key = message['key']
        input_text = message['text']
        if self.my_key == key:
            # print(f"viewer. set_input {message['text']}")
            input_text, output_lines = self.frontend.update(key, input_text)
            self.frontend.invoke_output_callbacks()
            await self.viewer.set_input_async(input_text)
            self.viewer.update()

    async def cancel_async(self):
        if self.task:
            self.is_cancel = True
            await self.task
            self.task = None

    async def start_async(self, sample_text):
        if not self.task:
            self.is_cancel = False
            self.task = asyncio.create_task(self.play_async(sample_text))

    async def play_async(self, sample_text):
        try:
            for text in sample_text.splitlines():
                user_name = self.my_key
                if text and text[0] == '\\':
                    key_index = min(int(text[1]), len(self.active_names) - 1)
                    user_name = self.active_names[key_index]
                    text = text[2:]

                src_text = ''
                for char in text + '\n':
                    if self.is_cancel: 
                        return
                    src_text += char

                    message = {
                        'key': user_name, 'text' : src_text
                    }
                    self.page.pubsub.send_all_on_topic('auto_text', message)
                    await asyncio.sleep(0.1)

        except Exception as e:
            self.logger.warning(f'play_async {e}.')

