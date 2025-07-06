import pyautogui as pgui
import time
from pynput import keyboard as kb
import sys


quit = False

def on_press_to_quit(key):
    """
    Quit program if 'q' is pressed
    """
    global quit
    try:
        if key.char == 'q':
            print('closing program')
            quit = True
    except AttributeError:
        pass

listener = kb.Listener(on_press=on_press_to_quit)
listener.start()

# Enter the name of your browser, based on the name of its icon image.
browser_img = 'brave.png'
try:
    browser_loc = pgui.locateCenterOnScreen(f'img/{browser_img}', confidence=0.8)

    if browser_loc:
        pgui.moveTo(browser_loc, duration=0.2)
        pgui.click()
        # Change the time depending on how long it takes to open your browser
        time.sleep(2)
except (pgui.ImageNotFoundException, Exception):
    print("Browser icon not found.")
    sys.exit('closing script')

pgui.hotkey('ctrl', 't')

pgui.write('https://www.youtube.com/playlist?list=WL')
time.sleep(0.05)
pgui.press("enter")

# change depending on how long it takes to load yt
time.sleep(5)


if __name__ == '__main__':
    while not quit:

        opt_loc = pgui.locateCenterOnScreen('img/options.png', confidence=0.8)

        if opt_loc:
            pgui.moveTo(opt_loc, duration=0.2)
            pgui.click()
            time.sleep(0.2)
        else: 
            print('options button not founded')
            break

        del_loc = pgui.locateCenterOnScreen('img/delete.png', confidence=0.8)

        if del_loc:
            pgui.moveTo(del_loc, duration=0.2)
            pgui.click()
            time.sleep(0.2)
        else: 
            print('delete button not founded')
            break