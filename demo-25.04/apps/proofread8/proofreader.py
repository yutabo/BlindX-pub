# MIT License (c) 2024, 2025 Masakazu Suzuoki, AxTecChare
# See LICENSE.txt for details.

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import asyncio
from blindx.kanhira import Kanhira
from blindx.remote_inference import RemoteInference
from rapidfuzz import fuzz
import jaconv
import MeCab
import difflib


import unicodedata
import re
from difflib import SequenceMatcher

BLUE = '\033[38;5;25m'         # 青系前景（.ansi21 相当）
CYAN = '\033[36m'            # シアン 校正の入ったもとテキスト
YELLOW = '\033[38;5;226m'    # 黄色　校正箇所
SOFT_YELLOW = '\033[38;5;143m'
RED = '\033[31m'
BOLD = '\033[1m'
BOLD_RED = '\033[31;1m'  # 太字・赤
RESET = '\033[0m'
RESUME = '\033[39m'  #色を標準色に

def normalize_ellipsis(text: str) -> str:
    # 半角ピリオド3つ以上 → 全角三点リーダ（U+2026）に置換（2つ連続に統一）
    import re
    return re.sub(r'\.{3,}', '……', text)

def normalize_and_compare(a, b):
#    print(f' normalize and compare :  IN1:{a}  IN2:{b}') 
    a_norm = unicodedata.normalize('NFKC', a)
    b_norm = unicodedata.normalize('NFKC', b)
    return a_norm == b_norm

def normalize_punctuation(text):
    # 「…」を「.」に変換、「。」はそのまま
    text = text.replace('…', '.')
    # 「.」が連続している箇所を「...」に正規化（長さ統一）
    text = re.sub(r'\.{2,}', '...', text)
    return text


def is_similar(text1, text2, threshold=0.9):
    norm1 = normalize_punctuation(text1)
    norm2 = normalize_punctuation(text2)
    # 類似度計算
    similarity = SequenceMatcher(None, norm1, norm2).ratio()
    return similarity >= threshold, similarity

def normalize_text(text):
    text = remove_scores(text)
    text = jaconv.z2h(text, kana=False, digit=True, ascii=True)    
    text = jaconv.kata2hira(text)  # 任意
    return re.sub(r'[！？!?\。、．「」（）『』［］【】…‥・ー"\'\s]', '', text)

import MeCab
import platform
import os

def get_mecab_dic_path():
    if platform.system() == 'Windows':
        return "C:/msys64/mingw64/lib/mecab/dic/mecab-ipadic-neologd"
    elif platform.system() == 'Darwin':  # macOS
        return '/opt/homebrew/lib/mecab/dic/mecab-ipadic-neologd'
    else:
        raise RuntimeError("Unsupported OS")


# 🔽 グローバル変数として定義
DIC_PATH = get_mecab_dic_path()
# （任意）存在チェックも入れると安心
if not os.path.exists(os.path.join(DIC_PATH, "dicrc")):
    raise FileNotFoundError(f"MeCab辞書が見つかりません: {DIC_PATH}")

import re

def remove_scores(text):
    # スコア（,1.00など）を削除
    text = re.sub(r',\d+(?:\.\d+)?', '', text)
    # カンマ自体も除去（語と語の間をつなげる）
    return text.replace(',', '')

def parse_blindx_texts(blindx_texts):
    """
    blindx_texts 形式:
    例: T,1.00,he,1.00,B,1.00,e,1.00,... : トークンとスコアがカンマで交互に並んでいる
    コロン : でビームごとに区切られている

    戻り値: ["TheBeginning", "TheBegin", ...] のようなテキストリスト
    """
    outputs = blindx_texts.split(':')
    texts = []
    for output in outputs:
        items = output.split(',')
        tokens = items[::2]  # 偶数番目がトークン
        text = ''.join(tokens)
        texts.append(text)
    return texts


def check_chunk_match(pr):
#    dic_path = get_mecab_dic_path()
#    if not os.path.exists(os.path.join(dic_path, "dicrc")):
#        raise FileNotFoundError(f"MeCab辞書が見つかりません: {dic_path}")

    try:
        
#        wakati_tagger = MeCab.Tagger("-Owakati")
        wakati_tagger = MeCab.Tagger(f"-Owakati -d {DIC_PATH}") 
#        wakati_tagger = MeCab.Tagger("-Owakati -d /opt/homebrew/lib/mecab/dic/mecab-ipadic-neologd")
        norm_input = normalize_text(pr.input_text)
        input_chunks = wakati_tagger.parse(norm_input)

        if input_chunks is None:
            raise ValueError("MeCab parse returned None for input")

        input_chunks = input_chunks.strip().split()
