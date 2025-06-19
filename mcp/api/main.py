from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any
from mcp.orchestrator import Orchestrator

app = FastAPI()
orchestrator = Orchestrator()

class MCPRequest(BaseModel):
    input: str
    context: Dict[str, Any]
    parameters: Dict[str, Any]

@app.post("/mcp")
def mcp_endpoint(req: MCPRequest):
    result = orchestrator.handle(req.input, req.context, req.parameters)
    return result
