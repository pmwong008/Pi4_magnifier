import cv2
import tkinter as tk
from PIL import Image, ImageTk

# Initialize webcam (0 = first camera)
cap = cv2.VideoCapture(0)

# Create Tkinter window
root = tk.Tk()
root.title("Pi4 Magnifier Test")

# Label to hold video frames
label = tk.Label(root)
label.pack()

def update_frame():
    ret, frame = cap.read()
    if ret:
        # Convert OpenCV BGR → RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Convert to PIL Image
        img = Image.fromarray(frame)
        # Convert to Tkinter Image
        imgtk = ImageTk.PhotoImage(image=img)
        label.imgtk = imgtk
        label.configure(image=imgtk)
    # Schedule next frame update
    root.after(10, update_frame)

# Start loop
update_frame()
root.mainloop()

# Release camera when window closes
cap.release()
cv2.destroyAllWindows()
