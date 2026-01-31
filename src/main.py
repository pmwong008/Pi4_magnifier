#!/usr/bin/env python3
"""
Magnifier App with OpenCV window + Bluetooth Keypad Control
Accepts resolution argument from landing.py
"""

import cv2
import argparse
import threading
from evdev import InputDevice, categorize, ecodes

# --- Parse resolution argument ---
parser = argparse.ArgumentParser()
parser.add_argument("--res", default="800x450", help="Resolution WxH")
args = parser.parse_args()
w, h = map(int, args.res.split("x"))

# --- Camera setup ---
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)

zoom_level = 1.0
running = True

# --- Zoom controls ---
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

def quit_magnifier():
    global running
    print("Magnifier quit requested")
    running = False
    cv2.destroyAllWindows()

# --- Keypad listener ---
def keypad_listener(event_path="/dev/input/event0"):
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
                if key_event.keycode in ('KEY_KPPLUS', 'KEY_EQUAL'):
                    zoom_in()
                elif key_event.keycode in ('KEY_KPMINUS', 'KEY_MINUS'):
                    zoom_out()
                elif key_event.keycode in ('KEY_KP0', 'KEY_0'):
                    reset_zoom()
                elif key_event.keycode in ('KEY_ESC', 'KEY_KPENTER'):
                    running = False
                    break


# --- Main loop ---
def run_magnifier():
    global running
    cv2.namedWindow("Magnifier", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Magnifier", w, h)

    while running:
        ret, frame = cap.read()
        if not ret:
            print("No frame captured")
            break

        h_frame, w_frame = frame.shape[:2]
        center = (w_frame // 2, h_frame // 2)
        zoom_w, zoom_h = int(w_frame / zoom_level), int(h_frame / zoom_level)
        x1, y1 = center[0] - zoom_w // 2, center[1] - zoom_h // 2
        x2, y2 = x1 + zoom_w, y1 + zoom_h
        cropped = frame[y1:y2, x1:x2]
        resized = cv2.resize(cropped, (w_frame, h_frame))

        cv2.imshow("Magnifier", resized)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            quit_magnifier()


    cap.release()
    # cv2.destroyAllWindows()

if __name__ == "__main__":
    threading.Thread(target=keypad_listener, args=("/dev/input/event0",), daemon=True).start()
    run_magnifier()
