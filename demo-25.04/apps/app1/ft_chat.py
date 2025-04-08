# MIT License (c) 2024, 2025 Masakazu Suzuoki, AxTecChare
# See LICENSE.txt for details.

import flet as ft
import threading
from blindx.ft_color_spans import FtColorSpans

c_inactive_color = '#f0f0f0'
c_inactive_bgcolor = '#e8e8e8'
c_active_color = '#f0fff0'

class ChatMessage(ft.Row):
    def __init__(self, key, user_name, width):
        super().__init__()

        self.key = key
        self.vertical_alignment = ft.CrossAxisAlignment.START
        bgcolor = c_inactive_color

        if self.key == user_name:
            self.alignment=ft.MainAxisAlignment.END 
            bgcolor = c_active_color

        self.controls = [

            ft.CircleAvatar(
                content=ft.Text(self.get_initials(user_name)),
                color=ft.Colors.WHITE,
                bgcolor=self.get_avatar_color(user_name),
            ),

            ft.Container(
                content=ft.Column(
                    [
                        ft.Text(user_name, weight='bold', color=ft.Colors.BLUE),
                        ft.Text(width=width * 3 / 5, size=17, color=ft.Colors.BLACK),
                    ],
                    tight=True,
                    spacing=5,
                ),
                border=ft.border.all(1, ft.Colors.OUTLINE),
                border_radius=5,
                bgcolor=bgcolor,
                padding=5,  
            ),

        ]

    def set_message_text_spans(self, text_spans):  
        self.controls[1].content.controls[1].spans = text_spans

    def get_initials(self, user_name):
        return user_name[:1].capitalize()

    def get_avatar_color(self, user_name):
        colors_lookup = [
            ft.Colors.AMBER, ft.Colors.BLUE, ft.Colors.BROWN, ft.Colors.CYAN,
            ft.Colors.GREEN, ft.Colors.INDIGO, ft.Colors.LIME, ft.Colors.ORANGE, ft.Colors.PINK,
            ft.Colors.PURPLE, ft.Colors.RED, ft.Colors.TEAL, ft.Colors.YELLOW,
        ]
        return colors_lookup[hash(user_name) % len(colors_lookup)]

class FtChat(ft.Column):

    def __init__(self, my_key, on_change_event_async, on_button_event_async, width, height):
        super().__init__()

        self.my_key = my_key
        self.chat_messages = []
        self.width = width
        self.expand = True
        self.is_color_span = False
        self.lock = threading.Lock()

        self.input_text = ft.TextField(
            label= my_key,
            hint_text='Message Here..',
            hint_style=ft.TextStyle(italic=True),
            helper_text='ローマ字入力してください。改行で送信されます',
            autofocus=True,
            min_lines=1,
            max_lines=5,
            filled=True,
            expand=True,
            # text_size=14,
            text_size=16,
            multiline=True,
            on_change=on_change_event_async,
        )

        self.output_listview = ft.ListView(
            expand=True,
            spacing=10,
            padding = ft.padding.only(right=15),
            auto_scroll=True,
        )
        self.start_message = ft.Container(
            content=ft.Column(
                controls = [
                    ft.Text('BlindX Realtime Chat', size=38, color=ft.Colors.BLACK),
                ],
                alignment = ft.MainAxisAlignment.SPACE_EVENLY,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            height=height,
            alignment=ft.alignment.center,  # コンテナの中心に配置
        )

        self.controls=[
            ft.Container(
                content=self.output_listview,
                border=ft.border.all(1, ft.Colors.OUTLINE),
                border_radius=5,
                padding=10,
                expand=True,
                bgcolor="white",
            ),
            ft.Row(
                [
                    self.input_text,
                ]
            ),
            ft.Row(
                [
                    ft.Switch(
                        label="カラー表示", 
                        key='color_span', 
                        value=False, 
                        on_change=self.on_color_span_event_async
                    ),
                    ft.OutlinedButton(
                        text="自分の投稿を削除", 
                        key='clear_lines', 
                        on_click = on_button_event_async),
                    ft.OutlinedButton(
                        text="全削除", 
                        key='clear_all_lines', 
                        on_click = on_button_event_async),
                    ft.IconButton(
                        icon=ft.Icons.SETTINGS,
                        tooltip="詳細設定",
                        key='settings', 
                        on_click = on_button_event_async,
                    ),
                ],
                wrap=True,
                alignment=ft.MainAxisAlignment.END,
            ),

        ]

    def clear(self):
        self.chat_messages = []
        self.output_listview.controls = [self.start_message]
        self.input_text.value = ''
        self.update()

    def get_input(self):
        return self.input_text.value

    async def set_input_async(self, text):
        self.input_text.value = text
        self.input_text.update()

    def set_output(self, lines):
        with self.lock:

            user_names = set()    
            self.output_listview.controls = [self.start_message]

            valid_line_len = 0
            for line in lines:
                if line.key: valid_line_len += 1

            if valid_line_len != len(self.chat_messages):
                self.chat_messages.clear()

            lineno = 0    
            for line in lines:
                output_text = line.output_text.rstrip()
                user_name = line.key

                if line.key == None:
                    continue

                if user_name not in user_names:
                    new_login_text = f'{user_name} さんが参加しました'
                    message = ft.Text(new_login_text, italic=True, color=ft.Colors.BLACK45, size=16)
                    self.output_listview.controls.append(message)
                    user_names.add(user_name)    

                if lineno == len(self.chat_messages):
                    self.chat_messages.append(ChatMessage(self.my_key, user_name, self.width))

                if line.output_text and line.long_output_text == line.output_text:
                    spans = [ft.TextSpan(output_text)]
                else:
                    spans = FtColorSpans(
                        output_text, line.prev_output_text, line.postfix(), self.is_color_span)
                self.chat_messages[lineno].set_message_text_spans(spans)
                self.output_listview.controls.append(self.chat_messages[lineno])
                lineno += 1

            self.output_listview.controls.append(ft.Text('')) # bottom padding
            self.output_listview.update()

    async def on_color_span_event_async(self, e):
        self.is_color_span = e.control.value

