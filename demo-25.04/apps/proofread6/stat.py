import sys
import re
import unicodedata
from pathlib import Path

def display_width(text):
    """全角2、半角1として表示幅を計算"""
    return sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in text)

def pad_to_width(text, width):
    """指定された見た目幅に左詰めでパディング"""
    pad = width - display_width(text)
    return text + ' ' * max(0, pad)

def extract_counts(filepath):
    fail = pass_ = 0
    with open(filepath, encoding='utf-8') as f:
        for line in f:
            if "FAIL COUNT" in line:
                line = re.sub(r'<[^>]+>', '', line)  # HTMLタグを削除
                m = re.search(r'FAIL COUNT\s*:\s*(\d+)\s+PASS COUNT\s*:\s*(\d+)', line)
                if m:
                    fail = int(m.group(1))
                    pass_ = int(m.group(2))
    return fail, pass_

def main():
    files = sys.argv[1:]
    if not files:
        print("使い方: python stat.py file1.html file2.html ...")
        return

    NAME_COL_WIDTH = 40
    total_fail = total_pass = 0

    print(f"{pad_to_width('ファイル名', NAME_COL_WIDTH)} {'FAIL':>6} {'PASS':>6} {'PASS率':>7}")
    print("-" * (NAME_COL_WIDTH + 6 + 6 + 7 + 3))

    for filepath in files:
        fail, pass_ = extract_counts(filepath)
        total_fail += fail
        total_pass += pass_
        total = fail + pass_
        ratio = (pass_ / total * 100) if total else 0.0

        filename = Path(filepath).name
        print(f"{pad_to_width(filename, NAME_COL_WIDTH)} {fail:>6} {pass_:>6} {ratio:6.2f}%")

    grand_total = total_fail + total_pass
    overall_ratio = (total_pass / grand_total * 100) if grand_total else 0.0
    print("-" * (NAME_COL_WIDTH + 6 + 6 + 7 + 3))
    print(f"{pad_to_width('合計', NAME_COL_WIDTH)} {total_fail:>6} {total_pass:>6} {overall_ratio:6.2f}%")

if __name__ == "__main__":
    main()
