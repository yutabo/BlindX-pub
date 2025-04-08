# MIT License (c) 2024, 2025 Masakazu Suzuoki, AxTecChare
# See LICENSE.txt for details.

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import blindx.misc as misc
from blindx.backend import Backend
from blindx.frontend import Frontend
from blindx.auto_text import AutoText
from viewer_trio import Viewer
import flet as ft
import logging

logger = logging.getLogger(__name__)
backend = Backend()
frontend = Frontend(backend)
viewer = Viewer()

def output_callback(lines):
    viewer.set_output(lines)
    
async def autotext_callback_async(message):
    key = message['key']
    text = message['text']
    input_text, output_lines = frontend.update(key, text)
    viewer.set_input(key, input_text)
    viewer.set_output(backend.lines)

auto_text = AutoText('みさき', ['みさき', 'あやな', 'りょうすけ', 'ちくわ大明神'], autotext_callback_async)

async def main_async(page: ft.Page):

    frontend.set_output_callback(output_callback)

    full_path = misc.search_path('assets/samples/senario0.txt')
    sample_text = misc.load_string_from_file(full_path)

    await auto_text.start_async(sample_text)

    def on_keyboard_event(e):
        pass

    viewer.enroll(page, on_keyboard_event)
    viewer.update()

backend.start()
ft.app(target=main_async)
backend.shutdown()


"""
def main(page: ft.Page):

    def send_message_click(e):
        message_text = backend.lines[-1].output_text
        if message_text != '':
            backend.push_line()
            romhira.clear()
            viewer.clear_input()
            viewer.update()

    def on_keyboard_event(e):
        funckey_lookup = {
            'F5': '1', 'F6': '2', 'F7': '3', 'F8': '9', 
        }

        c = e.key

        if c == 'F1':
            auto_text.is_pause = True
            backend.clear()
            romhira.clear()
            viewer.clear()
            return

        if c == 'F2':
            auto_text.is_pause = False
            return

        elif c in funckey_lookup:
            viewer.set_markup(funckey_lookup[c])
            return;
        
        elif c == 'Escape':
            auto_text.shutdown()
            backend.shutdown()
            page.window.close()
            return

        elif c == 'Enter':
            send_message_click(e)
            return

        elif c == 'Backspace':
            if not romhira.empty():
                romhira.backward()
                
        else:
            romhira.addshift(c, e.shift)
            viewer.set_input(romhira.hiragana + romhira.preface)

        backend.lines[-1].input_text = romhira.hiragana
        backend.request()
        viewer.update()

    def backend_callback():
        viewer.set_output(backend.lines)

    viewer.enroll(page, on_keyboard_event, send_message_click)
    viewer.page.update()

    backend.start('http://localhost:8000', backend_callback)
    auto_text.start(viewer, backend, False) # no return

ft.app(target=main)
"""

