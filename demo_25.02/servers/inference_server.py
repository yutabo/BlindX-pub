#!/usr/bin/env python3
#
# inference server
#
from blindx.local_inference import LocalInference
import blindx.misc as misc
import asyncio
import websockets
import logging

async def main():
    misc.set_logger(__file__)
    logger = logging.getLogger(__name__)
    logger.info('start')
    connected_clients = set()
    async with LocalInference() as inference:
        async def handle_client(websocket):
            connected_clients.add(websocket)
            try:
                async for message in websocket:
                    if message == 'query:dict_names':
                        result = inference.query(message)
                    else:
                        result = inference.exec(message)
                    await websocket.send(result)

            except websockets.ConnectionClosed:
                logger.info('client disconnected.')
            finally:
                logger.info('client removed.')
                connected_clients.remove(websocket)

        async with websockets.serve(handle_client, "localhost", 6789):
            await asyncio.Future()  

if __name__ == "__main__":
    asyncio.run(main())
