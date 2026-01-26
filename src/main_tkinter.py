#!/usr/bin/env python3
"""
Pi4 Magnifier with Tkinter-embedded video + Bluetooth Keypad Control
"""

import cv2
import tkinter as tk
from PIL import Image, ImageTk
from evdev import InputDevice, categorize, ecodes
import threading

root = tk.Tk()
root.title("Pi4 Magnifier (Tkinter Embedded)")

cap = cv2.VideoCapture(0)
zoom_level = 1.0

video_label = tk.Label(root)
video_label.pack()

def update_frame():
    global zoom_level
    ret, frame = cap.read()
    if ret:
        h, w = frame.shape[:2]
        center = (w // 2, h // 2)
        zoom_w, zoom_h = int(w / zoom_level), int(h / zoom_level)
        x1, y1 = center[0] - zoom_w // 2, center[1] - zoom_h // 2
        x2, y2 = x1 + zoom_w, y1 + zoom_h
        cropped = frame[y1:y2, x1:x2]
        resized = cv2.resize(cropped, (w, h))

        # Convert BGR → RGB → PIL → Tkinter
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb)
        imgtk = ImageTk.PhotoImage(image=img)

        video_label.imgtk = imgtk
        video_label.configure(image=imgtk)
    root.after(30, update_frame)

def zoom_in():
    global zoom_level
    zoom_level = min(zoom_level + 0.1, 3.0)
    print("Zoom in:", zoom_level)

def zoom_out():
    global zoom_level
    zoom_level = max(zoom_level - 0.1, 1.0)
    print("Zoom out:", zoom_level)

def reset_zoom():
    global zoom_level
    zoom_level = 1.0
    print("Reset zoom")

def keypad_listener(event_path="/dev/input/eventX"):
    try:
        dev = InputDevice(event_path)
        print(f"Listening on {dev.path} ({dev.name})")
    except Exception as e:
        print(f"Error opening device {event_path}: {e}")
        return

    for event in dev.read_loop():
        if event.type == ecodes.EV_KEY:
            key_event = categorize(event)
            if key_event.keystate == key_event.key_down:
                if key_event.keycode == 'KEY_KPPLUS':
                    root.after(0, zoom_in)
                elif key_event.keycode == 'KEY_KPMINUS':
                    root.after(0, zoom_out)
                elif key_event.keycode == 'KEY_KP0':
                    root.after(0, reset_zoom)

if __name__ == "__main__":
    threading.Thread(target=keypad_listener, args=("/dev/input/eventX",), daemon=True).start()
    root.after(0, update_frame)
    root.mainloop()
    cap.release()
    cv2.destroyAllWindows()
