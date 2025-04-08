# MIT License (c) 2024, 2025 Masakazu Suzuoki, AxTecChare
# See LICENSE.txt for details.

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from blindx.backend import Backend
import blindx.misc as misc
import time

backend = Backend()
lineno = 0
backend.start()

full_path = misc.search_path('assets/samples/BlindX.txt')
sample_text = misc.load_string_from_file(full_path)

for text in sample_text.splitlines():
    lineno = backend.append_line('Alice')
    line = backend.lines[lineno]
    line.key = 'Alice'
    for char in text + '\n':
        line.input_text += char
        backend.request(line.key)
        time.sleep(0.05) # 5 chars per sec
        output_text = line.output_text + line.postfix()
        print(output_text)

time.sleep(1)
print('lines:')
for line in backend.lines:
    output_text = line.output_text.replace('\n', '\\n')
    print(f'    {output_text}')

backend.shutdown()


    
