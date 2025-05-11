
#include <ESP8266WebServer.h>
#include <ESP8266WiFi.h>
#include <functional>
#include <map>
#include "agent.h"

typedef std::function<void()> ActionFunction;

std::map<String, ActionFunction> actionMap;

const char* ssid = "LIA";
const char* password = "Lia321A@";
const int ledPinM1 = 0;
const int ledPinM2 = 2;

Action action(ledPinM1, ledPinM2);
ESP8266WebServer server(80);

DynamicJsonDocument planJsonDoc(2000);
DynamicJsonDocument beliefsJsonDoc(2000);
DynamicJsonDocument desireJsonDoc(2000);
DynamicJsonDocument intentionJsonDoc(2000);

JsonObject planObject = planJsonDoc.to<JsonObject>();
JsonObject beliefsObject = beliefsJsonDoc.to<JsonObject>();
JsonArray desireArray = desireJsonDoc.to<JsonArray>();
JsonArray intentionArray = intentionJsonDoc.to<JsonArray>();

void startCameraServer(){
  httpd_config_t config = HTTPD_DEFAULT_CONFIG();
  config.server_port = 80;

  httpd_uri_t stream_uri = {
    .uri       = "/stream",
    .method    = HTTP_GET,
    .handler   = stream_handler,
    .user_ctx  = NULL
  };

  if (httpd_start(&stream_httpd, &config) == ESP_OK) {
    httpd_register_uri_handler(stream_httpd, &stream_uri);
  }
}

