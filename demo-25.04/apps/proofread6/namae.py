import sys
import re

honorifics = ['さん', 'ちゃん', '君', 'くん', '様', 'さま']
blacklist = {'お母さん', 'お父さん', 'お兄ちゃん', 'お姉ちゃん', '猫さん', '看護師さん',
             '車掌さん', '神様', 'おじいさん', 'おばあさん', '患者さん'}

def remove_honorific(word):
    for h in honorifics:
        if word.endswith(h):
            return word[:-len(h)]
    return word

def is_name(word):
    return re.fullmatch(r'[一-龯ァ-ヶー]{2,4}', word)  # 漢字 or カタカナ2〜4文字

def extract_clean_names(filename):
    with open(filename, encoding="utf-8") as f:
        text = f.read()

    # 句読点や記号で分割して単語ごとに見る
    tokens = re.split(r'[、。！？「」（）・\s\n\r]+', text)

    result = set()

    for token in tokens:
        for h in honorifics:
            if token.endswith(h) and len(token) > len(h):
                if token in blacklist:
                    continue
                name = remove_honorific(token)
                if is_name(name):
                    result.add(name)

    return sorted(result)

def main():
    if len(sys.argv) < 2:
        print("使い方: python namae_clean.py <ファイル名>")
        return
    filename = sys.argv[1]
    names = extract_clean_names(filename)
    print(" ".join(names))

if __name__ == "__main__":
    main()


