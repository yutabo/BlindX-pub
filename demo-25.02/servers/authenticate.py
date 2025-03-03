# MIT License (c) 2024, 2025 Masakazu Suzuoki, AxTecChare
# See LICENSE.txt for details.

import asyncio
import websockets
import logging

VALID_API_KEYS = [
    'PUBLICKEY'
]

def valid_api_keys():
    return VALID_API_KEYS

async def verify(logger, websocket):
    api_key = websocket.subprotocol

    if api_key in VALID_API_KEYS:
        await websocket.send("authentication successful")
        return True
    else:
        await websocket.close(code=4001, reason="unauthorized")
        return False
