# 🌿 Weed Detection via Multi-Agent BDI Architecture

Este projeto propõe uma abordagem distribuída e inteligente para reconhecimento de ervas daninhas em plantações, utilizando agentes embarcados e um agente central inteligente.

---

## 🛰️ Arquitetura

- **Agentes ESP32-CAM (x2)**: Monitoram plantações e transmitem vídeo + recebem comandos.
- **Agente Central (software)**:
  - Detecção com YOLOv5 (& Label Studio).
  - Processamento multithreaded.
  - Coordenação de planos BDI.
- **Plano de ação**: Ao identificar erva daninha, o agente central elabora e despacha planos para drones agirem.

📌 Tudo orquestrado com uma arquitetura **BDI (Belief-Desire-Intention)**.

---

## ⚙️ Tecnologias

- ESP32-CAM (simulado)
- YOLOv5 + Label Studio (detecção simulada)
- Python + threading
- Arquitetura BDI personalizada

---

## 🧪 Exemplo de Execução

```bash
python agent_bdi.py
