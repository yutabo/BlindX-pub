# MIT License (c) 2024, 2025 Masakazu Suzuoki, AxTecChare
# See LICENSE.txt for details.


import flet as ft
from difflib import SequenceMatcher

class FtColorSpans(list):
    def __init__(self, output_text, prev_output_text, postfix, is_color=True):
        super().__init__()

        if is_color:
            self += self.compare_strings(output_text, prev_output_text) 
            if postfix:
                self.append(ft.TextSpan(postfix))

        else:        
            style = ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE)
            self.append(ft.TextSpan(output_text + postfix, style=style))

    def compare_strings(self, str1, str2):
        matcher = SequenceMatcher(None, str1, str2)
        spans = []
        bold = ft.FontWeight.BOLD
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                spans.append(ft.TextSpan(str1[i1:i2], style=ft.TextStyle(color='black', weight=bold)))
            elif tag == 'replace':
                spans.append(ft.TextSpan(str1[i1:i2], style=ft.TextStyle(color='red', weight=bold)))
            elif tag == 'delete':
                spans.append(ft.TextSpan(str1[i1:i2], style=ft.TextStyle(color='green', weight=bold)))
            elif tag == 'insert':
                spans.append(ft.TextSpan(str2[j1:j2], style=ft.TextStyle(color='blue', weight=bold)))

        return spans

class FtColorSpansSimple(list):
    def __init__(self, str1, str2):
        super().__init__()
        self += self.compare_strings(str1, str2)

    def compare_strings(self, str1, str2):
        matcher = SequenceMatcher(None, str1, str2)
        spans = []
        bold = ft.FontWeight.BOLD

        styleA = ft.TextStyle(color='blue')
        styleB = ft.TextStyle(color='blue', weight=ft.FontWeight.BOLD, decoration=ft.TextDecoration.UNDERLINE)

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                spans.append(ft.TextSpan(str1[i1:i2], style=styleA))
            elif tag == 'replace':
                spans.append(ft.TextSpan(str1[i1:i2], style=styleB))
            elif tag == 'delete':
                spans.append(ft.TextSpan(str1[i1:i2], style=styleB))
            elif tag == 'insert':
                spans.append(ft.TextSpan(str2[j1:j2], style=styleB))

        return spans

class FtColorSpansSimple2(list):
    def __init__(self, str1, str2):
        super().__init__()
        self += self.compare_strings(str1, str2)

    def compare_strings(self, str1, str2):

        styleA = ft.TextStyle()
        styleB = ft.TextStyle(color='blue', decoration=ft.TextDecoration.UNDERLINE)
        spans = []

        if not str2:
            spans.append(ft.TextSpan(str1, style=styleA))
        else:    
            matcher = SequenceMatcher(None, str1, str2)
            for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                if tag == 'equal':
                    spans.append(ft.TextSpan(str1[i1:i2], style=styleA))
                elif tag == 'replace':
                    spans.append(ft.TextSpan(str1[i1:i2], style=styleB))
                elif tag == 'delete':
                    spans.append(ft.TextSpan(str1[i1:i2], style=styleB))
                elif tag == 'insert':
                    spans.append(ft.TextSpan(str2[j1:j2], style=styleB))
            
        return spans

