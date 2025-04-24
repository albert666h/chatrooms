import os
import websockets
import asyncio


def display_options():
    print("[*] Select your option:")
    print("1. create room")
    print("2. join room")
    print("3. exit")

async def create_room(websocket):
    pass

async def join_room(websocket):
    pass

async def connect():
    async with websockets.connect("ws://localhost:5678") as websocket:
        await websocket.send(input("> "))

async def main():
    print("[*] Welcome to ChatRoom")
    async with websockets.connect("ws://localhost:5678") as websocket:
        # Registration

        res = ""
        while True:
            name = input("username: ")
            await websocket.send(name) # send the name to verify

            # check if username is taken
            res = await websocket.recv()
            if res == "0":      # username taken
                print(f"[-] Username {name} already taken, try another one")
            elif res == "1":
                print(f"[+] Successfully registered as {name}")
                break

        opt = ''
        while not opt == '3':
            display_options()
            opt = input("[*] option: ")

            match opt:
                case '1':
                    await create_room()
                case '2':
                    await join_room()
                case '3':
                    break
                case _:
                    print("[-] Invalid Option. Choose again")               


    print("[*] Bye")


if __name__ == "__main__":
    asyncio.run(main())