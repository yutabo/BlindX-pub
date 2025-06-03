import re
import sys

def is_valid_japanese(name):
    return bool(re.search(r'[一-龯ぁ-んァ-ン]', name)) and not re.fullmatch(r'[？＠\W_]+', name)

def extract_names_from_file(file_path):
    names = set()
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            matches = re.findall(r'［(.+?)］', line)
            for match in matches:
                if '＠' in match:
                    parts = match.split('＠')
                elif '　' in match:
                    parts = match.split('　')
                elif ' ' in match:
                    parts = match.split(' ')
                else:
                    parts = [match.strip()]

                for part in parts:
                    part = part.strip()
                    if 'の' in part:
                        # 例：「春樹のマミヤ」→「春樹」「マミヤ」
                        subparts = part.split('の')
                        for sub in subparts:
                            sub = sub.strip()
                            if is_valid_japanese(sub):
                                names.add(sub)
                    else:
                        if is_valid_japanese(part):
                            names.add(part)
    return names

def main(file_paths):
    all_names = set()
    for path in file_paths:
        all_names.update(extract_names_from_file(path))

    print(' '.join(sorted(all_names)))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使い方: python extract_names.py ファイル1 ファイル2 ...")
    else:
        main(sys.argv[1:])

