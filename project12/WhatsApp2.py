import webbrowser
import pyautogui
import time

numbers = [
    "917044726076",
    "918777059815",
    "918910330373",
    "918444011950",
    "917478834104",
    "918145241653"
]

message = "Welcome to CodeHub"

for number in numbers:
    webbrowser.open(f"https://web.whatsapp.com/send?phone={number}")
    time.sleep(10)

    pyautogui.write(message)
    pyautogui.press("enter")

    time.sleep(5)