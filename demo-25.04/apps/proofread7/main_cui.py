#@title かな漢字変換テスト
# MIT License (c) 2024, 2025 Masakazu Suzuoki, AxTecChare
# See LICENSE.txt for details.

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


import asyncio
import blindx.misc as misc
from proofreader import Proofreader
import argparse
from tqdm import tqdm
import logging
import re
import io

if __name__ == "__main__":

    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='source filename', default='input.txt')
    parser.add_argument('-o', '--output', help='result filename', default='-')
    parser.add_argument('-e', '--echo', help='phrase') 
    parser.add_argument('--encoding', choices=['utf-8', 'utf-16-le'], default='utf-8', help='text encoding') 
    parser.add_argument('--hotwords', nargs='+', help='hot words')
    parser.add_argument('--hotfile', help='hot file')
    args = parser.parse_args()
    def read_lines(name):
        with open(name, 'r', encoding=args.encoding) as f:
            lines = []
            for input_text in f:
                line = ''
                for char in input_text.rstrip('\n'):
                    if ord(char) != 65279:
                        line += char
                lines.append(line)
            return lines

    def load_hotwords(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
            hotwords = text.strip().split()
        return hotwords

    async def main():
        misc.set_logger('kousei', logging.WARN)
        RED = '\033[31m'
        RED_BOLD = '\033[1;31m'
        RESET = '\033[0m'

        hotwords = [
            ' ', '　', '、', ',', '…', '^◆.*$',
            '【.*?】', '［.*?］', '^◆.*$', '//.*$', '^;.*$',
        ]
        
        if args.hotwords:
            hotwords += args.hotwords
        if args.hotfile:
            hotwords += load_hotwords(args.hotfile)

        if args.echo:
            lines = [args.echo]
        else:    
            lines = read_lines(args.input)

        proofreader = Proofreader()
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


        for lineno, line in enumerate(progress_bar if progress_bar else lines):
            proofreader.output_texts = []
            proofreader.input_text = ""
            proofreader.hiragana_text = ""                
            
            if not line.strip():
#                print(f"スキップされた行: {lineno}")
                continue
            pass_flag = False
            output_scores = {}  # これを最初に定義！
            for dict_index in range(proofreader.dict_count):
                await proofreader.test_async(line, dict_index)

            # 全体のスコア評価（全文 or 文節一致が1つでもあれば PASS）
            pass_flag = False

            output_scores = {}

            for output_text, dictionary_name in proofreader.output_texts:
                zenkaku_output_text = proofreader.concat_output_text(output_text)
#                print(f'[DEBUG] zenkaku_output_text = {zenkaku_output_text}')
#                print(f'[DEBUG] proofreader.output_texts = {proofreader.output_texts}')
                score, _ = proofreader.get_score(zenkaku_output_text)
                output_scores[(zenkaku_output_text, dictionary_name)] = score
                if score == 100:
                    pass_flag = True
                    break

            # スコア評価：90以上のスコアが1つでもあれば PASS 候補
            has_high_score = any(score >= 90 for score in output_scores.values())
            # 文節一致
            
            has_chunk_match = proofreader.all_input_chunks_matched(proofreader.input_text, proofreader.output_texts)

            # どちらも満たしたときだけ PASS
            if pass_flag == False :  # 最初の条件がPASSの場合はそのまま通す
                pass_flag = has_high_score and has_chunk_match
                
            if pass_flag:
                pass_count += 1
                print(f'{proofreader.input_text}')
                continue
            else:

#                print(f'{proofreader.input_text}')
#                print(f' ひらがな: {proofreader.hiragana_text}')
                #                    for output_text, dictionary_name in proofreader.output_texts:
                
                fail_count += 1
                output_scores = {}

                for output_text, dictionary_name in proofreader.output_texts:
                    try:
                        zenkaku_output_text = proofreader.concat_output_text(output_text)
                        score, chunk_match = proofreader.get_score(zenkaku_output_text)

                        #print(f'      {score:3.0f}: {zenkaku_output_text} [{dictionary_name}]')  # ← ターミナル確認用
                        
                        match = re.match(r'T(\d+)', dictionary_name)
                        if match:
                            model_index = int(match.group(1))
                            model_name = proofreader.t5_names[model_index]
                        else:
                            model_name = dictionary_name
                            
                        output_scores[(zenkaku_output_text, model_name)] = score
                            
                    except Exception as e:
                        print(f"[ERROR] 変換失敗: {e} / output_text={output_text} / dict={dictionary_name}")                

                        # スコアで並び替え（高得点順）
                sorted_scores = sorted(output_scores.items(), key=lambda x: x[1], reverse=True)
#                    print(f' [DEBUG] sorted_scores : {sorted_scores}  output_scores : {output_scores}')
                    # 出力
#                for (zenkaku_output_text, model_name), score in sorted_scores:
#                    print(f'      {score:3.0f}: {zenkaku_output_text} [{model_name}]')
                seen_texts = set()
                print(f'{proofreader.highlight_diff(proofreader.input_text,zenkaku_output_text)}') 
                for (zenkaku_output_text, model_name), score in sorted_scores:
                    if zenkaku_output_text in seen_texts:
                        continue  # すでに出力済みの文はスキップ
                    seen_texts.add(zenkaku_output_text)
                    #                    print(f'      {score:3.0f}: {zenkaku_output_text} [{model_name}]')
                    if has_high_score == True:
                        print(f'\033[31m{zenkaku_output_text}\033[0m : {score:3.0f} [{model_name}] ')
                    else:
                        print(f'{RED}{zenkaku_output_text}{RESET} : {RED}{RED_BOLD}{score:3.0f}{RESET} [{model_name}] ')
                                   
            if progress_bar:
                progress_bar.set_postfix({'怪しい行': fail_count})

        print(f'\n       FAIL COUNT :  \033[31m{fail_count:3.0f}\033[0m    PASS COUNT : {pass_count:3.0f}\n')


        if buffer:        
            sys.stdout = sys.__stdout__  # 元に戻す
            from ansi2html import Ansi2HTMLConverter

            conv = Ansi2HTMLConverter()
            html_output = conv.convert(buffer.getvalue(), full=True)

            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(html_output) 

        await proofreader.shutdown_async()

        
# 他の関数やクラスの外に書く！
# ファイルの一番最後でOK！

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())        

#        asyncio.run(main())


