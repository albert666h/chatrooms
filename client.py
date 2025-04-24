import os
import websockets
import asyncio


def display_options():
    print("[*] Select your option:")
    print("1. create room")
    print("2. join room")
    print("3. exit")

async def create_room(websocket):
    """Send a request to create a room"""
    await websocket.send("create room")
    id = await websocket.recv()
    print(f"[*] Created room with id: {id}")

async def join_room(websocket):
    """Send a request to join a room"""
    await websocket.send("join room")
    rooms = await websocket.recv() # get the list of available rooms
    print(rooms)

    id = input("[*] room id: ")
    await websocket.send(id)
    res = await websocket.recv()
    
    # check if the join is valid
    if res == "success":
        print("Success!")
    else:
        print(res)
        return


async def main():
    print("[*] Welcome to ChatRoom")
    try:
        async with websockets.connect("ws://localhost:5678") as websocket:
            # Registration
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

            while True:
                display_options()
                opt = input("[*] option: ")

                match opt:
                    case '1':
                        await create_room(websocket)
                    case '2':
                        await join_room(websocket)
                    case '3':
                        break
                    case _:
                        print("[-] Invalid Option. Choose again")               

        print("[*] Bye")

    except websockets.exceptions.ConnectionClosedError as e:
        print("[*] Connection to the server was closed:")
        print(e)
    except websockets.exceptions.InvalidURI as e:
        print("[*] Invalid WebSocket URI. Please check the URL format.")
        print(e)    
    except OSError as e:  # This catches errors like "Connection Refused" when the server is down
        print("[*] Could not connect to the WebSocket server. Is it running?")
        print(e)
    except Exception as e:
        # This will catch any other unexpected errors
        print("[-] Unexpected error occurred.")
        print(e)


if __name__ == "__main__":
    asyncio.run(main())