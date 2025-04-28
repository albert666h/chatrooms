import curses
import asyncio
import websockets


class ChatRoom:
    def __init__(self, stdscr, websocket):
        self.stdscr = stdscr
        self.websocket = websocket

        curses.curs_set(1)
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, -1, -1)

        self.height, self.width = stdscr.getmaxyx()
        self.input_height = 3
        self.output_height = self.height - self.input_height

        self.output_win = curses.newwin(self.output_height, self.width, 0, 0)
        self.input_win = curses.newwin(self.input_height, self.width, self.output_height, 0)

        self.messages = []
        self.max_messages = self.output_height - 2

    def draw_output(self):
        self.output_win.clear()
        self.output_win.border()
        visible_messages = self.messages[-self.max_messages:]
        for idx, msg in enumerate(visible_messages):
            self.output_win.addstr(idx + 1, 1, msg[:self.width - 2], curses.color_pair(1))
        self.output_win.refresh()

    async def get_user_input(self, prompt="> "):
        self.input_win.clear()
        self.input_win.border()
        self.input_win.addstr(1, 1, prompt, curses.color_pair(1))
        curses.echo()
        self.input_win.refresh()
        user_input = await asyncio.to_thread(self.input_win.getstr, 1, len(prompt)+1, self.width - len(prompt) - 3)
        curses.noecho()
        return user_input.decode("utf-8")

    def add_message(self, msg):
        self.messages.append(msg)
        self.draw_output()

    async def authenticate(self):
        while True:
            name = await self.get_user_input("username: ")
            await self.websocket.send(name)
            res = await self.websocket.recv()
            if res == "0":
                self.add_message(f"[-] Username {name} already taken.")
            elif res == "1":
                self.add_message(f"[+] Registered as {name}")
                return

    async def select_room(self):
        while True:
            self.add_message("[*] Options:")
            self.add_message("    1. create room")
            self.add_message("    2. join room")
            self.add_message("    3. exit")
            opt = await self.get_user_input("option: ")

            if opt == "1":
                await self.websocket.send("create room")
                room_id = await self.websocket.recv()
                self.add_message(f"[*] Created room with ID: {room_id}")

            elif opt == "2":
                await self.websocket.send("join room")
                rooms = await self.websocket.recv()
                self.add_message("[*] Available Rooms:")
                for line in rooms.splitlines():
                    self.add_message(line)
                room_id = await self.get_user_input("room id: ")
                await self.websocket.send(room_id)
                res = await self.websocket.recv()
                if res == "success":
                    await self.run_chat()
                else:
                    self.add_message("[-] " + res)

            elif opt == "3":
                return False
            else:
                self.add_message("[-] Invalid option.")

    async def run_chat(self):
        self.messages = []
        self.add_message("[*] Joined room. Type !exit to leave.")

        async def receive_messages():
            try:
                async for msg in self.websocket:
                    self.add_message(msg.strip())
                    if msg == "!exit":
                        break
            except websockets.exceptions.ConnectionClosed:
                self.add_message("[*] Connection closed.")

        async def send_messages():
            while True:
                msg = await self.get_user_input()
                await self.websocket.send(msg)
                if msg.strip() == "!exit":
                    break

        await asyncio.gather(receive_messages(), send_messages())
        self.messages = []

    async def run(self):
        await self.authenticate()
        joined = await self.select_room()
        if joined:
            await self.run_chat()


async def curses_main(stdscr):
    try:
        async with websockets.connect("ws://localhost:5678") as ws:
            chat_ui = ChatRoom(stdscr, ws)
            await chat_ui.run()
    except Exception as e:
        stdscr.clear()
        stdscr.addstr(0, 0, f"Error: {str(e)}", curses.color_pair(1))
        stdscr.refresh()
        await asyncio.sleep(3)


def main():
    curses.wrapper(lambda stdscr: asyncio.run(curses_main(stdscr)))


if __name__ == "__main__":
    main()