#        print(f"[DEBUG] input chunks: {input_chunks}")

        # 全ての output_text を1つにまとめて分かち書きし、結合
        all_output_chunks = []
        for output_text, _ in pr.output_texts:
            norm_output = normalize_text(output_text)
            out_chunks = wakati_tagger.parse(norm_output)
            if not out_chunks:
                continue
            out_chunks = out_chunks.strip().split()
            all_output_chunks.extend(out_chunks)

        joined_output = ''.join(all_output_chunks)
#        print(f"[DEBUG] joined all output = {joined_output}")

        unmatched_chunks = [chunk for chunk in input_chunks if chunk not in joined_output]

        if not unmatched_chunks:
#            print(f"[DEBUG] ✅ chunk_match 成立")
            return True, []
        else:
#            print(f"[DEBUG] ❌ unmatched chunks: {unmatched_chunks}")
            return False, unmatched_chunks  # マッチ失敗、unmatched のリスト付き

    except Exception as e:
        print(f"[ERROR] MeCab chunk_match failed: {e}")
        return False


class Proofreader():

    def __init__(self):
        self.kanhira = Kanhira()
        self.inference = RemoteInference()
        self.output_texts = []
        
        dic_path = get_mecab_dic_path()
        if not os.path.exists(os.path.join(dic_path, "dicrc")):
            raise FileNotFoundError(f"MeCab辞書が見つかりません: {dic_path}")

#        self.wakati_tagger = MeCab.Tagger("-Owakati")
        wakati_tagger = MeCab.Tagger(f"-Owakati -d {DIC_PATH}") 
#        wakati_tagger = MeCab.Tagger("-Owakati -d /opt/homebrew/lib/mecab/dic/mecab-ipadic-neologd")
#        print(f'[DEBUG] Neologd Start ')
        self.passed_index = 0

    @property
    def t5_names(self):
        return self.inference.t5_names

    
    async def start_async(self):
        await self.inference.start_async()
#        self.dict_names = await self.inference.send_recv_async('query:', 'dict_names')

        # dict_namesを取得して split(':') でリストに変換
        raw_dict_names = await self.inference.send_recv_async('query:', 'dict_names')
        self.dict_names = raw_dict_names.split(':')
        self.dict_count = len(self.dict_names)  # ✅ ←これでOK        
#        print("[DEBUG] dict_names =", self.dict_names)
        self.dict_count = len(self.dict_names)
#        self.dict_count = len(self.dict_names.split(':'))

    async def shutdown_async(self):
        await self.inference.shutdown_async()
        
    def concat_output_text(self, output_text):
        items = output_text.split(',')
        tokens = items[::2]
        probs = items[1::2]
        result_text = ''.join(tokens)
        return jaconv.h2z(result_text, ascii=True, digit=True)


    # 文節一致判定：output_texts の中に input_text の文節をすべて含むものが一つでもあるか？
    def get_score(self, zenkaku_output_text):
        chunk_match = False
        try:
            # 入力の存在チェックと前処理
            if self.zenkaku_input_text is None:
                raise ValueError("zenkaku_input_text が None です")
            if zenkaku_output_text is None:
                raise ValueError("zenkaku_output_text が None です")

            input_text = self.zenkaku_input_text.strip()
            output_text = zenkaku_output_text.strip()

            norm_input = normalize_ellipsis(input_text)
            norm_output = normalize_ellipsis(output_text)

#            print(f"[DEBUG:get_score] input = {repr(input_text)}")
#            print(f"[DEBUG:get_score] output = {repr(output_text)}")

            # 完全一致の場合は即座に100点
            if norm_input == norm_output:
#                print("[DEBUG:get_score] 完全一致 → score=100")
                return 100, True



            # 類似度スコアの計算
            try:
                overall_score = fuzz.ratio(norm_input, norm_output)
#                print(f"[DEBUG:get_score] fuzzy score = {overall_score}")
            except Exception as e:
#                print(f"[ERROR] fuzz.ratio failed: {e}")
                raise

            # 文節一致チェック（MeCab）
            try:
                #wakati_tagger = MeCab.Tagger("-Owakati")
                wakati_tagger = MeCab.Tagger(f"-Owakati -d {DIC_PATH}") 
