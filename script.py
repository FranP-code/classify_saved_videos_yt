import pyautogui as pgui
import time
import keyboard as kb


quit = False

# Enter the name of your browser, based on the name of its icon image.
browser = 'brave'

browser_loc = pgui.locateCenterOnScreen(f'img/{browser}.png', confidence=0.8)

if browser_loc:
    pgui.moveTo(browser_loc, duration=0.2)
    time.sleep(0.2)
    pgui.click()
    # Change the time depending on how long it takes to open your browser
    time.sleep(2)
else:
    print("Browser icon not found.")
    exit()

pgui.hotkey('ctrl', 't')

pgui.write('https://www.youtube.com/playlist?list=WL')
time.sleep(0.05)
pgui.press("enter")

# change depending on how long it takes to load yt
time.sleep(5)

while not quit:

    if kb.is_pressed('q'):
        print(':(')
        quit = True
        continue
    
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
