#!/usr/bin/env python3
#
# test chat
#
import random
import flet as ft
# from ft_color_spans import ColorSpans
from blindx.ft_color_spans import FtColorSpans

c_inactive_color = '#f0f0f0'
# c_inactive_bgcolor = '#b0d0b0'
c_inactive_bgcolor = '#b0b0d0'

c_active_color = '#f0fff0'
# c_active_bgcolor = '#e0ffe0'
c_active_bgcolor = '#d0d0ff'
c_inactive_shadow=ft.BoxShadow()

c_active_shadow=ft.BoxShadow(
    spread_radius=5,
    blur_radius=15,
    color=ft.Colors.GREY,
    offset=ft.Offset(5, 5)
)

class Message:
    def __init__(self, key, text_spans):
        self.key = key
        self.text_spans = text_spans

class ChatMessage(ft.Row):
    def __init__(self, key, message):
        super().__init__()
        self.vertical_alignment = ft.CrossAxisAlignment.START
        bgcolor = c_inactive_color

        if key == message.key:
            self.alignment=ft.MainAxisAlignment.END 
            bgcolor = c_active_color

        self.controls = [
            ft.CircleAvatar(
                content=ft.Text(message.key[:1].capitalize()),
                color=ft.Colors.WHITE,
                bgcolor=self.get_avatar_color(message.key),
            ),

            ft.Container(
                content=ft.Column(
                    [
                        ft.Text(message.key, weight='bold'),
                        ft.Text(
                            spans=message.text_spans,
                            selectable=True, width=240),
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

    def get_avatar_color(self, key):
        colors_lookup = [
            ft.Colors.AMBER,
            ft.Colors.BLUE,
            ft.Colors.BROWN,
            ft.Colors.CYAN,
            ft.Colors.GREEN,
            ft.Colors.INDIGO,
            ft.Colors.LIME,
            ft.Colors.ORANGE,
            ft.Colors.PINK,
            ft.Colors.PURPLE,
            ft.Colors.RED,
            ft.Colors.TEAL,
            ft.Colors.YELLOW,
        ]
        return colors_lookup[hash(key) % len(colors_lookup)]

class Chat(ft.Column):

    def __init__(self, my_key, width = 620, height = 940):
        super().__init__()

        self.my_key = my_key
        self.input_text = ft.TextField(
            # hint_text='ローマ字入力してください',
            prefix = ft.Text(my_key + ': '),
            autofocus=True,
            shift_enter=True,
            min_lines=1,
            max_lines=5,
            filled=True,
            expand=True,
            text_size=13,
        )

        self.output_listview = ft.ListView(
            expand=True,
            spacing=10,
            padding = ft.padding.only(right=15),
            auto_scroll=True,
        )

        self.target_controls = []
        self.width = width
        self.height = height
        
        self.controls=[
            ft.Container(
                content=self.output_listview,
                border=ft.border.all(1, ft.Colors.OUTLINE),
                border_radius=5,
                padding=10,
                expand=True,
                bgcolor=c_active_bgcolor,
            ),
            ft.Row(
                [
                    self.input_text,
                ]
            ),
        ]

    def clear(self):
        self.target_controls.clear()
        self.output_listview.controls.append(ft.Text(' ')) # padding
        self.input_text.value = ''
        self.append_start_message()

    def append_start_message(self):
        start_message = ft.Container(
            content=ft.Text('BlindX Chat', size=48),
            height=self.height-40,
            alignment=ft.alignment.center,  # コンテナの中心に配置
        )
        self.output_listview.controls.insert(-1, start_message)

    def set_input(self, key, text):
        if key != self.my_key:
            self.input_text.value = '.' * int(len(text)/4)

            self.input_text.bgcolor = c_inactive_color
            self.controls[0].bgcolor = c_inactive_bgcolor
            self.controls[0].shadow = c_inactive_shadow

        else:    
            self.input_text.value = text
            self.input_text.text_style = ft.TextStyle(weight=ft.FontWeight.BOLD)    
            self.input_text.focus()

            self.input_text.bgcolor = c_active_color
            self.controls[0].bgcolor = c_active_bgcolor
            self.controls[0].shadow = c_active_shadow


    def set_output(self, lines):
        if True:
            while len(self.target_controls) < len(lines):
                self.target_controls.append(-1)

            for i, line in enumerate(lines):
                input_text = line.input_text
                stage_input_text = line.stage_input_text

                output_text = line.output_text.removesuffix('\n')
                long_output_text = line.long_output_text.removesuffix('\n')
                prev_output_text = line.prev_output_text.removesuffix('\n')

                if output_text and long_output_text == output_text:
                    text_spans = [ft.TextSpan(output_text)]
                else:
                    text_spans = FtColorSpans(
                        output_text, prev_output_text, line.postfix(), True)

                index = self.target_controls[i]

                if index >= 0:
                    self.output_listview.controls[index].set_message_text_spans(text_spans)

                elif output_text.strip() != '':
                    # message_type = 'my_message' if line.key == self.my_key else 'message'
                    message = ChatMessage(
                        self.my_key,
                        Message(line.key, text_spans),
                    )
                    self.output_listview.controls.insert(-1, message)
                    self.target_controls[i] = len(self.output_listview.controls) - 2
