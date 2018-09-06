import os,sys
import threading
import logging

import time
import atexit
if os.name == "nt":
    import msvcrt
    def get_key_press():
        if msvcrt.kbhit():
            return msvcrt.getch()
else:
    import select
    import termios

    import tty
    try:
        old_settings = termios.tcgetattr(sys.stdin)
    except:
        logging.getLogger("serial_mock").warn("No keyboard listeners available :(")
        get_key_press = lambda :1
    else:
        atexit.register(lambda:termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings))
        tty.setcbreak(sys.stdin.fileno())
        def get_key_press():
            if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
                return sys.stdin.read(1)

class KBListen:
    def __init__(self,on_key_handler):
        self.on_key_handler = on_key_handler
        self.halt = False
    def Listen(self):
        def run():
            while not self.halt:
                key = get_key_press()
                if key:
                    self.on_key_handler(key)
        th = threading.Thread(target=run)
        th.start()

if __name__ == "__main__":
    def on_key(key):
        print("KK:",key)
    kb = KBListen(on_key)
    kb.Listen()


    while True:
        try:
            time.sleep(1)
        except:
            break
    kb.halt=True
    print("GOODBYE!")