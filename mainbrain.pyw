import os
import time
import webbrowser
import pyttsx3
import speech_recognition as sr
import pystray
import pyautogui
import threading
import random
from PIL import Image
from pywinauto import Desktop

class Chanakya:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.is_sleeping = False
        self.mic = None

    def speak(self, text):
        def speaker_thread():
            try:
                engine = pyttsx3.init()
                engine.setProperty('rate', 185)
                # Pronunciation fixes
                pronounce_text = text.replace("hisab", "hisaab").replace("Hisab", "Hisaab")
                print(f"Chanakya: {text}")
                engine.say(pronounce_text)
                engine.runAndWait()
                engine.stop()
            except: pass
        threading.Thread(target=speaker_thread).start()

    def manage_calculator(self):
        try:
            app = Desktop(backend="uia").window(title_re=".*Calculator.*")
            if app.exists():
                app.set_focus()
                return True
        except: pass
        os.system("start calc")
        time.sleep(1.2)
        return False

    def process_command(self, recognizer, audio):
        try:
            query = recognizer.recognize_google(audio, language="en-IN").lower()
            
            # Corrections
            if "hiseb" in query: query = query.replace("hiseb", "hisab")
            query = query.replace("chanakya", "").strip()
            print(f"User heard: {query}")

            if self.is_sleeping:
                if any(w in query for w in ["wake up", "uth jao"]):
                    self.is_sleeping = False
                    self.speak("Ji Malik, hazir hoon.")
                return

            # --- 1. MATH LOGIC WITH VOICE RESULT ---
            if any(op in query for op in ["+", "-", "x", "plus", "into", "multiplied by", "divided by"]):
                # Cleaning query for calculation
                math_q = query.replace("plus", "+").replace("minus", "-").replace("into", "*").replace("x", "*").replace("divided by", "/")
                final_math = "".join([c for c in math_q if c in "0123456789+-*/."])

                if final_math:
                    try:
                        # Calculation solving
                        result = eval(final_math)
                        # Chanakya result bolega
                        self.speak(f"Iska jawaab hai {result}")
                        
                        # Calculator mein bhi entry karega record ke liye
                        self.manage_calculator()
                        time.sleep(0.5)
                        pyautogui.typewrite(final_math)
                        pyautogui.press('enter')
                    except:
                        self.speak("Maaf kijiyega Malik, yeh calculation thodi mushkil hai.")
                return

            # --- 2. GREETINGS ---
            if any(w in query for w in ["good boy", "shabash", "nice"]):
                self.speak(random.choice(["Shukriya Malik!", "Dhanyawad!", "Hamesha aapki sewa mein."]))
                return

            # --- 3. OTHER COMMANDS ---
            if "screenshot" in query:
                folder = os.path.join(os.environ['USERPROFILE'], 'Pictures', 'Chanakya_Screenshots')
                if not os.path.exists(folder): os.makedirs(folder)
                pyautogui.screenshot().save(os.path.join(folder, f"Snap_{int(time.time())}.png"))
                self.speak("Screenshot le liya gaya hai.")
                return

            if "mute" in query:
                pyautogui.press("volumemute")
                return

            if any(w in query for w in ["youtube", "google", "notepad"]):
                self.speak("Ji khul gaya.")
                if "youtube" in query: webbrowser.open("https://youtube.com")
                elif "google" in query: webbrowser.open("https://google.com")
                else: os.system("start notepad")
                return

            if any(w in query for w in ["so jao", "sleep"]):
                self.speak("Theek hai Malik.")
                self.is_sleeping = True
                return

            if "close" in query:
                pyautogui.hotkey('alt', 'f4')
                return

        except: pass

    def run(self):
        print("Chanakya Starting...")
        self.mic = sr.Microphone()
        with self.mic as source: self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
        self.recognizer.listen_in_background(self.mic, self.process_command)
        self.speak("Pranaam Malik!")
        icon = pystray.Icon("Chanakya", Image.new('RGB', (64, 64), color='orange'), menu=pystray.Menu(pystray.MenuItem("Exit", lambda: os._exit(0))))
        icon.run()

if __name__ == "__main__":
    Chanakya().run()