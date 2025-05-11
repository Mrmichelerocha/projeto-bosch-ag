
#ifndef AGENT_H
#define AGENT_H

#include <Arduino.h>
#include <ArduinoJson.h>

extern DynamicJsonDocument beliefsJsonDoc;

class Action {
public:
    Action(int pinM1, int pinM2);
    void Left();
    void Right();
    void Front();
    void desligarM1();
    void desligarM2();
    void setFrontStatus(const char* status);
    void setRightStatus(const char* status);
    void setLeftStatus(const char* status);
    void StartCamera();
private:
    int pinM1, pinM2;
};

#endif
