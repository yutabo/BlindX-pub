# MIT License (c) 2024, 2025 Masakazu Suzuoki, AxTecChare
# See LICENSE.txt for details.

from blindx.backend import Backend
from blindx.backend import BackendLine
import asyncio
import websockets
import logging

class BackendShare():

    def __init__(self, backend):

        self.logger = logging.getLogger(__name__)
        self.uri = "ws://localhost:6790"
        self.backend = backend
        self.my_key = None
        self.active_names = []
        self.websocket = None
        self.sync_task = None
        self.recv_task = None
        self.lines = []
        self.sync_event = asyncio.Event()

    def backend_output_callback(self, lines):
        self.sync_event.set()

    async def start_async(self):
        self.logger.info('start')
        if not self.backend: return # do nothing

        try:
            self.websocket = await websockets.connect(self.uri)
        except Exception as e:
            self.logger.error(f'connection failed {e}.')
            self.websocket = None
            return

        self.sync_task = asyncio.create_task(self.sync_loop())
        self.recv_task = asyncio.create_task(self.recv_loop())

        await self.websocket.send('reload:')
        while not self.my_key:
            await asyncio.sleep(0.5)

        self.backend.add_output_callback(self.backend_output_callback)    

    async def shutdown_async(self):
        self.logger.info('shutdown')

        if self.backend:
            self.backend.discard_output_callback(self.backend_output_callback)    

        for task in (self.sync_task, self.recv_task):
            task.cancel()
            task = None

        """    
        if self.sync_task:
            self.sync_task.cancel()
            self.sync_task = None

        if self.recv_task:
            self.recv_task.cancel()
            self.recv_task = None
        """
        if self.websocket:
            await self.websocket.close()
            self.websocket = None

    async def sync_loop(self):
        while True:
            while self.websocket:
                try:
                    await self.sync_event.wait()
                    if not self.backend.lines:
                        if self.lines:
                            self.lines = []
                            self.logger.info('send clear')
                            await self.websocket.send('clear:')

                    else:    
                        self.align_lines()
                        for lineno, line in enumerate(self.backend.lines):
                            if line.key == self.my_key or self.lines[lineno].key == self.my_key:
                                if line.quick_hash() != self.lines[lineno].quick_hash():
                                    line.serialize()
                                    self.lines[lineno] = line.dup()
                                    await self.websocket.send(str(lineno) + ':' + line.serialized_text)

                    self.sync_event = asyncio.Event()

                except websockets.ConnectionClosed:
                    self.logger.info(f'reconnect')
                    await self.websocket.close()
                    self.websocket = await websockets.connect(self.uri)

                except Exception as e:
                    self.logger.warning(f'send_loop failed {e}')
                    await asyncio.sleep(1)


    async def recv_loop(self):
        while True:
            while self.websocket:
                try:
                    message = await self.websocket.recv()
                    list = message.split(':', 1)

                    if list[0] == 'clear':
                        self.logger.info('recv clear')
                        self.backend.clear_all_lines()
                        self.lines = []

                    elif list[0] == 'name':
                        sublist = list[1].split(':')
                        self.my_key = sublist[0]
                        self.active_names = sublist[1:]
                        self.logger.info(f'recv name [{self.my_key}]')

                    else:    
                        lineno = int(list[0])
                        if lineno >= len(self.backend.lines):
                            self.backend.lines.extend([BackendLine()] * (lineno + 1 - len(self.lines)))

                        self.backend.lines[lineno].serialized_text = list[1]
                        self.backend.lines[lineno].deserialize()
                        self.align_lines()
                        self.lines[lineno] = self.backend.lines[lineno].dup()
                        self.backend.invoke_output_callbacks()

                except Exception as e:
                    self.logger.warning(f'recv_loop failed {e}.')
                    await asyncio.sleep(1)

    def align_lines(self):

        lenA = len(self.lines)
        lenB = len(self.backend.lines)
        if lenA > lenB:
            del self.lines[lenB:]
        if lenA < lenB:
            self.lines.extend([BackendLine()] * (lenB - lenA))

