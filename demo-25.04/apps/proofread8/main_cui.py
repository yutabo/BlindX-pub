#@title かな漢字変換テスト
# MIT License (c) 2024, 2025 Masakazu Suzuoki, AxTecChare
# See LICENSE.txt for details.

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


import asyncio
import blindx.misc as misc
from proofreader import Proofreader
from proofreader import check_chunk_match
import argparse
from tqdm import tqdm
import logging
import re
import io
import jaconv
import unicodedata
import difflib

BLUE = '\033[38;5;25m'         # 青系前景（.ansi21 相当）
CYAN = '\033[36m'            # シアン 校正の入ったもとテキスト
YELLOW = '\033[38;5;226m'    # 黄色　校正箇所
SOFT_YELLOW = '\033[38;5;143m'
RED = '\033[31m'
BOLD = '\033[1m'
BOLD_RED = '\033[31;1m'  # 太字・赤
RESET = '\033[0m'
RESUME = '\033[39m'  #色を標準色に

SCORE_THRESHOLD = 40  # ← 好みに応じて調整可能（60とかでも可）

def normalize(text):
    return unicodedata.normalize("NFKC", text.strip())

def split_output_text(output_text: str, expected_lines: int):
    if output_text.count('\\n') >= expected_lines - 1:
        # 改行数が十分ある場合は \\n で分割
        return output_text.split('\\n')
    else:
        # 改行数が不足している場合は句点で分割
        lines = re.split(r'(?<=。)', output_text)
        return [line.strip() for line in lines if line.strip()]

def make_numbered_input(lines):
    """入力行に 1: 文… という形式で番号を振って連結する"""
    return "\n".join(f"{i+1}: {line}" for i, line in enumerate(lines))

import re

def extract_numbered_output(output_text: str, expected_lines: int):
    """
    '1: ...\\n2: ...\\n3: ...' のような出力を、行ごとのリストに変換
    """
    matches = re.findall(r'\d+\s*:\s*.*?(?=\n\d+\s*:|$)', output_text, flags=re.DOTALL)
    lines = [re.sub(r'^\d+\s*:\s*', '', m).strip() for m in matches]

    # 行数補正
    if len(lines) < expected_lines:
        lines += [''] * (expected_lines - len(lines))
    elif len(lines) > expected_lines:
        lines = lines[:expected_lines]

    return lines


if __name__ == "__main__":

    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='source filename', default='input.txt')
    parser.add_argument('-o', '--output', help='result filename', default='-')
    parser.add_argument('-e', '--echo', help='phrase')
    parser.add_argument('--hotwords', help='スペース区切りでHOTWORDSを指定（省略可能）', default='') 
    #    parser.add_argument('--encoding', choices=['utf-8', 'utf-16-le'], default='utf-8', help='text encoding') 
    #    parser.add_argument('--hotwords', nargs='+', help='hot words')
    parser.add_argument('--encoding', default='auto', help='text encoding (e.g., utf-8, utf-16-le, or auto)')
    parser.add_argument('--hotfile', help='hot file')
    parser.add_argument('--max_chars', default=0, type=int, help='max chars　何文字詰め込むか')
    parser.add_argument('--num_beams', default=3, type=int, help='max beams : 何個候補を出すか')
    args = parser.parse_args()

    def chunk_lines_by_char_limit(lines, max_chars=None):
        if max_chars is None or max_chars <= 0:
            # max_charsが0以下なら、1文ごとにチャンク化
            return [([line], [idx]) for idx, line in enumerate(lines) if line.strip()] 

        chunks = []
        current_chunk = []
        current_length = 0
        current_indices = []

        for idx, line in enumerate(lines):
            line_length = len(line)

