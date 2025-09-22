import time
import win32api, win32con
import ctypes
from Wacom import WacomTablet, Distance

user32 = ctypes.windll.user32
screenW, screenH = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

MAX_X = 15200
MAX_Y = 9500

prevPressed = False

def handle(pen):
    global prevPressed

    x = pen.x
    y = pen.y

    screenX = int(min(max(0, x / MAX_X * screenW), screenW - 1))
    screenY = int(min(max(0, y / MAX_Y * screenH), screenH - 1))

    win32api.SetCursorPos((screenX, screenY))

    pressed = pen.pressure > 0
    if pressed and not prevPressed:
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    elif not pressed and prevPressed:
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)

    prevPressed = pressed



def main():
    tablet = WacomTablet()

    if tablet.read():
        try:
            while True:
                pen = tablet.pen
                if pen.distance != Distance.OUT:
                    handle(pen)
                time.sleep(0.005)
        except KeyboardInterrupt:
            print("\nExiting...")
        finally:
            tablet.terminate()
    else:
        print("Not found")

if __name__ == "__main__":
    main()
