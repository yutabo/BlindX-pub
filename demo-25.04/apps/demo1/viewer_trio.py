#!/usr/bin/env python3
#
# test chat
#
import random
import flet as ft
import threading
from ft_chat import Chat

class Viewer():
    def enroll(self, page, on_keyboard_event):
        self.page = page
        self.page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
        self.page.title = 'BlindX Chat'
        self.page.window.width = 1600
        self.page.window.height = 880
        self.page.on_keyboard_event = on_keyboard_event

        # self.output_lock = False
        self.lock = threading.Lock()

        self.left_chat = Chat('みさき', 450, 850)
        self.middle_chat = Chat('あやな', 450, 850)
        self.right_chat = Chat('りょうすけ', 450, 850)

        self.row = ft.Row(
            controls=[ 
                self.left_chat, 
                self.middle_chat, 
                self.right_chat, 
            ],
            alignment="spaceBetween", 
        )

        self.page.add(
            self.row,
        )

        self.clear()

    def clear(self):
        self.left_chat.clear()
        self.middle_chat.clear()
        self.right_chat.clear()
        self.update()
    
    def update(self):
        self.page.update()

    def clear_input(self):
        self.left_chat.input_text.value = ''
        self.middle_chat.input_text.value = ''
        self.right_chat.input_text.value = ''
        self.left_chat.input_text.focus()

    def set_output(self, lines):
        with self.lock:
            self.left_chat.set_output(lines)
            self.middle_chat.set_output(lines)
            self.right_chat.set_output(lines)
            self.update()

    def set_input(self, key, text):
        with self.lock:
            self.left_chat.set_input(key, text)
            self.middle_chat.set_input(key, text)
            self.right_chat.set_input(key, text)
            self.update()

    """        
    def set_user_name(self, name):
        self.left_chat.current_user_name = name
        self.middle_chat.current_user_name = name
        self.right_chat.current_user_name = name
    """

    def append_start_message(self):
        self.left_chat.append_start_message()
        self.middle_chat.append_start_message()
        self.right_chat.append_start_message()
        self.update()

if __name__ == '__main__':
    viewer = Viewer()

    def main(page: ft.Page):
        viewer.enroll(page)

    ft.app(target=main)
