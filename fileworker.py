import sys
import os
import string

def find_and_open(target):
    drives = [f"{l}:\\" for l in string.ascii_uppercase if os.path.exists(f"{l}:\\")]
    for drive in drives:
        for root, dirs, _ in os.walk(drive):
            if target.lower() in [d.lower() for d in dirs]:
                os.startfile(os.path.join(root, target))
                return True
    return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        find_and_open(sys.argv[1])