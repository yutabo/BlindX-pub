import sys
import glob
from pathlib import Path
from collections import Counter
import chardet
import MeCab

def robust_read_text(path):
    """文字コードを自動判別してテキストを読み込む"""
    raw = Path(path).read_bytes()
    detected = chardet.detect(raw)
    encoding = detected.get("encoding", "utf-8")

    try:
        return raw.decode(encoding)
    except (UnicodeDecodeError, LookupError):
        return raw.decode("utf-8", errors="ignore")

def extract_hotwords(text):
    """MeCabで固有名詞・一般名詞だけを抽出"""
#    tagger = MeCab.Tagger("-Ochasen")  # または -Owakati でも可（出力形式変わる）
    tagger = MeCab.Tagger()
    node = tagger.parseToNode(text)
    words = []
    while node:
        surface = node.surface
        features = node.feature.split(',')
        if features[0] == '名詞' and features[1] in ['固有名詞', '一般']:
            words.append(surface)
        node = node.next
    return words

def generate_hotwords_from_files(filepaths, min_count=3):
    """複数ファイルからhotwordsを抽出"""
    all_words = []
    for filepath in filepaths:
        try:
            text = robust_read_text(filepath)
            words = extract_hotwords(text)
            all_words.extend(words)
        except Exception as e:
            print(f"⚠️ 読み込み失敗: {filepath} → {e}")
            continue

    counter = Counter(all_words)
    hotwords = [word for word, count in counter.items() if count >= min_count]
    return hotwords

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使い方: python hottool.py 入力ファイル1.txt [入力ファイル2.txt ...]")
        sys.exit(1)

    file_paths = []
    for arg in sys.argv[1:]:
        file_paths.extend(glob.glob(arg))

    if not file_paths:
        print("❌ 有効なファイルが見つかりません")
        sys.exit(1)

    hotwords = generate_hotwords_from_files(file_paths, min_count=3)
    for word in sorted(hotwords):
        print(word)

