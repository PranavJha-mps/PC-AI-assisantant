import os
import time
import webbrowser
import pyttsx3
import speech_recognition as sr
import pystray
import threading
import subprocess
import string
from PIL import Image, ImageDraw

class Chanakya:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300 
        self.recognizer.dynamic_energy_threshold = False 
        self.recognizer.pause_threshold = 0.8
        
        self.processing = False 
        self.is_sleeping = False 
        self.user_title = "Malik"

    def speak(self, text):
        def speaker_thread():
            try:
                engine = pyttsx3.init()
                voices = engine.getProperty('voices')
                for voice in voices:
                    if "Hemant" in voice.name or "India" in voice.name:
                        engine.setProperty('voice', voice.id)
                        break
                engine.setProperty('rate', 190)
                engine.say(f"{text} {self.user_title}")
                engine.runAndWait()
            except: pass
        threading.Thread(target=speaker_thread, daemon=True).start()

    def call_cpp(self, task):
        """C++ Controller Bridge"""
        try:
            exe_path = os.path.join(os.getcwd(), "output", "controller.exe")
            if not os.path.exists(exe_path):
                exe_path = os.path.join(os.getcwd(), "controller.exe")
            subprocess.run([exe_path, task], creationflags=0x08000000)
        except: print("C++ Engine not found!")

    def get_active_drives(self):
        return [f"{l}:\\" for l in string.ascii_uppercase if os.path.exists(f"{l}:\\")]

    def deep_pc_scan(self, filename):
        """PC mein saari matching files/folders dhoondhne ke liye"""
        drives = self.get_active_drives()
        matches = []
        for drive in drives:
            try:
                # 'where' command files aur folders dono dhoond leta hai
                cmd = f'where /R "{drive}" *{filename}*'
                output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
                paths = output.decode('utf-8', errors='ignore').split('\r\n')
                for p in paths:
                    clean_path = p.strip()
                    if clean_path and not clean_path.lower().endswith(".lnk"):
                        matches.append(clean_path)
            except: continue
        return list(set(matches)) # Remove duplicates

    def ask_user_choice(self, matches):
        """Agar multiple files milein toh selection logic"""
        count = len(matches)
        if count > 3: count = 3 # Limit to top 3 for speed
        
        self.speak(f"Mujhe {count} matching files mili hain. Kaunsi wali kholun?")
        
        for i in range(count):
            fname = os.path.basename(matches[i])
            parent = os.path.dirname(matches[i]).split('\\')[-1]
            print(f"[{i+1}] {fname} in folder: {parent}")

        self.speak("Aap pehli, doosri, ya teesri bol kar chun sakte hain.")

        with sr.Microphone() as source:
            try:
                audio = self.recognizer.listen(source, timeout=7)
                choice = self.recognizer.recognize_google(audio, language="en-IN").lower()
                
                if "pehli" in choice or "first" in choice or "1" in choice: return matches[0]
                elif "doosri" in choice or "second" in choice or "2" in choice: return matches[1]
                elif "teesri" in choice or "third" in choice or "3" in choice: return matches[2]
            except: pass
        return None

    def process_logic(self, query):
        query = query.lower().strip()
        if not query: return
        print(f"Command: {query}")

        # --- SLEEP/WAKE ---
        if self.is_sleeping:
            if "jaag jao" in query or "wake up" in query:
                self.is_sleeping = False
                self.speak("Main hazir hoon")
            return
        if "so jao" in query or "sleep" in query:
            self.is_sleeping = True
            self.speak("Theek hai malik")
            return

        # --- C++ SYSTEM COMMANDS ---
        if "screenshot" in query: self.call_cpp("screenshot"); self.speak("Done")
        elif "volume up" in query: self.call_cpp("vol_up")
        elif "volume down" in query: self.call_cpp("vol_down")
        elif "mute" in query: self.call_cpp("vol_mute")
        elif "copy" in query: self.call_cpp("copy_line"); self.speak("Copied")
        elif "paste" in query: self.call_cpp("paste")
        elif "close" in query or "band karo" in query: self.call_cpp("close")

        # --- OPEN LOGIC (APP -> FILE -> WEB) ---
        elif "kholo" in query or "open" in query:
            target = query.replace("kholo","").replace("open","").strip()
            
            # 1. Desktop Apps Priority
            apps = {"whatsapp": "whatsapp:", "ppt": "powerpnt", "word": "winword", "blender": "blender"}
            if target in apps:
                self.speak(f"{target} khol raha hoon")
                subprocess.Popen(f"start {apps[target]}", shell=True)
                return

            # 2. PC Scan for Files/Folders
            self.speak(f"{target} ko dhoond raha hoon")
            matches = self.deep_pc_scan(target)

            if not matches:
                self.speak("PC mein nahi mila, Google kar raha hoon")
                webbrowser.open(f"https://www.google.com/search?q={target}")
            elif len(matches) == 1:
                os.startfile(matches[0])
                self.speak("Mil gaya, khol raha hoon")
            else:
                choice = self.ask_user_choice(matches)
                if choice: os.startfile(choice)

        # --- YOUTUBE & MATH ---
        elif "youtube" in query and "play" in query:
            song = query.replace("youtube","").replace("play","").strip()
            webbrowser.open(f"https://www.youtube.com/results?search_query={song}")
            time.sleep(5); self.call_cpp("enter")
        
        elif any(c.isdigit() for c in query):
            math_q = query.replace("into","*").replace("x","*").replace("plus","+").replace("minus","-")
            exp = "".join(c for c in math_q if c in "0123456789+-*/. ").strip()
            try: self.speak(f"Iska jawab {eval(exp)} hai")
            except: pass

    def start_listening(self):
        with sr.Microphone() as source:
            self.speak("Chanakya v5 online")
            while True:
                if not self.processing:
                    try:
                        self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                        audio = self.recognizer.listen(source, timeout=None, phrase_time_limit=6)
                        def handle(audio_data):
                            self.processing = True
                            try:
                                text = self.recognizer.recognize_google(audio_data, language="en-IN")
                                self.process_logic(text)
                            except: pass
                            self.processing = False
                        threading.Thread(target=handle, args=(audio,), daemon=True).start()
                    except: continue

    def run(self):
        threading.Thread(target=self.start_listening, daemon=True).start()
        img = Image.new('RGB', (64, 64), (255, 255, 255))
        d = ImageDraw.Draw(img); d.ellipse((10, 10, 54, 54), fill=(255, 165, 0))
        icon = pystray.Icon("Chanakya", img, "Chanakya", menu=pystray.Menu(pystray.MenuItem("Exit", lambda: os._exit(0))))
        icon.run()

if __name__ == "__main__":
    Chanakya().run()
