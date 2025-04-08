# MIT License (c) 2024, 2025 Masakazu Suzuoki, AxTecChare
# See LICENSE.txt for details.

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import blindx.misc as misc
from blindx.frontend import Frontend
from blindx.backend import Backend
from blindx.backend import ConditionVariable

complete_condition = ConditionVariable()

def output_callback(lines): 
    print(f'output:')
    for line in lines:
        if line.long_output_text:
            print('\t' + line.long_output_text, end='')
            if line.long_output_text == 'おしまい\n':
                complete_condition.notify_all()

backend = Backend()
frontend = Frontend(backend)

backend.add_output_callback(output_callback)
backend.start()

full_path = misc.search_path('assets/samples/BlindX.txt')
input_text = misc.load_string_from_file(full_path)
input_text += 'おしまい\n'

frontend.update('Alice', input_text, True)
complete_condition.wait()
backend.shutdown()


