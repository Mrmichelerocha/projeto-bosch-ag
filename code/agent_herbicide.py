import time
import threading
import requests
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
            for key, val in self.plans[goal]['context'].items():
                if key not in bb or bb[key] != val:
                    return None
            return self.plans[goal]['plan']
        return None

class Action:
    def ir_ate_agente_campo(self):
        print("🚜 Indo até o local do agente de campo...")
        time.sleep(5)  
        print("✅ Chegamos no local e eliminamos as ervas daninhas.")
        agente.add_beliefs({"erva_daninha_detectada": False})
        agente.add_beliefs({"aplicar_herbicida": False})
        print("✅ Voltando para base.")
        agente.add_beliefs({"missao_concluida": True})

    def informar_agente_campo(self):
        print("📡 Enviando confirmação para o agente de campo...")
        try:
            crença_agente_campo = {"erva_daninha": False}
            res = requests.post("http://127.0.0.1:5002/agent", json=crença_agente_campo)
            print(f"📬 Confirmação enviada | Status: {res.status_code}")
        except Exception as e:
            print(f"❌ Erro ao informar agente de campo: {e}")
        
        agente.add_beliefs({"contenção_comunicada": True})

    def informar_agente_supervisor(self):
        print("📡 Enviando confirmação para o agente de campo...")
        try:
            crença_agente_supervisor = {"erva_daninha": False}
            res = requests.post("http://127.0.0.1:5003/agent", json=crença_agente_supervisor)
            print(f"📬 Confirmação enviada | Status: {res.status_code}")
        except Exception as e:
            print(f"❌ Erro ao informar agente de campo: {e}")

        agente.add_beliefs({"contenção_comunicada": True})

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

agente = Agent()

agente.add_beliefs({
    "aplicar_herbicida": False,
    "coordenadas_agente_campo": False,
    "erva_daninha_detectada": False,
    "contenção_comunicada": False,
    "missao_concluida": False
})

agente.set_plan_library({
    "iniciar_missao": {
        "context": {
            "aplicar_herbicida": True,
            "coordenadas_agente_campo": True,
            "erva_daninha_detectada": True
        },
        "plan": ["ir_ate_agente_campo"]
    },
    "confirmar_limpeza": {
        "context": {
            "erva_daninha_detectada": False, "contenção_comunicada": False, "missao_concluida": True
        },
        "plan": ["informar_agente_campo", "informar_agente_supervisor"]
    }
})

app = Flask(__name__)

@app.route("/agent", methods=["GET", "POST"])
def endpoint_agent():
    if request.method == "GET":
        return jsonify(agente.beliefs)
    if request.method == "POST":
        novas = request.json
        agente.add_beliefs(novas)
        print(f"🧠 Novas crenças recebidas: {novas}")
        return jsonify({"msg": "Crenças atualizadas", "crencas": agente.beliefs})

def ciclo_agente():
    while True:
        agente.add_desires("iniciar_missao")
        agente.add_desires("confirmar_limpeza")

        while True:
            goal = agente.get_desires()
            if not goal:
                break
            agente.update_intention(goal)
            agente.execute_intention()

        time.sleep(3)

if __name__ == "__main__":
    threading.Thread(target=ciclo_agente, daemon=True).start()
    print("🌱 Agente Herbicida rodando na porta 5004...")
    app.run(host="0.0.0.0", port=5004)
