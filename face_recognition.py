import cv2
import requests
import numpy as np
from deepface import DeepFace
from collections import deque

# ESP32-CAM IP
url = "http://172.20.10.10/capture"

# Nur diese 4 Emotionen zulassen
allowed_emotions = ["happy", "sad", "angry", "neutral"]

# Verlauf zur Glättung
emotion_history = deque(maxlen=5)

# Analyse nur alle X Frames
analyze_interval = 2

# Gesichtserkennungs-Backend
detector_backend = "mediapipe"  # Alternativen: ssd, retinaface

# Fenster erstellen
cv2.namedWindow("📷 Emotionserkennung Livestream", cv2.WINDOW_NORMAL)

frame_count = 0

# Mapping-Funktion zur Emotionserkennung
def map_emotion(emotions):
    # print("🎯 Emotion-Scores:", emotions)  # Debug-Ausgabe

    if emotions.get("angry", 0) > 30:
        return "angry"
    elif emotions.get("happy", 0) > 30:
        return "happy"
    elif emotions.get("sad", 0) + emotions.get("fear", 0) > 40:
        return "sad"
    elif emotions.get("neutral", 0) > 50:
        return "neutral"
    else:
        # Fallback: stärkste erlaubte Emotion wählen
        filtered = {k: emotions[k] for k in allowed_emotions}
        return max(filtered, key=filtered.get)

while True:
    try:
        # Bild abrufen
        response = requests.get(url, timeout=2)
        if response.status_code != 200:
            print("⚠️ Kein gültiges Bild erhalten")
            continue

        img_array = np.frombuffer(response.content, dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        if img is None:
            print("⚠️ Bild konnte nicht dekodiert werden")
            continue

        # Bild aufhellen
        img = cv2.convertScaleAbs(img, alpha=1.2, beta=20)

        # Drehen (je nach ESP32-Lage)
        img = cv2.rotate(img, cv2.ROTATE_180)

        # Analyse nur alle X Frames
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

                    emotions = face.get("emotion", {})
                    emotion = map_emotion(emotions)
                    emotion_history.append(emotion)

                    if w > 0 and h > 0:
                        # Gesicht umrahmen
                        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

                        # Sortierte Score-Liste erzeugen
                        sorted_emotions = sorted(
                            [(k, int(v)) for k, v in emotions.items() if k in allowed_emotions],
                            key=lambda x: x[1], reverse=True
                        )

                        # Emo-Scores anzeigen (max. 4 Zeilen)
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

            except Exception as e:
                print("⚠️ Emotionserkennung fehlgeschlagen:", e)

        # Emotion glätten
        if emotion_history:
            smoothed_emotion = max(set(emotion_history), key=emotion_history.count)
            cv2.putText(img, f"Emotion: {smoothed_emotion}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)

        # Anzeige
        cv2.imshow("📷 Emotionserkennung Livestream", img)
        frame_count += 1

        # ESC zum Beenden
        if cv2.waitKey(1) & 0xFF == 27:
            break

    except Exception as e:
        print("🔴 Fehler beim Abrufen oder Verarbeiten des Bildes:", e)

cv2.destroyAllWindows()