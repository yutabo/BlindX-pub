# MIT License (c) 2024, 2025 Masakazu Suzuoki, AxTecChare
# See LICENSE.txt for details.
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from blindx.auto_text import AutoText
import asyncio

complete_event = asyncio.Event()

async def play_callback_async(message):
    key = message['key']
    input_text = message['text']
    print(f'{key} : {input_text}')

    if input_text == 'おしまい':
        complete_event.set()


async def main():

    sample_text = (
        '\\0ちょっとたかいふらい\n'
        '\\1しろいくもがぼーるにきえて\n'
        '\\2きょうはじめてみた\n'
        '\\3あなたがまぶしいくさやきゅう\n'
        'おしまい'
    )
    auto_text = AutoText('Alice', ['Alice', 'Bob', 'Charlie', 'Dave'], play_callback_async)
    await auto_text.start_async(sample_text)
    await complete_event.wait()

asyncio.run(main())
