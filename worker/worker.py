import random
import time
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Task(BaseModel):
    task_id: int
    complexity: int

cpu_load = random.uniform(0.2, 0.4)
failure_rate = random.uniform(0.05, 0.15)
trust = 1.0
last_failure_time = 0.0

@app.post("/execute")
def execute_task(task: Task):
    global cpu_load, trust, last_failure_time

    cpu_load = min(1.0, cpu_load + task.complexity * 0.05)

    if random.random() < failure_rate:
        trust *= 0.7
        last_failure_time = time.time()
        return {"status": "fail"}

    time.sleep(task.complexity * 0.1)

    cpu_load = max(0.1, cpu_load - 0.1)
    trust = min(1.0, trust + 0.05)

    return {"status": "success"}

@app.get("/metrics")
def metrics():
    return {
        "cpu_load": cpu_load,
        "failure_rate": failure_rate,
        "trust": trust,
        "last_failure_time": last_failure_time
    }
