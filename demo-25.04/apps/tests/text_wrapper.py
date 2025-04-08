#!/usr/bin/env python3
#
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from blindx.text_wrapper import TextWrapper
import blindx.misc as misc

text_wrapper = TextWrapper()
input_text = "びーとるずのめいきょく「へい・じゅーど」は`Hey Jude, Don't make it bad` というでだしではじまります。\n"

encoded_text = text_wrapper.encode(input_text)
decoded_text = text_wrapper.decode(encoded_text)

print(f'encoded_text={encoded_text}')
print(f'decoded_text={decoded_text}')
