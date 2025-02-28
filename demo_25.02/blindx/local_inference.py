# MIT License (c) 2024, 2025 Masakazu Suzuoki, AxTecChare
# See LICENSE.txt for details.

import blindx.misc as misc
from blindx.text_transformer import TextTransformer
from transformers import T5ForConditionalGeneration, T5Tokenizer

import os
import asyncio
import torch
import logging


class LocalInference():
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        os.environ['CUDA_VISIBLE_DEVICES'] = '0'
        self.target_dir = misc.search_path('models')
        # names = os.listdir(self.target_dir)
        self.t5_names = [name for name in os.listdir(self.target_dir) if 'all' in name]

    def start(self):
        self.device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
        self.logger.info(f'torch version: {torch.__version__}')
        self.logger.info(f'torch device:  {self.device}')

        self.tokenizer = T5Tokenizer.from_pretrained('sonoisa/t5-base-japanese-v1.1')
        self.text_transformer = TextTransformer()

        self.t5s = []
        for t5_name in self.t5_names:
            full_path = os.path.join(self.target_dir, t5_name)
            self.logger.info(f'load {full_path}')
            t5 = T5ForConditionalGeneration.from_pretrained(full_path)
            t5.to(self.device)
            self.t5s.append(t5)

    def shutdown(self):
        self.logger.info(f'session closed')

    def report(self, text, result):
        self.logger.info(f"in:  {text.replace('\n', '\\n')}")
        self.logger.info(f"out: {result.replace('\n', '\\n')}")

    def exec(self, message):
        print(f'exec: message={message}')
        try:
            com, length_str, text = message.split(':', 2)
        except ValueError:
            return 'ころんのかずがちがいます:' + message.replace(':', '：')

        try:
            if len(com) == 2 and com[0] == 'T':    
                t5 = self.t5s[int(com[1])]
            else:    
                raise IndexError    
        except IndexError:
            return 'むこうなこまんどです: ' + message.replace(':', '：')

        max_length = int(length_str)
        input_text = self.text_transformer.encode(text)
        input_ids = self.tokenizer(input_text, return_tensors='pt').input_ids.to(self.device)

        outputs = t5.generate(input_ids = input_ids, max_length=max_length)
        output_text = self.tokenizer.decode(outputs[0], skip_special_tokens = True)

        self.report(message, com + ':' + output_text) # debug
        return self.text_transformer.decode(output_text)

    def query(self, message):
            output = ''
            for t5_name in self.t5_names:
                output += t5_name + ':'
            output = output[:-1]    
            return output

    async def __aenter__(self):
        self.start()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        self.shutdown()




