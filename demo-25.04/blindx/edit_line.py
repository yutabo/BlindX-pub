# MIT License (c) 2024, 2025 Masakazu Suzuoki, AxTecChare
# See LICENSE.txt for details.

from .romhira import Romhira
from .frontend import Frontend
from .jis_keyboard import getchar_from_key

class EditLine():
    def __init__(self, frontend, on_change_callback):
        self.frontend = frontend
        self.on_change_callback = on_change_callback
        self.before = Romhira()
        self.after = ''
        self.cursor = 0
        self.strlen = 0

    def move(self, cursor):
        text = self.before.hiragana_and_preface() + self.after
        self.cursor = max(min(cursor, self.strlen), 0)
        self.before.clear()
        self.before.addstr(text[:self.cursor])
        self.after = text[self.cursor:]

    def add(self, char):
        self.before.add(char)

    def backspace(self):
        if self.cursor > 0:
            self.cursor -= 1
            self.before.backward()

    def delete(self):
        if self.cursor < self.strlen:
            self.after = self.after[1:]

    def kill(self):
        self.after = ''

    def clear(self):
        self.before.clear()
        self.after = ''

    def reset(self, text):
        self.clear()
        self.insert(text)

    def insert(self, text):
        self.before.addstr(text)

    def update(self, key):
        before_text = self.before.hiragana_and_preface()
        self.cursor = len(before_text)
        self.strlen = self.cursor + len(self.after)
        text = self.before.hiragana_and_preface() + self.after
        self.frontend.update(key, text, is_insert=True)

    def delete_line(self, key):    
        if self.frontend.lineno >= 0:
            prev_text = self.frontend.delete_line(key)
            self.reset(prev_text)
        else:
            self.frontend.update(key, '')
            next_text = self.frontend.next_line(key)
            self.reset(next_text)

    def join_line(self, key):    
        join_text = self.frontend.join_line(key)
        self.reset(join_text)

    def on_keyboard_input(self, keycode, ctrl, shift):
        key = 'Alice'

        if ctrl:
            if keycode == 'P':
                self.frontend.terminate_line()
                self.reset(self.frontend.prev_line(key))

            elif keycode == 'N':
                self.frontend.terminate_line()
                self.reset(self.frontend.next_line(key))

            elif keycode == 'A':
                self.move(0)

            elif keycode == 'E':
                self.move(self.strlen)

            elif keycode == 'F':
                self.move(self.cursor + 1)

            elif keycode == 'B':
                self.move(self.cursor - 1)

            elif keycode == 'D':
                if self.after:
                    self.delete()
                else:    
                    self.join_line(key)

            elif ctrl and keycode == 'K':
                if self.cursor > 0:
                    self.kill()
                else:
                    self.delete_line(key)

            elif keycode == 'H':
                if self.cursor > 0:
                    self.backspace()
                else:
                    after_text = self.after
                    self.delete_line(key)
                    self.after = after_text
                    
            elif keycode == 'M':
                if self.cursor == 0:
                    self.frontend.insert_and_move_to_next_line(key, True)
                    self.before.clear()
                elif self.cursor == self.strlen:
                    self.frontend.terminate_line()
                    self.reset(self.frontend.next_line(key))
                else:
                    self.add('\n')
                    self.update(key)
                    self.before.clear()

        elif keycode.isprintable():
            char = getchar_from_key(keycode, shift)
            self.add(char)

        self.update(key)
        self.on_change_callback(self)