#            print(f'[DEBUG] line = {line[:30]}')
            
            # 最初の行は無条件に入れる
            if not current_chunk:
                current_chunk.append(line)
                current_indices.append(idx)
                current_length += line_length
                continue

            # max_chars が None（制限なし）なら常に追加
            if max_chars is None or current_length + line_length <= max_chars:
                current_chunk.append(line)
                current_indices.append(idx)
                current_length += line_length
            else:
                chunks.append((current_chunk.copy(), current_indices.copy()))
                current_chunk = [line]
                current_indices = [idx]
                current_length = line_length

        if current_chunk:
            chunks.append((current_chunk.copy(), current_indices.copy()))
        return chunks

    def chunk_lines_by_char_limit_old(lines, max_chars=None):
        if max_chars is None:
            max_chars = 256

        chunks = []
        current_chunk = []
        current_length = 0
        current_indices = []

        for idx, line in enumerate(lines):
            line_length = len(line)

            # チャンクが空（最初の行）なら、長さ無視で入れる
            if not current_chunk:
                current_chunk.append(line)
                current_indices.append(idx)
                current_length += line_length
                continue

            # 現在のチャンクに収まるなら追加
            if current_length + line_length <= max_chars:
                current_chunk.append(line)
                current_indices.append(idx)
                current_length += line_length
            else:
                # 入れたらオーバーするが、現在のチャンクが空なら強制的に入れる
                chunks.append((current_chunk.copy(), current_indices.copy()))
                current_chunk = [line]
                current_indices = [idx]
                current_length = line_length

        if current_chunk:
            chunks.append((current_chunk.copy(), current_indices.copy()))

        return chunks

    import chardet
    from pathlib import Path

    def read_lines(path_str, encoding='auto'):
        path = Path(path_str)
        raw = path.read_bytes()

        if encoding == 'auto':
            detected = chardet.detect(raw)
            encoding = detected.get('encoding') or 'utf-8'

        try:
            decoded = raw.decode(encoding)
        except UnicodeDecodeError:
            print(f"⚠️ decode error with {encoding}, fallback to utf-8 with ignore")
            decoded = raw.decode('utf-8', errors='ignore')

        return [line.lstrip('\ufeff') for line in decoded.splitlines()]

    def load_hotwords(filepath):
        path = Path(filepath)

        try:
            raw = path.read_bytes()
        except Exception as e:
            print(f"❌ hotfile 読み込み失敗: {filepath} → {e}")
            return []

        detected = chardet.detect(raw)
        encoding = detected.get("encoding") or "utf-8"

        try:
            text = raw.decode(encoding)
        except UnicodeDecodeError:
            print(f"⚠️ UnicodeDecodeError（{encoding}）→ fallback to utf-8(errors='ignore')")
            text = raw.decode("utf-8", errors="ignore")

        hotwords = text.strip().split()
        return hotwords
    
    async def main():
        misc.set_logger('kousei', logging.WARN)
        RED = '\033[31m'
        BOLD = '\033[1m'
        RESET = '\033[0m'

        hotwords = [
            ' ', '　', '、', ',', '…', '^◆.*$',
            '【.*?】', '［.*?］', '^◆.*$', '//.*$', '^;.*$',
        ]
        
        if args.hotwords:
            hotwords += args.hotwords
        if args.hotfile:
            hotwords += load_hotwords(args.hotfile)
        max_chars = int(args.max_chars) if args.max_chars else None

        if args.echo:
            lines = [args.echo]
        else:
            lines = read_lines(args.input, encoding=args.encoding) 
            #            lines = read_lines(args.input)
        if args.num_beams:
            num_of_beams = args.num_beams

        proofreader  = Proofreader()
        proofreaders = []

        await proofreader.start_async()
        await proofreader.set_pattern_async('|'.join(hotwords))
        await proofreader.set_replacement_async('$')

        if args.output == '-':
            progress_bar = None
            buffer = None
        else:
            buffer = io.StringIO()
            original_stdout = sys.stdout
            sys.stdout = buffer
            progress_bar = None

        fail_count = 0
        pass_count = 0

        chunks = chunk_lines_by_char_limit(lines, max_chars=max_chars)

        #        print(f"[DEBUG] チャンク数 = {len(chunks)}")

        print(f'Max Chars : {max_chars}       Num Beams : {num_of_beams}')
        print(f"hotwords : {' '.join(hotwords)}")
        print('\n--------')

        # 1チャンクずつ処理
        for chunk_index, (chunk_lines, line_indices) in enumerate(chunks):
            input_text = "\n".join(chunk_lines)
            proofreader.input_text = input_text

            pass_flag = False
            output_scores = {}  # これを最初に定義！

            import difflib

            input_lines = input_text.splitlines()
            num_lines = len(input_lines)
            output_texts_per_line = [[] for _ in range(num_lines)]

            # 全出力を収集
            output_texts_all = []
            for dict_index in range(proofreader.dict_count):
#                print(f'dict_index = {dict_index}')
                output_texts = await proofreader.test_async(input_text, dict_index , num_of_beams)
                output_texts_all.extend(output_texts)

            # 出力ごとに処理
            for output_text, dict_name in output_texts_all:
                output_lines = output_text.split('\\n')

                # 行数が多すぎればカット、足りなければ空行追加
                if len(output_lines) < num_lines:
                    output_lines += [''] * (num_lines - len(output_lines))
                elif len(output_lines) > num_lines:
                    output_lines = output_lines[:num_lines]

                cursor = 0  # 最初の探索位置
                SIMILARITY_THRESHOLD = 0.2
                for out_line in output_lines:
                    out_line_clean = out_line.strip()
                    matched = False

                    for i in range(cursor, num_lines):
                        in_line_clean = input_lines[i].strip()
                        sim = difflib.SequenceMatcher(None, in_line_clean, out_line_clean).ratio()

                        if sim >= SIMILARITY_THRESHOLD:
#                            print(f"[MATCH] 行 {i}: sim={sim:.2f} | 入力: {in_line_clean} | 出力: {out_line_clean}")
                            output_texts_per_line[i].append((out_line, dict_name))
                            cursor = i + 1  # 次の探索はその次から
                            matched = True
                            break

