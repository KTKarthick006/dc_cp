import time
import requests
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

WORKERS = {
    "node1": "http://localhost:8001",
    "node2": "http://localhost:8002",
    "node3": "http://localhost:8003"
}

risk_threshold = 0.7

class Task(BaseModel):
    task_id: int
    complexity: int

def compute_risk(m):
    return (
        0.4 * m["cpu_load"] +
        0.4 * m["failure_rate"] +
        0.2 * (1 - m["trust"])
    )

def cognitive_penalty(m):
    penalty = 0.0

    if m["trust"] < 0.5:
        penalty += 0.2

    if time.time() - m["last_failure_time"] < 30:
        penalty += 0.3

    return penalty

@app.post("/submit")
def submit_task(task: Task):
    global risk_threshold

    candidates = []

    for node, url in WORKERS.items():
        metrics = requests.get(f"{url}/metrics").json()
        risk = compute_risk(metrics) + cognitive_penalty(metrics)

        if risk < risk_threshold:
            candidates.append((node, url, risk))

    if not candidates:
        risk_threshold = min(0.9, risk_threshold + 0.05)
        return {
            "status": "rejected",
            "risk_threshold": risk_threshold
        }

    node, url, risk = min(candidates, key=lambda x: x[2])
    result = requests.post(f"{url}/execute", json=task.dict()).json()

    if result["status"] == "fail":
        risk_threshold = max(0.4, risk_threshold - 0.05)
    else:
        risk_threshold = min(0.8, risk_threshold + 0.01)

    return {
        "assigned_to": node,
        "risk": round(risk, 3),
        "result": result["status"],
        "risk_threshold": round(risk_threshold, 3)
    }
