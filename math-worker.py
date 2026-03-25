import sys
import os
import time
import pyautogui

def do_math(query):
    os.system("start calc")
    time.sleep(1.0)
    math_query = query.replace("plus", "+").replace("minus", "-").replace("into", "*").replace("x", "*")
    final_math = "".join([c for c in math_query if c in "0123456789+-*/."])
    pyautogui.typewrite(final_math)
    pyautogui.press('enter')

if __name__ == "__main__":
    if len(sys.argv) > 1:
        do_math(sys.argv[1])
