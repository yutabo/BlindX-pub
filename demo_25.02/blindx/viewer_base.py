# MIT License (c) 2024, 2025 Masakazu Suzuoki, AxTecChare
# See LICENSE.txt for details.

from abc import ABC, abstractmethod

class ViewerBase(ABC):

    @abstractmethod
    async def start_async(self, page, key, on_keyboard_event, on_change_event, on_button_event):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def get_input(self):
        pass

    @abstractmethod
    async def set_input_async(self, text):
        pass

    @abstractmethod
    def set_output(self, lines):
        pass