void setUpWiFi() {
  Serial.println();
  Serial.print("Conectando à rede ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("Conectado à rede WiFi");
  Serial.print("Endereço IP: ");
  Serial.println(WiFi.localIP());
}

void handleGetPlan() {
  String response;
  serializeJson(planJsonDoc, response);
  server.send(200, "application/json", response);
}

void handleSetPlan() {
  String nameKey = server.arg("nameKey");
  String ctxKey = server.arg("ctxKey");
  String planKey = server.arg("planKey");

  JsonObject planName = planObject.createNestedObject(nameKey);
  DynamicJsonDocument contextJson(200);
  deserializeJson(contextJson, ctxKey);
  JsonObject contextObject = planName.createNestedObject("context");
  for (JsonPair keyValue : contextJson.as<JsonObject>()) {
    contextObject[keyValue.key()] = keyValue.value();
  }
  DynamicJsonDocument planJson(200);
  deserializeJson(planJson, planKey);
  JsonArray planArray = planName.createNestedArray("plan");
  for (JsonVariant value : planJson.as<JsonArray>()) {
    planArray.add(value);
  }

  String html = "<html><body><h1>Controle de Relé</h1>";
  html += "<form method='POST' action='/setplan'>";
  html += "<input type='text' name='nameKey' value=''>Name Plan Key<br>";
  html += "<input type='text' name='ctxKey' value=''>Ctx Key<br>";
  html += "<input type='text' name='planKey' value=''>Plan Key<br>";
  html += "<input type='submit' value='Enviar'>";
  html += "</form></body></html>";
  server.send(200, "text/html", html);
}

JsonVariant getPlan(String goal) {
  if (planObject.containsKey(goal)) {
    Serial.print("existe um plano com a meta");
    Serial.println(goal);
    JsonObject goalPlan = planObject[goal].as<JsonObject>();
    serializeJson(goalPlan, Serial);
    Serial.println();
    JsonObject context = goalPlan["context"].as<JsonObject>();
    serializeJson(context, Serial);
    Serial.println();
    for (JsonPair kv : context) {
      if (!beliefsObject.containsKey(kv.key().c_str()) ||
          beliefsObject[kv.key().c_str()] != kv.value()) {
        Serial.print("As Condições não foram satisfeitas");
        return JsonObject();
      }
    }
    JsonArray planArray = goalPlan["plan"].as<JsonArray>();
    serializeJson(planArray, Serial);
    Serial.println();
    return planArray;
  }
  return JsonObject();
}

void handleGetBeliefs() {
  String response;
  serializeJson(beliefsJsonDoc, response);
  server.send(200, "application/json", response);
}

void handleSetBeliefs() {
  String beliefsKey = server.arg("beliefsKey");
  String beliefsValue = server.arg("beliefsValue");
  beliefsObject[beliefsKey] = beliefsValue;

  String html = "<html><body><h1>Controle de Relé</h1>";
  html += "<form method='POST' action='/setbeliefs'>";
  html += "<input type='text' name='beliefsKey' value=''>Beliefs Key<br>";
  html += "<input type='text' name='beliefsValue' value=''>Beliefs Value<br>";
  html += "<input type='submit' value='Enviar'>";
  html += "</form></body></html>";
  server.send(200, "text/html", html);
}

void handleGetDesire() {
  String response;
  serializeJson(desireJsonDoc, response);
  server.send(200, "application/json", response);
}

void handleSetDesire() {
  String desireKey = server.arg("desireKey");
  desireArray.add(desireKey);

  String html = "<html><body><h1>Controle de Relé</h1>";
  html += "<form method='POST' action='/setdesire'>";
  html += "<input type='text' name='desireKey' value=''>Desire Key<br>";
  html += "<input type='submit' value='Enviar'>";
  html += "</form></body></html>";
  server.send(200, "text/html", html);
}

String getDesires() {
  if (desireArray.size() > 0) {
    String desire = desireArray[desireArray.size() - 1].as<String>();
    Serial.println("getDesires d1 " + desire);
    desireArray.remove(desireArray.size() - 1);
    Serial.println("getDesires d2 " + desire);
    return desire;
  }
  return "";
}

void handleGetIntention() {
  String response;
  serializeJson(intentionJsonDoc, response);
  server.send(200, "application/json", response);
}

void handleSetIntention() {
  String intentionKey = server.arg("intentionKey");
  intentionArray.add(intentionKey);

  String html = "<html><body><h1>Controle de Relé</h1>";
  html += "<form method='POST' action='/setintention'>";
  html += "<input type='text' name='intentionKey' value=''>Intention Key<br>";
  html += "<input type='submit' value='Enviar'>";
  html += "</form></body></html>";
  server.send(200, "text/html", html);
}

void updateIntention() {
  String goal = getDesires();
  JsonVariant plan = getPlan(goal);
  if (plan.size() > 0) {
    Serial.print("o plano não está mais vazio ");
    Serial.println("a goal que está em updateintention é " + goal);
    serializeJson(plan, Serial);
    Serial.println();
    for (size_t i = 0; i < plan.size(); i++) {
      JsonVariant value = plan[i];
      intentionArray.add(value);
    }
    executeIntention();
  }
}

void executeIntention() {
  while (intentionArray.size() > 0) {
    Serial.println();
    Serial.println("as intentions não estão vazias");
    String next = intentionArray[intentionArray.size() - 1];
    intentionArray.remove(intentionArray.size() - 1);
    Serial.println("intenção: " + next);
    JsonVariant nextPlan = getPlan(next);
    if (!nextPlan.isNull() && nextPlan.is<JsonArray>()) {
      Serial.println("Verificou que dentro de planos EXISTE nova intenção");
      JsonArray planArray = nextPlan.as<JsonArray>();
      for (JsonVariant value : planArray) {
        intentionArray.add(value);
      }
    } else if (actionMap.count(next) > 0) {
      Serial.println("verificou que existe a ação no arquivo pra FAZER");
      actionMap[next]();
    } else {
      Serial.println("Ação não pode ser executada");
    }
  }
}

void setUpWebServer() {
  server.on("/getplan", handleGetPlan);
  server.on("/getbeliefs", handleGetBeliefs);
  server.on("/getdesire", handleGetDesire);
  server.on("/getintention", handleGetIntention);
  server.on("/setplan", handleSetPlan);
  server.on("/setbeliefs", handleSetBeliefs);
  server.on("/setdesire", handleSetDesire);
  server.on("/setintention", handleSetIntention);
  server.on("/stream", startCameraServer);
  server.begin();
  Serial.println("Servidor iniciado");
}

void setup() {
  Serial.begin(115200);
  delay(1500);
  WiFi.forceSleepWake();

  actionMap["Front"] = std::bind(&Action::Front, action);
  actionMap["Left"] = std::bind(&Action::Left, action);
  actionMap["Right"] = std::bind(&Action::Right, action);
  action.StartCamera();

  setUpWiFi();
  setUpWebServer();
}

void loop() {
  server.handleClient();
  updateIntention();
  delay(1000);
}
