#!/usr/bin/env python3
"""
Landing page for Magnifier Appliance
- Configures HDMI output resolution
- Provides High/Low resolution launch buttons
- Supports keyboard shortcuts (DEV) and Bluetooth keypad (PROD)
"""

import tkinter as tk
import subprocess
import os
import threading
from evdev import InputDevice, categorize, ecodes

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_SCRIPT = os.path.join(PROJECT_DIR, "main.py")

# keep track of subprocess
magnifier_proc = None

# --- Mode flag ---
MODE = "DEV"   # change to "PROD" on Pi4B appliance

# --- HDMI configuration ---
def set_hdmi_resolution(mode):
    if MODE == "PROD":
        try:
            subprocess.run(["xrandr", "--output", "HDMI-1", "--mode", mode], check=True)
            print(f"HDMI set to {mode}")
        except subprocess.CalledProcessError as e:
            print("Failed to set HDMI resolution:", e)
    else:
        print(f"[DEV] Skipping HDMI reconfiguration, keeping current display")

# --- Launch functions ---

def setup_bindings():
    root.bind_all("<h>", lambda e: launch_high())
    root.bind_all("<l>", lambda e: launch_low())
    root.bind_all("<q>", lambda e: quit_landing())

def keypad_listener(device_path="/dev/input/event0"): 
    try: 
        device = InputDevice(device_path) 
        for event in device.read_loop(): 
            if event.type == ecodes.EV_KEY: 
                key_event = categorize(event) 
                if key_event.keystate == 1: 
                    if key_event.keycode == 'KEY_1': 
                        launch_high() 
                    elif key_event.keycode == 'KEY_2': 
                        launch_low() 
                    elif key_event.keycode in ('KEY_ESC','KEY_KPENTER'): 
                        quit_landing() 
    except Exception as e: 
        print("Keypad listener error:", e)

def launch_high():
    global magnifier_proc
    set_hdmi_resolution("1280x720")
    subprocess.Popen(["python3", MAIN_SCRIPT, "--res", "1280x720"])

def launch_low():
    global magnifier_proc
    set_hdmi_resolution("800x450")
    subprocess.Popen(["python3", MAIN_SCRIPT, "--res", "800x450"])

def quit_landing():
    global magnifier_proc
    print("Quit requested")
    # if magnifier is still running, kill it
    if magnifier_proc and magnifier_proc.poll() is None:
        magnifier_proc.terminate()
        try:
            magnifier_proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            magnifier_proc.kill()
    # root.quit()
    root.destroy() # close Tkinter window
    # In PROD, keypad listener thread is already running

# --- Bluetooth keypad monitor ---
def check_keypad():
    if MODE == "PROD":
        try:
            result = subprocess.run(
                ["bluetoothctl", "info", "E4:5F:01:96:5F:8F"],  # replace MAC
                capture_output=True, text=True
            )
            if "Connected: yes" in result.stdout:
                status_label.config(text="Control device connected", fg="green")
            else:
                status_label.config(text="Control device not found. Please check battery.", fg="red")
        except Exception:
            status_label.config(text="Error checking device status.", fg="red")
        root.after(10000, check_keypad)  # re-check every 10s
    else:
        status_label.config(text="[DEV] Skipping Bluetooth check", fg="blue")

def setup_inputs():
    if MODE == "DEV":
        setup_bindings()
    elif MODE == "PROD":
        threading.Thread(target=keypad_listener, daemon=True).start()

# --- Tkinter UI ---
root = tk.Tk()
root.title("Magnifier Options")
root.geometry("400x250")

status_label = tk.Label(root, text="Initializing...", font=("Arial", 12))
status_label.pack(pady=10)

tk.Button(root, text="High Resolution (Reading)", width=30, command=launch_high).pack(pady=10)
tk.Button(root, text="Low Resolution (Embroidery)", width=30, command=launch_low).pack(pady=10)
tk.Button(root, text="Quit Landing", command=quit_landing).pack(pady=10)

setup_inputs()

# Intercept window close button 
# root.protocol("WM_DELETE_WINDOW", quit_landing)

# Start keypad monitor
check_keypad()

root.mainloop()



