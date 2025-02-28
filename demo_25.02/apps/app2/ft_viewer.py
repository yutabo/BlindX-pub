# MIT License (c) 2024, 2025 Masakazu Suzuoki, AxTecChare
# See LICENSE.txt for details.

from blindx.backend import BackendLine

import flet as ft
import threading

class FtViewer:
    def start(self, page, on_keyboard_event):
        self.page = page
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.title = 'BlindX Share Edit',
        self.lock = threading.Lock()

        self.input_text = ft.Text(
            size=16, 
            expand=True,
        )

        self.output_listview = ft.ListView(
            auto_scroll=True,
        )

        top_container = ft.Container(
            content=ft.Text(
                'BlindX Report', 
                size=24,
                weight=ft.FontWeight.BOLD
            ),
            alignment=ft.alignment.center,
            height=60,
        )

        menu_container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.IconButton(
                                # icon=ft.Icons.FAST_FORWARD,
                                icon=ft.Icons.SKIP_NEXT,
                                # icon_color="blue400",
                                icon_size=24,
                            ),
                        ],
                    ),
                ],
            ),
        )

        def icon_button(icon, icon_size=18):
            return ft.IconButton(
                icon=icon, 
                icon_size=icon_size, 
                focus_color='white,0.0')

        upper_container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                self.input_text,
                                # icon_button(ft.Icons.MIC_OFF),
                                icon_button(ft.Icons.MENU),
                            ],
                            spacing=0,
                        ),
                        border=ft.border.all(1, ft.Colors.OUTLINE),
                        padding=2,
                    ),
                    ft.Text(
                        'ローマ字入力してください。改行で確定、バックスペースで１文字削除。左右上下矢印キーで移動します',
                        size=12,
                        style=ft.TextStyle(italic=True),
                    ),
                ],
                spacing=4,
            ),
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=5,
            padding=8,
        )

        """
        upper_container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            icon_button(ft.Icons.BACKSPACE_OUTLINED),
                            icon_button(ft.Icons.FORWARD_OUTLINED),
                            icon_button(ft.Icons.SKIP_PREVIOUS),
                            icon_button(ft.Icons.SKIP_NEXT),
                            icon_button(ft.Icons.ARROW_BACK),
                            icon_button(ft.Icons.ARROW_FORWARD),
                            icon_button(ft.Icons.ARROW_UPWARD),
                            icon_button(ft.Icons.ARROW_DOWNWARD),
                            icon_button(ft.Icons.REDO),
                            icon_button(ft.Icons.UNDO),
                            icon_button(ft.Icons.COPY),
                            icon_button(ft.Icons.PASTE),
                            icon_button(ft.Icons.UPLOAD),
                            icon_button(ft.Icons.DOWNLOAD),
                            icon_button(ft.Icons.DELETE_FOREVER),
                            icon_button(ft.Icons.HELP),
                            icon_button(ft.Icons.SETTINGS),
                        ],
                        spacing=0,
                    ),
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                self.input_text,
                                # icon_button(ft.Icons.MIC),
                                icon_button(ft.Icons.MIC_OFF),
                                icon_button(ft.Icons.MENU),
                            ],
                            spacing=0,
                        ),
                        border=ft.border.all(1, ft.Colors.OUTLINE),
                        padding=2,
                    ),
                    ft.Text(
                        'ローマ字入力してください。改行で確定、バックスペースで１文字削除。左右上下矢印キーで移動します',
                        size=12,
                        style=ft.TextStyle(italic=True),
                    ),
                ],
                spacing=4,
            ),
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=5,
            padding=8,
        )
        """

        lower_container = ft.Container(
            content=self.output_listview,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=5,
            padding=10,
            expand=True,
        )

        layout = ft.Column(
            controls=[
                top_container,
                upper_container, 
                # menu_container,
                lower_container
            ],
            expand=True 
        )

        page.on_keyboard_event = on_keyboard_event
        page.add(layout)

    def set_input(self, before, after):

        if not before and not after:
            self.input_text.spans = [
                ft.TextSpan(
                    'ひらがなを入力してください',
                    style=ft.TextStyle(
                        color='grey',
                    )
                )
            ]
            ft.TextSpan(after),
            self.input_text.update()  
            return

        # box_len = int(self.page.width / 17) - 3 # heyristic
        box_len = int(self.page.width / 16) - 10 # heyristic
        before_len = len(before)
        after_len = len(after)
        excess_len = before_len + after_len - box_len
        if excess_len > 0:
            after_len = min(after_len, int(excess_len/2))
            before_len = min(before_len, box_len - after_len)
            after = after[:box_len - before_len]
            before = before[-before_len:]

        self.input_text.spans = [
            ft.TextSpan(before),
            ft.TextSpan(
                '|',
                style=ft.TextStyle(
                    color='blue',
                    letter_spacing=-2,
                    weight='bold'
                ),
            ),  # 縦棒
            ft.TextSpan(after),
        ]
        self.input_text.update()  

    def set_output(self, lines, lineno):

        with self.lock:
            if not lines:
                self.output_listview.controls.clear()
                ft_container = ft.Container(
                    content=ft.Text(
                        'ここに結果が表示されます', 
                        color='grey',
                        size=20
                    ),
                    expand=True,
                    # bgcolor=bgcolor
                )
                self.output_listview.controls.append(ft_container)
                self.output_listview.update() 
                return

            self.output_listview.controls.clear()
            for current_lineno, line in enumerate(lines):
                if line.key == None:
                    continue

                output_text = line.output_text + line.postfix()
                output_text = output_text.rstrip()
                # bgcolor = ft.Colors.BLUE_50 if lineno == current_lineno else None
                bgcolor = ft.Colors.INDIGO_500 if lineno == current_lineno else None

                ft_container = ft.Container(
                    content=ft.Text(output_text, size=20),
                    expand=True,
                    bgcolor=bgcolor
                )
                self.output_listview.controls.append(ft_container)

            # self.page.update() # temporary
            self.output_listview.update() 

if __name__ == "__main__":

    def main(page):
        viewer = FtViewer()
        viewer.start(page)

        viewer.set_input('Hello world')

        lines = [BackendLine()] * 4
        lines[0].output_text = 'Hello world'
        lines[1].output_text = 'Hello world'
        lines[2].output_text = 'Hello world'
        lines[3].output_text = 'Hello world'

        viewer.set_output(lines, 1)
        page.update()
    ft.app(target=main)
