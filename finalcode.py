import threading
import cv2
import time
import os
from ultralytics import YOLO
import pyautogui
import tkinter as tk
import numpy as np
from pathlib import Path

# Disable PyAutoGUI fail-safe
pyautogui.FAILSAFE = False

# Get the absolute path to the model
script_dir = Path(__file__).parent
model_path = script_dir.parent / "model" / "train (1)" / "weights" / "best.pt"

# Load trained YOLO model with error handling
try:
    model = YOLO(str(model_path))
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
    exit(1)

# Create a global reference for the keyboard instance
keyboard = None
keyboard_ready = threading.Event()

# Virtual Keyboard Class
class VirtualKeyboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Virtual Keyboard")
        self.root.geometry("900x450")
        self.root.configure(bg="black")
        
        # Make window stay on top
        self.root.attributes('-topmost', True)

        # Text display box
        self.text_display = tk.Entry(root, font=("Arial", 20), width=50, justify="center")
        self.text_display.grid(row=0, column=0, columnspan=12, pady=10)

        # Full keyboard layout with better spacing
        self.keys = [
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '='],
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '[', ']'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ';', "'", "Enter"],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.', '/', 'Space', 'Backspace']
        ]

        self.labels = []
        self.selected_key = None
        self.last_highlighted = None

        # Create Keyboard UI
        for row_index, row in enumerate(self.keys):
            row_labels = []
            for col_index, key in enumerate(row):
                # Adjust width for special keys
                width = 8 if key in ["Space", "Enter", "Backspace"] else 5
                lbl = tk.Label(root, text=key, font=("Arial", 12), width=width, height=2, 
                              relief="raised", bg="lightgray", fg="black")
                lbl.grid(row=row_index + 1, column=col_index, padx=2, pady=2)
                row_labels.append(lbl)
            self.labels.append(row_labels)

    def highlight_key(self, row, col):
        """Highlights a key when the pointer moves over it"""
        try:
            # Reset previous highlight
            if self.last_highlighted:
                self.last_highlighted.config(bg="lightgray")
            
            # Bounds checking
            if 0 <= row < len(self.labels) and 0 <= col < len(self.labels[row]):
                self.selected_key = self.labels[row][col]
                self.selected_key.config(bg="yellow")
                self.last_highlighted = self.selected_key
        except (IndexError, tk.TclError):
            pass  # Handle any GUI errors gracefully

    def click_key(self):
        """Simulate a key press when the click gesture is detected"""
        if self.selected_key:
            try:
                key = self.selected_key.cget("text")
                current_text = self.text_display.get()
                
                if key == "Space":
                    self.text_display.insert(tk.END, " ")
                elif key == "Enter":
                    print(f"Typed text: {current_text}")
                    self.text_display.delete(0, tk.END)
                elif key == "Backspace":
                    if current_text:
                        self.text_display.delete(len(current_text) - 1, tk.END)
                else:
                    self.text_display.insert(tk.END, key)
                    
                # Visual feedback for key press
                self.selected_key.config(bg="red")
                self.root.after(200, lambda: self.selected_key.config(bg="yellow"))
            except tk.TclError:
                pass  # Handle any GUI errors gracefully

# Function to start Tkinter keyboard in a separate thread
def start_keyboard():
    global keyboard
    try:
        root = tk.Tk()
        keyboard = VirtualKeyboard(root)
        keyboard_ready.set()  # Signal that keyboard is ready
        root.mainloop()
    except Exception as e:
        print(f"Error starting keyboard: {e}")

# Start Tkinter keyboard in a separate thread
keyboard_thread = threading.Thread(target=start_keyboard, daemon=True)
keyboard_thread.start()

# Wait for keyboard to be ready
keyboard_ready.wait(timeout=5)
if not keyboard_ready.is_set():
    print("Warning: Keyboard failed to initialize")

# Open webcam with error handling
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open webcam")
    exit(1)
    
cap.set(3, 640)  # Set width
cap.set(4, 480)  # Set height
cap.set(cv2.CAP_PROP_FPS, 30)  # Ensure 30 FPS for smooth performance

