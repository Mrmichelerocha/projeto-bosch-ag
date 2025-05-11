
#include "agent.h"
#include <ESP8266WebServer.h>
#include <ArduinoJson.h>

extern ESP8266WebServer server;
extern DynamicJsonDocument beliefsJsonDoc;

Action::Action(int pinM1, int pinM2) {
    this->pinM1 = pinM1;
    this->pinM2 = pinM2;
    pinMode(pinM1, OUTPUT);
    pinMode(pinM2, OUTPUT);
    desligarM1();
    desligarM2();
}

void Action::Left() {
    analogWrite(pinM1, 300);
    delay(520);
    analogWrite(pinM1, 0);
    setLeftStatus("OK");
    delay(200);
}

void Action::Right() {
    analogWrite(pinM2, 300);
    delay(650);
    analogWrite(pinM2, 0);
    setRightStatus("OK");
    delay(200);
}

void Action::Front() {
    analogWrite(pinM1, 250);
    analogWrite(pinM2, 300);
    delay(500);
    analogWrite(pinM1, 0);
    analogWrite(pinM2, 0);
    setFrontStatus("OK");
    delay(100);
}

void Action::desligarM1() {
    analogWrite(pinM1, 0);
}

void Action::desligarM2() {
    analogWrite(pinM2, 0);
}

void Action::setFrontStatus(const char* status) {
    beliefsJsonDoc["Front"] = status;
}

void Action::setRightStatus(const char* status) {
    beliefsJsonDoc["Right"] = status;
}

void Action::setLeftStatus(const char* status) {
    beliefsJsonDoc["Left"] = status;
}

void Action::StartCamera() {
    server.on("/stream", HTTP_GET, []() {
        WiFiClient client = server.client();
        server.sendHeader("Content-Type", "multipart/x-mixed-replace; boundary=frame");
        server.send(200);
        while (client.connected()) {
            String fakeImage = "--frame\r\nContent-Type: image/jpeg\r\n\r\nFAKEJPEGDATA\r\n";
            client.print(fakeImage);
            delay(1000);
        }
    });
}
