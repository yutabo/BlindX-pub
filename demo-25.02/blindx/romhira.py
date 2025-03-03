# MIT License (c) 2024, 2025 Masakazu Suzuoki, AxTecChare
# See LICENSE.txt for details.

import unicodedata
import re

def is_zenkaku(char):
    return unicodedata.east_asian_width(char) in {'F', 'W', 'A'}

def is_kanji(char):
    codepoint = ord(char)
    return (
        0x4E00 <= codepoint <= 0x9FFF or  
        0x3400 <= codepoint <= 0x4DBF or  
        0x20000 <= codepoint <= 0x2A6DF or
        0x2A700 <= codepoint <= 0x2B73F or
        0x2B740 <= codepoint <= 0x2B81F or
        0x2B820 <= codepoint <= 0x2CEAF or
        0x2CEB0 <= codepoint <= 0x2EBEF
    )

class Romhira():

    def __init__(self, hiragana='', preface=''):

        self.hiragana = hiragana
        self.preface = preface
        self.is_escape = False 
        self.is_kanji = False

        self.zenkaku_number=[
            '１', '２', '３', '４', '５', '６', '７', '８', '９', '０', 
        ]

        self.dict1={'a':'あ', 'i':'い', 'u':'う', 'e':'え', 'o':'お',
                    '1':'１', '2':'２', '3':'３', '4':'４', '5':'５', 
                    '6':'６', '7':'７', '8':'８', '9':'９', '0':'０', 
                    '-':'ー', '^':'＾', '\\':'￥', '@':'＠', '[':'「', 
                    ';':'；', ':':'：', ']':'」', ',':'、', '.':'。', '/':'・', ' ':'　',
                    '!':'！', '"':'”', '#':'＃', '$':'＄', '%':'％', '&':'＆', 
                    "'":'’', '(':'（', ')':'）', '=':'＝', '~':'～', '|':'｜', 
                    '`':'‘', '{':'｛', '+':'＋', '*':'＊', '}':'｝', '<':'＜', 
                    '>':'＞', '?':'？', '_':'＿', 'A':'A', 'B':'B', 'C':'C', 
                    'D':'D', 'E':'E', 'F':'F', 'G':'G', 'H':'H', 'I':'I', 
                    'J':'J', 'K':'K', 'L':'L', 'M':'M', 'N':'N', 'O':'O', 
                    'P':'P', 'Q':'Q', 'R':'R', 'S':'S', 'T':'T', 'U':'U', 
                    'V':'V', 'W':'W', 'X':'X', 'Y':'Y', 'Z':'Z'}

        self.dict2={'ka':'か', 'ki':'き', 'ku':'く', 'ke':'け', 'ko':'こ',
                    'ca':'か', 'cu':'く', 'co':'こ',
                    'sa':'さ', 'si':'し', 'ci':'し', 'su':'す', 'se':'せ', 'ce':'せ', 'so':'そ',
                    'ta':'た', 'ti':'ち', 'tu':'つ', 'te':'て', 'to':'と',
                    'na':'な', 'ni':'に', 'nu':'ぬ', 'ne':'ね', 'no':'の',
                    'ha':'は', 'hi':'ひ', 'hu':'ふ', 'fu':'ふ', 'he':'へ', 'ho':'ほ',
                    'ma':'ま', 'mi':'み', 'mu':'む', 'me':'め', 'mo':'も',
                    'ya':'や', 'yi':'い', 'yu':'ゆ', 'ye':'いぇ', 'yo':'よ',
                    'ra':'ら', 'ri':'り', 'ru':'る', 're':'れ', 'ro':'ろ',
                    'wa':'わ', 'wi':'うぃ', 'wu':'う', 'we':'うぇ', 'wo':'を',
                    'nn':'ん', 'xn':'ん', "n'":'ん',
                    'va':'ゔぁ', 'vi':'ゔぃ', 'vu':'ゔ', 've':'ゔぇ', 'vo':'ゔぉ',
                    'ga':'が', 'gi':'ぎ', 'gu':'ぐ', 'ge':'げ', 'go':'ご',
                    'za':'ざ', 'zi':'じ', 'ji':'じ', 'zu':'ず', 'ze':'ぜ', 'zo':'ぞ',
                    'da':'だ', 'di':'ぢ', 'du':'づ', 'de':'で', 'do':'ど',
                    'ba':'ば', 'bi':'び', 'bu':'ぶ', 'be':'べ', 'bo':'ぼ',
                    'pa':'ぱ', 'pi':'ぴ', 'pu':'ぷ', 'pe':'ぺ', 'po':'ぽ',
                    'fa':'ふぁ', 'fi':'ふぃ', 'fe':'ふぇ', 'fo':'ふぉ',
                    'ja':'じゃ', 'ju':'じゅ', 'je':'じぇ', 'jo':'じょ',
                    'la':'ぁ', 'xa':'ぁ', 'li':'ぃ', 'xi':'ぃ', 'lu':'ぅ', 'xu':'ぅ', 
                    'le':'ぇ', 'xe':'ぇ', 'lo':'ぉ', 'xo':'ぉ',
                    'qa':'くぁ', 'qi':'くぃ', 'qu':'く', 'qe':'くぇ', 'qo':'くぉ',
                    }
        
        self.dict3={'shi':'し',
                    'chi':'ち', 'tsu':'つ',
                    'kya':'きゃ', 'kyi':'きぃ', 'kyu':'きゅ', 'kye':'きぇ', 'kyo':'きょ',
                    'kwa':'くぁ', 
                    'qya':'くゃ', 'qyi':'くぃ', 'qyu':'くゅ', 'qye':'くぇ', 'qyo':'くょ',
                    'qwa':'くぁ', 'qwi':'くぃ', 'qwu':'くぅ', 'qwe':'くぇ', 'qwo':'くぉ',
                    'sya':'しゃ', 'syi':'しぃ', 'syu':'しゅ', 'sye':'しぇ', 'syo':'しょ',
                    'sha':'しゃ', 'shu':'しゅ', 'she':'しぇ', 'sho':'しょ',
                    'swa':'すぁ', 'swi':'すぃ', 'swu':'すぅ', 'swe':'すぇ', 'swo':'すぉ',
                    'tya':'ちゃ', 'tyi':'ちぃ', 'tyu':'ちゅ', 'tye':'ちぇ', 'tyo':'ちょ',
                    'cha':'ちゃ', 'chu':'ちゅ', 'che':'ちぇ', 'cho':'ちょ',
                    'cya':'ちゃ', 'cyi':'ちぃ', 'cyu':'ちゅ', 'cye':'ちぇ', 'cyo':'ちょ',
                    'tsa':'つぁ', 'tsi':'つぃ', 'tse':'つぇ', 'tso':'つぉ',
                    'tha':'てゃ', 'thi':'てぃ', 'thu':'てゅ', 'the':'てぇ', 'tho':'てょ',
                    'twa':'とぁ', 'twi':'とぃ', 'twu':'とぅ', 'twe':'とぇ', 'two':'とぉ',
                    'nya':'にゃ', 'nyi':'にぃ', 'nyu':'にゅ', 'nye':'にぇ', 'nyo':'にょ',
                    'hya':'ひゃ', 'hyi':'ひぃ', 'hyu':'ひゅ', 'hye':'ひぇ', 'hyo':'ひょ',
                    'fya':'ふゃ', 'fyi':'ふぃ', 'fyu':'ふゅ', 'fye':'ふぇ', 'fyo':'ふょ',
                    'fwa':'ふぁ', 'fwi':'ふぃ', 'fwu':'ふぅ', 'fwe':'ふぇ', 'fwo':'ふぉ',
                    'mya':'みゃ', 'myi':'みぃ', 'myu':'みゅ', 'mye':'みぇ', 'myo':'みょ',
                    'rya':'りゃ', 'ryi':'りぃ', 'ryu':'りゅ', 'rye':'りぇ', 'ryo':'りょ',
                    'wha':'うぁ', 'whi':'うぃ', 'whu':'う', 'whe':'うぇ', 'who':'うぉ',
                    'wyi':'ゐ', 'wye':'ゑ',
                    'gya':'ぎゃ', 'gyi':'ぎぃ', 'gyu':'ぎゅ', 'gye':'ぎぇ', 'gyo':'ぎょ',
                    'gwa':'ぐぁ', 'gwi':'ぐぃ', 'gwu':'ぐぅ', 'gwe':'ぐぇ', 'gwo':'ぐぉ',
                    'zya':'じゃ', 'zyi':'じぃ', 'zyu':'じゅ', 'zye':'じぇ', 'zyo':'じょ',
                    'jya':'じゃ', 'jyi':'じぃ', 'jyu':'じゅ', 'jye':'じぇ', 'jyo':'じょ',
                    'dya':'ぢゃ', 'dyi':'ぢぃ', 'dyu':'ぢゅ', 'dye':'ぢぇ', 'dyo':'ぢょ',
                    'dha':'でゃ', 'dhi':'でぃ', 'dhu':'でゅ', 'dhe':'でぇ', 'dho':'でょ',
                    'dwa':'どぁ', 'dwi':'どぃ', 'dwu':'どぅ', 'dwe':'どぇ', 'dwo':'どぉ',
                    'bya':'びゃ', 'byi':'びぃ', 'byu':'びゅ', 'bye':'びぇ', 'byo':'びょ',
                    'pya':'ぴゃ', 'pyi':'ぴぃ', 'pyu':'ぴゅ', 'pye':'ぴぇ', 'pyo':'ぴょ',
                    'xya':'ゃ', 'xyi':'ぃ', 'xyu':'ゅ', 'xye':'ぇ', 'xyo':'ょ', 'xtu':'っ',
                    'lya':'ゃ', 'lyi':'ぃ', 'lyu':'ゅ', 'lye':'ぇ', 'lyo':'ょ', 'ltu':'っ',
                    'xwa':'ゎ', 'xka':'ゕ', 'xke':'ゖ',
                    'lwa':'ゎ', 'lka':'ゕ', 'lke':'ゖ',
                    'vya':'ゔゃ', 'vyi':'ゔぃ', 'vyu':'ゔゅ', 'vye':'ゔぇ', 'vyo':'ゔょ',
                    }
        
        self.dict4={'xtsu':'っ', 'ltsu':'っ',}
        self.repeatable_shiin='kstchfmyrwvgzjdbpxlq'
        #repeatable_shiin + repeatable_shiin → 最初の子音を「っ」に
        #n + (not 母音) → 最初のnを「ん」に

    def hiragana_and_preface(self):
        return self.hiragana + self.preface

    def clear(self):
        self.hiragana = ''
        self.preface = ''
        self.is_escape = False 
        self.is_kanji = False 

    def backward(self):
        if self.preface: 
            self.preface = self.preface[:-1]
        else:
            self.hiragana = self.hiragana[:-1]

    def addstr(self, str):
        for char in str:
            self.add(char)

    def add(self, char):
        # ignore spcial chars
        if len(char) > 1:
            return
        # aiu `aiu` -> あいう `aiu`
        if char == '`':
            self.is_escape = not self.is_escape
            self.hiragana += char
            self.preface = ''
            return

        # '1.5 desu.'-> '１．５です。'
        if char == '.' and self.hiragana[-1] in self.zenkaku_number:
            self.hiragana += '．'
            self.preface = ''
            return

        # '漢字desu' -> ’漢字です'
        if self.is_escape or is_zenkaku(char):
            if is_kanji(char):
                self.is_kanji = True
            self.hiragana += self.preface
            self.hiragana += char
            self.preface = ''
            return

        self.preface += char
        len_p = len(self.preface)
        if len_p >= 4:
            top = self.preface[:4]
            if top in self.dict4:
                self.hiragana += self.dict4[top]
                self.preface = self.preface[4:]
                return
            top1, top2 = self.preface[0], self.preface[1:4]
            if top1 in self.repeatable_shiin and top1==top2[0] and top2 in self.dict3:
                self.hiragana += f'っ{self.dict3[top2]}'
                self.preface = self.preface[4:]
                return
        if len_p >= 3:
            top = self.preface[:3]
            if top in self.dict3:
                self.hiragana += self.dict3[top]
                self.preface = self.preface[3:]
                return
            top1, top2 = self.preface[0], self.preface[1:3]
            if top1 in self.repeatable_shiin and top1==top2[0] and top2 in self.dict2:
                self.hiragana += f'っ{self.dict2[top2]}'
                self.preface = self.preface[3:]
                return
        if len_p >= 2:
            top = self.preface[:2]
            if top in self.dict2:
                self.hiragana += self.dict2[top]
                self.preface = self.preface[2:]
                return
            if top[0] == 'n' and top[1] != 'y':
                self.hiragana += 'ん'
                self.preface = self.preface[1:]
                return
        if len_p:
            top = self.preface[0]
            if top in self.dict1:
                self.hiragana += self.dict1[top]
                self.preface = self.preface[1:]




