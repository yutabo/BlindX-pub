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

def normalize_text(text):
    text = remove_scores(text)
    text = jaconv.z2h(text, kana=False, digit=True, ascii=True)    
    text = jaconv.kata2hira(text)  # 任意
    return re.sub(r'[！？!?\。、．「」（）『』［］【】…‥・ー"\'\s]', '', text)

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


class Proofreader():

    def __init__(self):
        self.kanhira = Kanhira()
        self.inference = RemoteInference()
        self.output_texts = []        
        self.wakati_tagger = MeCab.Tagger("-Owakati") 
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

    def get_score(self, zenkaku_output_text):
        overall_score = fuzz.ratio(self.zenkaku_input_text, zenkaku_output_text)
#        print(f' zenkaku output text : {zenkaku_output_text}')
#        print(f' zenkaku input text : {self.zenkaku_input_text}') 

        wakati_tagger = MeCab.Tagger("-Owakati")
        orig_chunks = wakati_tagger.parse(self.zenkaku_input_text).strip().split()
        out_chunks = wakati_tagger.parse(zenkaku_output_text).strip().split()  
        chunk_matched = len(set(orig_chunks) & set(out_chunks)) > 0
#        print(f' overall score : {overall_score}  chunk_matched = {chunk_matched}')

        self.last_score = overall_score  # ← スコアを保持
        self.last_chunk_match = chunk_matched  # ← 必要なら文節一致も

#        print(f'overall score : {overall_score}  chunk_matched = {chunk_matched}')
        return overall_score, chunk_matched

    def all_input_chunks_matched(self, input_text, output_texts):
        input_chunks = self.wakati_tagger.parse(input_text).strip().split()
        input_chunks = [normalize_text(chunk) for chunk in input_chunks if chunk.strip()]
        self.unmatched_chunks = []
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
            self.unmatched_chunks = unmatched_chunks
            return False

#        print(f"[DEBUG] all chunks matched in some output")
        return True


    import difflib
    import MeCab

    def highlight_diff(self, a, b):
        RED = '\033[31m'
        RED_BOLD = '\033[1;31m'
        RESET = '\033[0m'

        unmatched_chunks = self.unmatched_chunks
        final_output = a

        # ANSIコードの後処理として BOLD を追加（文字列レベル）
        for chunk in unmatched_chunks:
            final_output = final_output.replace(chunk, f"{RED_BOLD}{chunk}{RESET}")
        return final_output


    async def test_async(self, input_text, dict_index, num_beams = 2):
#        print(f"[DEBUG] raw input_text: {input_text}")
        self.input_text = input_text
#        self.hiragana_text = self.kanhira.convert(input_text)
        escaped_input_text = input_text.replace(':', '<COLON>')
        self.hiragana_text = self.kanhira.convert(escaped_input_text)
        self.zenkaku_input_text = jaconv.h2z(input_text, ascii=True, digit=True)
#        print(f"[DEBUG] hiragana_text: {self.input_text}")
        dict_cmd = f'T{dict_index}:{num_beams}+:'
        blindx_texts = await self.inference.send_recv_async(dict_cmd, self.hiragana_text)
#        print(f"[DEBUG] blindx_texts = {blindx_texts}") 
#        output_texts = blindx_texts.split(':')
#        print(f"[DEBUG] 辞書名 = {self.dict_names[dict_index]}")
        parsed_outputs = parse_blindx_texts(blindx_texts)

        for output_text in parsed_outputs:  # ← こちらに直す
            output_text = output_text.replace('<COLON>', ':')
            self.output_texts.append((output_text, self.dict_names[dict_index]))
            zenkaku_output_text = self.concat_output_text(output_text)
            score, _ = self.get_score(zenkaku_output_text)
        if score == 100:
            result = True
            self.passed_index += 1

#        for output_text in output_texts:
#            self.output_texts.append((output_text, f'T{dict_index}'))

        # ❌ return result はやめる（ここで判定しない）


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

