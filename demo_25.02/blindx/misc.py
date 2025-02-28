# MIT License (c) 2024, 2025 Masakazu Suzuoki, AxTecChare
# See LICENSE.txt for details.

import os
import logging
from logging.handlers import RotatingFileHandler

__all__ = [
    'set_logger', 'search_path', 'load_string_from_file',
]

def set_logger(path, console_level = logging.INFO, file_level = logging.INFO):

    log_path = os.path.splitext(path)[0] + ".log"
    basename = os.path.basename(log_path)

    root_logger = logging.getLogger()
    root_level = min(console_level, file_level)
    root_logger.setLevel(root_level)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_formatter = logging.Formatter(
        "%(asctime)s %(levelname)-s %(filename)s:%(lineno)d: %(message)s")
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(current_dir, 'log', basename)

    file_handler = RotatingFileHandler(
        full_path,
        mode="a",
        maxBytes=100 * 1024,
        backupCount=3,
        encoding="utf-8"
    )

    file_handler.setLevel(file_level)
    file_formatter = logging.Formatter(
        "%(asctime)s %(levelname)-s %(filename)s:%(lineno)d: %(message)s")
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

def search_path(path):
    base_dir = os.path.abspath('.')

    while True:
        target_path = os.path.join(base_dir, path)
        if os.path.exists(target_path):
            return target_path

        parent_dir = os.path.dirname(base_dir)
        if parent_dir == base_dir:
            break

        base_dir = parent_dir

    raise FileNotFoundError(f"'{path}' not found")

def load_string_from_file(file_path):
    try:    
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"{file_path} : {e}")
        return 'ふぁいるがみつかりませんでした'

