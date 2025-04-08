# MIT License (c) 2024, 2025 Masakazu Suzuoki, AxTecChare
# See LICENSE.txt for details.

import logging
import random

class Login():
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.available_names = [
            'Alice', 'Bob', 'Charol', 'Charile', 'Dave', 'Eve', 'Ellen', 'Frank', 'Isac', 'IVan', 
            'Justin', 'Marvin', 'Matilda', 'Oscar', 'Peggy', 'Steve', 'Trent', 'Trudy', 'Walter', 'Zoe' 
        ]
        self.active_names = []

    async def login_async(self):
        name = random.choice(self.available_names)
        await self.connect_async(name)
        return name

    async def connect_async(self, name):
        self.logger.info(f'connect {name}')
        self.active_names.append(name)
        self.available_names.remove(name)

    async def disconnect_async(self, name):
        self.active_names.remove(name)
        self.available_names.append(name)
        self.logger.info(f'disconnect {name}')

