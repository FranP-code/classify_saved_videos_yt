import pyautogui as pgui
import time
import keyboard as kb

# colocar el nombre de tu navegador, basado en el nombre de la imagen de su respectivo icono
browser = 'brave'

browser_loc = pgui.locateCenterOnScreen(f'img/{browser}.png', confidence=0.8)

pgui.moveTo(browser_loc, duration=0.2)
time.sleep(0.2)
pgui.click()

# cambia el tiempo dependiendo de cuanto tarde en abrir tu navegador
time.sleep(2)



pgui.hotkey('ctrl', 't')

pgui.write('https://www.youtube.com/playlist?list=WL')
time.sleep(0.05)
pgui.press("enter")

# cambiar dependiendo de cuanto tarde en cargarte yt
time.sleep(5)

videos = int(input('number of videos: '))

while videos != 0:

    if kb.is_pressed('q'):
        print(':(')
        break
    
    opt_loc = pgui.locateCenterOnScreen('img/options.png', confidence=0.8)

    pgui.moveTo(opt_loc, duration=0.2)
    pgui.click()
    time.sleep(0.2)

    del_loc = pgui.locateCenterOnScreen('img/delete.png', confidence=0.8)

    pgui.moveTo(del_loc, duration=0.2)
    pgui.click()
    time.sleep(0.2)

    videos -= 1
