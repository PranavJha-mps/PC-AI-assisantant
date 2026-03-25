import os
import time
import webbrowser
import pyttsx3
import speech_recognition as sr
import pystray
import pyautogui
import threading
import subprocess
import json
import string
from datetime import datetime
from PIL import Image, ImageDraw

class Chanakya:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.awaiting_choice = None
        self.pending_target = None
        self.is_sleeping = False 
        
        # --- JSON GENDER LOAD ---
        self.user_title = self.load_user_title()
        print(f"--- Chanakya System Booting for {self.user_title} ---")

    def load_user_title(self):
        try:
            json_path = os.path.join(self.script_dir, "user_data.json")
            with open(json_path, "r") as f:
                data = json.load(f)
                return data.get("gender", "Malik")
        except:
            return "Malik"

    def speak(self, text):
        def speaker_thread():
            try:
                engine = pyttsx3.init()
                engine.setProperty('rate', 190)
                full_text = f"{text} {self.user_title}"
                print(f"Chanakya: {full_text}") 
                engine.say(full_text)
                engine.runAndWait()
            except: pass
        threading.Thread(target=speaker_thread, daemon=True).start()

    def open_in_chrome(self, url):
        paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Google\Chrome\Application\chrome.exe")
        ]
        for path in paths:
            if os.path.exists(path):
                subprocess.Popen([path, url])
                return
        webbrowser.open(url)

    def check_local_existence(self, name):
        drives = [f"{l}:\\" for l in string.ascii_uppercase if os.path.exists(f"{l}:\\")]
        user_profile = os.environ['USERPROFILE']
        paths = [os.path.join(user_profile, 'Desktop'), os.path.join(user_profile, 'Downloads'), os.path.join(user_profile, 'Documents')]
        paths.extend(drives)
        for p in paths:
            if os.path.exists(p):
                try:
                    if any(name.lower() in f.lower() for f in os.listdir(p)): return True
                except: continue
        return False

    def launch_app(self, name):
        pyautogui.press('win'); time.sleep(0.4)
        pyautogui.write(name); time.sleep(0.6)
        pyautogui.press('enter')

    def process_command(self, recognizer, audio):
        try:
            print("\nListening Done...")
            query = recognizer.recognize_google(audio, language="en-IN").lower().strip()
            print(f"User Said: {query}")

            # 1. EXIT & CLOSE
            if any(w in query for w in ["close", "band karo", "hatao"]):
                if "chanakya" in query:
                    self.speak("Alvida")
                    os._exit(0)
                pyautogui.keyDown('alt'); pyautogui.press('f4'); pyautogui.keyUp('alt')
                return

            # 2. SLEEP & WAKE
            if any(w in query for w in ["so jao", "sleep mode"]):
                self.is_sleeping = True
                self.speak("Main so raha hoon")
                return

            if self.is_sleeping:
                if any(w in query for w in ["jaag jao", "wake up", "utho"]):
                    self.is_sleeping = False
                    self.speak("Main hazir hoon")
                return 

            # 3. CHOICE HANDLING (App vs Folder)
            if self.awaiting_choice == "decision":
                if any(w in query for w in ["folder", "file", "niche wala"]):
                    self.speak(f"{self.pending_target} folder khol raha hoon")
                    file_py = os.path.join(self.script_dir, "file.py")
                    subprocess.Popen(f'python "{file_py}" "{self.pending_target}"', shell=True)
                elif any(w in query for w in ["app", "software", "upar wala"]):
                    self.launch_app(self.pending_target)
                self.awaiting_choice = None
                return

            # 4. MATH LOGIC
            is_math = any(char.isdigit() for char in query) or any(w in query for w in ["plus", "minus", "multiply", "divide", "square"])
            if is_math and not any(w in query for w in ["youtube", "whatsapp", "folder", "search"]):
                math_query = query.replace("plus", "+").replace("minus", "-").replace("multiply", "*").replace("divide", "/").replace("square", "**2")
                final_exp = "".join(c for c in math_query if c in "0123456789+-*/. ").strip()
                if len(final_exp) > 1:
                    try:
                        res = eval(final_exp)
                        self.speak(f"Iska jawab {res} hai")
                        subprocess.Popen('calc.exe'); time.sleep(1.2)
                        pyautogui.write(final_exp.replace("**2", "q"), interval=0.05)
                        pyautogui.press('enter')
                        return
                    except: pass

            # 5. SCREENSHOT LOGIC (Added back)
            if "screenshot" in query:
                folder_path = os.path.join(os.environ['USERPROFILE'], 'Pictures', 'Chanakya_Snaps')
                if not os.path.exists(folder_path): os.makedirs(folder_path)
                file_name = f"Snap_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png"
                pyautogui.screenshot(os.path.join(folder_path, file_name))
                self.speak("Screenshot le liya hai")
                return

            # 6. VOLUME CONTROL
            if "volume" in query:
                for _ in range(5): pyautogui.press('volumeup' if "volume up" in query else 'volumedown')
                return

            # 7. OPENER & GOOGLE SEARCH (Chrome Direct)
            if any(w in query for w in ["open", "kholo", "search"]):
                target = query.replace("open", "").replace("kholo", "").replace("search", "").strip()
                
                if "youtube" in query:
                    st = target.replace("youtube", "").strip()
                    self.speak("YouTube par dekh lijiye")
                    self.open_in_chrome(f"https://www.youtube.com/results?search_query={st}")
                    return
                
                if "folder" in query or "file" in query:
                    clean = target.replace("folder", "").replace("file", "").strip()
                    subprocess.Popen(f'python "{os.path.join(self.script_dir, "file.py")}" "{clean}"', shell=True)
                    return

                if self.check_local_existence(target) and target:
                    self.speak(f"{target} mila hai. App ya Folder?")
                    self.awaiting_choice = "decision"; self.pending_target = target
                else:
                    self.launch_app(target)
                return

            # 8. UNIVERSAL FALLBACK (Google Search)
            if len(query) > 2:
                self.speak("Theek hai, Google par dekh lijiye")
                self.open_in_chrome(f"https://www.google.com/search?q={query}")

        except Exception as e: print(f"Error: {e}")

    def run_voice(self):
        try:
            self.mic = sr.Microphone()
            with self.mic as s: 
                self.recognizer.pause_threshold = 2.2
                self.recognizer.adjust_for_ambient_noise(s, duration=0.8)
            self.recognizer.listen_in_background(self.mic, self.process_command)
            self.speak("Chanakya taiyar hai")
        except: pass

    def run(self):
        threading.Thread(target=self.run_voice, daemon=True).start()
        img = Image.new('RGB', (64, 64), (255, 255, 255))
        d = ImageDraw.Draw(img); d.ellipse((10, 10, 54, 54), fill=(255, 165, 0))
        self.icon = pystray.Icon("Chanakya", img, "Chanakya", menu=pystray.Menu(pystray.MenuItem("Exit", lambda: os._exit(0))))
        try: self.icon.run()
        except: 
            while True: time.sleep(1)

if __name__ == "__main__":
    Chanakya().run()
