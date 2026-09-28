# High-Accuracy AI Virtual Mouse

A contactless, gesture-driven computer vision mouse pointer implementation using **Python**, **OpenCV**, and **MediaPipe**. This project leverages hand landmark tracking and advanced Exponential Moving Average (EMA) filtering to provide smooth cursor navigation, clicking, delta-proportional scrolling, and dynamic pinch-to-zoom controls via your webcam with zero pipeline-blocking delays.

## 🚀 Features

- **Adaptive Cursor Tracking:** High-speed, responsive Exponential Moving Average (EMA) filters remove micro-jitters while adapting to hand movement velocity.
- **Dynamic Touch Pad Boundaries:** Utilizes a localized camera viewport box, allowing you to reach absolute display edges comfortably.
- **Hysteresis Clicking Safeguard:** Automatically locks your cursor position securely mid-pinch to prevent pixel drifting during a tap event.
- **Proportional Delta Scrolling:** Tracks relative frame-to-frame movements rather than static coordinates, making list navigation smooth and natural.
- **Dynamic Pinch-to-Zoom:** Simulates smartphone pinch controls natively across web browsers and system views.

---

## 🎮 Gesture Reference Guide

| Action | Finger Configuration | Technical Mechanic |
| :--- | :--- | :--- |
| **Move Cursor** | **Index Finger Up** (Others curled into palm) | Maps the Index Tip position inside the UI bounding box to screen space coordinates. |
| **Left Click** | **Index + Middle Pinch** (Bring tips close together) | Calculates hand-scale normalized distances; includes a non-blocking 120ms tap buffer. |
| **Scroll Up / Down** | **Index + Middle + Ring Up** (Move hand up/down) | Measures physical translation speed deltas between frames to throttle scrolling speed. |
| **Zoom In / Out** | **Thumb + Index Distance** (Pinch close / Spread wide) | Modulates native system keystroke hooks (`Ctrl` + Scroll wheel) seamlessly. |

---

## ⚙️ Prerequisites & Installation

### 1. Clone the Repository
```bash
git clone https://github.com
cd ai-virtual-mouse
```

### 2. Environment Setup
To ensure total API compatibility and prevent protobuf/numpy mismatch crashes, install the dependencies using the version matrix below:

```bash
pip install opencv-python pyautogui
pip install "mediapipe<0.10.30"
pip install --upgrade "protobuf<5" "numpy>=1.26.0,<2"
```

---

## 💻 How to Run

Execute the main controller pipeline script from your project directory terminal:

```bash
python virtual_mouse.py
```

### Usage Tips:
- Press the **`Q`** key on your keyboard while focusing on the camera window feed to gracefully release hardware resources and close the application safely.
- For optimal gesture interpretation metrics, operate in a cleanly lit environment where your hand is front-facing rather than backlit.

---

## 🛠️ Project Structure
```text
├── virtual_mouse.py    # Core application pipeline script containing handling logic
└── README.md           # Project documentation and control guide
```
