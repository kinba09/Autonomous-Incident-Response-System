import json

from agents.orchestrator import run_autogen_incident_flow


if __name__ == "__main__":
    result = run_autogen_incident_flow()
    print(json.dumps(result, indent=2))