#                    if not matched:
#                        print(f"[SKIP] 類似度不足で破棄: '{out_line}'")
                        
            # すべての出力行のマッチ処理が終わったあと
            # ↓ この行の後に入れる
            # for output_text, dict_name in output_texts_all:
            #     ...

            proofreaders = []   # 初期化
            # ★ここで Proofreader を行ごとにまとめて構築
            for i in range(num_lines):
                pr = Proofreader()
                pr.input_text = input_lines[i]
                pr.zenkaku_input_text = normalize(input_lines[i])
                pr.output_texts = output_texts_per_line[i]  # ← すべての辞書出力がここにまとめて入る！
#                print(f'output texts = {output_texts_per_line[i]}')
                proofreaders.append(pr)
                #                print(f"[DEBUG] proofreaders に追加: 行 {i}: {pr.input_text}")


            BLUE = '\033[38;5;25m'         # 青系前景（.ansi21 相当）
            CYAN = '\033[36m'            # シアン 校正の入ったもとテキスト
            YELLOW = '\033[38;5;226m'    # 黄色　校正箇所
            BOLD_RED = '\033[31;1m'  # 太字・赤
            RESET = '\033[0m'
            BOLD = '\033[1m'
            RESUME = '\033[39m'  #色を標準色に
                

            #ここから判定
            for i, pr in enumerate(proofreaders):
#                print(f"\nline : {i} {pr.input_text}")
                output_scores = {}  # 初期化はここで一度だけ
                pass_flag = False
                seen_texts = set() 
                for output_text, dictionary_name in pr.output_texts:
                    try:
                        zenkaku_output_text = pr.concat_output_text(output_text)
                        score, chunk_match = pr.get_score(zenkaku_output_text)
                        if(score == 100):
                            pass_flag = True
                        match = re.match(r'T(\d+)', dictionary_name)
                        if match:
                            model_index = int(match.group(1))
                            model_name = pr.t5_names[model_index]
                        else:
                            model_name = dictionary_name

                        if zenkaku_output_text not in seen_texts:
                            output_scores[(zenkaku_output_text, model_name)] = score
                            seen_texts.add(zenkaku_output_text)
                            
                    except Exception as e:
                        print(f"[ERROR] 変換失敗: {e} / output_text={output_text} / dict={dictionary_name}")
                chunk_match,unmatched_chunks = check_chunk_match(pr)
                seen_texts = set()                         
                # スコアで並び替え（高得点順)
                sorted_scores = sorted(output_scores.items(), key=lambda x: x[1], reverse=True)
                #                print(f'[DEBUG] sorted score = {sorted_scores}')
                #                has_high_score = any(s >= 80 for s in output_scores.values())
                has_high_score = True
#                print(f' [DEBUG]  has_high_score {has_high_score}  chunk_match {chunk_match}')
                if(pass_flag or chunk_match):
#                    print(f'PASS: pass_flag {pass_flag}  has_high_score {has_high_score}  chunk_match {chunk_match}')
                    print(f'{pr.input_text}')
                    pass_count += 1
                else:
#                    print(f'{pr.highlight_diff(pr.input_text, zenkaku_output_text)}')
                    print(f'{BOLD}{CYAN}{pr.highlight_unmatched_chunks(pr.input_text, unmatched_chunks)}{RESET}')
#                    print(f' FAIL: has_high_score {has_high_score}  chunk_match {chunk_match}')
                    fail_count += 1
                    for (zenkaku_output_text, model_name), score in sorted_scores:
                        if zenkaku_output_text in seen_texts:
                            continue  # すでに出力済みの文はスキップ
                        seen_texts.add(zenkaku_output_text)
                        #                        print(f'      {score:3.0f}: {zenkaku_output_text} [{model_name}]')
                        if score < 50:
                            continue
                        if has_high_score == True:
                            print(f'\033[31m{pr.highlight_diff(zenkaku_output_text,input_text)}\033[0m : {score:3.0f} [{model_name}] ')
                        else:
                            print(f'{RED}{zenkaku_output_text}{RESET} : {RED}{BOLD}{score:3.0f}{RESET} [{model_name}] ')

                            
        if progress_bar:
            progress_bar.set_postfix({'怪しい行': fail_count})

        print(f'\n       FAIL COUNT :  {RED}{fail_count:3.0f}{RESUME}    PASS COUNT : {CYAN}{pass_count:3.0f}{RESUME}        REDUCTION : {SOFT_YELLOW}{(pass_count)/(pass_count + fail_count)*100:.1f}{RESUME} %       \n')

        if buffer:        
            sys.stdout = sys.__stdout__  # 元に戻す
            from ansi2html import Ansi2HTMLConverter

            conv = Ansi2HTMLConverter()
            html_output = conv.convert(buffer.getvalue(), full=True)

            # 💡 <meta charset="UTF-8"> を head に追加（あれば）
            if "<head>" in html_output:
                html_output = html_output.replace("<head>", "<head><meta charset='UTF-8'>", 1)

            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(html_output) 
                            
        await proofreader.shutdown_async()


        
# 他の関数やクラスの外に書く！
# ファイルの一番最後でOK！

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())        

#        asyncio.run(main())

