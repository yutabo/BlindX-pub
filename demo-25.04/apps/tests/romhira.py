# MIT License (c) 2024, 2025 Masakazu Suzuoki, AxTecChare
# See LICENSE.txt for details.
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from blindx.romhira import Romhira

romhira = Romhira()

romajis = [
    "ookinanopponofurudokeioziisannnoとけい kandoushitya",
    "aahayaku,kugatuninareba `I love you. you are the only one`アイラブユー",
    "seityourituha 1.5% datta."
]

for romaji in romajis:
    romhira.clear()
    for char in romaji:
        romhira.add(char)
    print(f'    in:  {romaji}')    
    print(f'    out: {romhira.hiragana}')    
    print('')
