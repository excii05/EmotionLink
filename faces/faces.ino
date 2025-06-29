#include <WiFi.h>
#include <WebServer.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include "happy.xbm"
#include "neutral.xbm"
#include "sad.xbm"
#include "angry.xbm"

// WLAN-Zugangsdaten
const char* ssid = "iPhone 16 Pro Tim";
const char* password = "Tim100205";

// Display Setup
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET    -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// Webserver auf Port 80
WebServer server(80);

void setup() {
  Serial.begin(115200);
  Wire.begin(14, 15); // SDA = GPIO14, SCL = GPIO15 (ESP32 CAM)
  display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  display.clearDisplay();
  display.display();

  // WLAN verbinden
  WiFi.begin(ssid, password);
  Serial.print("Verbinde mit WLAN");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nVerbunden mit IP: " + WiFi.localIP().toString());

  // HTTP-Handler
  server.on("/emotion", handleEmotion);
  server.begin();
}

void loop() {
  server.handleClient();
}

void handleEmotion() {
  String emotion = server.arg("value");
  Serial.println("Empfangene Emotion: " + emotion);

  if (emotion == "happy") {
    showEmotion(happy_face_bits, "Happy");
  } else if (emotion == "neutral") {
    showEmotion(neutral_face_bits, "Neutral");
  } else if (emotion == "sad") {
    showEmotion(sad_face_bits, "Sad");
  } else if (emotion == "angry") {
    showEmotion(angry_face_bits, "Angry");
  } else {
    showEmotion(nullptr, "Unknown");
  }

  server.send(200, "text/plain", "OK");
}

void showEmotion(const unsigned char* bitmap, const char* label) {
  display.clearDisplay();
  if (bitmap != nullptr)
    display.drawBitmap(32, 0, bitmap, 64, 64, SSD1306_WHITE);

  display.setTextSize(1);
  display.setCursor((SCREEN_WIDTH - strlen(label) * 6) / 2, 54);
  display.print(label);
  display.display();
}