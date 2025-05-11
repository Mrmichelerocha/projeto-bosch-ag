import requests
import random
import time
import threading
from flask import Flask, request, jsonify

class PlanLibrary:
    def __init__(self):
        self.plans = {}

    def set_plan_library(self, planlb):
        self.plans = planlb

    def add_plan(self, goal, prec, plan):
        self.plans[goal] = {'context': prec, 'plan': plan}

    def get_plan(self, goal, bb):
        if goal in self.plans:
            if set(self.plans[goal]['context'].items()).issubset(bb.items()):
                return self.plans[goal]['plan']
        return None

class Action:
    def verificar_erva_daninha(self):
        try:
            print("🎥 Buscando frame do agente de campo...")
            res = requests.get("http://127.0.0.1:5002/stream", timeout=1)
            if res.status_code != 200:
                print("❌ Não foi possível obter o frame.")
                supervisor.add_beliefs({"erva_daninha_detectada": False})
                return

            frame = res.json().get("frame")
            print(f"🧠 Frame recebido: {frame}")
            print(f"🧠 Frame recebido: {frame}")
            print(f"🧠 Frame recebido: {frame}")
            print(f"🧠 Frame recebido: {frame}")

        except Exception as e:
            print(f"💥 Erro ao buscar frame: {e}")
            supervisor.add_beliefs({"erva_daninha_detectada": False})
            return

        print("🔍 YOLO simulado analise...")
        time.sleep(5)
        print("🔍 YOLO simulado analise...")
        time.sleep(5)
        print("🔍 YOLO simulado analise...")
        time.sleep(5)


        detections = [
            {"class": "trigo", "confidence": 0.88},
            {"class": "erva_daninha", "confidence": 0.91},
        ]

        ervas = [d for d in detections if d["class"] == "erva_daninha" and d["confidence"] > 0.8]
        detectado = len(ervas) > 0

        supervisor.add_beliefs({"erva_daninha_detectada": detectado})
        print(f"📦 Simulação estruturada: {'ERVA DANINHA DETECTADA' if detectado else 'Somente trigo'}")
        print(f"📦 Simulação estruturada: {'ERVA DANINHA DETECTADA' if detectado else 'Somente trigo'}")
        print(f"📦 Simulação estruturada: {'ERVA DANINHA DETECTADA' if detectado else 'Somente trigo'}")
        print(f"📦 Simulação estruturada: {'ERVA DANINHA DETECTADA' if detectado else 'Somente trigo'}")

    def enviar_alarme_para_agente_campo(self):
        crença_agente_campo = {"erva_daninha": True}
        try:
            res = requests.post("http://192.168.15.4:5002/agent", json=crença_agente_campo)
            print(f"📡 Enviado ao agente de campo: {crença_agente_campo} | Status: {res.status_code}")
        except Exception as e:
            print(f"❌ Erro ao enviar crença: {e}")

        supervisor.add_beliefs({"agente_campo_comunicado": True})

    def enviar_alarme_para_agente_herbicida(self):
        print("💨 Preparando envio de alarme para o agente herbicida...")
        time.sleep(5)  

        payload = {
            "aplicar_herbicida": True,
            "coordenadas_agente_campo": True,
            "erva_daninha_detectada": True,
        }

        try:
            res = requests.post("http://127.0.0.1:5004/agent", json=payload)
            print(f"🧪 Herbicida acionado com sucesso! Status: {res.status_code}")
        except Exception as e:
            print(f"❌ Erro ao contatar agente herbicida: {e}")

        supervisor.add_beliefs({"agente_herbicida_comunicado": True})


        

class Agent:
    def __init__(self):
        self.beliefs = {}
        self.desires = []
        self.intention = []
        self.plan_library = PlanLibrary()

    def get_desires(self):
        return self.desires.pop() if self.desires else None

    def add_desires(self, desire):
        self.desires.append(desire)

    def add_beliefs(self, beliefs):
        self.beliefs.update(beliefs)

    def set_plan_library(self, pl):
        self.plan_library.set_plan_library(pl)

    def update_intention(self, goal):
        plan = self.plan_library.get_plan(goal, self.beliefs)
        if plan:
            self.intention.extend(plan)

    def execute_intention(self):
        while self.intention:
            next_goal = self.intention.pop()
            if self.plan_library.get_plan(next_goal, self.beliefs) is None:
                action = getattr(Action(), next_goal)
                action()
            else:
                self.intention.extend(self.plan_library.get_plan(next_goal, self.beliefs))

supervisor = Agent()

supervisor.add_beliefs({
    "erva_daninha_detectada": False,
    "agente_campo_comunicado": False,
    "agente_herbicida_comunicado": False,
    "coordenadas_agente_campo": False
})

supervisor.set_plan_library({
    "analisar_monitoramento": {
        "context": {"erva_daninha_detectada": False},
        "plan": ["verificar_erva_daninha"]
    },
    "acionar_agente_campo": {
        "context": {"erva_daninha_detectada": True, "agente_campo_comunicado": False},
        "plan": ["enviar_alarme_para_agente_campo"]
    },
    "acionar_herbicida_central": {
        "context": {"erva_daninha_detectada": True, "agente_herbicida_comunicado": False, "coordenadas_agente_campo": True},
        "plan": ["enviar_alarme_para_agente_herbicida"]
    }
})

app = Flask(__name__)

@app.route("/agent", methods=["GET", "POST"])
def endpoint_agent():
    if request.method == "GET":
        return jsonify(supervisor.beliefs)
    if request.method == "POST":
        novas = request.json
        supervisor.add_beliefs(novas)
        return jsonify({"msg": "Crenças atualizadas", "crencas": supervisor.beliefs})

def ciclo_supervisor():
    while True:
        supervisor.add_desires("analisar_monitoramento")
        supervisor.add_desires("acionar_agente_campo")
        supervisor.add_desires("acionar_herbicida_central")

        while True:
            goal = supervisor.get_desires()
            if not goal:
                break
            supervisor.update_intention(goal)
            supervisor.execute_intention()

        time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=ciclo_supervisor, daemon=True).start()
    print("🧠 Supervisor rodando")
    app.run(host="0.0.0.0", port=5003)
