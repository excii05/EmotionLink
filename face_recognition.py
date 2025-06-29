import cv2
import requests
import numpy as np
from deepface import DeepFace
from collections import deque

# Kameraquelle wählen
use_esp_cam = False
esp_url = "http://172.20.10.10/capture"

allowed_emotions = ["happy", "sad", "angry", "neutral"]
emotion_history = deque(maxlen=5)
box_history = deque(maxlen=3)

analyze_interval = 2
detector_backend = "ssd" # Alternativen: mediapipe, mtcnn, ssd, opencv, retinaface

cv2.namedWindow("📷 Emotionserkennung Livestream", cv2.WINDOW_NORMAL)
frame_count = 0

# Emotion-Mapping
def map_emotion(emotions):
    if emotions.get("angry", 0) > 30:
        return "angry"
    elif emotions.get("happy", 0) > 30:
        return "happy"
    elif emotions.get("sad", 0) + emotions.get("fear", 0) > 20:
        return "sad"
    elif emotions.get("neutral", 0) > 50:
        return "neutral"
    else:
        filtered = {k: emotions[k] for k in allowed_emotions}
        return max(filtered, key=filtered.get)

# Webcam öffnen
if not use_esp_cam:
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("🎥 Webcam konnte nicht geöffnet werden")

# Tracker & Status
tracker = None
tracking = False
tracking_box = None
tracking_fail_count = 0
last_emotions = {}

while True:
    try:
        if use_esp_cam:
            response = requests.get(esp_url, timeout=2)
            if response.status_code != 200:
                print("⚠️ Kein gültiges Bild erhalten")
                continue
            img_array = np.frombuffer(response.content, dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            if img is None:
                print("⚠️ Bild konnte nicht dekodiert werden")
                continue
            img = cv2.rotate(img, cv2.ROTATE_180)
        else:
            ret, img = cap.read()
            if not ret:
                print("⚠️ Kein Bild von Webcam erhalten")
                continue

        # ESP-Bild aufbereiten
        if use_esp_cam:
            img = cv2.resize(img, (img.shape[1]*2, img.shape[0]*2), interpolation=cv2.INTER_CUBIC)
            lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            cl = clahe.apply(l)
            limg = cv2.merge((cl, a, b))
            img = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
            img = cv2.convertScaleAbs(img, alpha=1.2, beta=20)

        # Alle X Frames analysieren
        if frame_count % analyze_interval == 0:
            try:
                result = DeepFace.analyze(
                    img,
                    actions=["emotion"],
                    detector_backend=detector_backend,
                    enforce_detection=True,
                )

                for face in result:
                    region = face.get("region", {})
                    x, y, w, h = region.get("x", 0), region.get("y", 0), region.get("w", 0), region.get("h", 0)
                    emotions = face.get("emotion", {})
                    last_emotions = emotions
                    emotion = map_emotion(emotions)
                    emotion_history.append(emotion)

                    # Nur sinnvolle Boxen
                    if w > 60 and h > 60:
                        tracking_box = (x, y, w, h)
                        tracker = cv2.TrackerKCF_create()
                        tracker.init(img, tracking_box)
                        tracking = True
                        tracking_fail_count = 0
                        box_history.append(tracking_box)

            except Exception as e:
                print("⚠️ Emotionserkennung fehlgeschlagen:", e)

        # Tracking verwenden, wenn aktiv
        if tracking and tracker is not None:
            success, box = tracker.update(img)
            if success:
                x, y, w, h = [int(v) for v in box]
                box_history.append((x, y, w, h))
            else:
                tracking_fail_count += 1
                if tracking_fail_count > 5:
                    tracking = False
                    tracker = None

        # Durchschnittliche Box berechnen
        if box_history:
            avg_box = np.mean(box_history, axis=0).astype(int)
            x, y, w, h = avg_box
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Emo-Scores anzeigen
            if last_emotions:
                sorted_emotions = sorted(
                    [(k, int(v)) for k, v in last_emotions.items() if k in allowed_emotions],
                    key=lambda x: x[1], reverse=True
                )

                for i, (emo, score) in enumerate(sorted_emotions[:4]):
                    cv2.putText(
                        img,
                        f"{emo}: {score}%",
                        (x + w + 20, y + 15 + i * 25),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.0,
                        (0, 0, 255),
                        2
                    )

        # Emotion glätten & anzeigen
        if emotion_history:
            smoothed_emotion = max(set(emotion_history), key=emotion_history.count)
            cv2.putText(img, f"Emotion: {smoothed_emotion}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)

        # Anzeige
        cv2.imshow("📷 Emotionserkennung Livestream", img)
        frame_count += 1

        if cv2.waitKey(1) & 0xFF == 27:  # ESC
            break

    except Exception as e:
        print("🔴 Fehler beim Abrufen oder Verarbeiten des Bildes:", e)

if not use_esp_cam:
    cap.release()
cv2.destroyAllWindows()