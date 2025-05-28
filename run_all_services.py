import subprocess

services = [
    ("agents.api_agent", 8001),
    ("agents.retriever_agent", 8002),
    ("agents.scraper_agent", 8003),
    ("agents.llm_agent", 8004),
    ("orchestrator.orchestrator", 8000),
]

processes = []

for module, port in services:
    print(f"Starting {module} on port {port}")
    p = subprocess.Popen(["uvicorn", f"{module}:app", "--port", str(port)])
    processes.append(p)

print("All services started. Press Ctrl+C to stop.")
try:
    for p in processes:
        p.wait()
except KeyboardInterrupt:
    print("Shutting down services...")
    for p in processes:
        p.terminate()
