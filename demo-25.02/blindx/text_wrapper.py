import re
class TextWrapper:
    def __init__(self, pattern = r'`.*?`', replacement='\\E'):
        self.pattern = re.compile(pattern)  # 正規表現をコンパイル
        self.replacement = replacement

    def encode(self, text):
        self.matches = []  # マッチした部分を格納するリスト

        def replacer(match):
            self.matches.append(match.group(0))  # マッチ部分を保存
            return self.replacement  # 置換後の文字列を返す

        modified_text = self.pattern.sub(replacer, text)
        return modified_text.replace('\n', '\\n')

    def decode(self, modified_text):
        if not hasattr(self, 'matches'):
            raise ValueError("encode() をよびだして matches をせいせいしてください。")

        result = []
        match_iter = iter(self.matches)  # マッチ部分のリストをイテレータ化
        parts = modified_text.replace('\\n', '\n').replace(' ', '').split(self.replacement)
        for i, part in enumerate(parts):
            result.append(part)
            if i < len(parts) - 1:
                result.append(next(match_iter, self.replacement))  # プレースホルダーを戻す

        return ''.join(result)
