from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from orchestrator import Orchestrator, AGENTS
import uvicorn

app = FastAPI(title="36-Agent Orchestrator", description="A web interface for the multi-agent orchestrator system")

class OrchestrateRequest(BaseModel):
    task: str

@app.post("/orchestrate")
async def orchestrate_task(request: OrchestrateRequest) -> str:
    try:
        orch = Orchestrator(AGENTS)
        result = await orch.orchestrate(request.task)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Orchestration failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)