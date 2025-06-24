#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// Display config
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET    -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// Include the bitmap images
#include "happy.xbm"
#include "neutral.xbm"
#include "sad.xbm"
#include "angry.xbm"

void setup() {
  Serial.begin(115200);

  // Initialize the display
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("SSD1306 allocation failed");
    while (true);
  }

  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
}

void loop() {
  showEmotion(happy_face_eyebrows_bits, "Happy");
  delay(2000);

  showEmotion(neutral_face_eyebrows_bits, "Neutral");
  delay(2000);

  showEmotion(sad_face_eyebrows_bits, "Sad");
  delay(2000);

  showEmotion(angry_face_eyebrows_bits, "Angry");
  delay(2000);
}

void showEmotion(const unsigned char* bitmap, const char* label) {
  display.clearDisplay();

  // Center the bitmap horizontally (128 - 64) / 2 = 32
  display.drawBitmap(32, 0, bitmap, 64, 64, SSD1306_WHITE);

  // Draw label below the face
  display.setTextSize(1);
  display.setCursor((SCREEN_WIDTH - strlen(label) * 6) / 2, 54); // Rough centering
  display.print(label);

  display.display();
}