#                wakati_tagger = MeCab.Tagger("-Owakati -d /opt/homebrew/lib/mecab/dic/mecab-ipadic-neologd")
                orig_chunks = wakati_tagger.parse(norm_input)
                out_chunks = wakati_tagger.parse(norm_output)

                if orig_chunks is None or out_chunks is None:
                    raise ValueError("MeCab parse returned None")

                orig_chunks = orig_chunks.strip().split()
                out_chunks = out_chunks.strip().split()
                chunk_match = len(set(orig_chunks) & set(out_chunks)) > 0
            except Exception as e:
                print(f"[ERROR] MeCab parse failed: {e}")
                chunk_match = False

 #           print(f"[DEBUG:get_score] returning score = {overall_score}, chunk_match = {chunk_match}")
            return overall_score, chunk_match

        except Exception as e:
            print(f"[ERROR] get_score 内部エラー: {e}")
            raise

    
    def all_input_chunks_matched_old(self, input_text, output_texts):
        input_chunks = self.wakati_tagger.parse(input_text).strip().split()
        input_chunks = [normalize_text(chunk) for chunk in input_chunks if chunk.strip()]

        # 出力側の merged text 群をすべて正規化して用意
        merged_outputs = [
            normalize_text(remove_scores(output_text))
            for output_text, _ in output_texts
        ]

        # 各 chunk が出力群のどれか1つに含まれているか確認
        unmatched_chunks = []
        for chunk in input_chunks:
            if not any(chunk in merged for merged in merged_outputs):
#                print(f"[DEBUG] unmatched chunk: '{chunk}'")
                unmatched_chunks.append(chunk)

        if unmatched_chunks:
#            print(f"[DEBUG] unmatched chunks: {unmatched_chunks}")
            return False

#        print(f"[DEBUG] all chunks matched in some output")
        return True


    import difflib

    def highlight_unmatched_chunks(self, input_text, unmatched_chunks):
        highlighted = input_text
        for chunk in unmatched_chunks:
            # chunk が複数回出る可能性があるため、すべて置換（最初のだけなら 1 を指定）
            highlighted = highlighted.replace(chunk, f"{SOFT_YELLOW}{chunk}{CYAN}")
        return highlighted
    
    def highlight_diff(self,a, b):
        matcher = difflib.SequenceMatcher(None, a, b)
        result = []
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                result.append(a[i1:i2])
            elif tag == 'replace' or tag == 'delete':
                result.append(f'{SOFT_YELLOW}{a[i1:i2]}{RED}')
                # 'insert' は A にはない部分なので無視
        return ''.join(result)
            
    async def test_async(self, input_text, dict_index, num_beams=2):
        self.input_text = input_text
        self.output_texts = []

        if(input_text == ''):   #何もないものを放り込むとエラーになるため
            return []

        try:
            # 入力の前処理（コロンのエスケープなど）
            escaped_input_text = input_text.replace(':', '<COLON>')
            self.hiragana_text = self.kanhira.convert(escaped_input_text)
            self.zenkaku_input_text = jaconv.h2z(input_text, ascii=True, digit=True)

            # モデル呼び出し
            dict_cmd = f'T{dict_index}:{num_beams}+:'
            blindx_texts = await self.inference.send_recv_async(dict_cmd, self.hiragana_text)

            # パース
            parsed_outputs = parse_blindx_texts(blindx_texts)
            if not parsed_outputs:
                print(f"[WARN] 出力なし: dict={self.dict_names[dict_index]}")
                return []

            # 出力整形
            for output_text in parsed_outputs:
                if not output_text or output_text.strip().startswith("<pad>"):
#                    print(f"[SKIP] 無効出力（padのみ？）: dict={self.dict_names[dict_index]}, chunk={input_text[:30]}")
                    continue
                output_text = output_text.replace('<COLON>', ':')
                self.output_texts.append((output_text, self.dict_names[dict_index]))
                
            return self.output_texts

        except Exception as e:
            print(f"[ERROR] test_async failed: {e}")
            return []

    async def set_pattern_async(self, pattern):
        self.kanhira.set_pattern(pattern)
        await self.inference.send_recv_async('set:wrapper_pattern:', pattern)

    async def set_replacement_async(self, replacement):
        self.kanhira.set_replacement(replacement)
        await self.inference.send_recv_async('set:wrapper_replacement:', replacement)


from ansi2html import Ansi2HTMLConverter

def save_colored_output_as_html(ansi_text: str, output_html_path: str):
    conv = Ansi2HTMLConverter()
    html = conv.convert(ansi_text, full=True)
    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(html)

