import cv2
import requests
import numpy as np
from deepface import DeepFace
from collections import deque

# ESP32-CAM IP
url = "http://172.20.10.10/capture"

# Emotionen, die du anzeigen möchtest
allowed_emotions = ["happy", "sad", "angry", "neutral"]

# Verlauf zur Glättung der Ergebnisse
emotion_history = deque(maxlen=5)

# Nur alle X Frames analysieren
analyze_interval = 2  # kleinere Zahl = flüssiger

# Bessere Gesichtserkennung verwenden
detector_backend = "mediapipe"  # Options: "mediapipe", "ssd", "retinaface"

# Fenster vorbereiten
cv2.namedWindow("📷 Emotionserkennung Livestream", cv2.WINDOW_NORMAL)

frame_count = 0

while True:
    try:
        # Kamera-Bild abrufen
        response = requests.get(url, timeout=2)
        if response.status_code != 200:
            print("⚠️ Kein gültiges Bild erhalten")
            continue

        img_array = np.frombuffer(response.content, dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        if img is None:
            print("⚠️ Bild konnte nicht dekodiert werden")
            continue

        # Bild ggf. aufhellen für bessere Erkennung
        img = cv2.convertScaleAbs(img, alpha=1.2, beta=20)

        # Bild ggf. drehen (ESP32 liefert es oft kopfüber)
        img = cv2.rotate(img, cv2.ROTATE_180)

        # Nur alle X Frames analysieren
        if frame_count % analyze_interval == 0:
            try:
                result = DeepFace.analyze(
                    img,
                    actions=["emotion"],
                    detector_backend=detector_backend,
                    enforce_detection=False
                )

                for face in result:
                    region = face.get("region", {})
                    x, y, w, h = region.get("x", 0), region.get("y", 0), region.get("w", 0), region.get("h", 0)

                    raw_emotion = face.get("dominant_emotion", "neutral")
                    emotion = raw_emotion if raw_emotion in allowed_emotions else "neutral"
                    emotion_history.append(emotion)

                    # Gesicht markieren, wenn Position valide
                    if w > 0 and h > 0:
                        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

            except Exception as e:
                print("⚠️ Emotionserkennung fehlgeschlagen:", e)

        # Glättung der Emotionen: häufigste der letzten Frames
        if emotion_history:
            smoothed_emotion = max(set(emotion_history), key=emotion_history.count)
            cv2.putText(img, f"Emotion: {smoothed_emotion}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 0), 2)

        # Anzeige
        cv2.imshow("📷 Emotionserkennung Livestream", img)
        frame_count += 1

        # Beenden mit ESC
        if cv2.waitKey(1) & 0xFF == 27:
            break

    except Exception as e:
        print("🔴 Fehler beim Abrufen oder Verarbeiten des Bildes:", e)

cv2.destroyAllWindows()