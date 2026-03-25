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
        self.awaiting_choice = None 
        self.pending_target = None
        self.search_paths = [
            os.path.join(os.environ['USERPROFILE'], 'Desktop'),
            os.path.join(os.environ['USERPROFILE'], 'Documents'),
            os.path.join(os.environ['USERPROFILE'], 'Videos'),
            os.path.join(os.environ['USERPROFILE'], 'Downloads')
        ]

    def speak(self, text):
        def speaker_thread():
            try:
                engine = pyttsx3.init()
                engine.setProperty('rate', 185)
                # Voice pronunciation fix
                p_text = text.replace("hisab", "hisaab").replace("Hisab", "Hisaab")
                print(f"Chanakya: {text}")
                engine.say(p_text)
                engine.runAndWait()
                engine.stop()
            except: pass
        threading.Thread(target=speaker_thread).start()

    def smart_search(self, target):
        """Logic to handle duplicates (App vs Folder)"""
        found_folder = None
        for path in self.search_paths:
            if os.path.exists(path):
                for item in os.listdir(path):
                    if target.lower() == item.lower() or target.lower() in item.lower():
                        found_folder = os.path.join(path, item)
                        break
        
        if found_folder:
            self.speak(f"Malik, {target} naam ki app aur folder dono hain. Kya kholun?")
            self.awaiting_choice = "decision"
            self.pending_target = {"folder": found_folder, "app": target}
            return
        
        # Default: Try opening as App/System search
        self.speak(f"{target} khol raha hoon.")
        pyautogui.press('win'); time.sleep(0.3); pyautogui.write(target); time.sleep(0.4); pyautogui.press('enter')

    def process_command(self, recognizer, audio):
        try:
            query = recognizer.recognize_google(audio, language="en-IN").lower().strip()
            if "hiseb" in query: query = query.replace("hiseb", "hisab")
            print(f"User: {query}")

            # --- CHOICE HANDLING ---
            if self.awaiting_choice == "decision":
                if "folder" in query:
                    os.startfile(self.pending_target["folder"])
                    self.speak("Folder khul gaya.")
                else:
                    t = self.pending_target["app"]
                    pyautogui.press('win'); time.sleep(0.3); pyautogui.write(t); time.sleep(0.4); pyautogui.press('enter')
                    self.speak("App khol di hai.")
                self.awaiting_choice = None
                return

            if self.is_sleeping and "wake up" not in query: return

            # --- 1. MEDIA CONTROLS (Pause/Play/Stop) ---
            if any(w in query for w in ["pause", "stop", "roko", "play", "chalao"]):
                pyautogui.press('space')
                return

            # --- 2. VOLUME (Silent) ---
            if any(w in query for w in ["volume up", "awaaz badhao"]):
                for _ in range(10): pyautogui.press("volumeup")
                return
            if any(w in query for w in ["volume down", "awaaz kam karo"]):
                for _ in range(10): pyautogui.press("volumedown")
                return
            if "mute" in query:
                pyautogui.press("volumemute")
                return

            # --- 3. UNIVERSAL OPENER ---
            if "open" in query or "kholo" in query:
                name = query.replace("open", "").replace("kholo", "").strip()
                if "whatsapp" in name:
                    os.system("start whatsapp://")
                    return
                if "youtube" in name:
                    webbrowser.open("https://youtube.com"); return
                self.smart_search(name)
                return

            # --- 4. MATH ---
            if any(op in query for op in ["+", "-", "x", "plus", "into"]):
                math_q = query.replace("plus", "+").replace("minus", "-").replace("into", "*").replace("x", "*")
                final_math = "".join([c for c in math_q if c in "0123456789+-*/."])
                if final_math and any(c.isdigit() for c in final_math):
                    try:
                        result = eval(final_math)
                        self.speak(f"Iska jawaab hai {result}")
                        return
                    except: pass

            # --- 5. SYSTEM ---
            if "time" in query:
                self.speak(time.strftime("%I:%M %p")); return
            if "screenshot" in query:
                path = os.path.join(os.environ['USERPROFILE'], 'Pictures', f"Snap_{int(time.time())}.png")
                pyautogui.screenshot().save(path)
                self.speak("Screenshot done."); return
            if "so jao" in query:
                self.is_sleeping = True; self.speak("Theek hai Malik."); return
            if "wake up" in query:
                self.is_sleeping = False; self.speak("Main hazir hoon."); return
            if "close" in query or "band karo" in query:
                pyautogui.hotkey('alt', 'f4'); return

        except: pass

    def run(self):
        self.mic = sr.Microphone()
        with self.mic as source: self.recognizer.adjust_for_ambient_noise(source)
        self.recognizer.listen_in_background(self.mic, self.process_command)
        self.speak("Chanakya Active!")
        pystray.Icon("Chanakya", Image.new('RGB', (64, 64), color='orange'), 
                     menu=pystray.Menu(pystray.MenuItem("Exit", lambda: os._exit(0)))).run()

if __name__ == "__main__":
    Chanakya().run()
