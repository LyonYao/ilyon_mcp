from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any
from mcp.orchestrator.orchestrator import Orchestrator
from mcp.api.capabilities import router as capabilities_router

app = FastAPI()
orchestrator = Orchestrator()

app.include_router(capabilities_router)

class MCPRequest(BaseModel):
    input: str
    context: Dict[str, Any]
    parameters: Dict[str, Any]

@app.post("/mcp")
def mcp_endpoint(req: MCPRequest):
    result = orchestrator.handle(req.input, req.context, req.parameters)
    return result
