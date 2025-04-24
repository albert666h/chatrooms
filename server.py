import os
import websockets
from websockets.exceptions import ConnectionClosedOK
import asyncio
from uuid import uuid4

rooms = {}
connections = {}

def create_room():
    """Create a new room and return the ID"""
    id = uuid4()
    rooms[id] = {"messages": [], "users": set()}

    return id

def remove_connection(user):
    """Remove the user from the connections"""
    if user in connections.keys():
            connections.pop(user, None)
            print(f"[*] {user} left the server")


async def handle_connection(user):
    """Manage users"""
    try:
        print(f"[*] {user} joined the server")
        while True:
            message = await connections[user].recv()
            if message is None:
                break
            
    except ConnectionClosedOK:
        remove_connection(user)
    finally:
        remove_connection(user)


async def register(websocket):
    """Register new connectins"""
    while True:
        try:
            name = await websocket.recv()
            if name in connections.keys():
                await websocket.send("0")
            else:
                await websocket.send(f"1")
                connections[name] = websocket
                await handle_connection(name)
                return
        except ConnectionClosedOK:
            return


async def main():
    try:
        async with websockets.serve(register, "localhost", 5678):
            await asyncio.Future() # run forever
    except Exception as e:
        print("[-] Eror")

if __name__ == "__main__":
    asyncio.run(main())