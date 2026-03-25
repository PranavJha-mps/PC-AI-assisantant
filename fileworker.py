import os
import sys

def search_and_open(target_name):
    user_profile = os.environ['USERPROFILE']
    target_name = target_name.lower().strip()
    
    # Priority Paths
    potential_paths = [
        os.path.join(user_profile, 'Desktop'),
        os.path.join(user_profile, 'OneDrive', 'Desktop'),
        os.path.join(user_profile, 'Documents')
    ]

    # --- PHASE 1: EXACT MATCH (Strict) ---
    for base in potential_paths:
        if not os.path.exists(base): continue
        for root, dirs, files in os.walk(base):
            # Isse wo 'encoding' jaise folders ke andar ghusega hi nahi
            if target_name in [d.lower() for d in dirs]:
                full_path = os.path.join(root, target_name)
                # Check agar exact name folder hai
                for d in dirs:
                    if d.lower() == target_name:
                        actual_path = os.path.join(root, d)
                        os.startfile(actual_path)
                        return True
    
    # --- PHASE 2: DRIVES (Top Level Only for Speed) ---
    for drive in ['D:\\', 'E:\\', 'F:\\']:
        if os.path.exists(drive):
            try:
                for item in os.listdir(drive):
                    if item.lower() == target_name:
                        os.startfile(os.path.join(drive, item))
                        return True
            except: continue
    return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = sys.argv[1].lower().replace("folder", "").replace("kholo", "").strip()
        search_and_open(query)
