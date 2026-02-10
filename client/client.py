import random
import time
import requests

URL = "http://localhost:9000/submit"

for i in range(1, 31):
    task = {
        "task_id": i,
        "complexity": random.randint(1, 10)
    }

    response = requests.post(URL, json=task).json()
    print(f"Task {i} → {response}")

    time.sleep(1)
