#include "secrets.h"
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include "WiFi.h"
#include <Wire.h>

#define echoPin 12
#define trigPin 13

#define AWS_IOT_PUBLISH_TOPIC   "water1/pub"
#define AWS_IOT_SUBSCRIBE_TOPIC "esp32/sub"
 
long duration, distance;
const char* deviceId = "1";
 
WiFiClientSecure net = WiFiClientSecure();
PubSubClient client(net);
 
void connectAWS(){
  // creds to log onto wifi
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
 
  Serial.println("Connecting to Wi-Fi");
 
  while (WiFi.status() != WL_CONNECTED){
    delay(500);
    Serial.print(".");
  }
 
  // creds to log onto AWS
  net.setCACert(AWS_CERT_CA);
  net.setCertificate(AWS_CERT_CRT);
  net.setPrivateKey(AWS_CERT_PRIVATE);
  client.setServer(AWS_IOT_ENDPOINT, 8883);
 
  // Create a message handler
  client.setCallback(messageHandler);
 
  Serial.println("Connecting to AWS IoT");
 
  while (!client.connect(THINGNAME)){
    Serial.print(".");
    delay(100);
  }
 
  // catch disconnect
  if (!client.connected()){
    Serial.println("AWS IoT Timeout!");
    return;
  }
 
  // Subscribe to the topic
  client.subscribe(AWS_IOT_SUBSCRIBE_TOPIC);
 
  Serial.println("AWS IoT Connected!");
}
 
void publishMessage(){
  String jsonPayload = "{\"distance\":" + String(distance) + "}";
  
  // Convert to char array to publish
  char jsonBuffer[512];
  jsonPayload.toCharArray(jsonBuffer, sizeof(jsonBuffer));

  client.publish(AWS_IOT_PUBLISH_TOPIC, jsonBuffer);
}
 
// for later if multiple devices / drums needed to talk to eachother
void messageHandler(char* topic, byte* payload, unsigned int length){
  Serial.print("incoming: ");
  Serial.println(topic);

  // Convert payload to a string for printing
  String message = "";
  for (unsigned int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.println("Message: " + message);
}
 
void setup(){
  Serial.begin(9600);
  delay(2000);
  connectAWS();

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  delayMicroseconds(2);

}
 
void loop(){
  // Make sure the device is still connected to AWS/wifi
  if (!client.connected()) {
    connectAWS();
  }

  // measure distance of water level from the sensor
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  duration = pulseIn(echoPin, HIGH);

  // Check if any reads failed and exit early (to try again).
  if (isnan(duration)){
    Serial.println(F("Failed to read from sensor!"));
    delay(60);
    return;
  }

  // Calculate distance (in inches)
  distance = duration / 58.2;

  // Print distance ton console
  Serial.print("Distance: ");
  Serial.print(distance);
  Serial.println(" cm");
 
  // Publish distance to AWS IoT
  publishMessage();

  delay(1000);
  client.loop();
}
