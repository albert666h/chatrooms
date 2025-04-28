import os
import websockets
from websockets.exceptions import ConnectionClosedOK
import asyncio
from uuid import uuid4

rooms = {}
connections = {}

def create_room(user):
    """Create a new room and return the ID"""
    id = str(uuid4())
    rooms[id] = {"messages": [], "users": set(), "admin": user}

    return id

def remove_connection(user):
    """Remove the user from the connections"""
    if user in connections.keys():
            connections.pop(user, None)
            print(f"[*] {user} left the server")

def room_help_message():
    print("[*] These are the commands the admin can use:")
    print(">   !help: display this message")
    print(">   !clear: clear the room")
    print(">   !delete: delete the room")
    print(">   !ban <user>: ban the <user>")

async def handle_room(user, room_id):
    try:
        print(f"[*] {user} joined the room {room_id}")
        while True:
            message = await connections[user].recv()
            if message == None:
                break
            elif message.strip() == "!exit":
                print(f"[*] {user} left the room {room_id}")
                await connections[user].send(f"!exit")
                rooms[room_id]["users"].remove(user)

                for u in rooms[room_id]["users"]:
                    await connections[u].send(f"[{user}] left the chat")
                return
            else:
                if rooms[room_id]["admin"] == user:
                    if message.strip() ==  "!help":
                        room_help_message()
                    elif message.strip() == "!clear":
                        pass
                    elif message.strip() == "!delete":
                        pass
                    elif message.strip()[:4] == "!ban":
                        pass
                
                rooms[room_id]["messages"].append({user:message})
                for u in rooms[room_id]["users"]:
                    if connections[u]:
                        await connections[u].send(f"[{user}] > {message}")

    except ConnectionClosedOK:
        remove_connection(user)

def get_rooms():
    res = ""
    for i, room in enumerate(rooms.keys()):
        res += f"{i+1}. {room}\n"
    
    return res

async def handle_join_room(user):
    rooms_str = get_rooms()
    try:
        await connections[user].send(rooms_str)
        id = await connections[user].recv()
        if id in rooms.keys():
            await connections[user].send("success")
            rooms[id]["users"].add(user)
            await handle_room(user, id)
        else:
            await connections[user].send("[-] No such room...")
    except ConnectionClosedOK:
        remove_connection(user)

async def handle_connection(user):
    """Manage users"""
    try:
        print(f"[*] {user} joined the server")
        while True:
            message = await connections[user].recv()
            match message:
                case None:
                    break
                case "create room":
                    id = create_room(user)
                    print(f"[*] Created a room with id: {id}")
                    await connections[user].send(id)
                
                case "join room":
                    await handle_join_room(user)

    except ConnectionClosedOK:
        remove_connection(user)
    finally:
        remove_connection(user)


async def register(websocket):
    """Register new connectins"""
    while True:
        try:
            name = await websocket.recv()
            name = name.strip()
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