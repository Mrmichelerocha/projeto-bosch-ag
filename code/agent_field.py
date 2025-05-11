import requests
import threading
import time
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
    def percorrer_local_definido(self):
        agente.add_beliefs({"envio_coordenadas": False,})
        print("🚜 Percorrendo local definido...")

    def parar_monitoramento(self):
        print("⛔ Monitoramento interrompido.")

    def enviar_coordenadas_ao_supervisor(self):
        print("⚠️ Enviando coordenadas ao supervisor e atualizando minha crença local...")

        # Envia as coordenadas e crença para o supervisor
        try:
            crença_supervisor = {"coordenadas_agente_campo": True}
            res = requests.post("http://127.0.0.1:5003/agent", json=crença_supervisor)
            print(f"📨 Supervisor notificado | Status: {res.status_code}")
        except Exception as e:
            print(f"❌ Falha ao notificar supervisor: {e}")

        agente.add_beliefs({"envio_coordenadas": True,})
        print("📡 Coordenadas enviadas ao supervisor!")

    def aguardar_contenção_de_pragas(self):
        print("⏳ Aguardando contenção de pragas...")

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

app = Flask(__name__)
agente = Agent()

# Crenças iniciais
agente.add_beliefs({
    "erva_daninha": False,
    "local": "ponto_1",
    "envio_coordenadas": False
})

agente.set_plan_library({
    "monitorar_trigo": {
        "context": {"erva_daninha": False},
        "plan": ["percorrer_local_definido"]
    },
    "alerta_ervaDaninha": {
        "context": {"erva_daninha": True, "envio_coordenadas": False},
        "plan": ["parar_monitoramento", "enviar_coordenadas_ao_supervisor"]
    },
    "aguardando_contençãoPragas": {
        "context": {"erva_daninha": True, "envio_coordenadas": True},
        "plan": ["aguardar_contenção_de_pragas"]
    }
})

@app.route("/agent", methods=["GET", "POST"])
def agent_endpoint():
    if request.method == "GET":
        return jsonify(agente.beliefs)
    elif request.method == "POST":
        new_beliefs = request.json
        agente.add_beliefs(new_beliefs)
        return jsonify({"msg": "Crenças atualizadas", "novas_crencas": agente.beliefs})

@app.route("/stream", methods=["GET"])
def stream():
    return jsonify({"frame": "frame_213.jpg"})

def ciclo_agente():
    while True:
        if not agente.desires:
            agente.add_desires("monitorar_trigo")
            agente.add_desires("alerta_ervaDaninha")
            agente.add_desires("aguardando_contençãoPragas")
        goal = agente.get_desires()
        if goal:
            agente.update_intention(goal)
            agente.execute_intention()
        time.sleep(2)

if __name__ == "__main__":
    threading.Thread(target=ciclo_agente, daemon=True).start()
    app.run(host="0.0.0.0", port=5002)
