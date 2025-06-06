import sys
import re
import glob
import MeCab
import chardet
from collections import Counter

#MECAB_ARGS = '-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd'
MECAB_ARGS = '-d /opt/homebrew/lib/mecab/dic/mecab-ipadic-neologd'
KEISHO = ['さん', '君', '様', 'ちゃん', 'くん']

def read_text_auto_encoding(filepath):
    with open(filepath, 'rb') as f:
        raw = f.read()
    detected = chardet.detect(raw)
    try:
        return raw.decode(detected['encoding'] or 'utf-8')
    except:
        print(f"❌ Failed to decode {filepath} with {detected['encoding']}")
        return ""

def extract_named_entities(text):
    tagger = MeCab.Tagger(MECAB_ARGS)
    tagger.parse("")  # MeCab バグ回避

    node = tagger.parseToNode(text)
    words = []
    previous_surface = ""
    previous_features = []

    while node:
        surface = node.surface
        features = node.feature.split(',')

        if (
            len(features) > 2 and
            features[0] == "名詞" and
            features[1] == "固有名詞" and
            features[2] in ["人名", "地域", "組織"]
        ):
            words.append(surface)

        if surface in KEISHO and previous_surface:
            if (
                len(previous_surface) >= 2 and
                previous_features and
                previous_features[0] == "名詞"
            ):
                words.append(previous_surface)

        previous_surface = surface
        previous_features = features
        node = node.next

    return words

def is_valid_hotword(word, all_words):
    if not word:
        return False
    if re.fullmatch(r'[ぁ-んー]+', word):   return False
#    if re.fullmatch(r'[ぁ-ん]{1,2}', word): return False
    if re.fullmatch(r'[ァ-ヶー]{1}', word): return False
    if re.fullmatch(r'[a-zA-ZＡ-Ｚａ-ｚ]{1,3}', word): return False
    # 一文字漢字で他に含まれている
    if re.fullmatch(r'[一-龯]', word):
        for other in all_words:
            if other != word and word in other:
                return False
    # 感嘆詞や句読点などの記号（！、…。など）
    if re.search(r'[。、．・…！!？?]', word):
        return False
    # よくある代名詞的な語
    NG_WORDS = {'その子', 'その人', 'この子', 'あの人', 'な！', 'なぁ', 'ふーん', 'へえ', 'うん', 'はい', 'いいえ', 'わー'}
    if word in NG_WORDS:
        return False

    return True

def main():
    all_text = ""
    for pattern in sys.argv[1:]:
        for file in glob.glob(pattern):
            text = read_text_auto_encoding(file)
            if text:
#                print(f"\n📂 Reading: {file}")
                all_text += text + "\n"

    raw_words = extract_named_entities(all_text)
#    print(f"\n📋 抽出された固有名詞候補: {raw_words}")

    count = Counter(raw_words)
    filtered = [w for w in count if count[w] >= 3 and is_valid_hotword(w, count)]
    filtered = sorted(set(filtered))

    with open("hotwords.txt", "w", encoding="utf-8") as f:
        for word in filtered:
            f.write(word + "\n")

    print(f"\n✅ {len(filtered)} hotwords extracted to hotwords.txt")




    if filtered:
        print("📄 抽出結果:", filtered)

if __name__ == "__main__":
    main()
