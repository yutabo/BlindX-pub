# MIT License (c) 2024, 2025 Masakazu Suzuoki, AxTecChare
# See LICENSE.txt for details.

# 日本語キーボード配列に基づくキーコードと文字の対応マップ
KEY_MAP = {
    # 数字キー（Shift 無し / Shift 有り）
    "1": ("1", "!"),
    "2": ("2", "\""),
    "3": ("3", "#"),
    "4": ("4", "$"),
    "5": ("5", "%"),
    "6": ("6", "&"),
    "7": ("7", "'"),
    "8": ("8", "("),
    "9": ("9", ")"),
    "0": ("0", ""),

    # アルファベットキー（Shift 無し / Shift 有り）
    "A": ("a", "A"),
    "B": ("b", "B"),
    "C": ("c", "C"),
    "D": ("d", "D"),
    "E": ("e", "E"),
    "F": ("f", "F"),
    "G": ("g", "G"),
    "H": ("h", "H"),
    "I": ("i", "I"),
    "J": ("j", "J"),
    "K": ("k", "K"),
    "L": ("l", "L"),
    "M": ("m", "M"),
    "N": ("n", "N"),
    "O": ("o", "O"),
    "P": ("p", "P"),
    "Q": ("q", "Q"),
    "R": ("r", "R"),
    "S": ("s", "S"),
    "T": ("t", "T"),
    "U": ("u", "U"),
    "V": ("v", "V"),
    "W": ("w", "W"),
    "X": ("x", "X"),
    "Y": ("y", "Y"),
    "Z": ("z", "Z"),
}

def getchar_from_key(key, shift):
    try:
        return KEY_MAP[key][int(shift)]
    except KeyError:
        return key

