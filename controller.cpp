#include <windows.h>
#include <iostream>
#include <string>
#include <vector>
#include <algorithm>

using namespace std;

// 1. Volume Control Logic
void setVolume(string mode) {
    if (mode == "up") {
        for(int i=0; i<5; i++) {
            keybd_event(VK_VOLUME_UP, 0, 0, 0);
            keybd_event(VK_VOLUME_UP, 0, KEYEVENTF_KEYUP, 0);
        }
    } else if (mode == "down") {
        for(int i=0; i<5; i++) {
            keybd_event(VK_VOLUME_DOWN, 0, 0, 0);
            keybd_event(VK_VOLUME_DOWN, 0, KEYEVENTF_KEYUP, 0);
        }
    } else if (mode == "mute") {
        keybd_event(VK_VOLUME_MUTE, 0, 0, 0);
        keybd_event(VK_VOLUME_MUTE, 0, KEYEVENTF_KEYUP, 0);
    }
}

// 2. Screenshot Logic (Using Windows Key + PrintScreen)
void takeScreenshot() {
    // Windows + PrintScreen automatically saves to Pictures/Screenshots
    keybd_event(VK_LWIN, 0, 0, 0);
    keybd_event(VK_SNAPSHOT, 0, 0, 0);
    Sleep(50);
    keybd_event(VK_SNAPSHOT, 0, KEYEVENTF_KEYUP, 0);
    keybd_event(VK_LWIN, 0, KEYEVENTF_KEYUP, 0);
}

// 3. Smart Copy-Paste (Line Selection)
void copyLine() {
    keybd_event(VK_HOME, 0, 0, 0); // Start of line
    keybd_event(VK_HOME, 0, KEYEVENTF_KEYUP, 0);
    Sleep(50);
    keybd_event(VK_SHIFT, 0, 0, 0);
    for(int i=0; i<8; i++) { // Select items in row
        keybd_event(VK_RIGHT, 0, 0, 0);
        keybd_event(VK_RIGHT, 0, KEYEVENTF_KEYUP, 0);
    }
    keybd_event(VK_SHIFT, 0, KEYEVENTF_KEYUP, 0);
    Sleep(50);
    keybd_event(VK_CONTROL, 0, 0, 0);
    keybd_event('C', 0, 0, 0);
    keybd_event('C', 0, KEYEVENTF_KEYUP, 0);
    keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0);
}

// 4. Close Window (Alt + F4)
void closeWindow() {
    keybd_event(VK_MENU, 0, 0, 0); // Alt
    keybd_event(VK_F4, 0, 0, 0);
    keybd_event(VK_F4, 0, KEYEVENTF_KEYUP, 0);
    keybd_event(VK_MENU, 0, KEYEVENTF_KEYUP, 0);
}

// 5. Press Enter (For YouTube Play)
void pressEnter() {
    keybd_event(VK_RETURN, 0, 0, 0);
    keybd_event(VK_RETURN, 0, KEYEVENTF_KEYUP, 0);
}

int main(int argc, char* argv[]) {
    // Hide Console Window for silent execution
    ShowWindow(GetConsoleWindow(), SW_HIDE);

    if (argc < 2) return 0;
    string command = argv[1];

    if (command == "vol_up") setVolume("up");
    else if (command == "vol_down") setVolume("down");
    else if (command == "vol_mute") setVolume("mute");
    else if (command == "screenshot") takeScreenshot();
    else if (command == "copy_line") copyLine();
    else if (command == "close") closeWindow();
    else if (command == "enter") pressEnter();
    else if (command == "paste") {
        keybd_event(VK_CONTROL, 0, 0, 0);
        keybd_event('V', 0, 0, 0);
        keybd_event('V', 0, KEYEVENTF_KEYUP, 0);
        keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0);
    }

    return 0;
}