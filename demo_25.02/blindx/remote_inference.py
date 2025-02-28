# MIT License (c) 2024, 2025 Masakazu Suzuoki, AxTecChare
# See LICENSE.txt for details.

import asyncio
import websockets
import logging

class RemoteInference():
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.uri = "ws://localhost:6789"
        self.websocket = None

    async def __aenter__(self):
        await self.start_async()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.shutdown_async()

    async def start_async(self):
        self.logger.info('start')
        try:
            self.websocket = await websockets.connect(self.uri)
        except Exception as e:
            self.logger.warning(f'connection failed {e}.')
            self.websocket = None
                
    async def shutdown_async(self):
        if self.websocket:
            self.logger.info('shutdown')
            await self.websocket.close()

    async def send_recv_async(self, dict_type, text):
        while self.websocket:
            try:            
                if text:
                    await self.websocket.send(dict_type + text)
                    return await self.websocket.recv()
                else:
                    return ''
            except websockets.ConnectionClosed:
                self.logger.info(f'reconnect')
                await self.websocket.close()
                self.websocket = await websockets.connect(self.uri)
                

if __name__ == "__main__":
    misc.set_logger(__file__)
    async def main():
        async with RemoteInference() as inference:
            for text in sample_text.splitlines():
                if text:
                    for i in range(0, 256):
                        sec = time.time()
                        result = inference.local_exec('T0:256:' + text)
                        print(f'msec = {int((time.time() - sec) * 1000)}')
                        print(result)

    asyncio.run(main())
