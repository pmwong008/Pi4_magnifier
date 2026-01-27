#!/usr/bin/env python3
"""
Pi4 Magnifier with OpenCV window + Bluetooth Keypad/Keyboard Control + FPS overlay
"""

import cv2
import time
from evdev import InputDevice, categorize, ecodes
import threading

# --- Camera setup ---
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)

zoom_level = 1.0
running = True

# FPS tracking
last_time = time.time()
frame_count = 0
fps = 0

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

# --- Keypad/keyboard listener ---
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

# --- Main loop ---
def run_magnifier():
    global running, frame_count, last_time, fps
    cv2.namedWindow("Magnifier", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Magnifier", 1280, 720)

    while running:
        ret, frame = cap.read()
        if not ret:
            print("No frame captured")
            break

        h, w = frame.shape[:2]
        center = (w // 2, h // 2)
        zoom_w, zoom_h = int(w / zoom_level), int(h / zoom_level)
        x1, y1 = center[0] - zoom_w // 2, center[1] - zoom_h // 2
        x2, y2 = x1 + zoom_w, y1 + zoom_h
        cropped = frame[y1:y2, x1:x2]
        resized = cv2.resize(cropped, (w, h))

        # FPS calculation
        frame_count += 1
        if frame_count >= 10:
            current_time = time.time()
            fps = frame_count / (current_time - last_time)
            last_time = current_time
            frame_count = 0

        # Overlay FPS
        cv2.putText(resized, f"FPS: {fps:.1f}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Magnifier", resized)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            running = False
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    threading.Thread(target=keypad_listener, args=("/dev/input/event0",), daemon=True).start()
    run_magnifier()
