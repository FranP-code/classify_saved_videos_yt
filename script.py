import pyautogui as pgui
import time
from pynput import keyboard as kb
import sys


playlist_url = 'https://www.youtube.com/playlist?list=WL'

quit = False

half_left = (
    0,
    0,
    pgui.size().width // 2,
    pgui.size().height
)

half_right = (
    pgui.size().width // 2,
    0,
    pgui.size().width,
    pgui.size().height
)

def on_press_to_quit(key):
    """Quit program if 'q' is pressed."""
    global quit
    try:
        if key.char == 'q':
            print('Closing program...')
            quit = True
    except AttributeError:
        pass


def locate_img(
        image: str,
        sleep_time:float=None,
        search_time:float=0,
        confidence:float=1.0,
        gray_scale:bool=False,
        region:tuple[int,int,int,int]=None
    ):
    """Locate and click on an image. Returns True if successful, False otherwise."""
    try:
        opt_loc = pgui.locateCenterOnScreen(
            f'img/{image}',
            confidence=confidence,
            minSearchTime=search_time,
            grayscale=gray_scale,
            region=region
            )

        if opt_loc:
            pgui.click(opt_loc)

            if sleep_time:
                time.sleep(sleep_time)
            
            return True

    except Exception as e:
        print(f"Error locating '{image}': {e}")
        return False


def change_to_not_available():
    try:

        success = locate_img('pl_opt.png', sleep_time=0.2, search_time=0.5, confidence=0.8, gray_scale=True, region=half_left)

        if not success: return False
        
        success = locate_img('not-available.png', search_time=0.5, confidence=0.8)
        
        if not success: return False

        window = pgui.size()
        x_pos = 3 * (window.width / 4)
        y_pos = window.height / 2
        pgui.moveTo(x_pos, y_pos)
        time.sleep(5)
        
        success = locate_img('options.png', sleep_time=0.2, confidence=0.8, gray_scale=True, region=half_right)

        if not success: return False

        return True

    except:
        print(f"Critical error in change_to_not_available")
        return False


listener = kb.Listener(on_press=on_press_to_quit)
listener.start()

# Open browser
browser_img = 'brave.png'

try:
    locate_img(browser_img, confidence=0.8, sleep_time=1)
except Exception as e:
    print(f"Error opening browser, you must have your browser pinned in the taskbar")
    sys.exit('Closing script.')

# Open YouTube
pgui.hotkey('ctrl', 't')
pgui.write(playlist_url)
pgui.press("enter")
time.sleep(5)


if __name__ == '__main__':
    counter = 0

    while not quit:
        # restart tab to free up resources
        if counter > 0 and (counter % 90) == 0:
            pgui.hotkey('ctrl', 'w')
            pgui.hotkey('ctrl', 't')
            pgui.write(playlist_url)
            pgui.press("enter")
            time.sleep(8)
        

        try:
            success = locate_img('options.png', sleep_time=0.2, confidence=0.8, gray_scale=True, region=half_right)

            if not success:
                print('changing plans to enable videos...')
                second_success = change_to_not_available()

                if not second_success:
                    break
        except:
            print('Error finding options image')
            break

        try:
            success = locate_img('delete.png', confidence=0.8)
            if success:
                counter += 1
                print(f"Deleted {counter} videos.")
                time.sleep(0.2)

            else: break

        except Exception as e:
            print(f"Error in delete step: {e}")
            break


    listener.stop()
    print("Script finished.")