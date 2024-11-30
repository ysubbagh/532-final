#include "secrets.h"
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include "WiFi.h"
#include <Wire.h>
#include <esp_sleep.h>

#define echoPin 12
#define trigPin 13
#define AWS_IOT_PUBLISH_TOPIC "water1/pub"
#define AWS_IOT_SUBSCRIBE_TOPIC "esp32/sub"

#define SLEEP_INTERVAL 1800e6  // 30 minutes in microseconds
#define TWENTY_SECONDS 20000 // 20 seconds in microseconds

long duration, distance;
const char* deviceId = "1";

WiFiClientSecure net = WiFiClientSecure();
PubSubClient client(net);

void connectAWS() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  // connect to internet
  Serial.println("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  // creds
  net.setCACert(AWS_CERT_CA);
  net.setCertificate(AWS_CERT_CRT);
  net.setPrivateKey(AWS_CERT_PRIVATE);
  client.setServer(AWS_IOT_ENDPOINT, 8883);
  client.setCallback(messageHandler);

  // connect to aws
  Serial.println("Connecting to AWS IoT");
  while (!client.connect(THINGNAME)) {
    Serial.print(".");
    delay(100);
  }

  if (!client.connected()) {
    Serial.println("AWS IoT Timeout!");
    return;
  }

  // get onto correct channel
  client.subscribe(AWS_IOT_SUBSCRIBE_TOPIC);
  Serial.println("AWS IoT Connected!");
}

// join data and make JSON to send to aws
void publishMessage() {
  String jsonPayload = "{\"distance\":" + String(distance) + "}";
  char jsonBuffer[512];
  jsonPayload.toCharArray(jsonBuffer, sizeof(jsonBuffer));
  client.publish(AWS_IOT_PUBLISH_TOPIC, jsonBuffer);
}

// for incoming messages from another devoce
void messageHandler(char* topic, byte* payload, unsigned int length) {
  Serial.print("incoming: ");
  Serial.println(topic);
  String message = "";
  for (unsigned int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.println("Message: " + message);
}

void setup() {
  Serial.begin(9600);
  delay(2000);

  // connect to internet and AWS
  connectAWS();

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

}


void loop() {
  // get distance via time
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  duration = pulseIn(echoPin, HIGH);

  if (isnan(duration)) {
    Serial.println(F("Failed to read from sensor!"));
    return;
  }

  distance = duration / 58.2;  // Calculate distance in cm

  Serial.print("Distance: ");
  Serial.print(distance);
  Serial.println(" cm");

  // post to aws
  publishMessage();
  delay(TWENTY_SECONDS);  // to stay within free tier, wait 20 seconds
  client.loop();
}