# Get screen size for mouse control
screen_width, screen_height = pyautogui.size()

# Gesture control variables
last_click_time = 0
click_delay = 0.5  # Minimum time between clicks

while cap.isOpened():
    start_time = time.time()  # Track time for FPS calculation

    ret, frame = cap.read()
    if not ret:
        break

    # Mirror the frame horizontally for natural interaction
    frame = cv2.flip(frame, 1)    # Run YOLO model on the frame
    results = model(frame)

    detected_gestures = []  # Store detected gestures in this frame
    best_detection = None
    highest_confidence = 0

    # Find the gesture with highest confidence
    for r in results:
        if r.boxes is not None:
            for box in r.boxes:
                confidence = float(box.conf[0])
                if confidence > highest_confidence:
                    highest_confidence = confidence
                    x1, y1, x2, y2 = map(int, box.xyxy[0])  # Bounding box
                    hand_center_x = (x1 + x2) // 2  # Center X of hand
                    hand_center_y = (y1 + y2) // 2  # Center Y of hand
                    label = r.names[int(box.cls[0])]  # Get detected gesture name
                    
                    best_detection = {
                        'label': label,
                        'bbox': (x1, y1, x2, y2),
                        'center': (hand_center_x, hand_center_y),
                        'confidence': confidence
                    }

    # Process only the best detection if it exists
    if best_detection:
        detected_gestures.append(best_detection['label'])
        x1, y1, x2, y2 = best_detection['bbox']
        hand_center_x, hand_center_y = best_detection['center']
        label = best_detection['label']    # Process only the best detection if it exists
    if best_detection:
        detected_gestures.append(best_detection['label'])
        x1, y1, x2, y2 = best_detection['bbox']
        hand_center_x, hand_center_y = best_detection['center']
        label = best_detection['label']

        # **Keyboard Control (Pointing & Click)**
        if keyboard and label == "pointing":
            # Map hand position to keyboard grid with better bounds checking
            keyboard_x = max(0, min(hand_center_x, 640))
            keyboard_y = max(0, min(hand_center_y, 480))
            
            # Normalize to keyboard dimensions
            col = int((keyboard_x / 640) * len(keyboard.keys[0]))
            row = int((keyboard_y / 480) * len(keyboard.keys))
            
            # Ensure we stay within bounds
            row = max(0, min(row, len(keyboard.labels) - 1))
            if row < len(keyboard.labels):
                col = max(0, min(col, len(keyboard.labels[row]) - 1))
                keyboard.highlight_key(row, col)

        if keyboard and label == "click":
            current_time = time.time()
            if current_time - last_click_time > click_delay:
                keyboard.click_key()
                last_click_time = current_time

        # **Mouse Control - Only for non-keyboard gestures**
        if label == "left click":
            current_time = time.time()
            if current_time - last_click_time > click_delay:
                pyautogui.click(button='left')
                last_click_time = current_time

        elif label == "right click":
            current_time = time.time()
            if current_time - last_click_time > click_delay:
                pyautogui.click(button='right')
                last_click_time = current_time

        elif label == "scroll up":
            pyautogui.scroll(3)

        elif label == "scroll down":
            pyautogui.scroll(-3)

        elif label == "zoom in":
            pyautogui.hotkey('ctrl', '+')

        elif label == "zoom out":
            pyautogui.hotkey('ctrl', '-')

        elif label == "pointing":
            # Map hand position to screen coordinates for mouse control
            screen_x = int((hand_center_x / 640) * screen_width)
            screen_y = int((hand_center_y / 480) * screen_height)
            pyautogui.moveTo(screen_x, screen_y, duration=0.05)

        # Draw bounding box on detected hand
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Show FPS and detected gestures on frame
    fps = 1 / max(time.time() - start_time, 0.001)
    cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(frame, f"Gestures: {', '.join(detected_gestures)}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    cv2.imshow("Gesture Control (Keyboard + Mouse)", frame)

    # Maintain frame rate
    end_time = time.time()
    elapsed_time = end_time - start_time
    time.sleep(max(0, (1 / 30) - elapsed_time))  

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
