import cv2
import requests
import numpy as np

# ESP32-CAM URL
url = "http://172.20.10.10/capture"  # ← IP-Adresse anpassen!

# Gesichtserkennungs-Modell von OpenCV laden
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

while True:
    try:
        # Bild von ESP32 abrufen
        response = requests.get(url)
        img_array = np.frombuffer(response.content, dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        # In Graustufen umwandeln
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Gesichter erkennen
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

        # Rechtecke über erkannte Gesichter zeichnen
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Bild anzeigen
        cv2.imshow("Gesichtserkennung", img)

        # Mit ESC abbrechen
        if cv2.waitKey(1) == 27:
            break

    except Exception as e:
        print("Fehler beim Abrufen oder Verarbeiten:", e)

cv2.destroyAllWindows()