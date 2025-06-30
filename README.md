# EmotionLink 😄😢😠😐

AI-Powered Real-Time Emotion-to-Emoji Display with ESP32  
Final Year Project by Tim Fuhrmann, Arman Sargsyan, and Tikhon Antimenko

## 🔍 Project Overview

**EmotionLink** is a real-time facial expression recognition system that detects a user's emotions and displays a corresponding emoji on an OLED screen connected to an ESP32-CAM microcontroller.

The system combines modern AI tools (DeepFace and OpenCV) with embedded hardware to enable responsive, intuitive interaction. A Python script analyzes video input from a webcam or ESP32-CAM, classifies the facial emotion, and sends it via HTTP to the ESP32, which updates an OLED display accordingly.

## 📷 System Architecture

- **Input:** Live facial image from webcam or ESP32-CAM
- **Emotion Recognition:** Python with DeepFace and OpenCV
- **Communication:** Local network using HTTP GET requests
- **Output:** Emotion emoji + label on SSD1306 OLED display

---

## 🧩 Components Used

<p>
  <img src="https://github.com/excii05/EmotionLink/blob/main/images/circuit_diagram.png" width="560" height="auto">
</p>

| Component                | Purpose                                  |
|-------------------------|------------------------------------------|
| ESP32-CAM (AI Thinker)  | Receives and displays emotion data       |
| OLED Display (SSD1306)  | Visual output of emotion (emoji + text)  |
| FTDI Programmer         | Programming and powering ESP32-CAM       |
| Jumper Wires, Breadboard| Wiring and prototyping                   |
| Python (DeepFace, OpenCV)| Emotion recognition                     |
| WiFi Network            | Enables communication between devices    |

**OLED wiring:**  
- SDA → GPIO14  
- SCL → GPIO15  
- Powered via FTDI programmer during development.

---

## 🧠 Code Highlights

### 🌀 Emotion Smoothing
To reduce flickering and false positives:
```python
emotion_history = deque(maxlen=5)
emotion_history.append(emotion)
smoothed_emotion = max(set(emotion_history), key=emotion_history.count)
```

### 🧍‍♂️ Face Tracking
Switches from detection to tracking for performance:
```python
if w > 60 and h > 60:
    tracking_box = (x, y, w, h)
    tracker = cv2.TrackerKCF_create()
    tracker.init(img, tracking_box)
```

### 🌐 ESP32 HTTP Server
ESP32 acts as a lightweight webserver:
```cpp
String emotion = server.arg("value");
if (emotion == "happy") {
    showEmotion(happy_face_bits, "Happy");
}
```
