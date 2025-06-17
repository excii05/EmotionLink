#include <WiFi.h>
#include <WiFiClient.h>
#include <WebServer.h>
#include "esp_camera.h"
#include "esp_http_server.h"

// WLAN-Zugangsdaten
const char* ssid = "iPhone 16 Pro Tim";
const char* password = "Tim100205";

// Kamera-Pin-Definitionen für ESP32-CAM (AI-Thinker-Modul)
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM     0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27

#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM       5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

void startCameraServer();  // Wird später definiert

void connectToWiFi() {
  WiFi.begin(ssid, password);
  Serial.print("Verbinde mit WLAN");

  int retries = 0;
  while (WiFi.status() != WL_CONNECTED && retries < 20) {
    delay(500);
    Serial.print(".");
    retries++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✅ WLAN verbunden");
    Serial.print("📡 IP-Adresse: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n❌ WLAN-Verbindung fehlgeschlagen – Neustart...");
    delay(2000);
    ESP.restart();
  }
}

void setupCamera() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer   = LEDC_TIMER_0;
  config.pin_d0       = Y2_GPIO_NUM;
  config.pin_d1       = Y3_GPIO_NUM;
  config.pin_d2       = Y4_GPIO_NUM;
  config.pin_d3       = Y5_GPIO_NUM;
  config.pin_d4       = Y6_GPIO_NUM;
  config.pin_d5       = Y7_GPIO_NUM;
  config.pin_d6       = Y8_GPIO_NUM;
  config.pin_d7       = Y9_GPIO_NUM;
  config.pin_xclk     = XCLK_GPIO_NUM;
  config.pin_pclk     = PCLK_GPIO_NUM;
  config.pin_vsync    = VSYNC_GPIO_NUM;
  config.pin_href     = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn     = PWDN_GPIO_NUM;
  config.pin_reset    = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;

  if(psramFound()){
    config.frame_size = FRAMESIZE_VGA;
    config.jpeg_quality = 10;
    config.fb_count = 2;
  } else {
    config.frame_size = FRAMESIZE_QVGA;
    config.jpeg_quality = 12;
    config.fb_count = 1;
  }

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("❌ Kamerainitialisierung fehlgeschlagen: 0x%x\n", err);
    delay(3000);
    ESP.restart();
  }

  Serial.println("📷 Kamera bereit");
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  connectToWiFi();
  setupCamera();
  startCameraServer();  // Webserver starten
}

void loop() {
  delay(10000);  // keine Aufgabe in loop
}

// ==== Kamera-Server starten ====
#include "esp_http_server.h"

esp_err_t captureHandler(httpd_req_t *req) {
  camera_fb_t *fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("❌ Kamera-Frame nicht erhalten");
    httpd_resp_send_500(req);
    return ESP_FAIL;
  }

  httpd_resp_set_type(req, "image/jpeg");
  httpd_resp_send(req, (const char *)fb->buf, fb->len);
  esp_camera_fb_return(fb);
  return ESP_OK;
}

void startCameraServer() {
  httpd_config_t config = HTTPD_DEFAULT_CONFIG();
  httpd_uri_t uri = {
    .uri       = "/capture",
    .method    = HTTP_GET,
    .handler   = captureHandler,
    .user_ctx  = NULL
  };

  httpd_handle_t server = NULL;
  if (httpd_start(&server, &config) == ESP_OK) {
    httpd_register_uri_handler(server, &uri);
    Serial.println("🟢 Kamera-Server läuft auf /capture");
  } else {
    Serial.println("❌ Fehler beim Starten des Webservers");
  }
}